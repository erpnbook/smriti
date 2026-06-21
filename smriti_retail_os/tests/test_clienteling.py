# -*- coding: utf-8 -*-
#
# @file: test_clienteling.py
# @description: Automated unit test suite for SMRITI Unified Customer Graph & Clienteling.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.2.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt
from frappe import _
from smriti_retail_os.clienteling.service import clienteling_service, walk_in_service
from smriti_retail_os.clienteling.api import clienteling_api

class TestClienteling(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestClienteling, cls).setUpClass()
        
        # 1. Create a Test Customer
        cls.customer_name = "_Test Clienteling Cust"
        if not frappe.db.exists("Customer", {"customer_name": cls.customer_name}):
            cust = frappe.new_doc("Customer")
            cust.customer_name = cls.customer_name
            cust.customer_group = "Individual"
            cust.customer_type = "Individual"
            cust.insert(ignore_permissions=True)
            cls.customer = cust.name
        else:
            cls.customer = frappe.db.get_value("Customer", {"customer_name": cls.customer_name})
            
        # 2. Create a Test Store Warehouse
        cls.store = "_Test Clienteling Store"
        if not frappe.db.exists("Warehouse", {"warehouse_name": cls.store}):
            wh = frappe.new_doc("Warehouse")
            wh.warehouse_name = cls.store
            wh.is_group = 0
            wh.insert(ignore_permissions=True)
            cls.warehouse = wh.name
        else:
            cls.warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": cls.store})
            
        # 3. Create a Test Employee (Executive)
        cls.employee_name = "_Test Clienteling Executive"
        if not frappe.db.exists("Employee", {"first_name": cls.employee_name}):
            emp = frappe.new_doc("Employee")
            emp.first_name = cls.employee_name
            emp.status = "Active"
            emp.gender = "Male"
            emp.date_of_birth = "1990-01-01"
            emp.date_of_joining = "2026-01-01"
            emp.insert(ignore_permissions=True)
            cls.employee = emp.name
        else:
            cls.employee = frappe.db.get_value("Employee", {"first_name": cls.employee_name})

    def setUp(self):
        # Clear existing telemetry and logs to isolate tests
        frappe.db.delete("SMRITI Customer Graph", {"customer": self.customer})
        frappe.db.delete("SMRITI Customer Profile", {"customer": self.customer})
        frappe.db.delete("SMRITI Walk In Visit", {"store": self.warehouse})
        frappe.db.delete("SMRITI Walk In Analytics", {"store": self.warehouse})
        frappe.db.delete("SMRITI Customer Interaction", {"customer": self.customer})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-ABV", "TST-LTV"]]})
        frappe.db.commit()

    def test_materialization_invariant(self):
        """Asserts that direct database writes to Customer Graph/Profile by standard users throw PermissionError."""
        # 1. Test Profile write rejection
        profile = frappe.new_doc("SMRITI Customer Profile")
        profile.customer = self.customer
        
        # Simulate standard session (Administrator session bypassed but flags are checked)
        profile.flags.ignore_permissions = False
        frappe.set_user("Guest")
        
        try:
            self.assertRaises(frappe.PermissionError, profile.insert)
        finally:
            frappe.set_user("Administrator")

    def test_walk_in_state_machine(self):
        """Validates Walk-In Funnel state transitions and exit reason / conversion requirements."""
        # 1. Log Initial Walk-In (Registered)
        visit = walk_in_service.record_walk_in(
            store=self.warehouse,
            executive=self.employee,
            customer=self.customer,
            status="Registered"
        )
        self.assertTrue(frappe.db.exists("SMRITI Walk In Visit", visit.name))
        self.assertEqual(visit.status, "Registered")

        # 2. Transition: Registered -> Browsing
        visit = walk_in_service.update_walk_in_status(visit.name, "Browsing")
        self.assertEqual(visit.status, "Browsing")

        # 3. Transition: Browsing -> Assisted
        visit = walk_in_service.update_walk_in_status(visit.name, "Assisted")
        self.assertEqual(visit.status, "Assisted")

        # 4. Invalid Transition Exception (to Exited without reason)
        self.assertRaises(
            frappe.ValidationError,
            walk_in_service.update_walk_in_status,
            visit_id=visit.name,
            status="Exited",
            reason=None
        )

        # 5. Invalid Transition Exception (to Converted without invoice links)
        self.assertRaises(
            frappe.ValidationError,
            walk_in_service.update_walk_in_status,
            visit_id=visit.name,
            status="Converted",
            invoice_type="Sales Invoice",
            invoice_id=None
        )

        # 6. Valid Transition: Assisted -> Exited (with reason)
        visit = walk_in_service.update_walk_in_status(
            visit_id=visit.name,
            status="Exited",
            reason="Pricing"
        )
        self.assertEqual(visit.status, "Exited")
        self.assertEqual(visit.reason_for_no_purchase, "Pricing")

    def test_profile_regeneration_queue(self):
        """Verifies that invoice hooks mark the graph/profile dirty and trigger background jobs."""
        # 1. Initialize Profile records
        clienteling_service.regenerate_customer_data(self.customer)
        
        # 2. Call mark_dirty with audit trails
        clienteling_service.mark_dirty(
            customer=self.customer,
            source="Test Suite",
            source_document="TST-DOC-001"
        )
        
        # 3. Verify dirty markers are physically persisted
        graph_dirty = frappe.db.get_value("SMRITI Customer Graph", self.customer, "is_dirty")
        profile_dirty = frappe.db.get_value("SMRITI Customer Profile", self.customer, "is_dirty")
        source = frappe.db.get_value("SMRITI Customer Graph", self.customer, "dirty_source")
        doc_id = frappe.db.get_value("SMRITI Customer Graph", self.customer, "dirty_document")
        
        self.assertEqual(graph_dirty, 1)
        self.assertEqual(profile_dirty, 1)
        self.assertEqual(source, "Test Suite")
        self.assertEqual(doc_id, "TST-DOC-001")

    def test_formula_registry_fallback(self):
        """Checks that if Formula definitions are missing, the calculations fallback gracefully without crash."""
        # Ensure TST-ABV and TST-LTV are deleted
        frappe.db.delete("SMRITI Formula Definition", {"formula_name": ["in", ["Average Basket Value", "Lifetime Value"]]})
        frappe.db.commit()

        # Execute regeneration
        try:
            clienteling_service.regenerate_customer_data(self.customer)
            profile = frappe.get_doc("SMRITI Customer Profile", self.customer)
            self.assertEqual(profile.calculation_status, "Completed")
            self.assertEqual(profile.lifetime_value, 0.0)
            self.assertEqual(profile.average_basket_value, 0.0)
        except Exception as e:
            self.fail(f"Regeneration crashed during registry fallback: {str(e)}")

    def test_graph_profile_consistency(self):
        """Validates that shared calculated fields match exactly between the Graph and Profile."""
        # 1. Seed custom Formula Definitions
        for fid, fname, expr in [
            ("TST-ABV", "Average Basket Value", "net_revenue / purchases_count"),
            ("TST-LTV", "Lifetime Value", "net_revenue")
        ]:
            if not frappe.db.exists("SMRITI Formula Definition", {"formula_id": fid}):
                frappe.get_doc({
                    "doctype": "SMRITI Formula Definition",
                    "formula_id": fid,
                    "formula_name": fname,
                    "formula_version": "1.0.0",
                    "formula_category": "Sales Analytics",
                    "status": "Approved",
                    "is_active": 1,
                    "effective_date": "2026-06-19",
                    "formula_expression": expr
                }).insert(ignore_permissions=True)
        frappe.db.commit()

        # 2. Recalculate
        clienteling_service.regenerate_customer_data(self.customer)
        
        graph = frappe.get_doc("SMRITI Customer Graph", self.customer)
        profile = frappe.get_doc("SMRITI Customer Profile", self.customer)
        
        # 3. Assert values are consistent
        self.assertEqual(graph.preferred_brand, profile.preferred_brand)
        self.assertEqual(graph.preferred_category, profile.preferred_category)
        self.assertEqual(graph.preferred_size, profile.preferred_size)
        self.assertEqual(graph.preferred_color, profile.preferred_color)
        self.assertEqual(graph.last_visit_date, profile.last_visit_date)
        self.assertEqual(graph.favorite_executive, profile.favorite_executive)
        self.assertEqual(flt(graph.visit_frequency_days), flt(profile.visit_frequency_days))
        self.assertEqual(flt(graph.net_revenue), flt(profile.lifetime_value))
        
        # Clean up seeded formulas
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-ABV", "TST-LTV"]]})
        frappe.db.commit()
