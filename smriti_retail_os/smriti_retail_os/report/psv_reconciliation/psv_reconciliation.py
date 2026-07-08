# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/report/psv_reconciliation/psv_reconciliation.py
# @description: Report showing variance between system and physical stock audits.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.balance_engine import get_all_party_balances

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",          "fieldname": "party_stock_account", "fieldtype": "Link",     "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",     "options": "Item", "width": 200},
        {"label": "System Balance", "fieldname": "system_balance",      "fieldtype": "Float",    "width": 120},
        {"label": "Physical Count", "fieldname": "physical_qty",        "fieldtype": "Float",    "width": 120},
        {"label": "Variance",       "fieldname": "variance",            "fieldtype": "Float",    "width": 100},
        {"label": "Audit Date",     "fieldname": "audit_date",          "fieldtype": "Date",     "width": 110},
        {"label": "Status",         "fieldname": "status",              "fieldtype": "Data",     "width": 100},
    ]

    all_balances_raw = get_all_party_balances(company)
    all_balances = {
        (r["party_stock_account"], r["item_code"]): r["balance"]
        for r in all_balances_raw
    }

    where = "WHERE s.status = 'Approved'"
    values = {}
    if filters.get("party_stock_account"):
        where += " AND s.party_stock_account = %(psa)s"
        values["psa"] = filters["party_stock_account"]
    if filters.get("from_date"):
        where += " AND s.audit_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        where += " AND s.audit_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    physical = smriti.db.sql(f"""
        SELECT s.party_stock_account, i.item_code,
               i.physical_qty, s.audit_date, s.status
        FROM `tabSMRITI Party Physical Snapshot` s
        JOIN `tabSMRITI Party Physical Item` i ON i.parent = s.name
        {where}
        ORDER BY s.party_stock_account, i.item_code
    """, values=values, as_dict=True)

    data = []
    for row in physical:
        key = (row.party_stock_account, row.item_code)
        sys_bal = all_balances.get(key, 0)
        data.append({
            "party_stock_account": row.party_stock_account,
            "item_code":           row.item_code,
            "system_balance":      sys_bal,
            "physical_qty":        row.physical_qty,
            "variance":            row.physical_qty - sys_bal,
            "audit_date":          row.audit_date,
            "status":              row.status,
        })
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link", "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link", "options": "SMRITI Party Stock Account"},
        {"fieldname": "from_date",           "label": "Audit From",    "fieldtype": "Date"},
        {"fieldname": "to_date",             "label": "Audit To",      "fieldtype": "Date"},
    ]
