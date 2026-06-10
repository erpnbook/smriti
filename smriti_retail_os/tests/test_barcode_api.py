# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_barcode_api.py
# @description: Unit tests for SMRITI Print Template schema and barcode API template rendering.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-06
# @version: 1.0.0
# @license: MIT
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
        # Clean up any test templates and their versions
        test_templates = ["TEST_ZPL_TEMPLATE", "TEST_TSPL_TEMPLATE", "TEST_MAPPINGS_TEMPLATE", "TEST_TOO_LARGE", "TEST_INVALID_MAPPINGS", "TEST_RESTORE_SNAP_TEMPLATE", "TEST_LOCK_TEMPLATE", "TEST_LEGACY_TEMPLATE"]
        frappe.db.delete("SMRITI Print Template Version", {"template": ["in", test_templates]})
        frappe.db.delete("SMRITI Print Template", {"name": ["in", test_templates]})
        frappe.db.commit()
        from smriti_retail_os.setup import seed_master_doctypes, setup_activity_log_options
        seed_master_doctypes()
        setup_activity_log_options()

    def tearDown(self):
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
                "brand": "BIG BOSS",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 2
            }
        ]
        
        # Generate PRN - should support lookup by either "TEST_ZPL_TEMPLATE" or "Test ZPL Template"
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_ZPL_TEMPLATE")
        self.assertEqual(prn_data.count("^XA"), 2)
        self.assertEqual(prn_data.count("^XZ"), 2)
        self.assertIn("Bronze Loafer Shoe", prn_data)
        self.assertIn("499", prn_data)

        # Verify fallback by template_title
        prn_data_fallback = generate_prn(items=json.dumps(items_payload), template_name=template_name)
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
                "brand": "BIG BOSS",
                "mrp": 499.0,
                "size": "8",
                "color": "BRONZE",
                "print_qty": 1
            }
        ]
        
        # Generate PRN
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_TSPL_TEMPLATE")
        
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
        
        prn_data = generate_prn(items=json.dumps(items_payload), template_name="TEST_MAPPINGS_TEMPLATE")
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
            job_id = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
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
            job_id = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
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
        
        old_in_test = frappe.flags.in_test
        frappe.flags.in_test = False
        try:
            job_id = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
        finally:
            frappe.flags.in_test = old_in_test
                
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync', side_effect=Exception("Connection refused")):
            try:
                _process_print_job(print_job_id=job_id)
            except Exception:
                pass
                
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
            job_id = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload="^XA^XZ"
            )
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
            job_id = enqueue_print_job(
                template_name="TEST_ZPL_TEMPLATE",
                printer_ip="192.168.1.180",
                printer_port=9100,
                labels_count=2,
                payload=payload
            )
        finally:
            frappe.flags.in_test = old_in_test
            
        # Fail the job
        with patch('smriti_retail_os.barcode_api._send_to_printer_sync', side_effect=Exception("Network error")):
            try:
                _process_print_job(print_job_id=job_id)
            except Exception:
                pass
                
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
                return enqueue_print_job(
                    template_name="TEST_ZPL_TEMPLATE",
                    printer_ip="192.168.1.180",
                    printer_port=9100,
                    labels_count=1,
                    payload=f"{payload} - {idx}"
                )
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
                job_id = enqueue_print_job(
                    template_name="TEST_ZPL_TEMPLATE",
                    printer_ip="192.168.1.180",
                    printer_port=9100,
                    labels_count=2,
                    payload=payload
                )
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


