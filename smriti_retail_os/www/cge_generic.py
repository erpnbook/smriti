# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/cge_generic.py
# @description: SMRITI CGE Generic page controller — CGE UI context and auth.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/cge_generic.py
# @description: Dynamic page controller for SMRITI CGE v2 Module Explorers.
#               Enforces access checks and initializes target DocType context.
# @author: Antigravity AI
# @date: 2026-06-19
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access SMRITI CGE Explorers."), frappe.AuthenticationError)

    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: Only Store Managers and Administrators can access this page."), frappe.PermissionError)

    # 1. Resolve path to target DocType
    path = ""
    if hasattr(frappe.local, 'request') and hasattr(frappe.local.request, 'path'):
        path = frappe.local.request.path
    elif hasattr(frappe.local, 'path'):
        path = frappe.local.path
    elif hasattr(frappe, 'request') and hasattr(frappe.request, 'path'):
        path = frappe.request.path

    clean_path = "/" + path.strip("/") if path else ""

    path_to_doctype = {
        "/cge-benefit-instruments": "SMRITI Benefit Instrument",
        "/cge-membership-tiers": "SMRITI Membership Tier",
        "/cge-loyalty-programs": "SMRITI Loyalty Program",
        "/cge-campaigns": "SMRITI Campaign",
        "/cge-promotion-rules": "SMRITI Promotion Rule",
        "/cge-coupon-rules": "SMRITI Coupon Rule",
        "/cge-loyalty-rules": "SMRITI Loyalty Rule",
        "/cge-benefit-wallets": "SMRITI Benefit Wallet",
        "/cge-customer-benefit-profiles": "SMRITI Customer Benefit Profile",
        "/cge-benefit-resolution-policies": "SMRITI Benefit Resolution Policy",
        "/cge-liability-snapshots": "SMRITI Benefit Liability Snapshot",
        "/cge-benefit-audit-logs": "SMRITI Benefit Audit Log"
    }

    target_doctype = path_to_doctype.get(clean_path)
    if not target_doctype:
        # Fallback search matching substrings
        for p, dt in path_to_doctype.items():
            if p in clean_path:
                target_doctype = dt
                break

    if not target_doctype:
        frappe.throw(_("Invalid CGE Explorer route path: {0}").format(clean_path))

    # Cleanse default web templates to enforce standalone SMRITI presentation
    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    context.csrf_token = frappe.sessions.get_csrf_token()
    context.user = frappe.session.user
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0
    
    # Context variables for generic frontend
    context.target_doctype = target_doctype
    context.target_title = target_doctype.replace("SMRITI ", "")
    context.title = f"SMRITI {context.target_title}"

    return context
