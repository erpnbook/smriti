# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-presentation.py
# @description: Page controller for SMRITI Retail OS Business Owner Presentation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.5
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

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
    context.title = "SMRITI Retail OS — Owner Presentation"

    return context
