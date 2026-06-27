# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/migrate_cge_to_v2.py
# @description: SMRITI Migrate Cge To V2 — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/patches/migrate_cge_to_v2.py
# @description: Migration patch to transition CGE v1.0 data to CGE v2.0 architecture.
# @author: SMRITI Architect / USER & AITDL
# @date: 2026-06-19
#

import frappe
from frappe import _
from frappe.utils import flt, now_datetime

# DRY_RUN = True blocks database mutation and only performs dry-run validation, reporting counts and schemas.
DRY_RUN = False

REQUIRED_INDEXES = {
    "SMRITI Benefit Wallet": {
        "uq_wallet_cust_comp_inst": ["customer", "company", "benefit_instrument"]
    },
    "SMRITI Benefit Ledger": {
        "idx_ledger_cust_inst_date": ["customer", "benefit_instrument", "posting_date"],
        "idx_ledger_ref": ["reference_doctype", "reference_name"]
    }
}

def execute(dry_run=None):
    """
    SMRITI CGE v2 Migration Patch.
    1. Verify CGE v2 DocTypes exist in the system.
    2. Seed Benefit Instrument Types (LOYALTY, CASHBACK, etc.).
    3. Seed Benefit Instruments (Promo Cashback, Loyalty Points).
    4. Port SMRITI Wallet Ledger to Benefit Ledger.
    5. Calculate and compile Benefit Wallet states.
    6. Port Campaigns and Liability snapshots.
    """
    global DRY_RUN
    if dry_run is not None:
        DRY_RUN = dry_run
    print("==================================================")
    print("  SMRITI CGE v2 Migration Script  ")
    if DRY_RUN:
        print("  MODE: DRY RUN (NO DATABASE WRITES)  ")
    else:
        print("  MODE: LIVE MIGRATION  ")
    print("==================================================")

    # 1. Validation Checks
    required_doctypes = [
        "SMRITI Benefit Instrument Type",
        "SMRITI Benefit Instrument",
        "SMRITI Benefit Wallet",
        "SMRITI Benefit Ledger",
        "SMRITI Benefit Liability Snapshot",
        "SMRITI Campaign",
        "SMRITI Promotion Rule",
        "SMRITI Coupon Rule",
        "SMRITI Loyalty Program",
        "SMRITI Loyalty Rule",
        "SMRITI Membership Tier",
        "SMRITI Benefit Resolution Policy",
        "SMRITI Customer Benefit Profile",
        "SMRITI Benefit Audit Log"
    ]

    missing_dt = [dt for dt in required_doctypes if not frappe.db.exists("DocType", dt)]
    if missing_dt:
        print(f"ERROR: Missing DocType schemas: {missing_dt}")
        print("Ensure migrations have run or doctype JSONs are loaded first.")
        if not DRY_RUN:
            frappe.throw(_("Cannot run live migration. Missing target DocTypes: {0}").format(missing_dt))
            return

    # 1b. Check Database Indexes (Phase 4C Constraint Hardening)
    print("Validating Database Indexes...")
    for doctype, indexes in REQUIRED_INDEXES.items():
        if frappe.db.table_exists(doctype):
            table_name = f"tab{doctype}"
            for idx_name, cols in indexes.items():
                try:
                    idx_rows = frappe.db.sql(f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s", (idx_name,), as_dict=True)
                    if not idx_rows:
                        print(f" - [Warning] Missing database index: {idx_name} on `{table_name}` for columns {cols}")
                    else:
                        db_cols = [r.get("Column_name") or r.get("column_name") for r in idx_rows]
                        if set(db_cols) == set(cols):
                            print(f" - [Exists] Index: {idx_name} on `{table_name}` covering {cols}")
                        else:
                            print(f" - [Mismatch] Index {idx_name} exists but covers columns {db_cols} instead of {cols}")
                except Exception as e:
                    print(f" - [Error] Could not check index {idx_name} on `{table_name}`: {str(e)}")
        else:
            print(f" - [Pending] Table `tab{doctype}` does not exist yet (cannot verify index {list(indexes.keys())})")

    # 2. Seed Benefit Instrument Types
    instrument_types = ["LOYALTY", "CASHBACK", "STORE_CREDIT", "VOUCHER", "MEMBERSHIP"]
    print(f"Validating Benefit Instrument Types: {instrument_types}")
    for it in instrument_types:
        if not frappe.db.exists("SMRITI Benefit Instrument Type", it):
            print(f" - [Seed Pending] Instrument Type: {it}")
            if not DRY_RUN:
                doc = frappe.get_doc({
                    "doctype": "SMRITI Benefit Instrument Type",
                    "type_name": it,
                    "description": f"{it} Benefit Classification"
                })
                doc.insert(ignore_permissions=True)
                print(f" - [Seeded] Instrument Type: {it}")
        else:
            print(f" - [Exists] Instrument Type: {it}")

    # 3. Seed Benefit Instruments
    instruments = [
        {
            "instrument_name": "Promo Cashback",
            "instrument_type": "CASHBACK",
            "validity_days": 90,
            "allow_negative_balance": 0,
            "reversal_strategy": "Full Reversal"
        },
        {
            "instrument_name": "Loyalty Points",
            "instrument_type": "LOYALTY",
            "validity_days": 365,
            "allow_negative_balance": 0,
            "reversal_strategy": "Full Reversal"
        }
    ]

    print("Validating Benefit Instruments...")
    for inst in instruments:
        if not frappe.db.exists("SMRITI Benefit Instrument", inst["instrument_name"]):
            print(f" - [Seed Pending] Instrument: {inst['instrument_name']}")
            if not DRY_RUN:
                doc = frappe.get_doc({
                    "doctype": "SMRITI Benefit Instrument",
                    **inst
                })
                doc.insert(ignore_permissions=True)
                print(f" - [Seeded] Instrument: {inst['instrument_name']}")
        else:
            print(f" - [Exists] Instrument: {inst['instrument_name']}")

    # 4. Port tabSMRITI Wallet Ledger to tabSMRITI Benefit Ledger
    legacy_count = 0
    if frappe.db.exists("DocType", "SMRITI Wallet Ledger"):
        legacy_count = frappe.db.count("SMRITI Wallet Ledger")
    print(f"Legacy Wallet Ledger entries found: {legacy_count}")

    if legacy_count > 0:
        if DRY_RUN:
            print(f" - [Dry Run] Would port {legacy_count} wallet ledger entries into SMRITI Benefit Ledger.")
        else:
            print(f" - [Porting] Executing SQL to port {legacy_count} records...")
            # Run SQL to insert legacy records into the new Benefit Ledger table
            frappe.db.sql("""
                INSERT INTO `tabSMRITI Benefit Ledger` (
                    name, creation, modified, modified_by, owner, docstatus,
                    ledger_sequence, customer, company, benefit_instrument,
                    transaction_type, event_type, amount, balance_remaining,
                    reference_doctype, reference_name, posting_date, expiry_date,
                    is_reversal, journal_entry, remarks
                )
                SELECT 
                    name, creation, modified, modified_by, owner, docstatus,
                    ledger_sequence, customer, company, 'Promo Cashback',
                    transaction_type, 
                    CASE 
                        WHEN transaction_type = 'Credit' THEN 'EARN'
                        ELSE 'REDEEM'
                    END,
                    amount, balance_remaining,
                    CASE 
                        WHEN reference_invoice LIKE 'SINV-%' THEN 'Sales Invoice'
                        WHEN reference_invoice LIKE 'PINV-%' THEN 'POS Invoice'
                        ELSE NULL
                    END,
                    reference_invoice, creation, expiry_date,
                    is_reversal, journal_entry, remarks
                FROM `tabSMRITI Wallet Ledger`;
            """)
            print(" - [Success] Ported legacy wallet ledger records.")

    # 5. Establish Benefit Wallets
    if legacy_count > 0:
        # Fetch unique combinations of customer and company to compile wallets
        print("Calculating Benefit Wallet current-state cache balances...")
        wallets_summary = frappe.db.sql("""
            select customer, company, 
                   sum(case when transaction_type = 'Credit' then amount else 0 end) -
                   sum(case when transaction_type = 'Debit' then amount else 0 end) as balance
            from `tabSMRITI Wallet Ledger`
            group by customer, company
        """, as_dict=True)

        print(f"Calculated unique wallet records to construct: {len(wallets_summary)}")
        for w in wallets_summary:
            cust = w["customer"]
            comp = w["company"]
            bal = flt(w["balance"])
            
            if DRY_RUN:
                print(f" - [Dry Run] Wallet for Customer: {cust}, Company: {comp} -> Balance: ₹{bal}")
            else:
                existing_wallet = frappe.db.exists("SMRITI Benefit Wallet", {
                    "customer": cust,
                    "company": comp,
                    "benefit_instrument": "Promo Cashback"
                })
                if not existing_wallet:
                    wallet_doc = frappe.get_doc({
                        "doctype": "SMRITI Benefit Wallet",
                        "customer": cust,
                        "company": comp,
                        "benefit_instrument": "Promo Cashback",
                        "balance": bal,
                        "last_updated": now_datetime()
                    })
                    wallet_doc.insert(ignore_permissions=True)
                else:
                    frappe.db.set_value("SMRITI Benefit Wallet", existing_wallet, {
                        "balance": bal,
                        "last_updated": now_datetime()
                    })
        if not DRY_RUN:
            print(" - [Success] Compiled Benefit Wallets.")

    # 6. Port Campaigns
    campaign_count = 0
    if frappe.db.exists("DocType", "SMRITI Coupon Campaign"):
        campaign_count = frappe.db.count("SMRITI Coupon Campaign")
    print(f"Legacy SMRITI Coupon Campaigns found: {campaign_count}")

    if campaign_count > 0:
        if DRY_RUN:
            print(f" - [Dry Run] Would port {campaign_count} SMRITI Coupon Campaigns to SMRITI Campaign.")
        else:
            frappe.db.sql("""
                INSERT INTO `tabSMRITI Campaign` (
                    name, creation, modified, modified_by, owner, docstatus,
                    campaign_name, company, status, start_date, end_date,
                    budget_limit, budget_reserved, budget_consumed, stop_on_limit
                )
                SELECT 
                    name, creation, modified, modified_by, owner, docstatus,
                    campaign_name, (select name from `tabCompany` limit 1),
                    CASE 
                        WHEN status = 'Active' THEN 'Active'
                        WHEN status = 'Completed' THEN 'Expired'
                        ELSE 'Draft'
                    END,
                    start_date, end_date,
                    budget_limit, budget_reserved, budget_consumed, stop_on_limit
                FROM `tabSMRITI Coupon Campaign`;
            """)
            print(" - [Success] Ported campaigns.")

    # 7. Commit
    if not DRY_RUN:
        frappe.db.commit()
        print("✅ Migration patch executed successfully!")
    else:
        print("✅ Dry-run validation checks complete. No database mutations occurred.")
