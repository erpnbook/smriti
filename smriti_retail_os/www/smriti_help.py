# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-help.py
# @description: Page controller for the SMRITI Help Center article view.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-11
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

no_cache = 1

def get_context(context):
    # Guest → login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "Help Center — SMRITI Retail OS"
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    context.base_template_path = "smriti_retail_os/templates/blank.html"
    
    # Get article key from query param
    article_key = frappe.form_dict.get("article")
    context.article_key = article_key
