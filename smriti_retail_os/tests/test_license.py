# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_license.py
# @description: Unit tests for SMRITI License Key Validator — Phase 1 Security Remediation.
#               Validates fail-closed behaviour of _get_secret() and core parse logic.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

from __future__ import annotations

import os
import unittest
from unittest.mock import patch, MagicMock

import frappe
import frappe.utils


class TestGetSecret(unittest.TestCase):
    """Tests for _get_secret() fail-closed behaviour."""

    def _clear_env(self, conf_patch, env_patch):
        """Helper: clear both conf and env so fallback path is taken."""
        conf_patch.smriti_license_secret = None
        env_patch.pop("SMRITI_LICENSE_SECRET", None)

    # ── Test 1: site_config.json path ─────────────────────────────────────────

    def test_site_config_secret_returned(self):
        """When smriti_license_secret is in frappe.conf, it must be returned."""
        from smriti_retail_os.license.key_validator import _get_secret

        with patch.object(frappe.conf, "smriti_license_secret", "test-secret-from-conf"), \
             patch.dict(os.environ, {}, clear=False):
            result = _get_secret()
            self.assertEqual(result, b"test-secret-from-conf")

    # ── Test 2: env var path ───────────────────────────────────────────────────

    def test_env_var_secret_returned(self):
        """When SMRITI_LICENSE_SECRET env var is set (and conf has none), env var is used."""
        from smriti_retail_os.license.key_validator import _get_secret

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {"SMRITI_LICENSE_SECRET": "env-secret"}):
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 0
            # Should return env var before reaching fail-closed
            result = _get_secret()
            self.assertEqual(result, b"env-secret")

    # ── Test 3: FAIL-CLOSED in production ────────────────────────────────────

    def test_get_secret_throws_in_production_mode(self):
        """
        When no secret is configured (conf and env both empty) AND
        developer_mode = 0 (production), _get_secret() MUST raise
        frappe.ValidationError (thrown via frappe.throw).

        This is the core Phase 1 security fix. Before the fix, the function
        silently returned the fallback dev key instead of throwing.
        """
        from smriti_retail_os.license.key_validator import _get_secret

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False) as mock_env:
            # Simulate production: no secret anywhere
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 0
            mock_env.pop("SMRITI_LICENSE_SECRET", None)

            with self.assertRaises((frappe.ValidationError, frappe.exceptions.ValidationError),
                                   msg="_get_secret() must throw in production when no secret is set"):
                _get_secret()

    # ── Test 4: developer_mode=1 uses fallback with warning ───────────────────

    def test_get_secret_uses_fallback_in_developer_mode(self):
        """
        When developer_mode=1 and no secret is configured, _get_secret() MUST
        return the _FALLBACK_SECRET bytes and log a warning — NOT throw.
        """
        from smriti_retail_os.license.key_validator import _get_secret, _FALLBACK_SECRET

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False) as mock_env, \
             patch.object(frappe, "log_error", return_value=None) as mock_log:
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 1
            mock_env.pop("SMRITI_LICENSE_SECRET", None)

            result = _get_secret()
            self.assertEqual(result, _FALLBACK_SECRET.encode("utf-8"))
            # Must have logged a warning
            mock_log.assert_called_once()
            call_kwargs = mock_log.call_args
            # Check the WARNING string is in the log title
            title_arg = call_kwargs[1].get("title") or (call_kwargs[0][0] if call_kwargs[0] else "")
            self.assertIn("WARNING", str(title_arg))


class TestParseLicenseKey(unittest.TestCase):
    """Smoke tests for parse_license_key() using generated keys in dev mode."""

    def _get_dev_key(self, customer_id="TEST-001", tier="Professional", expiry="2099-12-31"):
        """Generate a valid test key using the dev fallback secret."""
        from smriti_retail_os.license.key_validator import generate_license_key

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False):
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 1
            with patch.object(frappe, "log_error", return_value=None):
                return generate_license_key(customer_id, tier, expiry)

    def test_valid_key_parses(self):
        """A well-formed key with valid signature must parse without error."""
        from smriti_retail_os.license.key_validator import parse_license_key

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False):
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 1
            with patch.object(frappe, "log_error", return_value=None):
                key = self._get_dev_key()
                payload = parse_license_key(key)

        self.assertEqual(payload["cid"], "TEST-001")
        self.assertEqual(payload["tier"], "Professional")
        self.assertEqual(payload["iss"], "ERPNBOOK")

    def test_tampered_key_rejected(self):
        """A key with a modified payload must raise LicenseKeyError."""
        from smriti_retail_os.license.key_validator import parse_license_key, LicenseKeyError

        tampered = "SMRT-1-AAAABBBBCCCC-0000000000000000"
        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False):
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 1
            with patch.object(frappe, "log_error", return_value=None):
                with self.assertRaises(LicenseKeyError):
                    parse_license_key(tampered)

    def test_expired_key_rejected(self):
        """A key with an expiry date in the past must raise LicenseKeyError."""
        from smriti_retail_os.license.key_validator import parse_license_key, LicenseKeyError

        with patch.object(frappe, "conf", MagicMock(spec=[])) as mock_conf, \
             patch.dict(os.environ, {}, clear=False):
            mock_conf.smriti_license_secret = None
            mock_conf.developer_mode = 1
            with patch.object(frappe, "log_error", return_value=None):
                expired_key = self._get_dev_key(expiry="2020-01-01")
                with self.assertRaises(LicenseKeyError, msg="Expired key must be rejected"):
                    parse_license_key(expired_key)

    def test_unknown_tier_rejected(self):
        """generate_license_key must refuse invalid tier names."""
        from smriti_retail_os.license.key_validator import generate_license_key

        with self.assertRaises(ValueError):
            generate_license_key("CUST-001", "InvalidTier", "2099-12-31")


if __name__ == "__main__":
    unittest.main()
