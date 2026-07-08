# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/__init__.py
# @desc:    SMRITI Core Framework — root namespace.
#           All SMRITI modules must access platform services through
#           this package and its sub-modules. No module outside
#           core/platform/ may call frappe.* directly.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.1.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Architecture Reference:
#   SMRITI_PLATFORM_VISION.md    — Golden Rule and Five Categories
#   ARCHITECTURE.md §15          — SMRITI Core Framework + canonical patterns
#   SPC-012                      — Platform Adapter Boundary (constitutional law)
#   docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md
#
# ── CANONICAL IMPORT PATTERNS ─────────────────────────────────────────────────
#
# PREFERRED — for all business code (services, studios, APIs):
#
#   from smriti_retail_os import smriti
#
#   smriti.documents.get("Customer", name)
#   smriti.db.get("Customer", name, "credit_limit")
#   smriti.cache.get_or_set("key", builder, ttl=300)
#   smriti.events.publish("smriti:event", data)
#   smriti.jobs.enqueue("module.function", **kwargs)
#   smriti.permissions.require("Customer", "create")
#   smriti.errors.raise_validation("Title", "Message")
#   smriti.forms.SmritiForm / smriti.forms.SmritiField
#
# INTERNAL ONLY — for core/platform/ adapter code only:
#
#   from smriti_retail_os.core.platform import documents, db, cache, events, jobs
#   from smriti_retail_os.core.platform.registry import resolve
#
# FRAMEWORK CLASSES — for subclassing:
#
#   from smriti_retail_os.core.documents.base_document import SmritiDocument
#   from smriti_retail_os.core.services.base_service import BaseService
#   from smriti_retail_os.core.forms import SmritiForm, SmritiField, FormLifecycle
#
