# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/documents/mixins.py
# @desc:    SmritiDocument Mixins — reusable document behaviours.
#           Mix these into SmritiDocument subclasses to add
#           audit trails, workflow helpers, and permission guards.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#


class AuditMixin:
    """
    Adds audit trail support to SmritiDocument.
    Records: user, timestamp, before_value, after_value, reason.
    (Architecture Constitution Rule 10)

    Usage:
        class PurchaseDocument(SmritiDocument, AuditMixin):
            ...
        doc = PurchaseDocument.load("Purchase", "PO-001")
        doc.record_change("grand_total", before=5000, after=6500, reason="Price revision")
    """

    def record_change(self, field: str, before, after, reason: str = None):
        """Record a field change in the SMRITI audit log."""
        import frappe
        from smriti_retail_os.core.platform import permissions
        frappe.get_doc({
            "doctype": "SMRITI Audit Log",
            "reference_doctype": self.doctype,
            "reference_name": self.name,
            "field_changed": field,
            "before_value": str(before),
            "after_value": str(after),
            "changed_by": permissions.current_user(),
            "reason": reason or "",
        }).insert(ignore_permissions=True)


class WorkflowMixin:
    """
    Adds workflow state helpers to SmritiDocument.

    Usage:
        class PurchaseDocument(SmritiDocument, WorkflowMixin):
            ...
        doc.is_draft()     # → True if workflow_state == "Draft"
        doc.is_approved()  # → True if workflow_state == "Approved"
    """

    def workflow_state(self) -> str:
        """Return the current workflow state."""
        return self.get("workflow_state") or self.get("docstatus")

    def is_draft(self) -> bool:
        """True if the document is in Draft state."""
        return self.get("docstatus") == 0

    def is_submitted(self) -> bool:
        """True if the document is in Submitted (Posted) state."""
        return self.get("docstatus") == 1

    def is_cancelled(self) -> bool:
        """True if the document is Cancelled."""
        return self.get("docstatus") == 2


class PermissionMixin:
    """
    Adds permission guard helpers to SmritiDocument.

    Usage:
        class PurchaseDocument(SmritiDocument, PermissionMixin):
            ...
        doc.require_write_permission()
    """

    def require_read_permission(self):
        """Raise PermissionError if current user cannot read this document."""
        from smriti_retail_os.core.platform import permissions
        permissions.require_read(self.model_name, doc=self.raw)

    def require_write_permission(self):
        """Raise PermissionError if current user cannot write this document."""
        from smriti_retail_os.core.platform import permissions
        permissions.require_write(self.model_name, doc=self.raw)

    def require_submit_permission(self):
        """Raise PermissionError if current user cannot submit this document."""
        from smriti_retail_os.core.platform import permissions
        permissions.require(self.model_name, "submit", doc=self.raw)
