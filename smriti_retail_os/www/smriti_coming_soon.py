# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_coming_soon.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_coming_soon.py
# @description: Page controller for the SMRITI Coming Soon placeholder view.
#

import frappe

no_cache = 1

def get_context(context):
    # Guest → login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "Coming Soon — SMRITI Retail OS"
