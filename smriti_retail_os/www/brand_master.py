# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/brand_master.py
# @description: SMRITI Brand Master page controller — brand management UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
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

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("brand_master")
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
    context.title = "SMRITI Brand Master"

    return context
