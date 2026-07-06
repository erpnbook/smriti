# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-coming-soon.py
# @description: SMRITI Coming Soon page controller — feature roadmap display.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/www/smriti-coming-soon.py
# @description: Page controller for the SMRITI Coming Soon placeholder view.
#
import frappe

no_cache = 1

def get_context(context):
    # Guest → login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "Coming Soon — SMRITI Retail OS"
