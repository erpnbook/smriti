"""
add_tds_and_threshold_fields.py
---------------------------------
SMRITI Retail OS — v2.3.1 Migration Patch
Adds one physical DB column:

  1. SMRITI Supplier  →  tds_category  (Link → Tax Withholding Category)

NOTE: approval_threshold_inclusive_of_tax on SMRITI Purchase Settings is a
Single DocType field — Frappe writes Single doctype fields to `tabSingles`,
NOT to a per-doctype table. Frappe's meta-sync during `bench migrate` handles
it automatically from the JSON definition. No ALTER TABLE needed.

Copyright (c) 2026 AITDL NETWORK. All rights reserved.
"""

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti


def execute():
    # ── SMRITI Supplier — tds_category ───────────────────────────────────────
    # Regular (non-Single) DocType → physical table tabSMRITI Supplier
    table = "tabSMRITI Supplier"

    # Guard: table must exist (will be created by meta-sync if brand new install)
    tables = [r[0] for r in smriti.db.sql("SHOW TABLES LIKE %s", (table,))]
    if not tables:
        frappe.logger().info(
            f"v2.3.1 patch: {table} does not exist yet — skipping tds_category column add. "
            "Will be created when Frappe creates the table."
        )
        return

    existing = smriti.db.sql(
        f"SHOW COLUMNS FROM `{table}` LIKE %s", ("tds_category",)
    )
    if existing:
        frappe.logger().info(
            f"v2.3.1 patch: `{table}`.`tds_category` already exists — skipped."
        )
    else:
        smriti.db.sql(
            f"ALTER TABLE `{table}` ADD COLUMN `tds_category` varchar(140) DEFAULT NULL"
        )
        frappe.logger().info(
            f"v2.3.1 patch: `{table}`.`tds_category` (Link → Tax Withholding Category) created."
        )

    # ── SMRITI Purchase Settings — approval_threshold_inclusive_of_tax ───────
    # This is a Single DocType → stored in tabSingles, NOT a per-doctype table.
    # Frappe meta-sync during bench migrate automatically handles Single fields.
    # Nothing to do here.
    frappe.logger().info(
        "v2.3.1 patch: approval_threshold_inclusive_of_tax skipped "
        "(Single DocType — handled by Frappe meta-sync)."
    )

    smriti.db.commit()
    frappe.logger().info("v2.3.1 patch: complete.")
