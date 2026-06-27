# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_knowledge_center.py
# @description: Unit tests for SMRITI Knowledge Center — search and content APIs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
import json
import unittest
from smriti_retail_os.services.knowledge_service import (
    rebuild_knowledge_index,
    search_knowledge_index,
    calculate_knowledge_coverage,
    get_governance_stats,
    REDIS_INDEX_KEY
)

class TestKnowledgeCenter(unittest.TestCase):
    def setUp(self):
        # Clean up test terms and formulas to avoid collision
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002", "TST-TERM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001", "TST-F-002", "TST-FORM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["in", ["TST-T-001", "TST-T-002", "TST-F-001", "TST-F-002", "TST-TERM-RANK-MATCH", "TST-FORM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": ["in", ["TST-T-001", "TST-F-001"]]})
        frappe.db.delete("SMRITI PSV Exam Attempt", {"user": ["in", ["test@example.com", "Administrator"]]})
        frappe.db.commit()
        frappe.cache().delete_value(REDIS_INDEX_KEY)

    def tearDown(self):
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002", "TST-TERM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001", "TST-F-002", "TST-FORM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["in", ["TST-T-001", "TST-T-002", "TST-F-001", "TST-F-002", "TST-TERM-RANK-MATCH", "TST-FORM-RANK-MATCH"]]})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": ["in", ["TST-T-001", "TST-F-001"]]})
        frappe.db.delete("SMRITI PSV Exam Attempt", {"user": ["in", ["test@example.com", "Administrator"]]})
        frappe.db.commit()
        frappe.cache().delete_value(REDIS_INDEX_KEY)

    def test_rebuild_and_search_index(self):
        # 1. Insert test business term
        t_doc = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-001",
            "term_name": "Test Glossary Term One",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "This is a test dictionary definition for search validation.",
            "hinglish_definition": "Hinglish explanation here.",
            "term_aliases": json.dumps(["Glossary Term One Alias"])
        })
        t_doc.insert(ignore_permissions=True)

        # 2. Insert test formula definition
        f_doc = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-F-001",
            "formula_name": "Test Formula One",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "formula_expression": "tst_f = a + b",
            "business_meaning": "Formula to test index search logic.",
            "worked_example": "a=1, b=2 => 3",
            "interpretation_guide": "Bands: Good/Bad",
            "recommended_action": "Do nothing"
        })
        f_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Rebuild index manually (though triggers would have run)
        count = rebuild_knowledge_index()
        self.assertGreater(count, 2)

        # Check search functionality
        results_term = search_knowledge_index("Glossary Term One")
        self.assertGreater(len(results_term), 0)
        self.assertEqual(results_term[0]["id"], "dict:TST-T-001")
        self.assertEqual(results_term[0]["type"], "Dictionary Term")
        self.assertEqual(results_term[0]["weight"], 100)

        # Check alias search
        results_alias = search_knowledge_index("Glossary Term One Alias")
        self.assertGreater(len(results_alias), 0)
        self.assertEqual(results_alias[0]["id"], "dict:TST-T-001")

        # Check formula search
        results_formula = search_knowledge_index("Test Formula One")
        self.assertGreater(len(results_formula), 0)
        self.assertEqual(results_formula[0]["id"], "formula:TST-F-001")
        self.assertEqual(results_formula[0]["type"], "Formula Definition")
        self.assertEqual(results_formula[0]["weight"], 90)

    def test_ranking_and_weighting(self):
        # Insert a term and a formula sharing the same keyword in title/content
        # Term has weight 100, Formula has weight 90
        # When searched, they should score the same on matching, but term should be ordered first
        t_doc = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-TERM-RANK-MATCH",
            "term_name": "SharedKeyword Term",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "A term designed to test rank match priority.",
            "hinglish_definition": "Hinglish explanation.",
            "term_aliases": json.dumps([])
        })
        t_doc.insert(ignore_permissions=True)

        f_doc = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-FORM-RANK-MATCH",
            "formula_name": "SharedKeyword Formula",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "formula_expression": "x = y",
            "business_meaning": "A formula designed to test rank match priority.",
            "worked_example": "x=1",
            "interpretation_guide": "Bands",
            "recommended_action": "Action"
        })
        f_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        rebuild_knowledge_index()

        # Search for "SharedKeyword"
        results = search_knowledge_index("SharedKeyword")
        self.assertGreaterEqual(len(results), 2)
        
        # Verify the top is the Dictionary Term
        self.assertEqual(results[0]["type"], "Dictionary Term")
        self.assertEqual(results[0]["id"], "dict:TST-TERM-RANK-MATCH")
        
        # Verify the second is the Formula
        self.assertEqual(results[1]["type"], "Formula Definition")
        self.assertEqual(results[1]["id"], "formula:TST-FORM-RANK-MATCH")

    def test_knowledge_coverage_calculation(self):
        # Delete existing terms so we control the math completely
        frappe.db.delete("SMRITI Business Term")
        frappe.db.commit()

        # 1. Complete Term
        c_term = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-001",
            "term_name": "Complete Glossary Term",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "This definition is long enough to pass validation.",
            "hinglish_definition": "Hinglish explanation.",
            "faq": json.dumps([{"question": "Q?", "answer": "A."}]),
            "manual_reference": "Vol 1",
            "training_reference": "Exercise 52"
        })
        c_term.insert(ignore_permissions=True)

        # 2. Incomplete Term (Missing FAQ/Refs)
        i_term = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-002",
            "term_name": "Incomplete Glossary Term",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "Definition is also long enough.",
            "hinglish_definition": "Hinglish explanation.",
            "faq": json.dumps([]), # Empty faq
            "manual_reference": "",
            "training_reference": ""
        })
        i_term.insert(ignore_permissions=True)
        frappe.db.commit()

        coverage = calculate_knowledge_coverage()
        # 1 complete out of 2 total active terms = 50.0%
        self.assertEqual(coverage, 50.0)

    def test_governance_stats(self):
        # Ensure we have some terms and formulas
        t_doc = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-001",
            "term_name": "Test Glossary Term One",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "This is a test dictionary definition for search validation.",
            "hinglish_definition": "Hinglish explanation here."
        })
        t_doc.insert(ignore_permissions=True)

        f_doc = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-F-001",
            "formula_name": "Test Formula One",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "formula_expression": "tst_f = a + b",
            "business_meaning": "Formula to test index search logic."
        })
        f_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Simulate access logs
        # Dictionary Accessed log
        log_term = frappe.get_doc({
            "doctype": "SMRITI PSV Activity Log",
            "timestamp": frappe.utils.now_datetime(),
            "event_type": "DICTIONARY_ACCESSED",
            "action_type": "Dictionary Accessed",
            "reference_name": "TST-T-001",
            "user": "test@example.com",
            "details": "Version: 1.0.0"
        })
        log_term.insert(ignore_permissions=True)

        # Formula Explained log
        log_formula = frappe.get_doc({
            "doctype": "SMRITI PSV Activity Log",
            "timestamp": frappe.utils.now_datetime(),
            "event_type": "FORMULA_EXPLAINED",
            "action_type": "Formula Explained",
            "reference_name": "TST-F-001",
            "user": "test@example.com",
            "details": "Version: 1.0.0"
        })
        log_formula.insert(ignore_permissions=True)
        frappe.db.commit()

        stats = get_governance_stats()
        self.assertGreaterEqual(stats["terms_count"], 1)
        self.assertGreaterEqual(stats["formulas_count"], 1)
        self.assertGreaterEqual(len(stats["top_terms"]), 1)
        self.assertGreaterEqual(len(stats["top_formulas"]), 1)
        
        # Verify specific references in top statistics
        term_ids = [t["id"] for t in stats["top_terms"]]
        formula_ids = [f["id"] for f in stats["top_formulas"]]
        self.assertIn("TST-T-001", term_ids)
        self.assertIn("TST-F-001", formula_ids)

    def test_document_registry_role_visibility(self):
        from smriti_retail_os.api.help_api import get_document_registry, get_manual_html, search_knowledge

        # Test as System Manager (Administrator)
        frappe.set_user('Administrator')
        admin_registry = get_document_registry()
        
        # Verify Governance docs are present for Administrator
        self.assertIn("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION", admin_registry)
        self.assertIn("AI_CONTENT_POLICY", admin_registry)
        
        # Verify direct file read works for Administrator
        brd_html = get_manual_html("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION")
        self.assertIn("Branding", brd_html)
        
        # Test as Store Manager (manager@smriti.com) - SMRITI Store Manager is not a System Manager
        frappe.set_user('manager@smriti.com')
        manager_registry = get_document_registry()
        
        # Verify Governance docs are hidden for Store Manager
        self.assertNotIn("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION", manager_registry)
        self.assertNotIn("AI_CONTENT_POLICY", manager_registry)
        
        # Verify direct file read raises PermissionError for Store Manager
        with self.assertRaises(frappe.PermissionError):
            get_manual_html("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION")
            
        # Verify search does not return governance results for Store Manager
        manager_search = search_knowledge("Branding")
        for res in manager_search:
            self.assertNotEqual(res.get("type"), "Governance")
            self.assertNotEqual(res.get("metadata", {}).get("visibility"), "admin")

        # Test as Cashier (cashier@smriti.com)
        frappe.set_user('cashier@smriti.com')
        cashier_registry = get_document_registry()
        
        # Verify Governance docs are hidden for Cashier
        self.assertNotIn("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION", cashier_registry)
        self.assertNotIn("AI_CONTENT_POLICY", cashier_registry)
        
        # Verify direct file read raises PermissionError for Cashier
        with self.assertRaises(frappe.PermissionError):
            get_manual_html("BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION")

        # Reset user back to Administrator
        frappe.set_user('Administrator')

    def test_formula_visibility_permissions(self):
        from smriti_retail_os.services.formula_service import get_formula_detail

        # Create approved test formula
        f_approved = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-F-001",
            "formula_name": "Test Approved Formula",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "formula_expression": "a + b",
        })
        f_approved.insert(ignore_permissions=True)

        # Create draft test formula
        f_draft = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-F-002",
            "formula_name": "Test Draft Formula",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Draft",
            "is_active": 0,
            "effective_date": "2026-06-19",
            "formula_expression": "x + y",
        })
        f_draft.insert(ignore_permissions=True)
        frappe.db.commit()

        # 1. System Manager role can view both
        frappe.set_user('Administrator')
        doc1 = get_formula_detail("TST-F-001")
        doc2 = get_formula_detail("TST-F-002")
        self.assertEqual(doc1.formula_id, "TST-F-001")
        self.assertEqual(doc2.formula_id, "TST-F-002")

        # 2. Store Manager / Cashier cannot view draft formula
        frappe.set_user('cashier@smriti.com')
        # Can view approved
        doc_app = get_formula_detail("TST-F-001")
        self.assertEqual(doc_app.formula_id, "TST-F-001")

        # Cannot view draft
        with self.assertRaises(frappe.PermissionError):
            get_formula_detail("TST-F-002")

        # Cannot view unregistered non-existent formula
        with self.assertRaises(frappe.PermissionError):
            get_formula_detail("NON-EXISTENT")

        # Reset user
        frappe.set_user('Administrator')

    def test_formula_link_interception(self):
        from smriti_retail_os.api.help_api import get_manual_html
        
        frappe.set_user('Administrator')
        html_content = get_manual_html("volume_2_manager_guide")
        
        # Verify that the manual HTML compiles with the explicit formula: URI scheme
        self.assertIn('href="formula:INV-002"', html_content)
        self.assertIn('href="formula:INV-003"', html_content)
        self.assertIn('href="formula:INV-001"', html_content)
        self.assertIn('href="formula:INV-004"', html_content)
        self.assertIn('href="formula:TRF-001"', html_content)

    def test_dynamic_registry_scan(self):
        from smriti_retail_os.services.knowledge_service import get_assets
        from smriti_retail_os.api.help_api import get_document_registry

        # Ensure dynamic assets are discovered
        assets = get_assets(module="PSV", category="Enablement")
        self.assertGreater(len(assets), 0)
        
        # Verify psv_demo_dataset metadata structure
        demo_asset = next((a for a in assets if a["name"] == "psv_demo_dataset"), None)
        self.assertIsNotNone(demo_asset)
        self.assertEqual(demo_asset["category"], "Demo Center")
        self.assertEqual(demo_asset["document_type"], "enablement")

        # Verify certified guide metadata structure
        cert_asset = next((a for a in assets if a["name"] == "psv_certified_planner_guide"), None)
        self.assertIsNotNone(cert_asset)
        self.assertEqual(cert_asset["category"], "Certification")
        self.assertEqual(cert_asset["document_type"], "certification")

        # Verify registry integrates them
        registry = get_document_registry()
        self.assertIn("psv_demo_dataset", registry)
        self.assertIn("psv_certified_planner_guide", registry)

    def test_download_enablement_file(self):
        from smriti_retail_os.api.help_api import download_enablement_file

        # Clean previous responses
        if hasattr(frappe.local, "response"):
            frappe.local.response = frappe._dict()

        frappe.set_user('Administrator')
        download_enablement_file(file_key="psv_demo_dataset")
        
        self.assertEqual(frappe.local.response.filename, "psv_demo_dataset.csv")
        self.assertEqual(frappe.local.response.type, "download")
        self.assertIsNotNone(frappe.local.response.filecontent)

        # Test ZIP bundle generation
        frappe.local.response = frappe._dict()
        download_enablement_file(file_key="zip_bundle")
        self.assertEqual(frappe.local.response.filename, "SMRITI_PSV_Enablement_Pack.zip")
        self.assertEqual(frappe.local.response.type, "download")
        self.assertIsNotNone(frappe.local.response.filecontent)

    def test_download_enablement_file_security(self):
        from smriti_retail_os.api.help_api import download_enablement_file

        # 1. Non-permitted role (Guest)
        frappe.set_user('Guest')
        with self.assertRaises(frappe.PermissionError):
            download_enablement_file(file_key="psv_demo_dataset")

        # 2. Path Traversal checking using directory traversal sequences
        frappe.set_user('Administrator')
        
        # Using bad key formats
        with self.assertRaises(frappe.ValidationError):
            download_enablement_file(file_key="../etc/passwd")

        with self.assertRaises(frappe.ValidationError):
            download_enablement_file(file_key="..\\..\\boot.py")

        # Let's mock a registered asset containing path traversal to test realpath containment check
        from smriti_retail_os.api.help_api import DOCUMENT_REGISTRY
        original_registry = DOCUMENT_REGISTRY.copy()
        try:
            # Inject malicious asset
            DOCUMENT_REGISTRY["malicious_asset"] = {
                "name": "malicious_asset",
                "title": "Malicious",
                "document_type": "enablement",
                "file_name": "../../boot.py" # Traversal filename but without path markers in file_key
            }
            # This should raise ValidationError due to filename checks
            with self.assertRaises(frappe.ValidationError):
                download_enablement_file(file_key="malicious_asset")
        finally:
            # Restore registry
            import smriti_retail_os.api.help_api
            smriti_retail_os.api.help_api.DOCUMENT_REGISTRY = original_registry

    def test_routing_redirects(self):
        from smriti_retail_os.boot import check_desk_access
        import werkzeug.routing.exceptions

        # Mock request path
        original_request = getattr(frappe.local, "request", None)
        
        class MockRequest:
            def __init__(self, path):
                self.path = path
                self.cookies = {}

        try:
            frappe.local.request = MockRequest(path="/app/knowledge-center/psv")
            with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect) as context:
                check_desk_access()
            self.assertEqual(context.exception.new_url, "/smriti-help?tab=enablement")

            frappe.local.request = MockRequest(path="/enablement/psv/")
            with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect) as context:
                check_desk_access()
            self.assertEqual(context.exception.new_url, "/smriti-help?tab=enablement")
        finally:
            frappe.local.request = original_request

    def test_exam_attempt_workflow(self):
        from smriti_retail_os.api.help_api import start_psv_exam, submit_psv_exam
        
        # 1. Start exam
        frappe.set_user('Administrator')
        res = start_psv_exam(exam_id="level_1")
        self.assertEqual(res["status"], "In Progress")
        self.assertIsNotNone(res["attempt_id"])
        self.assertGreater(len(res["questions"]), 0)
        
        # 2. Check that answers are omitted in start payload
        for q in res["questions"]:
            self.assertNotIn("answer", q)
            self.assertNotIn("correct_answer", q)
            
        # 3. Submit exam with correct answers (from guide parsing to get 100% score)
        from smriti_retail_os.api.help_api import _parse_answer_key
        answer_key = _parse_answer_key("psv_certified_planner_guide")
        
        # Format submission
        answers_json = json.dumps({str(k): v for k, v in answer_key.items()})
        sub_res = submit_psv_exam(attempt_id=res["attempt_id"], answers_json=answers_json)
        
        self.assertEqual(sub_res["status"], "Passed")
        self.assertEqual(sub_res["score"], 100.0)
        self.assertIsNotNone(sub_res["certificate_hash"])
        
        # Reset user
        frappe.set_user('Administrator')

    def test_single_active_attempt_enforcement(self):
        from smriti_retail_os.api.help_api import start_psv_exam
        frappe.set_user('Administrator')
        
        # First attempt starts successfully
        res1 = start_psv_exam(exam_id="level_1")
        self.assertEqual(res1["status"], "In Progress")
        
        # Second attempt should return the active attempt
        res2 = start_psv_exam(exam_id="level_1")
        self.assertEqual(res2["attempt_id"], res1["attempt_id"])
        self.assertEqual(res2["status"], "In Progress")

        # Let's try creating a document directly to test block in validate() hook
        from frappe.exceptions import ValidationError
        attempt_doc = frappe.get_doc({
            "doctype": "SMRITI PSV Exam Attempt",
            "user": frappe.session.user,
            "exam_id": "level_1",
            "start_time": frappe.utils.now_datetime(),
            "status": "In Progress"
        })
        with self.assertRaises(ValidationError):
            attempt_doc.insert()

        frappe.set_user('Administrator')

    def test_cheat_prevention_answer_omission(self):
        from smriti_retail_os.api.help_api import start_psv_exam
        frappe.set_user('Administrator')
        res = start_psv_exam(exam_id="level_1")
        for q in res["questions"]:
            self.assertNotIn("answer", q)
            self.assertNotIn("correct_answer", q)
            self.assertNotIn("correct", q)

    def test_time_limit_expiration(self):
        from smriti_retail_os.api.help_api import submit_psv_exam
        frappe.set_user('Administrator')
        
        # Create an attempt that is already expired (e.g. 65 minutes ago)
        from datetime import timedelta
        start_time = frappe.utils.now_datetime() - timedelta(minutes=65)
        
        attempt = frappe.get_doc({
            "doctype": "SMRITI PSV Exam Attempt",
            "user": frappe.session.user,
            "exam_id": "level_1",
            "start_time": start_time,
            "status": "In Progress"
        })
        attempt.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Submit this expired attempt
        res = submit_psv_exam(attempt_id=attempt.name, answers_json=json.dumps({"1": "A"}))
        self.assertEqual(res["status"], "Failed")
        self.assertEqual(res["score"], 0.0)
        self.assertIn("time limit", res["reason"].lower())

    def test_certificate_verification_hash(self):
        from smriti_retail_os.api.help_api import start_psv_exam, submit_psv_exam, verify_psv_certificate
        frappe.set_user('Administrator')
        
        res = start_psv_exam(exam_id="level_1")
        from smriti_retail_os.api.help_api import _parse_answer_key
        answer_key = _parse_answer_key("psv_certified_planner_guide")
        answers_json = json.dumps({str(k): v for k, v in answer_key.items()})
        sub_res = submit_psv_exam(attempt_id=res["attempt_id"], answers_json=answers_json)
        
        cert_hash = sub_res["certificate_hash"]
        self.assertIsNotNone(cert_hash)
        
        # Call verification endpoint
        verify_res = verify_psv_certificate(certificate_hash=cert_hash)
        self.assertTrue(verify_res["valid"])
        self.assertEqual(verify_res["attempt_id"], res["attempt_id"])
        self.assertEqual(verify_res["score"], 100.0)
        
        # Check invalid hash
        verify_res_bad = verify_psv_certificate(certificate_hash="invalid_hash_code_here")
        self.assertFalse(verify_res_bad["valid"])
        self.assertIn("invalid", verify_res_bad["error"].lower())




