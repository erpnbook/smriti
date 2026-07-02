# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/api/smriti_notifications_api.py
Whitelisted API endpoints for SMRITI Notification Center.
Author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
"""
import frappe
from smriti_retail_os.notification_studio.service.notification_service import (
    get_notifications, get_unread_count, mark_as_read, mark_all_read
)


@frappe.whitelist()
def get_my_notifications(notif_type="all", limit=50, page=1):
    """Get paginated notifications for the current user."""
    user = frappe.session.user
    return get_notifications(user, notif_type=notif_type, limit=int(limit), page=int(page))


@frappe.whitelist()
def get_unread_badge():
    """Get unread notification count for sidebar bell badge."""
    user = frappe.session.user
    count = get_unread_count(user)
    return {"count": count, "has_unread": count > 0}


@frappe.whitelist()
def mark_notification_read(name):
    """Mark a single notification as read."""
    user = frappe.session.user
    return mark_as_read(name, user)


@frappe.whitelist()
def mark_all_notifications_read():
    """Mark all notifications as read for current user."""
    user = frappe.session.user
    return mark_all_read(user)


@frappe.whitelist()
def get_notification_summary():
    """
    Get notification summary for sidebar dropdown (last 8 + unread count).
    Called on page load to hydrate the bell badge.
    """
    user = frappe.session.user
    count = get_unread_count(user)
    recent = get_notifications(user, limit=8, page=1)
    return {
        "unread_count": count,
        "notifications": recent.get("items", [])
    }


@frappe.whitelist()
def delete_notification(name):
    """Soft delete (dismiss) a notification."""
    user = frappe.session.user
    try:
        doc = frappe.get_doc("SMRITI Notification Log", name)
        if doc.for_user == user:
            frappe.delete_doc("SMRITI Notification Log", name, ignore_permissions=True)
            frappe.db.commit()
        return {"status": "ok"}
    except Exception as e:
        frappe.log_error(str(e), "delete_notification")
        return {"status": "error", "message": str(e)}
