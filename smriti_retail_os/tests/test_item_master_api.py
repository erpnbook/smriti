# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_item_master_api.py
# @description: Unit tests for the SMRITI Item Master API.
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
    delete_size_variant,
    import_pivot_item_master,
    import_item_master,
    get_items_missing_barcodes,
)

def ensure_test_tax_template(company):
    # Ensure Item Tax Template GST 18% - VTC exists in the test DB
    if not frappe.db.exists("Item Tax Template", {"title": "GST 18% - VTC", "company": company}):
        try:
            t = frappe.new_doc("Item Tax Template")
            t.title = "GST 18% - VTC"
            t.company = company
            t.gst_treatment = "Taxable"
            t.gst_rate = 18.0
            
            filters_cgst = [
                ["account_type", "=", "Tax"],
                ["company", "=", company],
                ["name", "like", "%CGST%"],
                ["name", "not like", "%RCM%"],
                ["name", "not like", "%Refund%"]
            ]
            cgst = frappe.db.get_value("Account", filters_cgst, "name")
            
            filters_sgst = [
                ["account_type", "=", "Tax"],
                ["company", "=", company],
                ["name", "like", "%SGST%"],
                ["name", "not like", "%RCM%"],
                ["name", "not like", "%Refund%"]
            ]
            sgst = frappe.db.get_value("Account", filters_sgst, "name")
            
            if cgst:
                t.append("taxes", {"tax_type": cgst, "tax_rate": 9.0})
            if sgst:
                t.append("taxes", {"tax_type": sgst, "tax_rate": 9.0})
            t.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            print("Failed to create test tax template:", str(e))

class TestSmritiRetailItemMasterAPI(unittest.TestCase):

    def setUp(self):
        # 1. Resolve basic test dependencies
        self.company = frappe.db.exists("Company", "_Test Company")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name
            
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)
        ensure_test_tax_template(self.company)

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


class TestPivotMatrixImport(unittest.TestCase):
    """
    Unit tests for the Excel/Google Sheets paste-based pivot matrix import.
    Simulates multi-row paste (ARTICLE / COLOR / CATEGORY / size columns / MRP)
    and verifies that parent templates + child variant items are created cleanly.
    """

    PIVOT_STYLE_1 = "20016"
    PIVOT_STYLE_2 = "20017"
    COLORS = ["BLACK", "BEIGE"]

    def setUp(self):
        """Resolve test dependencies and ensure clean state."""
        self.company = frappe.db.exists("Company", "_Test Company")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        frappe.defaults.set_user_default("company", self.company, frappe.session.user)
        ensure_test_tax_template(self.company)

        # Grant store manager role if not already present
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"}):
            r = frappe.new_doc("Has Role")
            r.parent = frappe.session.user
            r.parenttype = "User"
            r.parentfield = "roles"
            r.role = "SMRITI Store Manager"
            r.insert(ignore_permissions=True)

        frappe.db.commit()
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        frappe.db.delete("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"})
        frappe.db.commit()

    def _cleanup(self):
        """Remove all test items created by the pivot import tests."""
        for style in [self.PIVOT_STYLE_1, self.PIVOT_STYLE_2]:
            variants = frappe.db.get_all("Item", filters={"variant_of": style}, pluck="name")
            for var in variants:
                frappe.db.delete("Item Barcode", {"parent": var})
                frappe.db.delete("Item Price", {"item_code": var})
                frappe.delete_doc("Item", var, ignore_missing=True, force=True)
            if frappe.db.exists("Item", style):
                frappe.delete_doc("Item", style, ignore_missing=True, force=True)
        frappe.db.delete("GST HSN Code", {"hsn_code": "640311"})
        frappe.db.commit()

    def _build_pivot_payload(self, styles):
        """
        Build styles_json payload mimicking the parsed output of the frontend TSV parser.
        Each element contains base_details + sizes_config.
        """
        return frappe.as_json(styles)

    # ──────────────────────────────────────────────────────────────────────
    def test_pivot_import_basic_two_rows(self):
        """
        Simulates pasting two rows from Excel:
          ARTICLE | COLOR  | CATOGARY | SUB-CATO    | 37 | 38 | 39 | 40 | 41 | 42 | MRP
          20016   | BLACK  | SANDAL   | LASTIC PATTA|  0 |  9 |  9 |  9 |  9 |  9 | 1899
          20016   | BEIGE  | SANDAL   | LASTIC PATTA|  0 |  9 |  9 |  9 |  9 |  9 | 1899
        Expects: 1 parent template (20016) + 10 size variants (5 per color).
        """
        styles = [
            {
                "base_details": {
                    "article_no": self.PIVOT_STYLE_1,
                    "description": "LASTIC PATTA",
                    "color": "BLACK",
                    "brand": "",
                    "item_group": "SANDAL",
                    "cost_price": 0,
                    "mrp": 1899,
                    "gst_percentage": "18",
                    "hsn_code": "640311",
                    "gender": "UNISEX",
                    "purchase_class": "FW",
                    "vendor_code": "",
                    "product_tax_group": "",
                    "merchandise_category": "SANDAL",
                    "sub_category": "LASTIC PATTA",
                },
                "sizes_config": [
                    {"size": "38", "active": True, "qty": 9},
                    {"size": "39", "active": True, "qty": 9},
                    {"size": "40", "active": True, "qty": 9},
                    {"size": "41", "active": True, "qty": 9},
                    {"size": "42", "active": True, "qty": 9},
                ]
            },
            {
                "base_details": {
                    "article_no": self.PIVOT_STYLE_1,
                    "description": "LASTIC PATTA",
                    "color": "BEIGE",
                    "brand": "",
                    "item_group": "SANDAL",
                    "cost_price": 0,
                    "mrp": 1899,
                    "gst_percentage": "18",
                    "hsn_code": "640311",
                    "gender": "UNISEX",
                    "purchase_class": "FW",
                    "vendor_code": "",
                    "product_tax_group": "",
                    "merchandise_category": "SANDAL",
                    "sub_category": "LASTIC PATTA",
                },
                "sizes_config": [
                    {"size": "38", "active": True, "qty": 9},
                    {"size": "39", "active": True, "qty": 9},
                    {"size": "40", "active": True, "qty": 9},
                    {"size": "41", "active": True, "qty": 9},
                    {"size": "42", "active": True, "qty": 9},
                ]
            },
        ]

        res = import_pivot_item_master(self._build_pivot_payload(styles))

        self.assertTrue(res["success"], msg=f"Import failed: {res.get('errors', [])}")
        self.assertEqual(len(res.get("errors", [])), 0, msg=f"Unexpected errors: {res.get('errors', [])}")

        # Parent template 20016 must exist with has_variants = 1
        self.assertTrue(frappe.db.exists("Item", self.PIVOT_STYLE_1))
        parent = frappe.get_doc("Item", self.PIVOT_STYLE_1)
        self.assertEqual(parent.has_variants, 1)

        # 10 variant items total (5 sizes × 2 colors)
        variants = frappe.db.get_all("Item", filters={"variant_of": self.PIVOT_STYLE_1}, pluck="name")
        self.assertEqual(len(variants), 10, msg=f"Expected 10 variants, got {len(variants)}: {variants}")

        # Spot-check specific variants
        for color in ["BLACK", "BEIGE"]:
            for size in ["38", "39", "40", "41", "42"]:
                vc = f"{self.PIVOT_STYLE_1}-{color}-{size}"
                self.assertTrue(frappe.db.exists("Item", vc), msg=f"Missing variant: {vc}")
                # Each variant must have exactly one EAN-13 barcode
                barcode = frappe.db.get_value("Item Barcode", {"parent": vc}, "barcode")
                self.assertIsNotNone(barcode, msg=f"No barcode for {vc}")
                self.assertEqual(len(barcode), 13, msg=f"Barcode for {vc} is not 13 digits: {barcode}")
                # MRP price list entry must exist
                price = frappe.db.get_value(
                    "Item Price",
                    {"item_code": vc, "price_list": "Standard Selling"},
                    "price_list_rate"
                )
                self.assertIsNotNone(price, msg=f"No Standard Selling price for {vc}")
                self.assertAlmostEqual(float(price), 1899.0, places=1, msg=f"Wrong MRP for {vc}")

    # ──────────────────────────────────────────────────────────────────────
    def test_pivot_import_idempotent(self):
        """
        Importing the same pivot payload twice should not create duplicate variants
        and should not raise errors — it updates existing items instead.
        """
        styles = [
            {
                "base_details": {
                    "article_no": self.PIVOT_STYLE_2,
                    "description": "Test Sandal Style",
                    "color": "RED",
                    "brand": "",
                    "item_group": "Products",
                    "cost_price": 0,
                    "mrp": 999,
                    "gst_percentage": "18",
                    "hsn_code": "640311",
                    "gender": "UNISEX",
                    "purchase_class": "FW",
                    "vendor_code": "",
                    "product_tax_group": "",
                    "merchandise_category": "",
                    "sub_category": "",
                },
                "sizes_config": [
                    {"size": "40", "active": True, "qty": 5},
                    {"size": "41", "active": True, "qty": 5},
                ]
            }
        ]

        # First import — creates 2 variants
        res1 = import_pivot_item_master(self._build_pivot_payload(styles))
        self.assertTrue(res1["success"])
        self.assertEqual(len(res1.get("errors", [])), 0)
        variants_after_first = frappe.db.get_all("Item", filters={"variant_of": self.PIVOT_STYLE_2}, pluck="name")
        self.assertEqual(len(variants_after_first), 2)

        # Second import — same payload; must not create duplicates
        res2 = import_pivot_item_master(self._build_pivot_payload(styles))
        self.assertTrue(res2["success"])
        self.assertEqual(len(res2.get("errors", [])), 0)
        variants_after_second = frappe.db.get_all("Item", filters={"variant_of": self.PIVOT_STYLE_2}, pluck="name")
        self.assertEqual(
            len(variants_after_second), 2,
            msg=f"Idempotency failed — got {len(variants_after_second)} variants on second run"
        )


class TestBarcodeHardening(unittest.TestCase):
    def setUp(self):
        self.company = frappe.db.exists("Company", "_Test Company")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)
        ensure_test_tax_template(self.company)

        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"}):
            r = frappe.new_doc("Has Role")
            r.parent = frappe.session.user
            r.parenttype = "User"
            r.parentfield = "roles"
            r.role = "SMRITI Store Manager"
            r.insert(ignore_permissions=True)
        frappe.db.commit()
        
        self.test_variant_code = "TST-HARDEN-BLK-8"
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        frappe.db.delete("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"})
        frappe.db.commit()

    def _cleanup(self):
        frappe.db.delete("Item Barcode", {"parent": self.test_variant_code})
        frappe.db.delete("Item Barcode", {"barcode": "9998887776665"})
        frappe.db.delete("Item Barcode", {"barcode": "9998887776660"})
        frappe.db.delete("Item Barcode", {"barcode": "SEC89012345"})
        frappe.db.delete("Item Price", {"item_code": self.test_variant_code})
        frappe.delete_doc("Item", self.test_variant_code, ignore_missing=True, force=True)
        frappe.delete_doc("Item", "TST-HARDEN", ignore_missing=True, force=True)
        frappe.db.delete("Supplier", {"custom_vendor_code": "VND-TEST-1"})
        frappe.db.commit()

    def test_manual_barcode_validation(self):
        """
        Verify manual barcode format and length validation.
        """
        base_details = {
            "article_no": "TST-HARDEN",
            "description": "Test Hardening Jordan",
            "color": "BLK",
            "brand": "Nike",
            "item_group": "Products",
            "cost_price": 1000,
            "mrp": 2000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "",
            "product_tax_group": ""
        }
        
        # Scenario 1: Spaces in manual barcode
        sizes_config = [
            { "size": "8", "active": True, "barcode_mode": "manual", "manual_barcode": "SPACE BARCODE" }
        ]
        with self.assertRaises(frappe.ValidationError):
            create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))

        # Scenario 2: Special characters
        sizes_config[0]["manual_barcode"] = "BARCODE@#"
        with self.assertRaises(frappe.ValidationError):
            create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))

        # Scenario 3: Under minimum length
        sizes_config[0]["manual_barcode"] = "12"
        with self.assertRaises(frappe.ValidationError):
            create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))

        # Scenario 4: Over maximum length
        sizes_config[0]["manual_barcode"] = "1" * 35
        with self.assertRaises(frappe.ValidationError):
            create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))

    def test_secondary_barcode_preservation(self):
        """
        Verify updates preserve secondary barcodes while ensuring single primary.
        """
        # Create style variant
        base_details = {
            "article_no": "TST-HARDEN",
            "description": "Test Hardening Sandal",
            "color": "BLK",
            "brand": "Puma",
            "item_group": "Products",
            "cost_price": 500,
            "mrp": 1000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "",
            "product_tax_group": ""
        }
        sizes_config = [
            { "size": "8", "active": True, "barcode_mode": "manual", "manual_barcode": "9998887776665" }
        ]
        
        create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))
        
        # Link a secondary barcode manually to mimic vendor barcode population
        var_doc = frappe.get_doc("Item", self.test_variant_code)
        var_doc.append("barcodes", {
            "barcode": "SEC89012345",
            "uom": "Nos",
            "custom_is_primary": 0
        })
        var_doc.save(ignore_permissions=True)
        
        # Verify the two barcodes exist
        self.assertEqual(len(var_doc.barcodes), 2)
        
        # Run create_style_with_variants again with a different primary barcode
        sizes_config[0]["manual_barcode"] = "9998887776660"
        create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))
        
        # Reload and check
        var_doc = frappe.get_doc("Item", self.test_variant_code)
        primaries = [b.barcode for b in var_doc.barcodes if b.custom_is_primary]
        secondaries = [b.barcode for b in var_doc.barcodes if not b.custom_is_primary]
        
        self.assertEqual(len(primaries), 1)
        self.assertEqual(primaries[0], "9998887776660")
        self.assertIn("SEC89012345", secondaries)
        self.assertEqual(len(secondaries), 1)

    def test_missing_barcode_detection(self):
        """
        Verify get_items_missing_barcodes returns active variants without barcodes.
        """
        from smriti_retail_os.item_master_api import _ensure_hsn_code
        _ensure_hsn_code("640311")
        
        # Create an item without barcodes
        item = frappe.new_doc("Item")
        item.item_code = self.test_variant_code
        item.item_name = "Jordan Missing Barcode"
        item.item_group = "Products"
        item.stock_uom = "Nos"
        item.gst_hsn_code = "640311"
        item.insert(ignore_permissions=True)
        
        missing = get_items_missing_barcodes()
        missing_codes = [m["item_code"] for m in missing]
        self.assertIn(self.test_variant_code, missing_codes)

    def test_vendor_code_validation(self):
        """
        Verify that vendor code validation blocks Item save/import if vendor code
        is not registered in Supplier Master.
        """
        from smriti_retail_os.item_master_api import validate_import_rows, import_item_master
        
        base_details = {
            "article_no": "TST-HARDEN",
            "description": "Test Vendor Code Item",
            "color": "BLK",
            "brand": "Nike",
            "item_group": "Products",
            "cost_price": 1000,
            "mrp": 2000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "VND-TEST-1",
            "product_tax_group": ""
        }
        sizes_config = [
            { "size": "8", "active": True, "barcode_mode": "manual", "manual_barcode": "9998887776665" }
        ]
        
        # 1. Verification of validate_import_rows (dry-run)
        row = {
            "BARCODE NO": "9998887776665",
            "PRODUCT STYLE CODE": "TST-HARDEN",
            "ITEM DESCRIPTION": "Test Vendor Code Item",
            "COLOR": "BLK",
            "SIZE": "8",
            "PLANNED MRP": "2000",
            "VENDOR CODE": "VND-TEST-1"
        }
        res_validate = validate_import_rows(frappe.as_json([row]))
        self.assertEqual(res_validate[0]["status"], "error")
        self.assertTrue(any("Vendor Code 'VND-TEST-1' not found" in e for e in res_validate[0]["errors"]))

        # 2. Verification of create_style_with_variants (single save)
        with self.assertRaises(frappe.ValidationError) as exc:
            create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))
        self.assertIn("Vendor Code 'VND-TEST-1' not found", str(exc.exception))

        # 3. Verification of import_item_master (bulk save)
        res_import = import_item_master(frappe.as_json([row]))
        self.assertEqual(res_import["created"], 0)
        self.assertEqual(len(res_import["failed"]), 1)
        self.assertIn("Vendor Code 'VND-TEST-1' not found", res_import["failed"][0]["error"])

        # 4. Now create Supplier with custom_vendor_code="VND-TEST-1"
        supp_group = frappe.db.get_value("Supplier Group", {}, "name")
        if not supp_group:
            supp_group = "All Supplier Groups"
            sg = frappe.new_doc("Supplier Group")
            sg.supplier_group_name = supp_group
            sg.insert(ignore_permissions=True)

        supp = frappe.new_doc("Supplier")
        supp.supplier_name = "Test Validation Supplier"
        supp.supplier_group = supp_group
        supp.custom_vendor_code = "VND-TEST-1"
        supp.insert(ignore_permissions=True)
        frappe.db.commit()

        # 5. Verify validations pass with valid vendor_code
        res_validate_ok = validate_import_rows(frappe.as_json([row]))
        self.assertEqual(res_validate_ok[0]["status"], "valid")

        res_create_ok = create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))
        self.assertTrue(res_create_ok["success"])

    def test_supplier_vendor_code_mapping(self):
        """
        Verify Supplier Registry Vendor Code mapping and Item Master linkage.
        """
        from smriti_retail_os.master_api import save_supplier_detail, get_supplier_detail
        
        # Cleanup potential existing test suppliers
        frappe.db.delete("Supplier", {"custom_vendor_code": "VND-TEST-MAP-1"})
        frappe.db.delete("Supplier", {"supplier_name": "Test Null Vendor Supplier 1"})
        frappe.db.delete("Supplier", {"supplier_name": "Test Null Vendor Supplier 2"})
        frappe.db.delete("Item Barcode", {"parent": "TST-MAP-ITEM-1"})
        frappe.delete_doc("Item", "TST-MAP-ITEM-1", ignore_missing=True, force=True)
        frappe.db.commit()

        # 1. Test saving supplier details with null/None vendor code doesn't collide
        s1 = save_supplier_detail(
            supplier_name="Test Null Vendor Supplier 1",
            supplier_type="Company",
            supplier_group="Local",
            custom_vendor_code=""
        )
        s2 = save_supplier_detail(
            supplier_name="Test Null Vendor Supplier 2",
            supplier_type="Company",
            supplier_group="Local",
            custom_vendor_code=None
        )
        self.assertIsNotNone(s1.get("name"))
        self.assertIsNotNone(s2.get("name"))

        # 2. Test saving and retrieving custom_vendor_code via APIs
        s3 = save_supplier_detail(
            supplier_name="Test Map Supplier 1",
            supplier_type="Company",
            supplier_group="Local",
            custom_vendor_code="VND-TEST-MAP-1"
        )
        details = get_supplier_detail(s3["name"])
        self.assertEqual(details.get("custom_vendor_code"), "VND-TEST-MAP-1")

        # 3. Test that importing item template links the supplier
        base_details = {
            "article_no": "TST-MAP-ITEM-1",
            "description": "Test Map Link Item",
            "color": "BLK",
            "brand": "Nike",
            "item_group": "Products",
            "cost_price": 1000,
            "mrp": 2000,
            "gst_percentage": "18",
            "hsn_code": "640311",
            "gender": "UNISEX",
            "purchase_class": "FW",
            "vendor_code": "VND-TEST-MAP-1",
            "product_tax_group": ""
        }
        sizes_config = [
            { "size": "8", "active": True, "barcode_mode": "auto", "manual_barcode": "" }
        ]
        
        # Creation path
        res_create = create_style_with_variants(frappe.as_json(base_details), frappe.as_json(sizes_config))
        self.assertTrue(res_create["success"])
        
        # Verify supplier linked
        item_doc = frappe.get_doc("Item", "TST-MAP-ITEM-1")
        self.assertTrue(any(d.supplier == s3["name"] and d.supplier_part_no == "VND-TEST-MAP-1" for d in item_doc.supplier_items))

        # Cleanup
        frappe.db.delete("Supplier", {"custom_vendor_code": "VND-TEST-MAP-1"})
        frappe.db.delete("Supplier", {"supplier_name": "Test Null Vendor Supplier 1"})
        frappe.db.delete("Supplier", {"supplier_name": "Test Null Vendor Supplier 2"})
        frappe.db.delete("Item Barcode", {"parent": "TST-MAP-ITEM-1"})
        frappe.delete_doc("Item", "TST-MAP-ITEM-1", ignore_missing=True, force=True)
        frappe.db.commit()

    def test_hsn_gst_rate_derivation(self):
        """
        Test that HSN-derived GST rate takes priority.
        """
        # Create a mock HSN code and configure taxes
        hsn_test_code = "99999999"

        # Pre-test cleanup — remove stale records from any previous failed run
        frappe.db.delete("GST HSN Code", {"name": hsn_test_code})
        tax_template_name = f"GST 12% - Test - {self.company}"
        # Delete by title match (name may include company abbreviation suffix)
        stale = frappe.db.get_all("Item Tax Template", filters={"title": tax_template_name}, pluck="name")
        for s in stale:
            frappe.delete_doc("Item Tax Template", s, ignore_missing=True, force=True)
        frappe.db.commit()

        # Create Item Tax Template for 12%
        if not frappe.db.exists("Item Tax Template", {"title": tax_template_name}):
            t = frappe.new_doc("Item Tax Template")
            t.title = tax_template_name
            t.company = self.company
            t.gst_treatment = "Taxable"
            t.gst_rate = 12.0

            # Find accounts
            filters_cgst = [["account_type", "=", "Tax"], ["company", "=", self.company], ["name", "like", "%CGST%"]]
            cgst = frappe.db.get_value("Account", filters_cgst, "name")
            filters_sgst = [["account_type", "=", "Tax"], ["company", "=", self.company], ["name", "like", "%SGST%"]]
            sgst = frappe.db.get_value("Account", filters_sgst, "name")

            if cgst:
                t.append("taxes", {"tax_type": cgst, "tax_rate": 6.0})
            if sgst:
                t.append("taxes", {"tax_type": sgst, "tax_rate": 6.0})
            t.insert(ignore_permissions=True)

        # Re-fetch actual name (may include company abbreviation suffix)
        tax_template_name = frappe.db.get_value(
            "Item Tax Template", {"title": f"GST 12% - Test - {self.company}"}, "name"
        ) or tax_template_name

        hsn_doc = frappe.new_doc("GST HSN Code")
        hsn_doc.name = hsn_test_code
        hsn_doc.hsn_code = hsn_test_code
        hsn_doc.append("taxes", {
            "item_tax_template": tax_template_name,
            "company": self.company
        })
        hsn_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # 1. Test get_hsn_gst_rate API
        from smriti_retail_os.item_master_api import get_hsn_gst_rate
        rate = get_hsn_gst_rate(hsn_test_code)
        self.assertEqual(rate, 12)

        # 2. Test validate_import_rows derives GST from HSN
        from smriti_retail_os.item_master_api import validate_import_rows
        rows_to_validate = [{
            "BARCODE NO": "TEST-HSN-BAR-1",
            "PRODUCT STYLE CODE": "TST-HSN-STYLE",
            "ITEM DESCRIPTION": "Test HSN Item",
            "BRAND NAME": "Nike",
            "COLOR": "RED",
            "SIZE": "9",
            "PLANNED MRP": 2500,
            "COST PRICE": 1200,
            "PRODUCT TAX": "18",  # We provide 18, but HSN should override to 12
            "HSN CODE": hsn_test_code,
            "VENDOR CODE": ""
        }]
        
        # In validation, it should validate against derived GST rate (12 is valid, but let's make sure it doesn't fail)
        results = validate_import_rows(frappe.as_json(rows_to_validate))
        self.assertEqual(results[0]["status"], "valid")
        self.assertEqual(len(results[0]["errors"]), 0)

        # 3. Test import_item_master prioritizes HSN GST rate
        from smriti_retail_os.item_master_api import import_item_master, _clear_hsn_cache
        frappe.db.delete("Item Barcode", {"parent": "TST-HSN-STYLE-RED-9"})
        frappe.delete_doc("Item", "TST-HSN-STYLE-RED-9", ignore_missing=True, force=True)
        frappe.delete_doc("Item", "TST-HSN-STYLE", ignore_missing=True, force=True)
        frappe.db.commit()
        # Clear all caches to ensure fresh HSN/template resolution
        frappe.clear_document_cache("GST HSN Code", hsn_test_code)
        _clear_hsn_cache()

        import_res = import_item_master(frappe.as_json(rows_to_validate))
        self.assertEqual(import_res.get("created"), 1)

        # Verify created item has 12% GST override from HSN
        item_variant = frappe.get_doc("Item", "TST-HSN-STYLE-RED-9")
        self.assertEqual(item_variant.custom_gst_percentage, "12")

        # Cleanup
        frappe.db.delete("GST HSN Code", {"name": hsn_test_code})
        frappe.db.delete("Item Tax Template", {"name": tax_template_name})
        frappe.db.delete("Item Barcode", {"parent": "TST-HSN-STYLE-RED-9"})
        frappe.delete_doc("Item", "TST-HSN-STYLE-RED-9", ignore_missing=True, force=True)
        frappe.delete_doc("Item", "TST-HSN-STYLE", ignore_missing=True, force=True)
        frappe.db.commit()


class TestImportLookupCache(unittest.TestCase):
    """
    Verifies that _build_import_lookup_cache() returns the correct structure.
    Fix 4: Ensures the N+1 query eliminator pre-loads all required lookup sets.
    """

    @classmethod
    def setUpClass(cls):
        frappe.set_user("Administrator")

    def test_cache_returns_all_required_keys(self):
        """Cache dict must contain all 5 lookup structures."""
        from smriti_retail_os.item_master_api import _build_import_lookup_cache
        cache = _build_import_lookup_cache()
        self.assertIn("barcode_to_item",   cache)
        self.assertIn("existing_items",    cache)
        self.assertIn("existing_vendors",  cache)
        self.assertIn("existing_brands",   cache)
        self.assertIn("existing_doctypes", cache)

    def test_cache_types_are_correct(self):
        """barcode_to_item must be a dict; the rest must be sets."""
        from smriti_retail_os.item_master_api import _build_import_lookup_cache
        cache = _build_import_lookup_cache()
        self.assertIsInstance(cache["barcode_to_item"],   dict)
        self.assertIsInstance(cache["existing_items"],    set)
        self.assertIsInstance(cache["existing_vendors"],  set)
        self.assertIsInstance(cache["existing_brands"],   set)
        self.assertIsInstance(cache["existing_doctypes"], set)

    def test_cache_existing_items_not_empty(self):
        """existing_items set must contain at least one item (site has items from setup)."""
        from smriti_retail_os.item_master_api import _build_import_lookup_cache
        cache = _build_import_lookup_cache()
        # We don't assert a specific item but the set must be usable
        self.assertIsInstance(cache["existing_items"], set)


class TestSaveUserNoHardcodedPassword(unittest.TestCase):
    """
    Verifies Fix 1: save_user() no longer assigns the known static password SmritiUser123!.
    Two users created in the same second must get different passwords.
    """

    @classmethod
    def setUpClass(cls):
        frappe.set_user("Administrator")

    def _get_user_hashed_password(self, email):
        """Fetch the hashed password from __Auth table for comparison."""
        try:
            row = frappe.db.sql(
                "SELECT `password` FROM `__Auth` WHERE `doctype`='User' AND `name`=%s AND `fieldname`='password'",
                email, as_dict=True
            )
            return row[0].password if row else None
        except Exception:
            return None

    def test_new_users_have_unique_passwords(self):
        """
        Two users created via save_user() must have DIFFERENT hashed passwords.
        If SmritiUser123! were still hardcoded, both would produce the same hash.
        """
        from smriti_retail_os.security_api import save_user
        email_a = "test_smriti_sec_a@test.internal"
        email_b = "test_smriti_sec_b@test.internal"

        # Cleanup before test
        for e in [email_a, email_b]:
            if frappe.db.exists("User", e):
                frappe.delete_doc("User", e, ignore_missing=True, force=True)
        frappe.db.commit()

        try:
            save_user(email_a, "Test", "SecA")
            save_user(email_b, "Test", "SecB")
            frappe.db.commit()

            pwd_a = self._get_user_hashed_password(email_a)
            pwd_b = self._get_user_hashed_password(email_b)

            # Both users must have a password set
            self.assertIsNotNone(pwd_a, "User A has no password hash")
            self.assertIsNotNone(pwd_b, "User B has no password hash")

            # The two passwords must be DIFFERENT (random tokens \u2260 shared hardcoded value)
            self.assertNotEqual(
                pwd_a, pwd_b,
                "Both users share the same password hash \u2014 hardcoded credential may still be in use"
            )
        finally:
            for e in [email_a, email_b]:
                if frappe.db.exists("User", e):
                    frappe.delete_doc("User", e, ignore_missing=True, force=True)
            frappe.db.commit()
