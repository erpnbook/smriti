# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/sizewise_invoice.py
# @description: Page controller for SMRITI Sizewise Tax Invoice portal.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
from __future__ import unicode_literals
import frappe

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login'
        raise frappe.Redirect

    context.csrf_token = frappe.sessions.get_csrf_token()
    context.cashier = frappe.session.user
    context.no_cache = True
    return context
