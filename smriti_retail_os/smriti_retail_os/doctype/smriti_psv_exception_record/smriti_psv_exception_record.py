# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_psv_exception_record/smriti_psv_exception_record.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SMRITIPSVExceptionRecord(Document):
    def before_save(self):
        if self.status == "Reconciled" and self.db_essential("status") != "Reconciled":
            self.reconciled_by = frappe.session.user
            self.reconciled_on = frappe.utils.now_datetime()
            
            # Check if all exceptions for this location are resolved, if so, restore status
            self.check_and_restore_location_status()

    def check_and_restore_location_status(self):
        # Check if there are any other pending exceptions for this account
        has_pending = frappe.db.exists("SMRITI PSV Exception Record", {
            "party_stock_account": self.party_stock_account,
            "status": "Pending Reconciliation",
            "name": ["!=", self.name]
        })
        if not has_pending:
            frappe.db.set_value("SMRITI Party Stock Account", self.party_stock_account, "status", "Active")
            
    def db_essential(self, fieldname):
        return frappe.db.get_value(self.doctype, self.name, fieldname)
