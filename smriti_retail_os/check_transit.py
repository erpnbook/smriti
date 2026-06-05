# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/check_transit.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
import traceback

def execute():
    try:
        print("Transit Exists:", frappe.db.exists("Warehouse Type", "Transit"))
        print(frappe.get_all("Warehouse Type", fields=["name"]))
    except Exception as e:
        print("Error getting Warehouse Types:")
        traceback.print_exc()

    # Try creating a company to catch the exact stack trace
    try:
        if not frappe.db.exists("Company", "Transit Test Co"):
            doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": "Transit Test Co",
                "abbr": "TTC",
                "default_currency": "INR",
                "country": "India"
            })
            doc.insert(ignore_permissions=True)
            print("Company created successfully (Unexpected)")
            doc.delete()
        else:
            print("Test company already exists.")
    except Exception as e:
        print("STACK TRACE CAUGHT:")
        traceback.print_exc()
