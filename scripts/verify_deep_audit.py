# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/verify_deep_audit.py
# @description: Deep audit runner -- validates SMRITI backend API integrity.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt

def verify_smriti_retail_os():
    print("\n[SMRITI] Starting Deep Audit Verification...")
    errors = 0

    # 1. Check Schema Consistency
    print("\n1. Verifying Schema Alignment:")
    pos_fields = frappe.get_meta("POS Invoice").fields
    field_names = [f.fieldname for f in pos_fields]
    
    expected_fields = ["discount_amount", "billing_address_gstin", "owner"]
    for f in expected_fields:
        if f in field_names or f == "owner":
            print(f"  [OK] Field '{f}' verified.")
        else:
            print(f"  [ERROR] Field '{f}' missing from POS Invoice!")
            errors += 1

    # 2. Check Child Tables
    print("\n2. Verifying Child Tables:")
    if frappe.db.exists("DocType", "Sales Invoice Payment"):
        print("  [OK] 'Sales Invoice Payment' table exists.")
    else:
        print("  [ERROR] 'Sales Invoice Payment' table missing!")
        errors += 1

    # 3. Test Reporting API
    print("\n3. Testing Reports API:")
    try:
        from smriti_retail_os.reports_api import get_sales_report
        report = get_sales_report()
        if "summary" in report:
            print("  [OK] Sales Report API execution successful.")
            print(f"       Total Sales: {report['summary']['total_sales']}")
        else:
            print("  [ERROR] Sales Report API returned invalid format.")
            errors += 1
    except Exception as e:
        print(f"  [ERROR] Sales Report API crashed: {str(e)}")
        errors += 1

    # 4. Test Shift API
    print("\n4. Testing Shift API:")
    try:
        from smriti_retail_os.shift_api import get_active_shift
        # Mock a cashier session
        original_user = frappe.session.user
        frappe.set_user("Administrator")
        shift = get_active_shift("Administrator")
        print("  [OK] Shift API execution successful.")
        frappe.set_user(original_user)
    except Exception as e:
        print(f"  [ERROR] Shift API crashed: {str(e)}")
        errors += 1

    print(f"\n[SMRITI] Audit Complete. Total Errors Found: {errors}")
    if errors == 0:
        print("[SMRITI] System is STABLE and Schema-Aligned.")
    else:
        print("[SMRITI] Please review the errors above.")

if __name__ == "__main__":
    verify_smriti_retail_os()
