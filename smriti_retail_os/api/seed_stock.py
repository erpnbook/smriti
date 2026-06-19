# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/seed_stock.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
import frappe

def run():
    print("START SEEDING STOCK...")
    company = "_Test Company"
    warehouse = "Goods In Transit - _C"
    cost_center = "Main - _C"
    items = ["ITEM-001", "ITEM-002", "ITEM-003", "ITEM-004", "ITEM-005"]

    # Check if stock already exists
    has_stock = False
    for item_code in items:
        qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
        if qty and qty > 0:
            print(f"Item {item_code} already has stock: {qty}")
            has_stock = True
            break
            
    if has_stock:
        print("Stock already exists, skipping seeding.")
        return

    # Create Material Receipt Stock Entry
    se = frappe.get_doc({
        "doctype": "Stock Entry",
        "purpose": "Material Receipt",
        "stock_entry_type": "Material Receipt",
        "company": company,
        "set_posting_time": 1,
        "items": []
    })

    for item_code in items:
        if not frappe.db.exists("Item", item_code):
            print(f"Item {item_code} does not exist, skipping.")
            continue
        se.append("items", {
            "item_code": item_code,
            "qty": 1000,
            "t_warehouse": warehouse,
            "cost_center": cost_center,
            "basic_rate": 1000.0,
            "incoming_rate": 1000.0,
            "uom": "Nos",
            "stock_uom": "Nos",
            "conversion_factor": 1.0
        })

    if not se.items:
        print("No items to add stock for.")
        return

    se.insert(ignore_permissions=True)
    se.submit()
    print(f"Created and submitted Stock Entry {se.name} for items.")
    frappe.db.commit()
