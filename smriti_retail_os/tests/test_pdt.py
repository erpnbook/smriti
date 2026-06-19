# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_pdt.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.tests.test_psv import TestPSV
from smriti_retail_os.balance_engine import get_party_balance
from smriti_retail_os.services.forecasting_service import (
    calculate_weekly_velocity_stats,
    calculate_weeks_of_cover,
    calculate_predicted_stockout_date
)
from smriti_retail_os.services.optimization_service import optimize_network_transfer
from smriti_retail_os.services.twin_quality_service import evaluate_twin_quality, evaluate_variant_curve
from smriti_retail_os.services.simulation_service import run_sandbox_simulation
from smriti_retail_os.services.pdt_service import rebuild_twin_cache, enqueue_rebuild_twin_cache

class TestPDT(TestPSV):
    def setUp(self):
        super().setUp()
        frappe.db.delete("SMRITI SKU Twin")
        frappe.db.commit()

    def test_sku_twin_creation_and_uniqueness(self):
        # 1. Assert DocType exists
        self.assertTrue(frappe.db.exists("DocType", "SMRITI SKU Twin"))
        
        # 2. Insert standard twin
        twin1 = frappe.get_doc({
            "doctype": "SMRITI SKU Twin",
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item,
            "current_stock": 10.0,
            "weekly_velocity": 2.0,
            "twin_state": "Healthy"
        })
        twin1.insert(ignore_permissions=True)
        frappe.db.commit()

        # 3. Assert duplicate insert throws ValidationError
        twin2 = frappe.get_doc({
            "doctype": "SMRITI SKU Twin",
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item,
            "current_stock": 15.0,
            "weekly_velocity": 4.0,
            "twin_state": "Healthy"
        })
        self.assertRaises(frappe.ValidationError, twin2.insert, ignore_permissions=True)

    def test_forecasting_logic(self):
        # 1. Seed some sales entries in ledger (qty < 0)
        from smriti_retail_os.ledger_engine import make_ledger_entry
        from frappe.utils import add_days, now_datetime
        
        # Add 5 sales of 10 units each on different days
        for i in range(5):
            posting_time = add_days(now_datetime(), -i)
            make_ledger_entry(
                company=self.company,
                posting_datetime=posting_time,
                party_stock_account=self.account_name,
                item_code=self.item,
                qty=-10.0,
                voucher_type="Sales",
                voucher_no=f"INV-TEST-{i}"
            )
        frappe.db.commit()

        # 2. Calculate velocity stats
        stats = calculate_weekly_velocity_stats(self.company, self.account_name, self.item)
        self.assertGreater(stats["weekly_velocity"], 0.0)
        self.assertGreater(stats["velocity_std_dev"], 0.0)
        self.assertTrue(10.0 <= stats["velocity_confidence"] <= 100.0)

        # 3. WOC and Stockout Date
        woc = calculate_weeks_of_cover(50.0, stats["weekly_velocity"])
        self.assertEqual(woc, round(50.0 / stats["weekly_velocity"], 2))

        stockout = calculate_predicted_stockout_date(50.0, stats["weekly_velocity"])
        self.assertIsNotNone(stockout)

    def test_cost_aware_rebalancing_optimization(self):
        # 1. Create a second PSA (Pune Outlet) in same West zone
        pune_psa = f"{self.customer}-Pune Outlet"
        if not frappe.db.exists("SMRITI Party Stock Account", pune_psa):
            pune = frappe.new_doc("SMRITI Party Stock Account")
            pune.company = self.company
            pune.customer = self.customer
            pune.location_name = "Pune Outlet"
            pune.zone = "West"
            pune.insert(ignore_permissions=True)
            
        # Ensure Mumbai target PSA has same zone
        frappe.db.set_value("SMRITI Party Stock Account", self.account_name, "zone", "West")
        frappe.db.commit()

        # 2. Seed Pune PSA with excess stock (100 units)
        from smriti_retail_os.psv_service import import_opening_balances
        import_opening_balances(self.company, pune_psa, [{"item_code": self.item, "qty": 100.0}])
        
        # Seed Mumbai PSA with 0 stock
        import_opening_balances(self.company, self.account_name, [{"item_code": self.item, "qty": 0.0}])

        # 3. Create a Reorder Rule for Mumbai PSA
        rule = frappe.new_doc("SMRITI PSV Reorder Rule")
        rule.company = self.company
        rule.party_stock_account = self.account_name
        rule.item_variant = self.item
        rule.safety_stock = 20.0
        rule.active = 1
        rule.insert(ignore_permissions=True)
        frappe.db.commit()

        # 4. Optimize transfer
        opt = optimize_network_transfer(self.company, self.account_name, self.item, 0.0)
        self.assertEqual(opt["recommendation_type"], "TRANSFER")
        self.assertEqual(opt["recommended_transfer_source"], pune_psa)
        self.assertEqual(opt["recommended_transfer_qty"], 20.0)
        self.assertGreater(opt["transfer_benefit_score"], 0.0)
        self.assertIn("EXCESS_WOC_AT_SOURCE", opt["reason_codes"])

    def test_variant_curve_detection(self):
        # Ensure Item Attribute "Test Curve Attribute" exists with correct values
        if frappe.db.exists("Item Attribute", "Test Curve Attribute"):
            frappe.delete_doc("Item Attribute", "Test Curve Attribute", force=True)

        attr = frappe.new_doc("Item Attribute")
        attr.attribute_name = "Test Curve Attribute"
        attr.append("item_attribute_values", {"attribute_value": "S", "abbr": "S"})
        attr.append("item_attribute_values", {"attribute_value": "M", "abbr": "M"})
        attr.insert(ignore_permissions=True)

        # 1. Create a template style item
        template_item = "TEST-STYLE-SHIRT"
        if not frappe.db.exists("Item", template_item):
            itm = frappe.new_doc("Item")
            itm.item_code = template_item
            itm.item_name = "Test Style Shirt"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.has_variants = 1
            itm.append("attributes", {"attribute": "Test Curve Attribute"})
            itm.insert(ignore_permissions=True)

        # 2. Create variant items
        var_s = "TEST-STYLE-SHIRT-S"
        if not frappe.db.exists("Item", var_s):
            itm = frappe.new_doc("Item")
            itm.item_code = var_s
            itm.item_name = "Test Style Shirt S"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.variant_of = template_item
            itm.append("attributes", {"attribute": "Test Curve Attribute", "attribute_value": "S"})
            itm.insert(ignore_permissions=True)

        var_m = "TEST-STYLE-SHIRT-M"
        if not frappe.db.exists("Item", var_m):
            itm = frappe.new_doc("Item")
            itm.item_code = var_m
            itm.item_name = "Test Style Shirt M"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.variant_of = template_item
            itm.append("attributes", {"attribute": "Test Curve Attribute", "attribute_value": "M"})
            itm.insert(ignore_permissions=True)

        # 3. Seed balance: Shirt-S has 5.0, Shirt-M has 0.0 (broken size curve!)
        from smriti_retail_os.psv_service import import_opening_balances
        import_opening_balances(self.company, self.account_name, [{"item_code": var_s, "qty": 5.0}])

        curve = evaluate_variant_curve(var_s, self.account_name)
        self.assertEqual(curve["variant_curve_status"], "Broken")
        self.assertEqual(curve["missing_sizes"], "M")

    def test_sandbox_simulation_isolation(self):
        # 1. Insert standard twin record in database
        twin = frappe.get_doc({
            "doctype": "SMRITI SKU Twin",
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item,
            "current_stock": 20.0,
            "weekly_velocity": 4.0,
            "weeks_of_cover": 5.0,
            "twin_state": "Healthy"
        })
        twin.insert(ignore_permissions=True)
        frappe.db.commit()

        # 2. Run simulation with a 1.5x velocity multiplier
        config = {
            "target_psas": [self.account_name],
            "item_codes": [self.item],
            "velocity_multiplier": 1.5
        }
        simulated = run_sandbox_simulation(config)
        
        self.assertEqual(len(simulated), 1)
        self.assertEqual(simulated[0]["weekly_velocity"], 6.0) # 4.0 * 1.5
        self.assertEqual(simulated[0]["weeks_of_cover"], round(20.0 / 6.0, 2))
        
        # 3. Assert DB twin record remains unmodified
        db_twin = frappe.get_doc("SMRITI SKU Twin", twin.name)
        self.assertEqual(db_twin.weekly_velocity, 4.0)

    def test_rebuild_lock_prevention(self):
        # 1. Enqueue job
        enqueue_rebuild_twin_cache(self.company, self.account_name, self.item, "FULL_REBUILD")
        
        # 2. Verify lock key is set in cache
        lock_key = f"pdt_rebuild:{self.company}:{self.account_name}:{self.item}"
        self.assertTrue(frappe.cache().get_value(lock_key))

        # 3. Call rebuild directly (this will process and clear lock)
        rebuild_twin_cache(self.company, self.account_name, self.item, "FULL_REBUILD")
        self.assertFalse(frappe.cache().get_value(lock_key))
        
        # 4. Verify SMRITI SKU Twin was created
        twin_exists = frappe.db.exists("SMRITI SKU Twin", {
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item
        })
        self.assertTrue(twin_exists)

    def test_pdt_dashboard_list(self):
        # 1. Create a twin record
        twin = frappe.get_doc({
            "doctype": "SMRITI SKU Twin",
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item,
            "current_stock": 30.0,
            "weekly_velocity": 5.0,
            "weeks_of_cover": 6.0,
            "twin_state": "Healthy"
        })
        twin.insert(ignore_permissions=True)
        frappe.db.commit()

        # 2. Call the API method
        from smriti_retail_os.api.pdt_api import get_pdt_dashboard_list
        res = get_pdt_dashboard_list({"twin_state": "Healthy"})
        
        self.assertGreater(len(res["twins"]), 0)
        self.assertEqual(res["twins"][0]["item_code"], self.item)
        self.assertEqual(res["stats"]["healthy"], 1)
        self.assertGreater(len(res["psas"]), 0)

