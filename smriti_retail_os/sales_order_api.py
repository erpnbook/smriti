# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/sales_order_api.py
# @description: Backend API for SMRITI Sales Orders module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-16
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, nowdate
from frappe import _

def check_store_manager_role():
    """
    Enforces that only SMRITI Store Manager or System Manager can perform submissions.
    """
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(_("Access Denied: Cashiers can only view. Only Store Managers or System Managers can submit sales orders."))

@frappe.whitelist()
def get_open_sales_orders(customer=None):
    """
    Fetches submitted and open Sales Orders.
    """
    filters = {
        "docstatus": 1,
        "status": ["not in", ["Closed", "Completed"]]
    }
    if customer:
        filters["customer"] = customer

    orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        fields=["name", "customer", "customer_name", "transaction_date", "grand_total", "per_delivered"],
        order_by="transaction_date desc"
    )
    return orders

@frappe.whitelist()
def get_so_details(so_name):
    """
    Fetches open item lines for a given Sales Order.
    """
    if not frappe.db.exists("Sales Order", so_name):
        return None

    so = frappe.get_doc("Sales Order", so_name)
    items = []
    
    for item in so.items:
        # Calculate pending quantity to deliver
        pending = flt(item.qty) - flt(item.delivered_qty)
        if pending > 0:
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "brand": item.brand,
                "qty": pending,
                "so_qty": item.qty,
                "delivered_qty": item.delivered_qty,
                "rate": item.rate,
                "stock_uom": item.stock_uom,
                "warehouse": item.warehouse,
                "so_item_name": item.name
            })

    return {
        "name": so.name,
        "customer": so.customer,
        "customer_name": so.customer_name,
        "company": so.company,
        "items": items
    }

@frappe.whitelist()
def create_sales_order(customer, items, delivery_date=None, remarks=None):
    """
    Creates and submits a standard Sales Order.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create Sales Order with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company") or (frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None)

    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.transaction_date = nowdate()
    so.delivery_date = delivery_date or nowdate()
    so.company = company
    if remarks:
        so.remarks = remarks

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse")

        if not wh:
            # Get default warehouse from Item or fallback
            wh = frappe.db.get_value("Item Reorder", {"parent": item_code}, "warehouse") or frappe.db.get_value("Item", item_code, "default_warehouse")
        if not wh:
            # Fallback to general warehouse
            wh = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")

        so.append("items", {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "delivery_date": delivery_date or nowdate(),
            "uom": it.get("stock_uom") or frappe.db.get_value("Item", item_code, "stock_uom") or "Nos"
        })

    try:
        so.insert(ignore_permissions=True)
        so.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": so.name,
        "message": _("Sales Order {0} submitted successfully.").format(so.name)
    }
