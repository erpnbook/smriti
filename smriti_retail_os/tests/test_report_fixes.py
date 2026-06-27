# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_report_fixes.py
# @description: Unit tests for SMRITI Report Run Fixes (ACP-REPORTS-002).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
from frappe import _
from smriti_retail_os.reports_api import (
    SMRITIReportEngine,
    get_smriti_report_data,
    extract_select_alias_map,
    expression_contains_subquery,
    table_supports_company_filter
)

class TestReportFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure test company exists
        cls.company_name = "_Test Company"
        if not frappe.db.exists("Company", cls.company_name):
            cls.company = frappe.new_doc("Company")
            cls.company.company_name = cls.company_name
            cls.company.default_currency = "INR"
            cls.company.country = "India"
            cls.company.insert(ignore_permissions=True)
            frappe.db.commit()

    def test_alias_map_extraction(self):
        """Test extract_select_alias_map parses select projections properly."""
        sql = """
            SELECT 
                COALESCE(i.custom_style_code, i.variant_of, i.name) as style_code,
                COALESCE(parent_item.item_name, i.item_name) as style_name,
                SUM(parent.total_qty) as qty_sold
            FROM `tabPOS Invoice Item` items
            JOIN `tabPOS Invoice` parent ON items.parent = parent.name
            WHERE 1=1
        """
        alias_map = extract_select_alias_map(sql)
        self.assertEqual(alias_map.get("style_code"), "COALESCE(i.custom_style_code, i.variant_of, i.name)")
        self.assertEqual(alias_map.get("style_name"), "COALESCE(parent_item.item_name, i.item_name)")
        self.assertEqual(alias_map.get("qty_sold"), "SUM(parent.total_qty)")

    def test_subquery_detection(self):
        """Test expression_contains_subquery flags expressions containing subqueries."""
        expr_with_select = "(SELECT name FROM `tabPOS Invoice` LIMIT 1)"
        expr_with_exists = "EXISTS(SELECT 1 FROM `tabItem` WHERE name=item_code)"
        normal_expr = "SUM(parent.total_qty)"
        
        self.assertTrue(expression_contains_subquery(expr_with_select))
        self.assertTrue(expression_contains_subquery(expr_with_exists))
        self.assertFalse(expression_contains_subquery(normal_expr))

    def test_reserved_aliases_guard(self):
        """Test that reserved aliases raise validation error during dynamic projection."""
        filters = {"company": self.company_name}
        engine = SMRITIReportEngine("daily_sales_summary", filters)
        engine.template.columns_json = json.dumps([
            {"fieldname": "parent", "label": "Parent"}
        ])
        
        with self.assertRaises(frappe.ValidationError):
            engine.run()

    def test_subquery_recovery_guard(self):
        """Test that subquery expressions in dictionary projection recovery are blocked."""
        # 1. Create a temporary report template
        template_id = "test_subquery_report"
        if not frappe.db.exists("SMRITI Report Template", template_id):
            tpl = frappe.new_doc("SMRITI Report Template")
            tpl.report_key = template_id
            tpl.report_name = "Test Subquery Report"
            tpl.report_category = "Sales"
            tpl.columns_json = json.dumps([
                {"fieldname": "qty_sold", "label": "Qty Sold"}
            ])
            tpl.insert(ignore_permissions=True)
            frappe.db.commit()

        # 2. Register temporary query in REPORT_QUERIES with subquery select alias
        from smriti_retail_os.reports_api import REPORT_QUERIES
        REPORT_QUERIES[template_id] = {
            "base_sql": "SELECT (SELECT SUM(qty) FROM `tabPOS Invoice Item` WHERE parent = name) as qty_sold FROM `tabPOS Invoice` WHERE 1=1",
            "group_by": None,
            "order_by": None
        }

        try:
            filters = {"company": self.company_name}
            engine = SMRITIReportEngine(template_id, filters)
            
            with self.assertRaises(frappe.ValidationError):
                engine.run()
        finally:
            # Clean up temporary query registration
            if template_id in REPORT_QUERIES:
                del REPORT_QUERIES[template_id]

    def test_unknown_column_validation_error(self):
        """Test that unrecognized terms in columns_json raise ValidationError."""
        filters = {"company": self.company_name}
        engine = SMRITIReportEngine("daily_sales_summary", filters)
        engine.template.columns_json = json.dumps([
            {"fieldname": "non_existent_column_abc", "label": "Unknown"}
        ])
        
        with self.assertRaises(frappe.ValidationError) as context:
            engine.run()
        self.assertIn("not defined in the SMRITI Business Dictionary", str(context.exception))

    def test_activity_log_company_filter(self):
        """Test that report query does not append company filter for tabActivity Log."""
        sql_with_activity_log = "SELECT user FROM `tabActivity Log` WHERE 1=1"
        self.assertFalse(table_supports_company_filter(sql_with_activity_log))

        filters = {"company": self.company_name}
        engine = SMRITIReportEngine("security_audit_log", filters)
        res = engine.run()
        self.assertTrue(isinstance(res, list))

    def test_custom_report_bypass(self):
        """Test that custom reports bypass dictionary checks but still enforce permissions and safety."""
        filters = {"company": self.company_name, "from_date": "2026-06-01", "to_date": "2026-06-07"}
        engine = SMRITIReportEngine("cash_book", filters)
        res = engine.run()
        self.assertTrue(isinstance(res, list))
