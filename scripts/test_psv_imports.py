# -*- coding: utf-8 -*-
#
# @file: scripts/test_psv_imports.py
# @description: Standalone test utility for PSV split service file import verification.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
#!/usr/bin/env python3
"""
Import verification test for all PSV service modules.
Mocks frappe so this can run without a live bench environment.
"""
import sys
import os
import types

# ── Inject app root into path ────────────────────────────────────────────────
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_ROOT)

# ── Build minimal frappe mock ─────────────────────────────────────────────────
frappe_mod = types.ModuleType("frappe")
frappe_mod.whitelist = lambda *a, **kw: (lambda f: f)
frappe_mod.ValidationError = Exception
frappe_mod.throw = lambda *a, **kw: None
frappe_mod.log_error = lambda *a, **kw: None
frappe_mod.get_all = lambda *a, **kw: []
frappe_mod.get_doc = lambda *a, **kw: types.SimpleNamespace(
    as_dict=lambda: {}, flags=types.SimpleNamespace(ignore_permissions=False),
    items=[], append=lambda *a, **kw: None,
    insert=lambda **kw: None, submit=lambda: None, cancel=lambda: None,
    db_set=lambda *a, **kw: None, save=lambda **kw: None
)
frappe_mod.get_single = lambda *a, **kw: types.SimpleNamespace(
    redistribution_scope="Same Territory",
    weeks_of_cover_critical=2,
    weeks_of_cover_healthy=8,
    weeks_of_cover_warning=4,
    star_velocity_threshold=1.0,
    last_processed_partner="",
    last_checkpoint="",
    save=lambda **kw: None
)
frappe_mod.get_cached_doc = lambda *a, **kw: types.SimpleNamespace(as_dict=lambda: {})
frappe_mod.new_doc = lambda *a, **kw: types.SimpleNamespace(
    flags=types.SimpleNamespace(ignore_permissions=False, ignore_links=False),
    items=[], append=lambda *a, **kw: None,
    insert=lambda **kw: None, submit=lambda: None, cancel=lambda: None,
    db_set=lambda *a, **kw: None, set=lambda *a, **kw: None, save=lambda **kw: None
)
frappe_mod.only_for = lambda *a, **kw: None
frappe_mod.msgprint = lambda *a, **kw: None
frappe_mod._ = lambda x: x

# frappe.conf
frappe_mod.conf = types.SimpleNamespace()
frappe_mod.conf.get = lambda key, default=None: default

# frappe.session
frappe_mod.session = types.SimpleNamespace(user="Administrator")

# frappe.local (needs to support attribute assignment)
class _Local:
    pass
frappe_mod.local = _Local()

# frappe.cache() factory
class _FakeCache:
    def get(self, key, *a, **kw):
        return None
    def set(self, key, val, *a, **kw):
        return True
    def delete(self, key):
        pass
frappe_mod.cache = lambda: _FakeCache()

# frappe.logger()
class _FakeLogger:
    def warning(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def error(self, *a, **kw): pass
frappe_mod.logger = lambda *a, **kw: _FakeLogger()

# frappe.db
class _FakeDB:
    def get_value(self, *a, **kw): return None
    def sql(self, *a, **kw): return []
    def get_single_value(self, *a, **kw): return None
    def exists(self, *a, **kw): return None
    def count(self, *a, **kw): return 0
    def set_value(self, *a, **kw): pass
    def begin(self): pass
    def commit(self): pass
    def rollback(self): pass
    def delete(self, *a, **kw): pass
    def get_all(self, *a, **kw): return []
frappe_mod.db = _FakeDB()

# frappe.utils
utils_mod = types.ModuleType("frappe.utils")
utils_mod.today = lambda: "2026-06-20"
utils_mod.now_datetime = lambda: "2026-06-20 00:00:00"
utils_mod.get_datetime = lambda x: x
utils_mod.getdate = lambda x: x
utils_mod.add_days = lambda d, n: d
utils_mod.now = lambda: "2026-06-20 00:00:00"

# frappe.utils.file_manager
fm_mod = types.ModuleType("frappe.utils.file_manager")
fm_mod.get_file_path = lambda *a: "/tmp/test.csv"

# Register all mock modules
sys.modules["frappe"] = frappe_mod
sys.modules["frappe.utils"] = utils_mod
sys.modules["frappe.utils.file_manager"] = fm_mod

# ── Mock smriti_retail_os sub-dependencies ────────────────────────────────────
# balance_engine and ledger_engine may import frappe at module level
# — let them import; frappe mock is already set.

# ── Run imports ───────────────────────────────────────────────────────────────
errors = []

modules_to_test = [
    "smriti_retail_os.psv_snapshot_service",
    "smriti_retail_os.psv_health_service",
    "smriti_retail_os.psv_analytics_service",
    "smriti_retail_os.psv_migration_service",
    "smriti_retail_os.psv_service",           # must import last (re-exports from above)
]

for mod_name in modules_to_test:
    try:
        __import__(mod_name)
        print(f"  OK  {mod_name}")
    except Exception as exc:
        print(f"  ERR {mod_name}: {exc}")
        errors.append((mod_name, exc))

print()
if errors:
    print(f"RESULT: {len(errors)} IMPORT ERROR(S)")
    for name, exc in errors:
        import traceback
        print(f"\n  --- {name} ---")
        print(f"  {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ALL IMPORTS OK")
    sys.exit(0)
