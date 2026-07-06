# -*- coding: utf-8 -*-
#
# @file: clienteling_api.py
# @description: Whitelisted backend API layer for SMRITI Clienteling.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
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
        
    profile_dict = profile.as_dict()
    
    # Attach SMRITI Customer Intelligence Graph details for explainability transparency
    intel_doc = frappe.db.get_value(
        "SMRITI Customer Intelligence Graph",
        customer,
        [
            "churn_formula_id", "churn_formula_version",
            "vip_formula_id", "vip_formula_version",
            "affinity_formula_id", "affinity_formula_version",
            "intelligence_graph_version"
        ],
        as_dict=True
    )
    if intel_doc:
        profile_dict.update(intel_doc)
        
    # Also fetch the actual expressions of these formulas from Formula Registry
    for key, f_id in [("churn_expr", "TST-CHURN"), ("vip_expr", "TST-VIP"), ("affinity_expr", "TST-AFFINITY")]:
        expr = None
        if f_id:
            expr = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": f_id}, "formula_expression")
        profile_dict[key] = expr
        
    return profile_dict

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
    
    # reviewed-ignore-permissions: clienteling telemetry, records user-customer contact log
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

@frappe.whitelist()
def log_explain_audit(metric, customer, formula_id=None, session_id=None, source_screen=None):
    """
    Inserts a SMRITI Explain Audit Event record when a user explains a metric.
    """
    if not metric or not customer:
        frappe.throw(_("Metric and Customer are required to log an explain audit event."))
        
    doc = frappe.new_doc("SMRITI Explain Audit Event")
    doc.user = frappe.session.user
    doc.metric = metric
    doc.customer = customer
    
    # Resolve formula ref link if formula_id (e.g. TST-VIP) is provided
    if formula_id:
        doc.formula_id = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": formula_id}, "name")
        
    doc.timestamp = frappe.utils.now_datetime()
    doc.session_id = session_id
    doc.source_screen = source_screen
    
    # reviewed-ignore-permissions: clienteling explainability telemetry log
    doc.flags.ignore_permissions = True
    doc.insert()
    return doc.as_dict()
