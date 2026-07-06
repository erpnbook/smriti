# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/www/smriti_clienteling.py
# @desc:    Page controller for SMRITI Clienteling Studio.
#           - Enforces login (redirects Guests to /login)
#           - Role guard
#           - Strips all Frappe chrome
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe

no_cache = 1


def get_context(context):
    """
    Called by Frappe before rendering www/smriti-clienteling.html.
    Enforces authentication, role access, and injects context for the UI.
    """
    # ── Guest redirect ────────────────────────────────────────────────────────
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-clienteling")
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

    return context
