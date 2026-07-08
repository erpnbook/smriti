# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/v1_2_3/purge_stale_mop_and_gst_rows.py
# @description: One-time patch to delete orphan child-table rows in
#               tabMode of Payment Account and tabGST Account that reference
#               companies which no longer exist in tabCompany.
#
#               Root cause of BUG-001:
#               When a Company is deleted (via ERPNext desk or frappe.delete_doc),
#               ERPNext does NOT cascade-delete its rows from:
#                 - tabMode of Payment Account  (company Link field)
#                 - tabGST Account              (company Link field, india_compliance)
#               On the next Company creation, ERPNext's set_mode_of_payment_account()
#               calls mode_of_payment.save(), which triggers Frappe's _validate_links()
#               across ALL rows — including the stale orphan rows — raising:
#                 "Could not find Row #N: Company: <deleted-company-name>"
#
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-05
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti


def execute():
    """
    Removes orphan rows from Mode of Payment Account and GST Account child
    tables where the referenced Company no longer exists.
    Safe to run multiple times (idempotent).
    """
    mop_deleted = _purge_table(
        table="tabMode of Payment Account",
        company_col="company",
        label="Mode of Payment Account"
    )

    gst_deleted = _purge_table(
        table="tabGST Account",
        company_col="company",
        label="GST Account"
    )

    if mop_deleted or gst_deleted:
        smriti.db.commit()
        frappe.logger().info(
            f"[SMRITI patch v1.2.3] Purged stale child rows — "
            f"MoP: {mop_deleted}, GST: {gst_deleted}"
        )
    else:
        frappe.logger().info(
            "[SMRITI patch v1.2.3] No stale child rows found — DB already clean."
        )


def _purge_table(table, company_col, label):
    """
    Deletes rows from `table` where `company_col` does not match any
    existing Company name. Returns the count of deleted rows.
    """
    stale = smriti.db.sql(
        f"""
        SELECT t.name
        FROM `{table}` t
        LEFT JOIN `tabCompany` c ON c.name = t.`{company_col}`
        WHERE c.name IS NULL
          AND t.`{company_col}` IS NOT NULL
          AND t.`{company_col}` != ''
        """,
        as_dict=True
    )

    if not stale:
        return 0

    names = tuple(r.name for r in stale)
    companies = list({smriti.db.sql(
        f"SELECT `{company_col}` FROM `{table}` WHERE name = %s", r.name
    )[0][0] for r in stale})

    frappe.logger().warning(
        f"[SMRITI patch v1.2.3] Deleting {len(stale)} stale {label} row(s) "
        f"for non-existent company/companies: {companies}"
    )

    if len(names) == 1:
        smriti.db.sql(f"DELETE FROM `{table}` WHERE name = %s", names[0])
    else:
        smriti.db.sql(f"DELETE FROM `{table}` WHERE name IN {names}")

    return len(stale)
