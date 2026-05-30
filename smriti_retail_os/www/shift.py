# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/shift.py
# @description: Python controller for the standalone SMRITI Shift Management.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Cashier, Store Manager, or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: MIT
#

import frappe

no_cache = 1
title = "SMRITI Shift Management"

def get_context(context):
    """
    Called by Frappe before rendering www/shift.html.
    - Redirects Guest users to /login
    - Ensures Cashiers / Store Managers / System Managers can access
    - Strips all Frappe chrome (navbar, sidebar, web includes)
    """
    # Redirect unauthenticated users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Role guard — Cashiers, Store Managers, System Managers allowed
    roles = frappe.get_roles(frappe.session.user)
    allowed = ["SMRITI Cashier", "SMRITI Store Manager", "System Manager"]
    if not any(r in roles for r in allowed):
        frappe.throw(
            "Access Denied: Shift Management is restricted to Cashiers and Managers.",
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
