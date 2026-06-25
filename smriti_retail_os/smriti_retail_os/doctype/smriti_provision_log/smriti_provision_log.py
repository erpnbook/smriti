# Copyright (c) 2026, AITDL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMRITIProvisionLog(Document):
    """
    Immutable provisioning step audit log.

    One record per provisioning step per run.
    Grouped by run_id; ordered by step_sequence.
    Never modified after creation — only new records are appended.
    """
    def before_save(self):
        # Enforce immutability: only allow insert, never update
        if not self.is_new():
            frappe.throw('Provision Log records are immutable and cannot be modified after creation.')
