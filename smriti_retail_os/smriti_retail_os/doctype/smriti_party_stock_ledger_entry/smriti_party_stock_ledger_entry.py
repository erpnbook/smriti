# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_party_stock_ledger_entry/smriti_party_stock_ledger_entry.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SMRITIPartyStockLedgerEntry(Document):
    def validate(self):
        if not self.is_new():
            frappe.throw(
                "SMRITI Party Stock Ledger entries are immutable. Use a reversal entry to correct.",
                frappe.ValidationError
            )

    def on_trash(self):
        frappe.throw(
            "SMRITI Party Stock Ledger entries cannot be deleted. Use a reversal entry to correct.",
            frappe.ValidationError
        )
