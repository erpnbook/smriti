# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/security.py
# @description: Page controller for SMRITI Security & Workflow Center.
#               Enforces access checks and initializes template context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from smriti_retail_os.security_api import _get_smriti_admin_email

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the SMRITI Security Center."), frappe.AuthenticationError)

    # Block Admin (Business Owner) from Security Center page
    _admin_email = _get_smriti_admin_email()
    if frappe.session.user in ("Admin", _admin_email):
        frappe.throw(_("Access Denied: The Admin (Business Owner) account is blocked from Security Center."), frappe.PermissionError)

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("security")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Security Center"
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    context.user = frappe.session.user
    
    # Determine if user is Security Architect
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0

    # Fetch reference options for User Permission selectors
    context.companies = frappe.get_all(
        "Company",
        fields=["name", "company_name"],
        order_by="company_name asc"
    )
    
    context.warehouses = frappe.get_all(
        "Warehouse",
        filters={"is_group": 0, "disabled": 0},
        fields=["name", "warehouse_name"],
        order_by="warehouse_name asc"
    )

    # Fetch retail doctypes list that managers can assign permissions for
    context.retail_doctypes = ["Company", "Warehouse"]

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
