# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-analytics-studio.py
# @description: Auth guard + context for SMRITI Analytics Studio page
# @author: Jawahar R. Mallah
# @version: 1.0.0
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti


def get_context(context):
    """
    Authentication guard and context injection for SMRITI Analytics Studio.
    Follows SMRITI Rule 7: every new page must have auth + context.
    """
    # Enforce authentication
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/smriti-analytics-studio"
        raise frappe.Redirect

    # Page meta
    context.title = "SMRITI Analytics Studio"
    context.no_cache = 1
    context.show_sidebar = False

    # User display info
    context.user_fullname = frappe.get_cached_value(
        "User", frappe.session.user, "full_name"
    ) or frappe.session.user

    # Company (for filter defaults)
    context.default_company = frappe.defaults.get_user_default("company") or \
        smriti.db.get_single("Global Defaults", "default_company") or ""

    # Available currencies
    context.currency_symbol = smriti.db.get_single("System Settings", "currency") or "INR"

    # CSRF token — required by smriti_ui_resolver.js frappe.call() shim
    # The shim reads window.csrf_token (global.csrf_token) on L71
    try:
        context.csrf_token = frappe.local.session.data.csrf_token or ""
    except Exception as e:
        context.csrf_token = f"ERROR: {str(e)}"

    return context
