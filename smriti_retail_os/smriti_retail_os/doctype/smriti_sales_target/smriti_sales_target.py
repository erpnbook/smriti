# -*- coding: utf-8 -*-
#
# @file: smriti_sales_target.py
# @description: Document controller class for SMRITI Sales Target.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITISalesTarget(Document):
    def validate(self):
        # Ensure only one target exists per employee, company, fiscal_year, and month
        duplicate = frappe.db.exists("SMRITI Sales Target", {
            "employee": self.employee,
            "company": self.company,
            "fiscal_year": self.fiscal_year,
            "month": self.month,
            "name": ["!=", self.name]
        })
        if duplicate:
            frappe.throw(
                _("A SMRITI Sales Target already exists for Employee {0} in {1} ({2}) for {3}.")
                .format(self.employee, self.fiscal_year, self.month, self.company),
                frappe.ValidationError
            )
