# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_billing_api.py
# @description: Unit tests for the SMRITI Billing API.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.utils import flt, cint, now_datetime
from smriti_retail_os.billing_api import (
    add_item_by_barcode,
    search_customer,
    hold_bill,
    recall_bill,
    search_items,
    load_held_invoice,
    validate_manager_override,
    submit_bill,
    create_return_invoice,
    create_custom_sales_return,
    update_sales_return,
    delete_sales_return
)


class TestSmritiRetailBillingAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

    def setUp(self):
        # 1. Resolve or Create basic link dependencies for the isolated test DB
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

        self.company = frappe.db.exists("Company", "_Test Company")
        if not self.company:
            # Create Transit Warehouse Type if missing to support default warehouse creation on Company insert
            if not frappe.db.exists("Warehouse Type", "Transit"):
                wt = frappe.new_doc("Warehouse Type")
                wt.name = "Transit"
                wt.warehouse_type = "Transit"
                wt.insert(ignore_permissions=True)
                
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        # Ensure the test company has a valid GSTIN and registered company address (Required for India Compliance)
        frappe.db.set_value("Company", self.company, "gstin", "27AAXFT2508H1ZR")
        
        # Seed Stock Entry Types if missing in isolated test DB
        for et in ["Material Receipt", "Material Issue", "Material Transfer"]:
            if not frappe.db.exists("Stock Entry Type", et):
                doc = frappe.new_doc("Stock Entry Type")
                doc.name = et
                doc.purpose = et
                doc.insert(ignore_permissions=True)

        
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

        # Create valid GST HSN Code record for India Compliance
        self.hsn_code = frappe.db.exists("GST HSN Code", "998311") or frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "998311"
            hsn.description = "Test Services"
            hsn.insert(ignore_permissions=True)
            self.hsn_code = hsn.name

        # Resolve Warehouse
        self.warehouse = frappe.db.get_value("Warehouse", {"company": self.company}, "name")
        if not self.warehouse:
            w = frappe.new_doc("Warehouse")
            w.warehouse_name = "Test Warehouse"
            w.company = self.company
            w.warehouse_type = "Transit"
            w.insert(ignore_permissions=True)
            self.warehouse = w.name
            
        # Set cashier user default warehouse and company to align all lookups and bypass negative stock checks
        frappe.defaults.set_user_default("warehouse", self.warehouse, frappe.session.user)
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)

        # Resolve Cost Center robustly
        self.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
        if not self.cost_center:
            self.cost_center = frappe.db.get_value("Cost Center", {"company": self.company, "is_group": 0}, "name")
        if not self.cost_center:
            # Check if root group cost center exists or create it
            # The root cost center name MUST equal company name to pass parent_cost_center check!
            parent_cc = frappe.db.get_value("Cost Center", {"cost_center_name": self.company}, "name")
            if not parent_cc:
                pcc = frappe.new_doc("Cost Center")
                pcc.cost_center_name = self.company
                pcc.company = self.company
                pcc.is_group = 1
                pcc.flags.ignore_mandatory = True # Bypass parent_cost_center check on Root CC!
                pcc.insert(ignore_permissions=True)
                parent_cc = pcc.name
                
            cc = frappe.new_doc("Cost Center")
            cc.cost_center_name = "Test Cost Center"
            cc.company = self.company
            cc.is_group = 0
            cc.parent_cost_center = parent_cc
            cc.insert(ignore_permissions=True)
            self.cost_center = cc.name

        # Resolve Income Account robustly
        self.income_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Income", "is_group": 0}, "name")
        if not self.income_account:
            parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Income", "is_group": 1}, "name")
            if not parent_account:
                p_acc = frappe.new_doc("Account")
                p_acc.account_name = "Root Income Group"
                p_acc.company = self.company
                p_acc.root_type = "Income"
                p_acc.is_group = 1
                p_acc.insert(ignore_permissions=True)
                parent_account = p_acc.name
                
            acc = frappe.new_doc("Account")
            acc.account_name = "Sales"
            acc.company = self.company
            acc.root_type = "Income"
            acc.account_type = "Income Account"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.income_account = acc.name
            
        # Configure Round Off and Cash details on the test Company to support payments precision rounding
        round_off_cost_center = self.cost_center
        round_off_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Round Off"}, "name") or self.income_account
        default_cash_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Cash"}, "name") or frappe.db.get_value("Account", {"company": self.company, "account_name": "Cash"}, "name")
        
        updates = {
            "round_off_cost_center": round_off_cost_center,
            "round_off_account": round_off_account,
            "default_cash_account": default_cash_account,
            "default_income_account": self.income_account
        }
        
        # Clean up any invalid account/cost center references to prevent LinkValidationErrors due to test DB pollution
        for field in ["stock_received_but_not_billed", "default_inventory_account", 
                      "stock_adjustment_account", "default_expense_account", 
                      "default_bank_account", "cost_center"]:
            val = frappe.db.get_value("Company", self.company, field)
            if val:
                doctype = "Cost Center" if field == "cost_center" else "Account"
                if not frappe.db.exists(doctype, val):
                    updates[field] = None
                    
        frappe.db.set_value("Company", self.company, updates)
        frappe.db.commit()

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

        # Resolve Mode of Payment
        self.mode_of_payment = frappe.db.get_value("Mode of Payment", {}, "name")
        if not self.mode_of_payment:
            mop = frappe.new_doc("Mode of Payment")
            mop.mode_of_payment = "Cash"
            mop.type = "Cash"
            mop.insert(ignore_permissions=True)
            self.mode_of_payment = mop.name

        # Ensure Mode of Payment has standard account linked for our test Company
        mop_doc = frappe.get_doc("Mode of Payment", self.mode_of_payment)
        has_company_account = False
        for acc_row in mop_doc.accounts:
            if acc_row.company == self.company:
                has_company_account = True
                break
        if not has_company_account:
            cash_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Cash"}, "name") or frappe.db.get_value("Account", {"company": self.company, "account_name": "Cash"}, "name")
            if cash_account:
                mop_doc.append("accounts", {
                    "company": self.company,
                    "default_account": cash_account
                })
                mop_doc.save(ignore_permissions=True)
                frappe.db.commit()

        # Resolve standard selling price list
        if not frappe.db.exists("Price List", "Standard Selling"):
            pl = frappe.new_doc("Price List")
            pl.price_list_name = "Standard Selling"
            pl.enabled = 1
            pl.selling = 1
            pl.buying = 0
            pl.currency = "INR"
            pl.insert(ignore_permissions=True)

        # Create test POS Profile for saving Draft POS Invoices
        self.pos_profile_name = "Test POS Profile"
        if not frappe.db.exists("POS Profile", self.pos_profile_name):
            pos_prof = frappe.new_doc("POS Profile")
            pos_prof.name = self.pos_profile_name # Explicitly assign name because of Prompt naming strategy!
            pos_prof.pos_profile_name = self.pos_profile_name
            pos_prof.company = self.company
            pos_prof.warehouse = self.warehouse
            pos_prof.cost_center = self.cost_center
            pos_prof.income_account = self.income_account
            pos_prof.selling_price_list = "Standard Selling"
            pos_prof.currency = "INR"
            pos_prof.append("payments", {
                "mode_of_payment": self.mode_of_payment,
                "default": 1
            })
            pos_prof.append("applicable_for_users", {
                "user": frappe.session.user
            })
            pos_prof.flags.ignore_mandatory = True # Bypass write_off_account/write_off_cost_center checks!
            pos_prof.insert(ignore_permissions=True)

        # Clean up potential old test records including barcodes child table orphans, tax templates and tax account
        frappe.db.delete("Item Price", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Barcode", {"parent": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Barcode", {"barcode": "8901234567890"})
        # CRITICAL: purge all child table rows before deleting Item to prevent orphan accumulation
        # frappe.db.delete("Item", ...) is raw SQL and does NOT cascade to child tables
        frappe.db.delete("Item Tax", {"parent": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Supplier", {"parent": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Variant Attribute", {"parent": "TEST-ITEM-BAR"})
        frappe.db.delete("Item", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Customer", {"customer_name": "Test Billing Customer"})
        frappe.db.delete("POS Invoice", {"customer": "Test Billing Customer"})
        frappe.db.delete("Sales Invoice", {"customer": "Test Billing Customer"})
        frappe.db.delete("GL Entry", {"party": "Test Billing Customer"})
        frappe.db.delete("Comment", {"reference_doctype": "POS Invoice"})
        
        # Clean up tax templates via delete_doc to ensure child tables are fully purged
        for name in frappe.db.get_all("Item Tax Template", filters={"name": ["like", "%18%"]}, pluck="name"):
            frappe.delete_doc("Item Tax Template", name, ignore_missing=True, force=True)
        for name in frappe.db.get_all("Sales Taxes and Charges Template", filters={"name": ["like", "%18%"]}, pluck="name"):
            frappe.delete_doc("Sales Taxes and Charges Template", name, ignore_missing=True, force=True)
            
        frappe.db.delete("Account", {"account_name": "GST 9+9", "company": self.company})
        frappe.db.commit()


        # Resolve or create a single non-group Tax account
        company_abbr = frappe.db.get_value("Company", self.company, "abbr") or "_C"
        self.tax_account = f"GST 9+9 - {company_abbr}"
        if not frappe.db.exists("Account", self.tax_account):
            parent_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Tax", "is_group": 1}, "name")
            if not parent_account:
                parent_account = frappe.db.get_value("Account", {"company": self.company, "account_name": f"Duties and Taxes - {company_abbr}"}, "name")
            if not parent_account:
                parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Liability", "is_group": 1}, "name")
            
            acc = frappe.new_doc("Account")
            acc.account_name = "GST 9+9"
            acc.company = self.company
            acc.root_type = "Liability"
            acc.account_type = "Tax"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)

        # Create test Item Tax Template for 18% GST
        self.item_tax_template_name = "18% GST"
        existing_itt = frappe.db.get_value("Item Tax Template", {"title": self.item_tax_template_name, "company": self.company}, "name")
        if not existing_itt:
            itt = frappe.new_doc("Item Tax Template")
            itt.title = self.item_tax_template_name
            itt.company = self.company
            itt.gst_rate = 18.0
            itt.append("taxes", {
                "tax_type": self.tax_account,
                "tax_rate": 18.0
            })
            itt.insert(ignore_permissions=True)
            existing_itt = itt.name
        self.item_tax_template_name = existing_itt

        # Create test Sales Taxes and Charges Template for 18% GST
        self.sales_tax_template_name = "18% GST Template"
        existing_stct = frappe.db.get_value("Sales Taxes and Charges Template", {"title": self.sales_tax_template_name, "company": self.company}, "name")
        if not existing_stct:
            stct = frappe.new_doc("Sales Taxes and Charges Template")
            stct.title = self.sales_tax_template_name
            stct.company = self.company
            stct.is_default = 1
            stct.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": self.tax_account,
                "description": "GST 18%",
                "rate": 18.0
            })
            stct.insert(ignore_permissions=True)
            existing_stct = stct.name
        else:
            frappe.db.set_value("Sales Taxes and Charges Template", existing_stct, "is_default", 1)
        self.sales_tax_template_name = existing_stct

        # 2. Setup a test Retail Item
        self.item = frappe.new_doc("Item")
        self.item.item_code = "TEST-ITEM-BAR"
        self.item.item_name = "Test Retail Product"
        self.item.item_group = self.item_group
        self.item.stock_uom = self.uom
        self.item.custom_is_retail_item = 1
        self.item.custom_mrp = 150.0
        self.item.standard_rate = 100.0
        self.item.custom_gst_percentage = "18"
        self.item.gst_hsn_code = self.hsn_code
        self.item.append("barcodes", {
            "barcode": "8901234567890",
            "uom": self.uom
        })
        self.item.append("item_defaults", {
            "company": self.company,
            "default_income_account": self.income_account
        })
        self.item.insert(ignore_permissions=True)

        # Trigger hook manually to sync prices and taxes
        from smriti_retail_os.hooks_logic import sync_item_taxes_and_prices, after_item_save
        sync_item_taxes_and_prices(self.item, None)
        after_item_save(self.item, None)
        # 3. Setup a test Customer
        self.cust = frappe.new_doc("Customer")
        self.cust.customer_name = "Test Billing Customer"
        self.cust.customer_type = "Individual"
        self.cust.mobile_no = "9988776655"
        self.cust.insert(ignore_permissions=True)
        
        # 3b. Setup a test Sales Person
        if not frappe.db.exists("Sales Person", "Rahul Sharma"):
            sp = frappe.new_doc("Sales Person")
            sp.sales_person_name = "Rahul Sharma"
            sp.commission_rate = 5.0
            sp.insert(ignore_permissions=True)

        # 4. Setup a test Manager PIN / Password
        # Assign Password to current user so we can test validation easily
        from frappe.utils.password import update_password
        update_password(frappe.session.user, "4321", fieldname="custom_smriti_pin")
        frappe.db.set_value("User", frappe.session.user, "custom_smriti_pin", "4321")
        
        # Ensure current user has SMRITI Store Manager role in DB
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"}):
            role_doc = frappe.new_doc("Has Role")
            role_doc.parent = frappe.session.user
            role_doc.parenttype = "User"
            role_doc.parentfield = "roles"
            role_doc.role = "SMRITI Store Manager"
            role_doc.insert(ignore_permissions=True)
        
        # Create stock entry to initialize stock for TEST-ITEM-BAR to prevent NegativeStockError on credit sales
        se = frappe.new_doc("Stock Entry")
        se.purpose = "Material Receipt"
        se.stock_entry_type = "Material Receipt"
        se.company = self.company
        se.posting_date = frappe.utils.nowdate()
        se.append("items", {
            "item_code": "TEST-ITEM-BAR",
            "qty": 100.0,
            "t_warehouse": self.warehouse,
            "uom": self.uom,
            "basic_rate": 100.0,
            "expense_account": self.income_account,
            "allow_zero_valuation_rate": 1
        })
        se.insert(ignore_permissions=True)
        se.submit()
        
        frappe.db.commit()

    def tearDown(self):
        # Clean up test records
        frappe.db.delete("Item", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Barcode", {"barcode": "8901234567890"})
        frappe.db.delete("Item Price", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Customer", {"customer_name": "Test Billing Customer"})
        
        # Clean up Stock Entries created for this test item
        se_names = frappe.db.sql_list("SELECT DISTINCT parent FROM `tabStock Entry Detail` WHERE item_code = 'TEST-ITEM-BAR'")
        if se_names:
            frappe.db.sql("DELETE FROM `tabStock Entry Detail` WHERE parent IN (%s)" % ", ".join(["%s"] * len(se_names)), tuple(se_names))
            frappe.db.sql("DELETE FROM `tabStock Entry` WHERE name IN (%s)" % ", ".join(["%s"] * len(se_names)), tuple(se_names))
            frappe.db.sql("DELETE FROM `tabStock Ledger Entry` WHERE item_code = 'TEST-ITEM-BAR'")
            frappe.db.sql("DELETE FROM `tabBin` WHERE item_code = 'TEST-ITEM-BAR'")
            
        # Safely and fully delete POS Invoices and Sales Invoices along with their child table items
        for dt, child_dt in [("POS Invoice", "POS Invoice Item"), ("Sales Invoice", "Sales Invoice Item")]:
            names = frappe.db.sql_list("SELECT name FROM `tab%s` WHERE customer = %%s" % dt, ("Test Billing Customer",))
            if names:
                frappe.db.sql("DELETE FROM `tab%s` WHERE parent IN (%s)" % (child_dt, ", ".join(["%s"] * len(names))), tuple(names))
                frappe.db.sql("DELETE FROM `tab%s` WHERE name IN (%s)" % (dt, ", ".join(["%s"] * len(names))), tuple(names))
                
        # Safely and fully delete Payment Entries along with their child table items
        pe_names = frappe.db.sql_list("SELECT name FROM `tabPayment Entry` WHERE party = %s", ("Test Billing Customer",))
        if pe_names:
            frappe.db.sql("DELETE FROM `tabPayment Entry Reference` WHERE parent IN (%s)" % ", ".join(["%s"] * len(pe_names)), tuple(pe_names))
            frappe.db.sql("DELETE FROM `tabPayment Entry Deduction` WHERE parent IN (%s)" % ", ".join(["%s"] * len(pe_names)), tuple(pe_names))
            frappe.db.sql("DELETE FROM `tabPayment Entry` WHERE name IN (%s)" % ", ".join(["%s"] * len(pe_names)), tuple(pe_names))

        frappe.db.delete("GL Entry", {"party": "Test Billing Customer"})
        frappe.db.delete("Comment", {"reference_doctype": "POS Invoice"})
        
        # Clean up test roles
        frappe.db.delete("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"})
        
        # Clean up test tax templates via delete_doc to ensure child tables are fully purged
        for item in frappe.db.get_all("Item Tax Template", filters={"title": "18% GST"}):
            frappe.delete_doc("Item Tax Template", item.name, ignore_missing=True, force=True)
        for item in frappe.db.get_all("Sales Taxes and Charges Template", filters={"title": "18% GST Template"}):
            frappe.delete_doc("Sales Taxes and Charges Template", item.name, ignore_missing=True, force=True)
            
        frappe.db.delete("Account", {"account_name": "GST 9+9", "company": self.company})
        
        frappe.db.commit()

    def test_add_item_by_barcode(self):
        """
        Verifies barcode scanning fetches standard rates, MRP, and GST correctly.
        """
        # Test by scanned barcode
        res = add_item_by_barcode("8901234567890")
        self.assertIsNotNone(res)
        self.assertEqual(res["item_code"], "TEST-ITEM-BAR")
        self.assertEqual(flt(res["rate"]), 100.0)
        self.assertEqual(flt(res["mrp"]), 150.0)
        self.assertEqual(res["gst_percentage"], 18)

        # Test fallback directly matching item_code
        res_direct = add_item_by_barcode("TEST-ITEM-BAR")
        self.assertIsNotNone(res_direct)
        self.assertEqual(res_direct["item_code"], "TEST-ITEM-BAR")

    def test_search_customer(self):
        """
        Verifies customer lookup by mobile or name.
        """
        # Search by mobile
        res = search_customer("9988776655")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["customer_name"], "Test Billing Customer")

        # Search by name
        res_name = search_customer("Billing Customer")
        self.assertTrue(len(res_name) > 0)

    def test_hold_and_recall_bill(self):
        """
        Verifies holding and recalling a bill creates and reads draft POS invoices.
        """
        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 2,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        # Hold current active bill
        res_hold = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload)
        )
        self.assertIsNotNone(res_hold)
        invoice_name = res_hold["invoice_name"]
        self.assertTrue(frappe.db.exists("POS Invoice", invoice_name))

        # Check in DB that custom hold fields are populated
        inv = frappe.get_doc("POS Invoice", invoice_name)
        self.assertEqual(inv.docstatus, 0)
        self.assertEqual(inv.custom_is_held, 1)
        self.assertEqual(inv.custom_held_by, frappe.session.user)

        # Recall held bills
        recalled_list = recall_bill(frappe.session.user)
        self.assertTrue(len(recalled_list) > 0)
        held_names = [r["name"] for r in recalled_list]
        self.assertIn(invoice_name, held_names)

        # Load specific held invoice items
        loaded = load_held_invoice(invoice_name)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["customer"], "Test Billing Customer")
        self.assertEqual(len(loaded["items"]), 1)
        self.assertEqual(loaded["items"][0]["item_code"], "TEST-ITEM-BAR")
        self.assertEqual(flt(loaded["items"][0]["qty"]), 2.0)

    def test_search_items(self):
        """
        Verifies catalog query search.
        """
        res = search_items("Retail Product")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["item_code"], "TEST-ITEM-BAR")

    def test_manager_override(self):
        """
        Verifies security override and audit comments logging.
        """
        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "qty": 1,
            "rate": 100.0,
            "mrp": 150.0
        }]
        res_hold = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload)
        )
        invoice_name = res_hold["invoice_name"]

        # 1. Invalid PIN check
        res_invalid = validate_manager_override("9999", "Void Row Override", invoice_name)
        self.assertFalse(res_invalid["authorized"])

        # 2. Valid PIN check
        res_valid = validate_manager_override("4321", "Void Row Override", invoice_name)
        self.assertTrue(res_valid["authorized"])
        self.assertEqual(res_valid["manager"], frappe.session.user)

        # 3. Check comment audit log creation
        comments = frappe.db.get_all(
            "Comment",
            filters={
                "reference_doctype": "POS Invoice",
                "reference_name": invoice_name
            },
            fields=["content"]
        )
        self.assertTrue(len(comments) > 0)
        self.assertIn("Manager Override approved", comments[0]["content"])

    def test_submit_bill_sales_invoice_fallback(self):
        """
        Verifies that when no cashier shift is open, submit_bill successfully
        submits a standard Sales Invoice directly, bypassing shift checks.
        """
        # Ensure no open shift exists for the cashier
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 3,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        payments_payload = [
            {"mode_of_payment": self.mode_of_payment, "amount": 354.0} # Qty 3 * Rate 100 * 1.18 Tax = 354.0
        ]

        # Submit bill
        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            payments=frappe.as_json(payments_payload)
        )

        self.assertIsNotNone(res)
        invoice_name = res["invoice"]
        self.assertTrue(frappe.db.exists("Sales Invoice", invoice_name))
        
        # Verify it is a standard Sales Invoice and submitted (docstatus=1)
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        self.assertEqual(invoice.docstatus, 1)
        self.assertEqual(invoice.is_pos, 0)
        self.assertEqual(flt(invoice.grand_total), 354.0)

        # Clean up created Sales Invoice
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.delete("GL Entry", {"voucher_no": invoice_name})
        frappe.db.commit()

    def test_submit_bill_on_credit(self):
        """
        Verifies that when on_credit=1, submit_bill successfully submits a standard
        outstanding Sales Invoice without payment entries and sets update_stock = 1.
        """
        # Ensure no open shift exists or is isolated for the cashier
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 2,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        # Submit bill on credit (empty payments payload)
        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            payments=frappe.as_json([]),
            on_credit=1
        )

        self.assertIsNotNone(res)
        invoice_name = res["invoice"]
        self.assertTrue(frappe.db.exists("Sales Invoice", invoice_name))
        
        # Verify it is a standard Sales Invoice, submitted (docstatus=1) and outstanding matches grand total
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        self.assertEqual(invoice.docstatus, 1)
        self.assertEqual(invoice.is_pos, 0)
        self.assertEqual(invoice.update_stock, 1)
        self.assertEqual(flt(invoice.grand_total), 236.0) # Qty 2 * Rate 100 * 1.18 Tax = 236.0
        self.assertEqual(flt(invoice.outstanding_amount), 236.0) # Outstanding matches grand_total on credit sale
        self.assertEqual(len(invoice.payments), 0)

        # Clean up created Sales Invoice
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.delete("GL Entry", {"voucher_no": invoice_name})
        frappe.db.commit()

    def test_create_return_invoice(self):
        """
        Verifies that create_return_invoice successfully creates and submits
        a return Sales Invoice against a submitted Sales Invoice.
        """
        # 1. Create a submitted Sales Invoice
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 3,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        payments_payload = [
            {"mode_of_payment": self.mode_of_payment, "amount": 354.0}
        ]

        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            payments=frappe.as_json(payments_payload)
        )

        invoice_name = res["invoice"]
        self.assertTrue(frappe.db.exists("Sales Invoice", invoice_name))

        # 2. Call create_return_invoice
        ret_res = create_return_invoice(invoice_name)

        self.assertIsNotNone(ret_res)
        ret_name = ret_res["name"]
        self.assertTrue(frappe.db.exists("Sales Invoice", ret_name))

        # 3. Assert properties of the return invoice
        ret_doc = frappe.get_doc("Sales Invoice", ret_name)
        self.assertEqual(ret_doc.docstatus, 1)
        self.assertEqual(cint(ret_doc.is_return), 1)
        self.assertEqual(ret_doc.return_against, invoice_name)
        self.assertEqual(flt(ret_doc.items[0].qty), -3.0)

        # 4. Clean up both invoices
        frappe.db.delete("Sales Invoice", {"name": ret_name})
        frappe.db.delete("GL Entry", {"voucher_no": ret_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": ret_name})
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.delete("GL Entry", {"voucher_no": invoice_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": invoice_name})
        frappe.db.commit()

    def test_create_custom_sales_return_single(self):
        # 1. Create a submitted Sales Invoice
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 3,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]
        payments_payload = [{"mode_of_payment": self.mode_of_payment, "amount": 354.0}]
        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            payments=frappe.as_json(payments_payload)
        )
        invoice_name = res["invoice"]

        # Test Draft Return against single bill
        ret_res = create_custom_sales_return(
            customer="Test Billing Customer",
            items=frappe.as_json([{"item_code": "TEST-ITEM-BAR", "qty": 2, "rate": 100.0}]),
            return_against_invoice=invoice_name,
            draft=1
        )
        self.assertIsNotNone(ret_res)
        draft_name = ret_res["name"]
        self.assertTrue(frappe.db.exists("Sales Invoice", draft_name))
        
        draft_doc = frappe.get_doc("Sales Invoice", draft_name)
        self.assertEqual(draft_doc.docstatus, 0)
        self.assertEqual(cint(draft_doc.is_return), 1)
        self.assertEqual(draft_doc.return_against, invoice_name)
        self.assertEqual(flt(draft_doc.items[0].qty), -2.0)

        # Cleanup
        frappe.db.delete("Sales Invoice", {"name": draft_name})
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.delete("GL Entry", {"voucher_no": invoice_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": invoice_name})
        frappe.db.commit()

    def test_create_custom_sales_return_standalone_and_update(self):
        # Test creating standalone return as Draft
        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "qty": 1,
            "rate": 100.0,
            "mrp": 150.0,
            "stock_uom": self.uom
        }]
        ret_res = create_custom_sales_return(
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            draft=1
        )
        self.assertIsNotNone(ret_res)
        ret_name = ret_res["name"]
        self.assertEqual(ret_res["docstatus"], 0)

        # Update the draft return
        updated_items = [{
            "item_code": "TEST-ITEM-BAR",
            "qty": 2,
            "rate": 90.0,
            "mrp": 150.0,
            "stock_uom": self.uom
        }]
        update_res = update_sales_return(
            name=ret_name,
            items=frappe.as_json(updated_items),
            remarks="Updated qty and rate",
            draft=1
        )
        self.assertEqual(update_res["name"], ret_name)
        self.assertEqual(update_res["docstatus"], 0)
        
        doc = frappe.get_doc("Sales Invoice", ret_name)
        self.assertEqual(flt(doc.items[0].qty), -2.0)
        self.assertEqual(flt(doc.items[0].rate), 90.0)
        self.assertEqual(doc.remarks, "Updated qty and rate")

        # Submit it via update_sales_return
        submit_res = update_sales_return(
            name=ret_name,
            items=frappe.as_json(updated_items),
            remarks="Submitting return",
            draft=0
        )
        self.assertEqual(submit_res["docstatus"], 1)

        # Test Deletion/Cancellation with Manager Pin Override
        mgr_user = frappe.session.user
        from frappe.utils.password import update_password
        update_password(mgr_user, "5555", fieldname="custom_smriti_pin")
        frappe.db.set_value("User", mgr_user, "custom_smriti_pin", "5555")
        frappe.db.commit()

        del_res = delete_sales_return(name=ret_name, manager_pin="5555")
        self.assertEqual(del_res["name"], ret_name)
        self.assertTrue(frappe.db.exists("Sales Invoice", ret_name))
        self.assertEqual(frappe.db.get_value("Sales Invoice", ret_name, "docstatus"), 2)

        frappe.db.delete("Sales Invoice", {"name": ret_name})
        frappe.db.delete("GL Entry", {"voucher_no": ret_name})
        frappe.db.delete("Stock Ledger Entry", {"voucher_no": ret_name})
        frappe.db.commit()


# =============================================================================
#  BILLING-002 — Stability Gap Tests
#  Sprint: Milestone 2 — Billing & POS Stability
#  Author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#  Authority: AITDL / AF-01 Architecture Freeze Compliant
# =============================================================================

class TestBillingStabilityGaps(TestSmritiRetailBillingAPI):
    """
    Targeted regression tests for the 4 stability gaps identified in BILLING-002.
    Inherits the full setUp/tearDown scaffold from TestBillingAPI to reuse
    test item, customer, stock, and POS profile setup.
    """

    def _base_items(self, qty=2, discount_percentage=0.0):
        return [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": qty,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": "",
            "discount_percentage": discount_percentage,
        }]

    def _base_payments(self, amount):
        return [{"mode_of_payment": self.mode_of_payment, "amount": amount}]

    # ── GAP-B02: Discount preserved through Hold → Recall ──

    def test_hold_preserves_discount_percentage(self):
        """
        GAP-B02: discount_percentage must survive hold → recall cycle.
        Risk: cashier holds discounted bill → recalls → discount lost → customer overcharged.
        """
        res = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(self._base_items(qty=1, discount_percentage=15.0))
        )
        loaded = load_held_invoice(res["invoice_name"])
        self.assertIsNotNone(loaded)
        self.assertEqual(flt(loaded["items"][0]["discount_percentage"]), 15.0)

    # ── GAP-B05: recall_bill returns non-zero display_total ──

    def test_recall_bill_returns_display_total(self):
        """
        GAP-B05: recall_bill must return display_total = SUM(qty x rate).
        Draft POS Invoices always have grand_total = 0 (Frappe skips totals on hold).
        display_total is an estimate for UI identification ONLY — not an accounting total.
        """
        res = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(self._base_items(qty=3))  # 3 x 100 = 300
        )
        invoice_name = res["invoice_name"]

        # Confirm draft grand_total is 0 (the bug this test targets)
        self.assertEqual(flt(frappe.db.get_value("POS Invoice", invoice_name, "grand_total")), 0.0)

        held_list = recall_bill(frappe.session.user)
        matched = [b for b in held_list if b["name"] == invoice_name]
        self.assertEqual(len(matched), 1)
        self.assertIn("display_total", matched[0])
        self.assertAlmostEqual(flt(matched[0]["display_total"]), 300.0, places=2)

    # ── GAP-B01: Idempotent submit — same session_id = same invoice ──

    def test_idempotent_submit_same_session_id(self):
        """
        GAP-B01: Submitting the same billing_session_id twice must return the
        SAME invoice. Prevents duplicate billing on double-click or network retry.
        """
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        session_id = "TEST-BSID-IDEMPOTENT-001"
        kwargs = dict(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(self._base_items(qty=1)),
            payments=frappe.as_json(self._base_payments(118.0)),
            billing_session_id=session_id
        )

        res1 = submit_bill(**kwargs)
        res2 = submit_bill(**kwargs)   # same session_id — must be idempotent

        self.assertEqual(
            res1["invoice"], res2["invoice"],
            f"Idempotency violated: two different invoices for session_id={session_id}"
        )
        # Cleanup
        frappe.db.delete("Sales Invoice", {"name": res1["invoice"]})
        frappe.db.delete("GL Entry", {"voucher_no": res1["invoice"]})
        frappe.db.commit()

    # ── GAP-B03: sales_staff appears in submitted invoice remarks ──

    def test_sales_staff_attributed_in_invoice_remarks(self):
        """
        GAP-B03: sales_staff must appear in submitted invoice remarks.
        Commission attribution requires staff linkage at invoice level.
        """
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        staff_name = "Rahul Sharma"
        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(self._base_items(qty=1)),
            payments=frappe.as_json(self._base_payments(118.0)),
            sales_staff=staff_name
        )
        invoice_name = res["invoice"]
        remarks = frappe.db.get_value("Sales Invoice", invoice_name, "remarks") or ""
        self.assertIn(staff_name, remarks,
            f"sales_staff '{staff_name}' must appear in remarks for commission attribution")

        # Cleanup
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.delete("GL Entry", {"voucher_no": invoice_name})
        frappe.db.commit()
