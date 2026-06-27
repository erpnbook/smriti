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

    # Only System Manager / Administrator allowed
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.local.flags.redirect_location = "/smriti"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Safe Mode"
