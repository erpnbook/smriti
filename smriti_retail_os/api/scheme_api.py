# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/scheme_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/scheme_api.py
# @description: Whitelisted API endpoints for SMRITI Scheme Creator (Pricing Rules).
# @author: Antigravity AI
# @date: 2026-06-16
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def get_schemes(search_txt=None):
    """
    Fetches SMRITI active selling schemes (Pricing Rules).
    """
    filters = {"selling": 1, "disable": 0}
    if search_txt:
        filters["title"] = ["like", f"%{search_txt}%"]
        
    rules = frappe.get_all(
        "Pricing Rule",
        filters=filters,
        fields=["name", "title", "apply_on", "price_or_product_discount", "rate_or_discount", "discount_percentage", "discount_amount", "rate", "min_qty", "free_qty", "same_item", "free_item", "valid_from", "valid_upto", "company"],
        order_by="creation desc"
    )
    
    # Dynamic enrichment of applied links
    for r in rules:
        applied_to = ""
        try:
            doc = frappe.get_doc("Pricing Rule", r.name)
            if r.apply_on == "Item Code":
                if doc.get("items"):
                    applied_to = ", ".join([x.item_code for x in doc.items if x.item_code])
                elif getattr(doc, "item_code", None):
                    applied_to = doc.item_code
            elif r.apply_on == "Item Group":
                if doc.get("item_groups"):
                    applied_to = ", ".join([x.item_group for x in doc.item_groups if x.item_group])
                elif getattr(doc, "item_group", None):
                    applied_to = doc.item_group
            elif r.apply_on == "Brand":
                if doc.get("brands"):
                    applied_to = ", ".join([x.brand for x in doc.brands if x.brand])
                elif getattr(doc, "brand", None):
                    applied_to = doc.brand
        except Exception:
            pass
        r["applied_to"] = applied_to or "-"
        
    return rules

@frappe.whitelist()
def create_scheme(title, apply_on, applied_to, discount_type, value, valid_from=None, valid_upto=None, company=None,
                  min_qty=None, free_qty=None, same_item=None, free_item=None):
    """
    Creates a SMRITI Pricing Rule representing a retail scheme.
    """
    check_manager_permission()
    
    if not title or not title.strip():
        frappe.throw(_("Scheme Title is required."))
    if not applied_to or not applied_to.strip():
        frappe.throw(_("Applied Target Value is required."))
        
    company = company or frappe.defaults.get_user_default("company")
    if not company:
        # Fallback
        companies = frappe.get_all("Company", limit=1, pluck="name")
        company = companies[0] if companies else ""
        
    val = flt(value)
    
    if discount_type == "Buy X Get Y Free":
        price_or_product_discount = "Product"
        min_q = flt(min_qty or value or 1)
        free_q = flt(free_qty or 1)
        same_it = 1 if same_item in (1, "1", True) else 0
        free_it = free_item if not same_it else None
        
        doc = frappe.get_doc({
            "doctype": "Pricing Rule",
            "title": title.strip(),
            "apply_on": apply_on,
            "selling": 1,
            "buying": 0,
            "company": company,
            "valid_from": valid_from,
            "valid_upto": valid_upto,
            "price_or_product_discount": "Product",
            "min_qty": min_q,
            "same_item": same_it,
            "free_item": free_it,
            "free_qty": free_q,
            "free_item_uom": frappe.db.get_value("Item", free_it or applied_to, "stock_uom") or "Nos"
        })
    else:
        rate_or_discount = "Discount Percentage" if discount_type == "Percentage" else ("Discount Amount" if discount_type == "Amount" else "Rate")
        doc = frappe.get_doc({
            "doctype": "Pricing Rule",
            "title": title.strip(),
            "apply_on": apply_on,
            "selling": 1,
            "buying": 0,
            "company": company,
            "valid_from": valid_from,
            "valid_upto": valid_upto,
            "price_or_product_discount": "Price",
            "rate_or_discount": rate_or_discount,
            "discount_percentage": val if discount_type == "Percentage" else 0.0,
            "discount_amount": val if discount_type == "Amount" else 0.0,
            "rate": val if discount_type == "Flat Rate" else 0.0
        })
    
    _set_pricing_rule_links(doc, apply_on, applied_to.strip())
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def update_scheme(name, title, apply_on, applied_to, discount_type, value, valid_from=None, valid_upto=None,
                  min_qty=None, free_qty=None, same_item=None, free_item=None):
    """
    Updates an existing SMRITI Pricing Rule details.
    """
    check_manager_permission()
    
    if not name or not frappe.db.exists("Pricing Rule", name):
        frappe.throw(_("Scheme '{0}' does not exist.").format(name))
        
    val = flt(value)
    doc = frappe.get_doc("Pricing Rule", name)
    doc.title = title.strip()
    doc.apply_on = apply_on
    doc.valid_from = valid_from
    doc.valid_upto = valid_upto
    
    if discount_type == "Buy X Get Y Free":
        doc.price_or_product_discount = "Product"
        doc.min_qty = flt(min_qty or value or 1)
        doc.same_item = 1 if same_item in (1, "1", True) else 0
        doc.free_qty = flt(free_qty or 1)
        if doc.same_item:
            doc.free_item = None
        else:
            doc.free_item = free_item
            doc.free_item_uom = frappe.db.get_value("Item", free_item, "stock_uom") or "Nos"
            
        doc.rate_or_discount = None
        doc.discount_percentage = 0.0
        doc.discount_amount = 0.0
        doc.rate = 0.0
    else:
        doc.price_or_product_discount = "Price"
        rate_or_discount = "Discount Percentage" if discount_type == "Percentage" else ("Discount Amount" if discount_type == "Amount" else "Rate")
        doc.rate_or_discount = rate_or_discount
        doc.discount_percentage = val if discount_type == "Percentage" else 0.0
        doc.discount_amount = val if discount_type == "Amount" else 0.0
        doc.rate = val if discount_type == "Flat Rate" else 0.0
        doc.min_qty = 0.0
        doc.same_item = 0
        doc.free_item = None
        doc.free_qty = 0.0
        doc.free_item_uom = None
        
    _set_pricing_rule_links(doc, apply_on, applied_to.strip())
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def delete_scheme(name):
    """
    Disables/Deletes a Pricing Rule scheme.
    """
    check_manager_permission()
    
    if not name or not frappe.db.exists("Pricing Rule", name):
        frappe.throw(_("Scheme '{0}' does not exist.").format(name))
        
    # Standard practice is to delete the rule
    frappe.delete_doc("Pricing Rule", name, ignore_permissions=True)
    return True

def _set_pricing_rule_links(doc, apply_on, applied_to):
    """
    Helper to set the linked fields/child tables in Pricing Rule
    supporting different ERPNbook versions.
    """
    meta = frappe.get_meta("Pricing Rule")
    
    # 1. Clear existing link structures
    for ct in ["items", "item_groups", "brands"]:
        if any(f.fieldname == ct for f in meta.fields):
            doc.set(ct, [])
            
    # 2. Populate based on apply_on
    if apply_on == "Item Code":
        if any(f.fieldname == "items" for f in meta.fields):
            doc.append("items", {"item_code": applied_to})
        elif hasattr(doc, "item_code"):
            doc.item_code = applied_to
            
    elif apply_on == "Item Group":
        if any(f.fieldname == "item_groups" for f in meta.fields):
            doc.append("item_groups", {"item_group": applied_to})
        elif hasattr(doc, "item_group"):
            doc.item_group = applied_to
            
    elif apply_on == "Brand":
        if any(f.fieldname == "brands" for f in meta.fields):
            doc.append("brands", {"brand": applied_to})
        elif hasattr(doc, "brand"):
            doc.brand = applied_to

def check_manager_permission():
    """
    Ensures the user has SMRITI Store Manager, System Manager, or Administrator role.
    """
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: You do not have permissions to manage Schemes."), frappe.PermissionError)
