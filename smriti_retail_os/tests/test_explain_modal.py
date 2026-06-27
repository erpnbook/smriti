# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_explain_modal.py
# @description: Unit tests for SMRITI Explain Engine — ⓘ modal content verification.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import json
import unittest
import frappe
from smriti_retail_os.api.explain_api import get_explain_payload

class TestExplainModal(unittest.TestCase):
    def setUp(self):
        # Ensure we have our test formula
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": "TST-EXP-001"})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": "TST-EXP-001"})
        frappe.db.commit()

        # Insert a dummy active and approved formula
        self.doc = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-EXP-001",
            "formula_name": "Test Explain Metric",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "formula_expression": "{x} / {y}",
            "business_meaning": "Test explain meaning",
            "worked_example": "80 / 20 = 4",
            "interpretation_guide": "High score is good",
            "recommended_action": "Check inventory",
            "implementation_reference": "services/optimization_service.py",
            "dependent_features": json.dumps(["Test Feature"]),
            "explainability_json": json.dumps({
                "related_training_lesson": "TRN-TST-001",
                "related_manual_section": "Volume 3 > Test Section",
                "related_dictionary_term": "Test Metric Term"
            })
        })
        self.doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Clean Redis cache for test key
        cache_key = "smriti:explain:TST-EXP-001:1.0.0"
        frappe.cache().delete_value(cache_key)

    def tearDown(self):
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": "TST-EXP-001"})
        frappe.db.delete("SMRITI PSV Activity Log", {"reference_name": "TST-EXP-001"})
        frappe.db.commit()

        cache_key = "smriti:explain:TST-EXP-001:1.0.0"
        frappe.cache().delete_value(cache_key)

    def test_explain_payload_generation(self):
        # 1. Test payload fetching (Cache Miss first)
        payload = get_explain_payload(formula_id="TST-EXP-001")
        self.assertEqual(payload["formula_id"], "TST-EXP-001")
        self.assertEqual(payload["formula_version"], "1.0.0")
        self.assertEqual(payload["formula_category"], "Inventory")
        self.assertEqual(payload["business_owner"], "Jawahar R. Mallah")
        self.assertEqual(payload["explainability_json"]["related_training_lesson"], "TRN-TST-001")

        # Check if audit log was written
        logs = frappe.get_all(
            "SMRITI PSV Activity Log",
            filters={"reference_name": "TST-EXP-001"},
            fields=["action_type", "event_type", "details"]
        )
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["action_type"], "Formula Explained")
        self.assertEqual(logs[0]["event_type"], "FORMULA_EXPLAINED")
        self.assertIn("Version: 1.0.0", logs[0]["details"])

    def test_explain_caching_and_cache_hits(self):
        cache_key = "smriti:explain:TST-EXP-001:1.0.0"
        self.assertIsNone(frappe.cache().get_value(cache_key))

        # First call - cache miss, populates cache
        payload_1 = get_explain_payload(formula_id="TST-EXP-001")
        
        # Redis cache key should now exist
        cached = frappe.cache().get_value(cache_key)
        self.assertIsNotNone(cached)
        cached_payload = json.loads(cached)
        self.assertEqual(cached_payload["formula_id"], "TST-EXP-001")

        # Second call - cache hit
        payload_2 = get_explain_payload(formula_id="TST-EXP-001")
        self.assertEqual(payload_2["formula_id"], "TST-EXP-001")

        # Audit logs should show 2 entries (one for each hit/miss)
        logs = frappe.get_all(
            "SMRITI PSV Activity Log",
            filters={"reference_name": "TST-EXP-001"},
            fields=["action_type", "event_type"]
        )
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["event_type"], "FORMULA_EXPLAINED")
        self.assertEqual(logs[1]["event_type"], "FORMULA_EXPLAINED")
