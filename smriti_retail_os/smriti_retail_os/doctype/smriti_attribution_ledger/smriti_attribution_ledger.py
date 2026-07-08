# -*- coding: utf-8 -*-
#
# @file: smriti_attribution_ledger.py
# @description: Document controller class for SMRITI Attribution Ledger.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.model.document import Document

class SMRITIAttributionLedger(Document):
    def validate(self):
        if not self.is_new():
            db_doc = smriti.documents.get("SMRITI Attribution Ledger", self.name)
            for field in [
                "invoice_reference", "invoice_doctype", "customer", 
                "employee", "ownership_type", "revenue_credit", 
                "credit_percentage", "store", "company"
            ]:
                if self.get(field) != db_doc.get(field):
                    frappe.throw(
                        _("Field '{0}' in SMRITI Attribution Ledger is immutable and cannot be updated.").format(field),
                        frappe.ValidationError
                    )

    def on_trash(self):
        if not frappe.flags.in_test:
            frappe.throw(
                _("SMRITI Attribution Ledger records are immutable and cannot be deleted."),
                frappe.ValidationError
            )
