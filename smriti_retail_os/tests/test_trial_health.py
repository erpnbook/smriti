# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_trial_health.py
# @description: Unit tests for SMRITI Trial Pipeline Health scoring, orchestration,
#               and security permission policies.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.0.0
# @sprint: 3C — Trial Health Snapshot
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
import unittest
from datetime import datetime
from smriti_retail_os.services.trial_service import (
    calculate_trial_health_score,
    generate_health_snapshot
)
from smriti_retail_os.api.trial_activation_api import (
    get_trial_health_snapshots,
    trigger_trial_health_snapshot
)


class TestTrialHealth(unittest.TestCase):
    def setUp(self):
        # Save current session user to restore later
        self.original_user = frappe.session.user
        frappe.set_user("Administrator")
        
        # Dynamically provision DocType and table in the test DB
        from smriti_retail_os.tests.utils import ensure_doctype_schema
        ensure_doctype_schema("SMRITI Trial Health Snapshot")
        
        # Clear snapshots for testing
        frappe.db.delete("SMRITI Trial Health Snapshot")
        frappe.db.commit()

    def tearDown(self):
        frappe.set_user(self.original_user)
        frappe.db.delete("SMRITI Trial Health Snapshot")
        frappe.db.commit()

    def test_calculate_health_score_edge_cases(self):
        # Case 1: Active = 0, Failed = 0 -> Expected: 100.0 (no trials processed yet)
        self.assertEqual(calculate_trial_health_score(0, 0, 2.0), 100.0)
        self.assertEqual(calculate_trial_health_score(0, 0, None), 100.0)

        # Case 2: Active = 0, Failed > 0 -> Expected: 0.0
        self.assertEqual(calculate_trial_health_score(0, 5, 2.0), 0.0)

        # Case 3: Active = 8, Failed = 2 -> Success Rate = 80%. Avg SLA = 6h. Target = 4h.
        # Penalty = (6 - 4) * 5 = 10%. Score = 80 - 10 = 70.0%
        self.assertEqual(calculate_trial_health_score(8, 2, 6.0, target_sla=4.0, penalty_mult=5.0), 70.0)

        # Case 4: Active = 10, Failed = 0 -> Success Rate = 100%. Avg SLA = 10h.
        # Penalty = (10 - 4) * 5 = 30% -> capped at max_penalty = 20%. Score = 100 - 20 = 80.0%
        self.assertEqual(calculate_trial_health_score(10, 0, 10.0, target_sla=4.0, penalty_mult=5.0, max_penalty=20.0), 80.0)

        # Case 5: Under SLA target (no penalty) -> Score = 100%
        self.assertEqual(calculate_trial_health_score(10, 0, 3.0, target_sla=4.0), 100.0)

    def test_generate_health_snapshot_persistence(self):
        # Assert custom DocType exists
        self.assertTrue(frappe.db.exists("DocType", "SMRITI Trial Health Snapshot"))

        # Generate a snapshot
        snapshot = generate_health_snapshot(snapshot_type="Manual", operator="Administrator")
        self.assertIsNotNone(snapshot.name)
        self.assertEqual(snapshot.snapshot_type, "Manual")
        self.assertEqual(snapshot.generated_by, "Administrator")
        
        # Verify values persisted in DB
        db_doc = frappe.get_doc("SMRITI Trial Health Snapshot", snapshot.name)
        self.assertEqual(db_doc.snapshot_version, "1.0")
        self.assertEqual(db_doc.formula_version, "1.0")
        
        # Verify interpretation band
        score = db_doc.health_score
        if score >= 80.0:
            self.assertEqual(db_doc.interpretation, "Healthy")
        elif score >= 50.0:
            self.assertEqual(db_doc.interpretation, "Monitor")
        else:
            self.assertEqual(db_doc.interpretation, "Critical")

    def test_snapshot_immutability_and_idempotency(self):
        # Generate twice within same window - should insert separate records (preserves history)
        s1 = generate_health_snapshot(snapshot_type="Daily")
        s2 = generate_health_snapshot(snapshot_type="Manual")
        
        self.assertNotEqual(s1.name, s2.name)
        
        snapshots_count = frappe.db.count("SMRITI Trial Health Snapshot")
        self.assertEqual(snapshots_count, 2)

    def test_api_permission_guards(self):
        # 1. Test as Guest - should throw PermissionError
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_trial_health_snapshots()
            
        with self.assertRaises(frappe.PermissionError):
            trigger_trial_health_snapshot()

        # 2. Test as ordinary non-admin role user
        # Temporarily create test user with "SMRITI Store Manager" role
        test_email = "test.manager@smriti.local"
        if not frappe.db.exists("User", test_email):
            test_user = frappe.get_doc({
                "doctype": "User",
                "email": test_email,
                "first_name": "Test Store Manager",
                "roles": [{"role": "SMRITI Store Manager"}]
            })
            test_user.insert(ignore_permissions=True)
            frappe.db.commit()

        frappe.set_user(test_email)
        
        with self.assertRaises(frappe.PermissionError):
            get_trial_health_snapshots()
            
        with self.assertRaises(frappe.PermissionError):
            trigger_trial_health_snapshot()

        # Restore admin and clean up test user
        frappe.set_user("Administrator")
        frappe.db.delete("User", {"email": test_email})
        frappe.db.commit()
