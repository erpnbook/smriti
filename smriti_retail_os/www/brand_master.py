# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/brand_master.py
# @description: SMRITI Brand Master page controller — brand management UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        return

    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: Only Store Managers and Administrators can access this page."), frappe.PermissionError)

    # Cleanse default web templates to enforce standalone SMRITI presentation
    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.csrf_token = frappe.sessions.get_csrf_token()
    context.user = frappe.session.user
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0
    context.title = "SMRITI Brand Master"

    return context
