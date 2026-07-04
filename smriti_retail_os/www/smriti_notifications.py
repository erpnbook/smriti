# -*- coding: utf-8 -*-
"""
smriti_retail_os/www/smriti_notifications.py
Auth check and context generation for SMRITI Notification Center.
Author: Jawahar R. Mallah
"""
import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)
    context.no_cache = 1
    context.cashier = frappe.session.user
    
    # Retrieve unread notification count
    from smriti_retail_os.notification_studio.service.notification_service import get_unread_count
    context.unread_count = get_unread_count(frappe.session.user)
    return context
