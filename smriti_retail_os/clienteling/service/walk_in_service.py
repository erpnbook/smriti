# -*- coding: utf-8 -*-
#
# @file: walk_in_service.py
# @description: Walk-In Intelligence state machine transitions and Daily Analytics compilation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, today, getdate, now_datetime
from frappe import _

def record_walk_in(store, executive=None, customer=None, phone=None, status="Registered", duration=0):
    """
    Creates a new walk-in log entry.
    """
    doc = frappe.new_doc("SMRITI Walk In Visit")
    doc.visit_date = today()
    doc.visit_time = frappe.utils.nowtime()
    doc.store = store
    doc.executive = executive
    doc.customer = customer
    doc.customer_phone = phone
    doc.status = status
    doc.engagement_duration = duration
    
    doc.flags.ignore_permissions = True
    doc.save()
    return doc

def update_walk_in_status(visit_id, status, reason=None, invoice_type=None, invoice_id=None, duration=None):
    """
    Executes valid state transitions inside the walk-in state machine.
    """
    doc = frappe.get_doc("SMRITI Walk In Visit", visit_id)
    valid_states = ["Registered", "Browsing", "Assisted", "Converted", "Exited"]
    
    if status not in valid_states:
        frappe.throw(_("Invalid walk-in funnel status: {0}").format(status))
        
    doc.status = status
    if status == "Exited":
        doc.reason_for_no_purchase = reason
    elif status == "Converted":
        if invoice_type == "Sales Invoice":
            doc.sales_invoice = invoice_id
        elif invoice_type == "POS Invoice":
            doc.pos_invoice = invoice_id
            
    if duration is not None:
        doc.engagement_duration = duration
        
    doc.flags.ignore_permissions = True
    doc.save()
    return doc

def aggregate_daily_analytics(date_str=None):
    """
    Compiles daily walk-in analytics per store.
    SMRITI Walk In Analytics is a derived snapshot and is never manually edited.
    """
    target_date = date_str or today()
    
    # 1. Clear existing summaries for the target date
    frappe.db.delete("SMRITI Walk In Analytics", {"date": target_date})
    
    # 2. Get active warehouses (stores)
    stores = frappe.db.get_all("Warehouse", filters={"is_group": 0})
    for s in stores:
        store = s.name
        
        visits = frappe.db.get_all(
            "SMRITI Walk In Visit",
            filters={"visit_date": target_date, "store": store},
            fields=["status", "engagement_duration", "sales_invoice", "pos_invoice"]
        )
        if not visits:
            continue
            
        total_walk_ins = len(visits)
        conversions = len([v for v in visits if v.status == "Converted"])
        
        # Calculate Conversion Rate
        conv_rate = (conversions / total_walk_ins * 100.0) if total_walk_ins > 0 else 0.0
        
        # Calculate average engagement
        avg_dur = sum(flt(v.engagement_duration) for v in visits) / total_walk_ins
        
        # Calculate revenue generated from walk-in conversions
        revenue = 0.0
        for v in visits:
            if v.status == "Converted":
                if v.sales_invoice:
                    revenue += flt(frappe.db.get_value("Sales Invoice", v.sales_invoice, "grand_total"))
                elif v.pos_invoice:
                    revenue += flt(frappe.db.get_value("POS Invoice", v.pos_invoice, "grand_total"))
                    
        analytics = frappe.new_doc("SMRITI Walk In Analytics")
        analytics.date = target_date
        analytics.store = store
        analytics.total_walk_ins = total_walk_ins
        analytics.total_conversions = conversions
        analytics.conversion_rate = conv_rate
        analytics.total_revenue = revenue
        analytics.avg_engagement_minutes = avg_dur
        
        analytics.flags.ignore_permissions = True
        analytics.save()
