# -*- coding: utf-8 -*-
"""
smriti_retail_os/search_studio/api/smriti_search_api.py
SMRITI Global Search API — searches across all SMRITI entities.
All reads are via frappe.db (ERPNext as read-only backend).
Author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
"""
import frappe
from smriti_retail_os import smriti


@frappe.whitelist()
def global_search(query, limit=12):
    """
    Search across Items, Customers, Suppliers, POs, Invoices, GRNs.
    Returns categorised results for the SMRITI command palette.
    """
    if not query or len(query.strip()) < 2:
        return {"items": [], "customers": [], "suppliers": [],
                "orders": [], "invoices": [], "pages": []}

    q = "%" + query.strip() + "%"
    limit = int(limit)

    results = {}

    # ── Items ──────────────────────────────────────────────────────────────
    try:
        results["items"] = smriti.db.sql("""
            SELECT item_code, item_name, item_group,
                   standard_rate, stock_uom
            FROM `tabItem`
            WHERE disabled = 0
              AND (item_code LIKE %(q)s OR item_name LIKE %(q)s
                   OR barcode IN (
                       SELECT barcode FROM `tabItem Barcode`
                       WHERE barcode LIKE %(q)s AND parent = item_code
                   ))
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
    except Exception:
        results["items"] = []

    # ── Customers ─────────────────────────────────────────────────────────
    try:
        results["customers"] = smriti.db.sql("""
            SELECT name, customer_name, customer_group,
                   mobile_no, email_id
            FROM `tabCustomer`
            WHERE disabled = 0
              AND (customer_name LIKE %(q)s OR name LIKE %(q)s
                   OR mobile_no LIKE %(q)s OR email_id LIKE %(q)s)
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
    except Exception:
        results["customers"] = []

    # ── Suppliers ─────────────────────────────────────────────────────────
    try:
        results["suppliers"] = smriti.db.sql("""
            SELECT name, supplier_name, supplier_group,
                   mobile_no, email_id
            FROM `tabSupplier`
            WHERE disabled = 0
              AND (supplier_name LIKE %(q)s OR name LIKE %(q)s
                   OR mobile_no LIKE %(q)s)
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
    except Exception:
        results["suppliers"] = []

    # ── Purchase Orders ───────────────────────────────────────────────────
    try:
        results["orders"] = smriti.db.sql("""
            SELECT name, supplier, supplier_name,
                   transaction_date, grand_total, status
            FROM `tabPurchase Order`
            WHERE docstatus < 2
              AND (name LIKE %(q)s OR supplier_name LIKE %(q)s)
            ORDER BY transaction_date DESC
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
        for r in results["orders"]:
            r["_type"] = "purchase_order"
    except Exception:
        results["orders"] = []

    # ── Sales Invoices ────────────────────────────────────────────────────
    try:
        results["invoices"] = smriti.db.sql("""
            SELECT name, customer, customer_name,
                   posting_date, grand_total, status
            FROM `tabSales Invoice`
            WHERE docstatus < 2
              AND (name LIKE %(q)s OR customer_name LIKE %(q)s)
            ORDER BY posting_date DESC
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
        for r in results["invoices"]:
            r["_type"] = "sales_invoice"
    except Exception:
        results["invoices"] = []

    # ── Purchase Receipts (GRN) ───────────────────────────────────────────
    try:
        results["grns"] = smriti.db.sql("""
            SELECT name, supplier, supplier_name,
                   posting_date, total, status
            FROM `tabPurchase Receipt`
            WHERE docstatus < 2
              AND (name LIKE %(q)s OR supplier_name LIKE %(q)s)
            ORDER BY posting_date DESC
            LIMIT %(limit)s
        """, {"q": q, "limit": limit}, as_dict=True)
        for r in results["grns"]:
            r["_type"] = "grn"
    except Exception:
        results["grns"] = []

    # ── SMRITI Pages (static, filtered by query match) ────────────────────
    all_pages = [
        {"label": "Purchase Studio",       "route": "/smriti-purchase",         "icon": "🏭"},
        {"label": "New Purchase Order",    "route": "/smriti-purchase-order",   "icon": "📋"},
        {"label": "New GRN",               "route": "/smriti-grn",              "icon": "📦"},
        {"label": "POS Billing",           "route": "/billing",                 "icon": "🧾"},
        {"label": "Inventory",             "route": "/inventory",               "icon": "📁"},
        {"label": "Products",              "route": "/products",                "icon": "🏷️"},
        {"label": "Item Master",           "route": "/item-master",             "icon": "📦"},
        {"label": "Customers",             "route": "/customers",               "icon": "👥"},
        {"label": "Suppliers",             "route": "/suppliers",               "icon": "🏭"},
        {"label": "Sales Invoices",        "route": "/sales-invoices",          "icon": "💰"},
        {"label": "Reports",               "route": "/reports",                 "icon": "📊"},
        {"label": "Notifications",         "route": "/smriti-notifications",    "icon": "🔔"},
        {"label": "My Profile",            "route": "/smriti-profile",          "icon": "👤"},
        {"label": "Barcode Studio",        "route": "/barcode",                 "icon": "📎"},
        {"label": "PSV Dashboard",         "route": "/psv-dashboard",           "icon": "📡"},
        {"label": "Analytics Dashboard",   "route": "/analytics",               "icon": "📈"},
    ]
    ql = query.strip().lower()
    results["pages"] = [p for p in all_pages if ql in p["label"].lower()][:6]

    return results


@frappe.whitelist()
def get_recent_docs():
    """Returns recently visited documents for the search palette recent section."""
    user = frappe.session.user
    try:
        recent = smriti.db.sql("""
            SELECT reference_doctype as doctype, reference_name as name,
                   creation
            FROM `tabActivity Log`
            WHERE user = %(user)s
              AND reference_doctype IS NOT NULL
              AND reference_doctype IN (
                  'Sales Invoice','Purchase Order','Purchase Receipt',
                  'Customer','Supplier','Item'
              )
            ORDER BY creation DESC
            LIMIT 8
        """, {"user": user}, as_dict=True)
        return recent
    except Exception:
        return []
