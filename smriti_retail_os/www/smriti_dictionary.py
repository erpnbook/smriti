# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-dictionary.py
# @description: SMRITI Business Dictionary page controller — KGF term lookup context.
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
from smriti_retail_os.services import dictionary_service

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Business Dictionary"

    # Fetch categories
    context.categories = [
        "Inventory", "Distribution", "Forecasting", "Audit",
        "Sales", "Customer", "Outlet", "System", "Governance", "Training"
    ]

    # Fetch initial terms list
    context.terms = dictionary_service.get_active_terms()
