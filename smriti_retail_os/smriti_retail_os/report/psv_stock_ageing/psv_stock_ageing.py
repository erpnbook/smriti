# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/report/psv_stock_ageing/psv_stock_ageing.py
# @description: Report showing ageing of dispatched stock at distributor locations.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import date_diff, today

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",      "fieldname": "party_stock_account", "fieldtype": "Link",  "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item",       "fieldname": "item_code",           "fieldtype": "Link",  "options": "Item", "width": 200},
        {"label": "0-30 Days",  "fieldname": "d0_30",               "fieldtype": "Float", "width": 90},
        {"label": "31-60 Days", "fieldname": "d31_60",              "fieldtype": "Float", "width": 90},
        {"label": "61-90 Days", "fieldname": "d61_90",              "fieldtype": "Float", "width": 90},
        {"label": "90+ Days",   "fieldname": "d90_plus",            "fieldtype": "Float", "width": 90},
        {"label": "Total",      "fieldname": "total",               "fieldtype": "Float", "width": 90},
    ]

    dispatches = smriti.db.sql("""
        SELECT party_stock_account, item_code, qty, posting_datetime
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s AND voucher_type = 'Dispatch'
        ORDER BY posting_datetime
    """, [company], as_dict=True)

    today_str = today()
    buckets = {}
    for row in dispatches:
        key = (row.party_stock_account, row.item_code)
        age = date_diff(today_str, row.posting_datetime)
        b = buckets.setdefault(key, {"d0_30": 0, "d31_60": 0, "d61_90": 0, "d90_plus": 0})
        if age <= 30:   b["d0_30"]    += row.qty
        elif age <= 60: b["d31_60"]   += row.qty
        elif age <= 90: b["d61_90"]   += row.qty
        else:           b["d90_plus"] += row.qty

    data = []
    # Filter by party if provided
    psa_filter = filters.get("party_stock_account")

    for (psa, item), b in sorted(buckets.items()):
        if psa_filter and psa != psa_filter:
            continue

        total = sum(b.values())
        if total <= 0:
            continue
        data.append({
            "party_stock_account": psa,
            "item_code":           item,
            **b,
            "total":               total,
        })
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link", "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link", "options": "SMRITI Party Stock Account"},
    ]
