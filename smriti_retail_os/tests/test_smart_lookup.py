# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_smart_lookup.py
# @desc:    Test suite for SMRITI Universal Smart Lookup.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 9 (Tests)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
import unittest
from smriti_retail_os.services.lookup_service import LookupService


class TestSmartLookup(unittest.TestCase):
    def setUp(self):
        # Resolve HSN code for items
        self.hsn_code = frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            try:
                hsn = frappe.new_doc("GST HSN Code")
                hsn.name = "999999"
                hsn.hsn_code = "999999"
                hsn.insert(ignore_permissions=True)
                self.hsn_code = hsn.name
            except Exception:
                pass

    def test_search_and_validation(self):
        # 1. Test search Customer (which uses standard Customer)
        res = LookupService.search("Customer", limit=5)
        self.assertIsInstance(res, list)

        # 2. Test search Supplier
        res = LookupService.search("Supplier", limit=5)
        self.assertIsInstance(res, list)

        # 3. Test validate (validates non-existent Supplier)
        val = LookupService.validate("Supplier", "NONEXISTENT-SUPPLIER-SMRITI")
        self.assertFalse(val["exists"])

    def test_quick_create_customer(self):
        cust_name = "SMRITI Test Quick Customer A"
        # Cleanup
        frappe.db.delete("Customer", {"customer_name": cust_name})
        frappe.db.delete("Customer", {"name": cust_name})

        # Create
        res = LookupService.create("Customer", {
            "customer_name": cust_name,
            "mobile_no": "9876543210"
        })
        self.assertEqual(res["label"], cust_name)
        self.assertTrue(frappe.db.exists("Customer", res["value"]))

        # Cleanup
        frappe.db.delete("Customer", {"name": res["value"]})

    def test_quick_create_supplier(self):
        sup_name = "SMRITI Test Quick Supplier A"
        # Cleanup
        frappe.db.delete("SMRITI Supplier", {"supplier_name": sup_name})
        frappe.db.delete("SMRITI Supplier", {"name": sup_name})

        # Create
        res = LookupService.create("Supplier", {
            "supplier_name": sup_name,
            "mobile_no": "9876543211",
            "email_id": "quick_sup@smriti.com"
        })
        self.assertEqual(res["label"], sup_name)
        self.assertTrue(frappe.db.exists("SMRITI Supplier", res["value"]))

        # Cleanup
        frappe.db.delete("SMRITI Supplier", {"name": res["value"]})

    def test_recent_records(self):
        recents = LookupService.recent("Customer")
        self.assertIsInstance(recents, list)
        self.assertLessEqual(len(recents), 5)
