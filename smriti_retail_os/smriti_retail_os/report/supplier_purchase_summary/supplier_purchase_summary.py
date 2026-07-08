# -*- coding: utf-8 -*-
# SMRITI Supplier Purchase Summary Script Report
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "SMRITI Supplier", "width": 140},
        {"fieldname": "supplier_name", "label": _("Supplier Name"), "fieldtype": "Data", "width": 200},
        {"fieldname": "po_count", "label": _("PO Count"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_po_amount", "label": _("Total PO Amount"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_ordered_qty", "label": _("Total Ordered Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "total_received_qty", "label": _("Total Received Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "fill_rate", "label": _("Fill Rate %"), "fieldtype": "Float", "width": 110},
        {"fieldname": "avg_po_value", "label": _("Avg PO Value"), "fieldtype": "Currency", "width": 130}
    ]

def get_data(filters):
    if not filters:
        filters = {}

    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    
    # Query aggregated PO data per supplier
    query = """
        SELECT 
            supplier,
            supplier_name,
            COUNT(name) as po_count,
            SUM(grand_total) as total_po_amount,
            SUM(total_qty) as total_ordered_qty,
            AVG(grand_total) as avg_po_value
        FROM `tabSMRITI Purchase Order`
        WHERE docstatus = 1 AND company = %s
    """
    params = [company]

    if filters.get("from_date"):
        query += " AND transaction_date >= %s"
        params.append(filters.get("from_date"))
    if filters.get("to_date"):
        query += " AND transaction_date <= %s"
        params.append(filters.get("to_date"))

    query += " GROUP BY supplier"
    
    rows = smriti.db.sql(query, tuple(params), as_dict=True)

    # Fetch child received quantities and calculate fill rate
    for row in rows:
        received_res = smriti.db.sql("""
            SELECT SUM(poi.received_qty) 
            FROM `tabSMRITI Purchase Order Item` poi 
            INNER JOIN `tabSMRITI Purchase Order` po ON poi.parent = po.name
            WHERE po.supplier = %s AND po.docstatus = 1 AND po.company = %s
        """, (row["supplier"], company))
        row["total_received_qty"] = flt(received_res[0][0]) if received_res and received_res[0][0] else 0.0
        
        ord_qty = flt(row["total_ordered_qty"])
        if ord_qty > 0:
            row["fill_rate"] = flt(row["total_received_qty"] / ord_qty) * 100.0
        else:
            row["fill_rate"] = 0.0

    return rows
