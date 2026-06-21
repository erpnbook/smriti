# -*- coding: utf-8 -*-
#
# @file: smriti_sales_kpi_snapshot.py
# @description: Document controller class for SMRITI Sales KPI Snapshot.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITISalesKPISnapshot(Document):
    def on_trash(self):
        if not frappe.flags.in_test:
            frappe.throw(
                _("SMRITI Sales KPI Snapshot records cannot be deleted manually."),
                frappe.ValidationError
            )
