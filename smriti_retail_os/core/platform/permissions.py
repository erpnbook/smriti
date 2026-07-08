# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/permissions.py
# @desc:    SMRITI Platform Permissions Adapter.
#           Wraps frappe.has_permission and related permission checks.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   from smriti_retail_os.core.platform import permissions
#
#   if permissions.can_read("Customer"):
#       ...
#
#   permissions.require_write("Purchase")   # raises if not allowed
#

from smriti_retail_os.core.platform.registry import resolve


def has_permission(model_name: str, ptype: str = "read", doc=None) -> bool:
    """
    Check whether the current user has the specified permission on a model.

    Args:
        model_name (str): SMRITI model name
        ptype (str): Permission type — "read", "write", "create", "delete",
                     "submit", "cancel", "amend", "print", "email"
        doc: Optional document object for document-level permission check

    Returns:
        bool: True if permitted

    Example:
        if permissions.has_permission("Purchase", "create"):
            po = documents.new("Purchase")
    """
    import frappe
    return frappe.has_permission(resolve(model_name), ptype=ptype, doc=doc)


def can_read(model_name: str, doc=None) -> bool:
    """Shortcut: check read permission."""
    return has_permission(model_name, ptype="read", doc=doc)


def can_write(model_name: str, doc=None) -> bool:
    """Shortcut: check write permission."""
    return has_permission(model_name, ptype="write", doc=doc)


def can_create(model_name: str) -> bool:
    """Shortcut: check create permission."""
    return has_permission(model_name, ptype="create")


def can_delete(model_name: str, doc=None) -> bool:
    """Shortcut: check delete permission."""
    return has_permission(model_name, ptype="delete", doc=doc)


def can_submit(model_name: str, doc=None) -> bool:
    """Shortcut: check submit permission."""
    return has_permission(model_name, ptype="submit", doc=doc)


def require(model_name: str, ptype: str = "read", doc=None):
    """
    Assert that the current user has the specified permission.
    Raises frappe.PermissionError if not permitted.

    Args:
        model_name (str): SMRITI model name
        ptype (str): Permission type
        doc: Optional document for document-level check

    Example:
        permissions.require("Purchase", "create")
        # Raises PermissionError if user cannot create a Purchase
    """
    import frappe
    if not has_permission(model_name, ptype=ptype, doc=doc):
        frappe.throw(
            f"You do not have permission to {ptype} {model_name} records.",
            frappe.PermissionError
        )


def require_read(model_name: str, doc=None):
    """Assert read permission or raise."""
    require(model_name, "read", doc)


def require_write(model_name: str, doc=None):
    """Assert write permission or raise."""
    require(model_name, "write", doc)


def require_create(model_name: str):
    """Assert create permission or raise."""
    require(model_name, "create")


def current_user() -> str:
    """Return the currently logged-in user email."""
    import frappe
    return frappe.session.user


def is_system_manager() -> bool:
    """Check whether the current user has the System Manager role."""
    import frappe
    return "System Manager" in frappe.get_roles()


def get_roles() -> list:
    """Return the list of roles assigned to the current user."""
    import frappe
    return frappe.get_roles()
