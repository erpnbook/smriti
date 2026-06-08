# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_psv.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days, today
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances
from smriti_retail_os.psv_service import import_opening_balances
from smriti_retail_os.ledger_engine import make_ledger_entry

class TestPSV(FrappeTestCase):
    def setUp(self):
        # 1. Resolve or Create basic link dependencies
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

        # 2. Create a mock company if missing
        self.company = "Test PSV Company"
        if not frappe.db.exists("Company", self.company):
            comp = frappe.new_doc("Company")
            comp.company_name = self.company
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)

        # Ensure valid GSTIN and Registered Address on Company for India Compliance
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

        # Create valid GST HSN Code record for India Compliance
        self.hsn_code = frappe.db.exists("GST HSN Code", "998311") or frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "998311"
            hsn.description = "Test Services"
            hsn.insert(ignore_permissions=True)
            self.hsn_code = hsn.name

        # Resolve standard selling price list
        if not frappe.db.exists("Price List", "Standard Selling"):
            pl = frappe.new_doc("Price List")
            pl.price_list_name = "Standard Selling"
            pl.enabled = 1
            pl.selling = 1
            pl.buying = 0
            pl.currency = "INR"
            pl.insert(ignore_permissions=True)

        # Ensure active Fiscal Year exists
        fy_name = "2026-2027"
        if not frappe.db.exists("Fiscal Year", fy_name):
            fy = frappe.new_doc("Fiscal Year")
            fy.year = fy_name
            fy.year_start_date = "2026-04-01"
            fy.year_end_date = "2027-03-31"
            fy.append("companies", {"company": self.company})
            fy.insert(ignore_permissions=True)
        else:
            fy = frappe.get_doc("Fiscal Year", fy_name)
            if not any(c.company == self.company for c in fy.companies):
                fy.append("companies", {"company": self.company})
                fy.save(ignore_permissions=True)

        # Resolve or create Cost Center
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
            cc.cost_center_name = "Test PSV Cost Center"
            cc.company = self.company
            cc.is_group = 0
            cc.parent_cost_center = parent_cc
            cc.insert(ignore_permissions=True)
            self.cost_center = cc.name

        # Resolve or create Income Account
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
            acc.account_name = "Sales - TEST"
            acc.company = self.company
            acc.root_type = "Income"
            acc.account_type = "Income Account"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.income_account = acc.name

        comp_doc = frappe.get_doc("Company", self.company)
        if not comp_doc.round_off_cost_center:
            comp_doc.round_off_cost_center = self.cost_center
        if not comp_doc.round_off_account:
            comp_doc.round_off_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Round Off"}, "name") or self.income_account
        comp_doc.save(ignore_permissions=True)

        # 3. Create a mock customer if missing
        self.customer = "Test PSV Customer"
        if not frappe.db.exists("Customer", self.customer):
            cust = frappe.new_doc("Customer")
            cust.customer_name = self.customer
            cust.customer_type = "Individual"
            cust.insert(ignore_permissions=True)

        # 4. Create a mock item if missing
        self.item = "TEST-PSV-ITEM"
        if not frappe.db.exists("Item", self.item):
            itm = frappe.new_doc("Item")
            itm.item_code = self.item
            itm.item_name = "Test PSV Item"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.insert(ignore_permissions=True)

        # 5. Create a Party Stock Account
        self.account_name = f"{self.customer}-Mumbai Outlet"
        if not frappe.db.exists("SMRITI Party Stock Account", self.account_name):
            acc = frappe.new_doc("SMRITI Party Stock Account")
            acc.company = self.company
            acc.customer = self.customer
            acc.location_name = "Mumbai Outlet"
            acc.insert(ignore_permissions=True)

    def tearDown(self):
        # Clean up created database records to prevent pollution
        frappe.db.rollback()

    def test_opening_balance(self):
        # 1. Import opening balances
        items_data = [{"item_code": self.item, "qty": 500.0}]
        import_opening_balances(self.company, self.account_name, items_data)

        # 2. Assert balance is 500
        bal = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal, 500.0)

    def test_sales_invoice_hooks(self):
        # 1. Create a standard Sales Invoice referencing custom_party_stock_account
        si = frappe.new_doc("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.custom_party_stock_account = self.account_name
        si.selling_price_list = "Standard Selling"
        si.price_list_currency = "INR"
        si.plc_conversion_rate = 1.0
        si.conversion_rate = 1.0
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 100.0,
            "rate": 10.0,
            "income_account": self.income_account,
            "cost_center": self.cost_center
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # 2. Assert positive ledger entry written (+100)
        bal = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal, 100.0)

        # 3. Cancel Sales Invoice
        si.cancel()

        # 4. Assert reversing entry written (balance becomes 0)
        bal_after_cancel = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal_after_cancel, 0.0)

    def test_sales_invoice_cancellation_exception(self):
        # 1. Dispatch 100 units via invoice submit
        si = frappe.new_doc("Sales Invoice")
        si.company = self.company
        si.customer = self.customer
        si.custom_party_stock_account = self.account_name
        si.selling_price_list = "Standard Selling"
        si.price_list_currency = "INR"
        si.plc_conversion_rate = 1.0
        si.conversion_rate = 1.0
        si.currency = "INR"
        si.append("items", {
            "item_code": self.item,
            "qty": 100.0,
            "rate": 10.0,
            "income_account": self.income_account,
            "cost_center": self.cost_center
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # 2. Record weekly sales upload for 100 units (balance drops to 0)
        upload = frappe.new_doc("SMRITI Party Sales Upload")
        upload.company = self.company
        upload.party_stock_account = self.account_name
        upload.period_start_date = today()
        upload.period_end_date = add_days(today(), 6)
        upload.file_hash = "mock_hash_for_test"
        upload.append("items", {
            "date": today(),
            "item_code": self.item,
            "qty_sold": 100.0
        })
        upload.insert(ignore_permissions=True)
        upload.submit()

        # Balance at location is now 0.0
        self.assertEqual(get_party_balance(self.account_name, self.item), 0.0)

        # 3. Cancel the original Sales Invoice (tries to remove 100 units from location, causing balance to drop to -100)
        si.cancel()

        # 4. Assert cancellation succeeds, but an Exception Record is created
        ex_rec = frappe.db.exists("SMRITI PSV Exception Record", {
            "party_stock_account": self.account_name,
            "sales_invoice": si.name,
            "item_code": self.item,
            "status": "Pending Reconciliation"
        })
        self.assertTrue(ex_rec)

        # Assert location status is set to Pending Reconciliation
        loc_status = frappe.db.get_value("SMRITI Party Stock Account", self.account_name, "status")
        self.assertEqual(loc_status, "Pending Reconciliation")

    def test_sales_upload_validations(self):
        # 1. Seeding 50 units
        items_data = [{"item_code": self.item, "qty": 50.0}]
        import_opening_balances(self.company, self.account_name, items_data)

        # 2. Attempt to upload sales of 100 units (overselling) -> should throw ValidationError
        upload = frappe.new_doc("SMRITI Party Sales Upload")
        upload.company = self.company
        upload.party_stock_account = self.account_name
        upload.period_start_date = today()
        upload.period_end_date = add_days(today(), 6)
        upload.file_hash = "hash_1"
        upload.append("items", {
            "date": today(),
            "item_code": self.item,
            "qty_sold": 100.0
        })
        self.assertRaises(frappe.ValidationError, upload.insert, ignore_permissions=True)

        # 3. Period Overlap Check:
        # Insert a valid upload for Week 1
        u1 = frappe.new_doc("SMRITI Party Sales Upload")
        u1.company = self.company
        u1.party_stock_account = self.account_name
        u1.period_start_date = today()
        u1.period_end_date = add_days(today(), 6)
        u1.file_hash = "hash_u1"
        u1.append("items", {
            "date": today(),
            "item_code": self.item,
            "qty_sold": 10.0
        })
        u1.insert(ignore_permissions=True)
        u1.submit()

        # Attempt to insert overlapping period upload -> should throw ValidationError
        u2 = frappe.new_doc("SMRITI Party Sales Upload")
        u2.company = self.company
        u2.party_stock_account = self.account_name
        u2.period_start_date = add_days(today(), 3)
        u2.period_end_date = add_days(today(), 9)
        u2.file_hash = "hash_u2"
        u2.append("items", {
            "date": today(),
            "item_code": self.item,
            "qty_sold": 10.0
        })
        self.assertRaises(frappe.ValidationError, u2.insert, ignore_permissions=True)

    def test_physical_snapshot_adjustments(self):
        # 1. Seeding 100 units
        items_data = [{"item_code": self.item, "qty": 100.0}]
        import_opening_balances(self.company, self.account_name, items_data)

        # 2. Create snapshot with physical count 90 (system count is 100, variance is -10)
        snap = frappe.new_doc("SMRITI Party Physical Snapshot")
        snap.company = self.company
        snap.party_stock_account = self.account_name
        snap.audit_date = today()
        snap.append("items", {
            "item_code": self.item,
            "physical_qty": 90.0,
            "variance_reason": "Theft"
        })
        snap.insert(ignore_permissions=True)

        # Submit without approval must fail
        self.assertRaises(frappe.ValidationError, snap.submit)

        # Approve and submit
        snap = frappe.get_doc("SMRITI Party Physical Snapshot", snap.name)
        snap.status = "Approved"
        snap.save()
        snap.submit()

        # Balance must now reconcile to 90.0
        bal = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal, 90.0)

    def test_scale_query_count(self):
        # 1. Bulk insert 10,000 ledger entries for 100 locations and 500 SKUs
        # Fast direct DB SQL insert to prevent timeout, specifying the mandatory primary key 'name'
        import uuid
        records = []
        for i in range(10000):
            loc = f"Loc-{i % 100}"
            item = f"Item-{i % 500}"
            name = f"LE-{uuid.uuid4().hex[:10]}-{i}"
            unique_hash = f"hash-{uuid.uuid4().hex}"
            records.append((
                name,
                self.company,
                now_datetime(),
                loc,
                item,
                10.0,
                "Dispatch",
                "MOCK-VOUCHER",
                unique_hash
            ))
            
        # Group insert in SQL
        frappe.db.sql("""
            INSERT INTO `tabSMRITI Party Stock Ledger Entry` 
            (name, company, posting_datetime, party_stock_account, item_code, qty, voucher_type, voucher_no, unique_hash)
            VALUES """ + ", ".join(["(%s, %s, %s, %s, %s, %s, %s, %s, %s)"] * 10000), 
            [val for rec in records for val in rec]
        )

        sku_list = [f"Item-{i}" for i in range(500)]
        
        # 2. Assert bulk balance query runs in exactly 1 query (eliminating N+1 query regression)
        queries = []
        original_execute_query = frappe.db.execute_query
        
        def mock_execute_query(query, values=None):
            queries.append((query, values))
            return original_execute_query(query, values)
            
        frappe.db.execute_query = mock_execute_query
        try:
            balances = get_bulk_party_balances("Loc-0", sku_list)
        finally:
            frappe.db.execute_query = original_execute_query
        
        self.assertEqual(len(queries), 1)
        self.assertEqual(balances.get("Item-0"), 200.0)

    def test_concurrency_ledger_entries(self):
        # 1. Create a ledger entry
        posting_dt = now_datetime()
        ple = make_ledger_entry(
            self.company, posting_dt, self.account_name, self.item, 10.0, "Dispatch", "VOUCHER-CONC"
        )
        self.assertIsNotNone(ple)

        # 2. Assert application-level duplicate check blocks it (returns None)
        ple_dup = make_ledger_entry(
            self.company, posting_dt, self.account_name, self.item, 10.0, "Dispatch", "VOUCHER-CONC"
        )
        self.assertIsNone(ple_dup)

        # 3. Assert database-level unique constraint is present and enforces integrity
        hash_val = ple.unique_hash
        
        db_error_raised = False
        try:
            frappe.db.sql("""
                INSERT INTO `tabSMRITI Party Stock Ledger Entry`
                (name, company, posting_datetime, party_stock_account, item_code, qty, voucher_type, voucher_no, unique_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                "duplicate-name", self.company, posting_dt, self.account_name, self.item, 10.0, "Dispatch", "VOUCHER-CONC", hash_val
            ))
        except Exception as e:
            db_error_raised = True
            err_str = str(e)
            self.assertTrue("Duplicate entry" in err_str or "1062" in err_str or "IntegrityError" in e.__class__.__name__ or "IntegrityError" in str(type(e)))
            
        self.assertTrue(db_error_raised)

    def test_migration_schema_integrity(self):
        # Verify all core tables and database schema components exist
        doctypes = [
            "SMRITI Party Stock Account",
            "SMRITI Party Stock Ledger Entry",
            "SMRITI Party Sales Upload",
            "SMRITI Party Sales Item",
            "SMRITI Party Physical Snapshot",
            "SMRITI Party Physical Item",
            "SMRITI PSV Settings",
            "SMRITI PSV Activity Log",
            "SMRITI PSV Exception Record"
        ]
        for dt in doctypes:
            if dt == "SMRITI PSV Settings":
                self.assertTrue(frappe.db.exists("DocType", dt))
            else:
                self.assertTrue(frappe.db.table_exists(dt))
            
        # Verify unique index on unique_hash field in ledger table
        indices = frappe.db.sql("SHOW INDEX FROM `tabSMRITI Party Stock Ledger Entry` WHERE Key_name = 'unique_hash'")
        self.assertTrue(len(indices) > 0 or frappe.db.exists("DocField", {"parent": "SMRITI Party Stock Ledger Entry", "fieldname": "unique_hash", "unique": 1}))

    def test_health_check_alerting(self):
        from smriti_retail_os.psv_service import run_psv_daily_health_check
        
        # Clean existing health alerts
        frappe.db.delete("SMRITI PSV Exception Record")
        frappe.db.commit()
        
        # 1. Run health check on clean state -> Should log late upload and never audited alerts
        run_psv_daily_health_check()
        
        late_upload_alert = frappe.db.get_value("SMRITI PSV Exception Record", {
            "party_stock_account": self.account_name,
            "alert_type": "Late Upload"
        }, ["name", "severity", "status", "last_seen"], as_dict=True)
        self.assertIsNotNone(late_upload_alert)
        self.assertEqual(late_upload_alert.severity, "Warning")
        self.assertEqual(late_upload_alert.status, "Pending Reconciliation")
        
        # 2. Run again -> verify alert suppression updates last_seen but doesn't duplicate
        last_seen_before = late_upload_alert.last_seen
        from frappe.utils import add_to_date
        frappe.db.set_value("SMRITI PSV Exception Record", late_upload_alert.name, "last_seen", add_to_date(last_seen_before, minutes=-5))
        
        run_psv_daily_health_check()
        
        # Open alerts count remains 2 (Late Upload, Never Audited)
        self.assertEqual(frappe.db.count("SMRITI PSV Exception Record", {"party_stock_account": self.account_name, "status": "Pending Reconciliation"}), 2)
        
        last_seen_after = frappe.db.get_value("SMRITI PSV Exception Record", late_upload_alert.name, "last_seen")
        self.assertNotEqual(last_seen_before, last_seen_after)

        # 3. Trigger Critical Negative Balance
        make_ledger_entry(self.company, now_datetime(), self.account_name, self.item, -50.0, "Dispatch", "VOUCHER-NEG")
        
        run_psv_daily_health_check()
        
        neg_alert = frappe.db.get_value("SMRITI PSV Exception Record", {
            "party_stock_account": self.account_name,
            "alert_type": "Negative Balance"
        }, ["name", "severity", "status"], as_dict=True)
        self.assertIsNotNone(neg_alert)
        self.assertEqual(neg_alert.severity, "Critical")
        
        # Verify location status is set to Pending Reconciliation
        loc_status = frappe.db.get_value("SMRITI Party Stock Account", self.account_name, "status")
        self.assertEqual(loc_status, "Pending Reconciliation")

        # 4. Resolve the negative balance
        import_opening_balances(self.company, self.account_name, [{"item_code": self.item, "qty": 100.0}])
        run_psv_daily_health_check()
        
        neg_alert_status = frappe.db.get_value("SMRITI PSV Exception Record", neg_alert.name, "status")
        self.assertEqual(neg_alert_status, "Reconciled")
