# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-knowledge-studio.py
# @description: Page controller for SMRITI Knowledge Studio web workspace.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: MIT
#

import frappe
import frappe.sessions

no_cache = 1

def get_context(context):
    """
    Called by Frappe before rendering www/smriti-knowledge-studio.html.
    - Redirects Guest users to /login
    - Strips default Frappe headers and chrome
    """
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Knowledge Studio"
    context.csrf_token = frappe.sessions.get_csrf_token() if getattr(frappe.local, "session_obj", None) else ""
    context.base_template_path = "smriti_retail_os/templates/blank.html"
    context.no_header = True
    context.no_breadcrumbs = True
    context.show_sidebar = False
    
    # Pass initial cash/user context
    context.cashier = frappe.session.user
    return context
