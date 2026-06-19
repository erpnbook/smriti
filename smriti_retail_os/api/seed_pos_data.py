# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/seed_pos_data.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
import frappe
from frappe import _

def run():
    print("START SEEDING POS DATA...")
    company = "_Test Company"
    price_list = "Standard Selling"
    cost_center = "Main - _C"

    # 1. Update POS Settings to use POS Invoice
    frappe.db.set_single_value("POS Settings", "invoice_type", "POS Invoice")
    print("Set POS Settings invoice_type to 'POS Invoice'")

    # 2. Create Item Tax Template for _Test Company
    item_tax_template_title = "GST 18% - _TC"
    item_tax_template_name = frappe.db.get_value("Item Tax Template", {"title": item_tax_template_title, "company": company}, "name")
    
    if not item_tax_template_name:
        itt = frappe.get_doc({
            "doctype": "Item Tax Template",
            "title": item_tax_template_title,
            "company": company,
            "gst_rate": 18,
            "gst_treatment": "Taxable",
            "taxes": [
                {
                    "tax_type": "Output Tax CGST - _C",
                    "tax_rate": 9.0
                },
                {
                    "tax_type": "Output Tax SGST - _C",
                    "tax_rate": 9.0
                }
            ]
        })
        itt.insert(ignore_permissions=True)
        item_tax_template_name = itt.name
        print(f"Created Item Tax Template: {item_tax_template_name}")
    else:
        print(f"Item Tax Template {item_tax_template_name} already exists.")

    # 3. Update Items to trigger the before_save hook (sync_item_taxes_and_prices)
    items = ["ITEM-001", "ITEM-002", "ITEM-003", "ITEM-004", "ITEM-005"]
    for item_code in items:
        if not frappe.db.exists("Item", item_code):
            print(f"Warning: Item {item_code} does not exist!")
            continue
        
        price_exists = frappe.db.exists("Item Price", {
            "item_code": item_code,
            "price_list": price_list
        })
        if not price_exists:
            ip = frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": price_list,
                "price_list_rate": 1000.0
            })
            ip.insert(ignore_permissions=True)
            print(f"Created Item Price for {item_code}: 1000.0")
        
        item = frappe.get_doc("Item", item_code)
        
        seen_uoms = set()
        unique_uoms = []
        for u in item.get("uoms") or []:
            if u.uom not in seen_uoms:
                seen_uoms.add(u.uom)
                unique_uoms.append(u)
        item.set("uoms", unique_uoms)
        
        item.custom_gst_percentage = "18"  # Set explicitly to ensure it finds the template
        item.save(ignore_permissions=True)
        print(f"Updated Item {item_code} with taxes: {[t.item_tax_template for t in item.taxes]}")

    # 4. Create Sales Taxes and Charges Template for _Test Company
    template_title = "GST 18% - _TC"
    existing = frappe.db.get_value("Sales Taxes and Charges Template", {"title": template_title, "company": company}, "name")
    
    if not existing:
        template = frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": template_title,
            "company": company,
            "is_default": 1,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": "Output Tax CGST - _C",
                    "description": "CGST 9%",
                    "rate": 9.0,
                    "cost_center": cost_center,
                    "account_currency": "INR"
                },
                {
                    "charge_type": "On Net Total",
                    "account_head": "Output Tax SGST - _C",
                    "description": "SGST 9%",
                    "rate": 9.0,
                    "cost_center": cost_center,
                    "account_currency": "INR"
                }
            ]
        })
        template.insert(ignore_permissions=True)
        template_name = template.name
        print(f"Created Sales Taxes and Charges Template. Generated name: {template_name}")
    else:
        template_name = existing
        print(f"Sales Taxes and Charges Template {template_name} already exists.")

    # 5. Link template to Test POS Profile
    pos_profile = frappe.get_doc("POS Profile", "Test POS Profile")
    pos_profile.taxes_and_charges = template_name
    
    # Resolve write_off_account
    write_off_account = frappe.db.get_value("Account", {"company": company, "account_type": "Write Off"}, "name")
    if not write_off_account:
        write_off_account = frappe.db.get_value("Account", {"company": company, "name": ["like", "%write%"]}, "name")
    if not write_off_account:
        write_off_account = frappe.db.get_value("Account", {"company": company, "root_type": "Expense"}, "name")
        
    pos_profile.write_off_account = write_off_account
    pos_profile.write_off_cost_center = cost_center
    
    pos_profile.save(ignore_permissions=True)
    print(f"Linked tax template '{template_name}' and set write-off account '{write_off_account}' on Test POS Profile.")

    frappe.db.commit()
    print("SEEDING COMPLETE!")
