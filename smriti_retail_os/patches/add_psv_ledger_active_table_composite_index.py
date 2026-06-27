# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/add_psv_ledger_active_table_composite_index.py
# @description: Adds composite index smriti_psv_ledger_company_cp_variant to tabPSV Ledger Entry.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def execute():
    doctype_name = "PSV Ledger Entry"
    table_name = "tabPSV Ledger Entry"
    index_name = "smriti_psv_ledger_company_cp_variant"

    # Guard: only run if the table exists
    if not frappe.db.table_exists(doctype_name):
        frappe.logger().info(f"[PSV Index Patch] Table `{table_name}` does not exist. Skipping.")
        return

    # Check if the index already exists
    existing = frappe.db.sql(
        """
        SELECT COUNT(*) 
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        """,
        (table_name, index_name)
    )

    if existing and existing[0][0] > 0:
        frappe.logger().info(
            f"[PSV Index Patch] Composite index `{index_name}` already exists on `{table_name}`. Skipping."
        )
        return

    frappe.logger().info(
        f"[PSV Index Patch] Creating composite index `{index_name}` on `{table_name}`..."
    )

    frappe.db.sql(
        f"""
        ALTER TABLE `{table_name}`
        ADD INDEX `{index_name}` (company, channel_partner, item_variant, posting_datetime)
        """
    )

    frappe.logger().info(
        f"[PSV Index Patch] Composite index `{index_name}` created successfully."
    )
