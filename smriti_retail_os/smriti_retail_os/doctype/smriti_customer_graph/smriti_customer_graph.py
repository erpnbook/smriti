# -*- coding: utf-8 -*-
#
# @file: smriti_customer_graph.py
# @description: Document controller class for SMRITI Customer Graph.
#               Enforces read-only database invariants.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITICustomerGraph(Document):
    def autoname(self):
        self.name = self.customer

    def validate(self):
        # Enforce that normal users cannot write directly to Customer Graph
        if not self.flags.ignore_permissions and frappe.session.user != "Administrator":
            if not frappe.user.has_role("System Manager"):
                frappe.throw(
                    _("Direct modifications to SMRITI Customer Graph are prohibited. This is a system-derived read-only ledger."),
                    frappe.PermissionError
                )
