# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/setup_wizard.py
# @description: Page controller for the SMRITI Retail OS Setup Wizard.
#               Validates user permissions before serving the setup layout.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-02
#

import frappe
from frappe import _
from smriti_retail_os.setup_wizard_api import verify_setup_wizard_access

no_cache = 1

def get_context(context):
    """
    Checks permissions and loads page title context.
    """
    try:
        verify_setup_wizard_access()
    except (frappe.AuthenticationError, frappe.PermissionError) as e:
        # Redirect guests to login page if authentication is required
        if frappe.session.user == "Guest":
            frappe.local.flags.redirect_to = "/login"
            raise frappe.Redirect
        # Otherwise, throw error on desk
        frappe.throw(e.title or str(e), frappe.PermissionError)

    context.no_cache = 1
    context.title = _("SMRITI Setup Wizard")
    csrf_token = None
    if getattr(frappe.local, "session_obj", None):
        try:
            csrf_token = frappe.sessions.get_csrf_token()
        except Exception:
            pass
    if not csrf_token and hasattr(frappe.local, "session") and getattr(frappe.local.session, "data", None):
        csrf_token = frappe.local.session.data.get("csrf_token")
    context.csrf_token = csrf_token or ""

    return context
