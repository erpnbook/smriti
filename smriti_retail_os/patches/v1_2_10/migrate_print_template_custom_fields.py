# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/v1_2_10/migrate_print_template_custom_fields.py
# @description: One-time patch to migrate legacy programmatic custom fields for SMRITI Print Template.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

def execute():
    """
    Deletes the legacy programmatic custom fields for SMRITI Print Template 
    from the tabCustom Field table after verifying that the target table has the columns,
    allowing the new file-based native schema fields to take over cleanly.
    """
    if smriti.db.exists("DocType", "SMRITI Print Template"):
        # Verify that all 4 custom fields are present as columns in tabSMRITI Print Template
        required_cols = ["custom_field_mappings_json", "custom_version", "custom_active", "custom_is_default"]
        
        for col in required_cols:
            if not frappe.db.has_column("SMRITI Print Template", col):
                frappe.throw(
                    msg=f"Migration failed: Column '{col}' is missing from 'tabSMRITI Print Template'. Standardize schema first.",
                    title="Migration Safety Check Failed"
                )
        
        # Delete Custom Field records
        smriti.db.delete("Custom Field", {"dt": "SMRITI Print Template"})
        # Mark SMRITI Print Template as a standard doctype in tabDocType before model sync
        smriti.db.set_value("DocType", "SMRITI Print Template", "custom", 0)
        smriti.db.commit()
        print("[SMRITI Patch] Cleaned up legacy custom fields successfully.")

