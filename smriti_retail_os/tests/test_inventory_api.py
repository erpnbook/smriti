# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_inventory_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.utils import flt, cint, nowdate
from smriti_retail_os.inventory_api import (
    scan_item_for_inventory,
    create_grn,
    create_stock_transfer,
    create_stock_adjustment,
    create_stock_audit,
    get_stock_summary
)

class TestSmritiRetailInventoryAPI(unittest.TestCase):
    
    def setUp(self):
        # Resolve UOM
        self.uom = frappe.db.exists("UOM", "Nos") or frappe.db.get_value("UOM", {}, "name")
        if not self.uom:
            uom_doc = frappe.new_doc("UOM")
            uom_doc.uom_name = "Nos"
            uom_doc.insert(ignore_permissions=True)
            self.uom = uom_doc.name

        # Resolve Item Group
        self.item_group = frappe.db.exists("Item Group", "All Item Groups") or frappe.db.get_value("Item Group", {}, "name")
        if not self.item_group:
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "All Item Groups"
            ig.is_group = 0
            ig.insert(ignore_permissions=True)
            self.item_group = ig.name

        # Resolve Company
        self.company = frappe.db.exists("Company", "_Test Company") or frappe.db.get_value("Company", {}, "name")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        # Resolve Warehouse
        self.warehouse = frappe.db.get_value("Warehouse", {"company": self.company}, "name")
        if not self.warehouse:
            w = frappe.new_doc("Warehouse")
            w.warehouse_name = "Test Stores"
            w.company = self.company
            w.insert(ignore_permissions=True)
            self.warehouse = w.name

        # Resolve Supplier
        self.supplier = frappe.db.get_value("Supplier", {}, "name")
        if not self.supplier:
            sup = frappe.new_doc("Supplier")
            sup.supplier_name = "Test Supplier"
            sup.supplier_group = frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"
            sup.insert(ignore_permissions=True)
            self.supplier = sup.name
        # Resolve Cost Center robustly
        self.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
        if not self.cost_center:
            self.cost_center = frappe.db.get_value("Cost Center", {"company": self.company, "is_group": 0}, "name")
        if not self.cost_center:
            parent_cc = frappe.db.get_value("Cost Center", {"cost_center_name": self.company}, "name")
            if not parent_cc:
                pcc = frappe.new_doc("Cost Center")
                pcc.cost_center_name = self.company
                pcc.company = self.company
                pcc.is_group = 1
                pcc.flags.ignore_mandatory = True
                pcc.insert(ignore_permissions=True)
                parent_cc = pcc.name
                
            cc = frappe.new_doc("Cost Center")
            cc.cost_center_name = "Test Cost Center"
            cc.company = self.company
            cc.is_group = 0
            cc.parent_cost_center = parent_cc
            cc.insert(ignore_permissions=True)
            self.cost_center = cc.name

        # Resolve Expense/Difference Account robustly
        self.expense_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Expense", "is_group": 0}, "name")
        if not self.expense_account:
            parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Expense", "is_group": 1}, "name")
            if not parent_account:
                p_acc = frappe.new_doc("Account")
                p_acc.account_name = "Root Expense Group"
                p_acc.company = self.company
                p_acc.root_type = "Expense"
                p_acc.is_group = 1
                p_acc.insert(ignore_permissions=True)
                parent_account = p_acc.name
                
            acc = frappe.new_doc("Account")
            acc.account_name = "Stock Adjustment"
            acc.company = self.company
            acc.root_type = "Expense"
            acc.account_type = "Stock Adjustment"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.expense_account = acc.name

        # Resolve Asset Difference Account robustly for Stock Reconciliation
        self.asset_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Asset", "is_group": 0}, "name")
        if not self.asset_account:
            parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Asset", "is_group": 1}, "name")
            if not parent_account:
                p_acc = frappe.new_doc("Account")
                p_acc.account_name = "Root Asset Group"
                p_acc.company = self.company
                p_acc.root_type = "Asset"
                p_acc.is_group = 1
                p_acc.insert(ignore_permissions=True)
                parent_account = p_acc.name
                
            acc = frappe.new_doc("Account")
            acc.account_name = "Temporary Opening"
            acc.company = self.company
            acc.root_type = "Asset"
            acc.account_type = "Temporary"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.asset_account = acc.name

        # Create default Stock Entry Types if missing
        for name in ["Material Transfer", "Material Issue", "Material Receipt"]:
            if not frappe.db.exists("Stock Entry Type", name):
                doc = frappe.new_doc("Stock Entry Type")
                doc.name = name
                doc.purpose = name
                doc.insert(ignore_permissions=True)

        # Create active Fiscal Year robustly if missing or if company is not in it
        fy_name = "2026-2027"
        if not frappe.db.exists("Fiscal Year", fy_name):
            fy = frappe.new_doc("Fiscal Year")
            fy.year = fy_name
            fy.year_start_date = "2026-04-01"
            fy.year_end_date = "2027-03-31"
            fy.append("companies", {
                "company": self.company
            })
            fy.insert(ignore_permissions=True)
        else:
            fy = frappe.get_doc("Fiscal Year", fy_name)
            if not any(c.company == self.company for c in fy.companies):
                fy.append("companies", {
                    "company": self.company
                })
                fy.save(ignore_permissions=True)
                frappe.db.commit()

        # Resolve Liability Account robustly for Stock Received But Not Billed
        self.liability_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Liability", "is_group": 0}, "name")
        if not self.liability_account:
            parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Liability", "is_group": 1}, "name")
            if not parent_account:
                p_acc = frappe.new_doc("Account")
                p_acc.account_name = "Root Liability Group"
                p_acc.company = self.company
                p_acc.root_type = "Liability"
                p_acc.is_group = 1
                p_acc.insert(ignore_permissions=True)
                parent_account = p_acc.name
                
            acc = frappe.new_doc("Account")
            acc.account_name = "Stock Received But Not Billed"
            acc.company = self.company
            acc.root_type = "Liability"
            acc.account_type = "Stock Received But Not Billed"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.liability_account = acc.name

        # Update Company defaults
        frappe.db.set_value("Company", self.company, "default_inventory_account", self.asset_account)
        frappe.db.set_value("Company", self.company, "stock_adjustment_account", self.expense_account)
        frappe.db.set_value("Company", self.company, "default_expense_account", self.expense_account)
        frappe.db.set_value("Company", self.company, "stock_received_but_not_billed", self.liability_account)
        frappe.db.set_value("Company", self.company, "cost_center", self.cost_center)
        frappe.db.commit()

        # Resolve GST HSN Code
        self.hsn_code = frappe.db.exists("GST HSN Code", "998311") or frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "998311"
            hsn.description = "Test Services"
            hsn.insert(ignore_permissions=True)
            self.hsn_code = hsn.name

        # Create active item
        self.item_code = "SM-TEST-INV-ITEM"
        if not frappe.db.exists("Item", self.item_code):
            it = frappe.new_doc("Item")
            it.item_code = self.item_code
            it.item_name = "Test Inventory Item"
            it.item_group = self.item_group
            it.stock_uom = self.uom
            it.custom_is_retail_item = 1
            it.is_stock_item = 1
            it.gst_hsn_code = self.hsn_code
            it.valuation_rate = 150.0
            it.insert(ignore_permissions=True)
            
            # Create barcode
            bc = frappe.new_doc("Item Barcode")
            bc.parent = self.item_code
            bc.parenttype = "Item"
            bc.parentfield = "barcodes"
            bc.barcode = "9876543210"
            bc.insert(ignore_permissions=True)

        # Set user as Administrator to bypass manager role check in tests
        frappe.set_user("Administrator")

    def test_scan_item_for_inventory(self):
        res = scan_item_for_inventory("9876543210", self.warehouse)
        self.assertIsNotNone(res)
        self.assertEqual(res["item_code"], self.item_code)
        self.assertEqual(res["stock_uom"], self.uom)

    def test_grn_creation(self):
        items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 150.0,
            "warehouse": self.warehouse
        }]
        
        res = create_grn(self.supplier, "INV-001", items)
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        self.assertTrue(frappe.db.exists("Purchase Receipt", res["name"]))

    def test_stock_transfer(self):
        # Create transit/target warehouse (must belong to same company to avoid InvalidWarehouseCompany)
        target_wh = frappe.db.get_value("Warehouse", {"name": ["!=", self.warehouse], "company": self.company, "is_group": 0})
        if not target_wh:
            # Create a dedicated transit warehouse for this company
            tw = frappe.new_doc("Warehouse")
            tw.warehouse_name = "Test Transit"
            tw.company = self.company
            tw.insert(ignore_permissions=True)
            target_wh = tw.name
        
        items = [{
            "item_code": self.item_code,
            "qty": 2,
            "stock_uom": self.uom
        }]
        res = create_stock_transfer(self.warehouse, target_wh, items)
        self.assertIsNotNone(res)
        self.assertTrue(frappe.db.exists("Stock Entry", res["name"]))

    def test_stock_adjustment(self):
        items = [{
            "item_code": self.item_code,
            "qty": 5,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        res = create_stock_adjustment(items, "Stock Damaged")
        self.assertIsNotNone(res)
        self.assertTrue(frappe.db.exists("Stock Entry", res["name"]))

    def test_stock_audit(self):
        items = [{
            "item_code": self.item_code,
            "qty": 50,
            "warehouse": self.warehouse
        }]
        res = create_stock_audit(items)
        self.assertIsNotNone(res)
        self.assertTrue(frappe.db.exists("Stock Reconciliation", res["name"]))

    def test_get_stock_summary(self):
        res = get_stock_summary(self.warehouse)
        self.assertIsInstance(res, list)
