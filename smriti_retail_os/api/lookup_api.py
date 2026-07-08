# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/api/lookup_api.py
# @desc:    Whitelisted Universal Lookup REST APIs. Exposes search, recent,
#           create, and validate endpoints to the SMRITI UI components.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 5 (REST / API)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
import json
from smriti_retail_os.services.lookup_service import LookupService


@frappe.whitelist()
def search(entity, text=None, filters=None, limit=20):
    """Universal debounced fuzzy search endpoint."""
    if filters and isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except Exception:
            pass
    return LookupService.search(entity, text, filters, limit)


@frappe.whitelist()
def recent(entity):
    """Retrieve recently selected/modified records for the entity."""
    return LookupService.recent(entity)


@frappe.whitelist()
def create(entity, data):
    """Quick Create on-the-fly record creation."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            pass
    return LookupService.create(entity, data)


@frappe.whitelist()
def validate(entity, value):
    """Validates presence of a record for a specific entity."""
    return LookupService.validate(entity, value)
