# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_business_dictionary.py
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

import json
import unittest
import frappe
from smriti_retail_os.services.dictionary_service import get_active_terms, get_term_detail

class TestBusinessDictionary(unittest.TestCase):
    def setUp(self):
        # Clean up test terms to avoid collision
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST-BD-001"})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": "TST-BD-001"})
        frappe.db.commit()

        # Ensure KGF-001 formula exists for link testing
        formula_doc_name = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": "KGF-001"})
        if not formula_doc_name:
            mock_formula = frappe.get_doc({
                "doctype": "SMRITI Formula Definition",
                "formula_id": "KGF-001",
                "formula_name": "Test Formula",
                "formula_category": "Inventory",
                "formula_version": "1.0.0",
                "status": "Approved",
                "is_active": 1,
                "effective_date": "2026-06-19",
                "formula_meaning": "Test meaning",
                "display_formula": "A / B",
                "formula_language": "documentation"
            })
            mock_formula.insert(ignore_permissions=True)
            formula_doc_name = mock_formula.name
            frappe.db.commit()

        # Seed child table records
        self.doc = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-BD-001",
            "term_name": "Test Dictionary Term",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "Test dictionary definition text.",
            "hinglish_definition": "Test dictionary Hinglish explanation.",
            "term_aliases": json.dumps(["Test Alias", "TST"]),
            "faq": json.dumps([{"q": "What is this?", "a": "A test term."}]),
            "common_mistakes": json.dumps([{"mistake": "Using wrong ID", "a": "Always use TST-BD-001."}]),
            "manual_reference": "Volume 3 > Test Manual",
            "training_reference": "TRN-TST-BD",
            "related_formulas": [{"doctype": "SMRITI Related Formula", "formula_id": formula_doc_name}],
            "related_terms": []
        })
        self.doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Clean Redis cache
        cache_key = "smriti:dictionary:TST-BD-001:1.0.0"
        frappe.cache().delete_value(cache_key)

    def tearDown(self):
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST-BD-001"})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": "TST-BD-001"})
        frappe.db.commit()

        cache_key = "smriti:dictionary:TST-BD-001:1.0.0"
        frappe.cache().delete_value(cache_key)

    def test_schema_and_validation(self):
        # 1. Assert DocType exists
        self.assertTrue(frappe.db.exists("DocType", "SMRITI Business Term"))

        # 2. Duplicate term_id + term_version throws ValidationError
        dup = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-BD-001",
            "term_name": "Duplicate Term",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "Duplicate definition.",
            "hinglish_definition": "Duplicate Hinglish."
        })
        self.assertRaises(frappe.ValidationError, dup.insert, ignore_permissions=True)

        # 3. Non-approved term cannot be active
        draft_doc = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-BD-001",
            "term_name": "Draft Term",
            "term_category": "Inventory",
            "term_version": "2.0.0",
            "status": "Draft",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "definition": "Draft definition.",
            "hinglish_definition": "Draft Hinglish."
        })
        self.assertRaises(frappe.ValidationError, draft_doc.insert, ignore_permissions=True)

        # 4. JSON field validators
        draft_doc.is_active = 0
        draft_doc.term_aliases = "{malformed"
        self.assertRaises(frappe.ValidationError, draft_doc.insert, ignore_permissions=True)

    def test_dictionary_caching_and_audit(self):
        # Cache Miss
        cache_key = "smriti:dictionary:TST-BD-001:1.0.0"
        self.assertIsNone(frappe.cache().get_value(cache_key))

        payload = get_term_detail("TST-BD-001")
        self.assertEqual(payload["term_id"], "TST-BD-001")
        self.assertEqual(payload["term_category"], "Inventory")
        self.assertIn("KGF-001", payload["related_formulas"])

        # Cache should now be populated
        cached = frappe.cache().get_value(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(json.loads(cached)["term_name"], "Test Dictionary Term")

        # Cache Hit
        payload_2 = get_term_detail("TST-BD-001")
        self.assertEqual(payload_2["term_name"], "Test Dictionary Term")

        # Audit logs should record 2 accesses
        logs = frappe.get_all(
            "SMRITI PSV Activity Log",
            filters={"reference_name": "TST-BD-001"},
            fields=["action_type", "event_type", "details"]
        )
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["action_type"], "Dictionary Accessed")
        self.assertEqual(logs[0]["event_type"], "DICTIONARY_ACCESSED")
        self.assertIn("Version: 1.0.0", logs[0]["details"])

    def test_seeded_terms(self):
        # Run seeding manually to ensure they exist
        from smriti_retail_os.patches.seed_default_terms import execute as seed_terms
        seed_terms()

        # Check a few core seeded terms
        core_terms = ["PSA", "PSV", "PDT", "WOC", "Dead Stock", "Variant Curve"]
        for tid in core_terms:
            self.assertTrue(
                frappe.db.exists("SMRITI Business Term", {"term_id": tid, "is_active": 1}),
                f"Default term {tid} was not seeded."
            )

        # Check PDT related formulas link has FRC-001
        pdt_detail = get_term_detail("PDT")
        self.assertIn("FRC-001", pdt_detail["related_formulas"])
        self.assertIn("WOC", pdt_detail["related_terms"])
