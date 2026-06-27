# -*- coding: utf-8 -*-
#
# @file: smriti_explain_audit_event.py
# @description: Document controller class for SMRITI Explain Audit Event.
#               Enforces read-only audit log validations and autonames events.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
import uuid

class SMRITIExplainAuditEvent(Document):
    def autoname(self):
        self.name = f"EXP-AUD-{str(uuid.uuid4())[:8].upper()}"

    def validate(self):
        # Enforce read-only constraint on manual updates by non-admin/system-manager users
        if not self.flags.ignore_permissions and frappe.session.user != "Administrator":
            if not frappe.user.has_role("System Manager"):
                frappe.throw(
                    _("SMRITI Explain Audit Event is a system-derived read-only audit log and cannot be manually modified."),
                    frappe.PermissionError
                )
