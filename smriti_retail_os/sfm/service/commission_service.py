# -*- coding: utf-8 -*-
#
# @file: commission_service.py
# @description: Core service layer logic for SMRITI Sales Force Commission (SFC).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, now_datetime
import calendar

def resolve_commission_rule(employee, company, posting_date):
    """
    Finds the active SMRITI Commission Rule for the employee and company on the posting date.
    
    Precedence Rules:
    1. Employee Specific Rule: Checked first. If multiple employee-specific rules match,
       the one with the highest priority (descending) is used.
    2. Highest Priority Rule: Checked within the matching category.
    3. Global Rule: Used if no Employee Specific Rule is found (matched from rules where employee is empty).
       Sorted by priority (descending).
    4. No Match = 0 Commission: Returns None if no rules match.
    """
    today = getdate(posting_date or nowdate())
    
    rules = frappe.get_all(
        "SMRITI Commission Rule",
        filters={
            "company": company,
            "is_active": 1
        },
        fields=[
            "name", "employee", "commission_rate", "min_revenue_threshold",
            "effective_from", "effective_to", "priority"
        ]
    )

    valid_rules = []
    for r in rules:
        eff_from = getdate(r.effective_from) if r.effective_from else None
        eff_to = getdate(r.effective_to) if r.effective_to else None
        
        if eff_from and today < eff_from:
            continue
        if eff_to and today > eff_to:
            continue
        valid_rules.append(r)

    if not valid_rules:
        return None

    # Separate employee overrides vs global rules
    overrides = [r for r in valid_rules if r.employee == employee]
    global_rules = [r for r in valid_rules if not r.employee]

    if overrides:
        overrides.sort(key=lambda x: (x.priority, x.commission_rate), reverse=True)
        return overrides[0]
    elif global_rules:
        global_rules.sort(key=lambda x: (x.priority, x.commission_rate), reverse=True)
        return global_rules[0]

    return None

def process_attribution_ledger_insert(doc, method=None):
    """
    Hook called on SMRITI Attribution Ledger after_insert.
    Generates a SMRITI Commission Event and SMRITI Commission Ledger entry.
    Supports standard attribution and negative reversals.
    """
    enable_sfc = frappe.db.get_single_value("SMRITI Commission Settings", "enable_sfc")
    if not enable_sfc:
        return

    auto_generate_events = frappe.db.get_single_value("SMRITI Commission Settings", "auto_generate_events")
    if not auto_generate_events:
        return

    # If it's a reversal (revenue_credit < 0 or reversal_reference is set)
    if flt(doc.revenue_credit) < 0 or doc.reversal_reference:
        orig_ledger_name = doc.reversal_reference
        orig_event = None
        orig_rate = 0.0
        rule_name = None
        
        if orig_ledger_name:
            orig_event = frappe.db.get_value(
                "SMRITI Commission Event", 
                {"attribution_ledger": orig_ledger_name, "event_status": "Processed"}, 
                ["name", "commission_rate", "commission_rule"], 
                as_dict=True
            )
        
        if orig_event:
            orig_rate = flt(orig_event.commission_rate)
            rule_name = orig_event.commission_rule
        else:
            rule = resolve_commission_rule(doc.employee, doc.company, doc.posting_date)
            orig_rate = flt(rule.commission_rate) if rule else 0.0
            rule_name = rule.name if rule else None

        comm_amount = flt(doc.revenue_credit) * (orig_rate / 100.0)

        # Create Reversal Event
        evt = frappe.new_doc("SMRITI Commission Event")
        evt.employee = doc.employee
        evt.invoice_reference = doc.invoice_reference
        evt.attribution_ledger = doc.name
        evt.attributed_revenue = flt(doc.revenue_credit)
        evt.commission_rule = rule_name
        evt.commission_rate = orig_rate
        evt.commission_amount = comm_amount
        evt.event_status = "Reversed"
        evt.posting_date = doc.posting_date
        evt.company = doc.company
        evt.insert(ignore_permissions=True)

        # Find original commission ledger entry to mark as Reversed
        orig_led_name = None
        if orig_event:
            orig_led_name = frappe.db.get_value("SMRITI Commission Ledger", {"commission_event": orig_event.name}, "name")
            if orig_led_name:
                frappe.db.set_value("SMRITI Commission Ledger", orig_led_name, "ledger_status", "Reversed")

        # Create Reversal Ledger entry
        led = frappe.new_doc("SMRITI Commission Ledger")
        led.employee = doc.employee
        led.commission_event = evt.name
        led.amount = comm_amount
        led.ledger_status = "Reversed"
        led.reversal_reference = orig_led_name
        led.posting_date = doc.posting_date
        led.posting_time = doc.posting_time
        led.company = doc.company
        led.insert(ignore_permissions=True)

    else:
        # Standard active insert
        rule = resolve_commission_rule(doc.employee, doc.company, doc.posting_date)
        rate = flt(rule.commission_rate) if rule else 0.0
        comm_amount = flt(doc.revenue_credit) * (rate / 100.0)

        evt = frappe.new_doc("SMRITI Commission Event")
        evt.employee = doc.employee
        evt.invoice_reference = doc.invoice_reference
        evt.attribution_ledger = doc.name
        evt.attributed_revenue = flt(doc.revenue_credit)
        evt.commission_rule = rule.name if rule else None
        evt.commission_rate = rate
        evt.commission_amount = comm_amount
        evt.event_status = "Processed"
        evt.posting_date = doc.posting_date
        evt.company = doc.company
        evt.insert(ignore_permissions=True)

        led = frappe.new_doc("SMRITI Commission Ledger")
        led.employee = doc.employee
        led.commission_event = evt.name
        led.amount = comm_amount
        led.ledger_status = "Active"
        led.posting_date = doc.posting_date
        led.posting_time = doc.posting_time
        led.company = doc.company
        led.insert(ignore_permissions=True)

def generate_monthly_settlement(employee, company, fiscal_year, month):
    """
    Computes monthly commission payout details for the given employee.
    Checks rules threshold and returns settlement draft data structure.
    """
    from smriti_retail_os.sfm.service.target_service import get_month_date_range
    start_date, end_date = get_month_date_range(fiscal_year, month)

    # 1. Calculate active attributed revenue from SMRITI Attribution Ledger
    revenue_res = frappe.db.sql("""
        select sum(revenue_credit) from `tabSMRITI Attribution Ledger`
        where employee = %s and company = %s and ledger_status = 'Active'
          and posting_date >= %s and posting_date <= %s
    """, (employee, company, start_date, end_date))
    total_revenue = flt(revenue_res[0][0]) if revenue_res and revenue_res[0][0] else 0.0

    # 2. Resolve active Commission Rule (as of end of month)
    rule = resolve_commission_rule(employee, company, end_date)
    threshold = flt(rule.min_revenue_threshold) if rule else 0.0

    # 3. Sum active Commission Ledger entries
    gross_comm = 0.0
    if total_revenue >= threshold:
        comm_res = frappe.db.sql("""
            select sum(amount) from `tabSMRITI Commission Ledger`
            where employee = %s and company = %s and ledger_status = 'Active'
              and posting_date >= %s and posting_date <= %s
        """, (employee, company, start_date, end_date))
        gross_comm = flt(comm_res[0][0]) if comm_res and comm_res[0][0] else 0.0

    return {
        "employee": employee,
        "company": company,
        "fiscal_year": fiscal_year,
        "month": month,
        "settlement_from_date": start_date,
        "settlement_to_date": end_date,
        "gross_commission": gross_comm,
        "net_commission": gross_comm,
        "settled_commission_amount": gross_comm,
        "status": "Draft",
        "adjustments": []
    }

def run_monthly_settlements(company, fiscal_year, month):
    """
    Finds all employees with active ledger records for the period and creates draft monthly settlements.
    """
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
    
    generated = []
    for emp in employees:
        if frappe.db.exists("SMRITI Commission Settlement", {"employee": emp, "company": company, "fiscal_year": fiscal_year, "month": month}):
            continue
            
        settle_data = generate_monthly_settlement(emp, company, fiscal_year, month)
        doc = frappe.get_doc({
            "doctype": "SMRITI Commission Settlement",
            "employee": settle_data["employee"],
            "company": settle_data["company"],
            "fiscal_year": settle_data["fiscal_year"],
            "month": settle_data["month"],
            "settlement_from_date": settle_data["settlement_from_date"],
            "settlement_to_date": settle_data["settlement_to_date"],
            "gross_commission": settle_data["gross_commission"],
            "net_commission": settle_data["net_commission"],
            "settled_commission_amount": settle_data["settled_commission_amount"],
            "status": "Draft"
        })
        doc.insert(ignore_permissions=True)
        generated.append(doc.name)

    frappe.db.commit()
    return generated
