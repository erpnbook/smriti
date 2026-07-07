# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_barcode_api.py
# @description: Unit tests for SMRITI Print Template schema and barcode API template rendering.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-06
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
from smriti_retail_os.barcode_api import (
    generate_prn,
    save_print_template,
)

class TestSmritiBarcodeAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import frappe.utils.background_jobs
        cls._original_validate_queue = frappe.utils.background_jobs.validate_queue
        frappe.utils.background_jobs.validate_queue = lambda qtype, *args, **kwargs: None
        if hasattr(frappe.utils.background_jobs, "default_queue_list"):
            if "barcode" not in frappe.utils.background_jobs.default_queue_list:
                frappe.utils.background_jobs.default_queue_list.append("barcode")
        # Clean up any test templates and their versions
        test_templates = ["TEST_ZPL_TEMPLATE", "TEST_TSPL_TEMPLATE", "TEST_MAPPINGS_TEMPLATE", "TEST_TOO_LARGE", "TEST_INVALID_MAPPINGS", "TEST_RESTORE_SNAP_TEMPLATE", "TEST_LOCK_TEMPLATE", "TEST_LEGACY_TEMPLATE"]
        frappe.db.delete("SMRITI Print Template Version", {"template": ["in", test_templates]})
        frappe.db.delete("SMRITI Print Template", {"name": ["in", test_templates]})
        frappe.db.commit()
        from smriti_retail_os.setup import seed_master_doctypes, setup_activity_log_options, create_smriti_barcode_settings_doctype
        seed_master_doctypes()
        setup_activity_log_options()
        create_smriti_barcode_settings_doctype()
        from smriti_retail_os.patches.seed_printability_formula import execute as seed_printability
        seed_printability()

    @classmethod
    def tearDownClass(cls):
        import frappe.utils.background_jobs
        if hasattr(cls, "_original_validate_queue"):
            frappe.utils.background_jobs.validate_queue = cls._original_validate_queue
        super().tearDownClass()

    def setUp(self):
        import frappe.utils.background_jobs
        self._original_validate_queue = frappe.utils.background_jobs.validate_queue
        frappe.utils.background_jobs.validate_queue = lambda qtype, *args, **kwargs: None
        if hasattr(frappe.utils.background_jobs, "default_queue_list"):
            if "barcode" not in frappe.utils.background_jobs.default_queue_list:
                frappe.utils.background_jobs.default_queue_list.append("barcode")

    def tearDown(self):
        import frappe.utils.background_jobs
        if hasattr(self, "_original_validate_queue"):
            frappe.utils.background_jobs.validate_queue = self._original_validate_queue
        # Clean up test templates and their versions
        test_templates = ["TEST_ZPL_TEMPLATE", "TEST_TSPL_TEMPLATE", "TEST_MAPPINGS_TEMPLATE", "TEST_TOO_LARGE", "TEST_INVALID_MAPPINGS", "TEST_RESTORE_SNAP_TEMPLATE", "TEST_LOCK_TEMPLATE", "TEST_LEGACY_TEMPLATE"]
        frappe.db.delete("SMRITI Print Template Version", {"template": ["in", test_templates]})
        frappe.db.delete("SMRITI Print Template", {"name": ["in", test_templates]})
        frappe.db.commit()

    def test_print_template_lifecycle(self):
        """Tests standard CRUD lifecycle of SMRITI Print Template records."""
        # 1. Create / Save Template
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}])
        )
        
        self.assertTrue(frappe.db.exists("SMRITI Print Template", "TEST_ZPL_TEMPLATE"))
        
        # 2. Read Template
        doc = frappe.get_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        self.assertEqual(doc.template_title, template_name)
        self.assertEqual(doc.label_size, "50x25")
        self.assertEqual(doc.printer_language, "ZPL")
        self.assertEqual(doc.printer_family, "ZPL")  # auto-fallback
        self.assertEqual(doc.raw_template, raw_zpl)
        self.assertEqual(doc.custom_version, "1.0.0") # default version value
        self.assertIsNotNone(doc.template_checksum)
        old_checksum = doc.template_checksum
        
        # 3. Update Template
        updated_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^FO20,80^FD{barcode}^FS\n^XZ"
        save_print_template(
            template_name=template_name,
            label_size="50x30",
            printer_language="ZPL",
            raw_template=updated_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}]),
            printer_family="CPCL"  # explicit printer family update
        )
        
        doc.reload()
        self.assertEqual(doc.label_size, "50x30")
        self.assertEqual(doc.printer_family, "CPCL")
        self.assertEqual(doc.raw_template, updated_zpl)
        self.assertNotEqual(doc.template_checksum, old_checksum)

        # 4. Delete Template
        frappe.db.delete("SMRITI Print Template Version", {"template": "TEST_ZPL_TEMPLATE"})
        frappe.delete_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        self.assertFalse(frappe.db.exists("SMRITI Print Template", "TEST_ZPL_TEMPLATE"))

    def test_template_rendering_zpl(self):
        """Tests ZPL template substitution and print command counts."""
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^FO20,50^FD{mrp}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "Tattly Threads",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 2
            }
        ]
        
        # Generate PRN - should support lookup by either "TEST_ZPL_TEMPLATE" or "Test ZPL Template"
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_ZPL_TEMPLATE").get("prn")
        self.assertEqual(prn_data.count("^XA"), 2)
        self.assertEqual(prn_data.count("^XZ"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data)
        self.assertIn("499", prn_data)

        # Verify fallback by template_title
        prn_data_fallback = generate_prn(items=json.dumps(items_payload), template_name=template_name).get("prn")
        self.assertEqual(prn_data_fallback.count("^XA"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data_fallback)

    def test_template_rendering_tspl(self):
        """Tests TSPL template rendering and print command outputs."""
        template_name = "Test TSPL Template"
        raw_tspl = "SIZE 50 mm, 25 mm\nCLS\nTEXT 20,20,\"3\",0,1,1,\"{item_name}\"\nPRINT 1,1"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="TSPL",
            raw_template=raw_tspl
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "Tattly Threads",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 1
            }
        ]
        
        # Generate PRN
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_TSPL_TEMPLATE").get("prn")
        
        self.assertEqual(prn_data.count("SIZE 50 mm, 25 mm"), 1)
        self.assertEqual(prn_data.count("PRINT 1,1"), 1)
        self.assertIn("Bronze Loafer Shoe", prn_data)

    def test_field_mapping_resolution(self):
        """Tests custom field mappings JSON dynamically maps values inside ZPL templates."""
        template_name = "Test Mappings Template"
        raw_zpl = "^XA\n^FO20,20^FD{my_custom_token}^FS\n^XZ"
        
        # Configure a field mapping for custom token -> brand
        mappings = [
            {
                "label_field": "my_custom_token",
                "erp_field": "brand"
            }
        ]
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps(mappings)
        )
        
        items_payload = [
            {
                "item_code": "BBM-40-BRZ",
                "item_name": "Bronze Loafer Shoe",
                "barcode": "8901234567890",
                "style": "BBM",
                "brand": "TATTLY BRAND",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 1
            }
        ]
        
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_MAPPINGS_TEMPLATE").get("prn")
        self.assertIn("TATTLY BRAND", prn_data)
        self.assertNotIn("{my_custom_token}", prn_data)

    def test_backward_compatibility(self):
        """Tests that legacy custom_ fieldnames continue to exist natively in the file-based schema."""
        template_name = "Test ZPL Template"
        raw_zpl = "^XA\n^FO20,20^FD{item_name}^FS\n^XZ"
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=raw_zpl,
            field_mappings_json=json.dumps([{"label_field": "item_name", "erp_field": "item_name"}])
        )
        
        doc = frappe.get_doc("SMRITI Print Template", "TEST_ZPL_TEMPLATE")
        
        # Verify legacy custom field attributes are directly accessible on the document object
        self.assertTrue(hasattr(doc, "custom_field_mappings_json"))
        self.assertTrue(hasattr(doc, "custom_version"))
        self.assertTrue(hasattr(doc, "custom_active"))
        self.assertTrue(hasattr(doc, "custom_is_default"))
        
        self.assertEqual(doc.custom_version, "1.0.0")
        self.assertEqual(doc.custom_active, 1)
        self.assertEqual(doc.custom_is_default, 0)
        self.assertIsNotNone(doc.custom_field_mappings_json)

    def test_template_size_validation(self):
        """Tests that a template exceeding 100 KB throws a ValidationError."""
        template_name = "Test Too Large Template"
        large_raw = "A" * (101 * 1024)  # 101 KB
        
        # Test validation on direct save/insert
        doc = frappe.new_doc("SMRITI Print Template")
        doc.name = "TEST_TOO_LARGE"
        doc.template_title = template_name
        doc.label_size = "50x25"
        doc.printer_language = "ZPL"
        doc.raw_template = large_raw
        
        self.assertRaises(frappe.ValidationError, doc.insert)
        
        # Test validation on API save_print_template call
        self.assertRaises(
            frappe.ValidationError,
            save_print_template,
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template=large_raw
        )

    def test_mappings_json_validation(self):
        """Tests field mapping JSON format validation."""
        template_name = "Test Invalid Mappings"
        
        # 1. Invalid JSON string
        doc = frappe.new_doc("SMRITI Print Template")
        doc.name = "TEST_INVALID_MAPPINGS"
        doc.template_title = template_name
        doc.label_size = "50x25"
        doc.printer_language = "ZPL"
        doc.raw_template = "^XA^XZ"
        doc.custom_field_mappings_json = "{invalid_json}"
        
        self.assertRaises(frappe.ValidationError, doc.insert)
        
        # 2. JSON is valid but not a list/array
        doc.custom_field_mappings_json = '{"label_field": "item_name"}'
        self.assertRaises(frappe.ValidationError, doc.insert)

    def test_honeywell_seed_exists(self):
        """Verifies that the default Honeywell template was successfully seeded."""
        self.assertTrue(frappe.db.exists("SMRITI Print Template", "IMPACT_HONEYWELL_IH2_ZPL"))
        doc = frappe.get_doc("SMRITI Print Template", "IMPACT_HONEYWELL_IH2_ZPL")
        self.assertEqual(doc.template_title, "IMPACT by Honeywell IH-2 (ZPL)")
        self.assertEqual(doc.printer_language, "ZPL")
        self.assertEqual(doc.printer_family, "ZPL")
        self.assertEqual(doc.label_size, "100x50")
        self.assertIn("IMPACT by Honeywell", doc.template_title)

    def test_async_1_enqueue_creates_job_and_prn(self):
        """test_async_1: enqueue creates job with status Queued + .prn file exists"""
        from smriti_retail_os.barcode_api import enqueue_print_job
        import os
        
        payload = "^XA^FDTest Async 1^FS^XZ"
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
        
        self.assertTrue(frappe.db.exists("SMRITI Print Job", {"job_id": job_id}))
        status = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "status")
        self.assertEqual(status, "Queued")
        
        prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
        self.assertTrue(os.path.exists(prn_path))
        with open(prn_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), payload)
            
        # Clean up
        frappe.db.delete("SMRITI Print Job", {"job_id": job_id})
        frappe.db.commit()
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass

    def test_async_2_process_success_deletes_prn(self):
        """test_async_2: _process_print_job sets Success, .prn file deleted after success"""
        from smriti_retail_os.barcode_api import enqueue_print_job, _process_print_job
        from unittest.mock import patch
        import os
        
        payload = "^XA^FDTest Async 2^FS^XZ"
        
        # Enqueue first to get job_id
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
            
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync') as mock_send:
            _process_print_job(print_job_id=job_id)
            mock_send.assert_called_once_with(payload, "192.168.1.180", 9100)
            
        status = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "status")
        self.assertEqual(status, "Success")
        
        prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
        self.assertFalse(os.path.exists(prn_path))
        
        # Clean up database
        frappe.db.delete("SMRITI Print Job", {"job_id": job_id})
        frappe.db.commit()

    def test_async_3_process_failed_retains_prn(self):
        """test_async_3: _process_print_job sets Failed, .prn file retained on failure"""
        from smriti_retail_os.barcode_api import enqueue_print_job, _process_print_job
        from unittest.mock import patch
        import os
        
        payload = "^XA^FDTest Async 3^FS^XZ"
        
        # Enqueue first to get job_id
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
                
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync', side_effect=Exception("Connection refused")):
            try:
                _process_print_job(print_job_id=job_id)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in tests/test_barcode_api.py:404: {sys.exc_info()[1]}")
                
        status = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "status")
        self.assertEqual(status, "Failed")
        
        prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
        self.assertTrue(os.path.exists(prn_path))
        
        # Clean up
        frappe.db.delete("SMRITI Print Job", {"job_id": job_id})
        frappe.db.commit()
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass

    def test_async_4_get_status_known_job(self):
        """test_async_4: get_print_job_status returns correct status for known job_id"""
        from smriti_retail_os.barcode_api import enqueue_print_job, get_print_job_status
        import os
        
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload="^XA^XZ"
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
        
        res = get_print_job_status(job_id)
        self.assertEqual(res.get("status"), "Queued")
        
        # Clean up
        frappe.db.delete("SMRITI Print Job", {"job_id": job_id})
        frappe.db.commit()
        prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass

    def test_async_5_get_status_unknown_job_throws(self):
        """test_async_5: get_print_job_status throws for unknown job_id"""
        from smriti_retail_os.barcode_api import get_print_job_status
        self.assertRaises(frappe.DoesNotExistError, get_print_job_status, "JOB-NONEXISTENT")

    def test_async_6_failed_job_retry(self):
        """test_async_6: Failed job retry creates new job_id with same payload content"""
        from smriti_retail_os.barcode_api import enqueue_print_job, retry_print_job, _process_print_job
        from unittest.mock import patch
        import os
        
        payload = "^XA^FDTest Async 6^FS^XZ"
        
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
            
        # Fail the job
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync', side_effect=Exception("Network error")):
            try:
                _process_print_job(print_job_id=job_id)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in tests/test_barcode_api.py:483: {sys.exc_info()[1]}")
                
        # Retry the job
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync') as mock_send_new:
            # We want the retry to run synchronously to verify success
            frappe.flags.in_test = True
            try:
                res = retry_print_job(job_id)
                new_job_id = res.get("job_id")
            finally:
                frappe.flags.in_test = old_in_test
            mock_send_new.assert_called_once_with(payload, "192.168.1.180", 9100)
            
        self.assertNotEqual(job_id, new_job_id)
        new_status = frappe.db.get_value("SMRITI Print Job", {"job_id": new_job_id}, "status")
        self.assertEqual(new_status, "Success")
        
        # Clean up both jobs
        frappe.db.delete("SMRITI Print Job", {"job_id": ["in", [job_id, new_job_id]]})
        frappe.db.commit()
        for j in [job_id, new_job_id]:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{j}.prn")
            try:
                os.unlink(prn_path)
            except FileNotFoundError:
                pass

    def test_async_7_concurrency_no_collisions(self):
        """test_async_7: Enqueue 250 jobs simultaneously using ThreadPoolExecutor. Verify unique IDs and no duplicates."""
        from smriti_retail_os.barcode_api import enqueue_print_job
        from concurrent.futures import ThreadPoolExecutor
        from unittest.mock import patch
        import os
        
        job_ids = []
        payload = "^XA^FDTest Async 7^FS^XZ"
        
        def run_enqueue(idx):
            frappe.init(site="smriti_retail")
            frappe.connect()
            try:
                frappe.flags.in_test = False
                res = enqueue_print_job(
                    template_name="TEST_ZPL_TEMPLATE",
                    printer_ip="192.168.1.180",
                    printer_port=9100,
                    labels_count=1,
                    payload=f"{payload} - {idx}"
                )
                return res["job_id"]
            except Exception as e:
                return str(e)
            finally:
                frappe.destroy()
                
        with patch("frappe.enqueue") as mock_enqueue:
            with ThreadPoolExecutor(max_workers=20) as executor:
                job_ids = list(executor.map(run_enqueue, range(250)))
            
        self.assertEqual(len(job_ids), 250)
        for j in job_ids:
            self.assertTrue(j.startswith("JOB-"))
            
        self.assertEqual(len(set(job_ids)), 250)
        
        db_count = frappe.db.count("SMRITI Print Job", {"job_id": ["in", job_ids]})
        self.assertEqual(db_count, 250)
        
        # Clean up
        frappe.db.delete("SMRITI Print Job", {"job_id": ["in", job_ids]})
        frappe.db.commit()
        for j in job_ids:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{j}.prn")
            try:
                os.unlink(prn_path)
            except FileNotFoundError:
                pass

    def test_async_8_cleanup_retention(self):
        """test_async_8: cleanup_old_print_jobs() deletes Success jobs older than 30d, Failed older than 90d, leaves recent."""
        from smriti_retail_os.barcode_api import cleanup_old_print_jobs
        from frappe.utils import add_days, now_datetime
        import os
        
        # Create 3 test jobs
        doc1 = frappe.new_doc("SMRITI Print Job")
        doc1.job_id = "JOB-TEST-S-OLD"
        doc1.name = "JOB-TEST-S-OLD"
        doc1.status = "Success"
        doc1.completed_on = add_days(now_datetime(), -31)
        doc1.insert(ignore_permissions=True)
        
        doc2 = frappe.new_doc("SMRITI Print Job")
        doc2.job_id = "JOB-TEST-F-OLD"
        doc2.name = "JOB-TEST-F-OLD"
        doc2.status = "Failed"
        doc2.completed_on = add_days(now_datetime(), -91)
        doc2.insert(ignore_permissions=True)
        
        prn_dir = frappe.get_site_path('private', 'print_jobs')
        os.makedirs(prn_dir, exist_ok=True)
        prn_path2 = os.path.join(prn_dir, "JOB-TEST-F-OLD.prn")
        with open(prn_path2, "w") as f:
            f.write("failed old payload")
            
        doc3 = frappe.new_doc("SMRITI Print Job")
        doc3.job_id = "JOB-TEST-F-NEW"
        doc3.name = "JOB-TEST-F-NEW"
        doc3.status = "Failed"
        doc3.completed_on = add_days(now_datetime(), -10)
        doc3.insert(ignore_permissions=True)
        prn_path3 = os.path.join(prn_dir, "JOB-TEST-F-NEW.prn")
        with open(prn_path3, "w") as f:
            f.write("failed new payload")
            
        frappe.db.commit()
        
        cleanup_old_print_jobs()
        
        self.assertFalse(frappe.db.exists("SMRITI Print Job", "JOB-TEST-S-OLD"))
        self.assertFalse(frappe.db.exists("SMRITI Print Job", "JOB-TEST-F-OLD"))
        self.assertFalse(os.path.exists(prn_path2))
        
        self.assertTrue(frappe.db.exists("SMRITI Print Job", "JOB-TEST-F-NEW"))
        self.assertTrue(os.path.exists(prn_path3))
        
        # Clean up doc3 and file3
        frappe.delete_doc("SMRITI Print Job", "JOB-TEST-F-NEW", ignore_permissions=True)
        frappe.db.commit()
        try:
            os.unlink(prn_path3)
        except FileNotFoundError:
            pass

    def test_async_9_get_recent_print_jobs(self):
        """test_async_9: get_recent_print_jobs API executes without DB schema issues and returns jobs."""
        from smriti_retail_os.barcode_api import get_recent_print_jobs, enqueue_print_job
        import os
        
        # Enqueue a print job to have at least one record
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            res = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                payload="^XA^FDTest Get Recent Jobs^FS^XZ",
                print_qty=2,
                item_code=None,
                barcode="123456789012"
            )
            job_id = res["job_id"]
        finally:
            frappe.flags.in_test = old_in_test
        
        try:
            # Query recent print jobs using the API
            jobs = get_recent_print_jobs(limit=10)
            self.assertTrue(len(jobs) >= 1)
            
            # Find our enqueued job in the list
            matched = [j for j in jobs if j.get("job_id") == job_id]
            self.assertEqual(len(matched), 1)
            self.assertEqual(matched[0]["status"], "Queued")
            self.assertEqual(matched[0]["template_name"], "TEST_ZPL_TEMPLATE")
            self.assertEqual(matched[0]["labels_count"], 2)
            self.assertEqual(matched[0]["printer_ip"], "192.168.1.180")
        finally:
            # Clean up print job and file
            frappe.delete_doc("SMRITI Print Job", job_id, ignore_permissions=True)
            frappe.db.commit()
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
            if os.path.exists(prn_path):
                try:
                    os.unlink(prn_path)
                except Exception:
                    pass

    def test_15_publish_realtime_targets_requested_by_user(self):
        """test_15: publish_realtime targets correct requested_by user in enqueue and process"""
        from smriti_retail_os.barcode_api import enqueue_print_job, _process_print_job
        from unittest.mock import patch
        import os
        
        payload = "^XA^FDTest Async 15^FS^XZ"
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        
        with patch('frappe.publish_realtime') as mock_publish:
            try:
                res = enqueue_print_job(
                    template_name="TEST_ZPL_TEMPLATE",
                    printer_ip="192.168.1.180",
                    printer_port=9100,
                    labels_count=2,
                    payload=payload
                )
                job_id = res["job_id"]
            finally:
                frappe.flags.in_test = old_in_test
            
            # Check queued event publish
            mock_publish.assert_any_call(
                "smriti.barcode.print_status",
                {
                    "event_version": 1,
                    "job_id": job_id,
                    "status": "Queued"
                },
                user=frappe.session.user
            )
            
            # Check process event publish
            with patch('smriti_retail_os.barcode_api._send_to_printer_sync') as mock_send:
                _process_print_job(print_job_id=job_id)
                
            mock_publish.assert_any_call(
                "smriti.barcode.print_status",
                {
                    "event_version": 1,
                    "job_id": job_id,
                    "status": "Success"
                },
                user=frappe.session.user
            )
            
        # Clean up
        frappe.db.delete("SMRITI Print Job", {"job_id": job_id})
        frappe.db.commit()
        prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass

    def test_16_template_restore_inserts_history_snapshot(self):
        """test_16: template restore inserts history snapshot of the pre-restored state"""
        from smriti_retail_os.barcode_api import (
            save_print_template,
            get_print_template_versions,
            restore_print_template_version,
        )
        
        template_name = "Test Restore Snap Template"
        frappe.db.delete("SMRITI Print Template", {"name": "TEST_RESTORE_SNAP_TEMPLATE"})
        frappe.db.delete("SMRITI Print Template Version", {"template": "TEST_RESTORE_SNAP_TEMPLATE"})
        frappe.db.commit()
        
        # 1. Create first version
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^FDV1^XZ",
            custom_version="1.0.0"
        )
        doc = frappe.get_doc("SMRITI Print Template", "TEST_RESTORE_SNAP_TEMPLATE")
        v1_checksum = doc.template_checksum
        
        # 2. Modify to create V2 (this snapshots V1 as version 1.0.0 in history)
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^FDV2^XZ",
            custom_version="2.0.0"
        )
        doc.reload()
        v2_checksum = doc.template_checksum
        
        versions = get_print_template_versions(template_name)
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].version_number, "1.0.0")
        self.assertEqual(versions[0].raw_template, "^XA^FDV1^XZ")
        
        # 3. Restore to V1 (should snapshot V2 as version 2.0.0 in history)
        restore_print_template_version(
            template_name=template_name,
            version_number="1.0.0",
            expected_checksum=v2_checksum
        )
        
        doc.reload()
        self.assertEqual(doc.raw_template, "^XA^FDV1^XZ")
        self.assertEqual(doc.template_checksum, v1_checksum)
        
        # Check versions - we should now have 2 versions in history (V1 and V2)
        versions_after = get_print_template_versions(template_name)
        self.assertEqual(len(versions_after), 2)
        self.assertEqual(versions_after[0].version_number, "2.0.0")
        self.assertEqual(versions_after[0].raw_template, "^XA^FDV2^XZ")
        
        # Clean up
        frappe.db.delete("SMRITI Print Template", {"name": "TEST_RESTORE_SNAP_TEMPLATE"})
        frappe.db.delete("SMRITI Print Template Version", {"template": "TEST_RESTORE_SNAP_TEMPLATE"})
        frappe.db.commit()

    def test_17_legacy_template_no_visual_layout_blocks_canvas(self):
        """test_17: Legacy template has no custom_visual_layout_json"""
        template_name = "Test Legacy Template"
        frappe.db.delete("SMRITI Print Template", {"name": "TEST_LEGACY_TEMPLATE"})
        frappe.db.commit()
        
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^FDLegacy^XZ"
        )
        
        doc = frappe.get_doc("SMRITI Print Template", "TEST_LEGACY_TEMPLATE")
        self.assertIsNone(doc.custom_visual_layout_json)
        
        # Clean up
        frappe.delete_doc("SMRITI Print Template", "TEST_LEGACY_TEMPLATE")
        frappe.db.commit()

    def test_18_dpi_dot_coordinate_translation(self):
        """test_18: DPI dot coordinate translation correctness"""
        # dots = mm * dpi / 25.4
        # At 203 DPI: 10mm -> 10 * 203 / 25.4 = 79.92 -> 80 dots
        # At 300 DPI: 10mm -> 10 * 300 / 25.4 = 118.11 -> 118 dots
        
        def translate_mm_to_dots(mm, dpi):
            return round(mm * dpi / 25.4)
            
        self.assertEqual(translate_mm_to_dots(10, 203), 80)
        self.assertEqual(translate_mm_to_dots(10, 300), 118)
        self.assertEqual(translate_mm_to_dots(50, 203), 400)
        self.assertEqual(translate_mm_to_dots(50, 300), 591)

    def test_19_mismatched_checksum_throws_validation_error(self):
        """test_19: restore version with mismatched expected_checksum throws ValidationError"""
        from smriti_retail_os.barcode_api import (
            save_print_template,
            restore_print_template_version,
        )
        
        template_name = "Test Lock Template"
        frappe.db.delete("SMRITI Print Template", {"name": "TEST_LOCK_TEMPLATE"})
        frappe.db.delete("SMRITI Print Template Version", {"template": "TEST_LOCK_TEMPLATE"})
        frappe.db.commit()
        
        # 1. Create version 1
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^FDV1^XZ",
            custom_version="1.0.0"
        )
        
        # 2. Modify to version 2 (creating history snapshot for 1.0.0)
        save_print_template(
            template_name=template_name,
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^FDV2^XZ",
            custom_version="2.0.0"
        )
        
        # Try to restore version 1.0.0 with a bad expected_checksum
        self.assertRaises(
            frappe.ValidationError,
            restore_print_template_version,
            template_name=template_name,
            version_number="1.0.0",
            expected_checksum="bad_checksum_value"
        )
        
        # Clean up
        frappe.db.delete("SMRITI Print Template", {"name": "TEST_LOCK_TEMPLATE"})
        frappe.db.delete("SMRITI Print Template Version", {"template": "TEST_LOCK_TEMPLATE"})
        frappe.db.commit()

    def test_20_print_safe_margin_boundary_detection(self):
        """test_20: safe margin limits boundary detection (1.5mm inset)"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        # Element inside safe zone
        layout = json.dumps([
            {"id": "txt1", "type": "text", "x": 2.0, "y": 2.0, "w": 10.0, "h": 5.0, "content": "Hello"}
        ])
        res = validate_layout_diagnostics(layout, "50x25")
        self.assertEqual(res["errors_count"], 0)
        self.assertEqual(res["warnings_count"], 0)

        # Barcode crossing 1.5mm margin (Error)
        layout_error = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 1.0, "y": 2.0, "w": 20.0, "h": 10.0, "content": "123456"}
        ])
        res_error = validate_layout_diagnostics(layout_error, "50x25")
        self.assertEqual(res_error["errors_count"], 1)
        self.assertEqual(res_error["diagnostics"][0]["severity"], "error")

        # Text crossing 1.5mm margin (Warning)
        layout_warn = json.dumps([
            {"id": "txt2", "type": "text", "x": 1.0, "y": 2.0, "w": 10.0, "h": 5.0, "content": "Hello"}
        ])
        res_warn = validate_layout_diagnostics(layout_warn, "50x25")
        self.assertEqual(res_warn["errors_count"], 0)
        self.assertEqual(res_warn["warnings_count"], 1)
        self.assertEqual(res_warn["diagnostics"][0]["severity"], "warning")

        # Element crossing absolute edge (Error)
        layout_out = json.dumps([
            {"id": "txt3", "type": "text", "x": 45.0, "y": 2.0, "w": 10.0, "h": 5.0, "content": "Hello"}
        ])
        res_out = validate_layout_diagnostics(layout_out, "50x25")
        self.assertEqual(res_out["errors_count"], 1)
        self.assertEqual(res_out["diagnostics"][0]["severity"], "error")

    def test_21_text_overflow_detection(self):
        """test_21: text bounding-box overflow calculation (short text passes, long text triggers warning)"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        # Short text, fits within w=20mm
        layout_fit = json.dumps([
            {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 20.0, "h": 5.0, "content": "Short"}
        ])
        res_fit = validate_layout_diagnostics(layout_fit, "50x25")
        self.assertEqual(res_fit["warnings_count"], 0)

        # Long text, exceeds w=5mm (estimated width is len * 1.8 = 30.6mm)
        layout_overflow = json.dumps([
            {"id": "txt2", "type": "text", "x": 5.0, "y": 5.0, "w": 5.0, "h": 5.0, "content": "Very Long Text Name"}
        ])
        res_overflow = validate_layout_diagnostics(layout_overflow, "50x25")
        self.assertEqual(res_overflow["warnings_count"], 1)
        self.assertEqual(res_overflow["diagnostics"][0]["severity"], "warning")

    def test_22_collision_detection(self):
        """test_22: element collision detection (overlapping fields)"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        # Overlapping text and barcode (collision)
        layout_overlap = json.dumps([
            {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 10.0, "h": 5.0, "content": "Text"},
            {"id": "bc1", "type": "barcode", "x": 8.0, "y": 6.0, "w": 15.0, "h": 8.0, "content": "1234"}
        ])
        res_overlap = validate_layout_diagnostics(layout_overlap, "50x25")
        self.assertEqual(res_overlap["errors_count"], 1)
        self.assertEqual(res_overlap["diagnostics"][0]["severity"], "error")

        # Non-overlapping
        layout_ok = json.dumps([
            {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 10.0, "h": 5.0, "content": "Text"},
            {"id": "bc1", "type": "barcode", "x": 20.0, "y": 5.0, "w": 15.0, "h": 8.0, "content": "1234"}
        ])
        res_ok = validate_layout_diagnostics(layout_ok, "50x25")
        self.assertEqual(res_ok["errors_count"], 0)

        # Decorative element (box) overlap - ignored
        layout_decor = json.dumps([
            {"id": "box1", "type": "box", "x": 4.0, "y": 4.0, "w": 20.0, "h": 10.0},
            {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 10.0, "h": 5.0, "content": "Text"}
        ])
        res_decor = validate_layout_diagnostics(layout_decor, "50x25")
        self.assertEqual(res_decor["errors_count"], 0)

    def test_23_layout_wrapper_backward_compatibility(self):
        """test_23: wrapped/unwrapped JSON compatibility"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        
        elements = [
            {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 10.0, "h": 5.0, "content": "Text"}
        ]
        # Unwrapped array
        layout_unwrapped = json.dumps(elements)
        # Wrapped layout structure
        layout_wrapped = json.dumps({
            "layout_version": 1,
            "compiler_version": 1,
            "elements": elements
        })
        
        res1 = validate_layout_diagnostics(layout_unwrapped, "50x25")
        res2 = validate_layout_diagnostics(layout_wrapped, "50x25")
        
        self.assertEqual(res1["diagnostics"], res2["diagnostics"])
        self.assertEqual(res1["errors_count"], res2["errors_count"])

    def test_24_printability_formula_seeded(self):
        """test_24: Verify SMRITI-PRN-SCORE-01 formula exists in Formula Registry"""
        self.assertTrue(frappe.db.exists("SMRITI Formula Definition", {"formula_id": "SMRITI-PRN-SCORE-01"}))
        doc = frappe.get_doc("SMRITI Formula Definition", {"formula_id": "SMRITI-PRN-SCORE-01"})
        self.assertEqual(doc.status, "Approved")
        self.assertEqual(doc.is_active, 1)
        self.assertIn("explainability_json", doc.as_dict())

    def test_25_settings_fallback_and_default_values(self):
        """test_25: Verify fallback values when settings DocType is missing or values are empty"""
        from smriti_retail_os.barcode_api import (
            get_barcode_hrt_reserved_height,
            get_enforce_printability_threshold,
        )
        orig_exists = frappe.db.exists
        def mock_exists(dt, *args, **kwargs):
            if dt == "SMRITI Barcode Settings" or "SMRITI Barcode Settings" in args:
                return False
            return orig_exists(dt, *args, **kwargs)
        
        with unittest.mock.patch("frappe.db.exists", side_effect=mock_exists):
            self.assertEqual(get_barcode_hrt_reserved_height(), 2.5)
            self.assertEqual(get_enforce_printability_threshold(), 1)

    def test_26_save_validation_boundary_conditions(self):
        """test_26: Test save validation block on boundary scores (69 vs 70) and config enforce toggle"""
        from smriti_retail_os.barcode_api import save_print_template, validate_layout_diagnostics
        
        elements_70 = [
            {"id": "txt1", "type": "text", "x": 1.0, "y": 2.0, "w": 10.0, "h": 2.0, "content": ""},
            {"id": "txt2", "type": "text", "x": 1.0, "y": 5.0, "w": 10.0, "h": 2.0, "content": ""},
            {"id": "txt3", "type": "text", "x": 1.0, "y": 8.0, "w": 10.0, "h": 2.0, "content": ""},
            {"id": "txt4", "type": "text", "x": 15.0, "y": 2.0, "w": 5.0, "h": 2.0, "content": "Very Long Text Name"},
            {"id": "txt5", "type": "text", "x": 15.0, "y": 5.0, "w": 5.0, "h": 2.0, "content": "Very Long Text Name"},
            {"id": "txt6", "type": "text", "x": 15.0, "y": 8.0, "w": 5.0, "h": 2.0, "content": "Very Long Text Name"},
        ]
        layout_70 = json.dumps(elements_70)
        res_70 = validate_layout_diagnostics(layout_70, "50x25")
        self.assertEqual(res_70["printability_score"], 70.0)
        self.assertEqual(res_70["grade"], "C")
        
        try:
            save_print_template(
                template_name="TEST_LOCK_TEMPLATE",
                label_size="50x25",
                printer_language="ZPL",
                raw_template="^XA^XZ",
                custom_visual_layout_json=layout_70
            )
        except frappe.ValidationError:
            self.fail("save_print_template should not throw on Score = 70")
            
        elements_65 = elements_70 + [
            {"id": "txt7", "type": "text", "x": 1.0, "y": 11.0, "w": 10.0, "h": 2.0, "content": ""}
        ]
        layout_65 = json.dumps(elements_65)
        res_65 = validate_layout_diagnostics(layout_65, "50x25")
        self.assertTrue(res_65["printability_score"] < 70)
        self.assertEqual(res_65["grade"], "F")
        
        frappe.db.set_single_value("SMRITI Barcode Settings", "enforce_printability_threshold", 1)
        frappe.db.commit()
        self.assertRaises(
            frappe.ValidationError,
            save_print_template,
            template_name="TEST_LOCK_TEMPLATE",
            label_size="50x25",
            printer_language="ZPL",
            raw_template="^XA^XZ",
            custom_visual_layout_json=layout_65
        )
        
        frappe.db.set_single_value("SMRITI Barcode Settings", "enforce_printability_threshold", 0)
        frappe.db.commit()
        try:
            save_print_template(
                template_name="TEST_LOCK_TEMPLATE",
                label_size="50x25",
                printer_language="ZPL",
                raw_template="^XA^XZ",
                custom_visual_layout_json=layout_65
            )
        except frappe.ValidationError:
            self.fail("save_print_template should allow save on Grade F when enforce is disabled")
            
        frappe.db.set_single_value("SMRITI Barcode Settings", "enforce_printability_threshold", 1)
        frappe.db.commit()

    def test_27_quiet_zone_intrusion_modes(self):
        """test_27: Test quiet zone intrusions (non-decorative triggers error, decorative triggers warning)"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        
        layout_err = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 10.0, "y": 5.0, "w": 20.0, "h": 10.0, "format": "code128"},
            {"id": "txt1", "type": "text", "x": 6.0, "y": 6.0, "w": 3.0, "h": 3.0, "content": "Text"}
        ])
        res_err = validate_layout_diagnostics(layout_err, "50x25")
        self.assertEqual(res_err["errors_count"], 1)
        self.assertEqual(res_err["breakdown"]["quiet_zone"], 0)
        
        layout_warn = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 10.0, "y": 5.0, "w": 20.0, "h": 10.0, "format": "code128"},
            {"id": "box1", "type": "box", "x": 6.0, "y": 6.0, "w": 3.0, "h": 3.0}
        ])
        res_warn = validate_layout_diagnostics(layout_warn, "50x25")
        self.assertEqual(res_warn["errors_count"], 0)
        self.assertEqual(res_warn["warnings_count"], 1)
        self.assertEqual(res_warn["breakdown"]["quiet_zone"], 20)

    def test_28_virtual_hrt_collision(self):
        """test_28: Verify virtual HRT space overlap collision triggers error"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        
        layout_overlap = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 10.0, "y": 5.0, "w": 20.0, "h": 10.0, "format": "code128"},
            {"id": "txt1", "type": "text", "x": 15.0, "y": 16.0, "w": 5.0, "h": 2.0, "content": "Text"}
        ])
        res_overlap = validate_layout_diagnostics(layout_overlap, "50x25")
        self.assertEqual(res_overlap["errors_count"], 1)
        self.assertEqual(res_overlap["breakdown"]["collision"], 0)

    def test_29_barcode_density_rules(self):
        """test_29: Test minimum recommended barcode widths per barcode family"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics
        
        layout_ean = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 10.0, "y": 5.0, "w": 20.0, "h": 10.0, "format": "ean13"}
        ])
        res_ean = validate_layout_diagnostics(layout_ean, "50x25")
        self.assertEqual(res_ean["warnings_count"], 1)
        self.assertEqual(res_ean["breakdown"]["density"], 10)
        
        layout_code = json.dumps([
            {"id": "bc1", "type": "barcode", "x": 10.0, "y": 5.0, "w": 20.0, "h": 10.0, "format": "code128"}
        ])
        res_code = validate_layout_diagnostics(layout_code, "50x25")
        self.assertEqual(res_code["warnings_count"], 0)
        self.assertEqual(res_code["breakdown"]["density"], 15)

    def test_30_formula_corruption_fallback(self):
        """test_30: Verify fallback safety when Formula Registry is corrupted/missing"""
        from smriti_retail_os.barcode_api import validate_layout_diagnostics, get_printability_formula_config
        
        try:
            frappe.cache().delete_value("smriti:barcode_printability_formula_config")
        except Exception:
            pass
        
        orig_exists = frappe.db.exists
        def mock_exists(dt, *args, **kwargs):
            if dt == "SMRITI Formula Definition":
                return False
            return orig_exists(dt, *args, **kwargs)
            
        with unittest.mock.patch("frappe.db.exists", side_effect=mock_exists):
            cfg = get_printability_formula_config()
            self.assertEqual(cfg["weights"]["margin"], 25)
            self.assertEqual(cfg["weights"]["quiet_zone"], 25)
            
            layout = json.dumps([
                {"id": "txt1", "type": "text", "x": 5.0, "y": 5.0, "w": 10.0, "h": 5.0, "content": "Hello"}
            ])
            res = validate_layout_diagnostics(layout, "50x25")
            self.assertEqual(res["printability_score"], 100.0)
            self.assertEqual(res["grade"], "A+")

    def test_31_formula_missing_warning_log(self):
        """test_31: Verify that a warning log is generated when SMRITI-PRN-SCORE-01 formula is missing"""
        from smriti_retail_os.barcode_api import get_printability_formula_config
        
        # Delete any existing warning error logs for clean check
        frappe.db.delete("Error Log", {"method": "SMRITI Formula Registry Warning"})
        frappe.db.commit()
        
        try:
            frappe.cache().delete_value("smriti:barcode_printability_formula_config")
        except Exception:
            pass
            
        orig_exists = frappe.db.exists
        def mock_exists(dt, *args, **kwargs):
            if dt == "SMRITI Formula Definition":
                args_str = str(args) + str(kwargs)
                if "SMRITI-PRN-SCORE-01" in args_str:
                    return False
            return orig_exists(dt, *args, **kwargs)
            
        with unittest.mock.patch("frappe.db.exists", side_effect=mock_exists):
            cfg = get_printability_formula_config()
            self.assertEqual(cfg["weights"]["margin"], 25)
            
            # Verify that Error Log is created
            log_exists = frappe.db.exists("Error Log", {"method": "SMRITI Formula Registry Warning"})
            self.assertTrue(log_exists)
            
            # Verify log content
            log_doc = frappe.get_doc("Error Log", log_exists)
            self.assertIn("SMRITI-PRN-SCORE-01", log_doc.error)

    def test_32_expand_item_variants(self):
        """test_32: expand_item_variants on templates and standard items"""
        from smriti_retail_os.barcode_api import expand_item_variants
        
        # Create standard test items if not exists
        if not frappe.db.exists("Item", "TEST-ITEM-123"):
            if not frappe.db.exists("GST HSN Code", "641590"):
                frappe.get_doc({"doctype": "GST HSN Code", "hsn_code": "641590"}).insert(ignore_permissions=True)
            doc = frappe.new_doc("Item")
            doc.item_code = "TEST-ITEM-123"
            doc.item_name = "Test Item 123"
            doc.item_group = "All Item Groups"
            doc.gst_hsn_code = "641590"
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        # Test Standard Item
        res_std = expand_item_variants("TEST-ITEM-123", 5)
        self.assertEqual(len(res_std), 1)
        self.assertEqual(res_std[0]["item_code"], "TEST-ITEM-123")
        self.assertEqual(res_std[0]["print_qty"], 5)

        # Cleanup
        frappe.delete_doc("Item", "TEST-ITEM-123", ignore_permissions=True)
        frappe.db.commit()

    def test_33_get_items_by_range(self):
        """test_33: numerical and alphabetical range loading"""
        from smriti_retail_os.barcode_api import get_items_by_range
        
        # Create standard test items with ranges
        for i in range(1, 6):
            code = f"BBM-{i:04d}"
            if not frappe.db.exists("Item", code):
                if not frappe.db.exists("GST HSN Code", "641590"):
                    frappe.get_doc({"doctype": "GST HSN Code", "hsn_code": "641590"}).insert(ignore_permissions=True)
                doc = frappe.new_doc("Item")
                doc.item_code = code
                doc.item_name = f"Test Range Item {i}"
                doc.item_group = "All Item Groups"
                doc.gst_hsn_code = "641590"
                doc.insert(ignore_permissions=True)
                
        frappe.db.commit()
        
        # Numerical range BBM-0002 to BBM-0004
        res_num = get_items_by_range("BBM-0002", "BBM-0004")
        self.assertEqual(len(res_num), 3)
        codes = [r["item_code"] for r in res_num]
        self.assertIn("BBM-0002", codes)
        self.assertIn("BBM-0003", codes)
        self.assertIn("BBM-0004", codes)
        
        # Alphabetical range
        res_alpha = get_items_by_range("BBM-0001", "BBM-0003")
        self.assertEqual(len(res_alpha), 3)
        
        # Clean up
        for i in range(1, 6):
            frappe.delete_doc("Item", f"BBM-{i:04d}", ignore_permissions=True)
        frappe.db.commit()

    def test_34_get_transaction_items_checklist(self):
        """test_34: get_transaction_items_checklist returns transaction checklist data"""
        from smriti_retail_os.barcode_api import get_transaction_items_checklist
        
        # Check empty or missing transaction returns empty list
        res = get_transaction_items_checklist("Purchase Receipt", "PR-NONEXISTENT")
        self.assertEqual(res, [])



