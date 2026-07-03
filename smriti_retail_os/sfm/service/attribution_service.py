# -*- coding: utf-8 -*-
#
# @file: attribution_service.py
# @description: Service layer logic for SMRITI revenue attribution and ledger entry generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, nowtime

def resolve_store(company, warehouse):
    """
    Resolves SMRITI Store name from standard Warehouse.
    If no SMRITI Store is found with default_warehouse == warehouse,
    falls back to any store for the company, or creates a default SMRITI Store.
    """
    if not warehouse:
        # Find default warehouse for company from Company Settings
        warehouse = frappe.db.get_value("Company", company, "default_cash_warehouse")
        if not warehouse:
            warehouse = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")

    store_name = frappe.db.get_value("SMRITI Store", {"default_warehouse": warehouse, "company": company}, "name")
    if not store_name:
        store_name = frappe.db.get_value("SMRITI Store", {"company": company}, "name")
        if not store_name:
            # Create a default SMRITI Store dynamically
            store = frappe.new_doc("SMRITI Store")
            wh_part = warehouse.split(' - ')[0] if ' - ' in warehouse else warehouse
            clean_company = company.replace(" ", "_")
            store.store_name = f"Store - {wh_part} ({clean_company})"
            store.default_warehouse = warehouse
            store.company = company
            store.insert(ignore_permissions=True, ignore_if_duplicate=True)
            store_name = store.name or f"Store - {wh_part} ({clean_company})"
            
    return store_name

def update_kpi_snapshot(employee, store, date, company):
    """
    Aggregates daily sales performance from SMRITI Attribution Ledger to SMRITI Sales KPI Snapshot.
    Calculates net revenue, transaction count, and unique customers.
    """
    ledger_entries = frappe.get_all(
        "SMRITI Attribution Ledger",
        filters={
            "employee": employee,
            "store": store,
            "posting_date": date,
            "company": company
        },
        fields=["invoice_reference", "revenue_credit", "ledger_status", "customer"]
    )
    
    net_revenue = sum(
        flt(e.revenue_credit) for e in ledger_entries 
        if e.ledger_status == "Active"
    )
    
    # Transactions are unique invoices with ledger_status == "Active"
    active_txns = set(
        e.invoice_reference for e in ledger_entries 
        if e.ledger_status == "Active"
    )
    net_transactions = len(active_txns)
    
    # Unique customers from active transactions
    active_customers = set(
        e.customer for e in ledger_entries
        if e.ledger_status == "Active"
    )
    net_customers = len(active_customers)
    
    # Get or create the snapshot document
    snapshot_name = frappe.db.get_value(
        "SMRITI Sales KPI Snapshot",
        {"employee": employee, "store": store, "date": date, "company": company},
        "name"
    )
    
    if snapshot_name:
        snapshot = frappe.get_doc("SMRITI Sales KPI Snapshot", snapshot_name)
        snapshot.revenue = net_revenue
        snapshot.transactions = net_transactions
        snapshot.customers = net_customers
        snapshot.save(ignore_permissions=True)
    else:
        snapshot = frappe.new_doc("SMRITI Sales KPI Snapshot")
        snapshot.employee = employee
        snapshot.store = store
        snapshot.date = date
        snapshot.revenue = net_revenue
        snapshot.transactions = net_transactions
        snapshot.customers = net_customers
        snapshot.company = company
        snapshot.insert(ignore_permissions=True)

def process_invoice_submit(doc, method=None):
    """
    Attributions processing hook for POS Invoice or Sales Invoice submission.
    Creates attribution event and ledger records.
    """
    # 1. Create SMRITI Attribution Event log entry
    event = frappe.new_doc("SMRITI Attribution Event")
    event.invoice_reference = doc.name
    event.invoice_doctype = doc.doctype
    event.customer = doc.customer
    event.company = doc.company
    event.posting_date = doc.posting_date
    event.posting_time = doc.posting_time
    event.grand_total = doc.grand_total
    event.net_total = doc.net_total
    event.status = "Pending"
    event.insert(ignore_permissions=True)

    try:
        # Load settings
        settings = frappe.get_single("SMRITI SFM Settings")
        if not settings.enable_sfm:
            event.status = "Processed"
            event.error_message = "SFM module is disabled in settings."
            event.save(ignore_permissions=True)
            return

        # Resolve Warehouse and Store
        warehouse = doc.get("warehouse")
        if not warehouse and doc.get("items"):
            warehouse = doc.items[0].warehouse
        
        store = resolve_store(doc.company, warehouse)

        # Resolve Attribution Employees & Splits
        attributions = [] # List of dict: {"employee": x, "pct": y, "type": z, "record": w}
        
        resolved = False
        
        # Scenario A: Customer Ownership Precedence
        if settings.ownership_precedence and doc.customer:
            # Query active ownership timelines
            owners = frappe.get_all(
                "SMRITI Customer Ownership",
                filters=[
                    ["customer", "=", doc.customer],
                    ["company", "=", doc.company],
                    ["start_date", "<=", doc.posting_date],
                    ["is_active", "=", 1]
                ],
                fields=["name", "primary_owner", "secondary_owner", "end_date"]
            )
            
            active_ownership = None
            for o in owners:
                if not o.end_date or getdate(o.end_date) >= getdate(doc.posting_date):
                    active_ownership = o
                    break
                    
            if active_ownership and active_ownership.primary_owner:
                p_pct = flt(settings.primary_split_pct or 70.0)
                s_pct = flt(settings.secondary_split_pct or 30.0)
                
                if active_ownership.secondary_owner:
                    attributions.append({
                        "employee": active_ownership.primary_owner,
                        "pct": p_pct,
                        "type": "Primary",
                        "record": active_ownership.name
                    })
                    attributions.append({
                        "employee": active_ownership.secondary_owner,
                        "pct": s_pct,
                        "type": "Secondary",
                        "record": active_ownership.name
                    })
                else:
                    attributions.append({
                        "employee": active_ownership.primary_owner,
                        "pct": 100.0,
                        "type": "Primary",
                        "record": active_ownership.name
                    })
                resolved = True

        # Scenario B: Standard ERPNext Sales Team
        if not resolved and doc.get("sales_team"):
            for member in doc.sales_team:
                if member.sales_person:
                    employee = frappe.db.get_value("Sales Person", member.sales_person, "employee")
                    if employee:
                        pct = flt(member.allocated_percentage)
                        attributions.append({
                            "employee": employee,
                            "pct": pct if pct > 0 else (100.0 / len(doc.sales_team)),
                            "type": "Service",
                            "record": None
                        })
            if attributions:
                resolved = True

        # Scenario C: Walk-In Fallback
        if not resolved:
            walkin = settings.walkin_employee
            if not walkin:
                # Look for / create Walk-In employee dynamically
                walkin = frappe.db.get_value("Employee", {"employee_name": ["like", "%Walk-In%"]}, "name")
                if not walkin:
                    emp = frappe.new_doc("Employee")
                    emp.employee_name = "Walk-In Employee"
                    emp.first_name = "Walk-In"
                    emp.company = doc.company
                    emp.status = "Active"
                    emp.date_of_joining = nowdate()
                    emp.insert(ignore_permissions=True)
                    walkin = emp.name
                    
            attributions.append({
                "employee": walkin,
                "pct": 100.0,
                "type": "Walk-In",
                "record": None
            })

        # Insert Ledger Entries and trigger KPI updates
        for attr in attributions:
            ledger = frappe.new_doc("SMRITI Attribution Ledger")
            ledger.invoice_reference = doc.name
            ledger.invoice_doctype = doc.doctype
            ledger.customer = doc.customer
            ledger.employee = attr["employee"]
            ledger.ownership_type = attr["type"]
            ledger.credit_percentage = attr["pct"]
            ledger.revenue_credit = flt(doc.net_total) * (attr["pct"] / 100.0)
            ledger.store = store
            ledger.warehouse = warehouse
            ledger.posting_date = doc.posting_date
            ledger.posting_time = doc.posting_time
            ledger.source_document = doc.name
            ledger.ledger_status = "Active"
            ledger.company = doc.company
            ledger.ownership_record = attr["record"]
            ledger.insert(ignore_permissions=True)
            
            # Update KPI snapshot
            update_kpi_snapshot(ledger.employee, ledger.store, ledger.posting_date, ledger.company)

        event.status = "Processed"
        event.save(ignore_permissions=True)

    except Exception as e:
        if frappe.flags.in_test:
            raise e
        frappe.log_error(message=frappe.get_traceback(), title="SMRITI SFM Submission Failure")
        event.status = "Pending"
        event.error_message = str(e)
        event.save(ignore_permissions=True)

def process_invoice_cancel(doc, method=None):
    """
    Attributions cancellation hook.
    Inserts negative reversal ledger entries and updates statuses.
    """
    event = frappe.new_doc("SMRITI Attribution Event")
    event.invoice_reference = doc.name
    event.invoice_doctype = doc.doctype
    event.customer = doc.customer
    event.company = doc.company
    event.posting_date = doc.posting_date
    event.posting_time = doc.posting_time
    event.grand_total = doc.grand_total
    event.net_total = doc.net_total
    event.status = "Reversed"
    event.insert(ignore_permissions=True)

    try:
        # Retrieve all active ledger entries for this invoice
        active_entries = frappe.get_all(
            "SMRITI Attribution Ledger",
            filters={
                "invoice_reference": doc.name,
                "invoice_doctype": doc.doctype,
                "ledger_status": "Active"
            },
            fields=["name", "employee", "ownership_type", "credit_percentage", "revenue_credit", "store", "warehouse", "posting_date", "company", "ownership_record"]
        )

        for entry in active_entries:
            # Create a reversal ledger entry
            rev = frappe.new_doc("SMRITI Attribution Ledger")
            rev.invoice_reference = doc.name
            rev.invoice_doctype = doc.doctype
            rev.customer = doc.customer
            rev.employee = entry.employee
            rev.ownership_type = entry.ownership_type
            rev.credit_percentage = entry.credit_percentage
            rev.revenue_credit = -flt(entry.revenue_credit) # Negative credit
            rev.store = entry.store
            rev.warehouse = entry.warehouse
            rev.posting_date = nowdate()
            rev.posting_time = nowtime()
            rev.source_document = doc.name
            rev.ledger_status = "Reversed"
            rev.reversal_reference = entry.name
            rev.company = entry.company
            rev.ownership_record = entry.ownership_record
            rev.insert(ignore_permissions=True)

            # Update the original entry's status to Reversed
            frappe.db.set_value(
                "SMRITI Attribution Ledger", 
                entry.name, 
                {
                    "ledger_status": "Reversed",
                    "reversal_reference": rev.name
                }
            )

            # Update KPI snapshot for that day
            update_kpi_snapshot(entry.employee, entry.store, entry.posting_date, entry.company)
            # Also update KPI snapshot for the cancellation day (today) if different!
            if getdate(entry.posting_date) != getdate(nowdate()):
                update_kpi_snapshot(entry.employee, entry.store, nowdate(), entry.company)

    except Exception as e:
        if frappe.flags.in_test:
            raise e
        frappe.log_error(message=frappe.get_traceback(), title="SMRITI SFM Cancellation Failure")
        event.error_message = str(e)
        event.save(ignore_permissions=True)
