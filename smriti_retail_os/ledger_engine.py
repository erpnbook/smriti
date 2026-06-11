# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/ledger_engine.py
# @description: Immutable Ledger Engine for SMRITI Party Stock Visibility.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import hashlib
import frappe
from frappe import _

def generate_ledger_hash(company, voucher_type, voucher_no, item_code, party_stock_account):
    """
    Generates a unique, collision-resistant SHA-256 hash scoped by company.
    """
    raw_str = f"{company}||{voucher_type}||{voucher_no}||{item_code}||{party_stock_account}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

def make_ledger_entry(company, posting_datetime, party_stock_account, item_code, qty, 
                      voucher_type, voucher_no, adjustment_type=None, reason=None, 
                      approved_by=None, approved_on=None):
    """
    Builds and inserts an immutable ledger entry. Crucially, it does NOT commit.
    Let the calling process (e.g. Sales Invoice Submit) handle transaction boundaries.
    """
    if not qty:
        return None

    unique_hash = generate_ledger_hash(company, voucher_type, voucher_no, item_code, party_stock_account)
    
    # Block double-writes defensively before trying database insertion
    if frappe.db.exists("SMRITI Party Stock Ledger Entry", {"unique_hash": unique_hash}):
        return None
        
    ple = frappe.get_doc({
        "doctype": "SMRITI Party Stock Ledger Entry",
        "company": company,
        "posting_datetime": posting_datetime or frappe.utils.now_datetime(),
        "party_stock_account": party_stock_account,
        "item_code": item_code,
        "qty": float(qty),
        "voucher_type": voucher_type, # Dispatch, Sales, Adjustment, Return, Opening
        "voucher_no": voucher_no,
        "unique_hash": unique_hash,
        "adjustment_type": adjustment_type,
        "reason": reason,
        "approved_by": approved_by,
        "approved_on": approved_on
    })
    
    ple.flags.ignore_permissions = True
    try:
        ple.insert()
    except frappe.DuplicateEntryError:
        # Layer 3 idempotency: DB UNIQUE constraint caught a race condition.
        # Another concurrent request already inserted this entry — treat as success.
        return None

    # PERF-001: Invalidate the Redis balance cache for this (PSA, item) pair.
    # Imported lazily to avoid circular dependency (balance_engine → ledger_engine).
    try:
        from smriti_retail_os.balance_engine import invalidate_balance_cache
        invalidate_balance_cache(party_stock_account, item_code)
    except Exception:
        pass  # Cache invalidation failure must never break a ledger write

    return ple


def log_activity(action_type, party_stock_account=None, reference_doctype=None, reference_name=None, details=None):
    """
    Creates an entry in the SMRITI PSV Activity Log.
    """
    ip_addr = "127.0.0.1"
    try:
        if frappe.local and frappe.local.request_ip:
            ip_addr = frappe.local.request_ip
    except Exception:
        pass

    log = frappe.get_doc({
        "doctype": "SMRITI PSV Activity Log",
        "timestamp": frappe.utils.now_datetime(),
        "user": frappe.session.user or "Administrator",
        "action_type": action_type,
        "party_stock_account": party_stock_account,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "ip_address": ip_addr,
        "details": details
    })
    log.flags.ignore_permissions = True
    log.insert()
