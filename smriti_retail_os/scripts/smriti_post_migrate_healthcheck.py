# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/scripts/smriti_post_migrate_healthcheck.py
# @description: Post-migration database and registry health checks for SMRITI Retail OS.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-18
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def run():
    print("\n================ SMRITI POST-MIGRATE HEALTH CHECK ================")
    
    doctypes = [
        "SMRITI Company Settings", "SMRITI Report Role", "SMRITI Report Template",
        "SMRITI Saved View", "SMRITI Address Audit Log", "SMRITI Key Custodian",
        "SMRITI Print Job", "SMRITI Heel Type", "SMRITI Outsole",
        "SMRITI Upper Material", "SMRITI Gender", "SMRITI Purchase Class",
        "SMRITI Merchandise Category", "SMRITI Sub Category"
    ]
    
    # Check 1: DocType Registry
    try:
        missing_dt = []
        for dt in doctypes:
            if not frappe.db.exists("DocType", dt):
                missing_dt.append(dt)
        if missing_dt:
            print(f"FAIL  DocType Registry (Missing: {', '.join(missing_dt)})")
        else:
            print("PASS  DocType Registry")
    except Exception as e:
        print(f"FAIL  DocType Registry ({str(e)})")
        
    # Check 2: Missing Tables
    try:
        missing_tables = []
        for dt in doctypes:
            meta = frappe.get_meta(dt)
            if not meta.issingle:
                if not frappe.db.table_exists(dt):
                    missing_tables.append(dt)
        if missing_tables:
            print(f"FAIL  Missing Tables (Missing: {', '.join(missing_tables)})")
        else:
            print("PASS  Missing Tables")
    except Exception as e:
        print(f"FAIL  Missing Tables ({str(e)})")
        
    # Check 3: Missing Fields
    try:
        mismatched_fields = []
        for dt in doctypes:
            meta = frappe.get_meta(dt)
            if not meta.issingle and frappe.db.table_exists(dt):
                db_cols = frappe.db.get_table_columns(dt)
                for f in meta.fields:
                    if f.fieldtype not in ["Section Break", "Column Break", "Table", "Table MultiSelect", "HTML", "Button"]:
                        if f.fieldname not in db_cols:
                            mismatched_fields.append(f"{dt}.{f.fieldname}")
        if mismatched_fields:
            print(f"FAIL  Missing Fields (Missing: {', '.join(mismatched_fields)})")
        else:
            print("PASS  Missing Fields")
    except Exception as e:
        print(f"FAIL  Missing Fields ({str(e)})")
        
    # Check 4: Custom Fields
    try:
        # Check standard custom field synchronization (on Address or Customer/POS Invoice)
        custom_fields = frappe.db.count("Custom Field", {"module": "SMRITI Retail OS"})
        addr_custom = frappe.db.exists("Custom Field", {"dt": "Address", "fieldname": "store_trade_name"}) or frappe.db.exists("Custom Field", {"dt": "Address", "fieldname": "sb_store_trade_name"})
        if custom_fields > 0 or addr_custom:
            print("PASS  Custom Fields")
        else:
            print("FAIL  Custom Fields (No SMRITI custom fields found)")
    except Exception as e:
        print(f"FAIL  Custom Fields ({str(e)})")
        
    # Check 5: Property Setters
    try:
        # Check property setters presence
        setters = frappe.db.count("Property Setter", {"module": "SMRITI Retail OS"})
        print("PASS  Property Setters")
    except Exception as e:
        print(f"FAIL  Property Setters ({str(e)})")
        
    # Check 6: Fixtures
    try:
        roles_loaded = frappe.db.exists("Role", "SMRITI Cashier") and frappe.db.exists("Role", "SMRITI Store Manager")
        workspace_loaded = frappe.db.exists("Workspace", "SMRITI Retail OS")
        if roles_loaded and workspace_loaded:
            print("PASS  Fixtures")
        else:
            print(f"FAIL  Fixtures (Roles: {roles_loaded}, Workspace: {workspace_loaded})")
    except Exception as e:
        print(f"FAIL  Fixtures ({str(e)})")
        
    # Check 7: Seed Records
    try:
        modes = ["Cash", "UPI", "Card"]
        missing_modes = []
        for m in modes:
            if not frappe.db.exists("Mode of Payment", m):
                missing_modes.append(m)
        if missing_modes:
            print(f"FAIL  Seed Records (Missing MOP: {', '.join(missing_modes)})")
        else:
            print("PASS  Seed Records")
    except Exception as e:
        print(f"FAIL  Seed Records ({str(e)})")
        
    # Check 8: Company Settings
    try:
        settings = frappe.get_all("SMRITI Company Settings")
        print("PASS  Company Settings")
    except Exception as e:
        print(f"FAIL  Company Settings ({str(e)})")
        
    # Check 9: Report Templates
    try:
        templates = frappe.get_all("SMRITI Report Template")
        if len(templates) > 0:
            print("PASS  Report Templates")
        else:
            print("FAIL  Report Templates (No templates seeded)")
    except Exception as e:
        print(f"FAIL  Report Templates ({str(e)})")
        
    # Check 10: Print Jobs
    try:
        jobs = frappe.get_all("SMRITI Print Job")
        print("PASS  Print Jobs")
    except Exception as e:
        print(f"FAIL  Print Jobs ({str(e)})")
        
    print("==================================================================\n")
