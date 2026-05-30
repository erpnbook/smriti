# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_item_master_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_item_master_api.py
# @description: Unit tests for dedicated Sizewise Item Master CRUD APIs.
# @author: Antigravity <antigravity@google.com>
# @version: 1.0.0
# @license: MIT
#

import frappe
import unittest
from smriti_retail_os.item_master_api import (
    generate_ean13_barcode,
    get_style_details,
    create_style_with_variants,
    delete_size_variant
)

class TestSmritiRetailItemMasterAPI(unittest.TestCase):

    def setUp(self):
        # 1. Resolve basic test dependencies
        self.company = frappe.db.exists("Company", "_Test Company") or frappe.db.get_value("Company", {}, "name")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name
            
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)

        # Create store manager role link to prevent permission errors in tests
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"}):
            r = frappe.new_doc("Has Role")
            r.parent = frappe.session.user
            r.parenttype = "User"
            r.parentfield = "roles"
            r.role = "SMRITI Store Manager"
            r.insert(ignore_permissions=True)
            
        frappe.db.commit()
        
        # Ensure clean state for our test style code
        self.style_code = "TST-JORDAN-5"
        self.cleanup_records()

    def tearDown(self):
        self.cleanup_records()
        frappe.db.delete("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"})
        frappe.db.commit()

    def cleanup_records(self):
        # Deletes any variants and the parent template
        variants = frappe.db.get_all("Item", filters={"variant_of": self.style_code}, pluck="name")
        for var in variants:
            frappe.db.delete("Item Barcode", {"parent": var})
            frappe.db.delete("Item Price", {"item_code": var})
            frappe.delete_doc("Item", var, ignore_missing=True, force=True)
            
        if frappe.db.exists("Item", self.style_code):
            frappe.delete_doc("Item", self.style_code, ignore_missing=True, force=True)
            
        frappe.db.delete("Brand", {"name": "Nike Jordan"})
        frappe.db.delete("GST HSN Code", {"hsn_code": "640311"})
        frappe.db.commit()

    def test_ean13_barcode_generation(self):
        """
        Verifies that generate_ean13_barcode creates unique mathematically correct 13-digit EAN-13 barcodes.
        """
        barcode = generate_ean13_barcode()
        self.assertEqual(len(barcode), 13)
        self.assertTrue(barcode.startswith("23"))
        
        # Verify check-digit calculation
        body = barcode[:-1]
        odds = sum(int(body[i]) for i in range(0, 12, 2))
        evens = sum(int(body[i]) for i in range(1, 12, 2))
        total = odds + (evens * 3)
        check_digit = (10 - (total % 10)) % 10
        self.assertEqual(int(barcode[-1]), check_digit)

    def test_create_style_and_variants(self):
        """
        Verifies style template creation and size variants pivot grid insertion.
        """
        base_details = {
            "article_no": self.style_code,
            "description": "Jordan 5 Retro Sneakers",
            "color": "RED",
            "brand": "Nike Jordan",
            "item_group": "Products",
            "cost_price": 3000,
            "mrp": 6000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "",
            "product_tax_group": ""
        }
        
        sizes_config = [
            { "size": "8", "active": True, "barcode_mode": "auto", "manual_barcode": "" },
            { "size": "9", "active": True, "barcode_mode": "manual", "manual_barcode": "8908889990001" },
            { "size": "10", "active": False, "barcode_mode": "auto", "manual_barcode": "" }
        ]

        res = create_style_with_variants(
            base_details=frappe.as_json(base_details),
            sizes_config=frappe.as_json(sizes_config)
        )
        
        self.assertTrue(res["success"])
        self.assertEqual(res["created_count"], 2)
        
        # Verify parent template exists
        self.assertTrue(frappe.db.exists("Item", self.style_code))
        parent = frappe.get_doc("Item", self.style_code)
        self.assertEqual(parent.brand, "Nike Jordan")
        self.assertEqual(parent.has_variants, 1)

        # Verify Variant 8 (Auto barcode)
        v8_code = f"{self.style_code}-RED-8"
        self.assertTrue(frappe.db.exists("Item", v8_code))
        v8_bar = frappe.db.get_value("Item Barcode", {"parent": v8_code}, "barcode")
        self.assertIsNotNone(v8_bar)
        self.assertEqual(len(v8_bar), 13)
        self.assertTrue(v8_bar.startswith("23"))

        # Verify Variant 9 (Manual barcode)
        v9_code = f"{self.style_code}-RED-9"
        self.assertTrue(frappe.db.exists("Item", v9_code))
        v9_bar = frappe.db.get_value("Item Barcode", {"parent": v9_code}, "barcode")
        self.assertEqual(v9_bar, "8908889990001")

        # Verify Variant 10 (Inactive - skipped)
        v10_code = f"{self.style_code}-RED-10"
        self.assertFalse(frappe.db.exists("Item", v10_code))

        # Verify get_style_details reads the style correctly
        details = get_style_details(self.style_code)
        self.assertTrue(details["exists"])
        self.assertEqual(details["description"], "Jordan 5 Retro Sneakers")
        self.assertEqual(details["color"], "RED")
        self.assertEqual(len(details["sizes"]), 2)

    def test_delete_size_variant(self):
        """
        Verifies that delete_size_variant purges a specific variant and barcode mappings cleanly.
        """
        base_details = {
            "article_no": self.style_code,
            "description": "Jordan 5 Retro Sneakers",
            "color": "RED",
            "brand": "Nike Jordan",
            "item_group": "Products",
            "cost_price": 3000,
            "mrp": 6000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "",
            "product_tax_group": ""
        }
        
        sizes_config = [
            { "size": "11", "active": True, "barcode_mode": "auto", "manual_barcode": "" }
        ]

        create_style_with_variants(
            base_details=frappe.as_json(base_details),
            sizes_config=frappe.as_json(sizes_config)
        )
        
        v11_code = f"{self.style_code}-RED-11"
        self.assertTrue(frappe.db.exists("Item", v11_code))
        
        # Trigger clean delete
        del_res = delete_size_variant(v11_code)
        self.assertTrue(del_res["success"])
        
        # Verify completely purged
        self.assertFalse(frappe.db.exists("Item", v11_code))
        self.assertFalse(frappe.db.exists("Item Barcode", {"parent": v11_code}))
        self.assertFalse(frappe.db.exists("Item Price", {"item_code": v11_code}))
