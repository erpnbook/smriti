# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_status_sentinel.py
# @description: Unit & Integration tests for SMRITI Status Sentinel (S³).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import json
import os
import shutil
import tempfile
import threading
import time
import unittest

from smriti_retail_os.status.provider import BaseStatusProvider
from smriti_retail_os.status.registry import StatusSentinelRegistry
from smriti_retail_os.status.providers.maintenance import MaintenanceProvider
from smriti_retail_os.status.providers.migration import MigrationProvider
from smriti_retail_os.status.status_sentinel import resolve_system_status, write_status_atomically


class DeliberateFailureProvider(BaseStatusProvider):
    """
    Mock provider designed to raise a deliberate execution failure.
    """
    @property
    def name(self):
        return "faulty_provider"

    def get_status(self, site_path):
        raise RuntimeError("Deliberate status aggregation failure.")


class TestStatusSentinel(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_provider_isolation(self):
        """
        Verify Rule 5 (Provider Isolation): A failure in one provider
        must never crash the sentinel execution or aggregate crash.
        """
        registry = StatusSentinelRegistry()
        registry.register(DeliberateFailureProvider())
        
        # Add a healthy mock provider
        class HealthyProvider(BaseStatusProvider):
            @property
            def name(self): return "healthy_provider"
            def get_status(self, path):
                return {
                    "provider": self.name,
                    "status": "ok",
                    "updated_at": self._get_utc_timestamp(),
                    "data": {"working": True}
                }
        registry.register(HealthyProvider())

        # Execute
        results = registry.execute_all(self.temp_dir)

        # Check results
        self.assertIn("healthy_provider", results)
        self.assertEqual(results["healthy_provider"]["status"], "ok")

        self.assertIn("faulty_provider", results)
        self.assertEqual(results["faulty_provider"]["status"], "error")
        self.assertIn("Deliberate status aggregation failure", results["faulty_provider"]["data"]["error"])

    def test_precedence_logic(self):
        """
        Verify status resolution precedence: Migration > Maintenance > ReadOnly > Online.
        """
        # 1. Base online state
        results = {
            "migration": {"data": {"active": False}},
            "maintenance": {"data": {"active": False}},
            "readonly": {"data": {"active": False}}
        }
        self.assertEqual(resolve_system_status(results), "online")

        # 2. Add ReadOnly
        results["readonly"]["data"]["active"] = True
        self.assertEqual(resolve_system_status(results), "readonly")

        # 3. Add Maintenance (should override ReadOnly)
        results["maintenance"]["data"]["active"] = True
        self.assertEqual(resolve_system_status(results), "maintenance")

        # 4. Add Migration (should override Maintenance)
        results["migration"]["data"]["active"] = True
        self.assertEqual(resolve_system_status(results), "migration")

    def test_lock_corruption_handling(self):
        """
        Verify that corrupted/unparseable lock files do not crash providers
        and degrade gracefully by keeping the lock active with a warning status.
        """
        maint_provider = MaintenanceProvider()
        mig_provider = MigrationProvider()

        # Write corrupt lock files
        maint_lock = os.path.join(self.temp_dir, "maintenance.lock")
        mig_lock = os.path.join(self.temp_dir, "migration.lock")

        with open(maint_lock, "w") as f:
            f.write("%%% INVALID JSON %%%")
        with open(mig_lock, "w") as f:
            f.write("%%% INVALID JSON %%%")

        # Execute providers
        maint_res = maint_provider.get_status(self.temp_dir)
        mig_res = mig_provider.get_status(self.temp_dir)

        # Verify Maintenance degradation
        self.assertEqual(maint_res["status"], "warning")
        self.assertTrue(maint_res["data"]["active"])
        self.assertEqual(maint_res["data"]["reason"], "Scheduled Update (Corrupt Lock File)")

        # Verify Migration degradation
        self.assertEqual(mig_res["status"], "warning")
        self.assertTrue(mig_res["data"]["active"])
        self.assertEqual(mig_res["data"]["reason"], "Schema Migrations (Corrupt Lock File)")
        self.assertEqual(mig_res["data"]["progress_pct"], 0)

    def test_atomic_writes(self):
        """
        Verify that atomic writes prevent intermediate partial reads.
        """
        output_file = os.path.join(self.temp_dir, "status_sentinel.json")
        payload = {"dummy": "value" * 100}

        stop_event = threading.Event()
        errors = []

        def writer_loop():
            # Class fake logger for testing
            class MockLogger:
                def info(self, *args, **kwargs): pass
                def error(self, *args, **kwargs): pass
            logger = MockLogger()
            
            while not stop_event.is_set():
                write_status_atomically(output_file, payload, logger)
                time.sleep(0.001)

        def reader_loop():
            for _ in range(500):
                if os.path.exists(output_file):
                    try:
                        with open(output_file, "r") as f:
                            data = json.load(f)
                            if data.get("dummy") != payload["dummy"]:
                                errors.append("Mismatch in read data payload")
                    except Exception as e:
                        errors.append(f"Failed to read/parse status JSON: {e}")
                time.sleep(0.001)

        # Start loops
        writer_thread = threading.Thread(target=writer_loop)
        writer_thread.start()

        # Run reader
        reader_loop()

        # Stop writer
        stop_event.set()
        writer_thread.join()

        # Verify no read errors occurred
        self.assertEqual(len(errors), 0, f"Atomic read errors found: {errors}")

    def test_missing_output_folder(self):
        """
        Verify S3 creates the output folder dynamically if it does not exist.
        """
        nested_dir = os.path.join(self.temp_dir, "nested", "status")
        output_file = os.path.join(nested_dir, "status_sentinel.json")
        payload = {"test": "data"}
        
        class MockLogger:
            def info(self, *args, **kwargs): pass
            def error(self, *args, **kwargs): pass

        # Folder does not exist initially
        self.assertFalse(os.path.exists(nested_dir))
        
        # Write atomically
        write_status_atomically(output_file, payload, MockLogger())
        
        # Verify it created directory and wrote the file
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r") as f:
            self.assertEqual(json.load(f)["test"], "data")

    def test_unwriteable_output_file(self):
        """
        Verify S3 handles permission/write errors gracefully without crashing the CLI runner.
        """
        # Setup standard mock logger to capture warning message
        logs = []
        class MockLogger:
            def info(self, *args, **kwargs): pass
            def debug(self, *args, **kwargs): pass
            def warning(self, *args, **kwargs): pass
            def error(self, msg, *args, **kwargs):
                logs.append(msg % args)

        # Import and run S3 runner code on dummy site path (which should raise error writing output)
        from smriti_retail_os.status import status_sentinel
        # Mock status_sentinel.bench_root to point to our temp folder so it writes to temp_dir
        original_bench_root = status_sentinel.bench_root
        status_sentinel.bench_root = self.temp_dir
        
        # Ensure we have a dummy site directory structure under temp_dir for run() to pass check
        dummy_site_path = os.path.join(self.temp_dir, "sites", "smriti_retail")
        os.makedirs(dummy_site_path, exist_ok=True)
        
        # Mock write_status_atomically to raise PermissionError
        original_write = status_sentinel.write_status_atomically
        def faulty_write(*args, **kwargs):
            raise PermissionError("Mocked Permission Denied")
        status_sentinel.write_status_atomically = faulty_write
        
        try:
            # Running S3 should catch exception and log it without crashing
            original_setup_logging = status_sentinel.setup_logging
            status_sentinel.setup_logging = lambda: MockLogger()
            
            status_sentinel.run(site="smriti_retail")
            
            # Verify S3 caught error and logged it
            self.assertTrue(any("Failed to write telemetry output" in log for log in logs), f"Expected write failure log: {logs}")
        finally:
            status_sentinel.write_status_atomically = original_write
            status_sentinel.bench_root = original_bench_root
            status_sentinel.setup_logging = original_setup_logging


if __name__ == "__main__":
    unittest.main()
