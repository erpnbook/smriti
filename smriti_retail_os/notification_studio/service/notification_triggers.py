# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/service/notification_triggers.py
Doc events triggers for SMRITI Notification Studio.
Author: Jawahar R. Mallah
"""
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.notification_studio.service.notification_service import create_notification

ROLE_STORE_MANAGER = "SMRITI Store Manager"
ROLE_SYSTEM_MANAGER = "System Manager"

def get_users_by_role(role_name):
    users = smriti.db.get_list("Has Role", filters={"role": role_name}, pluck="parent")
    users = list(set(users))
    if not users:
        users = ["Administrator"]
    return users

def trigger_purchase_approval(doc, method):
    """
    Triggered on Purchase Order submit (on_submit).
    Sends notifications to System Managers.
    """
    if doc.doctype != "Purchase Order":
        return
    
    users = get_users_by_role(ROLE_SYSTEM_MANAGER)
    title = f"Purchase Order Approved: {doc.name}"
    message = f"Purchase Order {doc.name} for Supplier {doc.supplier} has been approved/submitted."
    
    for user in users:
        create_notification(
            user=user,
            notif_type="purchase_approval",
            title=title,
            message=message,
            reference_doctype="Purchase Order",
            reference_name=doc.name,
            action_url="/smriti-purchase#orders"
        )

def trigger_grn_received(doc, method):
    """
    Triggered on Purchase Receipt submit (on_submit).
    Sends notifications to Store Managers.
    """
    if doc.doctype != "Purchase Receipt":
        return
        
    users = get_users_by_role(ROLE_STORE_MANAGER)
    title = f"GRN Received: {doc.name}"
    message = f"Goods Receipt Note {doc.name} has been received for Supplier {doc.supplier}."
    
    for user in users:
        create_notification(
            user=user,
            notif_type="grn_received",
            title=title,
            message=message,
            reference_doctype="Purchase Receipt",
            reference_name=doc.name,
            action_url="/smriti-purchase#grn"
        )

def trigger_sales_notification(doc, method):
    """
    Triggered on Sales Invoice or POS Invoice submit (on_submit).
    Sends notifications to Store Managers.
    """
    if doc.doctype not in ["Sales Invoice", "POS Invoice"]:
        return
        
    users = get_users_by_role(ROLE_STORE_MANAGER)
    doc_label = "POS Invoice" if doc.is_pos else "Sales Invoice"
    title = f"New {doc_label} Submitted: {doc.name}"
    message = f"{doc_label} {doc.name} of amount {doc.grand_total} has been submitted."
    
    for user in users:
        create_notification(
            user=user,
            notif_type="sales",
            title=title,
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            action_url="/billing" if doc.is_pos else "/sales-invoices"
        )
