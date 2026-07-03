# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-uie.py
# @description: SMRITI UIE Integration Center controller.
# @author: Jawahar R. Mallah
#

import frappe

no_cache = 1
title = "Integration Center — SMRITI"

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    from smriti_retail_os.security_api import check_page_access
    try:
        check_page_access("smriti-uie")
    except frappe.PermissionError:
        frappe.local.flags.redirect_location = "/smriti-home"
        raise frappe.Redirect

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

    return context
