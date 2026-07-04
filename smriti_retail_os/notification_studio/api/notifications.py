# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/api/notifications.py
Whitelisted API endpoints for SMRITI Notification Center.
Author: Jawahar R. Mallah
"""
import frappe
from smriti_retail_os.notification_studio.service.notification_service import (
    get_notifications as _get_notifications,
    get_unread_count as _get_unread_count,
    mark_as_read as _mark_as_read,
    mark_all_read as _mark_all_read
)

@frappe.whitelist()
def get_notifications(notif_type="all", limit=50, page=1, user=None):
    """
    Get paginated notifications for a user.
    If not specified or not Administrator, defaults to the current session user.
    """
    session_user = frappe.session.user
    if not user or session_user != "Administrator":
        user = session_user
        
    return _get_notifications(user, notif_type=notif_type, limit=int(limit), page=int(page))

@frappe.whitelist()
def get_unread_count():
    """Get unread notification count for the current session user."""
    user = frappe.session.user
    count = _get_unread_count(user)
    return {"count": count}

@frappe.whitelist()
def mark_as_read(name):
    """Mark a notification as read."""
    user = frappe.session.user
    return _mark_as_read(name, user)

@frappe.whitelist()
def mark_all_read():
    """Mark all notifications as read."""
    user = frappe.session.user
    return _mark_all_read(user)
