# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/ledger_engine.py
# @description: Immutable Ledger Engine for SMRITI Party Stock Visibility.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import hashlib
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

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
    if smriti.db.exists("SMRITI Party Stock Ledger Entry", {"unique_hash": unique_hash}):
        return None
        
    ple = smriti.documents.new("PartyStockLedgerEntry")
    ple.update({
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
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: Financial/Data-integrity-adjacent exception in ledger_engine.py:68: {sys.exc_info()[1]}")

    return ple


def log_activity(action_type, party_stock_account=None, reference_doctype=None, reference_name=None, details=None, event_type=None):
    """
    Creates an entry in the SMRITI PSV Activity Log.
    """
    from smriti_retail_os.utils import get_client_ip
    ip_addr = get_client_ip()

    log = smriti.documents.new("PSVActivityLog")
    log.update({
        "timestamp": frappe.utils.now_datetime(),
        "user": frappe.session.user or "Administrator",
        "action_type": action_type,
        "event_type": event_type,
        "party_stock_account": party_stock_account,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "ip_address": ip_addr,
        "details": details
    })
    log.flags.ignore_permissions = True
    log.insert()
