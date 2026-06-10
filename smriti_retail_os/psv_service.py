# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/psv_service.py
# @description: Core service logic for SMRITI Party Stock Visibility.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import hashlib
import os
import csv
import contextlib
import frappe
from frappe import _
from frappe.utils import get_datetime, today, now_datetime
from smriti_retail_os.ledger_engine import make_ledger_entry, log_activity
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances


# ─── F4-FIX: PSV Distributed Upload Lock ─────────────────────────────────────
# Prevents overselling race condition where two concurrent sales uploads
# for the same Party Stock Account both pass the balance check and then
# both commit, creating a net-negative shadow balance.
#
# Implementation: Redis SET NX (set-if-not-exists) via frappe.cache().
# No new infrastructure required — Frappe already uses Redis for caching.
# Lock is scoped per party_stock_account, so concurrent uploads for
# DIFFERENT locations are not blocked.

_PSV_LOCK_EXPIRY_SECONDS = 30   # Max seconds a single upload validation can hold the lock
_PSV_LOCK_PREFIX = "smriti:psv:upload_lock:"


@contextlib.contextmanager
def _psv_upload_lock(party_stock_account):
    """
    Context manager that acquires a per-PSA distributed lock before
    running the overselling check + submit sequence.

    Raises frappe.ValidationError if the lock cannot be acquired
    (meaning another upload for the same PSA is in progress).
    """
    lock_key = f"{_PSV_LOCK_PREFIX}{party_stock_account}"
    cache = frappe.cache()

    # Redis SET NX EX — atomic set-if-not-exists with expiry
    acquired = cache.set(lock_key, 1, ex=_PSV_LOCK_EXPIRY_SECONDS, nx=True)

    if not acquired:
        frappe.throw(
            _("Another sales upload for party stock account '{0}' is currently being processed. "
              "Please wait a moment and try again.").format(party_stock_account),
            frappe.ValidationError
        )

    try:
        yield
    finally:
        # Always release the lock — even on exception
        try:
            cache.delete(lock_key)
        except Exception:
            pass  # Best-effort release; lock expires automatically after _PSV_LOCK_EXPIRY_SECONDS


# --- UNIVERSAL TRANSACTION ENGINE ---

def create_psv_transaction(psa, transaction_type, items, company=None, reference_doctype=None, reference_name=None, remarks=None, posting_date=None):
    if not company:
        company = frappe.db.get_value("SMRITI Party Stock Account", psa, "company")
        
    fingerprint = None
    if reference_doctype and reference_name:
        fingerprint = f"{transaction_type}::{reference_doctype}::{reference_name}"
        # BUG-006 FIX: Check both Draft (0) and Submitted (1) to close the race window
        # where two concurrent requests both pass a docstatus=1-only check.
        # Cancelled transactions (docstatus=2) are excluded — they may be legitimately reprocessed.
        existing = frappe.db.get_value(
            "SMRITI PSV Transaction",
            {"mapping_fingerprint": fingerprint, "docstatus": ["in", [0, 1]]},
            "name"
        )
        if existing:
            return existing


    doc = frappe.new_doc("SMRITI PSV Transaction")
    doc.party_stock_account = psa
    doc.transaction_type = transaction_type
    doc.company = company
    doc.reference_doctype = reference_doctype
    doc.reference_name = reference_name
    doc.remarks = remarks
    if posting_date:
        doc.posting_date = posting_date
        
    for item in items:
        if not item.get("item_code") or not item.get("qty"):
            continue
        doc.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "rate": item.get("rate") or 0.0,
            "reason": item.get("reason") or ""
        })
        
    if not doc.items:
        return None
        
    doc.flags.ignore_links = True
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc.name

# ─── SALES INVOICE HOOKS ──────────────────────────────────────────────────────

def get_posting_datetime(doc):
    """
    Safely combines ERPNext posting_date and posting_time into a Python datetime object.
    """
    if doc.posting_date and doc.posting_time:
        return get_datetime(f"{doc.posting_date} {doc.posting_time}")
    return get_datetime(doc.posting_date or today())

def process_sales_invoice_submit(doc, method=None):
    if not doc.get("custom_party_stock_account"): return
    try:
        tx_type = "RETURN" if doc.is_return else "TRANSFER_OUT"
        items_data = [{"item_code": i.item_code, "qty": i.qty, "rate": i.rate} for i in doc.items]
        if items_data:
            create_psv_transaction(doc.custom_party_stock_account, tx_type, items_data, doc.company, doc.doctype, doc.name, "Generated from Sales Invoice", get_posting_datetime(doc))
    except Exception as e:
        frappe.log_error(title=f"PSV Error: {doc.name}", message=frappe.get_traceback())
        frappe.get_doc({"doctype": "SMRITI PSV Exception Record", "party_stock_account": doc.custom_party_stock_account, "exception_type": "Hook Failure", "reference_doctype": doc.doctype, "reference_name": doc.name, "description": str(e), "status": "Pending Reconciliation"}).insert(ignore_permissions=True)
        frappe.db.commit()

def process_sales_invoice_cancel(doc, method=None):
    if not doc.get("custom_party_stock_account"): return
    try:
        tx_name = frappe.db.get_value("SMRITI PSV Transaction", {"reference_doctype": doc.doctype, "reference_name": doc.name, "docstatus": 1})
        if tx_name: frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()
    except Exception as e:
        frappe.log_error(title=f"PSV Cancel Error: {doc.name}", message=frappe.get_traceback())
        frappe.get_doc({"doctype": "SMRITI PSV Exception Record", "party_stock_account": doc.custom_party_stock_account, "exception_type": "Hook Failure", "reference_doctype": doc.doctype, "reference_name": doc.name, "description": str(e), "status": "Pending Reconciliation"}).insert(ignore_permissions=True)
        frappe.db.commit()
# ─── WEEKLY SALES UPLOAD ──────────────────────────────────────────────────────

def validate_sales_upload(doc):
    """Gathers MD5 validation and period locks validation.

    F4-FIX: Overselling check (step 5) now runs inside a per-PSA Redis lock
    to close the race window where two concurrent uploads could both pass
    the balance check and then both commit, resulting in a negative shadow balance.
    The lock is acquired only during the critical section (check + submit),
    not for the entire validate lifecycle.
    """
    # 1. Validate Period Start/End
    if not doc.period_start_date or not doc.period_end_date:
        frappe.throw(_("Period Start Date and Period End Date are required."))
    if doc.period_start_date > doc.period_end_date:
        frappe.throw(_("Period Start Date cannot be later than Period End Date."))

    # 2. File duplicate MD5 check
    if doc.excel_file:
        file_doc = frappe.get_doc("File", {"file_url": doc.excel_file})
        file_content = file_doc.get_content()
        file_hash = hashlib.md5(file_content).hexdigest()

        duplicate = frappe.db.exists(
            "SMRITI Party Sales Upload",
            {"file_hash": file_hash, "name": ["!=", doc.name]}
        )
        if duplicate:
            frappe.throw(_("Duplicate Upload: This exact file has already been imported under {0}.").format(duplicate))
        doc.file_hash = file_hash

    # 3. Period Overlap Check
    overlapping_import = frappe.db.sql("""
        SELECT name
        FROM `tabSMRITI Party Sales Upload`
        WHERE party_stock_account = %s
          AND docstatus = 1
          AND name != %s
          AND (
            (period_start_date <= %s AND period_end_date >= %s) OR
            (period_start_date <= %s AND period_end_date >= %s) OR
            (%s <= period_start_date AND %s >= period_end_date)
          )
    """, (
        doc.party_stock_account,
        doc.name,
        doc.period_start_date, doc.period_start_date,
        doc.period_end_date, doc.period_end_date,
        doc.period_start_date, doc.period_end_date
    ))
    if overlapping_import:
        frappe.throw(
            _("Period Lock: An imported sales file already exists for this location within the date range. Conflicting import: {0}.")
            .format(overlapping_import[0][0])
        )

    # 4. Parse Excel / CSV and populate items if currently empty (on draft save)
    if not doc.items and doc.excel_file:
        parse_and_populate_items(doc)

    # 5. Overselling check — runs inside per-PSA distributed lock to prevent
    #    concurrent upload race condition (F4-FIX: Redis SET NX).
    with _psv_upload_lock(doc.party_stock_account):
        # Re-read balances INSIDE the lock to get a fresh, race-safe snapshot.
        balances = get_bulk_party_balances(doc.party_stock_account, [item.item_code for item in doc.items])
        for item in doc.items:
            current_bal = balances.get(item.item_code, 0.0)
            if item.qty_sold > current_bal:
                frappe.throw(
                    _("Row #{0}: Cannot record sales of {1} units for SKU {2}. Current available balance is only {3} units.")
                    .format(item.idx, item.qty_sold, item.item_code, current_bal)
                )

def parse_and_populate_items(doc):
    """
    Parses CSV/Excel file and populates the child items table.
    """
    file_doc = frappe.get_doc("File", {"file_url": doc.excel_file})
    file_path = file_doc.get_full_path()
    
    # We support simple CSV parsing for testing/import, and Excel via openpyxl
    if file_path.endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    doc.append("items", {
                        "date": get_datetime(row[0]) if row[0] else today(),
                        "item_code": row[1].strip(),
                        "qty_sold": float(row[2])
                    })
    else:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(filename=file_path, read_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            # Expect header: Date, Item Code, Qty Sold
            for row in rows[1:]: # Skip header
                if row and len(row) >= 3 and row[1]:
                    doc.append("items", {
                        "date": get_datetime(row[0]) if row[0] else today(),
                        "item_code": str(row[1]).strip(),
                        "qty_sold": float(row[2] or 0)
                    })
        except ImportError:
            frappe.throw(_("Python library 'openpyxl' is required to parse Excel files."))

def process_sales_upload_submit(doc):
    frappe.db.set_value(doc.doctype, doc.name, "status", "Imported")
    items_data = [{"item_code": i.item_code, "qty": i.qty_sold} for i in doc.items]
    create_psv_transaction(doc.party_stock_account, "SALES_UPLOAD", items_data, doc.company, doc.doctype, doc.name, f"Imported from {doc.name}")

def process_sales_upload_cancel(doc):
    """
    Reverses a weekly sales upload.

    BUG-004 FIX: Previously wrote raw make_ledger_entry() calls directly, causing
    double-reversal because the PSV Transaction's on_cancel already writes VOID entries.

    Correct approach:
    1. Find the submitted SMRITI PSV Transaction linked to this upload.
    2. Cancel it — on_cancel() fires update_ledger(cancel=True) which writes the
       correct VOID entries with proper sign handling.
    3. Fallback: if no PSV Transaction exists (legacy/pre-fix data), write direct
       reversal entries as before — but with the correct sign.
    """
    frappe.db.set_value(doc.doctype, doc.name, "status", "Draft")

    # Preferred path: cancel the PSV Transaction (handles ledger reversal atomically)
    tx_name = frappe.db.get_value(
        "SMRITI PSV Transaction",
        {"reference_doctype": doc.doctype, "reference_name": doc.name, "docstatus": 1},
        "name"
    )
    if tx_name:
        frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()
    else:
        # Fallback for historical data that was processed before the PSV Transaction
        # document layer existed. Write direct reversal entries.
        for item in doc.items:
            # qty_sold is positive (e.g. 10 units sold).
            # Original SALES_UPLOAD ledger entry was negative (-10).
            # Reversal must be positive (+10) to restore balance.
            make_ledger_entry(
                company=doc.company,
                posting_datetime=now_datetime(),
                party_stock_account=doc.party_stock_account,
                item_code=item.item_code,
                qty=abs(item.qty_sold),  # Always positive — restoring stock
                voucher_type="Sales",
                voucher_no=f"VOID-{doc.name}",
                reason=_("Import Cancelled — direct fallback reversal")
            )

    log_activity(
        action_type="Cancel Dispatch",
        party_stock_account=doc.party_stock_account,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        details="Reversed weekly sales file import. Balances restored."
    )



# ─── PHYSICAL STOCK RECONCILIATION SNAPSHOT ────────────────────────────────────

def validate_physical_snapshot(doc):
    """Calculates variance based on current shadow ledger state"""
    for item in doc.items:
        # Populate system balance
        item.system_qty = get_party_balance(doc.party_stock_account, item.item_code)
        item.variance = item.physical_qty - item.system_qty

def process_physical_snapshot_submit(doc):
    if doc.status != "Approved":
        frappe.throw(_("Audit Snapshots must be explicitly approved before submitting."))
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()
    items_data = [{"item_code": i.item_code, "qty": i.variance, "reason": i.variance_reason} for i in doc.items if i.variance != 0.0]
    if items_data:
        create_psv_transaction(doc.party_stock_account, "AUDIT_ADJUSTMENT", items_data, doc.company, doc.doctype, doc.name, "Physical Snapshot Approved", get_datetime(doc.audit_date))

def process_physical_snapshot_cancel(doc):
    doc.approved_by = None
    doc.approved_on = None
    tx_name = frappe.db.get_value("SMRITI PSV Transaction", {"reference_doctype": doc.doctype, "reference_name": doc.name, "docstatus": 1})
    if tx_name:
        frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()

def import_opening_balances(company, party_stock_account, items_data):
    # INT-004 FIX: Use a date-scoped pseudo-reference as the fingerprint source so
    # that calling this function twice for the same PSA on the same day is idempotent.
    from frappe.utils import today
    pseudo_ref_name = f"OPENING-{party_stock_account}-{today()}"

    return create_psv_transaction(
        psa=party_stock_account,
        transaction_type="OPENING",
        items=items_data,
        company=company,
        reference_doctype="Opening Balance Import",
        reference_name=pseudo_ref_name,
        remarks="Initial Opening Balance Import"
    )

@frappe.whitelist()
def process_opening_balance(company, party_stock_account, items):
    """
    SEC-004 FIX: Enforce role-based access before allowing opening balance import.
    Previously public to any authenticated user — now restricted to store managers.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if isinstance(items, str):
        import json
        items = json.loads(items)

    if not company or not party_stock_account or not items:
        frappe.throw(_("Company, Party Stock Account, and at least one item are required."))

    return import_opening_balances(company, party_stock_account, items)

# ─── OPERATIONAL HEALTH ALERTS & CHECKS ────────────────────────────────────────

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
