# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-login.py
# @description: Python controller for the SMRITI branded login page.
#               Redirects already-authenticated users to their SMRITI home route.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: This file MUST be named smriti-login.py (hyphenated) to match
#       www/smriti-login.html. Frappe resolves .py by exact filename.
#       The underscore variant smriti_login.py is kept as a legacy stub.
#

import frappe

no_cache = 1

def get_context(context):
    # Already logged in — redirect to SMRITI home
    if frappe.session.user != "Guest":
        from smriti_retail_os.boot import _get_smriti_route
        from smriti_retail_os.security_api import check_page_access
        try:
            check_page_access("smriti-login")
        except frappe.PermissionError:
            frappe.local.flags.redirect_location = "/smriti-home"
            raise frappe.Redirect
    context.title    = "SMRITI Retail OS — Sign In"
