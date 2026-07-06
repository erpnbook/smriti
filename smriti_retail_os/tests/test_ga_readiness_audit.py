# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_ga_readiness_audit.py
# @description: Cross-module integration regression suite for SMRITI Retail OS (GA Readiness Audit v1.1).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
import unittest
import werkzeug.routing.exceptions
from unittest.mock import patch
from frappe import _
from frappe.utils import today, now_datetime, add_days
from smriti_retail_os.tests.test_psv import TestPSV
from smriti_retail_os.boot import check_desk_access
from smriti_retail_os.api.explain_api import get_explain_payload
from smriti_retail_os.cge.service.cge_service import CGERuleEvaluator
from smriti_retail_os.services.pdt_service import rebuild_twin_cache
from smriti_retail_os.reports_api import SMRITIReportEngine
from smriti_retail_os.ledger_engine import make_ledger_entry

class TestGAReadinessAudit(TestPSV):
    def setUp(self):
        super().setUp()
        frappe.session.user = "Administrator"
        # Ensure any test formula or terms are deleted before run
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": "TST-SYNC-FRM"})
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST_SYNC_TRM"})
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_uri": ["in", ["smriti:formula:TST-SYNC-FRM", "smriti:term:TST_SYNC_TRM"]]})
        frappe.db.delete("SMRITI Knowledge Relation")
        frappe.db.delete("SMRITI SKU Twin", {"company": self.company, "party_stock_account": self.account_name, "item_code": self.item})
        frappe.db.delete("SMRITI Loyalty Rule")
        frappe.db.delete("SMRITI Loyalty Tier")

    def tearDown(self):
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": "TST-SYNC-FRM"})
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST_SYNC_TRM"})
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_uri": ["in", ["smriti:formula:TST-SYNC-FRM", "smriti:term:TST_SYNC_TRM"]]})
        frappe.db.delete("SMRITI Knowledge Relation")
        frappe.db.delete("SMRITI SKU Twin", {"company": self.company, "party_stock_account": self.account_name, "item_code": self.item})
        frappe.db.delete("SMRITI Loyalty Rule")
        frappe.db.delete("SMRITI Loyalty Tier")
        super().tearDown()

    @patch("smriti_retail_os.psv_service.create_psv_transaction", side_effect=Exception("Simulated PSV DB Failure"))
    def test_billing_psv_resiliency(self, mock_create):
        """Verify that PSV Inventory Visibility Layer failure does not block Sales Invoice submission and creates an Exception Record."""
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
            "qty": 1.0,
            "rate": 100.0,
            "income_account": self.income_account,
            "cost_center": self.cost_center
        })
        si.insert(ignore_permissions=True)
        si.submit()

        # Assert invoice submits successfully
        self.assertEqual(si.docstatus, 1)

        # Assert exception record is created
        ex_rec_name = frappe.db.exists("SMRITI PSV Exception Record", {
            "party_stock_account": self.account_name,
            "sales_invoice": si.name,
            "status": "Pending Reconciliation"
        })
        self.assertTrue(ex_rec_name)

        # Assert exception record fields
        ex_rec = frappe.get_doc("SMRITI PSV Exception Record", ex_rec_name)
        self.assertEqual(ex_rec.sales_invoice, si.name)
        # Pending Reconciliation is SMRITI's Open state for PSV Exception Records
        self.assertEqual(ex_rec.status, "Pending Reconciliation")

        # Clean up Sales Invoice so it does not leak as an orphan to other health check tests
        frappe.db.delete("Sales Invoice", {"name": si.name})
        frappe.db.delete("Sales Invoice Item", {"parent": si.name})
        frappe.db.commit()

    def test_desk_routing_interception(self):
        """Verify that attempts to access blocked native desk/app routes raise RequestRedirect to SMRITI."""
        # Test paths that must trigger a redirect to /smriti
        test_paths = [
            "/desk/setup-wizard",
            "/desk/modules",
            "/desk#Form",
            "/desk/workspace",
            "/app/setup-wizard",
            "/app/modules"
        ]
        
        class MockRequest:
            def __init__(self, path):
                self.path = path
                self.cookies = {}
        
        # Set user as cashier (non-System-Manager) to enforce desk-access guard on remaining /desk/ and /app/ routes
        original_user = frappe.session.user
        frappe.session.user = "cashier@example.com"
        if not frappe.db.exists("User", "cashier@example.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "cashier@example.com",
                "first_name": "Cashier Test",
                "send_welcome_email": 0
            }).insert(ignore_permissions=True)
            user.add_roles("SMRITI Cashier")
            frappe.db.commit()
            
        original_request = getattr(frappe.local, "request", None)
        try:
            for path in test_paths:
                frappe.local.request = MockRequest(path)
                with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect) as context:
                    check_desk_access()
                self.assertEqual(context.exception.new_url, "/smriti")
        finally:
            frappe.session.user = "Administrator"
            if original_request:
                frappe.local.request = original_request
            else:
                delattr(frappe.local, "request")

    def test_explainability_metrics_validation(self):
        """Verify explainability definition resolves correctly for standard formulas."""
        # Ensure INV-002 exists and is active and approved
        fid = "INV-002"
        if not frappe.db.exists("SMRITI Formula Definition", {"formula_id": fid}):
            frappe.get_doc({
                "doctype": "SMRITI Formula Definition",
                "formula_id": fid,
                "formula_name": "Weeks of Cover Formula",
                "formula_version": "1.0.0",
                "formula_category": "Inventory",
                "status": "Approved",
                "is_active": 1,
                "effective_date": today(),
                "formula_expression": "current_stock / weekly_velocity",
                "business_meaning": "Tracks how many weeks current inventory will last.",
                "worked_example": "100 units stock / 25 weekly velocity = 4.0 WOC",
                "interpretation_guide": "3-4 weeks is normal.",
                "recommended_action": "Order when WOC < lead time.",
                "implementation_reference": "pdt_service.py",
                "business_owner": "Jawahar R. Mallah"
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            frappe.db.set_value("SMRITI Formula Definition", {"formula_id": fid}, {"status": "Approved", "is_active": 1})
            frappe.db.commit()
            
        # Clear cache for the formula
        version = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": fid, "is_active": 1, "status": "Approved"}, "formula_version")
        frappe.cache().delete_value(f"smriti:explain:{fid}:{version}")

        # Retrieve formula explainability payload
        payload = get_explain_payload(formula_id="INV-002")
        
        # Assertions
        self.assertEqual(payload["formula_id"], "INV-002")
        self.assertTrue(payload["business_meaning"])
        self.assertTrue(payload["formula_expression"])
        self.assertTrue(payload["worked_example"])
        
        # Verify explain audit log was successfully generated
        logs = frappe.get_all("SMRITI PSV Activity Log", filters={
            "reference_name": "INV-002",
            "action_type": "Formula Explained"
        })
        self.assertTrue(len(logs) > 0)

    def test_cge_resolution_pipeline(self):
        """Verify CGE rules, loyalty tier multipliers, and priority resolution without database wallet mutations."""
        # 1. Configure tier: Gold Tier gets 1.5X multiplier
        if not frappe.db.exists("SMRITI Loyalty Tier", "Gold Tier"):
            tier = frappe.new_doc("SMRITI Loyalty Tier")
            tier.tier_name = "Gold Tier"
            tier.min_points = 0.0
            tier.tier_multiplier = 1.5
            tier.active = 1
            tier.insert(ignore_permissions=True)
            frappe.db.commit()
            
        # Configure rule: Test Brand gets 2.0X multiplier, stacking allowed
        brand = "CGE Test Brand"
        if not frappe.db.exists("Brand", brand):
            b_doc = frappe.new_doc("Brand")
            b_doc.brand = brand
            b_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
        if not frappe.db.exists("SMRITI Loyalty Rule", "CGE Brand Multiplier"):
            rule = frappe.new_doc("SMRITI Loyalty Rule")
            rule.rule_name = "CGE Brand Multiplier"
            rule.rule_type = "Multiplier"
            rule.dimension = "Brand"
            rule.dimension_doctype = "Brand"
            rule.dimension_value = brand
            rule.rule_value = 2.0
            rule.priority = 1
            rule.allow_stack = 1
            rule.status = "Active"
            rule.insert(ignore_permissions=True)
            frappe.db.commit()
            
        # Ensure CGE settings is populated
        settings = frappe.get_doc("SMRITI CGE Settings")
        settings.enable_rule_trace = 1
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Create a Sales Invoice mockup (do not submit/commit wallet balances)
        invoice = frappe.new_doc("Sales Invoice")
        invoice.name = "INV-CGE-TEST-GA-01"
        invoice.customer = self.customer
        invoice.posting_date = today()
        invoice.company = self.company
        
        # Create test item with brand
        item_code = "TEST-CGE-GA-ITEM"
        if not frappe.db.exists("Item", item_code):
            itm = frappe.new_doc("Item")
            itm.item_code = item_code
            itm.item_name = "Test CGE Ray Item"
            itm.item_group = self.item_group
            itm.brand = brand
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.insert(ignore_permissions=True)
            frappe.db.commit()
            
        invoice.append("items", {
            "item_code": item_code,
            "qty": 1,
            "rate": 1000.0,
            "warehouse": self.warehouse
        })
        
        # Evaluate CGE resolution pipeline
        evaluator = CGERuleEvaluator(invoice)
        results = evaluator.evaluate()
        
        # Assert rule evaluation resolves correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["multiplier"], 3.0) # 2.0 brand * 1.5 Gold Tier = 3.0

    def test_pdt_cache_refresh_pipeline(self):
        """Verify the Product Twin cache rebuild and recalculation pipeline."""
        # Seed some sales history to generate velocity calculation
        # Add 5 sales of 10 units each
        for i in range(5):
            posting_time = add_days(now_datetime(), -i)
            make_ledger_entry(
                company=self.company,
                posting_datetime=posting_time,
                party_stock_account=self.account_name,
                item_code=self.item,
                qty=-10.0,
                voucher_type="Sales",
                voucher_no=f"INV-PDT-TEST-{i}"
            )
        frappe.db.commit()
        
        # Trigger cache rebuild
        rebuild_twin_cache(self.company, self.account_name, self.item, "FULL_REBUILD")
        
        # Assert database record exists
        twin_name = frappe.db.exists("SMRITI SKU Twin", {
            "company": self.company,
            "party_stock_account": self.account_name,
            "item_code": self.item
        })
        self.assertTrue(twin_name)
        
        twin = frappe.get_doc("SMRITI SKU Twin", twin_name)
        
        # Assertions on pipeline metrics calculations (not specific forecast accuracy values)
        self.assertIsNotNone(twin.weekly_velocity)
        self.assertGreater(twin.weekly_velocity, 0.0)
        
        self.assertIsNotNone(twin.weeks_of_cover)
        self.assertIsNotNone(twin.last_recalculated)
        self.assertEqual(twin.freshness_status, "Fresh")
        
        # Assert Redis cache is updated
        redis_key = f"smriti:pdt:{self.company}:{self.account_name}:{self.item}"
        cached = frappe.cache().get_value(redis_key)
        self.assertIsNotNone(cached)

    def test_dictionary_formula_sync(self):
        """Verify SKOS Asset auto-sync edge maps between Formula and Business Dictionary."""
        # 1. Clean existing records
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": "TST-SYNC-FRM"})
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST_SYNC_TRM"})
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_uri": ["in", ["smriti:formula:TST-SYNC-FRM", "smriti:term:TST_SYNC_TRM"]]})
        frappe.db.delete("SMRITI Knowledge Relation")
        frappe.db.commit()
        
        # 2. Create Formula Definition
        frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-SYNC-FRM",
            "formula_name": "Sync Test Formula",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": today(),
            "formula_expression": "A / B",
            "business_meaning": "Formula definition for test sync",
            "worked_example": "10 / 2 = 5",
            "interpretation_guide": "Interpretation details",
            "recommended_action": "Recommended details",
            "implementation_reference": "Ref",
            "business_owner": "Jawahar R. Mallah"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        
        # 3. Create Business Term
        formula_name = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": "TST-SYNC-FRM"})
        frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST_SYNC_TRM",
            "term_name": "Sync Test Term",
            "term_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "term_version": "1.0.0",
            "effective_date": today(),
            "definition": "Business term definition for test sync",
            "hinglish_definition": "Hinglish test definition",
            "term_aliases": json.dumps(["TST_SYNC_TRM"]),
            "manual_reference": "Volume 3 > Test Reference",
            "training_reference": "TRN-SYNC-TEST",
            "related_formulas": [{"formula_id": formula_name}],
            "related_terms": [],
            "faq": json.dumps([]),
            "common_mistakes": json.dumps([])
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        
        # 4. Verify SKOS Asset Auto-Sync
        # SMRITI Knowledge Asset exists for Formula
        formula_asset = frappe.db.exists("SMRITI Knowledge Asset", {"asset_uri": "smriti:formula:TST-SYNC-FRM"})
        self.assertTrue(formula_asset)
        
        # SMRITI Knowledge Asset exists for Term
        term_asset = frappe.db.exists("SMRITI Knowledge Asset", {"asset_uri": "smriti:term:TST_SYNC_TRM"})
        self.assertTrue(term_asset)
        
        # Verify directed relation edge exists in KGR-01
        f_asset_name = frappe.db.get_value("SMRITI Knowledge Asset", {"asset_uri": "smriti:formula:TST-SYNC-FRM"})
        t_asset_name = frappe.db.get_value("SMRITI Knowledge Asset", {"asset_uri": "smriti:term:TST_SYNC_TRM"})
        relation_exists = frappe.db.exists("SMRITI Knowledge Relation", {
            "source_asset_id": t_asset_name,
            "target_asset_id": f_asset_name
        })
        self.assertTrue(relation_exists)
        
        # 5. Query Explain Engine
        payload = get_explain_payload(formula_id="TST-SYNC-FRM")
        self.assertEqual(payload["formula_id"], "TST-SYNC-FRM")
        self.assertEqual(payload["business_meaning"], "Formula definition for test sync")

    def test_report_dictionary_runtime_resolution(self):
        """Verify report engine projection recovery fallback and explainability audit logs."""
        template_id = "test_resolution_report"
        if not frappe.db.exists("SMRITI Report Template", template_id):
            tpl = frappe.new_doc("SMRITI Report Template")
            tpl.report_key = template_id
            tpl.report_name = "Test Resolution Report"
            tpl.report_category = "Sales"
            # Request 'qty_sold' which is in our dictionary aliases
            tpl.columns_json = json.dumps([
                {"fieldname": "qty_sold", "label": "Qty Sold"}
            ])
            tpl.insert(ignore_permissions=True)
            frappe.db.commit()
            
        from smriti_retail_os.reports_api import REPORT_QUERIES
        REPORT_QUERIES[template_id] = {
            "base_sql": "SELECT SUM(parent.total_qty) as qty_sold FROM `tabPOS Invoice` parent WHERE parent.docstatus = 1",
            "group_by": None,
            "order_by": None
        }
        
        # Clear audit logs for this template
        frappe.db.delete("SMRITI PSV Activity Log", {
            "reference_name": template_id,
            "action_type": "Formula Explained"
        })
        frappe.db.commit()
        
        try:
            filters = {"company": self.company}
            engine = SMRITIReportEngine(template_id, filters)
            res = engine.run()
            
            # Assert report runs successfully
            self.assertTrue(isinstance(res, list))
            
            # Assert projection recovery occurs and explainability audit event is created
            logs = frappe.get_all("SMRITI PSV Activity Log", filters={
                "reference_name": template_id,
                "action_type": "Formula Explained"
            })
            self.assertTrue(len(logs) > 0)
        finally:
            if template_id in REPORT_QUERIES:
                del REPORT_QUERIES[template_id]
