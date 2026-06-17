# -*- coding: utf-8 -*-
# @file: smriti_retail_os/www/psv_exception_analysis.py
# @description: Page controller for PSV Exception Analysis.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0

import frappe

no_cache = 1
title = "SMRITI PSV Exception Analysis"

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
    return context
