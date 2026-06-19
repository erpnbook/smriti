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

sites_path = "/home/frappe/frappe-bench/sites"
site = "frontend"
if not os.path.exists(os.path.join(sites_path, site)):
    folders = [f for f in os.listdir(sites_path) if os.path.isdir(os.path.join(sites_path, f)) and f not in ('assets', 'languages')]
    if folders:
        site = folders[0]
frappe.init(site=site, sites_path=sites_path)
frappe.connect()
frappe.flags.in_import = True

# Force developer_mode to 1 globally so standard pages can be imported/deleted
frappe.conf.developer_mode = 1
if hasattr(frappe.local, 'conf'):
    frappe.local.conf.developer_mode = 1

def import_page(page_name):
    json_path = frappe.get_app_path('smriti_retail_os', 'smriti_retail_os', 'page', page_name, f'{page_name}.json')
    if not os.path.exists(json_path):
        print(f"SKIP {page_name}")
        return
    with open(json_path) as f:
        data = json.load(f)
    roles = data.pop('roles', [])
    for k in ['modified', 'modified_by', 'creation', 'owner']:
        data.pop(k, None)
        
    data['name'] = page_name
    data['page_name'] = page_name
        
    old_hyphen_name = page_name.replace('_', '-')
    for name_to_check in (page_name, old_hyphen_name):
        if frappe.db.exists('Page', name_to_check):
            frappe.delete_doc('Page', name_to_check, ignore_permissions=True, force=True)
            print(f"DELETED OLD {name_to_check}")
        
    data['doctype'] = 'Page'
    doc = frappe.get_doc(data)
    for r in roles:
        doc.append('roles', r)
    doc.insert(ignore_permissions=True)
    print(f"CREATED {page_name}")

import_page('smriti_desk')
import_page('smriti_billing')
import_page('smriti_shift')
import_page('smriti_inventory')
import_page('smriti_barcode')
import_page('smriti_purchase')
import_page('smriti_reports')
import_page('smriti_loyalty')
import_page('smriti_backup')
import_page('smriti_item_master')
import_page('smriti_cge')
frappe.db.commit()
print("DONE")
