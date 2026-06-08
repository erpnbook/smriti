# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/balance_engine.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe

def get_party_balance(party_stock_account, item_code, posting_datetime=None):
    """
    Returns the current available shadow balance for a given SKU at a location.
    If posting_datetime is provided, it returns the historical balance at that point in time.
    """
    query = """
        SELECT SUM(qty) 
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE party_stock_account = %s AND item_code = %s
    """
    params = [party_stock_account, item_code]

    if posting_datetime:
        query += " AND posting_datetime <= %s"
        params.append(posting_datetime)

    result = frappe.db.sql(query, params)
    return float(result[0][0]) if result and result[0][0] is not None else 0.0

def get_bulk_party_balances(party_stock_account, item_codes=None):
    """
    Returns a dictionary of SKU: Balance for a location in a single SQL round-trip.
    """
    query = """
        SELECT item_code, SUM(qty)
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE party_stock_account = %s
    """
    params = [party_stock_account]

    if item_codes:
        query += " AND item_code IN %s"
        params.append(tuple(item_codes))

    query += " GROUP BY item_code"
    
    result = frappe.db.sql(query, params, as_dict=False)
    return {r[0]: float(r[1]) for r in result}
