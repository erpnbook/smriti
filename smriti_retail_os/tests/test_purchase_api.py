# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_purchase_api.py
# @description: Unit tests for the SMRITI Purchase API.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.utils import flt, cint, nowdate, add_days
from smriti_retail_os.purchase_api import (
    get_open_purchase_orders,
    get_po_details,
    create_purchase_order,
    create_purchase_receipt,
    create_purchase_return
)

class TestSmritiRetailPurchaseAPI(unittest.TestCase):
    
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

        # Ensure Products exists for footwear matrix auto-creation fallback
        if not frappe.db.exists("Item Group", "Products"):
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "Products"
            ig.is_group = 0
            parent = frappe.db.get_value("Item Group", {"is_group": 1}, "name")
            if parent:
                ig.parent_item_group = parent
            ig.insert(ignore_permissions=True)
            frappe.db.commit()

        # Resolve Company
        self.company = frappe.db.exists("Company", "_Test Company")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        # Ensure the test company has a valid GSTIN and registered company address (Required for India Compliance)
        frappe.db.set_value("Company", self.company, "gstin", "27AAXFT2508H1ZR")
        
        addr_name = f"{self.company}-Registered-Test"
        if not frappe.db.exists("Address", addr_name):
            addr = frappe.new_doc("Address")
            addr.address_title = self.company
            addr.address_type = "Office"
            addr.address_line1 = "Test Street"
            addr.city = "Mumbai"
            addr.state = "Maharashtra"
            addr.pincode = "400001"
            addr.country = "India"
            addr.is_primary_address = 1
            addr.is_shipping_address = 1
            addr.is_your_company_address = 1
            addr.gstin = "27AAXFT2508H1ZR"
            addr.append("links", {"link_doctype": "Company", "link_name": self.company})
            addr.insert(ignore_permissions=True)
            frappe.db.commit()

        # Set user default company to align all backend API company lookups to _Test Company
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)

        # Resolve Warehouse
        self.warehouse = frappe.db.get_value("Warehouse", {"company": self.company}, "name")
        if not self.warehouse:
            w = frappe.new_doc("Warehouse")
            w.warehouse_name = "Test Stores"
            w.company = self.company
            w.insert(ignore_permissions=True)
            self.warehouse = w.name

        # Resolve Supplier
        self.supplier = frappe.db.get_value("Supplier", {"disabled": 0, "on_hold": 0}, "name")
        if not self.supplier:
            existing = frappe.db.get_value("Supplier", {}, "name")
            if existing:
                frappe.db.set_value("Supplier", existing, {"disabled": 0, "on_hold": 0})
                frappe.db.commit()
                self.supplier = existing
            else:
                sup = frappe.new_doc("Supplier")
                sup.supplier_name = "Test Supplier"
                sup_group = frappe.db.get_value("Supplier Group", {}, "name")
                if not sup_group:
                    sg = frappe.new_doc("Supplier Group")
                    sg.supplier_group_name = "All Supplier Groups"
                    sg.insert(ignore_permissions=True)
                    sup_group = sg.name
                sup.supplier_group = sup_group
                sup.insert(ignore_permissions=True)
                self.supplier = sup.name

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

        # Resolve Asset Account
        self.asset_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Asset", "is_group": 0}, "name")

        # Update Company defaults
        frappe.db.set_value("Company", self.company, "default_inventory_account", self.asset_account)
        frappe.db.set_value("Company", self.company, "stock_received_but_not_billed", self.liability_account)
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

        # Set user as Administrator
        frappe.set_user("Administrator")

    def test_create_purchase_order(self):
        items = [{
            "item_code": self.item_code,
            "qty": 5,
            "rate": 120.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        
        res = create_purchase_order(self.supplier, items)
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        self.assertTrue(frappe.db.exists("Purchase Order", res["name"]))

    def test_create_purchase_order_with_custom_warehouse(self):
        items = [{
            "item_code": self.item_code,
            "qty": 5,
            "rate": 120.0,
            "stock_uom": self.uom
        }]
        
        res = create_purchase_order(self.supplier, items, warehouse=self.warehouse)
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        po_doc = frappe.get_doc("Purchase Order", res["name"])
        self.assertEqual(po_doc.items[0].warehouse, self.warehouse)

    def test_get_open_purchase_orders(self):
        pos = get_open_purchase_orders(self.supplier)
        self.assertIsInstance(pos, list)

    def test_get_po_details(self):
        # Create a PO first
        items = [{
            "item_code": self.item_code,
            "qty": 5,
            "rate": 120.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        po = create_purchase_order(self.supplier, items)
        
        details = get_po_details(po["name"])
        self.assertIsNotNone(details)
        self.assertEqual(details["name"], po["name"])
        self.assertEqual(details["supplier"], self.supplier)
        self.assertTrue(len(details["items"]) > 0)
        self.assertEqual(details["items"][0]["item_code"], self.item_code)

    def test_create_purchase_receipt_standalone(self):
        items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 150.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        
        res = create_purchase_receipt(self.supplier, items)
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        self.assertTrue(frappe.db.exists("Purchase Receipt", res["name"]))

    def test_create_purchase_receipt_standalone_with_custom_warehouse(self):
        items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 150.0,
            "stock_uom": self.uom
        }]
        
        res = create_purchase_receipt(self.supplier, items, warehouse=self.warehouse)
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        pr_doc = frappe.get_doc("Purchase Receipt", res["name"])
        self.assertEqual(pr_doc.items[0].warehouse, self.warehouse)

    def test_create_purchase_receipt_against_po(self):
        # 1. Create and submit PO
        items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 120.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        po = create_purchase_order(self.supplier, items)
        
        # 2. Get PO details to fetch child item row name
        details = get_po_details(po["name"])
        po_item_name = details["items"][0]["po_item_name"]
        
        # 3. Create PR against this PO
        receipt_items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 120.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom,
            "po_item_name": po_item_name
        }]
        
        res = create_purchase_receipt(self.supplier, receipt_items, po["name"])
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        self.assertTrue(frappe.db.exists("Purchase Receipt", res["name"]))
        
        # Check that PO is received
        po_received_qty = frappe.db.get_value("Purchase Order Item", po_item_name, "received_qty")
        self.assertEqual(flt(po_received_qty), 10.0)

    def test_create_purchase_order_footwear_matrix(self):
        # Ensure price lists exist
        for pl in ["Standard Selling", "MRP"]:
            if not frappe.db.exists("Price List", pl):
                pl_doc = frappe.new_doc("Price List")
                pl_doc.price_list_name = pl
                pl_doc.enabled = 1
                pl_doc.selling = 1
                pl_doc.insert(ignore_permissions=True)

        variant_code = "TESTSTYLE-BLACK-38"
        if frappe.db.exists("Item", variant_code):
            try:
                frappe.delete_doc("Item", variant_code, force=True)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in tests/test_purchase_api.py:313: {sys.exc_info()[1]}")

        items = [{
            "item_code": variant_code,
            "qty": 12,
            "rate": 350.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]

        target_schedule_date = add_days(nowdate(), 5)
        res = create_purchase_order(
            self.supplier, 
            items, 
            schedule_date=target_schedule_date, 
            remarks="Matrix PO Test Remarks",
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            image_filename="test_image.png"
        )
        self.assertIsNotNone(res)
        self.assertTrue(res["name"])
        self.assertTrue(frappe.db.exists("Purchase Order", res["name"]))
        
        # Verify custom schedule date and remarks
        po_doc = frappe.get_doc("Purchase Order", res["name"])
        self.assertEqual(str(po_doc.schedule_date), target_schedule_date)
        self.assertEqual(po_doc.terms, "Matrix PO Test Remarks")

        # Verify variant item was created correctly
        self.assertTrue(frappe.db.exists("Item", variant_code))
        item_doc = frappe.get_doc("Item", variant_code)
        self.assertEqual(item_doc.item_name, "TESTSTYLE BLACK 38")
        self.assertTrue(item_doc.image)
        self.assertTrue(item_doc.image.startswith("/files/"))
        self.assertEqual(item_doc.stock_uom, self.uom)
        self.assertEqual(cint(item_doc.custom_is_retail_item), 1)

        # Verify price list entries
        selling_rate = frappe.db.get_value("Item Price", {"item_code": variant_code, "price_list": "Standard Selling"}, "price_list_rate")
        mrp_rate = frappe.db.get_value("Item Price", {"item_code": variant_code, "price_list": "MRP"}, "price_list_rate")
        self.assertEqual(flt(selling_rate), 350.0 * 1.2)
        self.assertEqual(flt(mrp_rate), 350.0 * 1.5)

    def test_create_purchase_return(self):
        """
        Verifies that create_purchase_return successfully creates and submits
        a Purchase Return (Debit Note) against a submitted Purchase Receipt.
        """
        # 1. Create standalone submitted Purchase Receipt
        items = [{
            "item_code": self.item_code,
            "qty": 10,
            "rate": 150.0,
            "warehouse": self.warehouse,
            "stock_uom": self.uom
        }]
        
        res = create_purchase_receipt(self.supplier, items)
        self.assertIsNotNone(res)
        receipt_name = res["name"]
        self.assertTrue(frappe.db.exists("Purchase Receipt", receipt_name))

        # 2. Call create_purchase_return
        ret_res = create_purchase_return(receipt_name)
        
        self.assertIsNotNone(ret_res)
        ret_name = ret_res["name"]
        self.assertTrue(frappe.db.exists("Purchase Receipt", ret_name))

        # 3. Assert properties of the return Purchase Receipt
        ret_doc = frappe.get_doc("Purchase Receipt", ret_name)
        self.assertEqual(ret_doc.docstatus, 1)
        self.assertEqual(cint(ret_doc.is_return), 1)
        self.assertEqual(ret_doc.return_against, receipt_name)
        self.assertEqual(flt(ret_doc.items[0].qty), -10.0)

        # 4. Clean up both receipts
        frappe.db.delete("Purchase Receipt", {"name": ret_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": ret_name})
        frappe.db.delete("GL Entry", {"voucher_no": ret_name})
        frappe.db.delete("Purchase Receipt", {"name": receipt_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": receipt_name})
        frappe.db.delete("GL Entry", {"voucher_no": receipt_name})
        frappe.db.commit()

