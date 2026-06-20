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
        frappe.db.commit()

        # Clean up dynamic report config
        from smriti_retail_os.reports_api import REPORT_QUERIES
        if "tst_gov_report" in REPORT_QUERIES:
            del REPORT_QUERIES["tst_gov_report"]

    def create_test_records(self):
        # Register dynamic report config
        from smriti_retail_os.reports_api import REPORT_QUERIES
        REPORT_QUERIES["tst_gov_report"] = {
            "base_sql": "SELECT posting_date, grand_total FROM `tabPOS Invoice` WHERE docstatus = 1",
            "group_by": None,
            "order_by": "posting_date DESC"
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
