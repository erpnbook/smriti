# -*- coding: utf-8 -*-
#
# @file: smriti_commission_rule.py
# @description: Document controller class for SMRITI Commission Rule.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class SMRITICommissionRule(Document):
    def validate(self):
        # Prevent start_date > end_date
        if self.effective_from and self.effective_to:
            if getdate(self.effective_from) > getdate(self.effective_to):
                frappe.throw(
                    _("Effective From date ({0}) cannot be after Effective To date ({1}).")
                    .format(self.effective_from, self.effective_to),
                    frappe.ValidationError
                )
