# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/check_groups.py
# @description: Utility to validate and auto-create required ERPNext Item Groups.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
frappe.init(site='smriti_retail')
frappe.connect()
print('C-Groups:', frappe.get_all('Customer Group', pluck='name'))
print('Territories:', frappe.get_all('Territory', pluck='name'))
