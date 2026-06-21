# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_dictionary.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_dictionary.py
# @description: SMRITI Business Dictionary page controller — KGF term lookup context.
#

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
