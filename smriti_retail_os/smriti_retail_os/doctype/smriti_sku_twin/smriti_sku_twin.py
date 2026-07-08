# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_sku_twin/smriti_sku_twin.py
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

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.model.document import Document

class SMRITISKUTwin(Document):
    def validate(self):
        # Uniqueness validation
        duplicate = smriti.db.exists(
            "SMRITI SKU Twin",
            {
                "company": self.company,
                "party_stock_account": self.party_stock_account,
                "item_code": self.item_code,
                "name": ["!=", self.name]
            }
        )
        if duplicate:
            frappe.throw(
                frappe._("A Product Twin already exists for company {0}, PSA {1}, and item {2} ({3}).")
                .format(self.company, self.party_stock_account, self.item_code, duplicate)
            )
