# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/psv_integration.py
# @description: PSV integration hooks for Delivery Note and Stock Entry events.
#               Handles Inventory Visibility Layer entries for channel stock operations.
#
# ─── Architecture Note ───────────────────────────────────────────────────────
# This module is called by Frappe document event hooks (hooks.py).
# It bridges ERPNext Delivery Notes and Stock Entries into the PSV Inventory Visibility Layer
# WITHOUT mutating the ERPNext Stock Ledger Entry or GL Entry.
#
# PSV SPECIAL RULE (GEMINI.md):
#   - MUST NOT modify tabStock Ledger Entry
#   - MUST NOT modify tabGL Entry
#   - MUST use its own Inventory Visibility Layer only (SMRITI Party Stock Ledger Entry)
#
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-11
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _


# ─── Delivery Note PSV Integration ───────────────────────────────────────────

def handle_delivery_note_submit(doc, method=None):
    """
    Called on Delivery Note submission (on_submit hook).

    Creates a TRANSFER_OUT PSV transaction for each item in the DN,
    ONLY if the DN carries custom_party_stock_account (explicit operator action).

    ─── PSV Activation Intent ────────────────────────────────────────────────
    PSV fires ONLY when custom_party_stock_account is set on the Delivery Note.
    This field is set manually by the operator — it does NOT auto-populate.
    Therefore:
      - DN from Sales Order: PSV fires only if operator added PSA to the DN.
      - Standard B2B delivery: PSV does NOT fire (no PSA set).

    ─── Edge Cases Handled ───────────────────────────────────────────────────
    DN Amendments:  If this DN was created as an amendment of another DN,
                    the original DN's PSV transaction already covers the old qty.
                    The amendment will create its own TRANSFER_OUT for the
                    revised quantities. No double-counting occurs because
                    the original DN's PSV TX is voided on cancellation.

    Partial Returns: Partial returns flow through the Delivery Note Return
                    (a separate DN with is_return=1 and negative qtys).
                    The on_submit hook fires on the Return DN, which is handled
                    by the same function — negative qtys are passed to
                    create_psv_transaction which creates a RETURN type entry.
                    No special handling is needed here.

    ARCHITECTURE: Reads ERPNext DN data, writes SMRITI Inventory Visibility Layer only.
    No SLE or GL mutation occurs here.
    ──────────────────────────────────────────────────────────────────────────
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return  # Not a PSV-linked DN — pass through cleanly

    # Guard: Skip if this is a return DN with negative qty (handled as RETURN type below)
    # For DN returns (is_return = 1), flip the transaction_type to RETURN
    is_return = bool(doc.get("is_return"))
    transaction_type = "RETURN" if is_return else "TRANSFER_OUT"

    try:
        from smriti_retail_os.psv_service import create_psv_transaction, get_posting_datetime

        # Use abs(qty) — PSV records magnitude; direction is determined by transaction_type
        items_data = [
            {
                "item_code": i.item_code,
                "qty": abs(i.qty),    # DN returns have negative qty in ERPNext
                "rate": i.rate or 0.0
            }
            for i in doc.items
            if i.item_code and i.qty
        ]
        if not items_data:
            return

        so_ref = doc.get("against_sales_order") or ""
        remark_prefix = "Return via" if is_return else "Dispatched via"
        so_note = f" (SO: {so_ref})" if so_ref else ""

        create_psv_transaction(
            psa=psa,
            transaction_type=transaction_type,
            items=items_data,
            company=doc.company,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            remarks=f"{remark_prefix} Delivery Note: {doc.name}{so_note}",
            posting_date=get_posting_datetime(doc),
        )

    except Exception:
        frappe.log_error(
            title=f"PSV DN Submit Error: {doc.name}",
            message=frappe.get_traceback()
        )
        # Create exception record for operational health monitoring
        _create_dn_exception_record(doc, psa, "Hook Failure", "Delivery Note submit hook failed.")



def handle_delivery_note_cancel(doc, method=None):
    """
    Called on Delivery Note cancellation (on_cancel hook).

    Cancels the associated SMRITI PSV Transaction, which fires
    the on_cancel handler that writes VOID entries restoring the shadow balance.

    ARCHITECTURE: Reversal is delegated to SMRITI PSV Transaction.cancel()
    which handles sign-correct VOID entry creation internally.
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    try:
        tx_name = frappe.db.get_value(
            "SMRITI PSV Transaction",
            {
                "reference_doctype": doc.doctype,
                "reference_name": doc.name,
                "docstatus": 1
            },
            "name"
        )
        if tx_name:
            frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()
        else:
            frappe.log_error(
                title=f"PSV DN Cancel — No TX found: {doc.name}",
                message=(
                    f"Delivery Note {doc.name} cancelled but no submitted PSV Transaction "
                    f"was found for party_stock_account={psa}. "
                    f"Shadow balance may need manual reconciliation."
                )
            )
    except Exception:
        frappe.log_error(
            title=f"PSV DN Cancel Error: {doc.name}",
            message=frappe.get_traceback()
        )
        _create_dn_exception_record(doc, psa, "Hook Failure", "Delivery Note cancel hook failed.")


# ─── Stock Entry PSV Integration (Sales Returns) ─────────────────────────────

def handle_sales_return_submit(doc, method=None):
    """
    Called on Stock Entry submission (on_submit hook).

    Handles PSV Inventory Visibility Layer for Sales Returns received back from a
    SMRITI Party Stock Account (stock_entry_type = "Material Receipt" or
    custom_party_stock_account is set).

    ARCHITECTURE: Only fires if custom_party_stock_account is on the Stock Entry.
    Creates a RETURN transaction (positive qty — restoring balance).
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    # Only process return-type entries
    entry_type = doc.get("stock_entry_type") or ""
    if entry_type not in ("Material Receipt", "Material Transfer"):
        # Not a return — skip
        return

    try:
        from smriti_retail_os.psv_service import create_psv_transaction

        items_data = [
            {"item_code": i.item_code, "qty": i.qty, "rate": i.basic_rate or 0.0}
            for i in doc.items
            if i.item_code and i.qty
        ]
        if not items_data:
            return

        create_psv_transaction(
            psa=psa,
            transaction_type="RETURN",
            items=items_data,
            company=doc.company,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            remarks=f"Stock return via Stock Entry: {doc.name}",
        )

    except Exception:
        frappe.log_error(
            title=f"PSV SE Submit Error: {doc.name}",
            message=frappe.get_traceback()
        )


def handle_sales_return_cancel(doc, method=None):
    """
    Called on Stock Entry cancellation (on_cancel hook).

    Reverses the PSV Transaction created during Stock Entry submit,
    restoring Inventory Visibility Layer to pre-return state.
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    try:
        tx_name = frappe.db.get_value(
            "SMRITI PSV Transaction",
            {
                "reference_doctype": doc.doctype,
                "reference_name": doc.name,
                "docstatus": 1
            },
            "name"
        )
        if tx_name:
            frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()
    except Exception:
        frappe.log_error(
            title=f"PSV SE Cancel Error: {doc.name}",
            message=frappe.get_traceback()
        )


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _create_dn_exception_record(doc, psa, exception_type, description):
    """Creates a SMRITI PSV Exception Record for operational health monitoring."""
    try:
        from frappe.utils import now_datetime
        frappe.get_doc({
            "doctype": "SMRITI PSV Exception Record",
            "party_stock_account": psa,
            "alert_type": exception_type,
            "timestamp": now_datetime(),
            "last_seen": now_datetime(),
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "reconciliation_notes": description,
            "status": "Pending Reconciliation"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        # Exception record creation must never raise — just log
        frappe.log_error(
            title="PSV Exception Record Creation Failed",
            message=frappe.get_traceback()
        )
