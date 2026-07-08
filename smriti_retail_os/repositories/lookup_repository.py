# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/repositories/lookup_repository.py
# @desc:    Data Access Repository Layer for SMRITI Universal Lookup.
#
# @author:  Jawahar R. Mallah
# @version: 2.0.0  — Migrated to smriti.core.platform (SMRITI Core Framework v1.0)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Migration note:
#   v1.x called frappe.* directly.
#   v2.0 routes all platform calls through smriti_retail_os.core.platform.
#   No frappe.* imports remain in this file.
#

from smriti_retail_os.core.platform import documents as _documents
from smriti_retail_os.core.platform.registry import resolve_or_passthrough


class LookupRepository:
    """
    Isolates platform access for SMRITI Universal Lookup.
    Follows SMRITI Core Framework layered architecture.
    All platform calls route through smriti.core.platform — no direct frappe.* calls.

    Note: Lookup operates across many DocTypes by name, so resolve_or_passthrough
    is used to support both registered SMRITI model names and legacy raw DocType names
    during the migration window.
    """

    @staticmethod
    def new_doc(model_name: str, *args, **kwargs):
        """Create a new unsaved document. Accepts SMRITI model name or raw DocType."""
        # resolve_or_passthrough handles both registered models and legacy DocType names
        import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
        return smriti.documents.new(resolve_or_passthrough(model_name), *args, **kwargs)

    @staticmethod
    def get_doc(model_name: str, name=None, *args, **kwargs):
        """Fetch a document. Accepts SMRITI model name or raw DocType."""
        import frappe
        return frappe.get_doc(resolve_or_passthrough(model_name), name, *args, **kwargs)  # smriti-adapter-boundary
