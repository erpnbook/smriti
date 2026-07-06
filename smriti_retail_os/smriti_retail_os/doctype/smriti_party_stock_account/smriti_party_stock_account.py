# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_party_stock_account/smriti_party_stock_account.py
# @description: DocType controller for SMRITI Party Stock Account.
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

class SMRITIPartyStockAccount(Document):
    def autoname(self):
        # Auto-name format: "Customer-Location Name"
        clean_loc = self.location_name.strip()
        self.name = f"{self.customer}-{clean_loc}"
