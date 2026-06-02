# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/platform_center.py
# @description: Python controller for the SMRITI Platform Center.
#               - Enforces Guest redirect
#               - Allows both Administrator (full access) and Admin (restricted view)
#               - Strips Frappe chrome for clean standalone rendering
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-02
# @version: 1.2.0
# @license: MIT
#

import frappe

no_cache = 1
title = "SMRITI Platform Center"

# Permitted users — everyone else is blocked
ALLOWED_USERS = {"Administrator", "Admin"}

def get_context(context):
    """
    Sets up rendering context for the SMRITI Platform Center page.

    Access policy:
        - Guest               → redirect to /login
        - Administrator       → full access, is_admin_account = False
        - Admin (Biz Owner)   → restricted view, is_admin_account = True
        - Any other user      → PermissionError (403)
    """
    user = frappe.session.user

    # Redirect unauthenticated users
    if user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Block everyone who is not in the allowed set
    if user not in ALLOWED_USERS:
        frappe.throw(
            "Access Denied: Platform Center is restricted to Administrator and Admin accounts only.",
            frappe.PermissionError
        )

    # Strip ALL Frappe web includes to render SMRITI operational UI cleanly
    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.csrf_token    = frappe.sessions.get_csrf_token()
    context.current_user  = user
    # Flag consumed by the Jinja template to conditionally render restricted UI
    context.is_admin_account = (user == "Admin")

    return context
