# -*- coding: utf-8 -*-
# SMRITI Open Purchase Orders Script Report
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "po_number", "label": _("PO Number"), "fieldtype": "Link", "options": "SMRITI Purchase Order", "width": 160},
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "SMRITI Supplier", "width": 140},
        {"fieldname": "supplier_name", "label": _("Supplier Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "transaction_date", "label": _("Transaction Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "schedule_date", "label": _("Schedule Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "total_qty", "label": _("Total Qty"), "fieldtype": "Float", "width": 100},
        {"fieldname": "grand_total", "label": _("Grand Total"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "per_received", "label": _("Received %"), "fieldtype": "Float", "width": 110},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    if not filters:
        filters = {}
    
    conds = {"docstatus": 1, "status": ["in", ["Submitted", "Approved", "Ordered", "Partially Received"]]}
    if filters.get("company"):
        conds["company"] = filters.get("company")
    if filters.get("supplier"):
        conds["supplier"] = filters.get("supplier")
    if filters.get("from_date"):
        conds["transaction_date"] = [">=", filters.get("from_date")]
    if filters.get("to_date"):
        conds.setdefault("transaction_date", ["<=", filters.get("to_date")])

    return smriti.db.get_list(
        "SMRITI Purchase Order",
        filters=conds,
        fields=["name as po_number", "supplier", "supplier_name", "transaction_date", "schedule_date", "total_qty", "grand_total", "per_received", "status"],
        order_by="transaction_date desc"
    )
