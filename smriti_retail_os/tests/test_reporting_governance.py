# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_reporting_governance.py
# @description: Unit tests for SMRITI reporting engine governance rules (KGF & Rule 13).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
from smriti_retail_os.reports_api import SMRITIReportEngine

class TestReportingGovernance(unittest.TestCase):
    def setUp(self):
        # We will create temporary test terms and templates
        self.cleanup_records()
        self.create_test_records()

    def tearDown(self):
        self.cleanup_records()

    def cleanup_records(self):
        # Clean up test business terms
        test_terms = ["tst_dim_approved", "tst_meas_approved", "tst_meas_no_agg", "tst_term_deprecated", "tst_term_blocked", "tst_term_unapproved"]
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", test_terms]})
        frappe.db.delete("SMRITI Business Term", {"dictionary_key": ["in", test_terms]})
        
        # Clean up test formulas
        test_formulas = ["TST-FRM-001", "TST-FRM-002", "TST-FRM-003"]
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", test_formulas]})
        
        # Clean up test report template
        frappe.db.delete("SMRITI Report Template", {"name": "tst_gov_report"})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": "tst_gov_report"})
        
        # Clean up test users
        frappe.db.delete("User", {"email": ["in", ["user_a@example.com", "user_b@example.com", "test_user@example.com"]]})
        
        frappe.db.commit()

        # Clean up dynamic report config
        from smriti_retail_os.reports_api import REPORT_QUERIES
        if "tst_gov_report" in REPORT_QUERIES:
            del REPORT_QUERIES["tst_gov_report"]

    def create_test_records(self):
        # Create test users to satisfy link validation
        for email, name in [("user_a@example.com", "User A"), ("user_b@example.com", "User B"), ("test_user@example.com", "Test User")]:
            if not frappe.db.exists("User", email):
                frappe.get_doc({
                    "doctype": "User",
                    "email": email,
                    "first_name": name,
                    "send_welcome_email": 0
                }).insert(ignore_permissions=True)

        # Register dynamic report config
        from smriti_retail_os.reports_api import REPORT_QUERIES
        REPORT_QUERIES["tst_gov_report"] = {
            "base_sql": "SELECT parent.posting_date, parent.grand_total FROM `tabPOS Invoice` parent WHERE parent.docstatus = 1",
            "group_by": None,
            "order_by": "parent.posting_date DESC"
        }

        # 1. Create active, approved formulas
        self.f_approved = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-FRM-001",
            "formula_name": "Approved Formula",
            "formula_category": "Inventory",
            "formula_version": "1.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-20",
            "formula_meaning": "Formula meaning",
            "display_formula": "A + B",
            "formula_expression": "A + B",
            "formula_language": "documentation"
        }).insert(ignore_permissions=True)

        self.f_unapproved = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-FRM-002",
            "formula_name": "Draft Formula",
            "formula_category": "Inventory",
            "formula_version": "1.0",
            "status": "Draft",
            "is_active": 0,
            "effective_date": "2026-06-20",
            "formula_meaning": "Formula meaning",
            "display_formula": "A + B",
            "formula_expression": "A + B",
            "formula_language": "documentation"
        }).insert(ignore_permissions=True)

        self.f_inactive = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-FRM-003",
            "formula_name": "Inactive Formula",
            "formula_category": "Inventory",
            "formula_version": "1.0",
            "status": "Approved",
            "is_active": 0,
            "effective_date": "2026-06-20",
            "formula_meaning": "Formula meaning",
            "display_formula": "A + B",
            "formula_expression": "A + B",
            "formula_language": "documentation"
        }).insert(ignore_permissions=True)

        # 2. Create business terms
        # A. Dimension (Approved)
        self.t_dim_approved = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_dim_approved",
            "term_name": "Test Dimension Approved",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Approved",
            "approval_status": "Approved",
            "is_active": 1,
            "is_reportable": 1,
            "measure_or_dimension": "Dimension",
            "dictionary_key": "tst_dim_approved",
            "projection_path": "POS Invoice.posting_date",
            "entity_type": "POS Invoice",
            "data_type": "Date",
            "effective_date": "2026-06-20",
            "definition": "Approved test dimension.",
            "hinglish_definition": "Approved test dimension Hinglish."
        }).insert(ignore_permissions=True)

        # B. Measure (Approved with Sum aggregation)
        self.t_meas_approved = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_meas_approved",
            "term_name": "Test Measure Approved",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Approved",
            "approval_status": "Approved",
            "is_active": 1,
            "is_reportable": 1,
            "measure_or_dimension": "Measure",
            "default_aggregation": "Sum",
            "dictionary_key": "tst_meas_approved",
            "projection_path": "POS Invoice.grand_total",
            "entity_type": "POS Invoice",
            "data_type": "Currency",
            "related_formulas": [{"doctype": "SMRITI Related Formula", "formula_id": self.f_approved.name}],
            "effective_date": "2026-06-20",
            "definition": "Approved test measure.",
            "hinglish_definition": "Approved test measure Hinglish."
        }).insert(ignore_permissions=True)

        # C. Measure with no aggregation (invalid for reports)
        self.t_meas_no_agg = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_meas_no_agg",
            "term_name": "Test Measure No Aggregation",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Approved",
            "approval_status": "Approved",
            "is_active": 1,
            "is_reportable": 1,
            "measure_or_dimension": "Measure",
            "default_aggregation": "None",
            "dictionary_key": "tst_meas_no_agg",
            "projection_path": "POS Invoice.discount_amount",
            "entity_type": "POS Invoice",
            "data_type": "Currency",
            "effective_date": "2026-06-20",
            "definition": "No agg test measure.",
            "hinglish_definition": "No agg test measure Hinglish."
        }).insert(ignore_permissions=True)

        # D. Deprecated Term
        self.t_term_deprecated = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_term_deprecated",
            "term_name": "Test Term Deprecated",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Deprecated",
            "approval_status": "Deprecated",
            "is_active": 0,
            "is_reportable": 1,
            "measure_or_dimension": "Dimension",
            "dictionary_key": "tst_term_deprecated",
            "projection_path": "POS Invoice.discount_amount",
            "entity_type": "POS Invoice",
            "data_type": "Currency",
            "effective_date": "2026-06-20",
            "definition": "Deprecated test term.",
            "hinglish_definition": "Deprecated test term Hinglish."
        }).insert(ignore_permissions=True)

        # E. Blocked Term
        self.t_term_blocked = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_term_blocked",
            "term_name": "Test Term Blocked",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Deprecated",
            "approval_status": "Blocked",
            "is_active": 0,
            "is_reportable": 1,
            "measure_or_dimension": "Dimension",
            "dictionary_key": "tst_term_blocked",
            "projection_path": "POS Invoice.discount_amount",
            "entity_type": "POS Invoice",
            "data_type": "Currency",
            "effective_date": "2026-06-20",
            "definition": "Blocked test term.",
            "hinglish_definition": "Blocked test term Hinglish."
        }).insert(ignore_permissions=True)

        # F. Unapproved Term (Draft)
        self.t_term_unapproved = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_term_unapproved",
            "term_name": "Test Term Unapproved",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Draft",
            "approval_status": "Draft",
            "is_active": 0,
            "is_reportable": 1,
            "measure_or_dimension": "Dimension",
            "dictionary_key": "tst_term_unapproved",
            "projection_path": "POS Invoice.discount_amount",
            "entity_type": "POS Invoice",
            "data_type": "Currency",
            "effective_date": "2026-06-20",
            "definition": "Unapproved test term.",
            "hinglish_definition": "Unapproved test term Hinglish."
        }).insert(ignore_permissions=True)

        # 3. Create Report Template
        self.template = frappe.get_doc({
            "doctype": "SMRITI Report Template",
            "report_name": "Test Governance Report",
            "report_key": "tst_gov_report",
            "report_category": "Sales",
            "base_sql": "SELECT posting_date, grand_total FROM `tabPOS Invoice` WHERE docstatus = 1",
            "columns_json": json.dumps([
                {"fieldname": "tst_dim_approved", "label": "Date"},
                {"fieldname": "tst_meas_approved", "label": "Total"}
            ]),
            "company_restricted": 0,
            "cache_minutes": 0
        }).insert(ignore_permissions=True)

        frappe.db.commit()

    def test_approved_report_executes(self):
        # A valid report with approved terms and approved formulas should run without exceptions
        engine = SMRITIReportEngine("tst_gov_report")
        # Validate that no exceptions are raised
        engine.validate_report_dictionary_bounds()
        engine.validate_report_formula_bounds()

    def test_unregistered_term_fails(self):
        # Set template columns to include an unregistered term
        frappe.db.set_value("SMRITI Report Template", "tst_gov_report", "columns_json", json.dumps([
            {"fieldname": "unregistered_term_xyz", "label": "Invalid"}
        ]))
        frappe.db.commit()
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_dictionary_bounds()
        self.assertIn("not defined in the SMRITI Business Dictionary", str(context.exception))

    def test_deprecated_term_fails(self):
        frappe.db.set_value("SMRITI Report Template", "tst_gov_report", "columns_json", json.dumps([
            {"fieldname": "tst_term_deprecated", "label": "Deprecated"}
        ]))
        frappe.db.commit()
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_dictionary_bounds()
        self.assertTrue("deprecated" in str(context.exception) or "not approved" in str(context.exception))

    def test_blocked_term_fails(self):
        frappe.db.set_value("SMRITI Report Template", "tst_gov_report", "columns_json", json.dumps([
            {"fieldname": "tst_term_blocked", "label": "Blocked"}
        ]))
        frappe.db.commit()
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_dictionary_bounds()
        self.assertIn("not approved", str(context.exception))

    def test_unapproved_term_fails(self):
        frappe.db.set_value("SMRITI Report Template", "tst_gov_report", "columns_json", json.dumps([
            {"fieldname": "tst_term_unapproved", "label": "Unapproved"}
        ]))
        frappe.db.commit()
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_dictionary_bounds()
        self.assertIn("not approved", str(context.exception))

    def test_missing_aggregation_on_measure_fails(self):
        frappe.db.set_value("SMRITI Report Template", "tst_gov_report", "columns_json", json.dumps([
            {"fieldname": "tst_meas_no_agg", "label": "No Aggregation"}
        ]))
        frappe.db.commit()
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_dictionary_bounds()
        self.assertIn("must define a default aggregation type", str(context.exception))

    def test_unapproved_linked_formula_fails(self):
        # Link unapproved formula to tst_meas_approved
        term_doc = frappe.get_doc("SMRITI Business Term", {"term_id": "tst_meas_approved"})
        term_doc.set("related_formulas", [])
        term_doc.append("related_formulas", {
            "formula_id": self.f_unapproved.name
        })
        term_doc.save(ignore_permissions=True)
        frappe.db.commit()

        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_formula_bounds()
        self.assertIn("not approved", str(context.exception))

    def test_inactive_linked_formula_fails(self):
        # Link inactive formula to tst_meas_approved
        term_doc = frappe.get_doc("SMRITI Business Term", {"term_id": "tst_meas_approved"})
        term_doc.set("related_formulas", [])
        term_doc.append("related_formulas", {
            "formula_id": self.f_inactive.name
        })
        term_doc.save(ignore_permissions=True)
        frappe.db.commit()

        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_formula_bounds()
        self.assertIn("inactive", str(context.exception))

    def test_missing_linked_formula_fails(self):
        # Link non-existent formula to tst_meas_approved
        term_doc = frappe.get_doc("SMRITI Business Term", {"term_id": "tst_meas_approved"})
        term_doc.set("related_formulas", [])
        term_doc.append("related_formulas", {
            "formula_id": "NON-EXISTENT"
        })
        term_doc.flags.ignore_links = True
        term_doc.save(ignore_permissions=True)
        frappe.db.commit()

        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.ValidationError) as context:
            engine.validate_report_formula_bounds()
        self.assertIn("does not exist in the Formula Registry", str(context.exception))

    def test_safe_sql_auto_aggregation_and_grouping(self):
        engine = SMRITIReportEngine("tst_gov_report")
        config = {
            "base_sql": "SELECT posting_date, grand_total FROM `tabPOS Invoice` WHERE docstatus = 1",
            "group_by": None,
            "order_by": "posting_date DESC"
        }
        original_sql = frappe.db.sql
        sql_called_with = []
        def mock_sql(query, *args, **kwargs):
            if "tabPOS Invoice" in query and "SELECT parent.posting_date" in query:
                sql_called_with.append(query)
                return []
            return original_sql(query, *args, **kwargs)
        
        try:
            frappe.db.sql = mock_sql
            engine._run_sql_report(config)
        finally:
            frappe.db.sql = original_sql

        self.assertTrue(len(sql_called_with) > 0)
        generated_query = sql_called_with[0]
        
        self.assertIn("SELECT parent.posting_date as tst_dim_approved, Sum(parent.grand_total) as tst_meas_approved FROM `tabPOS Invoice`", generated_query)
        self.assertIn("GROUP BY parent.posting_date", generated_query)

    def test_explainability_audit_log(self):
        original_sql = frappe.db.sql
        def mock_sql(query, *args, **kwargs):
            if "tabPOS Invoice" in query and "SELECT parent.posting_date" in query:
                return []
            return original_sql(query, *args, **kwargs)
        
        try:
            frappe.db.sql = mock_sql
            engine = SMRITIReportEngine("tst_gov_report")
            engine.run()
        finally:
            frappe.db.sql = original_sql
        
        logs = frappe.get_all("SMRITI PSV Activity Log", filters={
            "reference_doctype": "SMRITI Report Template",
            "reference_name": "tst_gov_report",
            "action_type": "Formula Explained"
        }, fields=["details"])
        
        self.assertTrue(len(logs) > 0)
        details = json.loads(logs[0]["details"])
        self.assertIn("tst_dim_approved", details["selected_terms"])
        self.assertIn("tst_meas_approved", details["selected_terms"])
        self.assertEqual(details["aggregation"]["tst_meas_approved"], "Sum")
        self.assertIn("tst_dim_approved", details["group_by"])

    def test_cache_partitioning_and_isolation_test_rep_001(self):
        # TEST-REP-001 (Tenant Cache Partitioning)
        # Verify cache keys are user-and-company specific and include sorted user roles.
        engine = SMRITIReportEngine("tst_gov_report", filters={"company": "Company A"})
        
        # Mock session user and roles
        frappe.session.user = "user_a@example.com"
        original_get_roles = frappe.get_roles
        
        # Test Case 1: user_a, roles ["Role B", "Role A"], Company A
        frappe.get_roles = lambda *args, **kwargs: ["Role B", "Role A"]
        key1 = engine.get_cache_key()
        
        # Test Case 2: same user and company, but different order of roles -> should match because we sort roles
        frappe.get_roles = lambda *args, **kwargs: ["Role A", "Role B"]
        key2 = engine.get_cache_key()
        self.assertEqual(key1, key2)
        
        # Test Case 3: different company -> key should change
        engine_comp_b = SMRITIReportEngine("tst_gov_report", filters={"company": "Company B"})
        key3 = engine_comp_b.get_cache_key()
        self.assertNotEqual(key1, key3)
        
        # Test Case 4: different user -> key should change
        frappe.session.user = "user_b@example.com"
        key4 = engine.get_cache_key()
        self.assertNotEqual(key1, key4)
        
        # Restore original functions
        frappe.get_roles = original_get_roles
        frappe.session.user = "Administrator"

    def test_export_logging_test_rep_002(self):
        # TEST-REP-002 (Export Logging)
        # Verify that invoking export_smriti_report generates a valid SMRITI Audit Event log with expected payload schema
        from smriti_retail_os.reports_api import export_smriti_report
        
        # Clear existing logs for report
        frappe.db.delete("SMRITI Audit Event", {"event_type": "REPORT_EXPORTED"})
        frappe.db.commit()
        
        # Run export
        export_smriti_report("tst_gov_report", filters={"company": "_Test Company"})
        
        # Fetch log
        logs = frappe.get_all("SMRITI Audit Event", filters={"event_type": "REPORT_EXPORTED"}, fields=["after_state", "user", "company"])
        self.assertTrue(len(logs) > 0)
        
        payload = json.loads(logs[0]["after_state"])
        self.assertEqual(payload["report_key"], "tst_gov_report")
        self.assertEqual(payload["export_format"], "csv")
        self.assertEqual(payload["company"], "_Test Company")
        self.assertEqual(payload["user"], frappe.session.user)
        self.assertIn("template_version", payload)
        self.assertIn("rows", payload)
        self.assertIn("filters", payload)

    def test_read_only_query_policy_test_rep_003(self):
        # TEST-REP-003 (Read-Only Query Policy)
        # Verify queries violating REPORT_QUERY_POLICY_V1 are rejected.
        from smriti_retail_os.reports_api import validate_query_safety
        
        # Valid queries
        validate_query_safety("SELECT name FROM tabUser")
        validate_query_safety("WITH cte AS (SELECT 1) SELECT * FROM cte")
        
        # Violations: Multi-statement execution (semicolons)
        with self.assertRaises(frappe.ValidationError) as context:
            validate_query_safety("SELECT name FROM tabUser; DELETE FROM tabUser")
        self.assertIn("Multi-statement", str(context.exception))
        
        # Violations: Must start with SELECT or WITH
        with self.assertRaises(frappe.ValidationError) as context:
            validate_query_safety("INSERT INTO tabUser (name) VALUES ('test')")
        self.assertIn("start with SELECT or WITH", str(context.exception))
        
        # Violations: Mutation keywords
        with self.assertRaises(frappe.ValidationError) as context:
            validate_query_safety("SELECT name FROM tabUser WHERE name = 'test' OR EXISTS (DROP TABLE tabUser)")
        self.assertIn("DDL/DML mutation keywords", str(context.exception))

    def test_default_deny_test_rep_004(self):
        # TEST-REP-004 (Default Deny)
        # Verify empty role access templates block non-manager users.
        self.template.set("role_access", [])
        self.template.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Mock session user with custom non-admin roles
        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda *args, **kwargs: ["SMRITI Cashier"]
        frappe.session.user = "cashier@example.com"
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.PermissionError):
            engine.check_permissions(action="run")
            
        # Restore original
        frappe.get_roles = original_get_roles
        frappe.session.user = "Administrator"

    def test_saved_view_constraints_test_rep_005(self):
        # TEST-REP-005 (Saved View Constraints)
        # Verify uniqueness and JSON validation gates in SMRITI Saved View.
        view1 = frappe.get_doc({
            "doctype": "SMRITI Saved View",
            "view_name": "Test Saved View 1",
            "report_template": "tst_gov_report",
            "user": "test_user@example.com",
            "applied_filters_json": '{"company": "Test Company"}',
            "visible_columns_json": '["tst_dim_approved"]'
        })
        view1.insert(ignore_permissions=True)
        
        # Try duplicate uniqueness -> should fail
        view2 = frappe.get_doc({
            "doctype": "SMRITI Saved View",
            "view_name": "Test Saved View 1",
            "report_template": "tst_gov_report",
            "user": "test_user@example.com",
            "applied_filters_json": '{"company": "Test Company"}',
            "visible_columns_json": '["tst_dim_approved"]'
        })
        with self.assertRaises(frappe.ValidationError) as context:
            view2.insert(ignore_permissions=True)
        self.assertIn("already exists", str(context.exception))
        
        # Invalid JSON filters -> should fail
        view3 = frappe.get_doc({
            "doctype": "SMRITI Saved View",
            "view_name": "Test Saved View 2",
            "report_template": "tst_gov_report",
            "user": "test_user@example.com",
            "applied_filters_json": '{company: Test Company}',
            "visible_columns_json": '["tst_dim_approved"]'
        })
        with self.assertRaises(frappe.ValidationError) as context:
            view3.insert(ignore_permissions=True)
        self.assertIn("Invalid JSON format", str(context.exception))
        
        # Clean up
        frappe.db.delete("SMRITI Saved View", {"report_template": "tst_gov_report"})
        frappe.db.commit()

    def test_template_audit_and_versioning_test_rep_006(self):
        # TEST-REP-006 (Template Audit & Versioning)
        # Verify modifying a template's details logs audit payload and increments version.
        frappe.db.delete("SMRITI Audit Event", {"event_type": "REPORT_TEMPLATE_MODIFIED"})
        frappe.db.commit()
        
        template_doc = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        old_version = template_doc.template_version or 1
        template_doc.report_name = "Test Governance Report Modified"
        template_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Check version incremented
        updated_template = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        self.assertEqual(updated_template.template_version, old_version + 1)
        
        # Check audit event log
        logs = frappe.get_all("SMRITI Audit Event", filters={"event_type": "REPORT_TEMPLATE_MODIFIED"}, fields=["before_state", "after_state"])
        self.assertTrue(len(logs) > 0)
        
        before = json.loads(logs[0]["before_state"])
        after = json.loads(logs[0]["after_state"])
        self.assertEqual(before["report_name"], "Test Governance Report")
        self.assertEqual(after["report_name"], "Test Governance Report Modified")

    def test_saved_view_ownership_isolation_test_rep_007(self):
        # TEST-REP-007 (Saved Views Ownership Protection)
        # Verify User A cannot modify or delete User B's saved view.
        view = frappe.get_doc({
            "doctype": "SMRITI Saved View",
            "view_name": "User B View",
            "report_template": "tst_gov_report",
            "user": "user_b@example.com",
            "applied_filters_json": '{}',
            "visible_columns_json": '[]'
        })
        view.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Login as User A and try to edit -> should fail
        frappe.session.user = "user_a@example.com"
        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda *args, **kwargs: ["SMRITI Store Manager"]
        
        view_doc = frappe.get_doc("SMRITI Saved View", view.name)
        view_doc.view_name = "User B View Edited"
        with self.assertRaises(frappe.PermissionError):
            view_doc.save(ignore_permissions=True)
            
        # Login as User A and try to delete -> should fail
        with self.assertRaises(frappe.PermissionError):
            view_doc.delete(ignore_permissions=True)
            
        # Restore original
        frappe.get_roles = original_get_roles
        frappe.session.user = "Administrator"
        frappe.db.delete("SMRITI Saved View", {"name": view.name})
        frappe.db.commit()

    def test_export_permission_enforcement_test_rep_008(self):
        # TEST-REP-008 (Export Permission Enforcement)
        # Verify a user with cashier role cannot call export_smriti_report without explicit permission.
        self.template.set("role_access", [])
        self.template.append("role_access", {
            "role": "SMRITI Cashier",
            "export_allowed": 0
        })
        self.template.save(ignore_permissions=True)
        frappe.db.commit()
        
        original_get_roles = frappe.get_roles
        frappe.get_roles = lambda *args, **kwargs: ["SMRITI Cashier"]
        frappe.session.user = "cashier@example.com"
        
        engine = SMRITIReportEngine("tst_gov_report")
        with self.assertRaises(frappe.PermissionError) as context:
            engine.check_permissions(action="export")
        self.assertIn("Export Denied", str(context.exception))
        
        # Now explicitly grant template-level export role
        frappe.session.user = "Administrator"
        frappe.get_roles = original_get_roles
        
        t_doc = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        t_doc.set("role_access", [])
        t_doc.append("role_access", {
            "role": "SMRITI Cashier",
            "export_allowed": 1
        })
        t_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Test again as cashier -> should now succeed
        frappe.get_roles = lambda *args, **kwargs: ["SMRITI Cashier"]
        frappe.session.user = "cashier@example.com"
        
        engine2 = SMRITIReportEngine("tst_gov_report")
        self.assertTrue(engine2.check_permissions(action="export"))
        
        # Restore original
        frappe.get_roles = original_get_roles
        frappe.session.user = "Administrator"

    def test_concurrent_template_versioning_test_rep_009(self):
        # TEST-REP-009 (Concurrent Template Versioning)
        # Verify template version assignment is serialized and increments sequentially.
        template_doc = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        v1 = template_doc.template_version or 1
        
        # Simulating concurrent fetch:
        doc1 = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        doc2 = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        
        doc1.save(ignore_permissions=True)
        
        # doc2 has stale modified timestamp. Saving it directly raises TimestampMismatchError
        with self.assertRaises(frappe.TimestampMismatchError):
            doc2.save(ignore_permissions=True)
            
        # Reloading doc2 gets the new version and timestamp, then saving increments version again
        doc2.reload()
        doc2.save(ignore_permissions=True)
        frappe.db.commit()
        
        final_doc = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        self.assertEqual(final_doc.template_version, v1 + 2)

    def test_incompatible_report_column(self):
        # Create a business term that references POS Invoice Item (aliased as items)
        self.t_meas_items = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "tst_meas_items_qty",
            "term_name": "Test Items Qty",
            "term_category": "Sales",
            "term_version": "1.0",
            "status": "Approved",
            "approval_status": "Approved",
            "is_active": 1,
            "is_reportable": 1,
            "measure_or_dimension": "Measure",
            "default_aggregation": "Sum",
            "dictionary_key": "tst_meas_items_qty",
            "projection_path": "POS Invoice Item.qty",
            "entity_type": "POS Invoice Item",
            "data_type": "Float",
            "effective_date": "2026-06-20",
            "definition": "Approved test items quantity.",
            "hinglish_definition": "Approved test items quantity Hinglish."
        }).insert(ignore_permissions=True)
        frappe.db.commit()

        # Update the report template columns to include this incompatible column
        t_doc = frappe.get_doc("SMRITI Report Template", "tst_gov_report")
        original_columns = t_doc.columns_json
        t_doc.columns_json = json.dumps([
            {"fieldname": "tst_dim_approved", "label": "Date"},
            {"fieldname": "tst_meas_items_qty", "label": "Incompatible Qty"}
        ])
        t_doc.save(ignore_permissions=True)
        frappe.db.commit()

        # base_sql does not join POS Invoice Item, so running the report should throw a ValidationError
        engine = SMRITIReportEngine("tst_gov_report")
        config = {
            "base_sql": "SELECT parent.posting_date FROM `tabPOS Invoice` parent WHERE parent.docstatus = 1",
            "group_by": None,
            "order_by": "parent.posting_date DESC"
        }
        with self.assertRaises(frappe.ValidationError) as context:
            engine._run_sql_report(config)
        self.assertIn("cannot be displayed in this report because it requires the 'POS Invoice Item' table", str(context.exception))

        # Restore original template columns and clean up term
        t_doc.reload()
        t_doc.columns_json = original_columns
        t_doc.save(ignore_permissions=True)
        frappe.db.delete("SMRITI Business Term", {"term_id": "tst_meas_items_qty"})
        frappe.db.commit()
