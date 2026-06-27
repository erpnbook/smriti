# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/supplier_returns_api.py
# @description: SMRITI Supplier Returns Api — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/api/supplier_returns_api.py
# @description: Whitelisted API endpoints for SMRITI Supplier Returns module.
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, nowdate
from frappe import _

@frappe.whitelist()
def get_submitted_receipts(query=None):
    """
    Fetches submitted and non-return Purchase Receipts.
    """
    filters = {
        "docstatus": 1,
        "is_return": 0
    }
    or_filters = None
    if query:
        or_filters = {
            "name": ["like", f"%{query}%"],
            "supplier_name": ["like", f"%{query}%"]
        }

    receipts = frappe.db.get_all(
        "Purchase Receipt",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "posting_time", "grand_total"],
        order_by="posting_date desc, posting_time desc",
        limit=50
    )
    return receipts

@frappe.whitelist()
def get_receipt_details(receipt_name):
    """
    Fetches details of a specific Purchase Receipt for return processing.
    """
    if not frappe.db.exists("Purchase Receipt", receipt_name):
        return None

    pr = frappe.get_doc("Purchase Receipt", receipt_name)
    items = []
    
    for item in pr.items:
        # Calculate maximum possible return quantity
        # Purchase Receipt Item has returned_qty tracking returns
        returned = flt(item.returned_qty)
        max_return = flt(item.qty) - returned
        
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "brand": item.brand,
            "qty": item.qty,
            "returned_qty": returned,
            "max_return": max_return if max_return > 0 else 0.0,
            "rate": item.rate,
            "stock_uom": item.stock_uom,
            "warehouse": item.warehouse,
            "receipt_item_name": item.name
        })

    return {
        "name": pr.name,
        "supplier": pr.supplier,
        "supplier_name": pr.supplier_name,
        "company": pr.company,
        "items": items
    }

@frappe.whitelist()
def submit_supplier_return(receipt_name, return_items, remarks=None, manager_pin=None):
    """
    Creates and submits a Purchase Return against the original Purchase Receipt.
    Only allows users with Manager permissions (or valid manager_pin override).
    """
    if manager_pin:
        from smriti_retail_os.billing_api import validate_manager_override
        res = validate_manager_override(manager_pin, f"Submit Supplier Return against {receipt_name}")
        if not res.get("authorized"):
            frappe.throw(_("Manager authorization failed: Invalid PIN."))
    else:
        from smriti_retail_os.purchase_api import check_store_manager_role
        check_store_manager_role()

    if not frappe.db.exists("Purchase Receipt", receipt_name):
        frappe.throw(_("Original Purchase Receipt {0} not found.").format(receipt_name))

    docstatus = frappe.db.get_value("Purchase Receipt", receipt_name, "docstatus")
    if docstatus != 1:
        frappe.throw(_("Purchase Receipt {0} must be submitted to create a return.").format(receipt_name))

    if not return_items:
        frappe.throw(_("Return items list cannot be empty."))

    return_items_list = frappe.parse_json(return_items)
    
    # Create return mapping of receipt_item_name -> return_qty and optional warehouse
    return_qty_map = {}
    return_wh_map = {}
    for it in return_items_list:
        ref_row = it.get("receipt_item_name")
        qty = flt(it.get("qty"))
        wh = it.get("warehouse")
        if qty > 0:
            return_qty_map[ref_row] = qty
            if wh:
                return_wh_map[ref_row] = wh

    if not return_qty_map:
        frappe.throw(_("At least one item must have a return quantity greater than 0."))

    from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
    return_doc = make_purchase_return(receipt_name)
    
    # Keep only returning items, adjust quantities to negative values
    kept_items = []
    for item in return_doc.items:
        ref_row = item.purchase_receipt_item
        if ref_row in return_qty_map:
            # Set negative qty for returns
            item.qty = -1.0 * return_qty_map[ref_row]
            if ref_row in return_wh_map:
                item.warehouse = return_wh_map[ref_row]
            kept_items.append(item)
            
    return_doc.items = kept_items

    if not return_doc.items:
        frappe.throw(_("No matching items found for return."))

    if remarks:
        return_doc.remarks = remarks

    try:
        return_doc.insert(ignore_permissions=True)
        return_doc.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": return_doc.name,
        "message": _("Supplier Return {0} submitted successfully.").format(return_doc.name)
    }
