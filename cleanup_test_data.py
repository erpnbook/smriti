# -*- coding: utf-8 -*-
#
# @file: cleanup_test_data.py
# @description: Cleans up stale test data and temporary database entries.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
frappe.init(site="smriti_retail")
frappe.connect()
count_before = frappe.db.sql("SELECT COUNT(*) FROM `tabItem Tax` WHERE parent LIKE 'TEST-ART%%'")[0][0]
frappe.db.sql("DELETE FROM `tabItem Tax` WHERE parent LIKE 'TEST-ART%%'")
frappe.db.commit()
print(f"Cleaned {count_before} stale Item Tax rows")
frappe.destroy()
