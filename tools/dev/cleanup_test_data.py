# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/cleanup_test_data.py
# @description: Test data cleanup utility — removes SMRITI test fixtures after test runs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
"""
Temporary cleanup utility — removes stale Item Tax child rows
from test items that have accumulated hundreds of duplicates
across repeated test runs.
"""
import frappe


def clean_stale_item_taxes():
    """Remove duplicate Item Tax rows from TEST-ART items."""
    count = frappe.db.count("Item Tax", {"parent": ["like", "TEST-ART%"]})
    if count > 6:
        frappe.db.delete("Item Tax", {"parent": ["like", "TEST-ART%"]})
        frappe.db.commit()
    return f"Cleaned {count} rows"
