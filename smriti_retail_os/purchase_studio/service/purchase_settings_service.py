# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/purchase_settings_service.py
# @desc:    Reads and writes SMRITI Purchase Settings.
#           All policy decisions route through this service — no other file
#           reads SMRITI Purchase Settings directly.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 3 (Settings Service)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt

SETTINGS_DOCTYPE = "SMRITI Purchase Settings"
VALID_POLICIES   = {"grn_only", "standalone", "both"}
VALID_LC_RULES   = {"manual", "proportional", "disabled"}


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def get_settings():
    """
    Returns all SMRITI Purchase Settings as a plain dict.
    If the DocType record does not exist yet, returns safe defaults.
    """
    try:
        s = frappe.get_single(SETTINGS_DOCTYPE)
        return {
            "purchase_invoice_policy": s.purchase_invoice_policy or "both",
            "approval_threshold":      flt(s.approval_threshold),
            "grn_mandatory":           bool(s.grn_mandatory),
            "allow_over_receipt":      bool(s.allow_over_receipt),
            "auto_create_items":       bool(s.auto_create_items),
            "default_warehouse":       s.default_warehouse or "",
            "tolerance_percent":       flt(s.tolerance_percent),
            "landed_cost_rule":        s.landed_cost_rule or "manual"
        }
    except Exception:
        # Settings not yet created — return safe defaults
        return {
            "purchase_invoice_policy": "both",
            "approval_threshold":      0.0,
            "grn_mandatory":           False,
            "allow_over_receipt":      False,
            "auto_create_items":       True,
            "default_warehouse":       "",
            "tolerance_percent":       0.0,
            "landed_cost_rule":        "manual"
        }


def check_invoice_policy():
    """
    Returns the current Purchase Invoice Policy: "grn_only" | "standalone" | "both"
    """
    return get_settings().get("purchase_invoice_policy", "both")


def check_approval_required(grand_total):
    """
    Returns True if grand_total exceeds the approval threshold.
    threshold = 0 means approval is disabled (always False).
    """
    s = get_settings()
    threshold = flt(s.get("approval_threshold", 0))
    if threshold <= 0:
        return False
    return flt(grand_total) > threshold


def is_grn_mandatory():
    """
    Returns True if GRN is mandatory for all Purchase Invoices regardless of policy.
    """
    return bool(get_settings().get("grn_mandatory", False))


def is_over_receipt_allowed():
    """Returns True if receiving more than PO qty is permitted."""
    return bool(get_settings().get("allow_over_receipt", False))


def is_auto_create_items():
    """Returns True if items should be auto-created when not found in PO."""
    return bool(get_settings().get("auto_create_items", True))


def get_default_warehouse_setting():
    """Returns the configured default warehouse (may be empty string)."""
    return get_settings().get("default_warehouse", "")


# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────

def save_settings(fields):
    """
    Validates and saves SMRITI Purchase Settings.
    Writes a SETTINGS_CHANGED audit entry with before/after snapshots.

    Args:
        fields (dict): Any subset of settings fields to update.

    Raises:
        frappe.ValidationError for invalid field values.
    """
    _validate_settings(fields)

    # Capture before snapshot
    before = get_settings()

    # Apply changes
    s = frappe.get_single(SETTINGS_DOCTYPE)

    if "purchase_invoice_policy" in fields:
        s.purchase_invoice_policy = fields["purchase_invoice_policy"]
    if "approval_threshold" in fields:
        s.approval_threshold = flt(fields["approval_threshold"])
    if "grn_mandatory" in fields:
        s.grn_mandatory = int(bool(fields["grn_mandatory"]))
    if "allow_over_receipt" in fields:
        s.allow_over_receipt = int(bool(fields["allow_over_receipt"]))
    if "auto_create_items" in fields:
        s.auto_create_items = int(bool(fields["auto_create_items"]))
    if "default_warehouse" in fields:
        s.default_warehouse = fields["default_warehouse"] or ""
    if "tolerance_percent" in fields:
        s.tolerance_percent = flt(fields["tolerance_percent"])
    if "landed_cost_rule" in fields:
        s.landed_cost_rule = fields["landed_cost_rule"]

    s.save(ignore_permissions=True)
    frappe.db.commit()

    # Capture after snapshot
    after = get_settings()

    # Write audit trail
    from smriti_retail_os.purchase_studio.service.audit_service import log, SETTINGS_CHANGED
    log(
        event_type=SETTINGS_CHANGED,
        payload={"doctype": SETTINGS_DOCTYPE, "name": SETTINGS_DOCTYPE},
        before=before,
        after=after
    )


def _validate_settings(fields):
    """Internal validation for save_settings input."""
    if "purchase_invoice_policy" in fields:
        if fields["purchase_invoice_policy"] not in VALID_POLICIES:
            frappe.throw(_(
                "Invalid Purchase Invoice Policy '{0}'. "
                "Must be one of: grn_only, standalone, both."
            ).format(fields["purchase_invoice_policy"]))

    if "approval_threshold" in fields:
        if flt(fields["approval_threshold"]) < 0:
            frappe.throw(_("Approval Threshold cannot be negative."))

    if "tolerance_percent" in fields:
        tp = flt(fields["tolerance_percent"])
        if tp < 0 or tp > 100:
            frappe.throw(_("Tolerance % must be between 0 and 100."))

    if "landed_cost_rule" in fields:
        if fields["landed_cost_rule"] not in VALID_LC_RULES:
            frappe.throw(_(
                "Invalid Landed Cost Rule '{0}'. "
                "Must be one of: manual, proportional, disabled."
            ).format(fields["landed_cost_rule"]))

    if "default_warehouse" in fields and fields["default_warehouse"]:
        if not frappe.db.exists("Warehouse", fields["default_warehouse"]):
            frappe.throw(_(
                "Warehouse '{0}' does not exist."
            ).format(fields["default_warehouse"]))
