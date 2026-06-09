# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/report/psv_party_stock_balance/psv_party_stock_balance.py
# @description: Report showing current balances across all party stock accounts.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#

import frappe
from smriti_retail_os.balance_engine import get_all_party_balances

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party Account",  "fieldname": "party_stock_account", "fieldtype": "Link",     "options": "SMRITI Party Stock Account", "width": 180},
        {"label": "Location",       "fieldname": "location_name",       "fieldtype": "Data",     "width": 130},
        {"label": "Zone",           "fieldname": "zone",                "fieldtype": "Data",     "width": 80},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",     "options": "Item", "width": 200},
        {"label": "Balance Qty",    "fieldname": "balance",             "fieldtype": "Float",    "width": 100},
        {"label": "MRP",            "fieldname": "mrp",                 "fieldtype": "Currency", "width": 90},
        {"label": "Balance Value",  "fieldname": "balance_value",       "fieldtype": "Currency", "width": 120},
    ]

    all_balances = get_all_party_balances(company)

    # Convert filter conditions into lambdas
    conditions = []
    if filters.get("party_stock_account"):
        conditions.append(lambda r: r.party_stock_account == filters["party_stock_account"])
    if filters.get("zone"):
        conditions.append(lambda r: r.zone == filters["zone"])
    if not filters.get("show_zero"):
        conditions.append(lambda r: r.balance != 0)

    data = []
    for r in all_balances:
        # Check all conditions
        match = True
        for c in conditions:
            if not c(r):
                match = False
                break
        
        if match:
            mrp = frappe.db.get_value("Item", r.item_code, "standard_rate") or 0
            data.append({
                "party_stock_account": r.party_stock_account,
                "location_name":       r.location_name,
                "zone":                r.zone,
                "item_code":           r.item_code,
                "balance":             r.balance,
                "mrp":                 mrp,
                "balance_value":       r.balance * mrp,
            })

    data.sort(key=lambda x: (x["party_stock_account"], x["item_code"]))
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link",   "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link",   "options": "SMRITI Party Stock Account"},
        {"fieldname": "zone",                "label": "Zone",          "fieldtype": "Select", "options": "\nNorth\nSouth\nEast\nWest\nCentral"},
        {"fieldname": "show_zero",           "label": "Show Zero",     "fieldtype": "Check"},
    ]
