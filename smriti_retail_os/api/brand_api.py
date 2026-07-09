# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/brand_api.py
# @description: SMRITI Brand Api — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/api/brand_api.py
# @description: Whitelisted API endpoints for Brand Master management.
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

@frappe.whitelist()
def get_brands(search_txt=None):
    """
    Fetches the list of standard Brands.
    """
    filters = {}
    if search_txt:
        filters = {"name": ["like", f"%{search_txt}%"]}
    
    brands = smriti.db.get_list(
        "Brand",
        filters=filters,
        fields=["name", "brand", "description", "image"],
        order_by="name asc"
    )
    return brands

@frappe.whitelist()
def create_brand(brand_name, description=None):
    """
    Creates a new standard Brand.
    Enforces SMRITI Store Manager or System Manager role check.
    """
    check_manager_permission()
    
    if not brand_name or not brand_name.strip():
        frappe.throw(_("Brand Name is required."))
        
    brand_name = brand_name.strip()
    if smriti.db.exists("Brand", brand_name):
        frappe.throw(_("Brand '{0}' already exists.").format(brand_name))
        
    doc = smriti.documents.new("Brand")
    doc.update({
        "brand": brand_name,
        "description": description
    })
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def update_brand(brand_name, description=None):
    """
    Updates an existing standard Brand's description.
    Enforces role check.
    """
    check_manager_permission()
    
    if not brand_name or not smriti.db.exists("Brand", brand_name):
        frappe.throw(_("Brand '{0}' does not exist.").format(brand_name))
        
    doc = smriti.documents.get("Brand", brand_name)
    doc.description = description
    # reviewed-ignore-permissions: catalog brand updates, validated by product manager
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def delete_brand(brand_name):
    """
    Deletes a standard Brand record.
    Checks for any item references before deletion.
    """
    check_manager_permission()
    
    if not brand_name or not smriti.db.exists("Brand", brand_name):
        frappe.throw(_("Brand '{0}' does not exist.").format(brand_name))
        
    # Check if any Item references this brand
    if smriti.db.exists("Item", {"brand": brand_name}):
        frappe.throw(_("Cannot delete brand '{0}' because it is linked to active items.").format(brand_name))
        
    # reviewed-ignore-permissions: catalog brand deletion, validated by product manager
    smriti.documents.delete("Brand", brand_name, ignore_permissions=True)
    return True

def check_manager_permission():
    """
    Ensures the user has SMRITI Store Manager, System Manager, or Administrator role.
    """
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: You do not have permissions to manage Brands."), frappe.PermissionError)
