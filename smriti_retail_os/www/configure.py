# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/configure.py
# @description: Page controller for the SMRITI Master Configuration Portal.
#               Restricts access to Store Manager and System Manager roles.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from smriti_retail_os.company_api import (
    get_active_company,
    get_company_settings,
)
from smriti_retail_os.security_api import check_page_access

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    try:
        check_page_access("configure")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Config Portal"
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    
    active_company = get_active_company()
    context.company = active_company or ""
    context.company_settings = get_company_settings(active_company) if active_company else {}

    # Fetch reference options for settings dropdowns
    context.companies = smriti.db.get_list("Company", fields=["name", "company_name"])
    
    # Filter warehouses by active company if possible, or fetch all non-group warehouses
    warehouse_filters = {"is_group": 0, "disabled": 0}
    if active_company:
        warehouse_filters["company"] = active_company
    context.warehouses = smriti.db.get_list("Warehouse", filters=warehouse_filters, fields=["name", "warehouse_name"])
    
    # Filter POS profiles by active company if possible
    pos_filters = {"disabled": 0}
    if active_company:
        pos_filters["company"] = active_company
    context.pos_profiles = smriti.db.get_list("POS Profile", filters=pos_filters, fields=["name"])
    
    context.customers = smriti.db.get_list("Customer", filters={"disabled": 0}, fields=["name", "customer_name"])
    
    # Sales Taxes and Charges Templates (can filter by company)
    tax_filters = {}
    if active_company:
        tax_filters["company"] = active_company
    context.tax_templates = smriti.db.get_list("Sales Taxes and Charges Template", filters=tax_filters, fields=["name"])

    return context
