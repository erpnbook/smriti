# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_barcode_api.py
# @description: Unit tests for SMRITI Print Template schema and barcode API template rendering.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-06
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
from smriti_retail_os.barcode_api import (
    generate_prn,
    save_print_template,
)

class TestSmritiBarcodeAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clean up any test templates
        frappe.db.delete("SMRITI Print Template", {"name": ["in", ["TEST_ZPL_TEMPLATE", "TEST_TSPL_TEMPLATE", "TEST_MAPPINGS_TEMPLATE", "TEST_TOO_LARGE", "TEST_INVALID_MAPPINGS"]]})
        frappe.db.commit()
        from smriti_retail_os.setup import seed_master_doctypes
        seed_master_doctypes()

    def tearDown(self):
        # Clean up test templates
        frappe.db.delete("SMRITI Print Template", {"name": ["in", ["TEST_ZPL_TEMPLATE", "TEST_TSPL_TEMPLATE", "TEST_MAPPINGS_TEMPLATE", "TEST_TOO_LARGE", "TEST_INVALID_MAPPINGS"]]})
        frappe.db.commit()

    def test_print_template_lifecycle(self):
        """Tests standard CRUD lifecycle of SMRITI Print Template records."""
        # 1. Create / Save Template
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}])
        )
        
        self.assertTrue(frappe.db.exists("SMRITI Print Template", "TEST_ZPL_TEMPLATE"))
        
        # 2. Read Template
        doc = frappe.get_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        self.assertEqual(doc.template_title, template_name)
        self.assertEqual(doc.label_size, "50x25")
        self.assertEqual(doc.printer_language, "ZPL")
        self.assertEqual(doc.printer_family, "ZPL")  # auto-fallback
        self.assertEqual(doc.raw_template, raw_zpl)
        self.assertEqual(doc.custom_version, "1.0.0") # default version value
        self.assertIsNotNone(doc.template_checksum)
        old_checksum = doc.template_checksum
        
        # 3. Update Template
        updated_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^FO20,80^FD{barcode}^FS\n^XZ"
        save_print_template(
            template_name=template_name,
            label_size="50x30",
            printer_language="ZPL",
            raw_template=updated_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}]),
            printer_family="CPCL"  # explicit printer family update
        )
        
        doc.reload()
        self.assertEqual(doc.label_size, "50x30")
        self.assertEqual(doc.printer_family, "CPCL")
        self.assertEqual(doc.raw_template, updated_zpl)
        self.assertNotEqual(doc.template_checksum, old_checksum)

        # 4. Delete Template
        frappe.delete_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        self.assertFalse(frappe.db.exists("SMRITI Print Template", "TEST_ZPL_TEMPLATE"))

    def test_template_rendering_zpl(self):
        """Tests ZPL template substitution and print command counts."""
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "BIG BOSS",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 2
            }
        ]
        
        # Generate PRN - should support lookup by either "TEST_ZPL_TEMPLATE" or "Test ZPL Template"
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_ZPL_TEMPLATE")
        self.assertEqual(prn_data.count("^XA"), 2)
        self.assertEqual(prn_data.count("^XZ"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data)
        self.assertIn("499", prn_data)

        # Verify fallback by template_title
        prn_data_fallback = generate_prn(items=json.dumps(items_payload), template_name=template_name)
        self.assertEqual(prn_data_fallback.count("^XA"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data_fallback)

    def test_template_rendering_tspl(self):
        """Tests TSPL template rendering and print command outputs."""
        template_name = "Test TSPL Template"
        raw_tspl = "SIZE 50 mm, 25 mm\nCLS\nTEXT 20,20,\"3\",0,1,1,\"{item_name}\"\nPRINT 1,1"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="TSPL",
            raw_template=raw_tspl
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "BIG BOSS",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 1
            }
        ]
        
        # Generate PRN
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_TSPL_TEMPLATE")
        
        self.assertEqual(prn_data.count("SIZE 50 mm, 25 mm"), 1)
        self.assertEqual(prn_data.count("PRINT 1,1"), 1)
        self.assertIn("Bronze Loafer Shoe", prn_data)

    def test_field_mapping_resolution(self):
        """Tests custom field mappings JSON dynamically maps values inside ZPL templates."""
        template_name = "Test Mappings Template"
        raw_zpl = "^XA\n^FO20,20^FD{my_custom_token}^FS\n^XZ"
        
        # Configure a field mapping for custom token -> brand
        mappings = [
            {
                "label_field": "my_custom_token",
                "erp_field": "brand"
            }
        ]
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps(mappings)
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "TATTLY BRAND",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 1
            }
        ]
        
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_MAPPINGS_TEMPLATE")
        self.assertIn("TATTLY BRAND", prn_data)
        self.assertNotIn("{my_custom_token}", prn_data)

    def test_backward_compatibility(self):
        """Tests that legacy custom_ fieldnames continue to exist natively in the file-based schema."""
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}])
        )
        
        doc = frappe.get_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        
        # Verify legacy custom field attributes are directly accessible on the document object
        self.assertTrue(hasattr(doc, "custom_field_mappings_json"))
        self.assertTrue(hasattr(doc, "custom_version"))
        self.assertTrue(hasattr(doc, "custom_active"))
        self.assertTrue(hasattr(doc, "custom_is_default"))
        
        self.assertEqual(doc.custom_version, "1.0.0")
        self.assertEqual(doc.custom_active, 1)
        self.assertEqual(doc.custom_is_default, 0)
        self.assertIsNotNone(doc.custom_field_mappings_json)

    def test_template_size_validation(self):
        """Tests that a template exceeding 100 KB throws a ValidationError."""
        template_name = "Test Too Large Template"
        large_raw = "A" * (101 * 1024)  # 101 KB
        
        # Test validation on direct save/insert
        doc = frappe.new_doc("SMRITI Print Template")
        doc.name = "TEST_TOO_LARGE"
        doc.template_title = template_name
        doc.label_size = "50x25"
        doc.printer_language = "ZPL"
        doc.raw_template = large_raw
        
        self.assertRaises(frappe.ValidationError, doc.insert)
        
        # Test validation on API save_print_template call
        self.assertRaises(
            frappe.ValidationError,
            save_print_template,
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=large_raw
        )

    def test_mappings_json_validation(self):
        """Tests field mapping JSON format validation."""
        template_name = "Test Invalid Mappings"
        
        # 1. Invalid JSON string
        doc = frappe.new_doc("SMRITI Print Template")
        doc.name = "TEST_INVALID_MAPPINGS"
        doc.template_title = template_name
        doc.label_size = "50x25"
        doc.printer_language = "ZPL"
        doc.raw_template = "^XA^XZ"
        doc.custom_field_mappings_json = "{invalid_json}"
        
        self.assertRaises(frappe.ValidationError, doc.insert)
        
        # 2. JSON is valid but not a list/array
        doc.custom_field_mappings_json = '{"label_field": "item_name"}'
        self.assertRaises(frappe.ValidationError, doc.insert)

    def test_honeywell_seed_exists(self):
        """Verifies that the default Honeywell template was successfully seeded."""
        self.assertTrue(frappe.db.exists("SMRITI Print Template", "IMPACT_HONEYWELL_IH2_ZPL"))
        doc = frappe.get_doc("SMRITI Print Template", "IMPACT_HONEYWELL_IH2_ZPL")
        self.assertEqual(doc.template_title, "IMPACT by Honeywell IH-2 (ZPL)")
        self.assertEqual(doc.printer_language, "ZPL")
        self.assertEqual(doc.printer_family, "ZPL")
        self.assertEqual(doc.label_size, "100x50")
        self.assertIn("IMPACT by Honeywell", doc.template_title)

