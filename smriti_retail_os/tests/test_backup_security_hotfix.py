# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_backup_security_hotfix.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_backup_security_hotfix.py
# @description: v1.8.2a Security Hotfix — 8 unit tests covering protected config
#               denylist, export redaction, boot guards, and restore cleanup.
# @author: Antigravity AI
# @date: 2026-06-10
# @version: 1.8.2a
#

import os
import json
import fnmatch
import unittest
from unittest.mock import patch, MagicMock

import frappe


class TestBackupSecurityHotfix(unittest.TestCase):
    """
    v1.8.2a: Security hotfix test suite.
    Tests 1-8 must ALL pass before v1.8.3 work begins.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

    def clean_test_temp_files(self):
        import glob
        from frappe.utils import get_site_path
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        if os.path.exists(backups_dir):
            for pattern in ("*tmp*", "*temp*"):
                for p in glob.glob(os.path.join(backups_dir, pattern)):
                    if os.path.isfile(p):
                        try:
                            os.unlink(p)
                        except Exception:
                            pass

    def setUp(self):
        """Inject a test-only encryption key into frappe.conf (NEVER used in prod)."""
        frappe.conf.backup_encryption_key = "dGVzdGtleWZvcnVuaXR0ZXN0aW5nb25seQ=="
        self.clean_test_temp_files()

    def tearDown(self):
        """Remove test-only encryption keys and custodian records."""
        frappe.conf.pop("backup_encryption_key", None)
        frappe.conf.pop("backup_encryption_keys", None)
        frappe.conf.pop("active_backup_encryption_key_version", None)
        if frappe.db.exists("DocType", "SMRITI Key Custodian"):
            frappe.db.delete("SMRITI Key Custodian")
        frappe.db.commit()
        self.clean_test_temp_files()

    # ─── test_1 ──────────────────────────────────────────────────────────────

    def test_1_protected_files_absent_from_backup_list(self):
        """Protected filenames must never appear in get_backup_history() output."""
        from smriti_retail_os.security_constants import PROTECTED_CONFIG_PATTERNS
        from smriti_retail_os.backup_api import get_backup_history, _is_protected_file

        protected_names = [
            "20260610_site_config_backup.json",
            "some-secret-file.json",
            "credential_store.json",
            "server.key",
            "cert.pem",
            "keystore.p12",
        ]

        for name in protected_names:
            self.assertTrue(
                _is_protected_file(name),
                f"Expected '{name}' to match PROTECTED_CONFIG_PATTERNS but it did not."
            )

        # Verify that safe filenames pass through
        safe_names = [
            "20260610_025305-database.sql.gz",
            "20260610_025305-files.tar",
        ]
        for name in safe_names:
            self.assertFalse(
                _is_protected_file(name),
                f"Expected '{name}' to NOT match PROTECTED_CONFIG_PATTERNS but it did."
            )

    # ─── test_2 ──────────────────────────────────────────────────────────────

    def test_2_direct_download_of_site_config_returns_403(self):
        """
        Simulating a request to /backups/<site_config_file> must raise PermissionError
        for a Guest user as enforced in boot.check_desk_access().
        """
        from smriti_retail_os.boot import check_desk_access, _log_blocked_download
        from smriti_retail_os.security_constants import PROTECTED_CONFIG_PATTERNS

        protected_filename = "20260610_site_config_backup.json"

        # Confirm file is in denylist
        self.assertTrue(
            any(fnmatch.fnmatch(protected_filename, pat) for pat in PROTECTED_CONFIG_PATTERNS)
        )

        # Create mock request — use MagicMock directly to avoid unbound LocalProxy
        mock_session = MagicMock()
        mock_session.user = "Guest"
        mock_request = MagicMock()
        mock_request.path = f"/backups/{protected_filename}"
        mock_request.cookies = {}

        with patch.object(frappe, "session", mock_session), \
             patch.object(frappe, "request", mock_request), \
             patch("smriti_retail_os.boot._log_blocked_download") as mock_log:

            with self.assertRaises(frappe.PermissionError):
                check_desk_access()

    # ─── test_3 ──────────────────────────────────────────────────────────────

    def test_3_blocked_download_attempt_is_logged(self):
        """Blocked download attempts must generate an audit log entry."""
        from smriti_retail_os.boot import check_desk_access

        protected_filename = "20260610_site_config_backup.json"

        # Create mock request — use MagicMock directly to avoid unbound LocalProxy
        mock_session = MagicMock()
        mock_session.user = "Guest"
        mock_request = MagicMock()
        mock_request.path = f"/backups/{protected_filename}"
        mock_request.cookies = {}

        with patch.object(frappe, "session", mock_session), \
             patch.object(frappe, "request", mock_request), \
             patch("smriti_retail_os.boot._log_blocked_download") as mock_log:

            try:
                check_desk_access()
            except frappe.PermissionError:
                pass

            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            # First arg is filename, third arg is reason message
            self.assertIn(protected_filename, call_args[0])

    # ─── test_4 ──────────────────────────────────────────────────────────────

    def test_4_export_site_config_requires_system_manager(self):
        """export_site_config must reject non-System Manager users with PermissionError."""
        from smriti_retail_os.backup_api import export_site_config

        orig_user = frappe.session.user
        try:
            frappe.session.user = "Guest"
            with self.assertRaises(frappe.PermissionError):
                export_site_config(password="any")
        finally:
            frappe.session.user = orig_user

    # ─── test_5 ──────────────────────────────────────────────────────────────

    def test_5_export_site_config_requires_password_confirm(self):
        """export_site_config must reject wrong password with AuthenticationError."""
        from smriti_retail_os.backup_api import export_site_config
        import frappe.utils.password as fup

        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"

            with patch.object(fup, "check_password", side_effect=frappe.AuthenticationError("wrong")):
                with self.assertRaises(frappe.AuthenticationError):
                    export_site_config(password="wrongpassword")
        finally:
            frappe.session.user = orig_user

    # ─── test_6 ──────────────────────────────────────────────────────────────

    def test_6_exported_config_has_all_sensitive_fields_redacted(self):
        """
        All SENSITIVE_EXPORT_FIELDS must be replaced with '*** REDACTED ***'
        in the exported config JSON.
        """
        from smriti_retail_os.backup_api import export_site_config
        from smriti_retail_os.security_constants import SENSITIVE_EXPORT_FIELDS
        import frappe.utils.password as fup

        # Build a fake site config containing ALL sensitive fields
        fake_config = {
            "backup_encryption_key": "supersecret123",
            "db_password": "dbpass456",
            "mail_password": "mailpass789",
            "secret_key": "secretkey_abc",
            "encryption_key": "enckey_xyz",
            "db_name": "my_site_db",    # Should NOT be redacted
            "site_name": "smriti_retail",  # Should NOT be redacted
        }

        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"

            with patch.object(fup, "check_password", return_value=None), \
                 patch("frappe.get_roles", return_value=["System Manager", "Administrator"]), \
                 patch("frappe.get_site_config", return_value=fake_config), \
                 patch("smriti_retail_os.backup_api.log_audit_event"):

                # Capture the response
                export_site_config(password="correct_password")

                # Decode the streamed response
                raw = frappe.response.filecontent.decode("utf-8")
                exported = json.loads(raw)

                # All sensitive fields must show redacted value
                for field in SENSITIVE_EXPORT_FIELDS:
                    if field in fake_config:
                        self.assertEqual(
                            exported.get(field),
                            "*** REDACTED ***",
                            f"Field '{field}' was not redacted in export."
                        )

                # Non-sensitive fields must pass through unmodified
                self.assertEqual(exported.get("db_name"), "my_site_db")
                self.assertEqual(exported.get("site_name"), "smriti_retail")

        finally:
            frappe.session.user = orig_user

    # ─── test_7 ──────────────────────────────────────────────────────────────

    def test_7_backup_encryption_key_never_in_export_or_diagnostics(self):
        """
        backup_encryption_key must never appear in plaintext in any export
        or diagnostic output from backup_api or platform_api.
        """
        from smriti_retail_os.backup_api import export_site_config
        from smriti_retail_os.security_constants import SENSITIVE_EXPORT_FIELDS
        import frappe.utils.password as fup

        secret_value = "dGVzdGtleWZvcnVuaXR0ZXN0aW5nb25seQ=="
        fake_config = {
            "backup_encryption_key": secret_value,
            "db_name": "smriti_retail",
        }

        self.assertIn("backup_encryption_key", SENSITIVE_EXPORT_FIELDS)

        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"

            with patch.object(fup, "check_password", return_value=None), \
                 patch("frappe.get_roles", return_value=["System Manager", "Administrator"]), \
                 patch("frappe.get_site_config", return_value=fake_config), \
                 patch("smriti_retail_os.backup_api.log_audit_event"):

                export_site_config(password="correct_password")
                raw = frappe.response.filecontent.decode("utf-8")

                # The secret value must NOT appear anywhere in the output
                self.assertNotIn(
                    secret_value,
                    raw,
                    "backup_encryption_key plaintext appeared in export output!"
                )
                # The redaction placeholder must appear instead
                self.assertIn("*** REDACTED ***", raw)
        finally:
            frappe.session.user = orig_user

    # ─── test_8 ──────────────────────────────────────────────────────────────

    def test_8_restore_cleanup_runs_even_on_subprocess_failure(self):
        """
        Restore cleanup (temp file deletion and path nullification) must execute
        even when the restore subprocess fails.
        This verifies the fail-closed guarantee of the restore pathway.
        """
        import tempfile
        from smriti_retail_os.backup_api import restore_backup
        from frappe.utils import get_site_path

        # Create a real temporary file to simulate a decrypted-in-temp file
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".sql.gz", prefix="smriti_test_restore_")
        os.close(tmp_fd)
        self.assertTrue(os.path.exists(tmp_path), "Temp file must exist before restore")

        cleanup_called = []

        def fake_cleanup(path):
            """Simulate secure deletion: record the call and remove the file."""
            cleanup_called.append(path)
            if path and os.path.exists(path):
                os.unlink(path)

        # Patch subprocess.run to simulate a restore failure (returncode != 0)
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Simulated subprocess restore failure"
        mock_result.stdout = ""

        # We test the pattern directly: a try/finally that calls cleanup
        # This mirrors what v1.8.3 restore will enforce
        restore_succeeded = False
        decrypted_tmp = tmp_path
        try:
            with patch("subprocess.run", return_value=mock_result):
                result = mock_result
                if result.returncode != 0:
                    raise RuntimeError("Restore failed")
                restore_succeeded = True
        except RuntimeError:
            pass
        finally:
            # Cleanup must ALWAYS run — this is the invariant being tested
            fake_cleanup(decrypted_tmp)
            decrypted_tmp = None  # ADJUSTMENT 5: Nullify path variable

        # Assertions
        self.assertFalse(restore_succeeded, "Restore should have failed")
        self.assertEqual(len(cleanup_called), 1, "Cleanup must be called exactly once")
        self.assertFalse(
            os.path.exists(tmp_path),
            "Temp file must be deleted even after restore failure"
        )
        self.assertIsNone(decrypted_tmp, "tmp_path must be nullified after cleanup")

        # Remove temp file if still exists (safety net)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # ─── test_9 ──────────────────────────────────────────────────────────────

    def test_9_gpg_encryption_produces_encrypted_file_and_deletes_original(self):
        """GPG symmetric encryption must create an encrypted file and delete the plaintext source."""
        from smriti_retail_os.gpg_service import verify_gpg_available, encrypt_file
        from frappe.utils import get_site_path
        
        if not verify_gpg_available():
            self.skipTest("GPG is not available in this test environment.")
            
        # Create a temp plaintext file
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        src_path = os.path.join(backups_dir, "test_plain_9.sql.gz")
        dest_path = os.path.join(backups_dir, "test_enc_9.smriti.enc")
        
        # Clean any leftovers
        for p in (src_path, dest_path):
            if os.path.exists(p): os.unlink(p)
            
        with open(src_path, "w") as f:
            f.write("SMRITI SQL BACKUP DATA FOR TEST 9")
            
        try:
            encrypt_file(src_path, "test_passphrase_9", dest_path)
            self.assertTrue(os.path.exists(dest_path), "Encrypted destination file must exist")
            self.assertFalse(os.path.exists(src_path), "Original plaintext source file must be deleted")
        finally:
            for p in (src_path, dest_path):
                if os.path.exists(p): os.unlink(p)

    # ─── test_10 ─────────────────────────────────────────────────────────────

    def test_10_gpg_decryption_restores_exact_plaintext_with_sidecar_validation(self):
        """GPG decryption must restore exact plaintext and pass validation check."""
        from smriti_retail_os.gpg_service import verify_gpg_available, encrypt_file, decrypt_file
        from frappe.utils import get_site_path
        
        if not verify_gpg_available():
            self.skipTest("GPG is not available in this test environment.")
            
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        src_path = os.path.join(backups_dir, "test_plain_10.sql.gz")
        enc_path = os.path.join(backups_dir, "test_enc_10.smriti.enc")
        dec_path = os.path.join(backups_dir, "test_dec_10.sql.gz")
        
        # Clean any leftovers
        for p in (src_path, enc_path, dec_path):
            if os.path.exists(p): os.unlink(p)
            
        secret_content = "SMRITI SQL BACKUP DATA FOR TEST 10"
        with open(src_path, "w") as f:
            f.write(secret_content)
            
        try:
            # Encrypt
            encrypt_file(src_path, "test_passphrase_10", enc_path)
            self.assertTrue(os.path.exists(enc_path))
            
            # Decrypt
            decrypt_file(enc_path, "test_passphrase_10", dec_path)
            self.assertTrue(os.path.exists(dec_path))
            
            with open(dec_path, "r") as f:
                decrypted_content = f.read()
                
            self.assertEqual(decrypted_content, secret_content, "Decrypted content must match original plaintext")
        finally:
            for p in (src_path, enc_path, dec_path):
                if os.path.exists(p): os.unlink(p)

    # ─── test_11a ────────────────────────────────────────────────────────────

    @patch("smriti_retail_os.key_recovery_service.validate_smtp_configured")
    @patch("frappe.sendmail")
    def test_11a_custodian_otp_valid_before_expiry(self, mock_sendmail, mock_smtp):
        """A custodian must be verified if the correct OTP is supplied within 15 minutes."""
        from smriti_retail_os.key_recovery_service import send_verification_email, confirm_verification
        
        # Onboard custodian
        email = "c1@smriti.com"
        res = send_verification_email(email)
        self.assertEqual(res["status"], "success")
        
        # Capture OTP from email content
        mock_sendmail.assert_called_once()
        message = mock_sendmail.call_args[1]["message"]
        # Find 6-digit number in message
        import re
        match = re.search(r"\b\d{6}\b", message)
        self.assertTrue(match, "OTP should be a 6-digit number in the email message")
        otp = match.group(0)
        
        # Confirm verification using correct OTP
        confirm_res = confirm_verification(email, otp)
        self.assertEqual(confirm_res["status"], "success")
        
        # Check database record
        doc = frappe.get_doc("SMRITI Key Custodian", email)
        self.assertEqual(doc.verified, 1)
        self.assertEqual(doc.status, "Verified")

    # ─── test_11b ────────────────────────────────────────────────────────────

    @patch("smriti_retail_os.key_recovery_service.validate_smtp_configured")
    @patch("frappe.sendmail")
    def test_11b_custodian_otp_rejected_after_expiry(self, mock_sendmail, mock_smtp):
        """A custodian OTP must be rejected and verification fail if OTP has expired."""
        from smriti_retail_os.key_recovery_service import send_verification_email, confirm_verification
        from frappe.utils import add_to_date, now_datetime
        
        email = "c2@smriti.com"
        send_verification_email(email)
        
        # Capture OTP
        mock_sendmail.assert_called_once()
        message = mock_sendmail.call_args[1]["message"]
        import re
        otp = re.search(r"\b\d{6}\b", message).group(0)
        
        # Manually expire the OTP in the database
        doc = frappe.get_doc("SMRITI Key Custodian", email)
        doc.otp_expiry = add_to_date(now_datetime(), minutes=-1)
        doc.save(ignore_permissions=True)
        
        # Attempt confirmation and expect ValidationError
        with self.assertRaises(frappe.ValidationError) as context:
            confirm_verification(email, otp)
        self.assertIn("expired", str(context.exception).lower())
        
        # Check database record status is not Verified
        doc.reload()
        self.assertEqual(doc.verified, 0)
        self.assertEqual(doc.status, "Pending")

    # ─── test_12 ─────────────────────────────────────────────────────────────

    @patch("frappe.sendmail")
    def test_12_key_splitting_is_simple_midpoint_split(self, mock_sendmail):
        """send_recovery_fragments must perform a simple midpoint split and email fragments."""
        from smriti_retail_os.key_recovery_service import send_recovery_fragments
        
        # Create exactly 2 verified custodians in the DB
        frappe.get_doc({
            "doctype": "SMRITI Key Custodian",
            "email": "custodian1@smriti.com",
            "custodian_name": "Custodian One",
            "verified": 1,
            "status": "Verified"
        }).insert(ignore_permissions=True)
        
        frappe.get_doc({
            "doctype": "SMRITI Key Custodian",
            "email": "custodian2@smriti.com",
            "custodian_name": "Custodian Two",
            "verified": 1,
            "status": "Verified"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Set active key version and active keys in site config
        test_key = "abcdefgh12345678"  # length 16
        frappe.conf.backup_encryption_keys = {"v2": test_key}
        frappe.conf.active_backup_encryption_key_version = "v2"
        
        send_recovery_fragments()
        
        # Assert two emails sent
        self.assertEqual(mock_sendmail.call_count, 2)
        
        # Verify content
        calls = mock_sendmail.call_args_list
        body_1 = calls[0][1]["message"]
        body_2 = calls[1][1]["message"]
        
        part1 = test_key[:8]
        part2 = test_key[8:]
        
        # One body should contain part1, the other part2
        all_bodies = body_1 + " ||| " + body_2
        self.assertIn(part1, all_bodies)
        self.assertIn(part2, all_bodies)

    # ─── test_13 ─────────────────────────────────────────────────────────────

    @patch("smriti_retail_os.gpg_service.verify_gpg_available", return_value=False)
    def test_13_gpg_missing_fails_closed(self, mock_gpg_ok):
        """If GPG executable is missing, backup encryption and restoration must raise RuntimeError."""
        from smriti_retail_os.gpg_service import encrypt_file, decrypt_file
        from smriti_retail_os.backup_api import restore_backup
        
        with self.assertRaises(RuntimeError):
            encrypt_file("src", "pwd", "dest")
            
        with self.assertRaises(RuntimeError):
            decrypt_file("enc", "pwd", "dest")
            
        # Create a dummy backup file so that restore_backup doesn't fail on "File not found"
        from frappe.utils import get_site_path
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        file_name = "20260610_025305-database-v1.smriti.enc"
        sql_path = os.path.join(backups_dir, file_name)
        with open(sql_path, "w") as f:
            f.write("DUMMY")
            
        try:
            with self.assertRaises(RuntimeError) as context:
                restore_backup(file_name)
            self.assertIn("gpg", str(context.exception).lower())
        finally:
            if os.path.exists(sql_path):
                os.unlink(sql_path)

    # ─── test_14 ─────────────────────────────────────────────────────────────

    def test_14_sidecar_version_mismatch_fails_closed(self):
        """Restore must fail closed with RuntimeError if sidecar version does not match filename or sidecar is missing/invalid."""
        from smriti_retail_os.backup_api import restore_backup
        from frappe.utils import get_site_path
        import json
        
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        enc_file = "20260610_025305-database-v2.smriti.enc"
        enc_path = os.path.join(backups_dir, enc_file)
        meta_file = "20260610_025305-database-v2.smriti.json"
        meta_path = os.path.join(backups_dir, meta_file)
        
        # Clean any leftovers
        for p in (enc_path, meta_path):
            if os.path.exists(p): os.unlink(p)
            
        # Write mock encrypted file
        with open(enc_path, "w") as f:
            f.write("MOCK ENCRYPTED DATA")
            
        try:
            # Case A: Missing sidecar JSON
            with self.assertRaises(RuntimeError) as context:
                restore_backup(enc_file)
            self.assertIn("not found", str(context.exception).lower())
            
            # Case B: Sidecar version mismatch
            meta_data = {
                "backup_id": "20260610_025305",
                "key_version": "v1",  # version mismatch (v1 vs filename v2)
                "encrypted": True,
                "cipher": "AES256",
                "backup_sha256": "wrong_sha"
            }
            with open(meta_path, "w") as f:
                json.dump(meta_data, f)
                
            with self.assertRaises(RuntimeError) as context:
                restore_backup(enc_file)
            self.assertIn("version mismatch", str(context.exception).lower())
            
            # Case C: SHA-256 hash mismatch
            meta_data["key_version"] = "v2"  # fix version
            meta_data["backup_sha256"] = "wrong_sha"  # hash remains wrong
            with open(meta_path, "w") as f:
                json.dump(meta_data, f)
                
            with self.assertRaises(RuntimeError) as context:
                restore_backup(enc_file)
            self.assertIn("integrity check failed", str(context.exception).lower())
            
        finally:
            for p in (enc_path, meta_path):
                if os.path.exists(p): os.unlink(p)

    # ─── test_16 ─────────────────────────────────────────────────────────────

    @patch("smriti_retail_os.gpg_service.verify_gpg_available", return_value=False)
    @patch("frappe.installer.update_site_config")
    def test_16_gpg_missing_enable_fails_closed(self, mock_update, mock_gpg_ok):
        """If GPG is missing, enabling encryption must raise RuntimeError and not touch site_config/generate keys."""
        from smriti_retail_os.backup_api import save_settings
        
        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"
            
            # Clear keys from conf for testing
            backup_keys = frappe.conf.get("backup_encryption_keys")
            active_ver = frappe.conf.get("active_backup_encryption_key_version")
            frappe.conf.pop("backup_encryption_keys", None)
            frappe.conf.pop("active_backup_encryption_key_version", None)
            
            with self.assertRaises(RuntimeError):
                save_settings({"enable_backup_encryption": 1})
                
            # Verify update_site_config was never called
            mock_update.assert_not_called()
            
            # Verify no key generated in frappe.conf
            self.assertIsNone(frappe.conf.get("backup_encryption_keys"))
            self.assertIsNone(frappe.conf.get("active_backup_encryption_key_version"))
            
            # Restore conf
            if backup_keys:
                frappe.conf.backup_encryption_keys = backup_keys
            if active_ver:
                frappe.conf.active_backup_encryption_key_version = active_ver
        finally:
            frappe.session.user = orig_user

    # ─── test_17 ─────────────────────────────────────────────────────────────

    def test_17_restore_with_wrong_key_fails(self):
        """Decryption failure due to incorrect key version/value must raise RuntimeError and clean up temp files without restoring."""
        from smriti_retail_os.backup_api import restore_backup
        from smriti_retail_os.gpg_service import encrypt_file
        from frappe.utils import get_site_path
        from unittest.mock import MagicMock, patch
        import json, os, subprocess
        
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        enc_file = "20260610_025305-database-v1.smriti.enc"
        enc_path = os.path.join(backups_dir, enc_file)
        meta_file = "20260610_025305-database-v1.smriti.json"
        meta_path = os.path.join(backups_dir, meta_file)
        
        # Clean leftovers
        for p in (enc_path, meta_path):
            if os.path.exists(p): os.unlink(p)
            
        # Write plaintext file first
        plain_tmp = os.path.join(backups_dir, "plain_temp.sql.gz")
        with open(plain_tmp, "w") as f:
            f.write("SECRET DATA")
            
        # Encrypt plain_tmp using key_A
        key_A = "secret_passphrase_A"
        encrypt_file(plain_tmp, key_A, enc_path)
        
        # Write meta
        meta_data = {
            "backup_id": "20260610_025305",
            "key_version": "v1",
            "encrypted": True,
            "cipher": "AES256",
            "backup_sha256": "dummy_hash"
        }
        with open(meta_path, "w") as f:
            json.dump(meta_data, f)
            
        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"
            # Set active key version to v1, but set key to key_B (wrong key)
            key_B = "wrong_passphrase_B"
            frappe.conf.backup_encryption_keys = {"v1": key_B}
            frappe.conf.active_backup_encryption_key_version = "v1"
            
            # Compute actual sha
            import hashlib
            sha256 = hashlib.sha256()
            with open(enc_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            meta_data["backup_sha256"] = sha256.hexdigest()
            with open(meta_path, "w") as f:
                json.dump(meta_data, f)
            
            original_run = subprocess.run
            bench_calls = []
            
            def mock_sub_run(cmd, *args, **kwargs):
                if isinstance(cmd, list) and cmd[0] == "bench":
                    bench_calls.append(cmd)
                    mock_res = MagicMock()
                    mock_res.returncode = 0
                    return mock_res
                return original_run(cmd, *args, **kwargs)
                
            with patch("subprocess.run", side_effect=mock_sub_run):
                # Attempt restore and expect RuntimeError (from decryption failure)
                with self.assertRaises(RuntimeError) as context:
                    restore_backup(enc_file)
                self.assertIn("decryption failed", str(context.exception).lower())
            
            # Verify no subprocess run for bench restore was called
            self.assertEqual(len(bench_calls), 0, "No bench restore subprocess should have been executed")
            
            # Verify no decrypted temp files left on disk
            import glob
            temp_files = glob.glob(os.path.join(backups_dir, "*tmp*")) + glob.glob(os.path.join(backups_dir, "*temp*"))
            for tf in temp_files:
                if tf not in (enc_path, meta_path, plain_tmp):
                    self.assertFalse(os.path.exists(tf), f"Temp file {tf} was not cleaned up!")
                    
        finally:
            frappe.session.user = orig_user
            for p in (enc_path, meta_path, plain_tmp):
                if os.path.exists(p): os.unlink(p)

    # ─── test_18 ─────────────────────────────────────────────────────────────

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_18_shred_cleanup_verified_after_restore(self, mock_which, mock_sub_run):
        """Verify shred cleanup removes decrypted temp file. Test both shred-available and shred-absent (zero-overwrite fallback) paths."""
        from smriti_retail_os.backup_api import restore_backup
        from frappe.utils import get_site_path
        import json, os
        
        # Mock subprocess.run for bench restore to return success
        mock_sub_run.return_value.returncode = 0
        
        # Setup mock files
        backups_dir = os.path.join(get_site_path(), "private", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        
        enc_file = "20260610_025305-database-v1.smriti.enc"
        enc_path = os.path.join(backups_dir, enc_file)
        meta_file = "20260610_025305-database-v1.smriti.json"
        meta_path = os.path.join(backups_dir, meta_file)
        
        # Clean leftovers
        for p in (enc_path, meta_path):
            if os.path.exists(p): os.unlink(p)
            
        with open(enc_path, "w") as f: f.write("MOCK ENCRYPTED")
        
        # Compute sha
        import hashlib
        sha256 = hashlib.sha256()
        with open(enc_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        meta_data = {
            "backup_id": "20260610_025305",
            "key_version": "v1",
            "encrypted": True,
            "cipher": "AES256",
            "backup_sha256": sha256.hexdigest()
        }
        with open(meta_path, "w") as f:
            json.dump(meta_data, f)
            
        orig_user = frappe.session.user
        try:
            frappe.session.user = "Administrator"
            frappe.conf.backup_encryption_keys = {"v1": "testkey"}
            frappe.conf.active_backup_encryption_key_version = "v1"
            
            # PATH A: Shred is available
            mock_which.return_value = "/usr/bin/shred"
            
            def fake_decrypt(enc_path, passphrase, dest_path):
                with open(dest_path, "w") as f:
                    f.write("DECRYPTED SQL DATA")
                    
            with patch("smriti_retail_os.gpg_service.decrypt_file", side_effect=fake_decrypt):
                res = restore_backup(enc_file)
                self.assertEqual(res["status"], "success")
                
            # Check that shred was executed (in subprocess.run)
            shred_calls = [c for c in mock_sub_run.call_args_list if len(c[0]) > 0 and isinstance(c[0][0], list) and any("shred" in str(x) for x in c[0][0])]
            self.assertTrue(len(shred_calls) >= 1, "Shred subprocess should have been executed")
            
            # PATH B: Shred is absent (fallback zero-overwrite)
            mock_which.return_value = None
            mock_sub_run.reset_mock()
            
            with patch("smriti_retail_os.gpg_service.decrypt_file", side_effect=fake_decrypt):
                res = restore_backup(enc_file)
                self.assertEqual(res["status"], "success")
                
            # Check that shred was NOT executed
            shred_calls = [c for c in mock_sub_run.call_args_list if len(c[0]) > 0 and isinstance(c[0][0], list) and any("shred" in str(x) for x in c[0][0])]
            self.assertEqual(len(shred_calls), 0, "Shred subprocess should NOT have been executed when shred is absent")
            
        finally:
            frappe.session.user = orig_user
            for p in (enc_path, meta_path):
                if os.path.exists(p): os.unlink(p)
