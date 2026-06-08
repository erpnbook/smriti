# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/psv_service.py
# @description: Handles user login, registration, and JWT token generation.
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
import frappe
from frappe import _
from frappe.utils import get_datetime, today, now_datetime
from smriti_retail_os.ledger_engine import make_ledger_entry, log_activity
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances

# ─── SALES INVOICE HOOKS ──────────────────────────────────────────────────────

def get_posting_datetime(doc):
    """
    Safely combines ERPNext posting_date and posting_time into a Python datetime object.
    """
    if doc.posting_date and doc.posting_time:
        return get_datetime(f"{doc.posting_date} {doc.posting_time}")
    return get_datetime(doc.posting_date or today())

def process_sales_invoice_submit(doc, method=None):
    """Called on Sales Invoice on_submit hook"""
    if not doc.get("custom_party_stock_account"):
        return

    posting_dt = get_posting_datetime(doc)
    multiplier = -1.0 if doc.is_return else 1.0
    voucher_type = "Return" if doc.is_return else "Dispatch"

    for item in doc.items:
        make_ledger_entry(
            company=doc.company,
            posting_datetime=posting_dt,
            party_stock_account=doc.custom_party_stock_account,
            item_code=item.item_code,
            qty=item.qty * multiplier,
            voucher_type=voucher_type,
            voucher_no=doc.name
        )
    
    log_activity(
        action_type="Submit Dispatch" if not doc.is_return else "Submit Return",
        party_stock_account=doc.custom_party_stock_account,
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        details=f"Auto-dispatch of {len(doc.items)} items created from invoice submission."
    )

def validate_sales_invoice_cancel(doc, method=None):
    """Called on Sales Invoice before_cancel hook"""
    if not doc.get("custom_party_stock_account") or doc.is_return:
        return

    # Check if cancellation will result in a negative balance
    party_stock_account = doc.custom_party_stock_account
    triggered_exceptions = []

    for item in doc.items:
        current_bal = get_party_balance(party_stock_account, item.item_code)
        # Cancelling invoice removes dispatched quantity from the location
        new_bal = current_bal - item.qty
        if new_bal < 0.0:
            triggered_exceptions.append({
                "item_code": item.item_code,
                "missing_qty": abs(new_bal)
            })

    if triggered_exceptions:
        # Instead of blocking cancellation (avoiding deadlock), allow it but generate exception records
        frappe.db.set_value("SMRITI Party Stock Account", party_stock_account, "status", "Pending Reconciliation")
        
        for exc in triggered_exceptions:
            ex_rec = frappe.get_doc({
                "doctype": "SMRITI PSV Exception Record",
                "timestamp": now_datetime(),
                "party_stock_account": party_stock_account,
                "sales_invoice": doc.name,
                "item_code": exc["item_code"],
                "missing_qty": exc["missing_qty"],
                "status": "Pending Reconciliation"
            })
            ex_rec.flags.ignore_permissions = True
            ex_rec.insert()

        log_activity(
            action_type="Reconciliation Alert",
            party_stock_account=party_stock_account,
            reference_doctype="Sales Invoice",
            reference_name=doc.name,
            details=f"Invoice cancellation allowed. Created {len(triggered_exceptions)} pending exception records due to negative balances."
        )

def process_sales_invoice_cancel(doc, method=None):
    """Called on Sales Invoice on_cancel hook"""
    if not doc.get("custom_party_stock_account"):
        return

    posting_dt = now_datetime()
    multiplier = 1.0 if doc.is_return else -1.0
    voucher_type = "Dispatch" if doc.is_return else "Return"

    for item in doc.items:
        make_ledger_entry(
            company=doc.company,
            posting_datetime=posting_dt,
            party_stock_account=doc.custom_party_stock_account,
            item_code=item.item_code,
            qty=item.qty * multiplier,
            voucher_type=voucher_type,
            voucher_no=f"VOID-{doc.name}",
            reason=_("Sales Invoice Cancelled")
        )
    
    log_activity(
        action_type="Cancel Dispatch" if not doc.is_return else "Cancel Return",
        party_stock_account=doc.custom_party_stock_account,
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        details="Ledger adjustment written to reverse dispatched quantities."
    )


# ─── WEEKLY SALES UPLOAD ──────────────────────────────────────────────────────

def validate_sales_upload(doc):
    """Gathers MD5 validation and period locks validation"""
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

    # 5. Overselling checks (Validate Qty against current balances)
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
            # Fallback mock for testing environment without openpyxl
            pass

def process_sales_upload_submit(doc):
    """Inserts negative entries to Shadow Ledger"""
    frappe.db.set_value(doc.doctype, doc.name, "status", "Imported")
    
    for item in doc.items:
        make_ledger_entry(
            company=doc.company,
            posting_datetime=get_datetime(f"{item.date} 18:00:00") if item.date else now_datetime(),
            party_stock_account=doc.party_stock_account,
            item_code=item.item_code,
            qty=item.qty_sold * -1.0, # Negative for sales
            voucher_type="Sales",
            voucher_no=doc.name
        )

    log_activity(
        action_type="Upload Sales",
        party_stock_account=doc.party_stock_account,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        details=f"Weekly sales file imported with {len(doc.items)} records. Shadow balance decremented."
    )

def process_sales_upload_cancel(doc):
    """Reverses weekly sales entries"""
    frappe.db.set_value(doc.doctype, doc.name, "status", "Draft")

    for item in doc.items:
        make_ledger_entry(
            company=doc.company,
            posting_datetime=now_datetime(),
            party_stock_account=doc.party_stock_account,
            item_code=item.item_code,
            qty=item.qty_sold, # Reversing positive
            voucher_type="Sales",
            voucher_no=f"VOID-{doc.name}",
            reason=_("Import Cancelled")
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
    """Writes audit variance entries to Shadow Ledger"""
    if doc.status != "Approved":
        frappe.throw(_("Audit Snapshots must be explicitly approved by a Store Manager or Administrator before submitting."))

    # Save approval details
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()

    for item in doc.items:
        if item.variance == 0.0:
            continue

        adj_type = "Surplus Correction" if item.variance > 0.0 else "Shrinkage"
        make_ledger_entry(
            company=doc.company,
            posting_datetime=get_datetime(doc.audit_date),
            party_stock_account=doc.party_stock_account,
            item_code=item.item_code,
            qty=item.variance, # Positive for surplus, negative for shrinkage
            voucher_type="Adjustment",
            voucher_no=doc.name,
            adjustment_type=adj_type,
            reason=item.variance_reason,
            approved_by=doc.approved_by,
            approved_on=doc.approved_on
        )

    log_activity(
        action_type="Approve Snapshot",
        party_stock_account=doc.party_stock_account,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        details=f"Physical snapshot approved and adjustment ledger entries written."
    )

def process_physical_snapshot_cancel(doc):
    """Reverses physical stock audit adjustments"""
    doc.approved_by = None
    doc.approved_on = None

    for item in doc.items:
        if item.variance == 0.0:
            continue

        make_ledger_entry(
            company=doc.company,
            posting_datetime=now_datetime(),
            party_stock_account=doc.party_stock_account,
            item_code=item.item_code,
            qty=item.variance * -1.0, # Reverse entry
            voucher_type="Adjustment",
            voucher_no=f"VOID-{doc.name}",
            reason=_("Snapshot Cancelled")
        )

    log_activity(
        action_type="Cancel Dispatch",
        party_stock_account=doc.party_stock_account,
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        details="Audit snapshot cancelled and adjustments reversed."
    )


# ─── OPENING BALANCES LOADER ──────────────────────────────────────────────────

def import_opening_balances(company, party_stock_account, items_data):
    """
    Programmatic helper to seed opening stock lying at a customer outlet location.
    items_data should be a list of dicts: [{'item_code': 'X', 'qty': 100}]
    """
    posting_dt = now_datetime()
    
    for row in items_data:
        make_ledger_entry(
            company=company,
            posting_datetime=posting_dt,
            party_stock_account=party_stock_account,
            item_code=row["item_code"],
            qty=row["qty"],
            voucher_type="Opening",
            voucher_no="OPENING-BALANCE-IMPORT"
        )

    log_activity(
        action_type="Opening Balance Import",
        party_stock_account=party_stock_account,
        details=f"Imported initial opening balances for {len(items_data)} items."
    )
