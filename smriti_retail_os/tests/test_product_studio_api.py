# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_product_studio_api.py
# @desc:    Unit tests for the SMRITI Product Studio Service and Repository Layers.
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os import smriti
import unittest
from smriti_retail_os.item_studio.repository.product_repository import ProductRepository
from smriti_retail_os.item_studio.service.product_service import ProductService


class TestProductStudioAPI(unittest.TestCase):
    
    def setUp(self):
        self.test_barcode = "TESTBARCODE999"
        # Cleanup if exists
        if smriti.db.exists("Item", self.test_barcode):
            frappe.delete_doc("Item", self.test_barcode, force=1)
            smriti.db.commit()

    def tearDown(self):
        # Cleanup
        if smriti.db.exists("Item", self.test_barcode):
            frappe.delete_doc("Item", self.test_barcode, force=1)
            smriti.db.commit()

    def test_create_and_read_product(self):
        # Test creation validation (Cost Price > MRP)
        invalid_data = {
            "item_code": self.test_barcode,
            "item_name": "Test Shirt",
            "cost_price": 500.0,
            "mrp": 300.0
        }
        with self.assertRaises(frappe.ValidationError):
            ProductService.save_product(invalid_data)

        # Create valid product
        valid_data = {
            "item_code": self.test_barcode,
            "item_name": "Test Shirt Green",
            "cost_price": 150.0,
            "mrp": 399.0,
            "gst_percentage": "18",
            "brand": "SMRITI Brand",
            "item_group": "Products"
        }
        
        created_code = ProductService.save_product(valid_data)
        self.assertEqual(created_code, self.test_barcode)
        
        # Verify database fields
        detail = ProductService.get_product_detail(self.test_barcode)
        self.assertEqual(detail["item_name"], "Test Shirt Green")
        self.assertEqual(detail["cost_price"], 150.0)
        self.assertEqual(detail["mrp"], 399.0)

        # Update product
        updated_data = {
            "item_name": "Test Shirt Green V2",
            "cost_price": 180.0,
            "mrp": 450.0
        }
        ProductService.save_product(updated_data, self.test_barcode)
        
        updated_detail = ProductService.get_product_detail(self.test_barcode)
        self.assertEqual(updated_detail["item_name"], "Test Shirt Green V2")
        self.assertEqual(updated_detail["cost_price"], 180.0)
        self.assertEqual(updated_detail["mrp"], 450.0)

        # Test listing
        products = ProductService.get_products(filters={"name": self.test_barcode})
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["item_name"], "Test Shirt Green V2")

        # Soft Delete (Disable)
        ProductService.delete_product(self.test_barcode)
        self.assertEqual(smriti.db.get("Item", self.test_barcode, "disabled"), 1)

    def test_hsn_code_validation(self):
        # 1. Test invalid HSN code (<4 digits or >8 digits)
        invalid_hsn_data = {
            "item_code": self.test_barcode,
            "item_name": "Test HSN Product",
            "mrp": 500.0,
            "cost_price": 200.0,
            "hsn_code": "12"  # Too short (2 digits)
        }
        with self.assertRaises(frappe.ValidationError):
            ProductService.save_product(invalid_hsn_data)

        # 2. Test valid 4-digit HSN code
        valid_hsn_4 = {
            "item_code": self.test_barcode,
            "item_name": "Test HSN 4 Digit",
            "mrp": 500.0,
            "cost_price": 200.0,
            "hsn_code": "6402"
        }
        code = ProductService.save_product(valid_hsn_4)
        detail = ProductService.get_product_detail(code)
        self.assertEqual(detail["hsn_code"], "6402")
        self.assertTrue(smriti.db.exists("GST HSN Code", "6402"))

        # 3. Test valid 8-digit HSN code update
        update_hsn_8 = {
            "hsn_code": "64029990"
        }
        ProductService.save_product(update_hsn_8, self.test_barcode)
        detail_updated = ProductService.get_product_detail(self.test_barcode)
        self.assertEqual(detail_updated["hsn_code"], "64029990")
        self.assertTrue(smriti.db.exists("GST HSN Code", "64029990"))

