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
    get_print_templates,
)

class TestSmritiBarcodeAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clean up any test templates
        frappe.db.delete("SMRITI Print Template", {"template_name": ["Test ZPL Template", "Test TSPL Template"]})
        frappe.db.commit()

    def tearDown(self):
        # Clean up test templates
        frappe.db.delete("SMRITI Print Template", {"template_name": ["Test ZPL Template", "Test TSPL Template"]})
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
            field_mappings_json=json.dumps([{"placeholder": "{item_name}", "field": "item_name"}])
        )
        
        self.assertTrue(frappe.db.exists("SMRITI Print Template", template_name))
        
        # 2. Read Template
        doc = frappe.get_doc("SMRITI Print Template", template_name)
        self.assertEqual(doc.label_size, "50x25")
        self.assertEqual(doc.printer_language, "ZPL")
        self.assertEqual(doc.raw_template, raw_zpl)
        self.assertEqual(doc.custom_version, "1.0.0") # default version value
        
        # 3. Update Template
        updated_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^FO20,80^FD{barcode}^FS\n^XZ"
        save_print_template(
            template_name=template_name,
            label_size="50x30",
            printer_language="ZPL",
            raw_template=updated_zpl,
            field_mappings_json=json.dumps([{"placeholder": "{item_name}", "field": "item_name"}])
        )
        
        doc.reload()
        self.assertEqual(doc.label_size, "50x30")
        self.assertEqual(doc.raw_template, updated_zpl)

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
        
        # Generate PRN
        prn_data = generate_prn(items=json.dumps(items_payload), template_name=template_name)
        
        # ZPL should be duplicated twice (print_qty = 2)
        self.assertEqual(prn_data.count("^XA"), 2)
        self.assertEqual(prn_data.count("^XZ"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data)
        self.assertIn("499", prn_data)

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
        prn_data = generate_prn(items=json.dumps(items_payload), template_name=template_name)
        
        self.assertEqual(prn_data.count("SIZE 50 mm, 25 mm"), 1)
        self.assertEqual(prn_data.count("PRINT 1,1"), 1)
        self.assertIn("Bronze Loafer Shoe", prn_data)
