# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/add_psv_ledger_composite_index.py
# @description: SMRITI Add Psv Ledger Composite Index — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/patches/add_psv_ledger_composite_index.py
# @description: PERF-002 fix — Adds a composite index on
#               (party_stock_account, item_code, posting_datetime) to the
#               SMRITI Party Stock Ledger Entry table.
#
#               Without this index, every balance query performs a full table
#               scan on an append-only, ever-growing table. With 50 PSAs and
#               500 SKUs each over 2 years, this table could contain 10M+ rows.
#               The index makes balance queries use an index range scan instead.
#
#               Safe to run multiple times — checks if index exists before adding.
#

import frappe


def execute():
    table_name = "tabSMRITI Party Stock Ledger Entry"

    # Guard: only run if the table exists (module may not be installed)
    if not frappe.db.table_exists(table_name):
        frappe.logger().info(
            f"[PSV Index Patch] Table `{table_name}` does not exist. Skipping."
        )
        return

    index_name = "idx_psv_ledger_psa_item_dt"

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
            f"[PSV Index Patch] Index `{index_name}` already exists on `{table_name}`. Skipping."
        )
        return

    frappe.logger().info(
        f"[PSV Index Patch] Creating composite index `{index_name}` on `{table_name}`..."
    )

    frappe.db.sql(
        f"""
        ALTER TABLE `{table_name}`
        ADD INDEX `{index_name}` (party_stock_account, item_code, posting_datetime)
        """
    )

    frappe.logger().info(
        f"[PSV Index Patch] Index `{index_name}` created successfully."
    )

    # Also add a separate index on voucher_no to speed up the orphaned invoice
    # NOT EXISTS check in psv_service.run_psv_daily_health_check()
    voucher_index_name = "idx_psv_ledger_voucher_no"
    existing_voucher = frappe.db.sql(
        """
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        """,
        (table_name, voucher_index_name)
    )

    if not existing_voucher or existing_voucher[0][0] == 0:
        frappe.db.sql(
            f"""
            ALTER TABLE `{table_name}`
            ADD INDEX `{voucher_index_name}` (voucher_no)
            """
        )
        frappe.logger().info(
            f"[PSV Index Patch] Index `{voucher_index_name}` created successfully."
        )
