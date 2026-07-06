# -*- coding: utf-8 -*-
#
# @file: scripts/test_license_standalone.py
# @description: Standalone test runner for SMRITI License Key Validator fail-closed behaviour.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone test runner for key_validator._get_secret() fail-closed behaviour.
Does NOT require Frappe installation — mocks the frappe module entirely.

Run with:
    python3 scripts/test_license_standalone.py

Output is machine-parseable (PASS/FAIL per test).
"""

import sys
import os
import types
import unittest
from unittest.mock import MagicMock

# ── Build comprehensive frappe mock (no bench installation required) ──────────
# Must be done BEFORE any smriti_retail_os imports.

class _FrappeConf:
    smriti_license_secret = None
    developer_mode = 0

class _ValidationError(Exception): pass

def _frappe_throw(msg, exc=None, title=None):
    raise _ValidationError(msg)

# Root frappe module
_frappe_mod = types.ModuleType("frappe")
_frappe_mod.conf = _FrappeConf()
_frappe_mod.ValidationError = _ValidationError
_frappe_mod.throw = _frappe_throw
_frappe_mod.log_error = lambda *a, **kw: None
_frappe_mod._ = lambda x: x  # translation no-op
_frappe_mod.logger = lambda *a, **kw: MagicMock()
_frappe_mod.get_all = lambda *a, **kw: []
_frappe_mod.db = MagicMock()
_frappe_mod.session = MagicMock()

# frappe.exceptions
_exc_mod = types.ModuleType("frappe.exceptions")
_exc_mod.ValidationError = _ValidationError
sys.modules["frappe.exceptions"] = _exc_mod
_frappe_mod.exceptions = _exc_mod

# frappe.utils — used by license/manager.py
_utils_mod = types.ModuleType("frappe.utils")
from datetime import date as _date, datetime as _datetime
_utils_mod.getdate = lambda d=None: _date.today()
_utils_mod.date_diff = lambda a, b: 0
_utils_mod.now_datetime = lambda: _datetime.now()
_utils_mod.get_datetime = lambda d=None: _datetime.now()
_utils_mod.nowdate = lambda: str(_date.today())
_utils_mod.cint = lambda x: int(x) if x else 0
sys.modules["frappe.utils"] = _utils_mod
_frappe_mod.utils = _utils_mod

# frappe.model.document
_model_doc_mod = types.ModuleType("frappe.model.document")
_model_doc_mod.Document = object
sys.modules["frappe.model"] = types.ModuleType("frappe.model")
sys.modules["frappe.model.document"] = _model_doc_mod

# Register root module last (after sub-modules)
sys.modules["frappe"] = _frappe_mod

# ── Adjust sys.path and import ONLY key_validator directly ────────────────────

_APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _APP_ROOT)

# Import the target module directly — bypass the license __init__ which pulls manager
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "smriti_retail_os.license.key_validator",
    os.path.join(_APP_ROOT, "smriti_retail_os", "license", "key_validator.py")
)
_kv_mod = _ilu.module_from_spec(_spec)
sys.modules["smriti_retail_os.license.key_validator"] = _kv_mod
_spec.loader.exec_module(_kv_mod)

_get_secret = _kv_mod._get_secret
_FALLBACK_SECRET = _kv_mod._FALLBACK_SECRET
generate_license_key = _kv_mod.generate_license_key
parse_license_key = _kv_mod.parse_license_key
LicenseKeyError = _kv_mod.LicenseKeyError


# ── Tests ────────────────────────────────────────────────────────────────────

class TestGetSecretFailClosed(unittest.TestCase):

    def setUp(self):
        """Reset frappe mock to clean state before each test."""
        _frappe_mod.conf.smriti_license_secret = None
        _frappe_mod.conf.developer_mode = 0
        os.environ.pop("SMRITI_LICENSE_SECRET", None)

    def test_site_config_secret_used(self):
        """BEFORE: site_config.json has secret → must return it."""
        _frappe_mod.conf.smriti_license_secret = "my-production-secret"
        result = _get_secret()
        self.assertEqual(result, b"my-production-secret", "site_config secret not returned")
        print("[PASS] test_site_config_secret_used")

    def test_env_var_secret_used(self):
        """BEFORE: env var has secret → must return it."""
        os.environ["SMRITI_LICENSE_SECRET"] = "env-secret-value"
        result = _get_secret()
        self.assertEqual(result, b"env-secret-value", "env var secret not returned")
        print("[PASS] test_env_var_secret_used")

    def test_FAIL_CLOSED_production_throws(self):
        """
        CRITICAL: In production (developer_mode=0), with no secret configured,
        _get_secret() MUST raise ValidationError.

        This is the core Phase 1 security fix. Before: returned _FALLBACK_SECRET.
        After: raises frappe.ValidationError so no production instance silently
        validates keys against the well-known dev secret.
        """
        _frappe_mod.conf.developer_mode = 0
        _frappe_mod.conf.smriti_license_secret = None
        os.environ.pop("SMRITI_LICENSE_SECRET", None)

        with self.assertRaises(
            _ValidationError,
            msg="CRITICAL: _get_secret() must throw in production when no secret is configured"
        ):
            _get_secret()
        print("[PASS] test_FAIL_CLOSED_production_throws")

    def test_developer_mode_fallback_returns_dev_secret(self):
        """
        In developer_mode=1, with no secret configured,
        _get_secret() MUST return _FALLBACK_SECRET bytes.
        """
        _frappe_mod.conf.developer_mode = 1
        _frappe_mod.conf.smriti_license_secret = None
        os.environ.pop("SMRITI_LICENSE_SECRET", None)

        logged = []
        _frappe_mod.log_error = lambda *a, **kw: logged.append(kw.get("title", a[0] if a else ""))

        result = _get_secret()
        self.assertEqual(result, _FALLBACK_SECRET.encode("utf-8"))
        self.assertTrue(len(logged) > 0, "Warning log must be emitted in developer fallback")
        self.assertIn("WARNING", str(logged[0]), "Log title must contain 'WARNING'")
        print(f"[PASS] test_developer_mode_fallback_returns_dev_secret (log: {logged[0]!r})")


class TestParseLicenseKey(unittest.TestCase):

    def setUp(self):
        """Use developer_mode for key generation tests."""
        _frappe_mod.conf.smriti_license_secret = None
        _frappe_mod.conf.developer_mode = 1
        _frappe_mod.log_error = lambda *a, **kw: None
        os.environ.pop("SMRITI_LICENSE_SECRET", None)

    def test_valid_key_round_trip(self):
        """generate + parse must produce matching payload."""
        key = generate_license_key("CUST-001", "Professional", "2099-12-31")
        payload = parse_license_key(key)
        self.assertEqual(payload["cid"], "CUST-001")
        self.assertEqual(payload["tier"], "Professional")
        self.assertEqual(payload["iss"], "ERPNBOOK")
        print("[PASS] test_valid_key_round_trip")

    def test_tampered_key_rejected(self):
        """Tampered key must raise LicenseKeyError."""
        tampered = "SMRT-1-AAAABBBBCCCC-0000000000000000"
        with self.assertRaises(LicenseKeyError):
            parse_license_key(tampered)
        print("[PASS] test_tampered_key_rejected")

    def test_expired_key_rejected(self):
        """Key with past expiry must raise LicenseKeyError."""
        key = generate_license_key("CUST-002", "Starter", "2020-01-01")
        with self.assertRaises(LicenseKeyError):
            parse_license_key(key)
        print("[PASS] test_expired_key_rejected")

    def test_unknown_tier_rejected(self):
        """generate_license_key must refuse invalid tier."""
        with self.assertRaises(ValueError):
            generate_license_key("CUST-003", "SuperPremium", "2099-12-31")
        print("[PASS] test_unknown_tier_rejected")


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestGetSecretFailClosed))
    suite.addTests(loader.loadTestsFromTestCase(TestParseLicenseKey))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Tests run:    {result.testsRun}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    if result.wasSuccessful():
        print("OVERALL:      ALL PASS ✅")
        sys.exit(0)
    else:
        print("OVERALL:      FAILED ❌")
        for f in result.failures + result.errors:
            print(f"\n--- {f[0]} ---\n{f[1]}")
        sys.exit(1)
