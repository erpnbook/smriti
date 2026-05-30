# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/master_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint
from frappe import _

@frappe.whitelist()
def quick_create_item(item_name, barcode, rate, mrp, gst_percentage):
    """
    Creates a new Item, Barcode, and Price List entry in one step.
    Designed for "Dumb User" speed — minimal fields, maximum automation.
    """
    if not item_name or not barcode:
        frappe.throw(_("Item Name and Barcode are required."))

    # 1. Create the Item
    item = frappe.new_doc("Item")
    item.item_code = barcode # For retail, item_code = barcode is the simplest way
    item.item_name = item_name
    item.item_group = "Products"
    item.stock_uom = "Nos"
    item.is_stock_item = 1
    item.opening_stock = 0
    item.standard_rate = flt(rate)
    # Custom fields — use safe setter in case not installed
    try: item.custom_is_retail_item = 1
    except Exception: pass
    try: item.custom_gst_percentage = str(gst_percentage)
    except Exception: pass
    try: item.custom_mrp = flt(mrp)
    except Exception: pass
    
    # Auto-resolve Item Tax Template from percentage
    template_name = frappe.db.get_value(
        "Item Tax Template", 
        {"name": ["like", f"%{gst_percentage}%"]}, 
        "name"
    )
    if template_name:
        item.append("taxes", {
            "item_tax_template": template_name,
            "tax_category": ""
        })

    item.insert(ignore_permissions=True)

    # 2. Add Barcode (redundant if item_code = barcode, but good for ERPNext standard)
    item.append("barcodes", {
        "barcode": barcode,
        "uom": "Nos"
    })
    item.save(ignore_permissions=True)

    # 3. Create Price List entries
    create_item_price(item.name, "Standard Selling", rate)
    create_item_price(item.name, "MRP", mrp)

    frappe.db.commit()

    return {
        "item_code": item.name,
        "item_name": item.item_name,
        "rate": flt(rate),
        "mrp": flt(mrp),
        "gst_percentage": cint(gst_percentage),
        "stock_uom": "Nos"
    }

def create_item_price(item_code, price_list, rate):
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.enabled = 1
        pl.selling = 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    ip = frappe.new_doc("Item Price")
    ip.item_code = item_code
    ip.price_list = price_list
    ip.price_list_rate = flt(rate)
    ip.currency = "INR"
    ip.uom = "Nos"
    ip.insert(ignore_permissions=True)

@frappe.whitelist()
def quick_create_customer(customer_name, mobile_no):
    """
    Simplified Customer creation.
    """
    if not customer_name:
        frappe.throw(_("Customer Name is required."))

    cust = frappe.new_doc("Customer")
    cust.customer_name = customer_name
    cust.mobile_no = mobile_no
    
    # Robust Customer Group auto-resolution
    customer_group = "Individual"
    if not frappe.db.exists("Customer Group", customer_group):
        if frappe.db.exists("Customer Group", "All Customer Groups"):
            customer_group = "All Customer Groups"
        else:
            existing = frappe.db.get_all("Customer Group", order_by="creation asc", pluck="name", limit=1)
            if existing:
                customer_group = existing[0]
            else:
                cg = frappe.new_doc("Customer Group")
                cg.customer_group_name = "Individual"
                cg.insert(ignore_permissions=True)
                customer_group = cg.name
    cust.customer_group = customer_group

    # Robust Territory auto-resolution
    territory = "All Territories"
    if not frappe.db.exists("Territory", territory):
        existing = frappe.db.get_all("Territory", order_by="creation asc", pluck="name", limit=1)
        if existing:
            territory = existing[0]
        else:
            t = frappe.new_doc("Territory")
            t.territory_name = "All Territories"
            t.insert(ignore_permissions=True)
            territory = t.name
    cust.territory = territory
    
    cust.customer_type = "Individual"
    cust.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {
        "name": cust.name,
        "customer_name": cust.customer_name,
        "mobile_no": cust.mobile_no
    }

@frappe.whitelist()
def quick_create_supplier(supplier_name, mobile_no=None):
    """
    Simplified Supplier creation.
    """
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    supp = frappe.new_doc("Supplier")
    supp.supplier_name = supplier_name
    
    # Robust Supplier Group auto-resolution
    supplier_group = "Local"
    if not frappe.db.exists("Supplier Group", supplier_group):
        if frappe.db.exists("Supplier Group", "All Supplier Groups"):
            supplier_group = "All Supplier Groups"
        else:
            existing_groups = frappe.db.get_all("Supplier Group", order_by="creation asc", pluck="name", limit=1)
            if existing_groups:
                supplier_group = existing_groups[0]
            else:
                sg = frappe.new_doc("Supplier Group")
                sg.supplier_group_name = "Local"
                sg.insert(ignore_permissions=True)
                supplier_group = sg.name
    supp.supplier_group = supplier_group
    
    supp.supplier_type = "Individual"
    if mobile_no:
        supp.mobile_no = mobile_no
    supp.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {
        "name": supp.name,
        "supplier_name": supp.supplier_name
    }


@frappe.whitelist()
def save_supplier_on_fly(supplier_name, supplier_group, supplier_type, name=None):
    """
    Allows creating or updating a Supplier on the fly with permissions bypassed.
    """
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    if name:
        doc = frappe.get_doc("Supplier", name)
        doc.supplier_name = supplier_name
        doc.supplier_group = supplier_group
        doc.supplier_type = supplier_type
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Supplier")
        doc.supplier_name = supplier_name
        doc.supplier_type = supplier_type
        # Robust group resolution — same as quick_create_supplier
        resolved_group = supplier_group
        if not frappe.db.exists("Supplier Group", resolved_group):
            if frappe.db.exists("Supplier Group", "All Supplier Groups"):
                resolved_group = "All Supplier Groups"
            else:
                existing = frappe.db.get_all("Supplier Group", pluck="name", limit=1)
                resolved_group = existing[0] if existing else "Local"
        doc.supplier_group = resolved_group
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "name": doc.name,
        "supplier_name": doc.supplier_name
    }

