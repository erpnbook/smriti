# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_appearance.py
# @description: SMRITI Appearance & Theme Control Center — Page Controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 2.2.0
#

import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access SMRITI Appearance & Theme Settings."), frappe.AuthenticationError)

    # Cleanse default web templates to enforce standalone SMRITI presentation
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
    roles = frappe.get_roles(frappe.session.user)
    context.is_admin = 1 if (frappe.session.user == "Administrator" or "Administrator" in roles) else 0

    from smriti_retail_os.api.theme_api import get_installed_themes
    context.installed_themes = get_installed_themes()
    context.title = "SMRITI Appearance & Theme Management"

    return context
