# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_reports.py
# @description: Unit tests for SMRITI reporting engine, templates, saved views, caching, and APIs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-07
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
import hashlib
from smriti_retail_os.reports_api import (
    SMRITIReportEngine,
    get_smriti_report_data,
    save_smriti_saved_view,
    get_smriti_saved_views,
    delete_smriti_saved_view,
    get_smriti_reports_list
)

class TestSmritiReports(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

        # Use standard pre-configured _Test Company
        cls.company_name = "_Test Company"
        if not frappe.db.exists("Company", cls.company_name):
            cls.company = frappe.new_doc("Company")
            cls.company.company_name = cls.company_name
            cls.company.default_currency = "INR"
            cls.company.country = "India"
            cls.company.insert(ignore_permissions=True)
            frappe.db.commit()

        # Ensure test customer exists
        cls.customer_name = "Test Customer reports"
        if not frappe.db.exists("Customer", cls.customer_name):
            cust = frappe.new_doc("Customer")
            cust.customer_name = cls.customer_name
            cust.customer_group = frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups"
            cust.territory = frappe.db.get_value("Territory", {}, "name") or "All Territories"
            cust.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            frappe.db.commit()

        # Ensure test supplier exists
        cls.supplier_name = "Test Supplier reports"
        if not frappe.db.exists("Supplier", cls.supplier_name):
            supp = frappe.new_doc("Supplier")
            supp.supplier_name = cls.supplier_name
            supp.supplier_group = frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"
            supp.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        # Remove only the test customer and supplier. Keep standard company.
        frappe.db.delete("Customer", {"customer_name": cls.customer_name})
        frappe.db.delete("Supplier", {"supplier_name": cls.supplier_name})
        frappe.db.commit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # Clean up any leftover entries from previous aborted test runs
        frappe.db.delete("Payment Entry", {"company": self.company_name, "party": ["in", [self.customer_name, self.supplier_name]]})
        frappe.db.delete("Sales Invoice", {"company": self.company_name, "customer": self.customer_name})
        frappe.db.delete("Purchase Invoice", {"company": self.company_name, "supplier": self.supplier_name})
        frappe.db.delete("Payment Ledger Entry", {"company": self.company_name, "party": ["in", [self.customer_name, self.supplier_name]]})
        frappe.db.sql("""
            DELETE FROM `tabPayment Entry Reference` 
            WHERE parent NOT IN (SELECT name FROM `tabPayment Entry`)
        """)
        frappe.db.commit()

    def tearDown(self):
        # Clean up entries created by this test
        frappe.db.delete("Payment Entry", {"company": self.company_name, "party": ["in", [self.customer_name, self.supplier_name]]})
        frappe.db.delete("Sales Invoice", {"company": self.company_name, "customer": self.customer_name})
        frappe.db.delete("Purchase Invoice", {"company": self.company_name, "supplier": self.supplier_name})
        frappe.db.delete("Payment Ledger Entry", {"company": self.company_name, "party": ["in", [self.customer_name, self.supplier_name]]})
        frappe.db.sql("""
            DELETE FROM `tabPayment Entry Reference` 
            WHERE parent NOT IN (SELECT name FROM `tabPayment Entry`)
        """)
        frappe.db.commit()
        super().tearDown()

    def test_get_reports_list(self):
        """Tests that get_smriti_reports_list returns standard templates."""
        reports = get_smriti_reports_list()
        self.assertTrue(len(reports) >= 8)
        keys = [r.report_key for r in reports]
        self.assertIn("item_wise_sales", keys)
        self.assertIn("daily_sales_summary", keys)
        self.assertIn("cash_z_report", keys)
        self.assertIn("current_stock_position", keys)
        self.assertIn("size_wise_stock", keys)

    def test_report_engine_cache_key(self):
        """Tests the MD5 hash generation for caching reporting parameters."""
        filters = {"company": self.company_name, "from_date": "2026-06-01", "to_date": "2026-06-07"}
        engine = SMRITIReportEngine("item_wise_sales", filters)
        cache_key = engine.get_cache_key()
        
        # Calculate expected hash using correct cache_dict structure
        company = filters.get("company") or frappe.defaults.get_user_default("Company") or ""
        user = frappe.session.user or "Guest"
        roles = sorted(frappe.get_roles(user))
        cache_dict = {
            "filters": filters,
            "company": company,
            "user": user,
            "roles": roles
        }
        filter_hash = hashlib.md5(
            json.dumps(cache_dict, sort_keys=True).encode("utf-8")
        ).hexdigest()
        expected_key = f"smriti:item_wise_sales:{filter_hash}"
        self.assertEqual(cache_key, expected_key)

    def test_report_execution_and_caching(self):
        """Tests engine execution, cache writing, and caching retrieval."""
        # Clean cache first
        filters = {"company": self.company_name}
        engine = SMRITIReportEngine("item_wise_sales", filters)
        cache_key = engine.get_cache_key()
        frappe.cache().delete_value(cache_key)

        # Force template to have cache minutes
        frappe.db.set_value("SMRITI Report Template", "item_wise_sales", "cache_minutes", 10)
        frappe.db.commit()

        # Run report
        data = get_smriti_report_data("item_wise_sales", filters)
        self.assertIsNotNone(data)

        # Verify cached value exists
        cached = frappe.cache().get_value(cache_key)
        self.assertIsNotNone(cached)
        cached_data = json.loads(cached)
        self.assertEqual(len(data), len(cached_data))

        # Reset cache setting
        frappe.db.set_value("SMRITI Report Template", "item_wise_sales", "cache_minutes", 0)
        frappe.db.commit()
        frappe.cache().delete_value(cache_key)

    def test_saved_views_lifecycle(self):
        """Tests creating, fetching, and deleting saved views."""
        report_key = "item_wise_sales"
        view_name = "Test Sales View"
        applied_filters = {"company": self.company_name, "brand": "Smriti"}
        visible_cols = ["item_code", "item_name", "qty_sold"]

        # 1. Save view
        view_doc_name = save_smriti_saved_view(
            view_name=view_name,
            report_key=report_key,
            applied_filters_json=json.dumps(applied_filters),
            visible_columns_json=json.dumps(visible_cols),
            is_default=0
        )
        self.assertIsNotNone(view_doc_name)

        # 2. Get views
        views = get_smriti_saved_views(report_key)
        self.assertTrue(len(views) > 0)
        view_match = [v for v in views if v.name == view_doc_name][0]
        self.assertEqual(view_match.view_name, view_name)
        self.assertEqual(json.loads(view_match.applied_filters_json), applied_filters)
        self.assertEqual(json.loads(view_match.visible_columns_json), visible_cols)

        # 3. Delete view
        result = delete_smriti_saved_view(view_doc_name)
        self.assertEqual(result.get("success"), True)
        self.assertFalse(frappe.db.exists("SMRITI Saved View", view_doc_name))

    def test_saved_view_column_reordering(self):
        """Tests that custom column reordering is preserved in SMRITI Saved Views."""
        report_key = "daily_sales_summary"
        view_name = "Custom Reordered Daily Summary"
        applied_filters = {"company": self.company_name}
        
        # Simulating a dragged column reordering sequence
        custom_column_order = ["payment_mode", "posting_date", "total_invoices", "total_amount"]
        
        # 1. Save the custom view with the reordered column array
        view_doc_name = save_smriti_saved_view(
            view_name=view_name,
            report_key=report_key,
            applied_filters_json=json.dumps(applied_filters),
            visible_columns_json=json.dumps(custom_column_order),
            is_default=0
        )
        self.assertIsNotNone(view_doc_name)
        
        try:
            # 2. Retrieve views and verify the custom column order sequence is preserved exactly
            views = get_smriti_saved_views(report_key)
            matching_views = [v for v in views if v.name == view_doc_name]
            self.assertEqual(len(matching_views), 1)
            
            saved_order = json.loads(matching_views[0].visible_columns_json)
            self.assertEqual(saved_order, custom_column_order)
            self.assertEqual(saved_order[0], "payment_mode")
            self.assertEqual(saved_order[-1], "total_amount")
        finally:
            # 3. Clean up the saved view doc
            delete_smriti_saved_view(view_doc_name)

    def test_accounting_reports_seeding(self):
        """Tests that get_smriti_reports_list contains SMRITI Accounting Analytics reports."""
        reports = get_smriti_reports_list()
        keys = [r.report_key for r in reports]
        
        self.assertIn("payment_register", keys)
        self.assertIn("receipt_register", keys)
        self.assertIn("cash_book", keys)
        self.assertIn("day_book", keys)
        self.assertIn("customer_outstanding", keys)
        self.assertIn("supplier_outstanding", keys)
        
        # Verify categories
        for r in reports:
            if r.report_key in ["payment_register", "receipt_register", "cash_book", "day_book", "customer_outstanding", "supplier_outstanding"]:
                self.assertEqual(r.report_category, "Accounting")

    def test_payment_and_receipt_registers(self):
        """Tests payment_register and receipt_register SQL reports."""
        # Insert mock Sales Invoice first to satisfy reference validation in Payment Entry
        si_ref = frappe.new_doc("Sales Invoice")
        si_ref.company = self.company_name
        si_ref.customer = self.customer_name
        si_ref.currency = "INR"
        si_ref.grand_total = 5000.0
        si_ref.base_grand_total = 5000.0
        si_ref.base_rounded_total = 5000.0
        si_ref.rounded_total = 5000.0
        si_ref.base_net_total = 5000.0
        si_ref.net_total = 5000.0
        si_ref.outstanding_amount = 5000.0
        si_ref.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        
        si_ref_name = si_ref.name
        frappe.db.set_value("Sales Invoice", si_ref_name, {
            "posting_date": "2026-06-01",
            "outstanding_amount": 5000.0,
            "docstatus": 1
        })

        # Create mock Payment Ledger Entry so Payment Entry validation sees the invoice as outstanding
        ple = frappe.new_doc("Payment Ledger Entry")
        ple.company = self.company_name
        ple.posting_date = "2026-06-01"
        ple.due_date = "2026-06-01"
        ple.account_type = "Receivable"
        ple.account = "Debtors - _C"
        ple.party_type = "Customer"
        ple.party = self.customer_name
        ple.voucher_type = "Sales Invoice"
        ple.voucher_no = si_ref_name
        ple.against_voucher_type = "Sales Invoice"
        ple.against_voucher_no = si_ref_name
        ple.amount = 5000.0
        ple.amount_in_account_currency = 5000.0
        ple.account_currency = "INR"
        ple.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

        frappe.clear_document_cache("Sales Invoice", si_ref_name)
        frappe.db.commit()
        
        pe_rec = frappe.new_doc("Payment Entry")
        pe_rec.payment_type = "Receive"
        pe_rec.party_type = "Customer"
        pe_rec.party = self.customer_name
        pe_rec.company = self.company_name
        pe_rec.mode_of_payment = "Cash"
        pe_rec.paid_amount = 5000.0
        pe_rec.received_amount = 5000.0
        pe_rec.source_exchange_rate = 1.0
        pe_rec.target_exchange_rate = 1.0
        pe_rec.paid_from = "Debtors - _C"
        pe_rec.paid_to = "Cash - _C"
        pe_rec.paid_from_account_currency = "INR"
        pe_rec.paid_to_account_currency = "INR"
        
        # Append Reference as child row
        pe_rec.append("references", {
            "reference_doctype": "Sales Invoice",
            "reference_name": si_ref_name,
            "allocated_amount": 5000.0
        })
        pe_rec.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pe_receive_name = pe_rec.name
        frappe.db.set_value("Payment Entry", pe_receive_name, {
            "posting_date": "2026-06-01",
            "paid_amount": 5000.0,
            "base_paid_amount": 5000.0,
            "received_amount": 5000.0,
            "base_received_amount": 5000.0,
            "source_exchange_rate": 1.0,
            "target_exchange_rate": 1.0,
            "reference_no": "REF-REC-001",
            "docstatus": 1
        })

        # Insert mock Payment Entry (docstatus=1) for Pay
        pe_pay = frappe.new_doc("Payment Entry")
        pe_pay.payment_type = "Pay"
        pe_pay.party_type = "Supplier"
        pe_pay.party = self.supplier_name
        pe_pay.company = self.company_name
        pe_pay.mode_of_payment = "Bank"
        pe_pay.paid_amount = 3000.0
        pe_pay.received_amount = 3000.0
        pe_pay.source_exchange_rate = 1.0
        pe_pay.target_exchange_rate = 1.0
        pe_pay.paid_from = "Cash - _C"
        pe_pay.paid_to = "Creditors - _C"
        pe_pay.paid_from_account_currency = "INR"
        pe_pay.paid_to_account_currency = "INR"
        pe_pay.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pe_pay_name = pe_pay.name
        frappe.db.set_value("Payment Entry", pe_pay_name, {
            "posting_date": "2026-06-01",
            "paid_amount": 3000.0,
            "base_paid_amount": 3000.0,
            "received_amount": 3000.0,
            "base_received_amount": 3000.0,
            "source_exchange_rate": 1.0,
            "target_exchange_rate": 1.0,
            "reference_no": "REF-PAY-001",
            "remarks": "Test Payment Remarks",
            "docstatus": 1
        })
        
        frappe.db.commit()

        # 1. Run Payment Register
        filters = {
            "company": self.company_name,
            "from_date": "2026-06-01",
            "to_date": "2026-06-02"
        }
        res_pay = get_smriti_report_data("payment_register", filters)
        self.assertTrue(len(res_pay) > 0)
        match_pay = [r for r in res_pay if r.payment_entry_no == pe_pay_name]
        self.assertEqual(len(match_pay), 1)
        self.assertEqual(match_pay[0].party, self.supplier_name)
        self.assertEqual(float(match_pay[0].paid_amount), 3000.0)

        # 2. Run Receipt Register
        res_rec = get_smriti_report_data("receipt_register", filters)
        self.assertTrue(len(res_rec) > 0)
        match_rec = [r for r in res_rec if r.receipt_no == pe_receive_name]
        self.assertEqual(len(match_rec), 1)
        self.assertEqual(match_rec[0].customer, self.customer_name)
        self.assertEqual(float(match_rec[0].amount_received), 5000.0)
        self.assertEqual(match_rec[0].against_invoice, si_ref_name)

        # Cleanup
        frappe.db.delete("Payment Entry", pe_receive_name)
        frappe.db.delete("Payment Entry Reference", {"parent": pe_receive_name})
        frappe.db.delete("Payment Entry", pe_pay_name)
        frappe.db.delete("Sales Invoice", si_ref_name)
        frappe.db.commit()

    def test_cash_book(self):
        """Tests cash_book aggregator calculation."""
        # Use existing Cash - _C account under _Test Company
        cash_account = "Cash - _C"
        company = self.company_name
        
        # Insert test GL Entries
        gle_name1 = "GLE-TEST-CASH-001"
        gle_name2 = "GLE-TEST-CASH-002"
        frappe.db.delete("GL Entry", {"voucher_no": ["in", [gle_name1, gle_name2]]})
        
        # Opening entry (dated before from_date)
        gle1 = frappe.new_doc("GL Entry")
        gle1.posting_date = "2026-05-31"
        gle1.account = cash_account
        gle1.company = company
        gle1.debit = 10000.0
        gle1.credit = 0.0
        gle1.voucher_type = "Journal Entry"
        gle1.voucher_no = gle_name1
        gle1.docstatus = 1
        gle1.is_cancelled = 0
        gle1.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

        # Current entry (dated within from_date to_date)
        gle2 = frappe.new_doc("GL Entry")
        gle2.posting_date = "2026-06-01"
        gle2.account = cash_account
        gle2.company = company
        gle2.debit = 5000.0
        gle2.credit = 2000.0
        gle2.voucher_type = "Journal Entry"
        gle2.voucher_no = gle_name2
        gle2.docstatus = 1
        gle2.is_cancelled = 0
        gle2.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        
        frappe.db.commit()

        filters = {
            "company": company,
            "from_date": "2026-06-01",
            "to_date": "2026-06-01"
        }
        res = get_smriti_report_data("cash_book", filters)
        self.assertTrue(len(res) > 0)
        self.assertEqual(float(res[0]["opening_balance"]), 10000.0)
        self.assertEqual(float(res[0]["cash_receipts"]), 5000.0)
        self.assertEqual(float(res[0]["cash_payments"]), 2000.0)
        self.assertEqual(float(res[0]["closing_balance"]), 13000.0)

        # Cleanup
        frappe.db.delete("GL Entry", {"voucher_no": ["in", [gle_name1, gle_name2]]})
        frappe.db.commit()

    def test_day_book(self):
        """Tests day_book multi-doctype business daily summary aggregator."""
        company = self.company_name
        
        # Create mock Sales Invoice
        si = frappe.new_doc("Sales Invoice")
        si.company = company
        si.customer = self.customer_name
        si.currency = "INR"
        si.is_return = 0
        si.grand_total = 15000.0
        si.base_grand_total = 15000.0
        si.base_rounded_total = 15000.0
        si.rounded_total = 15000.0
        si.base_net_total = 15000.0
        si.net_total = 15000.0
        si.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        si_name = si.name
        frappe.db.set_value("Sales Invoice", si_name, {
            "posting_date": "2026-06-01",
            "docstatus": 1
        })

        # Create mock Purchase Invoice
        pi = frappe.new_doc("Purchase Invoice")
        pi.company = company
        pi.supplier = self.supplier_name
        pi.currency = "INR"
        pi.is_return = 0
        pi.grand_total = 8000.0
        pi.base_grand_total = 8000.0
        pi.base_rounded_total = 8000.0
        pi.rounded_total = 8000.0
        pi.base_net_total = 8000.0
        pi.net_total = 8000.0
        pi.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pi_name = pi.name
        frappe.db.set_value("Purchase Invoice", pi_name, {
            "posting_date": "2026-06-01",
            "docstatus": 1
        })

        # Create mock Payment Entry (Receive)
        pe_rec = frappe.new_doc("Payment Entry")
        pe_rec.payment_type = "Receive"
        pe_rec.party_type = "Customer"
        pe_rec.party = self.customer_name
        pe_rec.company = company
        pe_rec.paid_amount = 12000.0
        pe_rec.received_amount = 12000.0
        pe_rec.source_exchange_rate = 1.0
        pe_rec.target_exchange_rate = 1.0
        pe_rec.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pe_rec_name = pe_rec.name
        frappe.db.set_value("Payment Entry", pe_rec_name, {
            "posting_date": "2026-06-01",
            "paid_amount": 12000.0,
            "base_paid_amount": 12000.0,
            "received_amount": 12000.0,
            "base_received_amount": 12000.0,
            "source_exchange_rate": 1.0,
            "target_exchange_rate": 1.0,
            "docstatus": 1
        })

        # Create mock Payment Entry (Pay)
        pe_pay = frappe.new_doc("Payment Entry")
        pe_pay.payment_type = "Pay"
        pe_pay.party_type = "Supplier"
        pe_pay.party = self.supplier_name
        pe_pay.company = company
        pe_pay.paid_amount = 5000.0
        pe_pay.received_amount = 5000.0
        pe_pay.source_exchange_rate = 1.0
        pe_pay.target_exchange_rate = 1.0
        pe_pay.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pe_pay_name = pe_pay.name
        frappe.db.set_value("Payment Entry", pe_pay_name, {
            "posting_date": "2026-06-01",
            "paid_amount": 5000.0,
            "base_paid_amount": 5000.0,
            "received_amount": 5000.0,
            "base_received_amount": 5000.0,
            "source_exchange_rate": 1.0,
            "target_exchange_rate": 1.0,
            "docstatus": 1
        })

        frappe.db.commit()

        filters = {
            "company": company,
            "from_date": "2026-06-01",
            "to_date": "2026-06-01"
        }
        res = get_smriti_report_data("day_book", filters)
        self.assertTrue(len(res) > 0)
        day_row = res[0]
        self.assertEqual(day_row["date"], "2026-06-01")
        self.assertEqual(float(day_row["sales"]), 15000.0)
        self.assertEqual(float(day_row["purchases"]), 8000.0)
        self.assertEqual(float(day_row["receipts"]), 12000.0)
        self.assertEqual(float(day_row["payments"]), 5000.0)
        self.assertEqual(float(day_row["net_cash_position"]), 7000.0)

        # Cleanup
        frappe.db.delete("Sales Invoice", si_name)
        frappe.db.delete("Purchase Invoice", pi_name)
        frappe.db.delete("Payment Entry", pe_rec_name)
        frappe.db.delete("Payment Entry", pe_pay_name)
        frappe.db.commit()

    def test_outstandings_and_ageing(self):
        """Tests customer and supplier outstanding aging reports and filters."""
        company = self.company_name
        
        # 1. Customer Outstanding
        si = frappe.new_doc("Sales Invoice")
        si.company = company
        si.customer = self.customer_name
        si.currency = "INR"
        si.is_return = 0
        si.grand_total = 25000.0
        si.base_grand_total = 25000.0
        si.base_rounded_total = 25000.0
        si.rounded_total = 25000.0
        si.base_net_total = 25000.0
        si.net_total = 25000.0
        si.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        si_name = si.name
        
        from frappe.utils import add_days, nowdate
        frappe.db.set_value("Sales Invoice", si_name, {
            "posting_date": add_days(nowdate(), -45),
            "due_date": add_days(nowdate(), -15),
            "outstanding_amount": 25000.0,
            "docstatus": 1
        })

        # 2. Supplier Outstanding
        pi = frappe.new_doc("Purchase Invoice")
        pi.company = company
        pi.supplier = self.supplier_name
        pi.currency = "INR"
        pi.is_return = 0
        pi.grand_total = 18000.0
        pi.base_grand_total = 18000.0
        pi.base_rounded_total = 18000.0
        pi.rounded_total = 18000.0
        pi.base_net_total = 18000.0
        pi.net_total = 18000.0
        pi.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        pi_name = pi.name
        
        frappe.db.set_value("Purchase Invoice", pi_name, {
            "posting_date": add_days(nowdate(), -15),
            "due_date": nowdate(),
            "outstanding_amount": 18000.0,
            "docstatus": 1
        })

        frappe.db.commit()

        # Test Customer Outstanding report
        res_cust = get_smriti_report_data("customer_outstanding", {"company": company})
        self.assertTrue(len(res_cust) > 0)
        match_cust = [r for r in res_cust if r.invoice == si_name]
        self.assertEqual(len(match_cust), 1)
        self.assertEqual(match_cust[0].customer, self.customer_name)
        self.assertEqual(float(match_cust[0].outstanding_amount), 25000.0)
        self.assertTrue(match_cust[0].ageing_days >= 40)

        # Test Ageing bucket filter on Customer Outstanding
        res_cust_bucket_31_60 = get_smriti_report_data("customer_outstanding", {"company": company, "ageing_bucket": "31-60"})
        self.assertTrue(len(res_cust_bucket_31_60) > 0)
        self.assertIn(si_name, [r.invoice for r in res_cust_bucket_31_60])

        res_cust_bucket_1_30 = get_smriti_report_data("customer_outstanding", {"company": company, "ageing_bucket": "1-30"})
        self.assertNotIn(si_name, [r.invoice for r in res_cust_bucket_1_30])

        # Test Supplier Outstanding report
        res_supp = get_smriti_report_data("supplier_outstanding", {"company": company})
        self.assertTrue(len(res_supp) > 0)
        match_supp = [r for r in res_supp if r.invoice == pi_name]
        self.assertEqual(len(match_supp), 1)
        self.assertEqual(match_supp[0].supplier, self.supplier_name)
        self.assertEqual(float(match_supp[0].outstanding_amount), 18000.0)
        self.assertTrue(match_supp[0].ageing_days >= 10)


        # Test Ageing bucket filter on Supplier Outstanding
        res_supp_bucket_1_30 = get_smriti_report_data("supplier_outstanding", {"company": company, "ageing_bucket": "1-30"})
        self.assertTrue(len(res_supp_bucket_1_30) > 0)
        self.assertIn(pi_name, [r.invoice for r in res_supp_bucket_1_30])

        res_supp_bucket_31_60 = get_smriti_report_data("supplier_outstanding", {"company": company, "ageing_bucket": "31-60"})
        self.assertNotIn(pi_name, [r.invoice for r in res_supp_bucket_31_60])

        # Cleanup
        frappe.db.delete("Sales Invoice", si_name)
        frappe.db.delete("Purchase Invoice", pi_name)
        frappe.db.commit()

    def test_audit_reports(self):
        """Tests that SMRITI Security Audit Log and Address Change Log reports execute successfully."""
        # 1. Insert mock Activity Log
        log1 = frappe.new_doc("Activity Log")
        log1.user = "Administrator"
        log1.operation = "Login"
        log1.subject = "Test report run audit"
        log1.insert(ignore_permissions=True)
        log1_name = log1.name
        
        # 2. Insert mock SMRITI Address Audit Log
        log2 = frappe.new_doc("SMRITI Address Audit Log")
        log2.company = self.company_name
        log2.changed_by = "Administrator"
        log2.changed_at = "2026-06-12 12:00:00"
        log2.field_name = "address_line1"
        log2.old_value = "123 Old St"
        log2.new_value = "456 New Ave"
        log2.insert(ignore_permissions=True)
        log2_name = log2.name
        
        frappe.db.commit()
        
        # 3. Query Security Audit Log
        filters = {
            "from_date": "2026-06-01",
            "to_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "user": "Administrator"
        }
        res_sec = get_smriti_report_data("security_audit_log", filters)
        self.assertTrue(len(res_sec) > 0)
        self.assertIn("creation", res_sec[0])
        self.assertIn("user", res_sec[0])
        
        # 4. Query Address Change Log
        filters2 = {
            "company": self.company_name,
            "from_date": "2026-06-01",
            "to_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "changed_by": "Administrator"
        }
        res_addr = get_smriti_report_data("address_change_log", filters2)
        self.assertTrue(len(res_addr) > 0)
        self.assertIn("changed_at", res_addr[0])
        self.assertEqual(res_addr[0]["field_name"], "address_line1")
        
        # Cleanup
        frappe.db.delete("Activity Log", log1_name)
        frappe.db.delete("SMRITI Address Audit Log", log2_name)
        frappe.db.commit()
