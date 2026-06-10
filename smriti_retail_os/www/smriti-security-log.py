# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-security-log.py
# @description: Page controller for SMRITI Security Audit Log.
#               Enforces System Manager / Administrator access only.
#               No Frappe desk routes are exposed to end users.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-10
# @version: 1.8.2a
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

no_cache = 1
title = "SMRITI Security Audit Log"


def get_context(context):
    """
    Access policy:
      - Guest               → redirect to /smriti-login
      - Non-System Manager  → 403 PermissionError
      - System Manager      → full access
      - Administrator       → full access
    """
    user = frappe.session.user

    if user == "Guest":
        frappe.local.flags.redirect_location = "/smriti-login"
        raise frappe.Redirect

    roles = frappe.get_roles(user)
    if "System Manager" not in roles and user != "Administrator":
        frappe.throw(
            "Access Denied: SMRITI Security Audit Log requires System Manager role.",
            frappe.PermissionError,
        )

    # Strip all Frappe web chrome — render as pure SMRITI page
    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.csrf_token   = frappe.sessions.get_csrf_token()
    context.current_user = user
    context.title        = "SMRITI Security Audit Log"

    return context
