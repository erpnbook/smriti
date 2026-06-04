# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/security.py
# @description: Page controller for SMRITI Security & Workflow Center.
#               Enforces access checks and initializes template context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/security.py
# @description: Page controller for SMRITI Security & Workflow Center.
#               Enforces access checks and initializes template context.
# @author: Antigravity <antigravity@google.com>
# @version: 1.0.0
# @license: MIT
#

import frappe
from frappe import _
from smriti_retail_os.security_api import _get_smriti_admin_email

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the SMRITI Security Center."), frappe.AuthenticationError)

    # Block Admin (Business Owner) from Security Center page
    _admin_email = _get_smriti_admin_email()
    if frappe.session.user in ("Admin", _admin_email):
        frappe.throw(_("Access Denied: The Admin (Business Owner) account is blocked from Security Center."), frappe.PermissionError)

    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: Only Store Managers and Administrators can access this page."), frappe.PermissionError)

    context.no_cache = 1
    context.title = "SMRITI Security Center"
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.user = frappe.session.user
    
    # Determine if user is Security Architect
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0

    # Fetch reference options for User Permission selectors
    context.companies = frappe.get_all(
        "Company",
        fields=["name", "company_name"],
        order_by="company_name asc"
    )
    
    context.warehouses = frappe.get_all(
        "Warehouse",
        filters={"is_group": 0, "disabled": 0},
        fields=["name", "warehouse_name"],
        order_by="warehouse_name asc"
    )

    # Fetch retail doctypes list that managers can assign permissions for
    context.retail_doctypes = ["Company", "Warehouse"]

    return context
