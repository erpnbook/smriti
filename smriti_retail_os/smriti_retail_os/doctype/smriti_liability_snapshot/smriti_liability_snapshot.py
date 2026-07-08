# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_liability_snapshot/smriti_liability_snapshot.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.model.document import Document

class SMRITILiabilitySnapshot(Document):
    def validate(self):
        filters = {"snapshot_date": self.snapshot_date}
        if self.company:
            filters["company"] = self.company
        else:
            filters["company"] = ["is", "not set"]
            
        duplicate = smriti.db.get("SMRITI Liability Snapshot", filters, "name")
        if duplicate and duplicate != self.name:
            frappe.throw(
                frappe._("A SMRITI Liability Snapshot already exists for company {0} on {1}.").format(
                    self.company or "Global", self.snapshot_date
                ),
                frappe.DuplicateEntryError
            )

