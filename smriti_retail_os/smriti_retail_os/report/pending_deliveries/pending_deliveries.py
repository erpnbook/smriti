# -*- coding: utf-8 -*-
# SMRITI Pending Deliveries Script Report
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "po_number", "label": _("PO Number"), "fieldtype": "Link", "options": "SMRITI Purchase Order", "width": 160},
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "SMRITI Supplier", "width": 140},
        {"fieldname": "item_code", "label": _("Item Code"), "fieldtype": "Link", "options": "Item", "width": 150},
        {"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "ordered_qty", "label": _("Ordered Qty"), "fieldtype": "Float", "width": 110},
        {"fieldname": "received_qty", "label": _("Received Qty"), "fieldtype": "Float", "width": 110},
        {"fieldname": "pending_qty", "label": _("Pending Qty"), "fieldtype": "Float", "width": 110},
        {"fieldname": "uom", "label": _("UOM"), "fieldtype": "Link", "options": "UOM", "width": 80},
        {"fieldname": "warehouse", "label": _("Warehouse"), "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"fieldname": "schedule_date", "label": _("Schedule Date"), "fieldtype": "Date", "width": 120}
    ]

def get_data(filters):
    if not filters:
        filters = {}

    company = filters.get("company") or frappe.defaults.get_user_default("Company")
    
    query = """
        SELECT 
            poi.parent AS po_number,
            po.supplier,
            poi.item_code,
            poi.item_name,
            poi.qty AS ordered_qty,
            poi.received_qty,
            (poi.qty - poi.received_qty) AS pending_qty,
            poi.uom,
            poi.warehouse,
            po.schedule_date
        FROM `tabSMRITI Purchase Order Item` poi
        INNER JOIN `tabSMRITI Purchase Order` po ON poi.parent = po.name
        WHERE po.docstatus = 1 AND po.company = %s AND (poi.qty - poi.received_qty) > 0 AND po.status NOT IN ('Closed', 'Cancelled')
    """
    params = [company]

    if filters.get("supplier"):
        query += " AND po.supplier = %s"
        params.append(filters.get("supplier"))
    if filters.get("item_code"):
        query += " AND poi.item_code = %s"
        params.append(filters.get("item_code"))

    query += " ORDER BY po.schedule_date ASC"
    
    return frappe.db.sql(query, tuple(params), as_dict=True)
