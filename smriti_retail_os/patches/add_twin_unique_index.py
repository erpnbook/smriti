# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/add_twin_unique_index.py
# @description: SMRITI Add Twin Unique Index — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/patches/add_twin_unique_index.py
# @description: Adds unique index on SMRITI SKU Twin for (company, party_stock_account, item_code)
# @author: Antigravity AI
# @date: 2026-06-19
#

import frappe

def execute():
    table_name = "tabSMRITI SKU Twin"

    # Guard: table must exist
    if not frappe.db.table_exists(table_name):
        return

    # Delete duplicates keeping the newest / highest name record to ensure index creation succeeds
    frappe.db.sql(f"""
        DELETE t1 FROM `{table_name}` t1
        INNER JOIN `{table_name}` t2 
        ON COALESCE(t1.company, '') = COALESCE(t2.company, '')
        AND COALESCE(t1.party_stock_account, '') = COALESCE(t2.party_stock_account, '')
        AND COALESCE(t1.item_code, '') = COALESCE(t2.item_code, '')
        AND t1.name < t2.name
    """)

    index_name = "unique_company_psa_item"

    # Check if the unique index already exists
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

    if not existing or existing[0][0] == 0:
        frappe.db.sql(
            f"""
            ALTER TABLE `{table_name}`
            ADD UNIQUE INDEX `{index_name}` (company, party_stock_account, item_code)
            """
        )
        frappe.logger().info(
            f"[PDT Patch] Unique index `{index_name}` created successfully on `{table_name}`."
        )
