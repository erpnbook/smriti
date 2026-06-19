# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/create_indexes.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe

def run():
    print("Creating uq_wallet_cust_comp_inst...")
    try:
        frappe.db.sql("CREATE UNIQUE INDEX uq_wallet_cust_comp_inst ON `tabSMRITI Benefit Wallet` (customer, company, benefit_instrument)")
        print("Success")
    except Exception as e:
        print(f"Error/Already exists: {e}")
        
    print("Creating idx_ledger_cust_inst_date...")
    try:
        frappe.db.sql("CREATE INDEX idx_ledger_cust_inst_date ON `tabSMRITI Benefit Ledger` (customer, benefit_instrument, posting_date)")
        print("Success")
    except Exception as e:
        print(f"Error/Already exists: {e}")
        
    print("Creating idx_ledger_ref...")
    try:
        frappe.db.sql("CREATE INDEX idx_ledger_ref ON `tabSMRITI Benefit Ledger` (reference_doctype, reference_name)")
        print("Success")
    except Exception as e:
        print(f"Error/Already exists: {e}")
        
    frappe.db.commit()
    print("Index creation complete!")
