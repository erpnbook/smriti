# -*- coding: utf-8 -*-
# @file: smriti_retail_os/www/index.py
# @description: Root route handler — server-side redirect based on login state and role.

import frappe

no_cache = 1

def get_context(context):
    user = frappe.session.user

    if not user or user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    roles = frappe.get_roles(user)

    companies = frappe.get_all("Company", limit=1)
    if not companies:
        frappe.local.flags.redirect_location = "/setup-wizard"
        raise frappe.Redirect

    if "SMRITI Cashier" in roles:
        frappe.local.flags.redirect_location = "/billing"
        raise frappe.Redirect

    frappe.local.flags.redirect_location = "/app"
    raise frappe.Redirect
