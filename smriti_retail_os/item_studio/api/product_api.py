# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/item_studio/api/product_api.py
# @desc:    Whitelisted API boundaries for SMRITI Product Studio.
#           Interacts exclusively with ProductService.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.item_studio.service.product_service import ProductService
from smriti_retail_os.security_api import check_page_access


def _check_access():
    """Verifies that user is logged in and possesses Product Catalog access rights."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)
    check_page_access("products")


@frappe.whitelist()
def get_products(limit=200):
    """Retrieves list of active items for Catalog Grid."""
    _check_access()
    return ProductService.get_products(limit=limit)


@frappe.whitelist()
def get_product_detail(item_code):
    """Retrieves complete attributes of a product for the editor form."""
    _check_access()
    if not item_code:
        frappe.throw(_("Item Code parameter is required."))
    return ProductService.get_product_detail(item_code)


@frappe.whitelist()
def save_product(item_data, item_code=None):
    """Creates a new product or updates an existing one."""
    _check_access()
    if not item_data:
        frappe.throw(_("Product data is required."))
    
    # Run through service layer validation and logic
    return ProductService.save_product(item_data, item_code)


@frappe.whitelist()
def delete_product(item_code):
    """Disables the specified product."""
    _check_access()
    if not item_code:
        frappe.throw(_("Item Code parameter is required."))
    return ProductService.delete_product(item_code)


@frappe.whitelist()
def get_catalog_metadata():
    """Retrieves list of brands and item groups for filters."""
    _check_access()
    brands = [b.name for b in frappe.get_list("Brand", fields=["name"], limit_page_length=100)]
    categories = [c.name for c in frappe.get_list("Item Group", fields=["name"], limit_page_length=100)]
    return {
        "brands": brands,
        "categories": categories
    }
