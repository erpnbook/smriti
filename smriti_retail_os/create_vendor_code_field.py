# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/create_vendor_code_field.py
# @description: Migration helper to create the Vendor Code custom field on Supplier.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def run():
    print("Creating custom field custom_vendor_code on Supplier...")
    custom_fields = {
        "Supplier": [
            {
                "fieldname": "custom_vendor_code",
                "label": "Vendor Code",
                "fieldtype": "Data",
                "insert_after": "custom_credit_days",
                "unique": 1,
                "module": "SMRITI Retail OS"
            }
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
    print("Custom field custom_vendor_code created successfully on Supplier.")
