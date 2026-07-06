# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_audit_fixes.py
# @description: Audit fix verification tests — validates remediation patches.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/tests/test_audit_fixes.py
# @description: Regression and verification tests for Deep Audit report fixes.
# @author: Antigravity AI
# @date: 2026-06-12
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import os
import unittest
from unittest.mock import patch, MagicMock
import frappe
import werkzeug.routing.exceptions

class TestAuditFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure SMRITI roles and profiles exist
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

        # Create a test cashier user if not exists
        if not frappe.db.exists("User", "test_cashier@smriti.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "test_cashier@smriti.com",
                "first_name": "Test Cashier",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            user.add_roles("SMRITI Cashier")
            frappe.db.commit()

        # Create a test manager user if not exists
        if not frappe.db.exists("User", "test_manager@smriti.com"):
            user = frappe.get_doc({
                "doctype": "User",
                "email": "test_manager@smriti.com",
                "first_name": "Test Manager",
                "send_welcome_email": 0
            })
            user.insert(ignore_permissions=True)
            user.add_roles("SMRITI Store Manager")
            frappe.db.commit()

        # Set dedicated PIN in both tabPassword and User table
        from frappe.utils.password import update_password
        update_password("test_manager@smriti.com", "123456", fieldname="custom_smriti_pin")
        frappe.db.set_value("User", "test_manager@smriti.com", "custom_smriti_pin", "123456")
        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        if frappe.db.exists("User", "test_cashier@smriti.com"):
            frappe.db.delete("User", {"email": "test_cashier@smriti.com"})
        if frappe.db.exists("User", "test_manager@smriti.com"):
            frappe.db.delete("User", {"email": "test_manager@smriti.com"})
        frappe.db.commit()
        super().tearDownClass()

    def setUp(self):
        self.orig_user = frappe.session.user
        frappe.session.user = "test_cashier@smriti.com"
        frappe.cache().delete(f"smriti_pin_attempts:{frappe.session.user}")

    def tearDown(self):
        frappe.cache().delete(f"smriti_pin_attempts:{frappe.session.user}")
        frappe.session.user = self.orig_user

    # ─── PIN Rate Limiting Tests ──────────────────────────────────────────────

    def test_manager_override_pin_rate_limiting(self):
        """validate_manager_override must block after 5 failed PIN attempts."""
        from smriti_retail_os.billing_api import validate_manager_override

        # Check rate limiting key is empty initially
        key = f"smriti_pin_attempts:{frappe.session.user}"
        self.assertIsNone(frappe.cache().get(key))

        # Perform 5 failed attempts
        for i in range(5):
            res = validate_manager_override("999999", "Test Override Action")
            self.assertFalse(res.get("authorized"))
            self.assertEqual(int(frappe.cache().get(key)), i + 1)

        # 6th attempt must raise PermissionError (Too many failed attempts)
        with self.assertRaises(frappe.PermissionError):
            validate_manager_override("999999", "Test Override Action")

    def test_manager_override_pin_success_clears_attempts(self):
        """Successful PIN validation must clear the attempts counter in Redis."""
        from smriti_retail_os.billing_api import validate_manager_override

        key = f"smriti_pin_attempts:{frappe.session.user}"

        # 3 failed attempts
        for _ in range(3):
            validate_manager_override("999999", "Test Action")
        self.assertEqual(int(frappe.cache().get(key)), 3)

        # 1 successful attempt
        res = validate_manager_override("123456", "Test Action")
        self.assertTrue(res.get("authorized"))
        self.assertEqual(res.get("manager"), "test_manager@smriti.com")

        # Key must be deleted
        self.assertIsNone(frappe.cache().get(key))

    def test_shift_manager_pin_rate_limiting(self):
        """_validate_manager_pin must block after 5 failed PIN attempts."""
        from smriti_retail_os.shift_api import _validate_manager_pin

        key = f"smriti_pin_attempts:{frappe.session.user}"

        # Perform 5 failed attempts
        for i in range(5):
            res = _validate_manager_pin("999999", "Test Shift Action")
            self.assertFalse(res.get("authorized"))
            self.assertEqual(int(frappe.cache().get(key)), i + 1)

        # 6th attempt must raise PermissionError
        with self.assertRaises(frappe.PermissionError):
            _validate_manager_pin("999999", "Test Shift Action")

    def test_pin_failure_error_logging(self):
        """Failed PIN override attempts must create records in Frappe's Error Log."""
        from smriti_retail_os.billing_api import validate_manager_override

        # Clear existing logs for testing clean state
        frappe.db.delete("Error Log", {"method": "SMRITI Failed PIN Override Attempt"})
        frappe.db.commit()

        # Submit wrong PIN
        res = validate_manager_override("wrongpin", "Test Action")
        self.assertFalse(res.get("authorized"))

        # Verify entry created in Error Log
        logs = frappe.get_all("Error Log", filters={"method": "SMRITI Failed PIN Override Attempt"})
        self.assertTrue(len(logs) >= 1)

    # ─── Password Length Test ─────────────────────────────────────────────────

    def test_password_minimum_length_enforcement(self):
        """Password resets must reject strings shorter than 8 characters."""
        from smriti_retail_os.security_api import reset_user_password

        # Mock the updates/permission validation to let reset_user_password run
        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"
            # 7 chars should fail
            with self.assertRaises(frappe.ValidationError):
                reset_user_password("test_cashier@smriti.com", "1234567")

            # 8 chars should pass
            res = reset_user_password("test_cashier@smriti.com", "12345678")
            self.assertTrue(res.get("success"))
        finally:
            frappe.session.user = orig_user

    # ─── Desk Guard Redirect Test ─────────────────────────────────────────────

    def test_desk_guard_redirect_logic(self):
        """check_desk_access must redirect Cashiers attempting to access raw Desk paths."""
        from smriti_retail_os.boot import check_desk_access

        mock_session = MagicMock()
        mock_session.user = "test_cashier@smriti.com"

        mock_request = MagicMock()
        mock_request.path = "/desk"
        mock_request.cookies = {}

        # Set user roles to mock cashier
        with patch.object(frappe, "session", mock_session), \
             patch.object(frappe, "request", mock_request), \
             patch("frappe.get_roles", return_value=["SMRITI Cashier"]), \
             patch("smriti_retail_os.boot._log_blocked_download"):

            with self.assertRaises(werkzeug.routing.exceptions.RequestRedirect):
                check_desk_access()

    # ─── Enqueue Path Test ───────────────────────────────────────────────────

    def test_enqueue_post_billing_tasks_path(self):
        """Verify that correct import path is used for process_post_billing_tasks."""
        # This checks that importing from the enqueued module name is valid
        try:
            from smriti_retail_os.billing_api import process_post_billing_tasks
            self.assertTrue(callable(process_post_billing_tasks))
        except ImportError:
            self.fail("Could not import process_post_billing_tasks from smriti_retail_os.billing_api")

    # ─── Restore Validation (Unset Env Vars) Test ─────────────────────────────

    def test_restore_validation_raised_on_unset_env(self):
        """restore_backup must fail with ValidationError if MARIADB_ROOT_PASSWORD is unset."""
        from smriti_retail_os.backup_api import restore_backup

        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"
            
            # Use a dummy file that passes regex path checks
            dummy_filename = "20260610_025305-database.sql.gz"

            # Mock os.path.exists and get_site_path
            with patch("os.path.exists", return_value=True), \
                 patch.dict(os.environ, {}, clear=True):

                with self.assertRaises(frappe.ValidationError) as context:
                    restore_backup(dummy_filename)

                self.assertIn("environment variable is not set", str(context.exception))
        finally:
            frappe.session.user = orig_user
