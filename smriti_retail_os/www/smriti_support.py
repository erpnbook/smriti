# -*- coding: utf-8 -*-
# @file: smriti_retail_os/www/smriti_support.py
# @description: Page controller for SMRITI Support Center.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.

import frappe

no_cache = 1
title = "SMRITI Support Center"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.web_include_js  = []
    context.web_include_css = []
    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"
    context.cashier    = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()

    # System info for diagnostics
    context.frappe_version = frappe.__version__
    context.site_name = frappe.local.site

    return context
