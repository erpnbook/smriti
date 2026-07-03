# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-platform-admin.py
# @description: Python controller for the SMRITI Platform Admin page.
#               Provides trial activation, lead pipeline management, and
#               account provisioning dashboard.
#               Access: Administrator only.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @sprint: 3A — Platform Admin: Trial Activation & Account Provisioning
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe

no_cache = 1
title = "SMRITI Platform Admin"


def get_context(context):
    """
    Sets up rendering context for the SMRITI Platform Admin page.

    Access policy:
        - Guest         → redirect to /login
        - Administrator → full access
        - Any other     → PermissionError (403)
    """
    user = frappe.session.user

    # Redirect unauthenticated users
    if user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Strictly Administrator-only
    if user != "Administrator":
        frappe.throw(
            "Access Denied: Platform Admin is restricted to Administrator only.",
            frappe.PermissionError
        )

    # Strip ALL Frappe web includes to render SMRITI UI cleanly
    context.web_include_js  = []
    context.web_include_css = []

    context.no_header      = True
    context.no_breadcrumbs = True
    context.no_cache       = True
    context.show_sidebar   = False
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
    context.current_user = user

    # Initial dashboard data (client will also fetch via API)
    try:
        from smriti_retail_os.api.trial_activation_api import get_activation_dashboard
        context.dashboard_data = get_activation_dashboard()
    except Exception:
        context.dashboard_data = {}

    return context
