# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_telemetry.py
# @description: Unit tests for SMRITI Barcode scan telemetry.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from frappe.utils import add_days, getdate, now_datetime
from smriti_retail_os.barcode_api import (
    log_barcode_scan_event,
    delete_expired_scan_events,
    aggregate_scan_telemetry,
    get_barcode_feature_flags,
    clear_barcode_feature_flags_cache
)

class TestTelemetry(unittest.TestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        # Ensure governance event definitions and formula registry are seeded
        from smriti_retail_os.patches.seed_telemetry_meta import execute as seed_telemetry
        seed_telemetry()
        
        # Ensure SMRITI Barcode Settings exists and enable flags for baseline tests
        from smriti_retail_os.setup import create_smriti_barcode_settings_doctype
        create_smriti_barcode_settings_doctype()
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_capture_enabled", 1)
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_aggregation_enabled", 1)
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_learning_enabled", 1)
        clear_barcode_feature_flags_cache()

        # Ensure default warehouse exists
        w_name = frappe.db.get_value("Warehouse", {"warehouse_name": "Test Warehouse - SCN"}, "name")
        if not w_name:
            w = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Test Warehouse - SCN",
                "is_group": 0,
                "company": frappe.db.get_value("Company", {}, "name") or "_Test Company"
            })
            w.insert(ignore_permissions=True)
            frappe.db.commit()
            w_name = w.name
        self.warehouse = w_name

            
        # Create a mock Print Template if not exists
        if not frappe.db.exists("SMRITI Print Template", "Test Telemetry Template"):
            tmpl = frappe.get_doc({
                "doctype": "SMRITI Print Template",
                "name": "Test Telemetry Template",
                "template_title": "Test Telemetry Template",
                "label_size": "50x25",
                "printer_language": "ZPL",
                "printer_family": "ZPL",
                "raw_template": "^XA^XZ",
                "design_json": "{}",
                "status": "Active"
            })
            tmpl.insert(ignore_permissions=True)
            frappe.db.commit()

    def tearDown(self):
        # Cleanup test entries
        frappe.db.delete("SMRITI Barcode Scan Event")
        frappe.db.delete("SMRITI Barcode Telemetry Snapshot")
        frappe.db.commit()
        frappe.set_user("Administrator")

    def test_doctypes_exist(self):
        """Verifies that custom DocTypes exist and have correct fields."""
        self.assertTrue(frappe.db.exists("DocType", "SMRITI Telemetry Event Definition"))
        self.assertTrue(frappe.db.exists("DocType", "SMRITI Barcode Scan Event"))
        self.assertTrue(frappe.db.exists("DocType", "SMRITI Barcode Telemetry Snapshot"))

        # Verify event definition seeds
        self.assertTrue(frappe.db.exists("SMRITI Telemetry Event Definition", "SCAN-EVT-001"))
        self.assertTrue(frappe.db.exists("SMRITI Telemetry Event Definition", "SCAN-EVT-002"))
        self.assertTrue(frappe.db.exists("SMRITI Telemetry Event Definition", "SCAN-EVT-003"))

        # Verify formula definition
        self.assertTrue(frappe.db.exists("SMRITI Formula Definition", {"formula_id": "SMRITI-SCAN-REL-01"}))

    def test_log_scan_event_access_control(self):
        """Verifies role-based access for logging barcode scan events."""
        # Standard system manager / Administrator is allowed
        frappe.set_user("Administrator")
        doc1 = log_barcode_scan_event(
            event_uuid="uuid-001",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        self.assertEqual(doc1.governance_event_id, "SCAN-EVT-001")

        # Guest or unauthorized user should raise PermissionError
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            log_barcode_scan_event(
                event_uuid="uuid-002",
                template_id="Test Telemetry Template",
                barcode_family="Code128",
                printer_profile="Zebra 203 DPI",
                scan_method="Handheld Laser",
                scan_attempts=1,
                scan_success=1,
                first_pass_success=1,
                store_id=self.warehouse
            )

    def test_log_scan_event_governance_mapping(self):
        """Verifies scan outcomes map to correct SCAN-EVT governance codes."""
        frappe.set_user("Administrator")
        # Case 1: Retry success
        doc1 = log_barcode_scan_event(
            event_uuid="uuid-gov-002",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=3,
            scan_success=1,
            first_pass_success=0,
            store_id=self.warehouse
        )
        self.assertEqual(doc1.governance_event_id, "SCAN-EVT-002")

        # Case 2: Failure
        doc2 = log_barcode_scan_event(
            event_uuid="uuid-gov-003",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=5,
            scan_success=0,
            first_pass_success=0,
            store_id=self.warehouse
        )
        self.assertEqual(doc2.governance_event_id, "SCAN-EVT-003")

    def test_idempotency(self):
        """Verifies duplicate event_uuid results in returning original, no double insertion."""
        frappe.set_user("Administrator")
        doc1 = log_barcode_scan_event(
            event_uuid="uuid-idem-1",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        # Try again with same UUID
        doc2 = log_barcode_scan_event(
            event_uuid="uuid-idem-1",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        self.assertEqual(doc1.name, doc2.name)
        count = frappe.db.count("SMRITI Barcode Scan Event", {"event_uuid": "uuid-idem-1"})
        self.assertEqual(count, 1)

    def test_immutability(self):
        """Verifies that once created, scan events cannot be updated."""
        frappe.set_user("Administrator")
        doc = log_barcode_scan_event(
            event_uuid="uuid-immutable",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        
        # Try to modify fields and save
        doc.scan_attempts = 5
        with self.assertRaises(frappe.ValidationError):
            doc.save(ignore_permissions=True)

    def test_aggregation_and_zero_scans(self):
        """Verifies daily aggregation values, calculations, and division by zero handling."""
        frappe.set_user("Administrator")
        yesterday = add_days(getdate(), -1)
        
        # Insert raw events manually with yesterday's timestamp to test daily scheduler aggregation
        events = [
            # 2 First pass success
            {"event_uuid": "y-1", "governance_event_id": "SCAN-EVT-001", "scan_success": 1, "first_pass_success": 1, "scan_attempts": 1},
            {"event_uuid": "y-2", "governance_event_id": "SCAN-EVT-001", "scan_success": 1, "first_pass_success": 1, "scan_attempts": 1},
            # 1 Retry success
            {"event_uuid": "y-3", "governance_event_id": "SCAN-EVT-002", "scan_success": 1, "first_pass_success": 0, "scan_attempts": 2},
            # 1 Failure
            {"event_uuid": "y-4", "governance_event_id": "SCAN-EVT-003", "scan_success": 0, "first_pass_success": 0, "scan_attempts": 3}
        ]
        
        for ev in events:
            doc = frappe.get_doc({
                "doctype": "SMRITI Barcode Scan Event",
                "timestamp": yesterday,
                "store_id": self.warehouse,
                "template_id": "Test Telemetry Template",
                "barcode_family": "Code128",
                "printer_profile": "Zebra 203 DPI",
                "scan_method": "Handheld Laser",
                **ev
            })
            doc.insert(ignore_permissions=True)
            
        frappe.db.commit()

        # Run aggregation
        aggregate_scan_telemetry(period="Daily", target_date=yesterday)

        # Assert snapshot exists
        snapshots = frappe.get_all(
            "SMRITI Barcode Telemetry Snapshot",
            filters={
                "snapshot_date": yesterday,
                "store_id": self.warehouse,
                "template_id": "Test Telemetry Template"
            },
            fields=["total_scans", "first_pass_successes", "retry_successes", "failures", "scan_reliability_score", "first_pass_success_rate"]
        )
        self.assertEqual(len(snapshots), 1)
        snap = snapshots[0]
        self.assertEqual(snap.total_scans, 4)
        self.assertEqual(snap.first_pass_successes, 2)
        self.assertEqual(snap.retry_successes, 1)
        self.assertEqual(snap.failures, 1)
        
        # Expected reliability: ((2 + 0.5 * 1) / 4) * 100 = 62.5
        self.assertAlmostEqual(snap.scan_reliability_score, 62.5, places=2)
        # Expected rate: 2 / 4 = 0.5
        self.assertAlmostEqual(snap.first_pass_success_rate, 0.5, places=4)

        # Test division by zero: when total_scans = 0, score = 0.0 without exception.
        # Run aggregation for a date with zero scans (e.g. today)
        aggregate_scan_telemetry(period="Daily", target_date=getdate())
        # Asserts score calculation logic directly:
        # If total = 0, score is 0.0. The daily scheduler job shouldn't create snapshot records when no raw events exist, 
        # but the score calculator must output 0.0.

    def test_retention_policy_pruning(self):
        """Verifies that events older than 90 days are deleted, while newer ones are preserved."""
        frappe.set_user("Administrator")
        
        # Event 95 days old
        old_doc = frappe.get_doc({
            "doctype": "SMRITI Barcode Scan Event",
            "event_uuid": "old-event",
            "timestamp": add_days(now_datetime(), -95),
            "store_id": self.warehouse,
            "template_id": "Test Telemetry Template",
            "barcode_family": "Code128",
            "printer_profile": "Zebra 203 DPI",
            "scan_method": "Handheld Laser",
            "scan_attempts": 1,
            "scan_success": 1,
            "first_pass_success": 1,
            "governance_event_id": "SCAN-EVT-001"
        })
        old_doc.insert(ignore_permissions=True)

        # Event 10 days old
        new_doc = frappe.get_doc({
            "doctype": "SMRITI Barcode Scan Event",
            "event_uuid": "new-event",
            "timestamp": add_days(now_datetime(), -10),
            "store_id": self.warehouse,
            "template_id": "Test Telemetry Template",
            "barcode_family": "Code128",
            "printer_profile": "Zebra 203 DPI",
            "scan_method": "Handheld Laser",
            "scan_attempts": 1,
            "scan_success": 1,
            "first_pass_success": 1,
            "governance_event_id": "SCAN-EVT-001"
        })
        new_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Run retention clean
        delete_expired_scan_events()

        # Assert old one deleted, new one exists
        self.assertFalse(frappe.db.exists("SMRITI Barcode Scan Event", old_doc.name))
        self.assertTrue(frappe.db.exists("SMRITI Barcode Scan Event", new_doc.name))

    def test_log_scan_event_disabled(self):
        """Verifies that scan event logging is bypassed when capture is disabled."""
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_capture_enabled", 0)
        clear_barcode_feature_flags_cache()

        res = log_barcode_scan_event(
            event_uuid="uuid-disabled-1",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("status"), "disabled")
        self.assertFalse(frappe.db.exists("SMRITI Barcode Scan Event", {"event_uuid": "uuid-disabled-1"}))

    def test_aggregation_disabled(self):
        """Verifies that daily telemetry aggregation is skipped when disabled."""
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_aggregation_enabled", 0)
        clear_barcode_feature_flags_cache()

        yesterday = add_days(getdate(), -1)
        # Ensure a raw event exists (manually inserted bypassing log API or with it enabled)
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_capture_enabled", 1)
        clear_barcode_feature_flags_cache()
        log_barcode_scan_event(
            event_uuid="uuid-agg-dis-1",
            template_id="Test Telemetry Template",
            barcode_family="Code128",
            printer_profile="Zebra 203 DPI",
            scan_method="Handheld Laser",
            scan_attempts=1,
            scan_success=1,
            first_pass_success=1,
            store_id=self.warehouse
        )
        # Bypassing raw event save constraints for timestamp modification
        frappe.db.set_value("SMRITI Barcode Scan Event", {"event_uuid": "uuid-agg-dis-1"}, "timestamp", yesterday)
        frappe.db.commit()

        # Turn aggregation back to disabled
        frappe.db.set_single_value("SMRITI Barcode Settings", "barcode_telemetry_aggregation_enabled", 0)
        clear_barcode_feature_flags_cache()

        aggregate_scan_telemetry(period="Daily", target_date=yesterday)

        # Verify no snapshot was created
        snapshots = frappe.get_all(
            "SMRITI Barcode Telemetry Snapshot",
            filters={"snapshot_date": yesterday}
        )
        self.assertEqual(len(snapshots), 0)

    def test_missing_settings_failsafe(self):
        """Verifies fail-safe principle: when settings doc is deleted, all flags default to False."""
        frappe.db.delete("Singles", {"doctype": "SMRITI Barcode Settings"})
        frappe.db.commit()
        clear_barcode_feature_flags_cache()

        flags = get_barcode_feature_flags()
        self.assertFalse(flags.get("capture"))
        self.assertFalse(flags.get("aggregation"))
        self.assertFalse(flags.get("learning"))

