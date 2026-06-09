# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/report/psv_sell_through/psv_sell_through.py
# @description: Report showing sell-through percentages per location/item.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#

import frappe

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",          "fieldname": "party_stock_account", "fieldtype": "Link",    "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",    "options": "Item", "width": 200},
        {"label": "Dispatched",     "fieldname": "dispatched",          "fieldtype": "Float",   "width": 100},
        {"label": "Sold",           "fieldname": "sold",                "fieldtype": "Float",   "width": 100},
        {"label": "Balance",        "fieldname": "balance",             "fieldtype": "Float",   "width": 100},
        {"label": "Sell-Through %", "fieldname": "sell_through_pct",    "fieldtype": "Percent", "width": 120},
    ]

    rows = frappe.db.sql("""
        SELECT 
            party_stock_account,
            item_code,
            SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END)  AS dispatched,
            SUM(CASE WHEN qty < 0 THEN ABS(qty) ELSE 0 END) AS sold,
            SUM(qty) AS balance
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s
        GROUP BY party_stock_account, item_code
        HAVING dispatched > 0
        ORDER BY party_stock_account, item_code
    """, [company], as_dict=True)

    if filters.get("party_stock_account"):
        rows = [r for r in rows if r.party_stock_account == filters["party_stock_account"]]
    
    data = []
    min_sell_through = float(filters.get("min_sell_through") or 0)

    for r in rows:
        pct = round((r.sold / r.dispatched) * 100, 2) if r.dispatched else 0
        if pct >= min_sell_through:
            data.append({
                "party_stock_account": r.party_stock_account,
                "item_code":           r.item_code,
                "dispatched":          r.dispatched,
                "sold":                r.sold,
                "balance":             r.balance,
                "sell_through_pct":    pct,
            })

    data.sort(key=lambda x: x["sell_through_pct"], reverse=True)
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",         "fieldtype": "Link",  "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account",   "fieldtype": "Link",  "options": "SMRITI Party Stock Account"},
        {"fieldname": "min_sell_through",    "label": "Min Sell-Through %", "fieldtype": "Float"},
    ]
