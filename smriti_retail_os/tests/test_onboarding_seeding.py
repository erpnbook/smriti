# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_onboarding_seeding.py
# @description: Automated test for SMRITI onboarding and setup seeding verification.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import unittest
import frappe
from smriti_retail_os import smriti
from smriti_retail_os.setup import setup_smriti_retail_os

class TestOnboardingSeeding(unittest.TestCase):
    def setUp(self):
        frappe.set_user('Administrator')

    def test_seeding_and_idempotency(self):
        """
        Verify that:
        1. SMRITI Formula Definitions and Business Terms are automatically populated.
        2. Seeding execution is idempotent (consecutive executions create no duplicate records).
        """
        # Phase 1: Clean up existing seeded records to test a fresh install state
        smriti.db.delete("SMRITI Related Formula")
        smriti.db.delete("SMRITI Related Term")
        smriti.db.delete("SMRITI Business Term")
        smriti.db.delete("SMRITI Formula Definition")
        smriti.db.commit()

        # Verify tables are empty
        self.assertEqual(smriti.db.count("SMRITI Formula Definition"), 0)
        self.assertEqual(smriti.db.count("SMRITI Business Term"), 0)

        # Phase 2: Run setup function (simulating a fresh install)
        setup_smriti_retail_os()
        
        formula_count_1 = smriti.db.count("SMRITI Formula Definition")
        term_count_1 = smriti.db.count("SMRITI Business Term")

        # Verify that default records were created
        self.assertGreater(formula_count_1, 0, "Formula definitions were not seeded.")
        self.assertGreater(term_count_1, 0, "Business terms were not seeded.")
        self.assertEqual(formula_count_1, 14, f"Expected 14 formulas, found {formula_count_1}")
        self.assertEqual(term_count_1, 52, f"Expected 52 terms, found {term_count_1}")

        # Phase 3: Run setup function a second time (simulating a subsequent migration/update)
        setup_smriti_retail_os()

        formula_count_2 = smriti.db.count("SMRITI Formula Definition")
        term_count_2 = smriti.db.count("SMRITI Business Term")

        # Verify that counts are identical (proving idempotency)
        self.assertEqual(formula_count_1, formula_count_2, "Duplicate formula definitions were created on second run.")
        self.assertEqual(term_count_1, term_count_2, "Duplicate business terms were created on second run.")
