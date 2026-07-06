# -*- coding: utf-8 -*-
#
# @file: smriti_walk_in_visit.py
# @description: Document controller class for SMRITI Walk In Visit.
#               Validates exit reasons and state invariants.
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

class SMRITIWalkInVisit(Document):
    def validate(self):
        if self.status == "Exited" and not self.reason_for_no_purchase:
            frappe.throw(
                _("An exit reason ('reason_for_no_purchase') is required when the status is set to Exited."),
                frappe.ValidationError
            )
            
        if self.status == "Converted" and not self.sales_invoice and not self.pos_invoice:
            frappe.throw(
                _("A sales invoice link ('sales_invoice' or 'pos_invoice') is required when the status is set to Converted."),
                frappe.ValidationError
            )
