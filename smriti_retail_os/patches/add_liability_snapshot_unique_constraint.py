# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/add_liability_snapshot_unique_constraint.py
# @description: SMRITI Add Liability Snapshot Unique Constraint — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/patches/add_liability_snapshot_unique_constraint.py
# @description: Adds unique index on SMRITI Liability Snapshot for (company, snapshot_date)
# @author: Antigravity AI
# @date: 2026-06-19
#

import frappe

def execute():
    table_name = "tabSMRITI Liability Snapshot"

    # Guard: table must exist
    if not frappe.db.table_exists(table_name):
        return

    # Delete duplicates keeping the newest / highest name record to ensure index creation succeeds
    frappe.db.sql(f"""
        DELETE t1 FROM `{table_name}` t1
        INNER JOIN `{table_name}` t2 
        ON COALESCE(t1.company, '') = COALESCE(t2.company, '')
        AND t1.snapshot_date = t2.snapshot_date
        AND t1.name < t2.name
    """)

    index_name = "unique_company_snapshot_date"

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
            ADD UNIQUE INDEX `{index_name}` (company, snapshot_date)
            """
        )
        frappe.logger().info(
            f"[CGE Patch] Unique index `{index_name}` created successfully on `{table_name}`."
        )
