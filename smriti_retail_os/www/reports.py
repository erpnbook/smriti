# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/reports.py
# @description: Reports dashboard — role-gated server-side controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
import frappe.sessions

no_cache = 1

def get_context(context):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(user)
    allowed = {"SMRITI Store Manager", "SMRITI Admin", "System Manager", "Administrator"}
    if not allowed.intersection(set(roles)):
        frappe.throw(_("Access Denied"), frappe.PermissionError)

    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    # Make sure cashier and csrf_token are populated for the template
    context.cashier = user
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Reports — SMRITI Retail OS"

    return context
