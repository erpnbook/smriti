# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/errors.py
# @desc:    SMRITI Platform Error Adapter.
#           Provides HREP-compliant (Human-Readable Error Policy) error raising.
#           Wraps frappe.throw with SMRITI error codes and structured messaging.
#
#           RULE: Never call frappe.throw() outside this module.
#                 All error-raising must route through this module.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# SMRITI Error Dictionary (HREP Rule 5):
#   SMRITI-VAL-*     Validation errors (field missing, invalid value)
#   SMRITI-PERM-*    Permission errors
#   SMRITI-BIZ-*     Business rule violations
#   SMRITI-SYS-*     System / infrastructure errors
#   SMRITI-NET-*     Network / connectivity errors
#   SMRITI-DATA-*    Data integrity errors
#


# smriti-platform-core: this module IS the frappe abstraction layer — Guard 6 exempt by design
import datetime


def _make_ref_id(prefix: str = "ERR") -> str:
    """Generates a SMRITI error reference ID (e.g. SMRITI-ERR-20260708-A1B2)."""
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"SMRITI-{prefix}-{ts}"


def raise_validation(title: str, message: str, error_code: str = None):
    """
    Raise a validation error (HREP-compliant).
    Use for field-level and business rule validation failures.

    Args:
        title (str): Short, clear description of what failed
        message (str): Business-language explanation with guidance
        error_code (str): SMRITI error code, e.g. "SMRITI-VAL-001"

    Example:
        errors.raise_validation(
            "Supplier Not Selected",
            "Please select a supplier before saving the purchase order. "
            "Go to the Supplier field and choose from the list."
        )
    """
    import frappe
    ref = error_code or _make_ref_id("VAL")
    frappe.throw(
        f"<b>{title}</b><br>{message}<br><small>Ref: {ref}</small>",
        frappe.ValidationError,
        title=title
    )


def raise_permission(action: str, model_name: str = None, error_code: str = None):
    """
    Raise a permission error (HREP-compliant).

    Args:
        action (str): The action that was attempted, e.g. "create a purchase order"
        model_name (str): Optional SMRITI model name for context
        error_code (str): SMRITI error code, e.g. "SMRITI-PERM-001"

    Example:
        errors.raise_permission("approve purchase orders")
    """
    import frappe
    ref = error_code or _make_ref_id("PERM")
    subject = f" {model_name} records" if model_name else ""
    frappe.throw(
        f"You do not have permission to {action}{subject}. "
        f"Contact your store administrator if you believe this is incorrect.<br>"
        f"<small>Ref: {ref}</small>",
        frappe.PermissionError,
        title="Access Denied"
    )


def raise_business_error(title: str, message: str, error_code: str = None):
    """
    Raise a business rule violation error (HREP-compliant).
    Use for errors that represent a business constraint being broken.

    Args:
        title (str): Short, business-language title
        message (str): Full explanation + what the user should do
        error_code (str): SMRITI error code, e.g. "SMRITI-BIZ-001"

    Example:
        errors.raise_business_error(
            "Stock Not Available",
            "The requested quantity (50) exceeds available stock (23) "
            "in Stores warehouse. Adjust the quantity or raise a purchase order first.",
            error_code="SMRITI-BIZ-002"
        )
    """
    import frappe
    ref = error_code or _make_ref_id("BIZ")
    frappe.throw(
        f"<b>{title}</b><br>{message}<br><small>Ref: {ref}</small>",
        frappe.ValidationError,
        title=title
    )


def raise_system_error(title: str, message: str, error_code: str = None):
    """
    Raise a system-level error (HREP-compliant).
    Use when an infrastructure or unexpected technical failure occurs.
    The message must be business-friendly — no stack traces, no class names.

    Args:
        title (str): Short description
        message (str): What happened and what the user should do (e.g. "Try again in a few minutes")
        error_code (str): SMRITI error code, e.g. "SMRITI-SYS-001"
    """
    import frappe
    ref = error_code or _make_ref_id("SYS")
    frappe.throw(
        f"<b>{title}</b><br>{message}<br>"
        f"If the issue persists, contact your system administrator with reference: {ref}",
        title=title
    )


def raise_not_found(model_name: str, identifier: str):
    """
    Raise a not-found error when a requested record does not exist.

    Args:
        model_name (str): SMRITI model name (user-facing vocabulary)
        identifier (str): The name/ID that was not found

    Example:
        errors.raise_not_found("Customer", "CUST-999")
    """
    import frappe
    ref = _make_ref_id("DATA")
    frappe.throw(
        f"<b>{model_name} Not Found</b><br>"
        f"The {model_name} record '{identifier}' could not be found. "
        f"It may have been deleted or the reference is incorrect.<br>"
        f"<small>Ref: {ref}</small>",
        frappe.DoesNotExistError,
        title=f"{model_name} Not Found"
    )


def log_error(title: str, exc: Exception = None, context: dict = None, message: str = None):
    """
    Log an error to Frappe's error log without raising (for non-fatal errors).

    Args:
        title (str): Error title
        exc (Exception): Optional exception to log
        context (dict): Optional additional context
        message (str): Optional custom error message

    Example:
        try:
            sync_stock()
        except Exception as e:
            errors.log_error("PSV Stock Sync Failed", exc=e,
                             context={"company": company})
    """
    import frappe
    import traceback
    err_msg = message or ""
    if exc:
        if err_msg:
            err_msg += f"\n\nException: {exc}"
        else:
            err_msg = str(exc)
    if not err_msg:
        err_msg = title
    if context:
        err_msg += f"\n\nContext: {context}"
    if exc:
        err_msg += f"\n\nTraceback:\n{traceback.format_exc()}"
    frappe.log_error(title=title, message=err_msg)
