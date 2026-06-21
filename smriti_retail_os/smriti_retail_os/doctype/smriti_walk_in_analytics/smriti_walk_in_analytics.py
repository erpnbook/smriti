# -*- coding: utf-8 -*-
#
# @file: smriti_walk_in_analytics.py
# @description: Document controller class for SMRITI Walk In Analytics.
#               Enforces derived read-only invariant.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITIWalkInAnalytics(Document):
    def validate(self):
        # Enforce that normal users cannot write directly to Walk In Analytics
        if not self.flags.ignore_permissions and frappe.session.user != "Administrator":
            if not frappe.user.has_role("System Manager"):
                frappe.throw(
                    _("Direct modifications to SMRITI Walk In Analytics are prohibited. This is a system-derived read-only analytics snapshot."),
                    frappe.PermissionError
                )
