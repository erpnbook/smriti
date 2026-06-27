# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-go-live.py
# @description: SMRITI Go-Live page controller — onboarding completion UI context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)

    roles = set(frappe.get_roles(frappe.session.user))
    if not ({"SMRITI System Admin", "System Manager", "Administrator"} & roles):
        frappe.throw("Access restricted to System Manager.", frappe.PermissionError)

    context.no_cache = 1
    context.csrf_token = frappe.sessions.get_csrf_token()

