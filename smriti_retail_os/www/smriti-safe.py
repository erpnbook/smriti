# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-safe.py
# @description: Python controller for the SMRITI Safe Mode / Recovery page.
#               Only System Manager or Administrator can access this page.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: This file MUST be named smriti-safe.py (hyphenated) to match
#       www/smriti-safe.html. Frappe resolves .py by exact filename.
#       The underscore variant smriti_safe.py is kept as a legacy stub.
#

import frappe

no_cache = 1

def get_context(context):
    # Redirect unauthenticated users to login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-safe")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Safe Mode"
