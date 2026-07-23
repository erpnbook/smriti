# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/api/notifications.py
Whitelisted API endpoints for SMRITI Notification Center.
Author: Jawahar R. Mallah
"""
import frappe
from smriti_retail_os import smriti
from smriti_retail_os.notification_studio.service.notification_service import (
    get_notifications as _get_notifications,
    get_unread_count as _get_unread_count,
    mark_as_read as _mark_as_read,
    mark_all_read as _mark_all_read
)
from smriti_retail_os.notification_studio.repository.notification_repository import NotificationRepository


@frappe.whitelist(allow_guest=True)
def get_notifications(notif_type="all", limit=50, page=1, user=None):
    """
    Get paginated notifications for a user.
    If not specified or not Administrator, defaults to the current session user.
    """
    session_user = frappe.session.user
    if not user or session_user != "Administrator":
        user = session_user
    if user == "Guest":
        return {"items": [], "total": 0, "page": 1, "has_more": False}
        
    return _get_notifications(user, notif_type=notif_type, limit=int(limit), page=int(page))

@frappe.whitelist(allow_guest=True)
def get_unread_count():
    """Get unread notification count for the current session user."""
    user = frappe.session.user
    if user == "Guest":
        return {"count": 0}
    count = _get_unread_count(user)
    return {"count": count}

@frappe.whitelist(allow_guest=True)
def get_my_notifications(notif_type="all", limit=50, page=1):
    """Get paginated notifications for the current session user."""
    user = frappe.session.user
    if user == "Guest":
        return {"items": [], "total": 0, "page": 1, "has_more": False}
    return _get_notifications(user, notif_type=notif_type, limit=int(limit), page=int(page))

@frappe.whitelist(allow_guest=True)
def get_unread_badge():
    """Get unread notification count for sidebar bell badge."""
    user = frappe.session.user
    if user == "Guest":
        return {"count": 0, "has_unread": False}
    count = _get_unread_count(user)
    return {"count": count, "has_unread": count > 0}

@frappe.whitelist(allow_guest=True)
def mark_notification_read(name):
    """Mark a single notification as read."""
    user = frappe.session.user
    if user == "Guest":
        return {"status": "ok"}
    return _mark_as_read(name, user)

@frappe.whitelist(allow_guest=True)
def mark_all_notifications_read():
    """Mark all notifications as read for current user."""
    user = frappe.session.user
    if user == "Guest":
        return {"status": "ok"}
    return _mark_all_read(user)

@frappe.whitelist(allow_guest=True)
def get_notification_summary():
    """Get notification summary for sidebar dropdown (last 8 + unread count)."""
    user = frappe.session.user
    if user == "Guest":
        return {"unread_count": 0, "notifications": []}
    count = _get_unread_count(user)
    recent = _get_notifications(user, limit=8, page=1)
    return {
        "unread_count": count,
        "notifications": recent.get("items", [])
    }

@frappe.whitelist()
def delete_notification(name):
    """Soft delete (dismiss) a notification."""
    user = frappe.session.user
    try:
        doc = NotificationRepository.get_doc("SMRITI Notification Log", name)
        if doc.for_user == user:
            # reviewed-ignore-permissions: gated by user ownership validation
            NotificationRepository.delete_doc("SMRITI Notification Log", name, ignore_permissions=True)
            NotificationRepository.commit()
        return {"status": "ok"}
    except Exception as e:
        smriti.errors.log_error(str(e), "delete_notification")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def mark_as_read(name):
    """Mark a notification as read (alias for compatibility)."""
    user = frappe.session.user
    if user == "Guest":
        return {"status": "ok"}
    return _mark_as_read(name, user)

@frappe.whitelist(allow_guest=True)
def mark_all_read():
    """Mark all notifications as read (alias for compatibility)."""
    user = frappe.session.user
    if user == "Guest":
        return {"status": "ok"}
    return _mark_all_read(user)
