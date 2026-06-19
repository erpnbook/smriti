# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/scheme_creator.py
# @description: SMRITI Scheme Creator page controller — pricing scheme UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/scheme_creator.py
# @description: Page controller for SMRITI Scheme Creator.
#               Enforces access checks and initializes template context.
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the SMRITI Scheme Creator."), frappe.AuthenticationError)

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
    context.title = "SMRITI Scheme Creator"

    # Fetch reference lists for autocomplete/select options in the Scheme Creator UI
    context.item_groups = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name", order_by="name asc")
    context.brands = frappe.get_all("Brand", pluck="name", order_by="name asc")

    return context
