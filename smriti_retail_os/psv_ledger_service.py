# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_ledger_service.py
# @description: SMRITI Psv Ledger Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/smriti_retail_os/psv_ledger_service.py
# @description: Channel Stock ledger service — routes all writes through the
#               canonical PSV Transaction document (create_psv_transaction) to
#               ensure uniform fingerprint deduplication, exception handling,
#               and activity logging. Direct ledger writes are NOT permitted here.
# @version: 2.0.0
#

import frappe
from smriti_retail_os.psv_service import create_psv_transaction


# Map Sell-Through upload transaction type labels to PSV Transaction types
_TRANS_TYPE_MAP = {
    "Sell-Through":  "SALES_UPLOAD",
    "Return":        "RETURN",
    "Opening":       "OPENING",
    "Dispatch":      "TRANSFER_OUT",
    "Transfer-In":   "TRANSFER_IN",
    "Adjustment":    "MANUAL_ADJUSTMENT",
}


def create_transaction(customer: str, item_code: str, qty: float,
                       trans_type: str, ref_doctype: str, ref_name: str):
    """
    Creates a PSV ledger entry for a given customer's channel stock account.

    Routes through create_psv_transaction() (canonical path) rather than
    calling make_ledger_entry() directly, so that:
      - Fingerprint deduplication is applied
      - SMRITI PSV Transaction document is created (audit trail)
      - Exception records are auto-generated on failure

    Args:
        customer:    ERPNext Customer name
        item_code:   SKU / Item Code
        qty:         Quantity (positive = stock in, negative = stock out)
        trans_type:  Human-readable type label (e.g. "Sell-Through", "Return")
        ref_doctype: Source document type (e.g. "PSV Sell-Through Upload")
        ref_name:    Source document name
    """
    psa_name = frappe.db.get_value(
        "SMRITI Party Stock Account",
        {"customer": customer, "active": 1},
        "name"
    )
    if not psa_name:
        frappe.throw(
            frappe._("No active SMRITI Party Stock Account found for customer {0}").format(customer)
        )

    company = frappe.db.get_value("SMRITI Party Stock Account", psa_name, "company")

    # Map to canonical PSV transaction type; default to MANUAL_ADJUSTMENT
    psv_type = _TRANS_TYPE_MAP.get(trans_type, "MANUAL_ADJUSTMENT")

    return create_psv_transaction(
        psa=psa_name,
        transaction_type=psv_type,
        items=[{"item_code": item_code, "qty": qty}],
        company=company,
        reference_doctype=ref_doctype,
        reference_name=ref_name,
        remarks=f"Auto-created from {ref_doctype}: {ref_name}"
    )


def reverse_transaction(ref_doctype: str, ref_name: str):
    """
    Cancels the PSV Transaction linked to the given source document.

    Prefers cancelling the PSV Transaction (which fires on_cancel → VOID ledger
    entries) rather than writing raw reversal ledger entries directly. Falls back
    to direct reversal only if no PSV Transaction exists.
    """
    # Find the submitted PSV Transaction that references this document
    tx_name = frappe.db.get_value(
        "SMRITI PSV Transaction",
        {"reference_doctype": ref_doctype, "reference_name": ref_name, "docstatus": 1},
        "name"
    )

    if tx_name:
        # Preferred path: cancel PSV Transaction — on_cancel writes VOID ledger entries
        frappe.get_doc("SMRITI PSV Transaction", tx_name).cancel()
        return

    # Fallback: direct reversal if PSV Transaction was never created (legacy data)
    from smriti_retail_os.ledger_engine import make_ledger_entry

    entries = frappe.get_all(
        "SMRITI Party Stock Ledger Entry",
        filters={"voucher_no": ref_name},
        fields=["company", "party_stock_account", "item_code", "qty",
                "voucher_type", "voucher_no"]
    )
    for entry in entries:
        make_ledger_entry(
            company=entry.company,
            posting_datetime=frappe.utils.now_datetime(),
            party_stock_account=entry.party_stock_account,
            item_code=entry.item_code,
            qty=entry.qty * -1.0,
            voucher_type=entry.voucher_type,
            voucher_no=f"VOID-{entry.voucher_no}",
            reason="Reversal (fallback direct write)"
        )
