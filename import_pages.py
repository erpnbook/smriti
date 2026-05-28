# -*- coding: utf-8 -*-
#
# @file: import_pages.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
import os

frappe.conf.developer_mode = 1

def import_page(page_name):
    json_path = f'/home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/page/{page_name}/{page_name}.json'
    if not os.path.exists(json_path):
        print(f"SKIP {page_name}")
        return
    with open(json_path) as f:
        data = json.load(f)
    roles = data.pop('roles', [])
    for k in ['modified', 'modified_by', 'creation', 'owner']:
        data.pop(k, None)
        
    if frappe.db.exists('Page', page_name):
        frappe.delete_doc('Page', page_name, ignore_permissions=True, force=True)
        print(f"DELETED OLD {page_name}")
        
    data['doctype'] = 'Page'
    doc = frappe.get_doc(data)
    for r in roles:
        doc.append('roles', r)
    doc.insert(ignore_permissions=True)
    print(f"CREATED {page_name}")

import_page('smriti-desk')
import_page('smriti-billing')
import_page('smriti-shift')
import_page('smriti-inventory')
import_page('smriti-barcode')
import_page('smriti-purchase')
import_page('smriti-reports')
import_page('smriti-loyalty')
frappe.db.commit()
print("DONE")
