# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/psv-dashboard.py
# @description: Python controller for the standalone SMRITI PSV Dashboard page.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Store Manager or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: This file MUST be named psv-dashboard.py (hyphenated) to match
#       www/psv-dashboard.html. Frappe resolves .py by exact filename.
#       The underscore variant psv_dashboard.py is kept as a legacy stub.
#

import frappe

no_cache = 1
title = "SMRITI PSV Dashboard"

def get_context(context):
    """
    Called by Frappe before rendering www/psv-dashboard.html.
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
            "Access Denied: SMRITI PSV Dashboard is restricted to Store Managers and System Managers.",
            frappe.PermissionError
        )

    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.user       = frappe.session.user
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""

    # Get companies for dropdown filter
    context.companies = frappe.get_all("Company", fields=["name"])

    return context
