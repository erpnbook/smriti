# -*- coding: utf-8 -*-
#
# @file: import_pages.py
# @description: Handles page registration safely inside docker.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
import os

# Monkeypatch export_module_json to prevent PermissionError when in developer_mode
import frappe.modules.utils
frappe.modules.utils.export_module_json = lambda *args, **kwargs: None

try:
    import frappe.core.doctype.page.page
    frappe.core.doctype.page.page.export_module_json = lambda *args, **kwargs: None
except ImportError:
    pass

try:
    import frappe.modules.export_file
    frappe.modules.export_file.export_module_json = lambda *args, **kwargs: None
except ImportError:
    pass

frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()
frappe.flags.in_import = True

# Force developer_mode to 1 globally so standard pages can be imported/deleted
frappe.conf.developer_mode = 1
if hasattr(frappe.local, 'conf'):
    frappe.local.conf.developer_mode = 1

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
import_page('smriti-backup')
frappe.db.commit()
print("DONE")
