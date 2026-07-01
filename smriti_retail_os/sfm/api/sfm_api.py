# -*- coding: utf-8 -*-
#
# @file: sfm_api.py
# @description: Whitelisted API endpoints for SMRITI SFM dashboard.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt
from smriti_retail_os.sfm.service.target_service import get_month_date_range, get_employee_target_vs_achievement

@frappe.whitelist()
def get_sfm_leaderboard(company, fiscal_year, month, store=None):
    """
    Returns employee performance ranking based on revenue achievements for a given month and fiscal year.
    Optionally filters by store.
    """
    # Resolve date range
    start_date, end_date = get_month_date_range(fiscal_year, month)
    
    filters = {
        "company": company,
        "date": ["between", [start_date, end_date]]
    }
    if store:
        filters["store"] = store
        
    snapshots = frappe.get_all(
        "SMRITI Sales KPI Snapshot",
        filters=filters,
        fields=["employee", "revenue", "transactions", "customers"]
    )
    
    # Aggregate in memory
    agg = {}
    for s in snapshots:
        emp = s.employee
        if emp not in agg:
            agg[emp] = {"employee": emp, "revenue": 0.0, "transactions": 0, "customers": 0, "employee_name": ""}
        agg[emp]["revenue"] += flt(s.revenue)
        agg[emp]["transactions"] += int(s.transactions)
        agg[emp]["customers"] += int(s.customers)
        
    # Look up employee names
    for emp in agg.keys():
        agg[emp]["employee_name"] = frappe.db.get_value("Employee", emp, "employee_name") or emp
        
    # Sort descending by revenue
    leaderboard = sorted(agg.values(), key=lambda x: x["revenue"], reverse=True)
    
    # Add rank
    for idx, entry in enumerate(leaderboard):
        entry["rank"] = idx + 1
        
    return leaderboard

@frappe.whitelist()
def get_employee_summary(employee, fiscal_year, month, company):
    """
    Returns complete target, achievement, and KPI totals for a specific employee.
    """
    # Get target vs achievement
    res = get_employee_target_vs_achievement(employee, fiscal_year, month, company)
    
    # Resolve date range
    start_date, end_date = get_month_date_range(fiscal_year, month)
    
    # Fetch total transactions and customers from snapshot
    totals = frappe.db.get_value(
        "SMRITI Sales KPI Snapshot",
        {
            "employee": employee,
            "company": company,
            "date": ["between", [start_date, end_date]]
        },
        ["sum(transactions) as total_transactions", "sum(customers) as total_customers"],
        as_dict=True
    )
    
    res["total_transactions"] = int(totals.total_transactions) if totals and totals.total_transactions else 0
    res["total_customers"] = int(totals.total_customers) if totals and totals.total_customers else 0
    res["employee_name"] = frappe.db.get_value("Employee", employee, "employee_name") or employee
    
    return res

@frappe.whitelist()
def get_store_performance_center(company, fiscal_year, month, store=None):
    """
    Returns aggregated store metrics (total target, total achievement, top performer).
    """
    start_date, end_date = get_month_date_range(fiscal_year, month)
    
    # Query targets in this company
    target_filters = {"company": company, "fiscal_year": fiscal_year, "month": month}
    targets = frappe.get_all("SMRITI Sales Target", filters=target_filters, fields=["employee", "target_amount"])
    
    # If store is provided, we filter targets to only employees in that store (by their snapshots or employee branch)
    # Let's filter targets
    total_target = 0.0
    for t in targets:
        if store:
            # Check if this employee has any snapshot in this store for the month
            has_snapshot = frappe.db.exists("SMRITI Sales KPI Snapshot", {
                "employee": t.employee,
                "store": store,
                "date": ["between", [start_date, end_date]]
            })
            if not has_snapshot:
                continue
        total_target += flt(t.target_amount)
        
    # Achievements
    achievement_filters = {
        "company": company,
        "date": ["between", [start_date, end_date]]
    }
    if store:
        achievement_filters["store"] = store
        
    totals = frappe.db.get_value(
        "SMRITI Sales KPI Snapshot",
        achievement_filters,
        ["sum(revenue) as total_revenue", "sum(transactions) as total_transactions"],
        as_dict=True
    )
    
    total_revenue = flt(totals.total_revenue) if totals and totals.total_revenue else 0.0
    total_transactions = int(totals.total_transactions) if totals and totals.total_transactions else 0
    
    # Top performer
    leaderboard = get_sfm_leaderboard(company, fiscal_year, month, store)
    top_performer = leaderboard[0] if leaderboard else None
    
    return {
        "total_target": total_target,
        "total_achievement": total_revenue,
        "achievement_percentage": (total_revenue / total_target * 100.0) if total_target > 0 else 0.0,
        "total_transactions": total_transactions,
        "top_performer": top_performer
    }


# ── P4: Service-layer write/read methods (replaces frappe.client.* from smriti-sfm.html) ──

@frappe.whitelist()
def save_sales_target(
    target_name=None, employee=None, company=None,
    fiscal_year=None, month=None, target_amount=None, store=None
):
    """
    Create or update a SMRITI Sales Target.
    Replaces frappe.client.insert / frappe.client.update from smriti-sfm.html.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to manage sales targets."), frappe.PermissionError)

    fields = {
        "employee": employee,
        "company": company,
        "fiscal_year": fiscal_year,
        "month": month,
        "target_amount": flt(target_amount),
        "store": store,
    }

    if target_name and frappe.db.exists("SMRITI Sales Target", target_name):
        doc = frappe.get_doc("SMRITI Sales Target", target_name)
        doc.update(fields)
        doc.save(ignore_permissions=False)
    else:
        doc = frappe.get_doc({"doctype": "SMRITI Sales Target", **fields})
        doc.insert(ignore_permissions=False)

    frappe.db.commit()
    return {"name": doc.name}


@frappe.whitelist()
def save_customer_ownership(
    ownership_name=None, customer=None, employee=None,
    company=None, ownership_type=None, effective_from=None,
    effective_to=None, store=None, is_active=1
):
    """
    Create or update a SMRITI Customer Ownership record.
    Replaces frappe.client.insert / frappe.client.update from smriti-sfm.html.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to manage customer ownership."), frappe.PermissionError)

    fields = {
        "customer": customer,
        "employee": employee,
        "company": company,
        "ownership_type": ownership_type,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "store": store,
        "is_active": int(is_active),
    }

    if ownership_name and frappe.db.exists("SMRITI Customer Ownership", ownership_name):
        doc = frappe.get_doc("SMRITI Customer Ownership", ownership_name)
        doc.update(fields)
        doc.save(ignore_permissions=False)
    else:
        doc = frappe.get_doc({"doctype": "SMRITI Customer Ownership", **fields})
        doc.insert(ignore_permissions=False)

    frappe.db.commit()
    return {"name": doc.name}


@frappe.whitelist()
def get_sfm_settings():
    """Read SMRITI SFM Settings — replaces frappe.client.get_value from smriti-sfm.html."""
    doc = frappe.get_single("SMRITI SFM Settings")
    return {
        "enable_sfm": doc.enable_sfm,
        "ownership_precedence": doc.ownership_precedence,
        "primary_split_pct": flt(doc.primary_split_pct),
        "secondary_split_pct": flt(doc.secondary_split_pct),
        "walkin_employee": doc.walkin_employee,
    }


@frappe.whitelist()
def save_sfm_settings(
    enable_sfm=1, ownership_precedence=0,
    primary_split_pct=70, secondary_split_pct=30,
    walkin_employee=None
):
    """
    Save SMRITI SFM Settings.
    Replaces frappe.client.save from smriti-sfm.html.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to modify SFM settings."), frappe.PermissionError)

    doc = frappe.get_single("SMRITI SFM Settings")
    doc.enable_sfm           = int(enable_sfm)
    doc.ownership_precedence = int(ownership_precedence)
    doc.primary_split_pct    = flt(primary_split_pct)
    doc.secondary_split_pct  = flt(secondary_split_pct)
    if walkin_employee is not None:
        doc.walkin_employee  = walkin_employee
    doc.save(ignore_permissions=False)
    frappe.db.commit()
    return {"saved": True}


@frappe.whitelist()
def get_attribution_ledger(company=None, limit=100):
    """
    Return SMRITI Attribution Ledger entries.
    Replaces frappe.client.get_list from smriti-sfm.html.
    """
    filters = {}
    if company:
        filters["company"] = company

    rows = frappe.get_list(
        "SMRITI Attribution Ledger",
        filters=filters,
        fields=["name", "posting_date", "posting_time", "invoice_reference",
                "customer", "employee", "ownership_type", "credit_percentage",
                "revenue_credit", "store", "ledger_status"],
        order_by="posting_date desc, posting_time desc",
        limit_page_length=int(limit),
    )
    return rows
