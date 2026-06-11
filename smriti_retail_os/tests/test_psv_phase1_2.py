# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_psv_phase1_2.py
# @description: Unit tests for SMRITI Retail OS - PSV Phase 1.2 Inventory Productivity Metric.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-11
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days
from smriti_retail_os.psv_service import get_inventory_productivity_metrics

class TestPSVPhase1_2(FrappeTestCase):
    def setUp(self):
        # Clear database records to ensure clean slate
        frappe.db.delete("PSV Ledger Entry")
        frappe.db.delete("SMRITI Party Stock Ledger Entry")
        frappe.db.delete("Sales Invoice Item")
        frappe.db.delete("Sales Invoice")
        frappe.db.delete("Item Price")
        frappe.db.delete("Item")
        frappe.db.commit()

        # Create basic UOM, Item Group, and Company if they don't exist
        self.uom = frappe.db.exists("UOM", "Nos") or frappe.db.get_value("UOM", {}, "name")
        if not self.uom:
            uom_doc = frappe.new_doc("UOM")
            uom_doc.uom_name = "Nos"
            uom_doc.insert(ignore_permissions=True)
            self.uom = uom_doc.name

        self.item_group = frappe.db.exists("Item Group", "All Item Groups") or frappe.db.get_value("Item Group", {}, "name")
        if not self.item_group:
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "All Item Groups"
            ig.is_group = 0
            ig.insert(ignore_permissions=True)
            self.item_group = ig.name

        self.company = "Test PSV Company 1.2"
        if not frappe.db.exists("Company", self.company):
            comp = frappe.new_doc("Company")
            comp.company_name = self.company
            comp.abbr = "TPC2"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)

        self.customer = "Test Customer 1.2"
        if not frappe.db.exists("Customer", self.customer):
            cust = frappe.new_doc("Customer")
            cust.customer_name = self.customer
            cust.customer_type = "Individual"
            cust.insert(ignore_permissions=True)

        # Create valid GST HSN Code record for India Compliance
        self.hsn_code = frappe.db.exists("GST HSN Code", "998311") or frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "998311"
            hsn.description = "Test Services"
            hsn.insert(ignore_permissions=True)
            self.hsn_code = hsn.name

        # Set up threshold in PSV System Settings
        settings = frappe.get_single("PSV System Settings")
        settings.star_velocity_threshold = 1.0
        settings.save(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.db.rollback()

    def test_01_realized_price_calculation(self):
        # Create an Item
        item_code = "ITEM-REALIZED-PRICE"
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = self.item_group
        item.stock_uom = self.uom
        item.gst_hsn_code = self.hsn_code
        item.valuation_rate = 100.0
        item.insert(ignore_permissions=True)

        # Create Sales Invoice 1
        si1 = frappe.new_doc("Sales Invoice")
        si1.company = self.company
        si1.customer = self.customer
        si1.append("items", {
            "item_code": item_code,
            "qty": 5,
            "rate": 150.0,
            "base_amount": 750.0
        })
        si1.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        frappe.db.set_value("Sales Invoice", si1.name, {"docstatus": 1})
        frappe.db.sql("UPDATE `tabSales Invoice Item` SET docstatus = 1 WHERE parent = %s", (si1.name,))

        # Create Sales Invoice 2
        si2 = frappe.new_doc("Sales Invoice")
        si2.company = self.company
        si2.customer = self.customer
        si2.append("items", {
            "item_code": item_code,
            "qty": 5,
            "rate": 250.0,
            "base_amount": 1250.0
        })
        si2.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        frappe.db.set_value("Sales Invoice", si2.name, {"docstatus": 1})
        frappe.db.sql("UPDATE `tabSales Invoice Item` SET docstatus = 1 WHERE parent = %s", (si2.name,))

        # Add some shadow ledger entries
        # Qty sold: 10 units over last 14 days (velocity = 5.0 units/wk)
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-1', %s, %s, -10, %s, 'Sales')
        """, (self.company, item_code, add_days(now_datetime(), -2)))

        # Current balance: 10 units (so inventory_value = 10 * 100 = 1000)
        # Gross Margin = sales_qty * (realized_price - cost) = 10 * (200 - 100) = 1000
        # GMROI = 1000 / 1000 = 1.0
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-2', %s, %s, 20, %s, 'Opening')
        """, (self.company, item_code, add_days(now_datetime(), -10)))

        metrics = get_inventory_productivity_metrics(self.company, timespan_days=14)
        
        # Verify realized price is (5*150 + 5*250) / 10 = 200
        self.assertEqual(len(metrics["all_items"]), 1)
        item_metric = metrics["all_items"][0]
        self.assertEqual(item_metric["item_code"], item_code)
        self.assertEqual(item_metric["price"], 200.0)
        self.assertEqual(item_metric["gmroi"], 1.0)
        self.assertEqual(item_metric["velocity"], 5.0)  # 10 units / 2 weeks = 5.0 units/wk

    def test_02_star_sku_classification(self):
        # Star: velocity >= threshold (1.0) and GMROI >= 2.0
        item_code = "ITEM-STAR"
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = self.item_group
        item.stock_uom = self.uom
        item.gst_hsn_code = self.hsn_code
        item.valuation_rate = 100.0
        item.insert(ignore_permissions=True)

        # Sales Invoice bypassing complex validations
        si = frappe.new_doc("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.append("items", {
            "item_code": item_code,
            "qty": 10,
            "rate": 300.0,
            "base_amount": 3000.0
        })
        si.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        frappe.db.set_value("Sales Invoice", si.name, {"docstatus": 1})
        frappe.db.sql("UPDATE `tabSales Invoice Item` SET docstatus = 1 WHERE parent = %s", (si.name,))

        # Sales: 10 units over last 14 days (velocity = 5.0 units/wk >= 1.0 threshold)
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-STAR-1', %s, %s, -10, %s, 'Sales')
        """, (self.company, item_code, add_days(now_datetime(), -2)))

        # Balance = 5 units (inventory_value = 5 * 100 = 500)
        # Gross margin = 10 * (300 - 100) = 2000
        # GMROI = 2000 / 500 = 4.0 >= 2.0
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-STAR-2', %s, %s, 15, %s, 'Opening')
        """, (self.company, item_code, add_days(now_datetime(), -10)))

        metrics = get_inventory_productivity_metrics(self.company, timespan_days=14)
        item_metric = metrics["all_items"][0]
        self.assertEqual(item_metric["category"], "Star")
        self.assertEqual(item_metric["action"], "Increase Stock")
        self.assertEqual(metrics["summary"]["star"], 1)

    def test_03_stockout_winner_classification(self):
        # Stockout Winner: stock <= 0 and sales > 0 (margin > 0)
        item_code = "ITEM-STOCKOUT"
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = self.item_group
        item.stock_uom = self.uom
        item.gst_hsn_code = self.hsn_code
        item.valuation_rate = 100.0
        item.insert(ignore_permissions=True)

        # Sales price = 150.0 (margin = 50.0)
        si = frappe.new_doc("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.append("items", {
            "item_code": item_code,
            "qty": 10,
            "rate": 150.0,
            "base_amount": 1500.0
        })
        si.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        frappe.db.set_value("Sales Invoice", si.name, {"docstatus": 1})
        frappe.db.sql("UPDATE `tabSales Invoice Item` SET docstatus = 1 WHERE parent = %s", (si.name,))

        # Sales: 10 units
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-SO-1', %s, %s, -10, %s, 'Sales')
        """, (self.company, item_code, add_days(now_datetime(), -2)))

        # No opening balance/stock, so current balance = -10 (which is <= 0)
        # Margin = 10 * 50 = 500 > 0
        metrics = get_inventory_productivity_metrics(self.company, timespan_days=14)
        item_metric = metrics["all_items"][0]
        self.assertEqual(item_metric["category"], "Stockout Winner")
        self.assertEqual(item_metric["action"], "Replenish Urgent")
        self.assertIsNone(item_metric["gmroi"])
        self.assertEqual(metrics["summary"]["stockout_winner"], 1)

    def test_04_productivity_score_scaling(self):
        # Score = 0.6 * Norm_GMROI + 0.4 * Norm_Vel
        # Norm_GMROI = min(GMROI / 3.0, 1.0) * 100
        # Norm_Vel = min(Velocity / 5.0, 1.0) * 100
        # With huge GMROI and huge Velocity, verify score is capped at 100.
        item_code = "ITEM-MAX-SCORE"
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = self.item_group
        item.stock_uom = self.uom
        item.gst_hsn_code = self.hsn_code
        item.valuation_rate = 10.0
        item.insert(ignore_permissions=True)

        si = frappe.new_doc("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.append("items", {
            "item_code": item_code,
            "qty": 100,
            "rate": 1000.0,
            "base_amount": 100000.0
        })
        si.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        frappe.db.set_value("Sales Invoice", si.name, {"docstatus": 1})
        frappe.db.sql("UPDATE `tabSales Invoice Item` SET docstatus = 1 WHERE parent = %s", (si.name,))

        # Velocity = 100 / 1 week = 100 units/wk (Norm_Vel = min(100/5.0, 1.0) * 100 = 100)
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-MAX-1', %s, %s, -100, %s, 'Sales')
        """, (self.company, item_code, add_days(now_datetime(), -2)))

        # Balance = 1 unit (inv_value = 10)
        # Margin = 100 * (1000 - 10) = 99000
        # GMROI = 99000 / 10 = 9900 (Norm_GMROI = min(9900/3.0, 1.0) * 100 = 100)
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, item_code, qty, posting_datetime, voucher_type)
            VALUES 
            ('TEST-LE-MAX-2', %s, %s, 101, %s, 'Opening')
        """, (self.company, item_code, add_days(now_datetime(), -5)))

        metrics = get_inventory_productivity_metrics(self.company, timespan_days=7)
        item_metric = metrics["all_items"][0]
        self.assertEqual(item_metric["score"], 100.0)

    def test_05_performance_under_scale(self):
        # Verify database scaling (O(1) queries outside of setup)
        # Create 10 dummy items
        for i in range(10):
            code = f"SCALE-ITEM-{i}"
            if not frappe.db.exists("Item", code):
                item = frappe.new_doc("Item")
                item.item_code = code
                item.item_name = code
                item.item_group = self.item_group
                item.stock_uom = self.uom
                item.gst_hsn_code = self.hsn_code
                item.valuation_rate = 10.0
                item.insert(ignore_permissions=True)

        # Measure query counts during call if sql_log is available
        sql_log_attr = "sql_log"
        local_has_log = hasattr(frappe.local, sql_log_attr) if hasattr(frappe, "local") else False
        db_has_log = hasattr(frappe.db, sql_log_attr) if hasattr(frappe, "db") else False

        start_queries = 0
        if local_has_log:
            start_queries = len(frappe.local.sql_log)
        elif db_has_log:
            start_queries = len(frappe.db.sql_log)

        get_inventory_productivity_metrics(self.company, timespan_days=30)

        end_queries = 0
        if local_has_log:
            end_queries = len(frappe.local.sql_log)
        elif db_has_log:
            end_queries = len(frappe.db.sql_log)

        query_count = end_queries - start_queries
        if local_has_log or db_has_log:
            self.assertTrue(query_count < 15)

    def test_06_transparency_and_metadata(self):
        # 1. Test get_inventory_productivity_methodology returns proper versioning and author metadata
        from smriti_retail_os.psv_service import get_inventory_productivity_methodology
        methodology = get_inventory_productivity_methodology()
        
        self.assertEqual(methodology["version"], "1.0")
        self.assertEqual(methodology["effective_date"], "2026-06-11")
        self.assertIn("smriti_version", methodology)
        self.assertEqual(methodology["author"]["name"], "Jawahar R. Mallah")
        self.assertEqual(methodology["author"]["title"], "Founder, AITDL (AI Technology & Development Lab)")
        
        # 2. Test metrics returns warnings, confidence, and txn_count
        item_code = "ITEM-METADATA-TEST"
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = self.item_group
        item.stock_uom = self.uom
        item.gst_hsn_code = self.hsn_code
        item.valuation_rate = 0.0  # Should trigger "Cost Data Missing" warning
        item.insert(ignore_permissions=True)

        # Sales: 25 units in 5 separate transactions (Should trigger High confidence)
        for i in range(5):
            frappe.db.sql("""
                INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
                (name, company, item_code, qty, posting_datetime, voucher_type, voucher_no)
                VALUES 
                (%s, %s, %s, -5, %s, 'Sales', %s)
            """, (f"TEST-TXN-{i}", self.company, item_code, add_days(now_datetime(), -1), f"VOUCHER-{i}"))

        # Stock balance: -25 (Should trigger "Inventory Adjustment Required" warning)
        metrics = get_inventory_productivity_metrics(self.company, timespan_days=14)
        item_metric = [m for m in metrics["all_items"] if m["item_code"] == item_code]
        self.assertEqual(len(item_metric), 1)
        m = item_metric[0]
        
        self.assertEqual(m["confidence"], "High")
        self.assertIn("Cost Data Missing", m["warnings"])
        self.assertIn("Inventory Adjustment Required", m["warnings"])
        self.assertIn("Using Fallback Selling Price", m["warnings"])
        self.assertEqual(m["txn_count"], 5)
