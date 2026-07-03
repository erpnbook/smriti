# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/www/smriti-purchase-order.py
# @desc:    Page controller for SMRITI Purchase Order dedicated form page.
#           - Enforces login (redirects Guests to /login)
#           - Role guard: SMRITI Store Manager | System Manager
#           - Strips all Frappe chrome
#           - Injects: user, csrf_token, user_roles, purchase_settings
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 7 (www Page Controller)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe

no_cache = 1
title    = "SMRITI — New Purchase Order"


def get_context(context):
    """
    Page controller for the dedicated Purchase Order creation form.
    Only SMRITI Store Managers and System Managers may create POs.
    """
    # ── Guest redirect ────────────────────────────────────────────────────────
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-purchase-order")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-purchase"
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
    roles = frappe.get_roles(frappe.session.user)
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

    # ── Purchase Settings ─────────────────────────────────────────────────────
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
