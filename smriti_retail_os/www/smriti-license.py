# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-license.py
# @description: SMRITI License page controller — license key activation UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/www/smriti-license.py
# @description: Python controller for the SMRITI License & Registration page.
#               Enforces login and SMRITI System Admin / System Manager role.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md §9
# @version: 1.8.6
#

import frappe

no_cache = 1
title = "License & Registration — SMRITI"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-license")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti"
        raise frappe.Redirect

    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
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

    return context
