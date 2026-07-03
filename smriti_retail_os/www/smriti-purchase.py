# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/www/smriti-purchase.py
# @desc:    Page controller for SMRITI Purchase Studio.
#           - Enforces login (redirects Guests to /login)
#           - Role guard: Cashier | Store Manager | System Manager
#           - Strips all Frappe chrome
#           - Injects: user, csrf_token, license, site_config, user_roles, purchase_settings
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 7 (www Page Controller)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe

no_cache = 1
title    = "SMRITI Purchase Studio"


def get_context(context):
    """
    Called by Frappe before rendering www/smriti-purchase.html.
    Enforces authentication, role access, and injects context for the UI.
    """
    # ── Guest redirect ────────────────────────────────────────────────────────
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-purchase")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect

    # ── Strip ALL Frappe web includes ─────────────────────────────────────────
    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    # ── User context ──────────────────────────────────────────────────────────
    context.cashier    = frappe.session.user
    context.user_roles = list(roles)

    # ── CSRF token ────────────────────────────────────────────────────────────
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""

    # ── License context ───────────────────────────────────────────────────────
    try:
        from smriti_retail_os.license.manager import get_license_summary
        context.smriti_license = get_license_summary()
    except Exception:
        context.smriti_license = {}

    # ── Company site config ───────────────────────────────────────────────────
    try:
        from smriti_retail_os.company_api import get_company_settings, get_active_company
        active_company = get_active_company()
        comp_settings  = get_company_settings(active_company) if active_company else {}
        context.smriti_site_config = {
            "store_theme":      comp_settings.get("store_theme")      or "hybrid",
            "store_experience": comp_settings.get("store_experience") or "standard",
            "terminal_type":    comp_settings.get("terminal_type")    or "standard",
            "brand_overrides":  comp_settings.get("brand_overrides")  or {}
        }
    except Exception:
        context.smriti_site_config = {}

    # ── Purchase Settings (policy + threshold for frontend UI gating) ─────────
    try:
        from smriti_retail_os.purchase_studio.service.purchase_settings_service import get_settings
        context.purchase_settings = get_settings()
    except Exception:
        context.purchase_settings = {
            "purchase_invoice_policy": "both",
            "approval_threshold": 0,
            "grn_mandatory": False,
            "allow_over_receipt": False,
            "auto_create_items": True
        }

    return context
