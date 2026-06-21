# -*- coding: utf-8 -*-
#
# @file: clienteling_api.py
# @description: Whitelisted backend API layer for SMRITI Clienteling.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.2.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from smriti_retail_os.clienteling.service import clienteling_service, walk_in_service

@frappe.whitelist()
def get_customer_profile(customer):
    """
    Returns the materialized SMRITI Customer Profile snapshot for POS overlays.
    If it's marked dirty, it returns the current data but schedules recalculation.
    """
    if not customer:
        frappe.throw(_("Customer is required."))
        
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} not found.").format(customer))
        
    # If the profile doesn't exist, build it synchronously for the first lookup
    if not frappe.db.exists("SMRITI Customer Profile", customer):
        clienteling_service.regenerate_customer_data(customer)
        
    profile = frappe.get_doc("SMRITI Customer Profile", customer)
    
    # If it is dirty, trigger background refresh
    if profile.is_dirty:
        clienteling_service.mark_dirty(customer, source="API Get Profile", source_document="Manual")
        
    return profile.as_dict()

@frappe.whitelist()
def log_customer_interaction(customer, interaction_type, employee, interaction_outcome, store, channel, details=None):
    """
    Exposes SMRITI Customer Interaction creation.
    """
    if not customer or not interaction_type or not employee or not interaction_outcome or not store or not channel:
        frappe.throw(_("Missing mandatory fields for logging customer interaction."))
        
    doc = frappe.new_doc("SMRITI Customer Interaction")
    doc.customer = customer
    doc.interaction_date = frappe.utils.today()
    doc.interaction_time = frappe.utils.nowtime()
    doc.interaction_type = interaction_type
    doc.employee = employee
    doc.interaction_outcome = interaction_outcome
    doc.store = store
    doc.channel = channel
    doc.details = details
    
    doc.flags.ignore_permissions = True
    doc.insert()
    return doc.as_dict()

@frappe.whitelist()
def register_walk_in(store, phone=None, customer=None, status="Registered"):
    """
    Logs store walk-in.
    """
    visit = walk_in_service.record_walk_in(
        store=store,
        customer=customer,
        phone=phone,
        status=status
    )
    return visit.as_dict()

@frappe.whitelist()
def update_walk_in_visit(visit_id, status, reason=None, invoice_type=None, invoice_id=None, duration=None):
    """
    Updates walk-in visit status.
    """
    visit = walk_in_service.update_walk_in_status(
        visit_id=visit_id,
        status=status,
        reason=reason,
        invoice_type=invoice_type,
        invoice_id=invoice_id,
        duration=duration
    )
    return visit.as_dict()

@frappe.whitelist()
def get_store_walk_in_analytics(store, date=None):
    """
    Compiles and retrieves derived Walk-In Analytics snapshot for store.
    """
    target_date = date or frappe.utils.today()
    walk_in_service.aggregate_daily_analytics(target_date)
    
    analytics = frappe.get_all(
        "SMRITI Walk In Analytics",
        filters={"store": store, "date": target_date},
        fields=["total_walk_ins", "total_conversions", "conversion_rate", "total_revenue", "avg_engagement_minutes"]
    )
    
    if analytics:
        return analytics[0]
    return {
        "total_walk_ins": 0,
        "total_conversions": 0,
        "conversion_rate": 0.0,
        "total_revenue": 0.0,
        "avg_engagement_minutes": 0.0
    }
