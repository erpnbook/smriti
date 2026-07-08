# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/utils/opening_balance.py
# @description: Utility for parsing opening balance Excel files.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

@frappe.whitelist()
def parse_opening_excel(file_url: str) -> dict:
    """
    Parse opening balance Excel. 
    Expected Columns: Item Variant Code | Opening Qty
    """
    try:
        import openpyxl
    except ImportError:
        frappe.throw(_("Python library 'openpyxl' is required to parse Excel files."))

    file_doc = smriti.documents.get("File", {"file_url": file_url})
    file_path = file_doc.get_full_path()
    
    if not file_path.endswith(('.xlsx', '.xls')):
        frappe.throw(_("Please upload a valid Excel file (.xlsx or .xls)"))

    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb.active
    raw = list(ws.iter_rows(values_only=True))
    
    if not raw:
        return {"rows": [], "errors": ["Empty file"]}

    rows = []
    errors = []
    
    # Skip header
    for i, row in enumerate(raw[1:], start=2):
        if not row or len(row) < 2 or not row[0]:
            continue
            
        item_code = str(row[0]).strip()
        try:
            qty = float(row[1] or 0)
        except Exception:
            errors.append(f"Row {i}: Invalid qty for '{item_code}'")
            continue
            
        if qty <= 0:
            continue
            
        if not smriti.db.exists("Item", item_code):
            errors.append(f"Row {i}: Item Variant '{item_code}' not found in system")
            continue
            
        rows.append({"item_code": item_code, "qty": qty})

    return {"rows": rows, "errors": errors}
