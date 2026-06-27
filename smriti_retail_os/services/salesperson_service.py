# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/salesperson_service.py
# @description: Decoupled salesperson resolution, commission structure, and active list service.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: MIT
#

import frappe
from frappe import _

@frappe.whitelist()
def get_active_salespersons():
    """
    Returns list of active Sales Persons from ERPNext database to populate UI quick-chips and selectors.
    """
    return frappe.get_all(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name", "sales_person_name", "commission_rate"],
        order_by="sales_person_name asc",
        limit=50
    )

def get_company_salesperson_settings(company=None):
    """
    Retrieves salesperson settings from SMRITI Company Settings.
    """
    if not company:
        company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

    settings = {
        "enable_bill_sales_person": 1,
        "enable_item_sales_person": 1,
        "allow_item_sales_person_override": 1
    }

    if not company:
        return settings

    try:
        doc = frappe.get_doc("SMRITI Company Settings", company)
        settings["enable_bill_sales_person"] = frappe.utils.cint(doc.custom_enable_bill_sales_person)
        settings["enable_item_sales_person"] = frappe.utils.cint(doc.custom_enable_item_sales_person)
        settings["allow_item_sales_person_override"] = frappe.utils.cint(doc.custom_allow_item_sales_person_override)
    except frappe.DoesNotExistError:
        pass

    return settings

def resolve_item_salespersons(items, header_salesperson=None, company=None):
    """
    Resolves salesperson attribution for each item row based on override and inheritance rules.
    """
    settings = get_company_salesperson_settings(company)
    resolved_items = []

    for item in items:
        item_salesperson = item.get("custom_sales_person")
        
        # If item-level salesperson is not set, or override is disabled, inherit from bill-level salesperson
        if settings.get("enable_bill_sales_person") and header_salesperson:
            if not item_salesperson or not settings.get("allow_item_sales_person_override"):
                item_salesperson = header_salesperson

        # If item salesperson is disabled globally, strip it
        if not settings.get("enable_item_sales_person"):
            item_salesperson = None

        item["custom_sales_person"] = item_salesperson
        resolved_items.append(item)

    return resolved_items
