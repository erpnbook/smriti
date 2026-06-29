# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-pos-profiles.py
# @description: Standalone SMRITI POS Profiles Page Controller - Auth & context.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.8.6
# @sprint: 3C — POS Profile Custom Manager
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication Required: Please log in to access SMRITI POS Profiles."), frappe.AuthenticationError)

    roles = frappe.get_roles(frappe.session.user)
    allowed = {"System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: Only Administrators and System Managers can access this page."), frappe.PermissionError)

    # Standalone SMRITI styling setup
    context.web_include_js  = []
    context.web_include_css = []
    context.no_header       = True
    context.no_breadcrumbs  = True
    context.no_cache        = True
    context.show_sidebar    = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""
    context.user = frappe.session.user
    context.show_platform_admin = "System Manager" in roles or frappe.session.user == "Administrator"

    return context
