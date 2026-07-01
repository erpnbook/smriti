# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/audit_service.py
# @desc:    Writes immutable audit trail entries for all Purchase Studio events.
#           Implements SPC Rule 13: every critical action must be traceable with
#           User | Timestamp | Before Value | After Value | Reason.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 2 (Audit Service)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import json
import frappe
from frappe.utils import now_datetime


# ─────────────────────────────────────────────────────────────────────────────
# EVENT TYPE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

PO_SUBMITTED          = "PO_SUBMITTED"
PO_PENDING_APPROVAL   = "PO_PENDING_APPROVAL"
PO_APPROVED           = "PO_APPROVED"
PO_REJECTED           = "PO_REJECTED"
PO_CANCELLED          = "PO_CANCELLED"
GRN_SUBMITTED         = "GRN_SUBMITTED"
GRN_CANCELLED         = "GRN_CANCELLED"
PI_SUBMITTED          = "PI_SUBMITTED"
PI_CANCELLED          = "PI_CANCELLED"
RETURN_SUBMITTED      = "RETURN_SUBMITTED"
DEBIT_NOTE_CREATED    = "DEBIT_NOTE_CREATED"
SETTINGS_CHANGED      = "SETTINGS_CHANGED"
BATCH_ASSIGNED        = "BATCH_ASSIGNED"


# ─────────────────────────────────────────────────────────────────────────────
# CORE LOG FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def log(event_type, payload, before=None, after=None, reason=None, user=None):
    """
    Writes an immutable audit entry to SMRITI Purchase Audit Log.

    Args:
        event_type (str):   One of the constants above (e.g. PO_SUBMITTED)
        payload (dict):     Event-specific data (document name, supplier, total, etc.)
        before (dict):      State snapshot before the change (for reversible actions)
        after (dict):       State snapshot after the change
        reason (str):       Mandatory for rejection, cancellation, return events
        user (str):         Defaults to frappe.session.user

    This function is called AFTER frappe.db.commit() to ensure the audit entry
    only exists if the primary action succeeded.
    """
    try:
        doc = frappe.new_doc("SMRITI Purchase Audit Log")
        doc.event_type    = event_type
        doc.document_type = payload.get("doctype", "")
        doc.document_name = payload.get("name", "")
        doc.user          = user or frappe.session.user
        doc.timestamp     = now_datetime()
        doc.before_value  = json.dumps(before, default=str) if before else None
        doc.after_value   = json.dumps(after,  default=str) if after  else None
        doc.reason        = reason
        doc.payload       = json.dumps(payload, default=str)
        doc.insert(ignore_permissions=True)
        # Audit log has its own commit to ensure it persists even if
        # the caller's outer scope rolls back for unrelated reasons.
        frappe.db.commit()
    except Exception as e:
        # Audit failure must NEVER block the primary business operation.
        # Log to Error Log but do not re-raise.
        frappe.log_error(
            f"SMRITI Audit Log failure — event: {event_type} — {str(e)}",
            "Purchase Studio Audit Error"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FRAPPE HOOK TARGETS — on_cancel events
# (registered in hooks.py doc_events)
# ─────────────────────────────────────────────────────────────────────────────

def log_po_cancel(doc, method):
    """
    Called by Frappe on_cancel hook for Purchase Order.
    Writes a PO_CANCELLED audit entry.
    """
    log(
        event_type=PO_CANCELLED,
        payload={
            "doctype":       "Purchase Order",
            "name":          doc.name,
            "supplier":      doc.supplier,
            "grand_total":   float(doc.grand_total or 0),
            "cancelled_by":  frappe.session.user
        }
    )


def log_grn_cancel(doc, method):
    """
    Called by Frappe on_cancel hook for Purchase Receipt.
    Writes a GRN_CANCELLED audit entry.
    """
    log(
        event_type=GRN_CANCELLED,
        payload={
            "doctype":     "Purchase Receipt",
            "name":        doc.name,
            "supplier":    doc.supplier,
            "grand_total": float(doc.grand_total or 0),
            "po_name":     doc.items[0].purchase_order if doc.items else None,
            "cancelled_by": frappe.session.user
        }
    )


def log_pi_cancel(doc, method):
    """
    Called by Frappe on_cancel hook for Purchase Invoice.
    Writes a PI_CANCELLED audit entry.
    """
    log(
        event_type=PI_CANCELLED,
        payload={
            "doctype":               "Purchase Invoice",
            "name":                  doc.name,
            "supplier":              doc.supplier,
            "grand_total":           float(doc.grand_total or 0),
            "outstanding_amount":    float(doc.outstanding_amount or 0),
            "smriti_creation_mode":  doc.smriti_creation_mode or "",
            "cancelled_by":          frappe.session.user
        }
    )
