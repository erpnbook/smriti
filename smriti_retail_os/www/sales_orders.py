# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/sales_orders.py
# @description: Python controller for the standalone SMRITI Sales Orders module.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Store Manager or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: MIT
#

import frappe

no_cache = 1
title = "SMRITI Sales Orders"

def get_context(context):
    """
    Called by Frappe before rendering www/sales_orders.html.
    - Redirects Guest users to /login
    - Ensures only Store Managers / System Managers can access
    - Strips all Frappe chrome (navbar, sidebar, web includes)
    """
    # Redirect unauthenticated users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Role guard — Sales Orders module is manager-only
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(
            "Access Denied: Sales Orders is restricted to Store Managers and System Managers.",
            frappe.PermissionError
        )

    # Strip ALL Frappe web includes — this page is 100% standalone
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
