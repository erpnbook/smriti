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
    context.csrf_token = frappe.sessions.get_csrf_token()

    return context
