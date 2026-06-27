# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/purchase.py
# @description: Python controller for the standalone SMRITI Purchase Manager.
#               - Enforces login (redirects Guests to /login)
#               - Enforces Store Manager or System Manager role
#               - Strips all Frappe chrome from the page context
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
#

import frappe

no_cache = 1
title = "SMRITI Purchase Manager"

def get_context(context):
    """
    Called by Frappe before rendering www/purchase.html.
    - Redirects Guest users to /login
    - Ensures only Store Managers / System Managers can access
    - Strips all Frappe chrome (navbar, sidebar, web includes)
    """
    # Redirect unauthenticated users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Role guard — purchase module is manager-only
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(
            "Access Denied: Purchase Manager is restricted to Store Managers and System Managers.",
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

    # Pass license and site config for UI Configuration Engine
    from smriti_retail_os.license.manager import get_license_summary
    context.smriti_license = get_license_summary()
    
    from smriti_retail_os.company_api import get_company_settings, get_active_company
    active_company = get_active_company()
    comp_settings = get_company_settings(active_company) if active_company else {}
    
    context.smriti_site_config = {
        "store_theme": comp_settings.get("store_theme") or "hybrid",
        "store_experience": comp_settings.get("store_experience") or "standard",
        "terminal_type": comp_settings.get("terminal_type") or "standard",
        "brand_overrides": comp_settings.get("brand_overrides") or {}
    }

    return context
