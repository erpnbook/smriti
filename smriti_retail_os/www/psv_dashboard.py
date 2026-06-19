# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/psv_dashboard.py
# @description: SMRITI PSV Dashboard page controller — channel stock UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe

no_cache = 1
title = "SMRITI PSV Dashboard"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(frappe.session.user)
    allowed_roles = ["SMRITI Store Manager", "System Manager"]
    if not any(r in roles for r in allowed_roles):
        frappe.throw(
            "Access Denied: SMRITI PSV Dashboard is restricted to Store Managers and System Managers.",
            frappe.PermissionError
        )

    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.user = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()

    # Get companies for dropdown filter
    context.companies = frappe.get_all("Company", fields=["name"])

    return context
