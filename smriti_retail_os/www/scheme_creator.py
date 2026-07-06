# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/scheme_creator.py
# @description: SMRITI Scheme Creator page controller — pricing scheme UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/www/scheme_creator.py
# @description: Page controller for SMRITI Scheme Creator.
#               Enforces access checks and initializes template context.
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the SMRITI Scheme Creator."), frappe.AuthenticationError)

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("scheme_creator")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect

    # Cleanse default web templates to enforce standalone SMRITI presentation
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
    context.user = frappe.session.user
    roles = frappe.get_roles(frappe.session.user)
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0
    context.title = "SMRITI Scheme Creator"

    # Fetch reference lists for autocomplete/select options in the Scheme Creator UI
    context.item_groups = frappe.get_all("Item Group", filters={"is_group": 0}, pluck="name", order_by="name asc")
    context.brands = frappe.get_all("Brand", pluck="name", order_by="name asc")

    return context
