# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-home.py
# @description: Python controller for the standalone SMRITI Control Center.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Store Manager or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
#
# NOTE: This file MUST be named smriti-home.py (hyphenated) to match
#       www/smriti-home.html. Frappe resolves .py by exact filename.
#       The underscore variant smriti_home.py is kept as a legacy stub.
#

import frappe
import frappe.sessions

no_cache = 1
title = "SMRITI Control Center"

def get_context(context):
    """
    Called by Frappe before rendering www/smriti-home.html.
    - Redirects Guest users to /login
    - Ensures only Store Managers / System Managers can access
    - Strips all Frappe chrome (navbar, sidebar, web includes)
    """
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    check_page_access("smriti-home")

    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.cashier    = frappe.session.user
    context.show_platform_admin = "System Manager" in roles or frappe.session.user == "Administrator"
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    context.app_version = frappe.get_attr("smriti_retail_os.__version__")

    return context
