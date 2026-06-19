# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_login.py
# @description: SMRITI Login page controller — session validation and auth redirect.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe

no_cache = 1

def get_context(context):
    # Already logged in — redirect to SMRITI
    if frappe.session.user != "Guest":
        from smriti_retail_os.boot import _get_smriti_route
        roles = frappe.get_roles(frappe.session.user)
        frappe.local.flags.redirect_location = _get_smriti_route(roles)
        raise frappe.Redirect
    context.no_cache = 1
    context.title    = "SMRITI Retail OS — Sign In"
