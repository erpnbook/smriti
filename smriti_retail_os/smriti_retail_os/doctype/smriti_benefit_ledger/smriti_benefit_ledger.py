# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_ledger/smriti_benefit_ledger.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SMRITIBenefitLedger(Document):
    def validate(self):
        # Allow INSERT, block all UPDATEs (immutability)
        if not self.is_new():
            frappe.throw(
                _("Benefit Ledger entries are immutable and cannot be updated."),
                frappe.ValidationError
            )

    def on_trash(self):
        # Block all DELETEs
        frappe.throw(
            _("Deleting Benefit Ledger entries is prohibited."),
            frappe.ValidationError
        )
