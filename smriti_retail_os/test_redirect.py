# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/test_redirect.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
from smriti_retail_os import boot

def execute():
    # Test 1: Guest user
    frappe.local.session = frappe._dict(user='Guest')
    frappe.local.request = frappe._dict(path='/desk/smriti-cge', cookies={})
    
    print("Testing /desk/smriti-cge for Guest:")
    try:
        boot.check_desk_access()
        print("Result: Allowed")
    except Exception as e:
        print(f"Result: Redirected/Exception: {type(e).__name__} -> {e}")

    # Test 2: Administrator user
    frappe.local.session = frappe._dict(user='Administrator')
    frappe.local.request = frappe._dict(path='/desk/smriti-cge', cookies={})
    
    print("\nTesting /desk/smriti-cge for Administrator:")
    try:
        boot.check_desk_access()
        print("Result: Allowed")
    except Exception as e:
        print(f"Result: Redirected/Exception: {type(e).__name__} -> {e}")
