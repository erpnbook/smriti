# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-license.py
# @description: SMRITI License page controller — license key activation UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-license.py
# @description: Python controller for the SMRITI License & Registration page.
#               Enforces login and SMRITI System Admin / System Manager role.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md §9
# @version: 1.0.0
#

import frappe

no_cache = 1
title = "License & Registration — SMRITI"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = set(frappe.get_roles(frappe.session.user))
    allowed = {"SMRITI System Admin", "System Manager", "Administrator"}
    if not (roles & allowed):
        frappe.throw(
            "Access Denied: License & Registration is restricted to SMRITI System Admins.",
            frappe.PermissionError
        )

    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"
    context.csrf_token      = frappe.sessions.get_csrf_token()

    return context
