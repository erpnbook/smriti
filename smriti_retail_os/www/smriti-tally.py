# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-tally.py
# @description: SMRITI TallyPrime Integration page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

no_cache = 1
title = "TallyPrime Integration — SMRITI"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = set(frappe.get_roles(frappe.session.user))
    allowed = {"System Manager", "Administrator", "SMRITI Store Manager", "Accountant"}
    if not (roles & allowed):
        frappe.throw(
            "Access Denied: TallyPrime Integration console is restricted to System Managers, Store Managers, and Accountants.",
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
