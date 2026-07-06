# -*- coding: utf-8 -*-
#
# @file: sfc_api.py
# @description: Whitelisted APIs for SMRITI Sales Force Commission (SFC).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt
from smriti_retail_os.sfm.service.commission_service import (
    run_monthly_settlements,
    generate_monthly_settlement
)

@frappe.whitelist()
def run_monthly_calculation(company, fiscal_year, month):
    """
    Triggers bulk calculation of monthly commission settlements.
    Creates draft SMRITI Commission Settlement entries.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to run monthly commission calculations."), frappe.PermissionError)

    return run_monthly_settlements(company, fiscal_year, month)

@frappe.whitelist()
def get_monthly_commissions(company, fiscal_year, month):
    """
    Calculates monthly commission data for all active employees for preview.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to view monthly commission calculations."), frappe.PermissionError)

    from smriti_retail_os.sfm.service.target_service import get_month_date_range
    start_date, end_date = get_month_date_range(fiscal_year, month)

    employees_attr = frappe.db.sql_list("""
        select distinct employee from `tabSMRITI Attribution Ledger`
        where company = %s and ledger_status = 'Active'
          and posting_date >= %s and posting_date <= %s
    """, (company, start_date, end_date))

    employees_comm = frappe.db.sql_list("""
        select distinct employee from `tabSMRITI Commission Ledger`
        where company = %s and ledger_status = 'Active'
          and posting_date >= %s and posting_date <= %s
    """, (company, start_date, end_date))

    employees = list(set(employees_attr + employees_comm))

    summary = []
    for emp in employees:
        emp_name = frappe.db.get_value("Employee", emp, "employee_name") or emp
        
        settlement_name = frappe.db.get_value(
            "SMRITI Commission Settlement",
            {"employee": emp, "company": company, "fiscal_year": fiscal_year, "month": month},
            "name"
        )
        
        if settlement_name:
            doc = frappe.get_doc("SMRITI Commission Settlement", settlement_name)
            gross = flt(doc.gross_commission)
            net = flt(doc.net_commission)
            status = doc.status
            adjustments = [
                {
                    "reason": row.reason,
                    "amount": flt(row.amount),
                    "remarks": row.remarks,
                    "approved_by": row.approved_by,
                    "approved_on": str(row.approved_on)
                } for row in doc.adjustments
            ]
        else:
            settle_data = generate_monthly_settlement(emp, company, fiscal_year, month)
            gross = flt(settle_data["gross_commission"])
            net = flt(settle_data["net_commission"])
            status = "Draft"
            adjustments = []

        revenue_res = frappe.db.sql("""
            select sum(revenue_credit) from `tabSMRITI Attribution Ledger`
            where employee = %s and company = %s and ledger_status = 'Active'
              and posting_date >= %s and posting_date <= %s
        """, (emp, company, start_date, end_date))
        attributed_rev = flt(revenue_res[0][0]) if revenue_res and revenue_res[0][0] else 0.0

        summary.append({
            "employee": emp,
            "employee_name": emp_name,
            "attributed_revenue": attributed_rev,
            "gross_commission": gross,
            "net_commission": net,
            "status": status,
            "settlement_name": settlement_name or "",
            "adjustments": adjustments
        })

    return summary


# ── P4: Service-layer write methods (replaces frappe.client.insert from HTML) ──

@frappe.whitelist()
def save_commission_settlement(
    employee, company, fiscal_year, month,
    status, gross_commission, net_commission,
    adjustments=None, settlement_name=None
):
    """
    Create or update a SMRITI Commission Settlement.
    Replaces direct frappe.client.insert / frappe.client.update from smriti-sfc.html.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to save commission settlements."), frappe.PermissionError)

    import json
    adjs = json.loads(adjustments) if isinstance(adjustments, str) else (adjustments or [])

    if settlement_name and frappe.db.exists("SMRITI Commission Settlement", settlement_name):
        doc = frappe.get_doc("SMRITI Commission Settlement", settlement_name)
        doc.status            = status
        doc.gross_commission  = flt(gross_commission)
        doc.net_commission    = flt(net_commission)
        doc.adjustments       = []
        for adj in adjs:
            doc.append("adjustments", adj)
        doc.save(ignore_permissions=False)
    else:
        doc = frappe.get_doc({
            "doctype": "SMRITI Commission Settlement",
            "employee": employee,
            "company": company,
            "fiscal_year": fiscal_year,
            "month": month,
            "status": status,
            "gross_commission": flt(gross_commission),
            "net_commission": flt(net_commission),
        })
        for adj in adjs:
            doc.append("adjustments", adj)
        doc.insert(ignore_permissions=False)

    frappe.db.commit()
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def save_commission_rule(
    rule_name=None, company=None, employee=None,
    rule_type=None, base_rate=None, threshold_amount=None,
    accelerator_rate=None, effective_from=None, effective_to=None,
    is_active=1
):
    """
    Create or update a SMRITI Commission Rule.
    Replaces direct frappe.client.insert / frappe.client.update from smriti-sfc.html.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager"]):
        frappe.throw(_("Not authorized to save commission rules."), frappe.PermissionError)

    fields = {
        "company": company,
        "employee": employee,
        "rule_type": rule_type,
        "base_rate": flt(base_rate),
        "threshold_amount": flt(threshold_amount),
        "accelerator_rate": flt(accelerator_rate),
        "effective_from": effective_from,
        "effective_to": effective_to,
        "is_active": int(is_active),
    }

    if rule_name and frappe.db.exists("SMRITI Commission Rule", rule_name):
        doc = frappe.get_doc("SMRITI Commission Rule", rule_name)
        doc.update(fields)
        doc.save(ignore_permissions=False)
    else:
        doc = frappe.get_doc({"doctype": "SMRITI Commission Rule", **fields})
        doc.insert(ignore_permissions=False)

    frappe.db.commit()
    return {"name": doc.name}
