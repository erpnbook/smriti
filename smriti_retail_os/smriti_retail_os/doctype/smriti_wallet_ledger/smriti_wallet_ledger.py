# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
from frappe.model.document import Document
from frappe import _

class SMRITIWalletLedger(Document):
    def validate(self):
        if not self.is_new():
            frappe.throw(_("Wallet Ledger records are immutable and cannot be updated."))

    def on_trash(self):
        frappe.throw(_("Wallet Ledger records are immutable and cannot be deleted."))
