# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/import_cge_page.py
# @description: SMRITI Import Cge Page — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import json
import os
import frappe

def execute():
    frappe.conf.developer_mode = 1
    page_name = 'smriti_cge'
    json_path = frappe.get_app_path('smriti_retail_os', 'smriti_retail_os', 'page', page_name, f'{page_name}.json')
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return
        
    with open(json_path) as f:
        data = json.load(f)
        
    roles = data.pop('roles', [])
    for k in ['modified', 'modified_by', 'creation', 'owner']:
        data.pop(k, None)
        
    data['name'] = 'smriti-cge'
    data['page_name'] = 'smriti-cge'
    
    if frappe.db.exists('Page', 'smriti-cge'):
        frappe.delete_doc('Page', 'smriti-cge', ignore_permissions=True, force=True)
        print("Deleted existing page: smriti-cge")
        
    doc = frappe.get_doc(data)
    for r in roles:
        doc.append('roles', r)
        
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("IMPORT SUCCESSFUL: smriti-cge page imported and registered.")
