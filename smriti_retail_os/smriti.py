# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/smriti.py
# @desc:    SMRITI Framework API — the single import point for all business code.
#
#           This module is the public surface of the SMRITI Core Framework.
#           Business services, studios, and API handlers import this module.
#           The `smriti_retail_os/core/` internals are implementation details.
#
#           Usage:
#               from smriti_retail_os import smriti
#
#               customer = smriti.documents.get("Customer", "CUST-001")
#               smriti.cache.set("smriti_profiles", data, ttl=600)
#               smriti.events.publish("smriti:stock_update", {"item": "ITEM-001"})
#               smriti.errors.raise_validation("Supplier Required", "Please select a supplier.")
#               smriti.permissions.require("Purchase", "create")
#               smriti.jobs.enqueue("smriti_retail_os.services.sync.run", company="SM")
#
#           Architecture:
#               Business Code  →  smriti.*  →  core/platform/  →  Frappe ORM
#
#           Rule (SPC-012):
#               Business code NEVER imports smriti_retail_os.core.platform directly.
#               Business code NEVER calls frappe.* directly.
#               This module is the ONLY entry point.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from smriti_retail_os.core.platform import documents    # noqa: F401 — smriti.documents
from smriti_retail_os.core.platform import db           # noqa: F401 — smriti.db
from smriti_retail_os.core.platform import cache as _cache_module
from smriti_retail_os.core.platform import events       # noqa: F401 — smriti.events
from smriti_retail_os.core.platform import jobs         # noqa: F401 — smriti.jobs
from smriti_retail_os.core.platform import permissions  # noqa: F401 — smriti.permissions
from smriti_retail_os.core.platform import errors       # noqa: F401 — smriti.errors


class ResilientCache:
    def __init__(self, module):
        self._module = module

    def __getattr__(self, name):
        if hasattr(self._module, name):
            return getattr(self._module, name)
        import frappe
        cache_fn = getattr(frappe, "cache")
        return getattr(cache_fn(), name)

    def __call__(self):
        import frappe
        cache_fn = getattr(frappe, "cache")
        return cache_fn()


cache = ResilientCache(_cache_module)
tasks = jobs

from smriti_retail_os.core.platform.registry import (  # noqa: F401
    resolve,
    resolve_or_passthrough,
)

from smriti_retail_os.core import forms                # noqa: F401 — smriti.forms

__all__ = [
    "documents",
    "db",
    "cache",
    "events",
    "jobs",
    "tasks",
    "permissions",
    "errors",
    "forms",
    "resolve",
    "resolve_or_passthrough",
]

# ── Version ────────────────────────────────────────────────────────────────────
__framework_version__ = "1.0.0"
