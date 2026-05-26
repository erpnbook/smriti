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
    if frappe.db.exists('Page', page_name):
        doc = frappe.get_doc('Page', page_name)
        doc.update(data)
        doc.roles = []
        for r in roles:
            doc.append('roles', r)
        doc.save(ignore_permissions=True)
        print(f"UPDATED {page_name}")
    else:
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
frappe.db.commit()
print("DONE")
