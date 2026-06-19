# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_safe.py
# @description: SMRITI Safe page controller — authenticated context provider.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe

no_cache = 1

def get_context(context):
    # Only allow admin users
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.local.flags.redirect_location = "/smriti"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Safe Mode"
