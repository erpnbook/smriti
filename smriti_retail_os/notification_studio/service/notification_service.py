# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/service/notification_service.py
SMRITI Notification Service — business logic for creating and managing notifications.
Author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
"""
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import now_datetime


def create_notification(user, notif_type, title, message, reference_doctype=None, reference_name=None, action_url=None):
    """
    Create a SMRITI Notification Log entry and push real-time event.
    notif_type: purchase_approval | grn_received | low_stock |
                invoice_due | system | user | sales
    """
    try:
        doc = smriti.documents.new("NotificationLog")
        doc.update({
            "for_user": user,
            "notif_type": notif_type,
            "title": title,
            "message": message,
            "reference_doctype": reference_doctype or "",
            "reference_name": reference_name or "",
            "action_url": action_url or "",
            "is_read": 0,
            "created_at": now_datetime()
        })
        doc.insert(ignore_permissions=True)
        smriti.db.commit()

        # Push real-time to user
        smriti.realtime.publish(
            event="smriti_notification",
            message={
                "name": doc.name,
                "notif_type": notif_type,
                "title": title,
                "message": message,
                "action_url": action_url or "",
                "created_at": str(doc.created_at)
            },
            user=user
        )
        return doc.name
    except Exception as e:
        smriti.errors.log_error(f"SMRITI Notification Error: {e}", "notification_service")
        return None


def get_unread_count(user):
    """Return count of unread notifications for the given user."""
    try:
        return smriti.db.count("SMRITI Notification Log", {
            "for_user": user,
            "is_read": 0
        })
    except Exception:
        return 0


def mark_as_read(name, user):
    """Mark a single notification as read."""
    try:
        doc = smriti.documents.get("SMRITI Notification Log", name)
        if doc.for_user == user:
            doc.is_read = 1
            doc.save(ignore_permissions=True)
            smriti.db.commit()
        return True
    except Exception:
        return False


def mark_all_read(user):
    """Mark all notifications for the user as read."""
    try:
        smriti.db.set_value(
            "SMRITI Notification Log", {"for_user": user, "is_read": 0},
            "is_read", 1, update_modified=False
        )
        smriti.db.commit()
        return True
    except Exception:
        return False


def get_notifications(user, notif_type=None, limit=50, page=1):
    """
    Fetch paginated notifications for a user.
    Merges SMRITI Notification Log + Frappe Notification Log (read-only).
    """
    offset = (int(page) - 1) * int(limit)
    filters = {"for_user": user}
    if notif_type and notif_type != "all":
        filters["notif_type"] = notif_type

    try:
        rows = frappe.db.get_list(
            "SMRITI Notification Log",
            filters=filters,
            fields=["name", "notif_type", "title", "message",
                    "reference_doctype", "reference_name",
                    "action_url", "is_read", "created_at"],
            order_by="created_at desc",
            limit=int(limit),
            start=offset,
            ignore_permissions=True
        )
        total = smriti.db.count("SMRITI Notification Log", filters)
        return {"items": rows, "total": total, "page": int(page), "limit": int(limit)}
    except Exception as e:
        smriti.errors.log_error(f"get_notifications error: {e}", "notification_service")
        return {"items": [], "total": 0}
