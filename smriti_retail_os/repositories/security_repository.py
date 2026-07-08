# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/repositories/security_repository.py
# @desc:    Data Access Repository Layer for SMRITI Security and User Management.
#           Encapsulates all database reads and writes to User and Role-related data.
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
from smriti_retail_os.core.platform import db as _db


class SecurityRepository:
    """
    Isolates platform access for SMRITI User, Role, and Workflow operations.
    Follows SMRITI Core Framework layered architecture.
    All platform calls route through smriti.core.platform — no direct frappe.* calls.
    """

    @staticmethod
    def get_doc(model_name: str, name: str, **kwargs):
        """Fetch a security-related document by model name and document name."""
        return _documents.get(model_name, name, **kwargs)

    @staticmethod
    def new_doc(model_name: str):
        """Create a new unsaved security-related document."""
        return _documents.new(model_name)

    @staticmethod
    def set_value(model_name: str, name: str, field, value=None):
        """Update a field on a security-related document directly in the DB."""
        return _db.set(model_name, name, field, value)

    @staticmethod
    def delete(model_name: str, filters: dict):
        """Delete security-related records matching the given filters."""
        return _db.delete(model_name, filters)

    @staticmethod
    def delete_doc(model_name: str, name: str, force: bool = False):
        """Delete a security-related document by name."""
        return _documents.delete(model_name, name, force=force)

    @staticmethod
    def commit():
        """Commit the current database transaction."""
        return _db.commit()
