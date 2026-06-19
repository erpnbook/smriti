# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/mark_setup_complete.py
# @description: SMRITI Mark Setup Complete — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe


def execute():
    """
    Mark ERPNext/Frappe Setup Wizard as complete.
    Prevents wizard appearing on fresh or reset sites.
    """
    try:
        # Primary: System Settings (Single DocType — correct method)
        frappe.db.set_single_value("System Settings", "setup_complete", 1)
        print("✅ System Settings.setup_complete = 1")
    except Exception as e:
        print(f"⚠ System Settings patch skipped: {e}")

    try:
        # Secondary: tabSingles direct update (belt + suspenders)
        frappe.db.sql("""
            INSERT INTO `tabSingles` (doctype, field, value)
            VALUES ('System Settings', 'setup_complete', '1')
            ON DUPLICATE KEY UPDATE value = '1'
        """)
        print("✅ tabSingles setup_complete = 1")
    except Exception as e:
        print(f"⚠ tabSingles patch skipped: {e}")

    # NOTE: Do NOT set Global Defaults.setup_complete
    # Global Defaults is a Single DocType with no 'setup_complete' field
    # in standard ERPNext — this would cause migration failure

    frappe.db.commit()
    print("✅ SMRITI: Setup Wizard patch complete")
