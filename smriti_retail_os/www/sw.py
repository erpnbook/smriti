# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/sw.py
# @description: Page controller for SMRITI PWA Service Worker route.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
"""
www/sw.py — Serves the SMRITI Service Worker at /sw.js (root scope).

The Service Worker MUST be served from the root path /sw.js for it to
control all SMRITI pages. This py file makes Frappe route /sw.js
to the physical file at public/js/sw.js via a passthrough response.
"""
import frappe
from frappe import _

no_cache  = 1
no_sitemap = 1

def get_context(context):
    # Serve the JS file content directly with correct MIME type
    sw_content = frappe.read_file(
        frappe.get_app_path('smriti_retail_os', 'public', 'js', 'sw.js')
    )
    frappe.response.update({
        'type':     'binary',
        'filename': 'sw.js',
        'content':  sw_content.encode('utf-8') if isinstance(sw_content, str) else sw_content,
    })
    frappe.local.response.setdefault('headers', {})
    frappe.local.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    frappe.local.response.headers['Service-Worker-Allowed'] = '/'
    frappe.local.response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    context.no_cache = 1
    return context
