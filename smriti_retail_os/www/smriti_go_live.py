# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_go_live.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_go_live.py
# @description: SMRITI Go-Live page controller — onboarding completion UI context.
#

import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)

    roles = set(frappe.get_roles(frappe.session.user))
    if not ({"SMRITI System Admin", "System Manager", "Administrator"} & roles):
        frappe.throw("Access restricted to System Manager.", frappe.PermissionError)

    context.no_cache = 1
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
