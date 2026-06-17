# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/stock-audit.py
# @description: Python controller for the standalone SMRITI Stock Audit page.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Store Manager or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.1
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: This file MUST be named stock-audit.py (hyphenated) to match
#       www/stock-audit.html. Frappe resolves .py by exact filename.
#       The underscore variant stock_audit.py is kept as a legacy stub.
#

import frappe

no_cache = 1
title = "SMRITI Stock Audits"

def get_context(context):
    """
    Called by Frappe before rendering www/stock-audit.html.
    - Redirects Guest users to /login
    - Ensures Store Managers / System Managers can access
    - Strips all Frappe chrome
    """
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(frappe.session.user)
    allowed_roles = ["SMRITI Store Manager", "System Manager"]
    if not any(r in roles for r in allowed_roles):
        frappe.throw(
            "Access Denied: Stock Audits management is restricted to Store Managers and System Managers.",
            frappe.PermissionError
        )

    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.cashier    = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()

    return context
