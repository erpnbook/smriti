# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/add_smriti_feature_flag.py
# @description: SMRITI Add Smriti Feature Flag — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe


def execute():
    """
    Add custom_smriti_frontend_enabled field to System Settings.
    Allows instant disable of SMRITI frontend if production breaks.
    Default: 1 (enabled).
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    create_custom_fields({
        "System Settings": [{
            "fieldname": "custom_smriti_frontend_enabled",
            "label":     "SMRITI Frontend Enabled",
            "fieldtype": "Check",
            "default":   "1",
            "insert_after": "home_page",
            "description": (
                "Uncheck to disable SMRITI custom frontend and revert "
                "to standard Frappe Desk. Use in emergencies."
            ),
        }]
    })
    frappe.db.set_single_value(
        "System Settings", "custom_smriti_frontend_enabled", 1
    )
    frappe.db.commit()
    print("✅ SMRITI feature flag added to System Settings")
