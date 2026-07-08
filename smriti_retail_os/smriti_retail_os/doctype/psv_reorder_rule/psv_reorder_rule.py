# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/psv_reorder_rule/psv_reorder_rule.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt
#
# DEPRECATED — 2026-07-02
# This DocType ("PSV Reorder Rule") is superseded by "SMRITI PSV Reorder Rule"
# (smriti_retail_os/doctype/smriti_psv_reorder_rule/).
# All active service code (psv_analysis_service.py, balance_engine.py) was
# migrated in BUG-005 to reference "SMRITI PSV Reorder Rule".
# This file is kept to avoid migration errors if any historical DB records exist.
# Action: Run `smriti.db.count("PSV Reorder Rule")` on staging. If zero, remove
# this folder and add a migration patch in v2.1.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.model.document import Document


class PSVReorderRule(Document):
	pass

