# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_ai_context.py
# @description: Unit tests for SMRITI AI Context Builder & LLM Integration (Sprint SDC-004)
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import unittest
import frappe
from smriti_retail_os.services import ai_context_service
from smriti_retail_os.api import ai_integration_api

class TestAIContext(unittest.TestCase):
    def test_build_context_pack_empty(self):
        """Assert empty query returns an error."""
        res = ai_context_service.build_context_pack("")
        self.assertIn("ERROR: Query string cannot be empty", res)

    def test_build_context_pack_nonexistent(self):
        """Assert nonexistent query returns a warning."""
        res = ai_context_service.build_context_pack("NonexistentQueryXYZ")
        self.assertIn("WARNING: No primary knowledge objects resolved", res)
        self.assertIn("=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===", res)

    def test_build_context_pack_valid(self):
        """Assert valid query resolves correctly and contains SKE headers."""
        # Querying for 'woc' should resolve some objects
        res = ai_context_service.build_context_pack("woc")
        self.assertIn("=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===", res)
        self.assertIn("SKE Version: 1.1.2-GA", res)
        self.assertIn("PRIMARY KNOWLEDGE OBJECTS RESOLVED:", res)

    def test_explain_decision_context(self):
        """Assert explain_decision_context returns error with empty arguments."""
        res1 = ai_context_service.explain_decision_context("", "WOC-01")
        self.assertIn("ERROR", res1)
        res2 = ai_context_service.explain_decision_context("Formula", "")
        self.assertIn("ERROR", res2)

    def test_api_get_ai_context(self):
        """Test whitelisted API get_ai_context."""
        res = ai_integration_api.get_ai_context("woc")
        self.assertIn("=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===", res)

    def test_api_ask_smriti_ai_barcode(self):
        """Test ask_smriti_ai with barcode queries."""
        res = ai_integration_api.ask_smriti_ai("Explain barcode")
        self.assertIn("answer", res)
        self.assertIn("context_pack", res)
        self.assertIn("evidence_badge", res)
        self.assertIn("print_job_id", res["answer"])
        self.assertIn("warehouse_id", res["answer"])

    def test_api_ask_smriti_ai_woc(self):
        """Test ask_smriti_ai with WOC queries."""
        res = ai_integration_api.ask_smriti_ai("What is Weeks of Cover?")
        self.assertIn("answer", res)
        self.assertIn("context_pack", res)
        self.assertIn("evidence_badge", res)
        self.assertIn("WOC = Current Stock", res["answer"])

    def test_api_ask_smriti_ai_psv(self):
        """Test ask_smriti_ai with PSV queries."""
        res = ai_integration_api.ask_smriti_ai("Tell me about PSV visibility")
        self.assertIn("answer", res)
        self.assertIn("context_pack", res)
        self.assertIn("evidence_badge", res)
        self.assertIn("Inventory Visibility Layer", res["answer"])

    def test_api_ask_smriti_ai_unverified(self):
        """Test ask_smriti_ai safety fallback with unverified queries."""
        res = ai_integration_api.ask_smriti_ai("What is the weather in Delhi?")
        self.assertIn("answer", res)
        self.assertIn("context_pack", res)
        self.assertIn("evidence_badge", res)
        self.assertIn("restricted from answering queries that lack ground-truth", res["answer"])
        self.assertIn("❌ Unverified", res["evidence_badge"])
