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
    context.company = (
        frappe.defaults.get_user_default("company")
        or frappe.db.get_value("Company", {}, "name")
        or ""
    )
    return context
