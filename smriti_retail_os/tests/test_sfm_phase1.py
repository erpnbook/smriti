# -*- coding: utf-8 -*-
#
# @file: test_sfm_phase1.py
# @description: Automated test suite for SMRITI Sales Force Management (SFM) Phase 1 features.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os import smriti
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, getdate, add_days, flt
from smriti_retail_os.sfm.service.target_service import get_employee_target_vs_achievement

class TestSFMPhase1(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Seed standard Gender records if missing
        for g_name in ["Male", "Female"]:
            if not smriti.db.exists("Gender", g_name):
                g = smriti.documents.new("Gender")
                g.gender = g_name
                g.insert(ignore_permissions=True)
        # Create test company
        cls.company = "_Test SFM Company"
        if not smriti.db.exists("Company", cls.company):
            comp = smriti.documents.new("Company")
            comp.company_name = cls.company
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)

        # Ensure company is associated with active Fiscal Years
        for fy_name in smriti.db.get_list("Fiscal Year", filters={"disabled": 0}, pluck="name"):
            fy = smriti.documents.get("Fiscal Year", fy_name)
            if not any(c.company == cls.company for c in fy.companies):
                fy.append("companies", {"company": cls.company})
                fy.save(ignore_permissions=True)

        # Ensure valid GSTIN and Address on Company for compliance validation
        smriti.db.set_value("Company", cls.company, "gstin", "27AAXFT2508H1ZR")
        
        addr_name = f"{cls.company}-Registered-Test"
        if not smriti.db.exists("Address", addr_name):
            addr = smriti.documents.new("Address")
            addr.address_title = cls.company
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
            addr.append("links", {"link_doctype": "Company", "link_name": cls.company})
            addr.insert(ignore_permissions=True)
            smriti.db.commit()

        # Resolve or create basic accounts needed for Invoice submission
        cls.debit_to = smriti.db.get("Account", {"company": cls.company, "account_type": "Receivable", "is_group": 0}, "name")
        if not cls.debit_to:
            parent_recv = smriti.db.get("Account", {"company": cls.company, "account_type": "Receivable", "is_group": 1}, "name")
            acc = smriti.documents.new("Account")
            acc.account_name = "Debtors"
            acc.parent_account = parent_recv
            acc.company = cls.company
            acc.account_type = "Receivable"
            acc.insert(ignore_permissions=True)
            cls.debit_to = acc.name

        cls.income_account = smriti.db.get("Account", {"company": cls.company, "root_type": "Income", "is_group": 0}, "name")
        if not cls.income_account:
            parent_inc = smriti.db.get("Account", {"company": cls.company, "root_type": "Income", "is_group": 1}, "name")
            acc = smriti.documents.new("Account")
            acc.account_name = "Sales"
            acc.parent_account = parent_inc
            acc.company = cls.company
            acc.root_type = "Income"
            acc.insert(ignore_permissions=True)
            cls.income_account = acc.name

        # Resolve UOM and Item Group
        cls.uom = smriti.db.exists("UOM", "Nos") or smriti.db.get("UOM", {}, "name") or "Nos"
        cls.item_group = smriti.db.exists("Item Group", "All Item Groups") or smriti.db.get("Item Group", {}, "name") or "All Item Groups"

        # Resolve or create Warehouse
        cls.warehouse = smriti.db.get("Warehouse", {"company": cls.company, "is_group": 0}, "name")
        if not cls.warehouse:
            w = smriti.documents.new("Warehouse")
            w.warehouse_name = "Test SFM Stores"
            w.company = cls.company
            w.is_group = 0
            w.insert(ignore_permissions=True)
            cls.warehouse = w.name

        # Create test item brand
        cls.brand = "Raymond Test Brand"
        if not smriti.db.exists("Brand", cls.brand):
            b = smriti.documents.new("Brand")
            b.brand = cls.brand
            b.insert(ignore_permissions=True)

        if not smriti.db.exists("GST HSN Code", "649211"):
            hsn = smriti.documents.new("GST HSN Code")
            hsn.hsn_code = "649211"
            hsn.insert(ignore_permissions=True)

        # Create test item
        cls.item = "TEST-SFM-ITEM-01"
        if not smriti.db.exists("Item", cls.item):
            itm = smriti.documents.new("Item")
            itm.item_code = cls.item
            itm.item_name = "Test SFM Item"
            itm.item_group = cls.item_group
            itm.brand = cls.brand
            itm.stock_uom = cls.uom
            itm.gst_hsn_code = "649211"
            itm.insert(ignore_permissions=True)

        # Create test customer
        cls.customer = "Test Customer SFM"
        if not smriti.db.exists("Customer", cls.customer):
            cust = smriti.documents.new("Customer")
            cust.customer_name = cls.customer
            cust.customer_group = "Individual"
            cust.territory = "All Territories"
            cust.insert(ignore_permissions=True)

        # Create test employees
        cls.emp_p = "EMP-SFM-PRIMARY"
        if not smriti.db.exists("Employee", cls.emp_p):
            e = smriti.documents.new("Employee")
            e.employee_name = "Rahul Primary Owner"
            e.first_name = "Rahul"
            e.company = cls.company
            e.gender = "Male"
            e.status = "Active"
            e.date_of_joining = "2026-01-01"
            e.date_of_birth = "1990-01-01"
            e.insert(ignore_permissions=True)
            # Store ID in DB matching name
            smriti.db.set_value("Employee", e.name, "name", cls.emp_p)

        cls.emp_s = "EMP-SFM-SECONDARY"
        if not smriti.db.exists("Employee", cls.emp_s):
            e = smriti.documents.new("Employee")
            e.employee_name = "Sonia Secondary Owner"
            e.first_name = "Sonia"
            e.company = cls.company
            e.gender = "Female"
            e.status = "Active"
            e.date_of_joining = "2026-01-01"
            e.date_of_birth = "1990-01-01"
            e.insert(ignore_permissions=True)
            smriti.db.set_value("Employee", e.name, "name", cls.emp_s)

        cls.emp_w = "EMP-SFM-WALKIN"
        if not smriti.db.exists("Employee", cls.emp_w):
            e = smriti.documents.new("Employee")
            e.employee_name = "Walkin Fallback Staff"
            e.first_name = "Walkin"
            e.company = cls.company
            e.gender = "Male"
            e.status = "Active"
            e.date_of_joining = "2026-01-01"
            e.date_of_birth = "1990-01-01"
            e.insert(ignore_permissions=True)
            smriti.db.set_value("Employee", e.name, "name", cls.emp_w)

        # Create test SMRITI Store
        cls.store = "Store - Test SFM"
        if not smriti.db.exists("SMRITI Store", cls.store):
            s = smriti.documents.new("SMRITI Store")
            s.store_name = cls.store
            s.default_warehouse = cls.warehouse
            s.company = cls.company
            s.insert(ignore_permissions=True)
            cls.store = s.name

        smriti.db.commit()

    def setUp(self):
        super().setUp()
        frappe.flags.in_test = True
        frappe.session.user = "Administrator"

        # Clear transactions and ledgers
        smriti.db.delete("SMRITI Customer Ownership")
        smriti.db.delete("SMRITI Sales Target")
        smriti.db.delete("SMRITI Attribution Ledger")
        smriti.db.delete("SMRITI Attribution Event")
        smriti.db.delete("SMRITI Sales KPI Snapshot")

        # Clean up Sales Invoices
        invoice_names = smriti.db.get_list("Sales Invoice", filters={"company": self.company}, pluck="name")
        if invoice_names:
            smriti.db.delete("Sales Invoice Item", {"parent": ["in", invoice_names]})
            smriti.db.delete("Sales Invoice", {"name": ["in", invoice_names]})

        # Initialize Settings
        smriti.db.set_value("SMRITI SFM Settings", "SMRITI SFM Settings", {
            "enable_sfm": 1,
            "ownership_precedence": 1,
            "primary_split_pct": 70.0,
            "secondary_split_pct": 30.0,
            "walkin_employee": self.emp_w
        }, update_modified=False)

        frappe.clear_cache()
        smriti.db.commit()

    def tearDown(self):
        frappe.flags.in_test = False
        super().tearDown()

    def test_settings_split_validation(self):
        """Test split percentages must sum to exactly 100."""
        frappe.clear_cache()
        if hasattr(frappe.local, "document_cache"):
            frappe.local.document_cache.clear()
        settings = smriti.documents.get_single("SFMSettings")
        settings.primary_split_pct = 60.0
        settings.secondary_split_pct = 30.0 # Total 90%
        
        with self.assertRaises(frappe.ValidationError) as context:
            settings.save()
        self.assertIn("must sum to exactly 100", str(context.exception))

        frappe.clear_cache()
        if hasattr(frappe.local, "document_cache"):
            frappe.local.document_cache.clear()
        settings = smriti.documents.get_single("SFMSettings")
        settings.primary_split_pct = 70.0
        settings.secondary_split_pct = 30.0 # Total 100%
        settings.save() # Should pass

    def test_customer_ownership_timeline_validation(self):
        """Test timeline deactivation on active customer ownership creation."""
        # 1. Create original owner assignment starting 2026-06-01
        own1 = smriti.documents.new("SMRITI Customer Ownership")
        own1.customer = self.customer
        own1.primary_owner = self.emp_p
        own1.start_date = "2026-06-01"
        own1.company = self.company
        own1.is_active = 1
        own1.insert(ignore_permissions=True)
        
        # Verify active and end_date is null
        self.assertEqual(own1.is_active, 1)
        self.assertIsNone(own1.end_date)

        # 2. Create new owner assignment starting 2026-06-10
        own2 = smriti.documents.new("SMRITI Customer Ownership")
        own2.customer = self.customer
        own2.primary_owner = self.emp_w
        own2.start_date = "2026-06-10"
        own2.company = self.company
        own2.is_active = 1
        own2.insert(ignore_permissions=True)

        # 3. Reload original record and verify it is closed out with end_date = yesterday
        own1.reload()
        self.assertEqual(own1.is_active, 0)
        self.assertEqual(str(own1.end_date), "2026-06-09")

    def test_settings_precedence_and_split(self):
        """Test revenue split credits are resolved correctly based on customer ownership precedence."""
        # Assign customer owners
        own = smriti.documents.new("SMRITI Customer Ownership")
        own.customer = self.customer
        own.primary_owner = self.emp_p
        own.secondary_owner = self.emp_s
        own.start_date = "2026-06-01"
        own.company = self.company
        own.is_active = 1
        own.insert(ignore_permissions=True)

        # Submit Sales Invoice for this customer
        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-02"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 1000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Query Ledger Entries
        ledgers = smriti.db.get_list(
            "SMRITI Attribution Ledger",
            filters={"invoice_reference": si.name},
            fields=["employee", "credit_percentage", "revenue_credit", "ownership_type", "store", "ownership_record"]
        )

        # We expect 2 entries matching 70/30 split
        self.assertEqual(len(ledgers), 2)
        
        primary_match = [l for l in ledgers if l.employee == self.emp_p][0]
        self.assertEqual(flt(primary_match.credit_percentage), 70.0)
        self.assertEqual(flt(primary_match.revenue_credit), 700.0)
        self.assertEqual(primary_match.ownership_type, "Primary")
        self.assertEqual(primary_match.store, self.store)
        self.assertEqual(str(primary_match.ownership_record), str(own.name)) # SFM-ENH-001 reference check

        secondary_match = [l for l in ledgers if l.employee == self.emp_s][0]
        self.assertEqual(flt(secondary_match.credit_percentage), 30.0)
        self.assertEqual(flt(secondary_match.revenue_credit), 300.0)
        self.assertEqual(secondary_match.ownership_type, "Secondary")
        self.assertEqual(str(secondary_match.ownership_record), str(own.name))

    def test_walk_in_fallback(self):
        """Test walk-in employee fallback when no customer ownership matches."""
        # Submit Sales Invoice (no customer ownership defined)
        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-02"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 2000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Query Ledger Entries
        ledgers = smriti.db.get_list(
            "SMRITI Attribution Ledger",
            filters={"invoice_reference": si.name},
            fields=["employee", "credit_percentage", "revenue_credit", "ownership_type"]
        )

        # Expect 1 Walk-In fallback ledger entry at 100%
        self.assertEqual(len(ledgers), 1)
        self.assertEqual(ledgers[0].employee, self.emp_w)
        self.assertEqual(flt(ledgers[0].credit_percentage), 100.0)
        self.assertEqual(flt(ledgers[0].revenue_credit), 2000.0)
        self.assertEqual(ledgers[0].ownership_type, "Walk-In")

    def test_ledger_reversal_on_invoice_cancel(self):
        """Test ledger reversal entry generation when invoice is cancelled."""
        si = smriti.documents.new("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.posting_date = "2026-06-02"
        si.posting_time = "10:00:00"
        si.set_posting_time = 1
        si.debit_to = self.debit_to
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 1000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Cancel Sales Invoice
        si.cancel()

        # Query Ledger entries (including status)
        ledgers = smriti.db.get_list(
            "SMRITI Attribution Ledger",
            filters={"invoice_reference": si.name},
            fields=["name", "employee", "revenue_credit", "ledger_status", "reversal_reference"]
        )

        # Expecting 2 entries: 1 original Walk-In (Reversed) and 1 negative Reversal (Reversed)
        self.assertEqual(len(ledgers), 2)
        
        orig = [l for l in ledgers if l.revenue_credit > 0][0]
        self.assertEqual(orig.ledger_status, "Reversed")
        self.assertTrue(orig.reversal_reference)

        rev = [l for l in ledgers if l.revenue_credit < 0][0]
        self.assertEqual(rev.ledger_status, "Reversed")
        self.assertEqual(str(rev.reversal_reference), str(orig.name))
        self.assertEqual(flt(rev.revenue_credit), -1000.0)

    def test_kpi_snapshot_generation(self):
        """Test daily KPI snapshots are updated and target achievements compute properly."""
        # 1. Create a Target of 100,000 for Rahul Primary Employee in June 2026
        # Resolve fiscal year
        fiscal_year = smriti.db.get_list("Fiscal Year", limit=1, pluck="name")[0]
        
        target = smriti.documents.new("SMRITI Sales Target")
        target.employee = self.emp_p
        target.company = self.company
        target.fiscal_year = fiscal_year
        target.month = "Jun"
        target.target_amount = 100000.0
        target.insert(ignore_permissions=True)

        # 2. Add Customer Ownership assignment
        own = smriti.documents.new("SMRITI Customer Ownership")
        own.customer = self.customer
        own.primary_owner = self.emp_p
        own.start_date = "2026-06-01"
        own.company = self.company
        own.is_active = 1
        own.insert(ignore_permissions=True)

        # 3. Submit Invoice 1 (Revenue = 5,000)
        si1 = smriti.documents.new("Sales Invoice")
        si1.company = self.company
        si1.customer = self.customer
        si1.posting_date = "2026-06-05"
        si1.posting_time = "10:00:00"
        si1.set_posting_time = 1
        si1.debit_to = self.debit_to
        si1.currency = "INR"
        si1.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 5000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si1.insert(ignore_permissions=True)
        si1.submit()

        # Debug printing before assertion
        print("ALL LEDGERS IN TEST:", smriti.db.get_list("SMRITI Attribution Ledger", fields=["name", "employee", "posting_date", "revenue_credit"]))
        print("ALL SNAPSHOTS IN TEST:", smriti.db.get_list("SMRITI Sales KPI Snapshot", fields=["name", "employee", "date", "revenue"]))
        print("ALL EVENTS IN TEST:", smriti.db.get_list("SMRITI Attribution Event", fields=["invoice_reference", "status", "error_message"]))

        # Verify daily snapshot for Jun 5, 2026
        snapshot = smriti.documents.get("SMRITI Sales KPI Snapshot", {"employee": self.emp_p, "date": "2026-06-05"})
        self.assertEqual(flt(snapshot.revenue), 5000.0)
        self.assertEqual(snapshot.transactions, 1)
        self.assertEqual(snapshot.customers, 1)

        # 4. Submit Invoice 2 (Revenue = 3,000)
        si2 = smriti.documents.new("Sales Invoice")
        si2.company = self.company
        si2.customer = self.customer
        si2.posting_date = "2026-06-05"
        si2.posting_time = "11:00:00"
        si2.set_posting_time = 1
        si2.debit_to = self.debit_to
        si2.currency = "INR"
        si2.append("items", {
            "item_code": self.item,
            "qty": 1.0,
            "rate": 3000.0,
            "income_account": self.income_account,
            "warehouse": self.warehouse
        })
        si2.insert(ignore_permissions=True)
        si2.submit()

        # Verify daily snapshot has aggregated both transactions
        frappe.clear_cache()
        if hasattr(frappe.local, "document_cache"):
            frappe.local.document_cache.clear()
        snapshot = smriti.documents.get("SMRITI Sales KPI Snapshot", snapshot.name)
        self.assertEqual(flt(snapshot.revenue), 8000.0)
        self.assertEqual(snapshot.transactions, 2)
        self.assertEqual(snapshot.customers, 1) # Same customer, so unique count remains 1

        # 5. Cancel Invoice 2
        si2.cancel()
        
        # Verify daily snapshot after cancellation
        frappe.clear_cache()
        if hasattr(frappe.local, "document_cache"):
            frappe.local.document_cache.clear()
        snapshot = smriti.documents.get("SMRITI Sales KPI Snapshot", snapshot.name)
        self.assertEqual(flt(snapshot.revenue), 5000.0)
        self.assertEqual(snapshot.transactions, 1)

        # 6. Test target vs achievement service logic
        perf = get_employee_target_vs_achievement(self.emp_p, fiscal_year, "Jun", self.company)
        self.assertEqual(flt(perf["target_amount"]), 100000.0)
        self.assertEqual(flt(perf["achievement_amount"]), 5000.0)
        self.assertEqual(flt(perf["achievement_percentage"]), 5.0)
