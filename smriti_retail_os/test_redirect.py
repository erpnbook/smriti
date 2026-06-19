# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/test_redirect.py
# @description: SMRITI redirect test — boot.py route guard verification.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
from smriti_retail_os import boot

def execute():
    # Test 1: Guest user on legacy /desk route
    frappe.local.session = frappe._dict(user='Guest')
    frappe.local.request = frappe._dict(path='/desk/smriti-cge', cookies={})
    
    print("Testing /desk/smriti-cge for Guest (Should redirect to /smriti-cge):")
    try:
        boot.check_desk_access()
        print("Result: Allowed")
    except Exception as e:
        print(f"Result: Redirected/Exception: {type(e).__name__} -> {e}")

    # Test 2: Administrator user on canonical /app route
    frappe.local.session = frappe._dict(user='Administrator')
    frappe.local.request = frappe._dict(path='/app/smriti-cge', cookies={})
    
    print("\nTesting /app/smriti-cge for Administrator (Should redirect to /smriti-cge):")
    try:
        boot.check_desk_access()
        print("Result: Allowed")
    except Exception as e:
        print(f"Result: Redirected/Exception: {type(e).__name__} -> {e}")
