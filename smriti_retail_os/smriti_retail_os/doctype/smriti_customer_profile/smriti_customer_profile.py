# -*- coding: utf-8 -*-
#
# @file: smriti_customer_profile.py
# @description: Document controller class for SMRITI Customer Profile.
#               Enforces read-only database invariants.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITICustomerProfile(Document):
    def autoname(self):
        self.name = self.customer

    def validate(self):
        # Enforce that normal users cannot write directly to Customer Profile
        if not self.flags.ignore_permissions and frappe.session.user != "Administrator":
            if not frappe.user.has_role("System Manager"):
                frappe.throw(
                    _("Direct modifications to SMRITI Customer Profile are prohibited. This is a system-derived read-only presentation layer."),
                    frappe.PermissionError
                )
