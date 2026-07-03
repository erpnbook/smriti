# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/purchase_api.py
# @description: Backend API for SMRITI Purchase Operations terminal.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, nowdate
from frappe import _

def _get_default_warehouse(company):
    """Company ke saath matching warehouse lo."""
    if not company:
        return None
    warehouse = frappe.db.get_value(
        "Warehouse",
        {"company": company, "is_group": 0, "warehouse_name": "Stores"},
        "name"
    )
    if not warehouse:
        warehouse = frappe.db.get_value(
            "Warehouse",
            {"company": company, "is_group": 0},
            "name",
            order_by="creation asc"
        )
    if not warehouse:
        warehouse = frappe.db.get_value(
            "Warehouse",
            {"company": company},
            "name"
        )
    if warehouse and frappe.db.get_value("Warehouse", warehouse, "company") == company:
        return warehouse
    return None

def check_store_manager_role():
    """
    Enforces that only SMRITI Store Manager or System Manager can perform submissions.
    """
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(_("Access Denied: Cashiers can only view. Only Store Managers or System Managers can submit purchase transactions."))

def get_or_create_batch(item_code, expiry_date=None):
    """
    Finds or creates a batch for an item, optionally with an expiry date.
    """
    if expiry_date:
        existing = frappe.db.get_value("Batch", {"item": item_code, "expiry_date": expiry_date, "disabled": 0}, "name")
        if existing:
            return existing
        
        batch_doc = frappe.new_doc("Batch")
        batch_doc.item = item_code
        batch_doc.expiry_date = expiry_date
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name
    else:
        existing = frappe.db.get_value("Batch", {"item": item_code, "disabled": 0}, "name", order_by="creation desc")
        if existing:
            return existing
        
        batch_doc = frappe.new_doc("Batch")
        batch_doc.item = item_code
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name

@frappe.whitelist()
def get_open_purchase_orders(supplier=None):
    """
    Fetches submitted and open Purchase Orders.
    """
    filters = {
        "docstatus": 1,
        "status": ["not in", ["Closed", "Completed"]]
    }
    if supplier:
        filters["supplier"] = supplier

    pos = frappe.get_all(
        "Purchase Order",
        filters=filters,
        fields=["name", "supplier", "supplier_name", "transaction_date", "grand_total", "per_received"],
        order_by="transaction_date desc"
    )
    return pos

@frappe.whitelist()
def get_po_details(po_name):
    """
    Fetches open item lines for a given Purchase Order.
    """
    if not frappe.db.exists("Purchase Order", po_name):
        return None

    po = frappe.get_doc("Purchase Order", po_name)
    items = []
    
    for item in po.items:
        # Calculate pending quantity to receive
        pending = flt(item.qty) - flt(item.received_qty)
        if pending > 0:
            has_batch_no = frappe.db.get_value("Item", item.item_code, "has_batch_no")
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "brand": item.brand,
                "qty": pending,
                "po_qty": item.qty,
                "received_qty": item.received_qty,
                "rate": item.rate,
                "stock_uom": item.stock_uom,
                "warehouse": item.warehouse,
                "po_item_name": item.name,
                "has_batch_no": cint(has_batch_no)
            })

    return {
        "name": po.name,
        "supplier": po.supplier,
        "supplier_name": po.supplier_name,
        "company": po.company,
        "items": items
    }

@frappe.whitelist()
def create_purchase_order(supplier, items, schedule_date=None, remarks=None, image_base64=None, image_filename=None, warehouse=None):
    """
    Creates and submits a standard Purchase Order.
    Includes auto-creation of footwear variant items if they do not exist.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create Purchase Order with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company") or (frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None)
    warehouse = warehouse or _get_default_warehouse(company)

    # Save uploaded image file if present
    file_url = None
    if image_base64 and image_filename:
        try:
            import base64
            from frappe.utils.file_manager import save_file
            
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            file_content = base64.b64decode(image_base64)
            
            first_code = items_list[0].get("item_code") if len(items_list) > 0 else "temp_item"
            saved_file = save_file(
                image_filename, 
                file_content, 
                "Item", 
                first_code, 
                decode=False, 
                is_private=0
            )
            file_url = saved_file.file_url
        except Exception as e:
            frappe.log_error(f"SMRITI: Failed to save uploaded variant image: {str(e)}")

    po = frappe.new_doc("Purchase Order")
    po.supplier = supplier
    po.transaction_date = nowdate()
    po.schedule_date = schedule_date or nowdate()
    po.company = company
    if remarks:
        po.terms = remarks  # po.terms is the legal Terms & Conditions field where remarks go in SMRITI

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse") or warehouse

        # Self-healing Item Variant Auto-creation
        if not frappe.db.exists("Item", item_code):
            parts = item_code.split('-')
            style = parts[0] if len(parts) > 0 else "UNKNOWN"
            color = parts[1] if len(parts) > 1 else "UNKNOWN"
            size = parts[2] if len(parts) > 2 else "UNKNOWN"

            item = frappe.new_doc("Item")
            item.item_code = item_code
            item.item_name = f"{style} {color} {size}"
            default_group = frappe.db.get_single_value("SMRITI Settings", "default_item_group") or "Products"
            item.item_group = default_group if frappe.db.exists("Item Group", default_group) else "Products"
            item.stock_uom = "Nos"
            item.is_stock_item = 1
            item.standard_rate = rate
            item.custom_is_retail_item = 1
            item.custom_mrp = flt(rate * 1.5) # Auto default MRP to cost * 1.5
            
            # Assign uploaded image or fallback to existing variant image
            if file_url:
                item.image = file_url
            else:
                existing_img = frappe.db.get_value("Item", {"item_code": ["like", f"{style}-%"], "image": ["is", "set"]}, "image")
                if existing_img:
                    item.image = existing_img

            # Retrieve default GST HSN code from SMRITI Settings
            default_hsn = frappe.db.get_single_value("SMRITI Settings", "default_hsn_code")
            if default_hsn and frappe.db.exists("GST HSN Code", default_hsn):
                item.gst_hsn_code = default_hsn
            else:
                hsn_code = frappe.db.get_value("GST HSN Code", {}, "name")
                if hsn_code:
                    item.gst_hsn_code = hsn_code
            
            # Resolve GST Tax template (use standard 18% as default or try to match)
            template_name = frappe.db.get_value(
                "Item Tax Template", 
                {"name": ["like", "%18%"]}, 
                "name"
            )
            if template_name:
                item.append("taxes", {
                    "item_tax_template": template_name,
                    "tax_category": ""
                })
            item.insert(ignore_permissions=True)

            # Create/update price list entries
            for pl_name, pl_rate in [("Standard Selling", rate * 1.2), ("MRP", rate * 1.5)]:
                existing_ip = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": pl_name}, "name")
                if existing_ip:
                    frappe.db.set_value("Item Price", existing_ip, "price_list_rate", flt(pl_rate))
                else:
                    ip = frappe.new_doc("Item Price")
                    ip.item_code = item_code
                    ip.price_list = pl_name
                    ip.price_list_rate = flt(pl_rate)
                    ip.currency = "INR"
                    ip.uom = "Nos"
                    ip.insert(ignore_permissions=True)

        po.append("items", {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "schedule_date": schedule_date or nowdate(),
            "uom": it.get("stock_uom") or frappe.db.get_value("Item", item_code, "stock_uom")
        })

    # Correct Frappe submit lifecycle: insert() then submit()
    # DO NOT use docstatus=1 + save() — that bypasses before_submit/on_submit/after_submit hooks
    # which means stock reservation, GL entries, and PO status updates are never triggered.
    try:
        po.insert(ignore_permissions=True)
        po.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": po.name,
        "message": _("Purchase Order {0} submitted successfully.").format(po.name)
    }

@frappe.whitelist()
def create_purchase_receipt(supplier, items, po_name=None, warehouse=None):
    """
    Creates and submits a standard Purchase Receipt (GRN).
    Can be created against an existing Purchase Order or standalone (No PO).
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create Purchase Receipt with an empty items list."))

    items_list = frappe.parse_json(items)
    company = None
    if po_name and frappe.db.exists("Purchase Order", po_name):
        company = frappe.db.get_value("Purchase Order", po_name, "company")

    if not company:
        company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company") or (frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None)
    warehouse = warehouse or _get_default_warehouse(company)

    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = supplier
    pr.posting_date = nowdate()
    pr.company = company

    # If linked to a PO, reference it at the header level as well
    if po_name and frappe.db.exists("Purchase Order", po_name):
        # Fetching details from the PO
        po_doc = frappe.get_doc("Purchase Order", po_name)
        pr.buying_price_list = po_doc.buying_price_list
        pr.currency = po_doc.currency
        pr.conversion_rate = po_doc.conversion_rate

    # ── Batch-fetch item flags to eliminate N+1 queries in the item loop ─────
    item_codes_list = [it.get("item_code") for it in items_list]
    item_flag_rows = frappe.db.get_all(
        "Item",
        filters={"name": ["in", item_codes_list]},
        fields=["name", "has_batch_no", "stock_uom"]
    )
    item_flags_map = {r.name: r for r in item_flag_rows}
    # ──────────────────────────────────────────────────────────────────────────

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse") or warehouse

        # Handle batch & expiry tracking — uses pre-fetched flag, no per-item DB call
        batch_no = None
        item_flags = item_flags_map.get(item_code) or frappe._dict()
        if item_flags.get("has_batch_no"):
            expiry_date = it.get("expiry_date")
            batch_no = get_or_create_batch(item_code, expiry_date)

        row = {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "batch_no": batch_no,
            "uom": it.get("stock_uom") or item_flags.get("stock_uom") or "Nos"
        }

        # Map to Purchase Order if applicable
        if po_name:
            row["purchase_order"] = po_name
            row["purchase_order_item"] = it.get("po_item_name")

        pr.append("items", row)

    # Correct Frappe submit lifecycle: insert() then submit()
    # DO NOT use docstatus=1 + save() — that bypasses before_submit/on_submit/after_submit hooks
    # which means Stock Ledger Entries, GL Entries, and PO received_qty updates are never created.
    try:
        pr.insert(ignore_permissions=True)
        pr.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": pr.name,
        "message": _("Purchase Receipt {0} submitted successfully.").format(pr.name)
    }


@frappe.whitelist()
def create_purchase_return(receipt_name):
    """
    Creates and submits a Purchase Return against the original Purchase Receipt (GRN).
    """
    check_store_manager_role()

    docstatus = frappe.db.get_value("Purchase Receipt", receipt_name, "docstatus")
    if docstatus is None:
        frappe.throw(_("Purchase Receipt {0} not found.").format(receipt_name))
        
    if docstatus != 1:
        frappe.throw(_("Purchase Receipt {0} must be submitted to create a return.").format(receipt_name))

    from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
    
    return_doc = make_purchase_return(receipt_name)
    
    try:
        return_doc.insert(ignore_permissions=True)
        return_doc.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": return_doc.name,
        "message": _("Purchase Return {0} created and submitted successfully.").format(return_doc.name)
    }

