# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/platform_center.py
# @description: Python controller for the SMRITI Platform Center.
#               - Enforces Guest redirect
#               - Allows both Administrator (full access) and Admin (restricted view)
#               - Strips Frappe chrome for clean standalone rendering
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-02
# @version: 1.8.6
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

    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    context.current_user  = user
    # Flag consumed by the Jinja template to conditionally render restricted UI
    context.is_admin_account = (user == "Admin")

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
