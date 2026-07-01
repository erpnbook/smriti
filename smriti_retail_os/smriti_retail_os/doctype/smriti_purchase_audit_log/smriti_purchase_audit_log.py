# -*- coding: utf-8 -*-
# SMRITI Purchase Audit Log — DocType Controller
from frappe.model.document import Document


class SMRITIPurchaseAuditLog(Document):
    """Immutable audit trail record for all Purchase Studio business events.

    Records are write-once: no updates or deletes permitted after creation.
    """

    def before_save(self):
        """Enforce immutability — audit log entries must never be modified."""
        if not self.is_new():
            import frappe
            frappe.throw("Audit log entries are immutable and cannot be modified.")
