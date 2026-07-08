"""
add_tds_and_threshold_fields.py
---------------------------------
SMRITI Retail OS — v2.3.1 Migration Patch
Adds two fields that are now present in doctype JSON but need the DB column:

  1. SMRITI Supplier  →  tds_category  (Link → Tax Withholding Category)
  2. SMRITI Purchase Settings  →  approval_threshold_inclusive_of_tax  (Check)

Both operations are idempotent — columns that already exist are skipped.

Copyright (c) 2026 AITDL NETWORK. All rights reserved.
"""

import frappe
from frappe.utils import cint


def execute():
    # ── 1. SMRITI Supplier — tds_category ────────────────────────────────────
    _ensure_column(
        doctype="SMRITI Supplier",
        fieldname="tds_category",
        col_type="varchar(140)",
        default_val=None,
        description="tds_category (Link → Tax Withholding Category)",
    )

    # ── 2. SMRITI Purchase Settings — approval_threshold_inclusive_of_tax ────
    _ensure_column(
        doctype="SMRITI Purchase Settings",
        fieldname="approval_threshold_inclusive_of_tax",
        col_type="int(1)",
        default_val="0",
        description="approval_threshold_inclusive_of_tax (Check, default 0 = pre-GST basis)",
    )

    frappe.db.commit()
    frappe.logger().info("v2.3.1 patch: tds_category + approval_threshold_inclusive_of_tax columns ensured.")


def _ensure_column(doctype, fieldname, col_type, default_val, description):
    """
    Adds `fieldname` column to the DocType's physical table if not already present.
    Uses frappe.db.add_column so it works across MySQL and MariaDB.
    """
    table = f"tab{doctype}"
    existing = frappe.db.sql(
        f"SHOW COLUMNS FROM `{table}` LIKE %s", (fieldname,)
    )
    if existing:
        frappe.logger().info(
            f"v2.3.1 patch: column `{table}`.`{fieldname}` already exists — skipped."
        )
        return

    if default_val is not None:
        frappe.db.sql(
            f"ALTER TABLE `{table}` ADD COLUMN `{fieldname}` {col_type} DEFAULT %s",
            (default_val,),
        )
    else:
        frappe.db.sql(
            f"ALTER TABLE `{table}` ADD COLUMN `{fieldname}` {col_type} DEFAULT NULL"
        )

    frappe.logger().info(
        f"v2.3.1 patch: column `{table}`.`{fieldname}` ({description}) created."
    )
