# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/billing.py
# @description: Python controller for the standalone SMRITI Billing Terminal.
#               - Forces login redirect for unauthenticated users
#               - Marks the page as no_cache so Frappe doesn't serve stale HTML
#               - Strips all Frappe web includes (navbar, sidebar, etc.)
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
#

import frappe

# Frappe reads these module-level vars from www/*.py controllers
no_cache = 1
title = "SMRITI Billing Terminal"

def get_context(context):
    """
    Called by Frappe before rendering www/billing.html.
    - Redirects Guest users to /login
    - Removes all Frappe chrome (navbar, sidebar) from the page context
    - Removes web_include_js / web_include_css so our standalone page
      is truly self-contained with zero Frappe UI injected
    """
    # Redirect unauthenticated users to the SMRITI login page
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Strip ALL Frappe web includes — the billing page is 100% standalone
    # and manages its own CSS/JS. Injecting Frappe's web includes would
    # double-load fonts, trigger sidebar init, etc.
    context.web_include_js  = []
    context.web_include_css = []

    # Strip Frappe navbar / website header / footer from the template context
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    # Pass cashier info to template (available as {{ cashier }} in Jinja if needed)
    context.cashier = frappe.session.user
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
