# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/category_api.py
# @description: SMRITI Category Api — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe    # frappe.whitelist, frappe.throw, frappe.get_roles, frappe.session, frappe.delete_doc — framework utilities
from frappe import _  # i18n only
from smriti_retail_os import smriti

@frappe.whitelist()
def get_categories(search_txt=None):
    """
    Fetches the list of standard Item Groups (Categories).
    """
    filters = {}
    if search_txt:
        filters = {"name": ["like", f"%{search_txt}%"]}
    
    categories = smriti.db.get_list(
        "Category",
        filters=filters,
        fields=["name", "parent_item_group", "is_group"],
        order_by="name asc"
    )
    return categories

def _ensure_root_item_group():
    if not smriti.db.exists("Category", "All Item Groups"):
        root = smriti.documents.new("Category")
        root.update({
            "item_group_name": "All Item Groups",
            "is_group": 1,
            "parent_item_group": ""
        })
        root.insert(ignore_permissions=True)
        smriti.db.commit()


@frappe.whitelist()
def create_category(category_name, parent_category=None, is_group=0):
    """
    Creates a new standard Item Group (Category).
    Enforces SMRITI Store Manager or System Manager role check.
    """
    check_manager_permission()
    _ensure_root_item_group()
    
    if not category_name or not category_name.strip():
        frappe.throw(_("Category Name is required."))
        
    category_name = category_name.strip()
    if smriti.db.exists("Category", category_name):
        frappe.throw(_("Category '{0}' already exists.").format(category_name))

    parent_category = parent_category or "All Item Groups"
    if parent_category != "All Item Groups" and not smriti.db.exists("Category", parent_category):
        parent_category = "All Item Groups"

    doc = smriti.documents.new("Category")
    doc.update({
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
    
    if not category_name or not smriti.db.exists("Category", category_name):
        frappe.throw(_("Category '{0}' does not exist.").format(category_name))

    if parent_category and not smriti.db.exists("Category", parent_category):
        frappe.throw(_("Parent Category '{0}' does not exist.").format(parent_category))

    if parent_category == category_name:
        frappe.throw(_("A category cannot be its own parent."))

    doc = smriti.documents.get("Category", category_name)
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
    
    if not category_name or not smriti.db.exists("Category", category_name):
        frappe.throw(_("Category '{0}' does not exist.").format(category_name))

    if category_name == "All Item Groups":
        frappe.throw(_("The root category 'All Item Groups' cannot be deleted."))

    if smriti.db.exists("Category", {"parent_item_group": category_name}):
        frappe.throw(_("Cannot delete category '{0}' because it contains sub-categories.").format(category_name))

    if smriti.db.exists("Product", {"item_group": category_name}):
        frappe.throw(_("Cannot delete category '{0}' because it is linked to active items.").format(category_name))
        
    # reviewed-ignore-permissions: catalog group deletion, validated by product manager
    smriti.documents.delete("Item Group", category_name, ignore_permissions=True)
    return True

def check_manager_permission():
    """
    Ensures the user has SMRITI Store Manager, System Manager, or Administrator role.
    """
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: You do not have permissions to manage Categories."), frappe.PermissionError)
