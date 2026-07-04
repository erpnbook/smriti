# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_prn_regression.py
# @description: Automated PRN regression test comparing generated output to baseline structural checks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import unittest
import frappe
from smriti_retail_os.barcode.prn_generator import generate_prn


class TestPRNRegression(unittest.TestCase):
    def setUp(self):
        self.sample_items = [
            {
                "item_code": "TEST-ITEM-001",
                "item_name": "Antigravity Running Shoes",
                "barcode": "8901234567890",
                "brand": "SMRITI SPORT",
                "mrp": 2999,
                "size": "9",
                "color": "Midnight Black",
                "style": "ANTIGRAV-01",
                "print_qty": 2,
                "label_size": "50x25",
                "pkd_date": "07/26"
            }
        ]

    def test_zpl_fallback_generation(self):
        """Verify ZPL fallback PRN output matches structural expectations."""
        res = generate_prn(self.sample_items, template_name=None)
        
        self.assertIsInstance(res, dict)
        self.assertIn("prn", res)
        prn = res["prn"]
        
        # ZPL baseline check
        self.assertTrue(prn.startswith("^XA"))
        self.assertTrue(prn.endswith("^XZ\n") or prn.endswith("^XZ"))
        
        # Substituted values check
        self.assertIn("8901234567890", prn)
        self.assertIn("Antigravity Running Shoes", prn)
        self.assertIn("Rs.2999.00", prn)
        self.assertIn("SMRITI SPORT", prn)
        self.assertIn("Midnight Black", prn)

    def test_tspl_fallback_generation(self):
        """Verify TSPL 3-up fallback PRN output matches structural expectations."""
        tspl_items = [dict(self.sample_items[0], label_size="106x55", print_qty=1)]
        res = generate_prn(tspl_items, template_name=None)
        
        self.assertIsInstance(res, dict)
        self.assertIn("prn", res)
        prn = res["prn"]
        
        # TSPL commands check
        self.assertIn("SIZE 106.6 mm, 55.4 mm", prn)
        self.assertIn("GAP 3 mm, 0 mm", prn)
        self.assertIn("CLS", prn)
        
        # Substituted values check
        self.assertIn("8901234567890", prn)
        self.assertIn("Midnight Black", prn)
        self.assertIn("SMRITI SPORT", prn)


def verify_prn_output():
    """Dotted path entry point for bench execute verification."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPRNRegression)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("PRN Regression test failed.")
    print("PRN Regression test passed successfully.")
