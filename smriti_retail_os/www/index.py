# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/index.py
# @description: SMRITI root index controller — entry-point redirect and session check.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# @file: smriti_retail_os/www/index.py
# @description: Root route handler — server-side redirect based on login state and role.

import frappe

no_cache = 1

def get_context(context):
    user = frappe.session.user

    if not user or user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("index")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect
        frappe.local.flags.redirect_location = "/setup-wizard"
        raise frappe.Redirect

    from smriti_retail_os.boot import _get_smriti_route
    roles = frappe.get_roles()
    frappe.local.flags.redirect_location = _get_smriti_route(roles)
    raise frappe.Redirect
