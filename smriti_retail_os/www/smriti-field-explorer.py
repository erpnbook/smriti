# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-field-explorer.py
# @description: SMRITI Universal Field Explorer — page context & auth controller.
#               Route: /smriti-field-explorer
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-26
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.

import frappe

no_cache = 1

def get_context(context):
    # Guest → redirect to login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache   = 1
    context.title      = "SMRITI Universal Field Explorer"
    context.user       = frappe.session.user
    context.full_name  = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    # Pass initial doctype from query param (for direct linking from other modules)
    context.initial_doctype = frappe.request.args.get("doctype", "Item")
    context.initial_mode    = frappe.request.args.get("mode", "fields")
    context.initial_search  = frappe.request.args.get("search", "")

    # Check if opened as callback from barcode studio
    context.callback_route  = frappe.request.args.get("callback", "")
    context.callback_row    = frappe.request.args.get("row", "")
