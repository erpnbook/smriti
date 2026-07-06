# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/offline.py
# @description: Page controller for SMRITI PWA offline fallback page.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
"""
www/offline.py — Offline fallback page context.
Served at /offline by Frappe's www system.
No authentication required — must be publicly accessible.
"""
no_cache = 1
no_sitemap = 1

def get_context(context):
    context.no_cache = 1
    context.title = "SMRITI — Offline"
