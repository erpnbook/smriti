# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/event_hooks.py
# @desc:    SMRITI Connect Platform Engine event captures (DocType hooks).
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os.integration.core.dispatcher import dispatch_event

def handle_sales_invoice_submit(doc, method=None):
    """Intercepts Sales Invoice submission and publishes SALE_CREATED event."""
    payload = _build_sales_payload(doc)
    dispatch_event(
        event_type="SALE_CREATED",
        doc_type="Sales Invoice",
        doc_name=doc.name,
        payload=payload,
        priority="Normal"
    )

def handle_sales_invoice_cancel(doc, method=None):
    """Intercepts Sales Invoice cancellation and publishes SALE_CANCELLED event."""
    payload = _build_sales_payload(doc)
    dispatch_event(
        event_type="SALE_CANCELLED",
        doc_type="Sales Invoice",
        doc_name=doc.name,
        payload=payload,
        priority="Normal"
    )

def handle_purchase_invoice_submit(doc, method=None):
    """Intercepts Purchase Invoice submission and publishes PURCHASE_CREATED event."""
    payload = _build_purchase_payload(doc)
    dispatch_event(
        event_type="PURCHASE_CREATED",
        doc_type="Purchase Invoice",
        doc_name=doc.name,
        payload=payload,
        priority="Normal"
    )

def handle_purchase_invoice_cancel(doc, method=None):
    """Intercepts Purchase Invoice cancellation and publishes PURCHASE_CANCELLED event."""
    payload = _build_purchase_payload(doc)
    dispatch_event(
        event_type="PURCHASE_CANCELLED",
        doc_type="Purchase Invoice",
        doc_name=doc.name,
        payload=payload,
        priority="Normal"
    )


# ── Payload Builders ────────────────────────────────────────────────────────

def _build_sales_payload(doc) -> dict:
    """Builds standard, decoupled JSON payload representation for Sales Invoice."""
    items = []
    for item in doc.get("items") or []:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": float(item.qty),
            "rate": float(item.rate),
            "amount": float(item.amount)
        })
        
    return {
        "name": doc.name,
        "posting_date": str(doc.posting_date),
        "company": doc.company,
        "customer": doc.customer,
        "grand_total": float(doc.grand_total),
        "cash_ledger": doc.get("cash_ledger") or "Cash",
        "bank_ledger": doc.get("bank_ledger") or "Bank",
        "items": items
    }

def _build_purchase_payload(doc) -> dict:
    """Builds standard, decoupled JSON payload representation for Purchase Invoice."""
    items = []
    for item in doc.get("items") or []:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": float(item.qty),
            "rate": float(item.rate),
            "amount": float(item.amount)
        })

    return {
        "name": doc.name,
        "posting_date": str(doc.posting_date),
        "company": doc.company,
        "supplier": doc.supplier,
        "grand_total": float(doc.grand_total),
        "purchase_ledger": doc.get("purchase_ledger") or "Purchase Account",
        "items": items
    }
