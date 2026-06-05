# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/reports.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# @file: smriti_retail_os/www/reports.py
# @description: Reports dashboard — role-gated server-side controller.

import frappe

no_cache = 1

def get_context(context):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    roles = frappe.get_roles(user)
    allowed = {"SMRITI Store Manager", "SMRITI Admin",
               "System Manager", "Administrator"}
    if not allowed.intersection(set(roles)):
        frappe.throw("Access Denied", frappe.PermissionError)
    context.update({
        "title": "Reports — SMRITI Retail OS",
        "user": user
    })
