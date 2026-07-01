# -*- coding: utf-8 -*-
# SMRITI Purchase Settings — DocType Controller
from frappe.model.document import Document


class SMRITIPurchaseSettings(Document):
    """Single DocType storing Purchase Studio operational policy settings."""

    def validate(self):
        if self.purchase_invoice_policy not in ("grn_only", "standalone", "both"):
            import frappe
            frappe.throw("Invalid purchase_invoice_policy value")
        if self.approval_threshold and float(self.approval_threshold) < 0:
            import frappe
            frappe.throw("Approval threshold must be >= 0")
