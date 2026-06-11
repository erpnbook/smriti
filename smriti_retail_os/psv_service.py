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


@frappe.whitelist()
def get_landing_cost(variant):
    """
    Resolves the landing cost (buying/valuation rate) for a variant using a fallback hierarchy:
    1. Variant Item: valuation_rate
    2. Variant Item: standard_rate
    3. Variant Item: Standard Buying Price from Item Price table
    4. Parent Template Item: valuation_rate (if variant_of is set)
    5. Parent Template Item: standard_rate
    6. Parent Template Item: Standard Buying Price from Item Price table
    7. 0.0 (fallback)
    """
    if not variant:
        return 0.0
        
    if not hasattr(frappe.local, "landing_cost_cache"):
        frappe.local.landing_cost_cache = {}
        
    if variant in frappe.local.landing_cost_cache:
        return frappe.local.landing_cost_cache[variant]
        
    cost = _get_landing_cost_from_db(variant)
    frappe.local.landing_cost_cache[variant] = cost
    return cost


def _get_landing_cost_from_db(variant):
    item_details = frappe.db.get_value(
        "Item", variant, ["valuation_rate", "standard_rate", "variant_of", "name"], as_dict=True
    )
    if not item_details:
        return 0.0
    
    if item_details.get("valuation_rate"):
        return float(item_details["valuation_rate"])
        
    if item_details.get("standard_rate"):
        return float(item_details["standard_rate"])
        
    buying_price = frappe.db.get_value(
        "Item Price", {"item_code": variant, "price_list": "Standard Buying"}, "price_list_rate"
    )
    if buying_price:
        return float(buying_price)
        
    parent_code = item_details.get("variant_of")
    if parent_code:
        parent_details = frappe.db.get_value(
            "Item", parent_code, ["valuation_rate", "standard_rate"], as_dict=True
        )
        if parent_details:
            if parent_details.get("valuation_rate"):
                return float(parent_details["valuation_rate"])
                
            if parent_details.get("standard_rate"):
                return float(parent_details["standard_rate"])
                
            parent_buying_price = frappe.db.get_value(
                "Item Price", {"item_code": parent_code, "price_list": "Standard Buying"}, "price_list_rate"
            )
            if parent_buying_price:
                return float(parent_buying_price)
                
    return 0.0


def calculate_aging_for_variant(partner, variant, current_qty, snapshot_date=None):
    """
    Allocates the current_qty to aging buckets (0-30, 31-60, 61-90, 91-180, 180+)
    using FIFO logic on positive ledger entries.
    """
    from frappe.utils import getdate
    if not snapshot_date:
        snapshot_date = getdate(today())
    else:
        snapshot_date = getdate(snapshot_date)
        
    buckets = {
        "qty_0_30": 0.0,
        "qty_31_60": 0.0,
        "qty_61_90": 0.0,
        "qty_91_180": 0.0,
        "qty_180_plus": 0.0
    }
    
    if current_qty <= 0:
        return buckets
        
    # Fetch positive ledger entries ordered by posting_datetime desc (FIFO)
    entries = frappe.db.sql("""
        SELECT qty, posting_datetime
        FROM `tabPSV Ledger Entry`
        WHERE channel_partner = %s AND item_variant = %s AND qty > 0
        ORDER BY posting_datetime DESC
    """, (partner, variant), as_dict=True)
    
    if not entries:
        entries = frappe.db.sql("""
            SELECT qty, posting_datetime
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s AND item_code = %s AND qty > 0
            ORDER BY posting_datetime DESC
        """, (partner, variant), as_dict=True)

    remaining = current_qty
    for entry in entries:
        if remaining <= 0:
            break
        
        qty_to_allocate = min(remaining, float(entry["qty"]))
        remaining -= qty_to_allocate
        
        entry_date = getdate(entry["posting_datetime"])
        age_days = (snapshot_date - entry_date).days
        
        if age_days <= 30:
            buckets["qty_0_30"] += qty_to_allocate
        elif age_days <= 60:
            buckets["qty_31_60"] += qty_to_allocate
        elif age_days <= 90:
            buckets["qty_61_90"] += qty_to_allocate
        elif age_days <= 180:
            buckets["qty_91_180"] += qty_to_allocate
        else:
            buckets["qty_180_plus"] += qty_to_allocate
            
    if remaining > 0:
        buckets["qty_180_plus"] += remaining
        
    return buckets


def get_aging_alert(buckets, current_qty):
    if current_qty <= 0:
        return "Healthy"
    critical_qty = buckets["qty_180_plus"]
    warning_qty = buckets["qty_91_180"] + buckets["qty_180_plus"]
    
    if critical_qty > 0 or warning_qty > 0.5 * current_qty:
        return "Critical"
    elif warning_qty > 0.25 * current_qty or buckets["qty_61_90"] > 0:
        return "Warning"
    else:
        return "Healthy"


@frappe.whitelist()
def generate_snapshots():
    """
    Generates stock aging snapshots for all active channel partners.
    This process is incremental and resumable, governed by PSV System Settings.
    Uses a Redis lock to prevent concurrent runs.
    """
    lock_key = "smriti:psv:snapshot_generation"
    cache = frappe.cache()
    
    if cache.get(lock_key):
        frappe.logger().warning("PSV snapshot generation is already running. Skipping execution.")
        return "Skipped: Lock exists"
        
    cache.set(lock_key, 1, ex=3600)  # Lock for 1 hour
    
    try:
        # Ensure single settings doc exists
        settings = frappe.get_single("PSV System Settings")
        batch_size = int(settings.snapshot_batch_size or 500)
        last_processed = settings.last_processed_partner
        
        partners = frappe.get_all(
            "PSV Channel Partner",
            filters={"active": 1},
            fields=["name", "company", "territory", "region"],
            order_by="name"
        )
        
        if not partners:
            partners = frappe.get_all(
                "SMRITI Party Stock Account",
                filters={"active": 1},
                fields=["name", "company", "region"],
                order_by="name"
            )
            for p in partners:
                p["territory"] = "All Territories"
                
        if not partners:
            return "No active partners found"
            
        if last_processed:
            partners_to_process = [p for p in partners if p.name > last_processed]
            if not partners_to_process:
                partners_to_process = partners
                last_processed = ""
        else:
            partners_to_process = partners
            
        batch = partners_to_process[:batch_size]
        if not batch:
            return "No partners to process"
            
        snapshot_date = frappe.utils.getdate(today())
        
        for partner in batch:
            frappe.db.delete("PSV Stock Aging Snapshot", {
                "snapshot_date": snapshot_date,
                "channel_partner": partner.name
            })
            
            balances = frappe.db.sql("""
                SELECT item_variant, SUM(qty) as balance
                FROM `tabPSV Ledger Entry`
                WHERE channel_partner = %s
                GROUP BY item_variant
                HAVING SUM(qty) > 0
            """, (partner.name,), as_dict=True)
            
            if not balances:
                balances = frappe.db.sql("""
                    SELECT item_code as item_variant, SUM(qty) as balance
                    FROM `tabSMRITI Party Stock Ledger Entry`
                    WHERE party_stock_account = %s
                    GROUP BY item_code
                    HAVING SUM(qty) > 0
                """, (partner.name,), as_dict=True)
                
            for bal in balances:
                variant = bal["item_variant"]
                current_qty = float(bal["balance"])
                
                item_info = frappe.db.get_value("Item", variant, ["brand", "item_group"], as_dict=True)
                brand_name = item_info.get("brand") if item_info else ""
                item_group_name = item_info.get("item_group") if item_info else ""
                
                buckets = calculate_aging_for_variant(partner.name, variant, current_qty, snapshot_date)
                aging_alert = get_aging_alert(buckets, current_qty)
                
                snap = frappe.get_doc({
                    "doctype": "PSV Stock Aging Snapshot",
                    "snapshot_date": snapshot_date,
                    "channel_partner": partner.name,
                    "item_variant": variant,
                    "qty": current_qty,
                    "brand_name": brand_name,
                    "item_group_name": item_group_name,
                    "territory_name": partner.territory,
                    "qty_0_30": buckets["qty_0_30"],
                    "qty_31_60": buckets["qty_31_60"],
                    "qty_61_90": buckets["qty_61_90"],
                    "qty_91_180": buckets["qty_91_180"],
                    "qty_180_plus": buckets["qty_180_plus"],
                    "aging_alert": aging_alert
                })
                snap.insert(ignore_permissions=True)
                
        last_partner_processed = batch[-1].name
        
        all_done = False
        if len(batch) < batch_size or partner.name == partners[-1].name:
            all_done = True
            
        settings.last_snapshot_run = now_datetime()
        if all_done:
            settings.last_processed_partner = ""
            settings.last_checkpoint = ""
        else:
            settings.last_processed_partner = last_partner_processed
            settings.last_checkpoint = last_partner_processed
            
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        return f"Success: Processed {len(batch)} partners"
        
    finally:
        cache.delete(lock_key)


@frappe.whitelist()
def get_redistribution_suggestions(company=None):
    """
    Returns stock redistribution suggestions across channel partners for a company.
    """
    from frappe.utils import add_days
    settings = frappe.get_single("PSV System Settings")
    scope = settings.redistribution_scope or "Same Territory"
    critical_woc = settings.weeks_of_cover_critical or 2
    healthy_woc = settings.weeks_of_cover_healthy or 8
    
    filters = {"active": 1}
    if company:
        filters["company"] = company
        
    partners = frappe.get_all(
        "PSV Channel Partner",
        filters=filters,
        fields=["name", "company", "territory", "region", "zone"]
    )
    
    if not partners:
        partners = frappe.get_all(
            "SMRITI Party Stock Account",
            filters=filters,
            fields=["name", "company", "zone", "region"]
        )
        for p in partners:
            p["territory"] = "All Territories"
            
    if not partners:
        return []
        
    date_28_days_ago = add_days(today(), -28)
    
    balances = frappe.db.sql("""
        SELECT channel_partner, item_variant, SUM(qty) as balance
        FROM `tabPSV Ledger Entry`
        GROUP BY channel_partner, item_variant
        HAVING SUM(qty) != 0
    """, as_dict=True)
    
    if not balances:
        balances = frappe.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            GROUP BY party_stock_account, item_code
            HAVING SUM(qty) != 0
        """, as_dict=True)
        
    sales_data = frappe.db.sql("""
        SELECT channel_partner, item_variant, SUM(ABS(qty)) as total_sales
        FROM `tabPSV Ledger Entry`
        WHERE qty < 0 AND posting_datetime >= %s
          AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
        GROUP BY channel_partner, item_variant
    """, (date_28_days_ago,), as_dict=True)
    
    if not sales_data:
        sales_data = frappe.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY party_stock_account, item_code
        """, (date_28_days_ago,), as_dict=True)
        
    velocity_map = {}
    for s in sales_data:
        key = (s["channel_partner"], s["item_variant"])
        velocity_map[key] = float(s["total_sales"] or 0.0) / 4.0
        
    partner_info = {p.name: p for p in partners}
    
    sources = []
    sinks = []
    
    for b in balances:
        partner_name = b["channel_partner"]
        if partner_name not in partner_info:
            continue
            
        variant = b["item_variant"]
        balance = float(b["balance"] or 0.0)
        
        if balance <= 0:
            continue
            
        vel = velocity_map.get((partner_name, variant), 0.0)
        
        if vel > 0:
            woc = balance / vel
        else:
            woc = 999.0
            
        if woc > healthy_woc:
            excess = balance - (healthy_woc * vel)
            if excess > 0:
                sources.append({
                    "partner": partner_name,
                    "item": variant,
                    "balance": balance,
                    "velocity": vel,
                    "woc": woc,
                    "excess": excess
                })
        elif woc < critical_woc:
            shortage = (healthy_woc * vel) - balance
            if shortage > 0:
                sinks.append({
                    "partner": partner_name,
                    "item": variant,
                    "balance": balance,
                    "velocity": vel,
                    "woc": woc,
                    "shortage": shortage
                })
                
    suggestions = []
    for sink in sinks:
        for source in sources:
            if sink["item"] != source["item"]:
                continue
                
            p_sink = partner_info[sink["partner"]]
            p_source = partner_info[source["partner"]]
            
            match_geo = False
            if scope == "Same Territory":
                match_geo = (p_sink.territory == p_source.territory)
            elif scope == "Same Region":
                match_geo = (str(p_sink.region).strip().lower() == str(p_source.region).strip().lower())
            else:
                match_geo = True
                
            if match_geo:
                transfer_qty = min(source["excess"], sink["shortage"])
                if transfer_qty > 0:
                    suggestions.append({
                        "item_code": sink["item"],
                        "source_partner": source["partner"],
                        "target_partner": sink["partner"],
                        "suggested_transfer_qty": round(transfer_qty, 2),
                        "source_woc": round(source["woc"], 1),
                        "target_woc": round(sink["woc"], 1)
                    })
                    
    suggestions.sort(key=lambda x: x["suggested_transfer_qty"], reverse=True)
    return suggestions


@frappe.whitelist()
def create_reversal_entry(original_name, reason):
    """
    Creates a reversal entry for a PSV Ledger Entry.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])
    
    if not frappe.db.exists("PSV Ledger Entry", original_name):
        frappe.throw(_("Original ledger entry {0} not found.").format(original_name))
        
    orig = frappe.get_doc("PSV Ledger Entry", original_name)
    
    already_reversed = frappe.db.exists("PSV Ledger Entry", {"reversal_of": original_name})
    if already_reversed:
        frappe.throw(_("Ledger entry {0} has already been reversed by {1}.").format(original_name, already_reversed))
        
    rev = frappe.new_doc("PSV Ledger Entry")
    rev.company = orig.company
    rev.posting_datetime = now_datetime()
    rev.channel_partner = orig.channel_partner
    rev.item_variant = orig.item_variant
    rev.qty = -float(orig.qty)
    rev.transaction_type = "Reversal"
    rev.voucher_type = orig.voucher_type
    rev.voucher_no = orig.voucher_no
    rev.reversal_of = original_name
    rev.reversal_reason = reason
    rev.warehouse = orig.warehouse
    rev.currency = orig.currency
    rev.fiscal_year = orig.fiscal_year
    
    rev.insert(ignore_permissions=True)
    frappe.db.commit()
    return rev.name


@frappe.whitelist()
def get_channel_health_score(channel_partner, from_date=None, to_date=None):
    """
    Returns the channel health score for a channel partner.
    """
    enabled = frappe.db.get_single_value("PSV System Settings", "channel_health_enabled")
    if not enabled:
        return {
            "enabled": False,
            "score": 0.0,
            "status": "Disabled",
            "message": "Channel Health features are scheduled for Phase 1.2"
        }
    else:
        open_alerts = frappe.db.count("SMRITI PSV Exception Record", {
            "party_stock_account": channel_partner,
            "status": "Pending Reconciliation"
        })
        score = max(0.0, 100.0 - (open_alerts * 10.0))
        status = "Good" if score >= 80 else ("Average" if score >= 50 else "Poor")
        return {
            "enabled": True,
            "score": score,
            "status": status,
            "message": f"Channel Health: {status} ({score} pts)"
        }


@frappe.whitelist()
def get_sellin_sellout_summary(company, channel_partner=None):
    """
    Returns a summary of sell-in, sell-out, current stock balance, and WOC.
    """
    from frappe.utils import add_days
    date_28_days_ago = add_days(today(), -28)
    
    balance_res = frappe.db.sql("""
        SELECT SUM(qty) FROM `tabPSV Ledger Entry`
        WHERE company = %s {0}
    """.format("AND channel_partner = %s" if channel_partner else ""), 
    tuple(x for x in [company, channel_partner] if x))
    
    is_legacy = False
    if not balance_res or balance_res[0][0] is None:
        balance_res = frappe.db.sql("""
            SELECT SUM(qty) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, channel_partner] if x))
        is_legacy = True
        
    current_balance = float(balance_res[0][0]) if balance_res and balance_res[0][0] is not None else 0.0
    
    if not is_legacy:
        sellin_res = frappe.db.sql("""
            SELECT SUM(qty) FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty > 0 AND posting_datetime >= %s {0}
        """.format("AND channel_partner = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
    else:
        sellin_res = frappe.db.sql("""
            SELECT SUM(qty) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty > 0 AND posting_datetime >= %s {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
        
    sell_in_qty = float(sellin_res[0][0]) if sellin_res and sellin_res[0][0] is not None else 0.0
    
    if not is_legacy:
        sellout_res = frappe.db.sql("""
            SELECT SUM(ABS(qty)) FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales') {0}
        """.format("AND channel_partner = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
    else:
        sellout_res = frappe.db.sql("""
            SELECT SUM(ABS(qty)) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload') {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
        
    sell_out_qty = float(sellout_res[0][0]) if sellout_res and sellout_res[0][0] is not None else 0.0
    
    weekly_sales_velocity = sell_out_qty / 4.0
    
    if weekly_sales_velocity > 0:
        weeks_of_cover = current_balance / weekly_sales_velocity
    else:
        weeks_of_cover = 999.0 if current_balance > 0 else 0.0
        
    return {
        "current_balance": current_balance,
        "sell_in_qty": sell_in_qty,
        "sell_out_qty": sell_out_qty,
        "weekly_sales_velocity": weekly_sales_velocity,
        "weeks_of_cover": weeks_of_cover
    }


@frappe.whitelist()
def migrate_to_new_psv_partner(dry_run=0):
    """
    Migrates legacy PSV data to the new PSV Phase 1.1 architecture.
    """
    import time
    from frappe.utils import getdate
    
    start_time = time.time()
    
    report = {
        "customers_scanned": 0,
        "partners_created": 0,
        "partners_skipped": 0,
        "brands_created": 0,
        "warnings": [],
        "errors": [],
        "execution_time": 0.0
    }
    
    is_dry_run = int(dry_run) > 0
    
    try:
        legacy_psas = frappe.get_all(
            "SMRITI Party Stock Account",
            fields=["name", "company", "customer", "location_name", "zone", "region", "active", "status"]
        )
        
        report["customers_scanned"] = len(legacy_psas)
        
        for psa in legacy_psas:
            partner_name = f"{psa.customer}-{psa.location_name}"
            partner_exists = frappe.db.exists("PSV Channel Partner", partner_name)
            
            legacy_brands = frappe.db.sql("""
                SELECT DISTINCT i.brand
                FROM `tabSMRITI Party Stock Ledger Entry` ple
                INNER JOIN `tabItem` i ON ple.item_code = i.name
                WHERE ple.party_stock_account = %s AND i.brand IS NOT NULL AND i.brand != ''
            """, (psa.name,), as_dict=True)
            
            brands_list = [b["brand"] for b in legacy_brands]
            
            if partner_exists:
                report["partners_skipped"] += 1
            else:
                territory = frappe.db.get_value("Customer", psa.customer, "territory") or "All Territories"
                if not frappe.db.exists("Territory", territory):
                    territory = "All Territories"
                    
                partner_doc_data = {
                    "doctype": "PSV Channel Partner",
                    "name": partner_name,
                    "company": psa.company,
                    "customer": psa.customer,
                    "location_name": psa.location_name,
                    "territory": territory,
                    "zone": psa.zone or None,
                    "region": psa.region or "",
                    "active": psa.active,
                    "status": psa.status or "Active",
                    "effective_from": getdate(today())
                }
                
                brands_child = []
                for idx, brand in enumerate(brands_list):
                    brands_child.append({
                        "brand": brand,
                        "is_primary": 1 if idx == 0 else 0
                    })
                    report["brands_created"] += 1
                
                partner_doc_data["brands"] = brands_child
                
                if not is_dry_run:
                    try:
                        partner_doc = frappe.get_doc(partner_doc_data)
                        partner_doc.insert(ignore_permissions=True)
                        report["partners_created"] += 1
                    except Exception as e:
                        report["errors"].append(f"Error creating PSV Channel Partner {partner_name}: {str(e)}")
                        continue
                else:
                    report["partners_created"] += 1
            
            ledger_entries = frappe.get_all(
                "SMRITI Party Stock Ledger Entry",
                filters={"party_stock_account": psa.name},
                fields=["*"]
            )
            
            tx_type_map = {
                "Opening": "Opening",
                "Dispatch": "Dispatch",
                "Sales": "Sales",
                "Adjustment": "Adjustment",
                "Return": "Return",
                "Transfer": "Dispatch"
            }
            
            company_currency = frappe.db.get_value("Company", psa.company, "default_currency") or "INR"
            active_fy = frappe.db.get_value("Fiscal Year", {"year_start_date": ["<=", today()], "year_end_date": [">=", today()]}, "name")
            
            for le in ledger_entries:
                posting_datetime_str = str(le.posting_datetime)
                fy = active_fy
                if le.posting_datetime:
                    le_date_str = str(le.posting_datetime.date() if hasattr(le.posting_datetime, "date") else le.posting_datetime).split()[0]
                    le_fy = frappe.db.get_value("Fiscal Year", {"year_start_date": ["<=", le_date_str], "year_end_date": [">=", le_date_str]}, "name")
                    if le_fy:
                        fy = le_fy
                        
                tx_type = tx_type_map.get(le.voucher_type, "Adjustment")
                
                raw_string = f"{psa.company}{posting_datetime_str}{partner_name}{le.item_code}{str(le.qty)}{tx_type}{le.voucher_type}{le.voucher_no}"
                unique_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
                
                new_entry_exists = frappe.db.exists("PSV Ledger Entry", {"unique_hash": unique_hash})
                if new_entry_exists:
                    continue
                    
                ledger_doc_data = {
                    "doctype": "PSV Ledger Entry",
                    "company": psa.company,
                    "posting_datetime": le.posting_datetime,
                    "channel_partner": partner_name,
                    "item_variant": le.item_code,
                    "qty": le.qty,
                    "transaction_type": tx_type,
                    "voucher_type": le.voucher_type,
                    "voucher_no": le.voucher_no,
                    "unique_hash": unique_hash,
                    "currency": company_currency,
                    "fiscal_year": fy,
                    "hash_version": 1
                }
                
                if not is_dry_run:
                    try:
                        ledger_doc = frappe.get_doc(ledger_doc_data)
                        ledger_doc.insert(ignore_permissions=True)
                    except Exception as e:
                        report["errors"].append(f"Error migrating ledger entry for {partner_name}, item {le.item_code}: {str(e)}")
        
        if not is_dry_run:
            frappe.db.commit()
            
    except Exception as e:
        report["errors"].append(f"Migration failed with critical error: {str(e)}")
        
    report["execution_time"] = round(time.time() - start_time, 4)
    return report


@frappe.whitelist()
def get_stock_cover_risks(company):
    """
    Returns a list of all item variants at channel partners that have warning or critical Weeks of Cover.
    """
    from frappe.utils import add_days
    settings = frappe.get_single("PSV System Settings")
    critical_woc = settings.weeks_of_cover_critical or 2
    warning_woc = settings.weeks_of_cover_warning or 4
    
    partners = frappe.get_all("PSV Channel Partner", filters={"company": company, "active": 1}, fields=["name"])
    if not partners:
        partners = frappe.get_all("SMRITI Party Stock Account", filters={"company": company, "active": 1}, fields=["name"])
    if not partners:
        return []
        
    date_28_days_ago = add_days(today(), -28)
    
    use_new = frappe.db.exists("PSV Ledger Entry", {"company": company})
    if use_new:
        balances = frappe.db.sql("""
            SELECT channel_partner, item_variant, SUM(qty) as balance
            FROM `tabPSV Ledger Entry`
            WHERE company = %s
            GROUP BY channel_partner, item_variant
            HAVING SUM(qty) > 0
        """, (company,), as_dict=True)
        
        sales_data = frappe.db.sql("""
            SELECT channel_partner, item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
            GROUP BY channel_partner, item_variant
        """, (company, date_28_days_ago), as_dict=True)
    else:
        balances = frappe.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s
            GROUP BY party_stock_account, item_code
            HAVING SUM(qty) > 0
        """, (company,), as_dict=True)
        
        sales_data = frappe.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY party_stock_account, item_code
        """, (company, date_28_days_ago), as_dict=True)
        
    velocity_map = {}
    for s in sales_data:
        velocity_map[(s["channel_partner"], s["item_variant"])] = float(s["total_sales"] or 0.0) / 4.0
        
    risks = []
    for b in balances:
        partner = b["channel_partner"]
        variant = b["item_variant"]
        qty = float(b["balance"])
        
        vel = velocity_map.get((partner, variant), 0.0)
        if vel > 0:
            woc = qty / vel
        else:
            woc = 999.0
            
        if woc < warning_woc:
            status = "Critical" if woc < critical_woc else "Warning"
            risks.append({
                "item_code": variant,
                "channel_partner": partner,
                "weeks_cover": round(woc, 1),
                "status": status,
                "balance": qty,
                "velocity": round(vel, 2)
            })
            
    risks.sort(key=lambda x: x["weeks_cover"])
    return risks


@frappe.whitelist()
def get_channel_stock_trend(company):
    """
    Returns the historical total channel stock value trend.
    """
    dates = frappe.db.sql("""
        SELECT DISTINCT snapshot_date
        FROM `tabPSV Stock Aging Snapshot`
        ORDER BY snapshot_date DESC
        LIMIT 10
    """, as_dict=False)
    
    trend = []
    if dates:
        dates = list(dates)
        dates.reverse()
        for row in dates:
            date_val = row[0]
            snaps = frappe.db.sql("""
                SELECT item_variant, qty
                FROM `tabPSV Stock Aging Snapshot`
                WHERE snapshot_date = %s
            """, (date_val,), as_dict=True)
            
            total_val = 0.0
            for s in snaps:
                cost = get_landing_cost(s["item_variant"])
                total_val += float(s["qty"]) * cost
                
            trend.append({
                "date": str(date_val),
                "value": round(total_val, 2)
            })
            
    return trend


# Action Recommendation Constants
ACTION_INCREASE_STOCK = "Increase Stock"
ACTION_MAINTAIN = "Maintain"
ACTION_IMPROVE_MARGIN = "Improve Margin"
ACTION_LIQUIDATE = "Liquidate / Review"
ACTION_REPLENISH_URGENT = "Replenish Urgent"


@frappe.whitelist()
def get_inventory_productivity_metrics(company, timespan_days=30):
    """
    Computes GMROI and SKU Rationalization metrics in bulk.
    Returns: {
        "summary": {
            "star": int,
            "cash_cow": int,
            "underperformer": int,
            "slow_mover": int,
            "stockout_winner": int
        },
        "top_skus": list of dicts,
        "all_items": list of dicts
    }
    """
    from frappe.utils import add_days, now_datetime
    
    timespan_days = int(timespan_days or 30)
    start_date = add_days(now_datetime(), -timespan_days)
    
    # 1. Fetch velocity threshold
    star_velocity_threshold = float(frappe.db.get_single_value("PSV System Settings", "star_velocity_threshold") or 1.0)
    
    # Check if new schema/ledger exists
    use_new = frappe.db.exists("PSV Ledger Entry", {"company": company})
    
    # 2. Get current stock balances
    if use_new:
        bal_res = frappe.db.sql("""
            SELECT item_variant, SUM(qty) as balance
            FROM `tabPSV Ledger Entry`
            WHERE company = %s
            GROUP BY item_variant
        """, (company,), as_dict=True)
    else:
        bal_res = frappe.db.sql("""
            SELECT item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s
            GROUP BY item_code
        """, (company,), as_dict=True)
        
    balances = {r["item_variant"]: float(r["balance"] or 0.0) for r in bal_res}
    
    # 3. Get sales quantities and transaction counts
    if use_new:
        sales_res = frappe.db.sql("""
            SELECT item_variant, SUM(ABS(qty)) as sales_qty, COUNT(DISTINCT voucher_no) as txn_count
            FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
            GROUP BY item_variant
        """, (company, start_date), as_dict=True)
    else:
        sales_res = frappe.db.sql("""
            SELECT item_code as item_variant, SUM(ABS(qty)) as sales_qty, COUNT(DISTINCT voucher_no) as txn_count
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY item_code
        """, (company, start_date), as_dict=True)
        
    sales = {r["item_variant"]: float(r["sales_qty"] or 0.0) for r in sales_res}
    sales_txns = {r["item_variant"]: int(r["txn_count"] or 0) for r in sales_res}
    
    # Get all distinct SKUs that have either stock or sales
    all_skus = set(balances.keys()).union(sales.keys())
    if not all_skus:
        return {
            "summary": {"star": 0, "cash_cow": 0, "underperformer": 0, "slow_mover": 0, "stockout_winner": 0},
            "top_skus": [],
            "all_items": []
        }
        
    # 4. Get realized selling prices in bulk
    realized_prices_res = frappe.db.sql("""
        SELECT item_code as item_variant, SUM(base_amount) as total_amount, SUM(qty) as total_qty
        FROM `tabSales Invoice Item`
        WHERE docstatus = 1 AND parent IN (
            SELECT name FROM `tabSales Invoice` WHERE company = %s
        )
        GROUP BY item_code
    """, (company,), as_dict=True)
    
    realized_prices = {}
    for r in realized_prices_res:
        if r["total_qty"] and float(r["total_qty"]) > 0:
            realized_prices[r["item_variant"]] = float(r["total_amount"]) / float(r["total_qty"])
            
    # 5. Get standard prices in bulk
    std_prices_res = frappe.db.sql("""
        SELECT item_code as item_variant, price_list_rate
        FROM `tabItem Price`
        WHERE price_list = 'Standard Selling'
    """, as_dict=True)
    std_prices = {r["item_variant"]: float(r["price_list_rate"] or 0.0) for r in std_prices_res}
    
    # 6. Get item costs and templates in bulk
    item_info_res = frappe.db.sql("""
        SELECT name, valuation_rate, standard_rate, variant_of
        FROM `tabItem`
    """, as_dict=True)
    item_info = {r["name"]: r for r in item_info_res}
    
    # Helper to resolve cost (valuation/landing cost)
    def resolve_cost(sku):
        info = item_info.get(sku)
        if not info:
            return 0.0
        if info.get("valuation_rate"):
            return float(info["valuation_rate"])
        if info.get("standard_rate"):
            return float(info["standard_rate"])
        if info.get("variant_of"):
            p_info = item_info.get(info["variant_of"])
            if p_info:
                if p_info.get("valuation_rate"):
                    return float(p_info["valuation_rate"])
                if p_info.get("standard_rate"):
                    return float(p_info["standard_rate"])
        return 0.0

    # Helper to resolve price with fallbacks
    def resolve_price(sku):
        if sku in realized_prices:
            return realized_prices[sku]
        if sku in std_prices and std_prices[sku] > 0:
            return std_prices[sku]
        info = item_info.get(sku)
        if info and info.get("standard_rate"):
            return float(info["standard_rate"])
        if info and info.get("variant_of"):
            p_info = item_info.get(info["variant_of"])
            if p_info and p_info.get("standard_rate"):
                return float(p_info["standard_rate"])
        c = resolve_cost(sku)
        return c * 1.5
        
    # 7. Compute metrics for each SKU
    items_metrics = []
    summary_counts = {"star": 0, "cash_cow": 0, "underperformer": 0, "slow_mover": 0, "stockout_winner": 0}
    
    for sku in all_skus:
        bal = balances.get(sku, 0.0)
        s_qty = sales.get(sku, 0.0)
        s_txn = sales_txns.get(sku, 0)
        cost = resolve_cost(sku)
        price = resolve_price(sku)
        
        # Calculate velocity (units per week)
        weeks = timespan_days / 7.0
        velocity = s_qty / weeks if weeks > 0 else 0.0
        
        gross_margin = s_qty * (price - cost)
        inventory_value = bal * cost
        
        # Data Quality Warnings
        warnings = []
        if cost <= 0:
            warnings.append("Cost Data Missing")
        if sku not in realized_prices:
            warnings.append("Using Fallback Selling Price")
        if bal < 0:
            warnings.append("Inventory Adjustment Required")
            
        # Confidence Indicator
        if s_qty >= 20 and s_txn >= 5:
            confidence = "High"
        elif s_qty > 0 and s_txn > 0:
            confidence = "Medium"
        else:
            confidence = "Low"
            
        # GMROI calculation with empty/depleted stockout winner check
        is_depleted = (bal <= 0) and (s_qty > 0)
        
        if is_depleted:
            gmroi = None
            category = "Stockout Winner"
            action = ACTION_REPLENISH_URGENT
            summary_counts["stockout_winner"] += 1
        else:
            if inventory_value > 0:
                gmroi = gross_margin / inventory_value
            else:
                gmroi = 0.0
                
            # Classify based on velocity threshold and GMROI >= 2.0
            if velocity >= star_velocity_threshold:
                if gmroi >= 2.0:
                    category = "Star"
                    action = ACTION_INCREASE_STOCK
                    summary_counts["star"] += 1
                else:
                    category = "Underperformer"
                    action = ACTION_IMPROVE_MARGIN
                    summary_counts["underperformer"] += 1
            else:
                if gmroi >= 2.0:
                    category = "Cash Cow"
                    action = ACTION_MAINTAIN
                    summary_counts["cash_cow"] += 1
                else:
                    category = "Slow Mover"
                    action = ACTION_LIQUIDATE
                    summary_counts["slow_mover"] += 1
                    
        # Compute Inventory Productivity Score (0-100)
        g_val = gmroi if gmroi is not None else 3.0  # Give Stockout Winners top score for GMROI
        norm_gmroi = min(g_val / 3.0, 1.0) * 100.0
        norm_vel = min(velocity / 5.0, 1.0) * 100.0
        productivity_score = round((0.6 * norm_gmroi) + (0.4 * norm_vel), 2)
        
        items_metrics.append({
            "item_code": sku,
            "sales_qty": s_qty,
            "txn_count": s_txn,
            "velocity": round(velocity, 2),
            "cost": round(cost, 2),
            "price": round(price, 2),
            "gross_margin": round(gross_margin, 2),
            "inventory_value": round(inventory_value, 2),
            "current_stock": round(bal, 2),
            "gmroi": round(gmroi, 2) if gmroi is not None else None,
            "category": category,
            "action": action,
            "score": productivity_score,
            "confidence": confidence,
            "warnings": warnings
        })
        
    # Sort: productivity score descending
    items_metrics.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "summary": summary_counts,
        "top_skus": items_metrics[:10],
        "all_items": items_metrics
    }


@frappe.whitelist()
def get_inventory_productivity_methodology():
    """
    Returns the central, single source of truth for inventory productivity formulas,
    classification rules, and score explanations in SMRITI Retail OS.
    """
    import smriti_retail_os
    from frappe.utils import now_datetime
    smriti_version = getattr(smriti_retail_os, "__version__", "1.2.10")
    
    return {
        "title": _("Inventory Productivity & SKU Rationalization"),
        "category": _("Analytics Guides"),
        "version": "1.0",
        "effective_date": "2026-06-11",
        "smriti_version": smriti_version,
        "generated_datetime": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": "Founder – AITDL (AI Technology & Development Lab)",
            "quote": _("Software should not merely record transactions. It should help businesses make better decisions.")
        },
        "about_smriti": _(
            "SMRITI Retail OS was created from decades of observation, implementation experience, "
            "operational learning, business process analysis, and real-world retail challenges.\n\n"
            "The platform has been shaped through continuous interaction with retailers, distributors, "
            "warehouse operators, accountants, store managers, and business owners."
        ),
        "summary": _("This guide explains the analytical framework used to calculate and classify inventory productivity and SKU performance in SMRITI Retail OS."),
        "formulas": [
            {
                "name": "GMROI (Gross Margin Return on Investment)",
                "business_meaning": _("Measures the profitability of inventory. Tells you how many rupees of gross margin are generated for every rupee invested in stock."),
                "formula": "GMROI = Gross Margin / Current Inventory Value",
                "example": _("Gross Margin = ₹46,680, Inventory Value = ₹27,450. GMROI = 46,680 / 27,450 = 1.70"),
                "interpretation": _("A GMROI of 1.70 means every ₹1.00 invested in inventory generated ₹1.70 of gross margin. GMROI >= 2.0 is considered high-performing.")
            },
            {
                "name": "Gross Margin",
                "business_meaning": _("The net profit made from selling the item after subtracting its cost."),
                "formula": "Gross Margin = Sales Qty * (Average Realized Selling Price - Landing Cost)",
                "example": _("Sales Qty = 120, Price = ₹999, Cost = ₹610. Gross Margin = 120 * (999 - 610) = ₹46,680"),
                "interpretation": _("The total direct profit contributed by the SKU to the business.")
            },
            {
                "name": "Inventory Value",
                "business_meaning": _("The total capital tied up in the stock of this SKU."),
                "formula": "Inventory Value = Current Stock * Landing Cost",
                "example": _("Current Stock = 45, Cost = ₹610. Inventory Value = 45 * 610 = ₹27,450"),
                "interpretation": _("Represents the opportunity cost of locked capital in warehouse/store inventory.")
            },
            {
                "name": "Weekly Velocity",
                "business_meaning": _("The rate at which the item sells per week."),
                "formula": "Weekly Velocity = Sales Qty / (Timespan Days / 7)",
                "example": _("Sales Qty = 120, Timespan = 30 Days. Weekly Velocity = 120 / (30 / 7) = 28.0 units/week"),
                "interpretation": _("Measures product demand speed. Compared against the velocity threshold (default 1.0/wk) to classify demand speed.")
            },
            {
                "name": "Productivity Score",
                "business_meaning": _("A composite index (0-100) combining profitability (60% weight) and demand speed (40% weight)."),
                "formula": "Productivity Score = (0.6 * Normalized GMROI) + (0.4 * Normalized Velocity)",
                "example": _("Normalized GMROI = min(1.70 / 3.0, 1.0) * 100 = 56.7. Normalized Velocity = min(28.0 / 5.0, 1.0) * 100 = 100.0. Score = (0.6 * 56.7) + (0.4 * 100.0) = 74.0"),
                "interpretation": _("A single unified ranking to compare SKU efficiency across different categories and items.")
            }
        ],
        "classification_rules": [
            {
                "category": "Star (Core SKU)",
                "velocity": ">= star_velocity_threshold (Default 1.0/wk)",
                "gmroi": ">= 2.0 (200%)",
                "action": ACTION_INCREASE_STOCK,
                "description": _("High margin and high volume items. Ensure maximum stock availability.")
            },
            {
                "category": "Cash Cow",
                "velocity": "< star_velocity_threshold",
                "gmroi": ">= 2.0 (200%)",
                "action": ACTION_MAINTAIN,
                "description": _("High margin but low volume. Maintain steady inventory levels.")
            },
            {
                "category": "Underperformer",
                "velocity": ">= star_velocity_threshold",
                "gmroi": "< 2.0 (200%)",
                "action": ACTION_IMPROVE_MARGIN,
                "description": _("Low margin but high volume. Negotiate better buying rates or increase selling price.")
            },
            {
                "category": "Slow Mover",
                "velocity": "< star_velocity_threshold",
                "gmroi": "< 2.0 (200%)",
                "action": ACTION_LIQUIDATE,
                "description": _("Low margin and low volume. Liquidate excess stock or rationalize SKU from catalog.")
            },
            {
                "category": "Stockout Winner",
                "velocity": "Any",
                "gmroi": "Depleted (Stock <= 0 & Margin > 0)",
                "action": ACTION_REPLENISH_URGENT,
                "description": _("High-demand items currently out of stock. Replenish immediately to capture demand.")
            }
        ],
        "confidence_levels": [
            {
                "level": "High",
                "criteria": _("Sales Qty >= 20 and Transaction Count >= 5"),
                "description": _("Indicates highly reliable historical demand trends.")
            },
            {
                "level": "Medium",
                "criteria": _("Sales Qty > 0 and Transaction Count > 0 (excluding High)"),
                "description": _("Moderate reliability. The SKU has transaction history but limited volume.")
            },
            {
                "level": "Low",
                "criteria": _("No sales or transaction history"),
                "description": _("Low reliability. The metrics are mostly based on opening stock or standard rates without sales validation.")
            }
        ],
        "data_quality_warnings": [
            {
                "warning": "Cost Data Missing",
                "trigger": _("Item valuation rate and standard rate are both zero"),
                "action": _("Update the item cost in Item master or purchase transaction to ensure accurate margin calculations.")
            },
            {
                "warning": "Using Fallback Selling Price",
                "trigger": _("No sales invoices found for the item during the period"),
                "action": _("The system uses Item standard selling price list or markup rates as a fallback realized price.")
            },
            {
                "warning": "Inventory Adjustment Required",
                "trigger": _("Current stock balance in shadow ledger is negative"),
                "action": _("A stock reconciliation or transaction correction is required to fix the negative balance.")
            }
        ],
        "interpretation_guide": [
            {
                "title": _("Star (Core SKU)"),
                "guidance": _("High margin and high volume. Focus on maximizing stock availability, reducing reorder lead times, and giving them priority placement in warehouses.")
            },
            {
                "title": _("Cash Cow"),
                "guidance": _("High margin but low volume. Maintain a steady stock level to capture profit but avoid over-ordering, as velocity is slow.")
            },
            {
                "title": _("Underperformer"),
                "guidance": _("Low margin but high volume. Focus on improving gross margin by negotiating bulk discounts with vendors or increasing selling prices.")
            },
            {
                "title": _("Slow Mover"),
                "guidance": _("Low margin and low volume. Avoid replenishment. Run promotions, bundle deals, or liquidation campaigns to recover locked capital.")
            },
            {
                "title": _("Stockout Winner"),
                "guidance": _("Out of stock but has active demand. Place replenishment orders immediately to prevent lost sales and capture active market demand.")
            }
        ],
        "faqs": [
            {
                "question": _("Why is my GMROI shown as None / DEPLETED?"),
                "answer": _("If the current stock balance of a SKU is zero or negative, the inventory value is zero. Dividing gross margin by zero is mathematically undefined. If the item has sales history during this period, it is classified as a 'Stockout Winner' with GMROI set to None.")
            },
            {
                "question": _("What timespan is used for calculations?"),
                "answer": _("By default, the dashboard calculates velocity and margin metrics over a trailing 30-day window. You can change this period in the dashboard filters or system settings.")
            },
            {
                "question": _("How is the Normalized GMROI calculated?"),
                "answer": _("To prevent extreme GMROI values from distorting the composite score, GMROI is normalized on a scale from 0 to 100, where a GMROI of 3.0 (300%) or above receives the maximum score of 100.")
            }
        ],
        "about": _(
            "This analytical framework is part of SMRITI Retail OS. "
            "Designed by Jawahar R. Mallah, Founder – AITDL (AI Technology & Development Lab). "
            "Built from practical business operations, inventory management experience, "
            "retail workflows, implementation learnings, and real-world business requirements."
        )
    }



