# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/configure.py
# @description: Page controller for the SMRITI Master Configuration Portal.
#               Restricts access to Store Manager and System Manager roles.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
#

import frappe
from frappe import _
from smriti_retail_os.company_api import get_active_company, get_company_settings

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the configuration portal."), frappe.AuthenticationError)

    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: Only Store Managers can access this page."), frappe.PermissionError)

    context.no_cache = 1
    context.title = "SMRITI Config Portal"
    context.csrf_token = frappe.sessions.get_csrf_token()
    
    active_company = get_active_company()
    context.company = active_company or ""
    context.company_settings = get_company_settings(active_company) if active_company else {}

    # Fetch reference options for settings dropdowns
    context.companies = frappe.get_all("Company", fields=["name", "company_name"])
    
    # Filter warehouses by active company if possible, or fetch all non-group warehouses
    warehouse_filters = {"is_group": 0, "disabled": 0}
    if active_company:
        warehouse_filters["company"] = active_company
    context.warehouses = frappe.get_all("Warehouse", filters=warehouse_filters, fields=["name", "warehouse_name"])
    
    # Filter POS profiles by active company if possible
    pos_filters = {"disabled": 0}
    if active_company:
        pos_filters["company"] = active_company
    context.pos_profiles = frappe.get_all("POS Profile", filters=pos_filters, fields=["name"])
    
    context.customers = frappe.get_all("Customer", filters={"disabled": 0}, fields=["name", "customer_name"])
    
    # Sales Taxes and Charges Templates (can filter by company)
    tax_filters = {}
    if active_company:
        tax_filters["company"] = active_company
    context.tax_templates = frappe.get_all("Sales Taxes and Charges Template", filters=tax_filters, fields=["name"])

    return context
