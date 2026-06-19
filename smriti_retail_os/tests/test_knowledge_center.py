# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_knowledge_center.py
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
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002", "TST-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001", "TST-F-002", "TST-RANK-MATCH"]]})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": ["in", ["TST-T-001", "TST-F-001"]]})
        frappe.db.commit()
        frappe.cache().delete_value(REDIS_INDEX_KEY)

    def tearDown(self):
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002", "TST-RANK-MATCH"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001", "TST-F-002", "TST-RANK-MATCH"]]})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": ["in", ["TST-T-001", "TST-F-001"]]})
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
            "term_id": "TST-RANK-MATCH",
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
            "formula_id": "TST-RANK-MATCH",
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
        self.assertEqual(results[0]["id"], "dict:TST-RANK-MATCH")
        
        # Verify the second is the Formula
        self.assertEqual(results[1]["type"], "Formula Definition")
        self.assertEqual(results[1]["id"], "formula:TST-RANK-MATCH")

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
