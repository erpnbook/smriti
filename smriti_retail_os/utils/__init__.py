# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/utils/__init__.py
# @description: SMRITI Retail OS utilities package initializer.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# utils package init

import frappe

def get_client_ip():
    """
    Returns the client IP address from the request context, falling back to localhost.
    M-2 remediation (hardcoding audit 2026-07-03)
    """
    return getattr(frappe.local, "request_ip", "127.0.0.1")

