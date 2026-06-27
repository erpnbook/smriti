# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/delivery_challan.py
# @description: Page controller for SMRITI Delivery Challan Management portal.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-10
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

no_cache = 1
title = "SMRITI Delivery Challans"

def get_context(context):
    """
    Called by Frappe before rendering www/delivery_challan.html.
    - Redirects Guest users to /login
    - Ensures Cashiers / Store Managers / System Managers can access
    - Strips all Frappe chrome
    """
    # Redirect unauthenticated users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Role guard
    roles = frappe.get_roles(frappe.session.user)
    allowed_roles = ["SMRITI Cashier", "SMRITI Store Manager", "System Manager"]
    if not any(r in roles for r in allowed_roles):
        frappe.throw(
            "Access Denied: Delivery Challan module is restricted to Cashiers, Store Managers, and System Managers.",
            frappe.PermissionError
        )

    # Strip ALL Frappe web includes
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
