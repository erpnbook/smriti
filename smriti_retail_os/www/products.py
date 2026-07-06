# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/products.py
# @description: Python controller for the standalone SMRITI Products page.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Cashier, Store Manager, or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import frappe

no_cache = 1
title = "SMRITI Products catalog"

def get_context(context):
    """
    Called by Frappe before rendering www/products.html.
    - Redirects Guest users to /login
    - Ensures Cashiers / Store Managers / System Managers can access
    - Strips all Frappe chrome
    """
    # Redirect unauthenticated users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("products")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect

    # Strip ALL Frappe web includes
    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.cashier    = frappe.session.user
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""

    return context
