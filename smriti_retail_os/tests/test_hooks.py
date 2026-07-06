# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_hooks.py
# @description: Unit tests for SMRITI Frappe event hooks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.utils import flt, cint

class TestSmritiRetailHooks(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

    def setUp(self):
        # Clean up any test records
        frappe.db.delete("Item", {"item_code": "TEST-SHIRT"})
        frappe.db.delete("Customer", {"customer_name": "Test Rajesh Kumar"})
        frappe.db.delete("Supplier", {"supplier_name": "Test ABC Wholesalers"})
        frappe.db.delete("Address", {"address_title": ["like", "Test%"]})
        frappe.db.commit()

        # Ensure a default Supplier Group exists and fetch it
        self.supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
        if not self.supplier_group:
            sg = frappe.new_doc("Supplier Group")
            sg.supplier_group_name = "Test Local"
            sg.insert(ignore_permissions=True)
            self.supplier_group = sg.name

    def tearDown(self):
        # Clean up test records
        frappe.db.delete("Item", {"item_code": "TEST-SHIRT"})
        frappe.db.delete("Customer", {"customer_name": "Test Rajesh Kumar"})
        frappe.db.delete("Supplier", {"supplier_name": "Test ABC Wholesalers"})
        frappe.db.delete("Address", {"address_title": ["like", "Test%"]})
        frappe.db.commit()

    def test_customer_address_sync(self):
        """
        Tests that saving a Customer with custom_address_text auto-generates
        a standard linked Address record.
        """
        cust = frappe.new_doc("Customer")
        cust.customer_name = "Test Rajesh Kumar"
        cust.customer_type = "Individual"
        cust.primary_mobile_no = "9876543210"
        cust.tax_id = "29AABCR1718E1ZL" # Mathematically valid Karnataka GSTIN from India Compliance
        cust.custom_address_text = "Flat 402, Green Glen Layout\nBangalore\n560103"
        cust.insert(ignore_permissions=True)
        
        # Verify that Address record was created in the database and linked
        addr_name = frappe.db.get_value(
            "Address", 
            {
                "links.link_doctype": "Customer",
                "links.link_name": cust.name,
                "address_type": "Billing"
            }, 
            "name"
        )
        self.assertIsNotNone(addr_name)
        
        addr = frappe.get_doc("Address", addr_name)
        self.assertEqual(addr.address_line1, "Flat 402, Green Glen Layout")
        self.assertEqual(addr.address_line2, "Bangalore, 560103")
        self.assertEqual(addr.country, "India")
        self.assertEqual(addr.state, "Karnataka") # Resolved from GSTIN!

    def test_supplier_address_and_credit_days(self):
        """
        Tests that saving a Supplier auto-generates linked Address
        and creates/links a Payment Terms Template matching custom_credit_days.
        """
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = "Test ABC Wholesalers"
        supp.supplier_group = self.supplier_group
        supp.gstin = "29AABCR1718E1ZL"
        supp.custom_address_text = "Shed 4B, Peenya Industrial Area\nBangalore"
        supp.custom_credit_days = 45
        supp.insert(ignore_permissions=True)
        
        # 1. Verify address sync
        addr_name = frappe.db.get_value(
            "Address", 
            {
                "links.link_doctype": "Supplier",
                "links.link_name": supp.name,
                "address_type": "Billing"
            }, 
            "name"
        )
        self.assertIsNotNone(addr_name)
        addr = frappe.get_doc("Address", addr_name)
        self.assertEqual(addr.address_line1, "Shed 4B, Peenya Industrial Area")
        self.assertEqual(addr.state, "Karnataka") # Resolved from GSTIN!
        
        # 2. Verify Payment Term generation & linking
        supp_reload = frappe.get_doc("Supplier", supp.name)
        self.assertEqual(supp_reload.payment_terms, "Credit Term - 45 Days")
        
        # Verify Payment Term template exists
        ptt_exists = frappe.db.exists("Payment Terms Template", "Credit Term - 45 Days")
        self.assertTrue(ptt_exists)
        
        # Inspect terms
        ptt = frappe.get_doc("Payment Terms Template", "Credit Term - 45 Days")
        self.assertEqual(len(ptt.terms), 1)
        self.assertEqual(ptt.terms[0].credit_days, 45)

    def test_rich_customer_supplier_crud(self):
        """
        Tests SMRITI Customer and Supplier rich compliance details, billing & shipping
        address sync triggers, and tax inclusive overrides.
        """
        # 1. Customer Rich CRUD
        cust = frappe.new_doc("Customer")
        cust.customer_name = "Test Rajesh Kumar"
        cust.customer_type = "Company"
        cust.tax_id = "27AAXFT2508H1ZR" # Maharashtra GSTIN
        cust.custom_address_text = "Billing Street 1\nUmerkhadi\nMumbai\nMaharashtra\n400003"
        cust.custom_shipping_address_text = "Shipping Street 1\nPeenya\nBangalore\nKarnataka\n560058"
        cust.custom_tax_inclusive_override = "Inclusive"
        cust.insert(ignore_permissions=True)

        # Check billing address
        bill_addr = frappe.db.get_value("Address", {"links.link_name": cust.name, "address_type": "Billing"}, "name")
        self.assertIsNotNone(bill_addr)
        b_addr = frappe.get_doc("Address", bill_addr)
        self.assertEqual(b_addr.address_line1, "Billing Street 1")
        self.assertEqual(b_addr.state, "Maharashtra")

        # Check shipping address
        ship_addr = frappe.db.get_value("Address", {"links.link_name": cust.name, "address_type": "Shipping"}, "name")
        self.assertIsNotNone(ship_addr)
        s_addr = frappe.get_doc("Address", ship_addr)
        self.assertEqual(s_addr.address_line1, "Shipping Street 1")
        self.assertEqual(s_addr.state, "Karnataka") # Resolved from shipping text if state hook is active

        # Check tax override
        self.assertEqual(cust.custom_tax_inclusive_override, "Inclusive")

        # 2. Supplier Rich CRUD
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = "Test ABC Wholesalers"
        supp.supplier_group = self.supplier_group
        supp.gstin = "27AAXFT2508H1ZR"
        supp.custom_address_text = "Supplier Bill 1\nMumbai\nMaharashtra\n400003"
        supp.custom_shipping_address_text = "Supplier Ship 1\nBangalore\nKarnataka\n560058"
        supp.custom_credit_days = 60
        supp.insert(ignore_permissions=True)

        # Check billing and shipping addresses linked to supplier
        s_bill = frappe.db.get_value("Address", {"links.link_name": supp.name, "address_type": "Billing"}, "name")
        s_ship = frappe.db.get_value("Address", {"links.link_name": supp.name, "address_type": "Shipping"}, "name")
        self.assertIsNotNone(s_bill)
        self.assertIsNotNone(s_ship)

        # Check payment terms template link
        supp_reload = frappe.get_doc("Supplier", supp.name)
        self.assertEqual(supp_reload.payment_terms, "Credit Term - 60 Days")

    def test_desk_access_redirection(self):
        """
        Tests that accessing /desk and /app routes for non-desk users
        raises a Werkzeug RequestRedirect to /smriti.
        """
        import werkzeug.routing.exceptions
        from smriti_retail_os.boot import check_desk_access

        # Save current state to restore later
        original_user = frappe.session.user
        original_request = getattr(frappe.local, "request", None)

        try:
            # Test Guest redirection on /desk
            frappe.session.user = "Guest"
            req = frappe._dict({"path": "/desk", "cookies": {}})
            frappe.local.request = req
            with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect) as context:
                check_desk_access()
            # In Werkzeug, the target url is stored in new_url
            self.assertEqual(context.exception.new_url, "/smriti")

            # Test Guest redirection on /app
            req = frappe._dict({"path": "/app", "cookies": {}})
            frappe.local.request = req
            with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect) as context:
                check_desk_access()
            self.assertEqual(context.exception.new_url, "/smriti")

            # Test Administrator bypasses redirect (no exception raised)
            frappe.session.user = "Administrator"
            req = frappe._dict({"path": "/app", "cookies": {}})
            frappe.local.request = req
            check_desk_access()

        finally:
            frappe.session.user = original_user
            if original_request:
                frappe.local.request = original_request
            else:
                delattr(frappe.local, "request")
