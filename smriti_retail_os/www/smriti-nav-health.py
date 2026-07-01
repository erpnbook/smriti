# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-nav-health.py
# @description: SMRITI Navigation Health Dashboard — Controller
# @author: Jawahar R. Mallah
#

import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access this page.", frappe.AuthenticationError)

    context.no_cache = True
    context.page_title = "Navigation Health Dashboard"
    return context
