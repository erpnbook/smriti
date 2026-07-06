# -*- coding: utf-8 -*-
#
# @file: smriti_sales_kpi_snapshot.py
# @description: Document controller class for SMRITI Sales KPI Snapshot.
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

class SMRITISalesKPISnapshot(Document):
    def on_trash(self):
        if not frappe.flags.in_test:
            frappe.throw(
                _("SMRITI Sales KPI Snapshot records cannot be deleted manually."),
                frappe.ValidationError
            )
