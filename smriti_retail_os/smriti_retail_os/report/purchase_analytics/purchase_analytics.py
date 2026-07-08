# -*- coding: utf-8 -*-
# SMRITI Purchase Analytics Script Report
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_spend", "label": _("Total Spend"), "fieldtype": "Currency", "width": 160},
        {"fieldname": "po_count", "label": _("PO Count"), "fieldtype": "Int", "width": 110},
        {"fieldname": "avg_po_value", "label": _("Avg PO Value"), "fieldtype": "Currency", "width": 140}
    ]

def get_data(filters):
    if not filters:
        filters = {}

    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    
    query = """
        SELECT 
            DATE_FORMAT(transaction_date, '%%Y-%%m') as month,
            SUM(grand_total) as total_spend,
            COUNT(name) as po_count,
            AVG(grand_total) as avg_po_value
        FROM `tabSMRITI Purchase Order`
        WHERE docstatus = 1 AND status != 'Cancelled' AND company = %s
    """
    params = [company]

    if filters.get("from_date"):
        query += " AND transaction_date >= %s"
        params.append(filters.get("from_date"))
    if filters.get("to_date"):
        query += " AND transaction_date <= %s"
        params.append(filters.get("to_date"))

    query += " GROUP BY month ORDER BY month ASC"
    
    return smriti.db.sql(query, tuple(params), as_dict=True)
