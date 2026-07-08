# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/__init__.py
# @desc:    SMRITI Core Framework — root namespace.
#           All SMRITI modules must access platform services through
#           this package and its sub-modules. No module outside
#           core/platform/ may call frappe.* directly.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Architecture Reference:
#   SMRITI_PLATFORM_VISION.md    — Golden Rule and Five Categories
#   ARCHITECTURE.md              — Rule 2 (Service-First Design)
#   docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md
#
# Canonical import patterns:
#
#   from smriti_retail_os.core.platform import documents, db, cache, events, jobs
#   from smriti_retail_os.core.platform.registry import resolve
#   from smriti_retail_os.core.documents.base_document import SmritiDocument
#   from smriti_retail_os.core.services.base_service import BaseService
#
