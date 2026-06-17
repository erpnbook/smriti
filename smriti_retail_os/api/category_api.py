# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/category_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/category_api.py
# @description: Whitelisted API endpoints for Category (Item Group) management.
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

@frappe.whitelist()
def get_categories(search_txt=None):
    """
    Fetches the list of standard Item Groups (Categories).
    """
    filters = {}
    if search_txt:
        filters = {"name": ["like", f"%{search_txt}%"]}
    
    categories = frappe.get_all(
        "Item Group",
        filters=filters,
        fields=["name", "parent_item_group", "is_group"],
        order_by="name asc"
    )
    return categories

@frappe.whitelist()
def create_category(category_name, parent_category=None, is_group=0):
    """
    Creates a new standard Item Group (Category).
    Enforces SMRITI Store Manager or System Manager role check.
    """
    check_manager_permission()
    
    if not category_name or not category_name.strip():
        frappe.throw(_("Category Name is required."))
        
    category_name = category_name.strip()
    if frappe.db.exists("Item Group", category_name):
        frappe.throw(_("Category '{0}' already exists.").format(category_name))
        
    parent_category = parent_category or "All Item Groups"
    if parent_category != "All Item Groups" and not frappe.db.exists("Item Group", parent_category):
        # Fallback to All Item Groups if specified parent doesn't exist
        parent_category = "All Item Groups"
        
    doc = frappe.get_doc({
        "doctype": "Item Group",
        "item_group_name": category_name,
        "parent_item_group": parent_category,
        "is_group": int(is_group)
    })
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def update_category(category_name, parent_category=None):
    """
    Updates an existing Item Group's parent.
    Enforces role check.
    """
    check_manager_permission()
    
    if not category_name or not frappe.db.exists("Item Group", category_name):
        frappe.throw(_("Category '{0}' does not exist.").format(category_name))
        
    if parent_category and not frappe.db.exists("Item Group", parent_category):
        frappe.throw(_("Parent Category '{0}' does not exist.").format(parent_category))
        
    if parent_category == category_name:
        frappe.throw(_("A category cannot be its own parent."))
        
    doc = frappe.get_doc("Item Group", category_name)
    if parent_category:
        doc.parent_item_group = parent_category
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def delete_category(category_name):
    """
    Deletes an Item Group.
    Checks for active child groups or items.
    """
    check_manager_permission()
    
    if not category_name or not frappe.db.exists("Item Group", category_name):
        frappe.throw(_("Category '{0}' does not exist.").format(category_name))
        
    if category_name == "All Item Groups":
        frappe.throw(_("The root category 'All Item Groups' cannot be deleted."))
        
    # Check for child groups
    if frappe.db.exists("Item Group", {"parent_item_group": category_name}):
        frappe.throw(_("Cannot delete category '{0}' because it contains sub-categories.").format(category_name))
        
    # Check if any Item references this category
    if frappe.db.exists("Item", {"item_group": category_name}):
        frappe.throw(_("Cannot delete category '{0}' because it is linked to active items.").format(category_name))
        
    frappe.delete_doc("Item Group", category_name, ignore_permissions=True)
    return True

def check_manager_permission():
    """
    Ensures the user has SMRITI Store Manager, System Manager, or Administrator role.
    """
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: You do not have permissions to manage Categories."), frappe.PermissionError)
