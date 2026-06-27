# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_health_service.py
# @description: SMRITI PSV Health Service — operational alerts, health checks, and exception management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: Extracted from psv_service.py (Phase 4 remediation).
#       psv_service.py re-imports all public names for backward compatibility.
#

import frappe
from frappe import _
from frappe.utils import today, now_datetime

from smriti_retail_os.balance_engine import get_party_balance


def find_open_alert(alert_key):
    """Finds a pending (open) alert for the given key"""
    return frappe.db.get_value(
        "SMRITI PSV Exception Record",
        {"alert_key": alert_key, "status": "Pending Reconciliation"},
        "name"
    )


def create_or_update_alert(party_stock_account, alert_type, severity, details, item_code=None, sales_invoice=None, missing_qty=0.0):
    """
    Finds existing open alert for alert_key and updates last_seen,
    otherwise creates a new alert record.
    """
    alert_type_key = alert_type.upper().replace(" ", "_")
    item_code_val = item_code or ""
    alert_key = f"{party_stock_account}|{alert_type_key}|{item_code_val}"

    open_alert_name = find_open_alert(alert_key)
    if open_alert_name:
        frappe.db.set_value("SMRITI PSV Exception Record", open_alert_name, {
            "last_seen": now_datetime(),
            "reconciliation_notes": details
        })
        return open_alert_name
    else:
        doc = frappe.get_doc({
            "doctype": "SMRITI PSV Exception Record",
            "timestamp": now_datetime(),
            "last_seen": now_datetime(),
            "party_stock_account": party_stock_account,
            "alert_key": alert_key,
            "alert_type": alert_type,
            "severity": severity,
            "sales_invoice": sales_invoice,
            "item_code": item_code,
            "missing_qty": float(missing_qty),
            "status": "Pending Reconciliation",
            "reconciliation_notes": details
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        return doc.name


def run_psv_daily_health_check():
    """
    Daily scheduled job for SMRITI PSV module checking:
    1. Negative Balances (Critical)
    2. Pending Reconciliations (High)
    3. Late Uploads (Warning/Info)
    4. Locations Never Audited (Warning)
    5. Alert Resolution Pass
    """
    from frappe.utils import add_days, getdate
    
    # Get active locations
    active_locations = frappe.get_all(
        "SMRITI Party Stock Account", 
        filters={"active": 1},
        fields=["name", "status"]
    )
    
    for loc in active_locations:
        loc_name = loc["name"]
        
        # 1. Negative Balances (Critical)
        neg_items = frappe.db.sql("""
            SELECT item_code, SUM(qty) as bal
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s
            GROUP BY item_code
            HAVING SUM(qty) < 0
        """, (loc_name,), as_dict=True)
        
        for item in neg_items:
            create_or_update_alert(
                party_stock_account=loc_name,
                alert_type="Negative Balance",
                severity="Critical",
                details=f"Critical: Negative shadow balance ({item['bal']} units) detected.",
                item_code=item["item_code"],
                missing_qty=abs(item["bal"])
            )
            if loc["status"] != "Pending Reconciliation":
                frappe.db.set_value("SMRITI Party Stock Account", loc_name, "status", "Pending Reconciliation")
                
        # 2. Pending Reconciliations (High)
        has_pending_reconciliations = frappe.db.exists("SMRITI PSV Exception Record", {
            "party_stock_account": loc_name,
            "status": "Pending Reconciliation"
        })
        if has_pending_reconciliations:
            if loc["status"] != "Pending Reconciliation":
                frappe.db.set_value("SMRITI Party Stock Account", loc_name, "status", "Pending Reconciliation")
                
        # 3. Late Uploads (Warning/Info)
        latest_upload = frappe.db.get_value(
            "SMRITI Party Sales Upload",
            {"party_stock_account": loc_name, "docstatus": 1},
            "period_end_date",
            order_by="period_end_date desc"
        )
        if latest_upload:
            days_since_upload = (getdate(today()) - getdate(latest_upload)).days
            if days_since_upload > 7:
                create_or_update_alert(
                    party_stock_account=loc_name,
                    alert_type="Late Upload",
                    severity="Warning",
                    details=f"Warning: No sales upload in the last {days_since_upload} days."
                )
            elif days_since_upload > 1:
                create_or_update_alert(
                    party_stock_account=loc_name,
                    alert_type="Late Upload",
                    severity="Info",
                    details=f"Info: Sales upload is delayed by {days_since_upload} days."
                )
        else:
            create_or_update_alert(
                party_stock_account=loc_name,
                alert_type="Late Upload",
                severity="Warning",
                details="Warning: No sales uploads have ever been imported for this location."
            )
            
        # 4. Locations Never Audited (Warning)
        latest_audit = frappe.db.get_value(
            "SMRITI Party Physical Snapshot",
            {"party_stock_account": loc_name, "docstatus": 1},
            "audit_date",
            order_by="audit_date desc"
        )
        if latest_audit:
            days_since_audit = (getdate(today()) - getdate(latest_audit)).days
            if days_since_audit > 90:
                create_or_update_alert(
                    party_stock_account=loc_name,
                    alert_type="Never Audited",
                    severity="Warning",
                    details=f"Warning: Last physical stock audit was {days_since_audit} days ago."
                )
        else:
            create_or_update_alert(
                party_stock_account=loc_name,
                alert_type="Never Audited",
                severity="Warning",
                details="Warning: No physical stock audit has ever been recorded for this location."
            )
            
        # 5. Orphaned Invoice Detection (Hook Failure Recovery)
        # Find submitted Sales Invoices linked to this PSA that have no corresponding ledger entry
        orphaned_invoices = frappe.db.sql("""
            SELECT si.name, si.company
            FROM `tabSales Invoice` si
            WHERE si.custom_party_stock_account = %s
              AND si.docstatus = 1
              AND NOT EXISTS (
                  SELECT 1 FROM `tabSMRITI Party Stock Ledger Entry` le
                  WHERE le.voucher_no = si.name
                    AND le.party_stock_account = si.custom_party_stock_account
              )
        """, (loc_name,), as_dict=True)

        for orphan in orphaned_invoices:
            create_or_update_alert(
                party_stock_account=loc_name,
                alert_type="Hook Failure",
                severity="Critical",
                details=f"Orphaned Invoice: SI {orphan['name']} has PSA linked but no ledger entries. Likely hook failure during submission.",
                sales_invoice=orphan["name"]
            )

        # 6. Alert Resolution Pass
        open_alerts = frappe.get_all(
            "SMRITI PSV Exception Record",
            filters={"party_stock_account": loc_name, "status": "Pending Reconciliation"},
            fields=["name", "alert_type", "item_code"]
        )
        
        for alert in open_alerts:
            should_resolve = False
            
            if alert["alert_type"] == "Negative Balance" and alert["item_code"]:
                bal = get_party_balance(loc_name, alert["item_code"])
                if bal >= 0.0:
                    should_resolve = True
            elif alert["alert_type"] == "Late Upload":
                latest_up = frappe.db.get_value(
                    "SMRITI Party Sales Upload",
                    {"party_stock_account": loc_name, "docstatus": 1},
                    "period_end_date",
                    order_by="period_end_date desc"
                )
                if latest_up:
                    days = (getdate(today()) - getdate(latest_up)).days
                    if days <= 1:
                        should_resolve = True
            elif alert["alert_type"] == "Never Audited":
                latest_aud = frappe.db.get_value(
                    "SMRITI Party Physical Snapshot",
                    {"party_stock_account": loc_name, "docstatus": 1},
                    "audit_date",
                    order_by="audit_date desc"
                )
                if latest_aud:
                    days = (getdate(today()) - getdate(latest_aud)).days
                    if days <= 90:
                        should_resolve = True
            elif alert["alert_type"] == "Hook Failure" and alert.get("sales_invoice"):
                # Auto-resolve if ledger entries now exist for this invoice
                has_entries = frappe.db.exists("SMRITI Party Stock Ledger Entry", {
                    "voucher_no": alert["sales_invoice"],
                    "party_stock_account": loc_name
                })
                if has_entries:
                    should_resolve = True
                        
            if should_resolve:
                frappe.db.set_value("SMRITI PSV Exception Record", alert["name"], {
                    "status": "Reconciled",
                    "reconciled_by": "Administrator",
                    "reconciled_on": now_datetime(),
                    "reconciliation_notes": "Automatically resolved by daily operational health check."
                })
                
        # Re-verify if any open alerts remain
        still_has_open_alerts = frappe.db.exists("SMRITI PSV Exception Record", {
            "party_stock_account": loc_name,
            "status": "Pending Reconciliation"
        })
        if not still_has_open_alerts and loc["status"] != "Active":
            frappe.db.set_value("SMRITI Party Stock Account", loc_name, "status", "Active")


def validate_sales_invoice_cancel(doc, method=None):
    """
    Hook called before Sales Invoice cancellation.
    SMRITI PSV allows invoice cancellation to proceed even if it causes a temporary negative balance,
    creating an exception record downstream during on_cancel. Thus, this is a pass-through guard.
    """
    pass
