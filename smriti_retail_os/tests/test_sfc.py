# -*- coding: utf-8 -*-
#
# @file: test_sfc.py
# @description: Automated test suite for SMRITI Sales Force Commission (SFC).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os import smriti
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, getdate, flt
from smriti_retail_os.sfm.service.commission_service import (
    resolve_commission_rule,
    generate_monthly_settlement,
    run_monthly_settlements
)

class TestSFC(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Seed basic Gender records
        for g_name in ["Male", "Female"]:
            if not smriti.db.exists("Gender", g_name):
                g = smriti.documents.new("Gender")
                g.gender = g_name
                g.insert(ignore_permissions=True)
                
        cls.company = "_Test SFC Company"
        if not smriti.db.exists("Company", cls.company):
            smriti.db.delete("Company", {"abbr": "SFC2"})
            comp = smriti.documents.new("Company")
            comp.company_name = cls.company
            comp.abbr = "SFC2"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)

        for fy_name in smriti.db.get_list("Fiscal Year", filters={"disabled": 0}, pluck="name"):
            fy = smriti.documents.get("Fiscal Year", fy_name)
            if not any(c.company == cls.company for c in fy.companies):
                fy.append("companies", {"company": cls.company})
                fy.save(ignore_permissions=True)

        smriti.db.set_value("Company", cls.company, "gstin", "27AAXFT2508H1ZR")
        
        addr_name = f"{cls.company}-Registered-Test"
        if not smriti.db.exists("Address", addr_name):
            addr = smriti.documents.new("Address")
            addr.address_title = cls.company
            addr.address_type = "Office"
            addr.address_line1 = "Test Street"
            addr.city = "Mumbai"
            addr.state = "Maharashtra"
            addr.pincode = "400001"
            addr.country = "India"
            addr.is_primary_address = 1
            addr.is_shipping_address = 1
            addr.is_your_company_address = 1
            addr.gstin = "27AAXFT2508H1ZR"
            addr.append("links", {"link_doctype": "Company", "link_name": cls.company})
            addr.insert(ignore_permissions=True)

        # Resolve or create basic accounts
        cls.debit_to = smriti.db.get("Account", {"company": cls.company, "account_type": "Receivable", "is_group": 0}, "name")
        if not cls.debit_to:
            parent_recv = smriti.db.get("Account", {"company": cls.company, "account_type": "Receivable", "is_group": 1}, "name")
            acc = smriti.documents.new("Account")
            acc.account_name = "Debtors"
            acc.parent_account = parent_recv
            acc.company = cls.company
            acc.account_type = "Receivable"
            acc.insert(ignore_permissions=True)
            cls.debit_to = acc.name

        cls.income_account = smriti.db.get("Account", {"company": cls.company, "root_type": "Income", "is_group": 0}, "name")
        if not cls.income_account:
            parent_inc = smriti.db.get("Account", {"company": cls.company, "root_type": "Income", "is_group": 1}, "name")
            acc = smriti.documents.new("Account")
            acc.account_name = "Sales"
            acc.parent_account = parent_inc
            acc.company = cls.company
            acc.root_type = "Income"
            acc.insert(ignore_permissions=True)
            cls.income_account = acc.name

        cls.uom = smriti.db.exists("UOM", "Nos") or smriti.db.get("UOM", {}, "name") or "Nos"
        cls.item_group = smriti.db.exists("Item Group", "All Item Groups") or smriti.db.get("Item Group", {}, "name") or "All Item Groups"

        cls.warehouse = smriti.db.get("Warehouse", {"company": cls.company, "is_group": 0}, "name")
        if not cls.warehouse:
            w = smriti.documents.new("Warehouse")
            w.warehouse_name = "Test SFC Stores"
            w.company = cls.company
            w.is_group = 0
            w.insert(ignore_permissions=True)
            cls.warehouse = w.name

        cls.brand = "Raymond Test Brand"
        if not smriti.db.exists("Brand", cls.brand):
            b = smriti.documents.new("Brand")
            b.brand = cls.brand
            b.insert(ignore_permissions=True)

        if not smriti.db.exists("GST HSN Code", "649211"):
            hsn = smriti.documents.new("GST HSN Code")
            hsn.hsn_code = "649211"
            hsn.insert(ignore_permissions=True)

        cls.item = "TEST-SFC-ITEM-01"
        if not smriti.db.exists("Item", cls.item):
            itm = smriti.documents.new("Item")
            itm.item_code = cls.item
            itm.item_name = "Test SFC Item"
            itm.item_group = cls.item_group
            itm.brand = cls.brand
            itm.stock_uom = cls.uom
            itm.gst_hsn_code = "649211"
            itm.insert(ignore_permissions=True)

        cls.customer = "Test Customer SFC"
        if not smriti.db.exists("Customer", cls.customer):
            cust = smriti.documents.new("Customer")
            cust.customer_name = cls.customer
            cust.customer_group = "Individual"
            cust.territory = "All Territories"
            cust.insert(ignore_permissions=True)

        cls.store = "Store - Test SFC"
        if not smriti.db.exists("SMRITI Store", cls.store):
            s = smriti.documents.new("SMRITI Store")
            s.store_name = cls.store
            s.default_warehouse = cls.warehouse
            s.company = cls.company
            s.insert(ignore_permissions=True)
            cls.store = s.name

        # Create test employees
        cls.emp_p = "EMP-SFC-PRIMARY"
        if not smriti.db.exists("Employee", cls.emp_p):
            e = smriti.documents.new("Employee")
            e.employee_name = "Rahul Primary Owner"
            e.first_name = "Rahul"
            e.company = cls.company
            e.gender = "Male"
            e.status = "Active"
            e.date_of_joining = "2026-01-01"
            e.date_of_birth = "1990-01-01"
            e.insert(ignore_permissions=True)
            smriti.db.set_value("Employee", e.name, "name", cls.emp_p)

        cls.emp_s = "EMP-SFC-SECONDARY"
        if not smriti.db.exists("Employee", cls.emp_s):
            e = smriti.documents.new("Employee")
            e.employee_name = "Sonia Secondary Owner"
            e.first_name = "Sonia"
            e.company = cls.company
            e.gender = "Female"
            e.status = "Active"
            e.date_of_joining = "2026-01-01"
            e.date_of_birth = "1990-01-01"
            e.insert(ignore_permissions=True)
            smriti.db.set_value("Employee", e.name, "name", cls.emp_s)

        smriti.db.commit()

    def setUp(self):
        super().setUp()
        frappe.flags.in_test = True
        frappe.session.user = "Administrator"

        smriti.db.delete("SMRITI Commission Rule")
        smriti.db.delete("SMRITI Commission Event")
        smriti.db.delete("SMRITI Commission Ledger")
        smriti.db.delete("SMRITI Commission Settlement")
        smriti.db.delete("SMRITI Commission Adjustment Detail")
        smriti.db.delete("SMRITI Customer Ownership")
        smriti.db.delete("SMRITI Attribution Ledger")
        smriti.db.delete("SMRITI Attribution Event")

        invoice_names = smriti.db.get_list("Sales Invoice", filters={"company": self.company}, pluck="name")
        if invoice_names:
            smriti.db.delete("Sales Invoice Item", {"parent": ["in", invoice_names]})
            smriti.db.delete("Sales Invoice", {"name": ["in", invoice_names]})

        # Initialize settings
        smriti.db.set_value("SMRITI SFM Settings", "SMRITI SFM Settings", {
            "enable_sfm": 1,
            "ownership_precedence": 1,
            "primary_split_pct": 70.0,
            "secondary_split_pct": 30.0,
            "walkin_employee": self.emp_p
        }, update_modified=False)

        if not smriti.db.exists("SMRITI Commission Settings", "SMRITI Commission Settings"):
            smriti.documents.new("CommissionSettings").update({
                "enable_sfc": 1,
                "auto_generate_events": 1,
                "auto_generate_settlements": 0,
                "allow_negative_commission": 1
            }).insert(ignore_permissions=True)
        else:
            smriti.db.set_value("SMRITI Commission Settings", "SMRITI Commission Settings", {
                "enable_sfc": 1,
                "auto_generate_events": 1,
                "auto_generate_settlements": 0,
                "allow_negative_commission": 1
            }, update_modified=False)

        frappe.clear_cache()
        smriti.db.commit()

    def tearDown(self):
        frappe.flags.in_test = False
        super().tearDown()

    def test_commission_rule_precedence(self):
        """Verify employee-specific override rule takes precedence over global fallback rule."""
        # 1. Global Rule (2% rate)
        r_global = smriti.documents.new("SMRITI Commission Rule")
        r_global.rule_name = "Global Base Rule"
        r_global.commission_rate = 2.0
        r_global.company = self.company
        r_global.is_active = 1
        r_global.priority = 0
        r_global.insert(ignore_permissions=True)

        # 2. Employee Override Rule (3% rate)
        r_override = smriti.documents.new("SMRITI Commission Rule")
        r_override.rule_name = "Rahul Override Rule"
        r_override.employee = self.emp_p
        r_override.commission_rate = 3.0
        r_override.company = self.company
        r_override.is_active = 1
        r_override.priority = 10
        r_override.insert(ignore_permissions=True)

        # Resolve rules for primary and secondary employees
        rule_p = resolve_commission_rule(self.emp_p, self.company, "2026-06-02")
        self.assertEqual(rule_p.name, r_override.name)
        self.assertEqual(flt(rule_p.commission_rate), 3.0)

        rule_s = resolve_commission_rule(self.emp_s, self.company, "2026-06-02")
        self.assertEqual(rule_s.name, r_global.name)
        self.assertEqual(flt(rule_s.commission_rate), 2.0)

    def test_commission_event_and_ledger_generation(self):
        """Verify commission events and ledgers are posted successfully on invoice submit."""
        # Setup 2% global rule
        r_global = smriti.documents.new("SMRITI Commission Rule")
        r_global.rule_name = "Global Base Rule"
        r_global.commission_rate = 2.0
        r_global.company = self.company
        r_global.is_active = 1
        r_global.insert(ignore_permissions=True)

        # Submit Invoice
        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-02"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 10000.0, # Net total = 10000
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Check Attribution Ledger -> should fall back to Walk-In Employee (EMP-SFC-PRIMARY) at 100%
        ledgers = smriti.db.get_list(
            "SMRITI Attribution Ledger",
            filters={"invoice_reference": si.name},
            fields=["name", "employee", "revenue_credit"]
        )
        self.assertEqual(len(ledgers), 1)
        self.assertEqual(ledgers[0].employee, self.emp_p)
        self.assertEqual(flt(ledgers[0].revenue_credit), 10000.0)

        # Check Commission Event
        events = smriti.db.get_list(
            "SMRITI Commission Event",
            filters={"invoice_reference": si.name},
            fields=["name", "employee", "commission_rate", "commission_amount", "event_status", "attributed_revenue"]
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].employee, self.emp_p)
        self.assertEqual(flt(events[0].commission_rate), 2.0)
        self.assertEqual(flt(events[0].commission_amount), 200.0) # 10000 * 2%
        self.assertEqual(flt(events[0].attributed_revenue), 10000.0)
        self.assertEqual(events[0].event_status, "Processed")

        # Check Commission Ledger
        comm_ledgers = smriti.db.get_list(
            "SMRITI Commission Ledger",
            filters={"commission_event": events[0].name},
            fields=["name", "employee", "amount", "ledger_status"]
        )
        self.assertEqual(len(comm_ledgers), 1)
        self.assertEqual(comm_ledgers[0].employee, self.emp_p)
        self.assertEqual(flt(comm_ledgers[0].amount), 200.0)
        self.assertEqual(comm_ledgers[0].ledger_status, "Active")

    def test_commission_reversal_on_cancel(self):
        """Verify negative commission entries and active status cancellation on invoice reversal."""
        r_global = smriti.documents.new("SMRITI Commission Rule")
        r_global.rule_name = "Global Base Rule"
        r_global.commission_rate = 2.0
        r_global.company = self.company
        r_global.is_active = 1
        r_global.insert(ignore_permissions=True)

        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-02"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 5000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Cancel Invoice
        si.cancel()

        # Check all Commission Ledger entries for this invoice
        # Expecting 2: 1 original (Reversed), 1 negative reversal (Reversed)
        ledgers = smriti.db.get_list(
            "SMRITI Commission Ledger",
            filters={"employee": self.emp_p},
            fields=["name", "amount", "ledger_status", "reversal_reference"]
        )
        self.assertEqual(len(ledgers), 2)
        
        orig = [l for l in ledgers if l.amount > 0][0]
        self.assertEqual(orig.ledger_status, "Reversed")

        rev = [l for l in ledgers if l.amount < 0][0]
        self.assertEqual(rev.ledger_status, "Reversed")
        self.assertEqual(str(rev.reversal_reference), str(orig.name))
        self.assertEqual(flt(rev.amount), -100.0) # 5000 * 2% * -1

    def test_min_revenue_threshold(self):
        """Verify commission gross evaluates to 0 if monthly revenue threshold is not met."""
        fiscal_year = smriti.db.get_list("Fiscal Year", limit=1, pluck="name")[0]

        # Commission Rule with 5% rate and 20,000 threshold
        rule = smriti.documents.new("SMRITI Commission Rule")
        rule.rule_name = "High Performer Rule"
        rule.employee = self.emp_p
        rule.commission_rate = 5.0
        rule.min_revenue_threshold = 20000.0
        rule.company = self.company
        rule.is_active = 1
        rule.insert(ignore_permissions=True)

        # 1. First Invoice (Revenue ₹15,000 - under threshold)
        si1 = smriti.documents.new("Sales Invoice")
        si1.company = self.company
        si1.customer = self.customer
        si1.posting_date = "2026-06-05"
        si1.posting_time = "10:00:00"
        si1.set_posting_time = 1
        si1.debit_to = self.debit_to
        si1.currency = "INR"
        si1.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 15000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si1.insert(ignore_permissions=True)
        si1.submit()

        # Compute Monthly Payout preview -> should be 0 gross due to threshold check
        settle = generate_monthly_settlement(self.emp_p, self.company, fiscal_year, "Jun")
        self.assertEqual(flt(settle["gross_commission"]), 0.0)

        # 2. Second Invoice (Revenue ₹10,000 - brings total to ₹25,000 - meets threshold)
        si2 = smriti.documents.new("Sales Invoice")
        si2.company = self.company
        si2.customer = self.customer
        si2.posting_date = "2026-06-06"
        si2.posting_time = "10:00:00"
        si2.set_posting_time = 1
        si2.debit_to = self.debit_to
        si2.currency = "INR"
        si2.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 10000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si2.insert(ignore_permissions=True)
        si2.submit()

        # Compute Monthly Payout preview -> should now calculate commission on all active ledger entries (25,000 * 5% = 1250)
        settle = generate_monthly_settlement(self.emp_p, self.company, fiscal_year, "Jun")
        self.assertEqual(flt(settle["gross_commission"]), 1250.0)

    def test_monthly_settlement_adjustments_and_immutability(self):
        """Verify adjustments calculation, approval workflow, and lock-state checks."""
        fiscal_year = smriti.db.get_list("Fiscal Year", limit=1, pluck="name")[0]

        rule = smriti.documents.new("SMRITI Commission Rule")
        rule.rule_name = "Global Rule"
        rule.commission_rate = 10.0
        rule.company = self.company
        rule.is_active = 1
        rule.insert(ignore_permissions=True)

        # Submit Invoice generating ₹1,000 commission
        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-05"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 10000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # 1. Generate settlements draft
        generated = run_monthly_settlements(self.company, fiscal_year, "Jun")
        self.assertEqual(len(generated), 1)
        
        settle = smriti.documents.get("SMRITI Commission Settlement", generated[0])
        self.assertEqual(flt(settle.gross_commission), 1000.0)
        self.assertEqual(flt(settle.net_commission), 1000.0)
        self.assertEqual(flt(settle.settled_commission_amount), 1000.0)
        self.assertTrue(settle.settlement_from_date)
        self.assertTrue(settle.settlement_to_date)
        self.assertEqual(settle.status, "Draft")

        # 2. Add manual adjustments (+₹300 and -₹100)
        settle.append("adjustments", {
            "reason": "Special performance bonus",
            "amount": 300.0,
            "remarks": "approved by owner"
        })
        settle.append("adjustments", {
            "reason": "Uniform deduction",
            "amount": -100.0,
            "remarks": "deducted"
        })
        settle.save(ignore_permissions=True)

        # Reload and check net_commission is computed as ₹1,200
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        self.assertEqual(flt(settle.net_commission), 1200.0)
        self.assertEqual(flt(settle.settled_commission_amount), 1200.0)
        
        # Verify approval metadata populated automatically
        self.assertEqual(settle.adjustments[0].approved_by, "Administrator")
        self.assertTrue(settle.adjustments[0].approved_on)

        # 3. Transition to Approved
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.status = "Approved"
        settle.save(ignore_permissions=True)

        # Try to modify fields on Approved record -> should fail
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.gross_commission = 1500.0
        with self.assertRaises(frappe.ValidationError):
            settle.save(ignore_permissions=True)

        # Try to change status back to Draft -> should fail
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.status = "Draft"
        with self.assertRaises(frappe.ValidationError):
            settle.save(ignore_permissions=True)

        # 4. Transition Approved -> Paid (requires payment reference)
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.status = "Paid"
        with self.assertRaises(frappe.ValidationError):
            settle.save(ignore_permissions=True) # Fails due to missing payment reference

        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.status = "Paid"
        settle.payment_reference = "PAY-REF-SFC-001"
        settle.payment_date = "2026-06-30"
        settle.save(ignore_permissions=True) # Success

        # Try to edit Paid record -> should fail
        settle = smriti.documents.get("SMRITI Commission Settlement", settle.name)
        settle.payment_reference = "MODIFIED-REF"
        with self.assertRaises(frappe.ValidationError):
            settle.save(ignore_permissions=True)
