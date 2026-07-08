# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/__init__.py
# @desc:    SMRITI Platform Adapter — public API surface.
#           Imports all platform sub-modules so callers can do:
#
#               from smriti_retail_os.core.platform import documents
#               from smriti_retail_os.core.platform import db, cache, events, jobs
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# RULE: This is the ONLY package allowed to import frappe.* directly.
#       All other SMRITI modules must route through smriti.core.platform.
#
from smriti_retail_os.core.platform import (  # noqa: F401
    documents,
    db,
    cache,
    events,
    jobs,
    permissions,
    errors,
)
from smriti_retail_os.core.platform.registry import resolve  # noqa: F401
