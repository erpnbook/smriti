# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_sizewise_invoice.py
# @description: Unit tests for SMRITI Sizewise B2B Sales Tax Invoice module
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.0.0
# @license: MIT
#

import frappe
import json
import unittest
from frappe.utils import flt, cint
from smriti_retail_os.sizewise_invoice_api import (
    save_sizewise_invoice,
    submit_sizewise_invoice,
    get_sizewise_invoice,
    list_sizewise_invoices,
    cancel_sizewise_invoice,
    get_item_details_by_article
)

class TestSizewiseInvoiceAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

    def setUp(self):
        # Establish standard testing parameters
        self.company = frappe.db.exists("Company", "_Test Company") or frappe.db.get_value("Company", {}, "name")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        # Ensure the test company has a valid GSTIN
        frappe.db.set_value("Company", self.company, "gstin", "27AAXFT2508H1ZR") # Maharashtra GSTIN (state code 27)

        # Ensure the test company has a valid registered company address
        self._ensure_company_address(self.company)

        # Resolve standard CGST, SGST, IGST accounts of the test company
        def _find_account(name_pattern):
            return frappe.db.get_value(
                "Account",
                {"account_name": ["like", f"%{name_pattern}%"], "company": self.company, "is_group": 0},
                "name"
            )

        self.cgst_account = _find_account("CGST")
        self.sgst_account = _find_account("SGST")
        self.igst_account = _find_account("IGST")

        # Fallback to create them if entirely missing
        if not self.cgst_account:
            self.cgst_account = self._ensure_test_account("CGST - Test")
        if not self.sgst_account:
            self.sgst_account = self._ensure_test_account("SGST - Test")
        if not self.igst_account:
            self.igst_account = self._ensure_test_account("IGST - Test")

        # Ensure standard Item Tax Templates exist for the test company
        self.tax_template_12 = self._ensure_item_tax_template(
            "12% GST", 12.0, [(self.cgst_account, 6.0), (self.sgst_account, 6.0)]
        )
        self.tax_template_18 = self._ensure_item_tax_template(
            "18% GST", 18.0, [(self.igst_account, 18.0)]
        )

        # Create valid GST HSN Code records for India Compliance enforcement
        for hsn_code, hsn_desc in [("998311", "Test Services"), ("640399", "Footwear - Other")]:
            if not frappe.db.exists("GST HSN Code", hsn_code):
                hsn = frappe.new_doc("GST HSN Code")
                hsn.hsn_code = hsn_code
                hsn.description = hsn_desc
                hsn.insert(ignore_permissions=True)
        self.hsn_code = "640399"

        # Set user default company
        frappe.defaults.set_user_default("company", self.company, frappe.session.user)

        # Clean up any test transactions
        frappe.db.delete("Sales Taxes and Charges Template")
        frappe.db.delete("Sales Invoice", {"remarks": ["like", "%_sizewise_matrix%"]})
        frappe.db.delete("Customer", {"name": ["like", "Test B2B%"]})
        frappe.db.delete("Item", {"item_code": ["like", "TEST-ART%"]})
        frappe.db.commit()

        # Create test items (variants)
        self._ensure_test_item("TEST-ART-BLACK-36", 12)
        self._ensure_test_item("TEST-ART-BLACK-37", 12)
        self._ensure_test_item("TEST-ART-BLACK", 12)

        self._ensure_test_item("TEST-ART-18-BLACK-36", 18)
        self._ensure_test_item("TEST-ART-18-BLACK-37", 18)
        self._ensure_test_item("TEST-ART-18-BLACK", 18)

        # Create B2B customers
        self.customer_intra = self._ensure_test_customer("Test B2B Customer Intra", "27AAXFT2508H1ZR") # MH (Intrastate)
        self.customer_inter = self._ensure_test_customer("Test B2B Customer Inter", "29AABCR1718E1ZL") # KA (Interstate)

        # Set standard session user to Administrator to pass permission guards
        self.original_user = frappe.session.user
        frappe.set_user("Administrator")

    def _ensure_company_address(self, company_name):
        addr_name = f"{company_name}-Registered-Test"
        if not frappe.db.exists("Address", addr_name):
            addr = frappe.new_doc("Address")
            addr.address_title = company_name
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
            addr.append("links", {"link_doctype": "Company", "link_name": company_name})
            addr.insert(ignore_permissions=True)
            frappe.db.commit()
            return addr.name
        return addr_name

    def tearDown(self):
        frappe.set_user(self.original_user)
        # Clean up database
        frappe.db.delete("Sales Invoice", {"remarks": ["like", "%_sizewise_matrix%"]})
        frappe.db.delete("Customer", {"name": ["like", "Test B2B%"]})
        frappe.db.delete("Item", {"item_code": ["like", "TEST-ART%"]})
        frappe.db.delete("Address", {"name": ["like", "%-Registered-Test%"]})
        frappe.db.delete("Dynamic Link", {"link_name": ["like", "%_Test Company%"]})
        frappe.db.commit()

    def _ensure_test_account(self, account_name):
        acc = frappe.db.get_value("Account", {"account_name": account_name, "company": self.company}, "name")
        if not acc:
            doc = frappe.new_doc("Account")
            doc.account_name = account_name
            doc.company = self.company
            doc.parent_account = frappe.db.get_value("Account", {"is_group": 1, "company": self.company, "account_type": "Tax"}, "name") or frappe.db.get_value("Account", {"is_group": 1, "company": self.company}, "name")
            doc.account_type = "Tax"
            doc.insert(ignore_permissions=True)
            acc = doc.name
        return acc

    def _ensure_item_tax_template(self, title, pct, tax_accounts):
        itt_name = frappe.db.get_value("Item Tax Template", {"name": ["like", f"%{title}%"], "company": self.company}, "name")
        if not itt_name:
            itt = frappe.new_doc("Item Tax Template")
            itt.title = f"{title} - {self.company}"
            itt.company = self.company
            itt.gst_rate = pct
            itt.gst_treatment = "Taxable"
            for acc, rate in tax_accounts:
                if acc:
                    itt.append("taxes", {"tax_type": acc, "tax_rate": rate})
            itt.insert(ignore_permissions=True)
            itt_name = itt.name
        return itt_name

    def _ensure_test_item(self, item_code, gst_pct=12):
        if not frappe.db.exists("Item", item_code):
            item = frappe.new_doc("Item")
            item.item_code = item_code
            item.item_name = item_code
            item.item_group = frappe.db.get_value("Item Group", {}, "name")
            item.stock_uom = "Nos"
            item.is_sales_item = 1
            item.gst_hsn_code = "998311"
            item.custom_gst_percentage = str(int(gst_pct))
            
            # Map standard tax template to item row
            template = self.tax_template_12 if gst_pct == 12 else self.tax_template_18
            if template:
                item.append("taxes", {"item_tax_template": template, "tax_category": ""})
                
            item.insert(ignore_permissions=True)

    def _ensure_test_customer(self, customer_name, gstin):
        cust = frappe.new_doc("Customer")
        cust.customer_name = customer_name
        cust.customer_type = "Company"
        cust.tax_id = gstin
        cust.insert(ignore_permissions=True)
        return cust.name

    def test_save_and_submit_sizewise_invoice_intrastate(self):
        """Tests standard draft save and submission under intrastate rules (CGST+SGST)."""
        payload = {
            "invoice_name": None,
            "invoice_date": "2026-05-31",
            "customer": self.customer_intra,
            "place_of_supply": "27-Maharashtra",
            "tax_type": "intrastate",
            "size_columns": ["36", "37"],
            "rows": [
                {
                    "article": "TEST-ART",
                    "color": "BLACK",
                    "category": "SANDAL",
                    "sub_category": "LASTIC PATTA",
                    "sizes": {"36": 2, "37": 3},
                    "mrp": 1000.0,
                    "rate": 800.0,
                    "gst_pct": 12.0,
                    "hsn_code": "640399",
                    "item_code": "TEST-ART-BLACK"
                }
            ]
        }

        # 1. Save draft
        res = save_sizewise_invoice(payload)
        self.assertIsNotNone(res.get("name"))
        self.assertEqual(res.get("net_total"), 4000.0) # 5 units * 800.0 taxable rate = 4000.0
        
        # 2. Check draft invoice exist in DB
        si = frappe.get_doc("Sales Invoice", res.get("name"))
        self.assertEqual(si.docstatus, 0)
        self.assertEqual(len(si.items), 2) # exploded into 2 items (qty 2 and qty 3)
        self.assertEqual(si.items[0].qty, 2.0)
        self.assertEqual(si.items[1].qty, 3.0)

        # Verify that item_tax_rate is populated on item rows
        for item in si.items:
            tax_rate_dict = json.loads(item.item_tax_rate or "{}")
            self.assertEqual(tax_rate_dict.get(self.cgst_account), 6.0)
            self.assertEqual(tax_rate_dict.get(self.sgst_account), 6.0)

        # 3. Submit invoice
        sub_res = submit_sizewise_invoice(res.get("name"))
        self.assertEqual(sub_res.get("name"), res.get("name"))

        # Re-fetch submitted invoice and verify totals/taxes calculated by ERPNext
        si_submitted = frappe.get_doc("Sales Invoice", res.get("name"))
        self.assertEqual(si_submitted.docstatus, 1)
        self.assertEqual(flt(si_submitted.net_total), 4000.0)
        self.assertEqual(flt(si_submitted.grand_total), 4480.0) # 4000 + 12% GST = 4480.0

        # Verify tax table aggregation
        self.assertEqual(len(si_submitted.taxes), 2)
        tax_accounts = [t.account_head for t in si_submitted.taxes]
        self.assertIn(self.cgst_account, tax_accounts)
        self.assertIn(self.sgst_account, tax_accounts)

    def test_save_and_submit_sizewise_invoice_with_discount(self):
        """Tests draft save and submission with discount_percentage applied to line items."""
        payload = {
            "invoice_name": None,
            "invoice_date": "2026-05-31",
            "customer": self.customer_intra,
            "place_of_supply": "27-Maharashtra",
            "tax_type": "intrastate",
            "size_columns": ["36", "37"],
            "rows": [
                {
                    "article": "TEST-ART",
                    "color": "BLACK",
                    "category": "SANDAL",
                    "sub_category": "LASTIC PATTA",
                    "sizes": {"36": 2, "37": 3},
                    "mrp": 1000.0,
                    "rate": 800.0,
                    "discount_percentage": 35.0, # 35% discount
                    "gst_pct": 12.0,
                    "hsn_code": "640399",
                    "item_code": "TEST-ART-BLACK"
                }
            ]
        }

        # 1. Save draft
        res = save_sizewise_invoice(payload)
        self.assertIsNotNone(res.get("name"))

        # 2. Check draft invoice exists in DB
        si = frappe.get_doc("Sales Invoice", res.get("name"))
        self.assertEqual(si.docstatus, 0)
        self.assertEqual(len(si.items), 2)

        # Check discount_percentage is correctly saved
        for item in si.items:
            self.assertEqual(flt(item.discount_percentage), 35.0)

        # 3. Submit invoice
        submit_sizewise_invoice(res.get("name"))

        # Re-fetch submitted invoice and verify totals/taxes calculated by ERPNext
        si_submitted = frappe.get_doc("Sales Invoice", res.get("name"))
        self.assertEqual(si_submitted.docstatus, 1)

        # Net total should be: 5 units * 800.0 * (1 - 0.35) = 5 * 520 = 2600.0
        self.assertEqual(flt(si_submitted.net_total), 2600.0)
        # Grand total should be: 2600 + 12% GST = 2600 * 1.12 = 2912.0
        self.assertEqual(flt(si_submitted.grand_total), 2912.0)

        # Verify tax table aggregation (CGST + SGST)
        self.assertEqual(len(si_submitted.taxes), 2)
        for tax in si_submitted.taxes:
            if tax.account_head == self.cgst_account:
                self.assertEqual(flt(tax.tax_amount), 156.0) # 2600 * 6% = 156.0
            elif tax.account_head == self.sgst_account:
                self.assertEqual(flt(tax.tax_amount), 156.0) # 2600 * 6% = 156.0

    def test_create_sizewise_invoice_interstate(self):
        """Tests standard draft save and submission under interstate rules (IGST)."""
        payload = {
            "invoice_name": None,
            "invoice_date": "2026-05-31",
            "customer": self.customer_inter,
            "place_of_supply": "29-Karnataka",
            "tax_type": "interstate",
            "size_columns": ["36", "37"],
            "rows": [
                {
                    "article": "TEST-ART-18",
                    "color": "BLACK",
                    "category": "SANDAL",
                    "sub_category": "LASTIC PATTA",
                    "sizes": {"36": 5, "37": 5},
                    "mrp": 1000.0,
                    "rate": 900.0,
                    "gst_pct": 18.0,
                    "hsn_code": "640399",
                    "item_code": "TEST-ART-18-BLACK"
                }
            ]
        }

        # 1. Save draft
        res = save_sizewise_invoice(payload)
        si = frappe.get_doc("Sales Invoice", res.get("name"))

        # Verify that item_tax_rate is populated with IGST
        for item in si.items:
            tax_rate_dict = json.loads(item.item_tax_rate or "{}")
            self.assertEqual(tax_rate_dict.get(self.igst_account), 18.0)

        # 2. Submit invoice
        submit_sizewise_invoice(res.get("name"))
        si_sub = frappe.get_doc("Sales Invoice", res.get("name"))

        self.assertEqual(flt(si_sub.net_total), 9000.0) # 10 units * 900 = 9000.0
        self.assertEqual(flt(si_sub.grand_total), 10620.0) # 9000 + 18% IGST = 10620.0
        self.assertEqual(len(si_sub.taxes), 1)
        self.assertEqual(si_sub.taxes[0].account_head, self.igst_account)

    def test_matrix_persistence_and_reload(self):
        """Tests that the full sizewise matrix snapshot persists and reloads perfectly."""
        payload = {
            "invoice_name": None,
            "customer": self.customer_intra,
            "place_of_supply": "27-Maharashtra",
            "tax_type": "intrastate",
            "size_columns": ["36", "37"],
            "rows": [
                {
                    "article": "TEST-ART",
                    "color": "BLACK",
                    "sizes": {"36": 2, "37": 3},
                    "mrp": 1000.0,
                    "rate": 800.0,
                    "gst_pct": 12.0,
                    "hsn_code": "640399",
                    "item_code": "TEST-ART-BLACK"
                }
            ]
        }

        res = save_sizewise_invoice(payload)
        invoice_name = res.get("name")

        # Load back
        loaded = get_sizewise_invoice(invoice_name)
        self.assertEqual(loaded.get("invoice_name"), invoice_name)
        self.assertEqual(loaded.get("customer"), self.customer_intra)
        self.assertEqual(loaded.get("tax_type"), "intrastate")
        self.assertEqual(loaded.get("size_columns"), ["36", "37"])
        self.assertEqual(len(loaded.get("rows")), 1)
        self.assertEqual(loaded.get("rows")[0].get("article"), "TEST-ART")
        self.assertEqual(loaded.get("rows")[0].get("sizes").get("36"), 2)
        self.assertEqual(loaded.get("rows")[0].get("sizes").get("37"), 3)

    def test_get_item_details_by_article(self):
        """Tests that get_item_details_by_article works cleanly for exact, fuzzy, and variant matching."""
        # 1. Exact match on parent item
        res = get_item_details_by_article("TEST-ART-BLACK")
        self.assertEqual(res.get("article"), "TEST-ART-BLACK")
        self.assertEqual(res.get("gst_pct"), 12.0)
        
        # 2. Fuzzy match
        res_fuzzy = get_item_details_by_article("TEST-ART")
        self.assertIsNotNone(res_fuzzy.get("article"))
        self.assertIn("TEST-ART", res_fuzzy.get("article"))
        
        # 3. Blank check
        self.assertEqual(get_item_details_by_article(""), {})

    def test_security_guards_anonymous_rejection(self):
        """Tests that non-billing users and Guest sessions are rejected with a PermissionError."""
        payload = {
            "invoice_name": None,
            "customer": self.customer_intra,
            "rows": []
        }

        # Set user session to Guest
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            save_sizewise_invoice(payload)

        # Set user session to a custom user with no roles
        frappe.set_user("test@example.com")
        if not frappe.db.exists("User", "test@example.com"):
            user = frappe.new_doc("User")
            user.email = "test@example.com"
            user.first_name = "Test User"
            user.insert(ignore_permissions=True)
            
        with self.assertRaises(frappe.PermissionError):
            save_sizewise_invoice(payload)
