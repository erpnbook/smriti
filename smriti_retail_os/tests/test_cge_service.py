# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_cge_service.py
# @description: Unit tests for CGE service layer — channel gross earnings processing.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/tests/test_cge_service.py
# @description: Unit tests for SMRITI Customer Growth Engine (CGE) service layer components.
# @author: Antigravity AI
# @date: 2026-06-18
#

import frappe
import unittest
from frappe.utils import now_datetime, nowdate, add_to_date, flt
from smriti_retail_os.cge.service.cge_service import (
    CGERuleEvaluator,
    CGECampaignManager,
    CGEWalletLedger,
    generate_nightly_liability_snapshot,
    execute_snapshot_cleanup
)

class TestCGERuleEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test customer
        cls.customer_name = "_Test CGE Customer"
        if not frappe.db.exists("Customer", cls.customer_name):
            cust = frappe.new_doc("Customer")
            cust.customer_name = cls.customer_name
            cust.customer_group = "Individual"
            cust.insert(ignore_permissions=True)
            
        # Create test item brand
        cls.brand = "Raymond Test"
        if not frappe.db.exists("Brand", cls.brand):
            brand_doc = frappe.new_doc("Brand")
            brand_doc.brand = cls.brand
            brand_doc.insert(ignore_permissions=True)
            
        # Ensure test HSN code exists
        if not frappe.db.exists("GST HSN Code", "999900"):
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "999900"
            hsn.insert(ignore_permissions=True)

        # Create test items
        cls.item_code = "_Test CGE Item"
        if not frappe.db.exists("Item", cls.item_code):
            item_doc = frappe.new_doc("Item")
            item_doc.item_code = cls.item_code
            item_doc.item_name = cls.item_code
            item_doc.item_group = "All Item Groups"
            item_doc.brand = cls.brand
            item_doc.gst_hsn_code = "999900"
            item_doc.insert(ignore_permissions=True)

        # Get active company and warehouse dynamically
        cls.company_name = frappe.get_all("Company", limit=1)[0].name
        cls.warehouse = frappe.db.get_value("Warehouse", {"company": cls.company_name, "is_group": 0})
        if not cls.warehouse:
            parent = frappe.db.get_value("Warehouse", {"company": cls.company_name, "is_group": 1})
            w = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Stores - TDP",
                "parent_warehouse": parent,
                "company": cls.company_name,
                "is_group": 0
            })
            w.insert(ignore_permissions=True)
            cls.warehouse = w.name

        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up
        frappe.db.delete("SMRITI Loyalty Tier")
        frappe.db.delete("SMRITI Loyalty Rule")
        frappe.db.delete("SMRITI Wallet Ledger")
        frappe.db.delete("SMRITI Coupon Campaign")
        frappe.db.delete("SMRITI Liability Snapshot")
        frappe.db.delete("SMRITI Rule Evaluation Log")
        frappe.db.delete("Customer", {"name": cls.customer_name})
        frappe.db.delete("Item", {"name": cls.item_code})
        frappe.db.delete("Brand", {"name": cls.brand})
        frappe.db.commit()
        super().tearDownClass()

    def setUp(self):
        # Empty CGE tables
        frappe.db.delete("SMRITI Loyalty Tier")
        frappe.db.delete("SMRITI Loyalty Rule")
        frappe.db.delete("SMRITI Wallet Ledger")
        frappe.db.delete("SMRITI Coupon Campaign")
        frappe.db.delete("SMRITI Liability Snapshot")
        frappe.db.delete("SMRITI Rule Evaluation Log")
        frappe.db.commit()

    def test_wallet_immutability(self):
        """Verify submitted ledger entries cannot be edited or deleted."""
        # Post a transaction
        ledger = CGEWalletLedger.post_transaction(
            customer=self.customer_name,
            wallet_type="Promo Cashback",
            transaction_type="Credit",
            amount=100.0
        )
        self.assertIsNotNone(ledger.name)
        
        # Verify edit block
        ledger.amount = 200.0
        self.assertRaises(frappe.ValidationError, ledger.save)
        
        # Verify delete block
        self.assertRaises(frappe.ValidationError, ledger.delete)

    def test_budget_reservation(self):
        """Verify coupon campaign budget reservation, limit check, commit, and release."""
        # Create campaign
        campaign_name = "Festive Test Campaign"
        campaign = frappe.new_doc("SMRITI Coupon Campaign")
        campaign.campaign_name = campaign_name
        campaign.campaign_type = "Festival"
        campaign.start_date = nowdate()
        campaign.end_date = add_to_date(nowdate(), days=30)
        campaign.budget_limit = 500.0
        campaign.status = "Active"
        campaign.stop_on_limit = 1
        campaign.insert(ignore_permissions=True)
        
        # Create Coupon Link
        coupon_code = "TESTCOUPON123"
        if frappe.db.exists("Coupon Code", coupon_code):
            frappe.delete_doc("Coupon Code", coupon_code)
            
        coupon = frappe.new_doc("Coupon Code")
        coupon.coupon_code = coupon_code
        coupon.coupon_name = coupon_code
        coupon.custom_campaign = campaign_name
        coupon.insert(ignore_permissions=True)
        
        # 1. Reserve budget
        CGECampaignManager.reserve_budget(coupon_code, 150.0, "test_session_1")
        
        # Assert reserved
        campaign.reload()
        self.assertEqual(flt(campaign.budget_reserved), 150.0)
        
        # 2. Try to exceed limit
        self.assertRaises(frappe.ValidationError, CGECampaignManager.reserve_budget, coupon_code, 400.0, "test_session_2")
        
        # 3. Commit budget
        CGECampaignManager.commit_budget(coupon_code, 120.0, "test_session_1")
        campaign.reload()
        self.assertEqual(flt(campaign.budget_reserved), 0.0)
        self.assertEqual(flt(campaign.budget_consumed), 120.0)

    def test_rule_evaluation_stacking(self):
        """Verify loyalty rule resolution, customer tier multipliers, and stacking logic."""
        # Configure tier: Gold Tier gets 1.5X multiplier
        tier = frappe.new_doc("SMRITI Loyalty Tier")
        tier.tier_name = "Gold Tier"
        tier.min_points = 0.0 # Match customer instantly
        tier.tier_multiplier = 1.5
        tier.active = 1
        tier.insert(ignore_permissions=True)
        
        # Configure rule: Raymond gets 2.0X multiplier, stacking allowed
        rule = frappe.new_doc("SMRITI Loyalty Rule")
        rule.rule_name = "Raymond Brand Multiplier"
        rule.rule_type = "Multiplier"
        rule.dimension = "Brand"
        rule.dimension_doctype = "Brand"
        rule.dimension_value = self.brand
        rule.rule_value = 2.0
        rule.priority = 1
        rule.allow_stack = 1
        rule.status = "Active"
        rule.insert(ignore_permissions=True)
        
        # Setup settings to enable logging
        settings = frappe.get_doc("SMRITI CGE Settings")
        settings.enable_rule_trace = 1
        settings.save(ignore_permissions=True)
        
        # Create Sales Invoice mockup doc
        invoice = frappe.new_doc("Sales Invoice")
        invoice.name = "INV-TEST-0001"
        invoice.customer = self.customer_name
        invoice.posting_date = nowdate()
        invoice.company = frappe.get_all("Company", limit=1)[0].name
        
        # Append item
        invoice.append("items", {
            "item_code": self.item_code,
            "qty": 1,
            "rate": 1000.0,
            "warehouse": self.warehouse
        })
        
        # Evaluate
        evaluator = CGERuleEvaluator(invoice)
        results = evaluator.evaluate()
        
        # Assert matching and stacking (2X brand * 1.5X tier = 3X)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["multiplier"], 3.0)
        
        # Verify trace log was generated
        logs = frappe.get_all("SMRITI Rule Evaluation Log", filters={"invoice": invoice.name})
        self.assertGreater(len(logs), 0)
