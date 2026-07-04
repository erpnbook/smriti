# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/service/scheduled_checks.py
Daily scheduled background checks for SMRITI Notification Studio.
Author: Jawahar R. Mallah
"""
import frappe
from frappe.utils import today
from smriti_retail_os.notification_studio.service.notification_service import create_notification
from smriti_retail_os.notification_studio.service.notification_triggers import get_users_by_role, ROLE_STORE_MANAGER, ROLE_SYSTEM_MANAGER
from smriti_retail_os.notification_studio.repository.notification_repository import NotificationRepository

def _already_notified_today(user, notif_type, reference_doctype, reference_name):
    """
    Dedup safety check: returns True if a notification has already been created today
    for this user, type, and reference key.
    """
    count = frappe.db.count("SMRITI Notification Log", {
        "for_user": user,
        "notif_type": notif_type,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "creation": (">=", today())
    })
    return count > 0

def run_low_stock_checks():
    """
    Daily check for low stock levels.
    Compares Bin.actual_qty vs Item.safety_stock or Item Reorder.warehouse_reorder_level.
    """
    try:
        # Check 1: safety_stock at item level via Repository
        safety_stock_items = NotificationRepository.get_safety_stock_violations()

        # Check 2: warehouse_reorder_level in Item Reorder table via Repository
        reorder_items = NotificationRepository.get_reorder_level_violations()

        low_stock_list = safety_stock_items + reorder_items

        if not low_stock_list:
            return

        users = get_users_by_role(ROLE_STORE_MANAGER)
        for bin_info in low_stock_list:
            item_code = bin_info["item_code"]
            warehouse = bin_info["warehouse"]
            qty = bin_info["actual_qty"]
            limit = bin_info["limit_qty"]
            
            title = f"Low Stock Alert: {item_code}"
            message = f"Item {item_code} in Warehouse {warehouse} has actual quantity {qty}, which is below reorder limit ({limit})."
            
            for user in users:
                ref_key = f"{item_code}:{warehouse}"
                if not _already_notified_today(user, "low_stock", "Item", ref_key):
                    create_notification(
                        user=user,
                        notif_type="low_stock",
                        title=title,
                        message=message,
                        reference_doctype="Item",
                        reference_name=ref_key,
                        action_url="/inventory"
                    )
    except Exception as e:
        frappe.log_error(f"SMRITI Scheduled Low Stock Check Error: {e}", "scheduled_checks")

def run_due_invoice_checks():
    """
    Daily check for overdue Sales Invoices.
    """
    try:
        # Fetch Sales Invoices that are unpaid and past due date
        overdue_invoices = frappe.get_all("Sales Invoice", filters={
            "docstatus": 1,
            "outstanding_amount": (">", 0),
            "due_date": ("<", today())
        }, fields=["name", "due_date", "outstanding_amount", "customer"])

        if not overdue_invoices:
            return

        users = get_users_by_role(ROLE_SYSTEM_MANAGER)
        for inv in overdue_invoices:
            title = f"Overdue Invoice Alert: {inv.name}"
            message = f"Invoice {inv.name} for Customer {inv.customer} has an outstanding amount of {inv.outstanding_amount} and was due on {inv.due_date}."
            
            for user in users:
                if not _already_notified_today(user, "invoice_due", "Sales Invoice", inv.name):
                    create_notification(
                        user=user,
                        notif_type="invoice_due",
                        title=title,
                        message=message,
                        reference_doctype="Sales Invoice",
                        reference_name=inv.name,
                        action_url="/sales-invoices"
                    )
    except Exception as e:
        frappe.log_error(f"SMRITI Scheduled Overdue Invoice Check Error: {e}", "scheduled_checks")
