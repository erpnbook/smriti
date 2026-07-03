# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/adapter/erp_adapter.py
# @desc:    ALL ERPNext DocType interactions for Purchase Studio.
#           No other file in purchase_studio may call frappe DocType APIs directly.
#           If ERPNext upgrades a field or function, only this file changes.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 1 (ERPNext Adapter)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, nowdate, now_datetime


# ─────────────────────────────────────────────────────────────────────────────
# WAREHOUSE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def get_default_warehouse(company):
    """
    Resolves the best available warehouse for a given company.
    Priority: 'Stores' warehouse → any non-group warehouse → any warehouse.
    Returns None if no warehouse found.
    """
    if not company:
        return None
    wh = frappe.db.get_value(
        "Warehouse",
        {"company": company, "is_group": 0, "warehouse_name": "Stores"},
        "name"
    )
    if not wh:
        wh = frappe.db.get_value(
            "Warehouse",
            {"company": company, "is_group": 0},
            "name",
            order_by="creation asc"
        )
    if not wh:
        wh = frappe.db.get_value("Warehouse", {"company": company}, "name")
    if wh and frappe.db.get_value("Warehouse", wh, "company") == company:
        return wh
    return None


def resolve_company(po_name=None, warehouse=None):
    """
    Returns the active company from: PO → user default → global default → first company.
    """
    company = None
    if po_name:
        company = frappe.db.get_value("Purchase Order", po_name, "company")
    if not company:
        company = frappe.defaults.get_user_default("company")
    if not company:
        company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        all_cos = frappe.get_all("Company", limit=1, fields=["name"])
        company = all_cos[0].name if all_cos else None
    return company


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE ORDER OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def list_purchase_orders(filters, fields, page=1, page_size=50):
    """
    Returns paginated list of Purchase Orders matching filters.
    """
    limit_start = (page - 1) * page_size
    total = frappe.db.count("Purchase Order", filters)
    items = frappe.get_all(
        "Purchase Order",
        filters=filters,
        fields=fields,
        order_by="transaction_date desc",
        limit_start=limit_start,
        limit_page_length=page_size
    )
    return {"total": total, "items": items}


def get_po(po_name):
    """
    Returns a fully loaded Purchase Order document.
    Raises 404 if not found.
    # ERPNext v14+: frappe.get_doc("Purchase Order", name)
    """
    if not frappe.db.exists("Purchase Order", po_name):
        frappe.throw(f"Purchase Order '{po_name}' not found.", frappe.DoesNotExistError)
    return frappe.get_doc("Purchase Order", po_name)


def insert_and_submit_po(po_doc):
    """
    Persists and submits a Purchase Order through the correct Frappe lifecycle.
    NEVER use docstatus=1 + save() — that bypasses before_submit/on_submit hooks
    which means stock reservation, GL entries, and status updates are skipped.

    Returns the submitted PO name.
    Rolls back and re-raises on any exception.
    """
    try:
        po_doc.insert(ignore_permissions=True)
        po_doc.submit()
        frappe.db.commit()
        return po_doc.name
    except Exception:
        frappe.db.rollback()
        raise


def get_item_flags(item_codes_list):
    """
    Batch-fetches item flags (has_batch_no, stock_uom) for a list of item codes.
    Eliminates N+1 queries in item loops.
    Returns dict: {item_code: row}
    """
    if not item_codes_list:
        return {}
    rows = frappe.db.get_all(
        "Item",
        filters={"name": ["in", item_codes_list]},
        fields=["name", "has_batch_no", "stock_uom"]
    )
    return {r.name: r for r in rows}


# ─────────────────────────────────────────────────────────────────────────────
# BATCH OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_batch(item_code, expiry_date=None):
    """
    Returns an existing batch or creates a new one.
    Optionally associates an expiry date.
    """
    if expiry_date:
        existing = frappe.db.get_value(
            "Batch",
            {"item": item_code, "expiry_date": expiry_date, "disabled": 0},
            "name"
        )
    else:
        existing = frappe.db.get_value(
            "Batch",
            {"item": item_code, "disabled": 0},
            "name",
            order_by="creation desc"
        )
    if existing:
        return existing

    batch = frappe.new_doc("Batch")
    batch.item = item_code
    if expiry_date:
        batch.expiry_date = expiry_date
    batch.insert(ignore_permissions=True)
    return batch.name


# ─────────────────────────────────────────────────────────────────────────────
# GRN / PURCHASE RECEIPT OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def list_grns(filters, fields, page=1, page_size=50):
    """Returns paginated list of Purchase Receipts."""
    limit_start = (page - 1) * page_size
    total = frappe.db.count("Purchase Receipt", filters)
    items = frappe.get_all(
        "Purchase Receipt",
        filters=filters,
        fields=fields,
        order_by="posting_date desc",
        limit_start=limit_start,
        limit_page_length=page_size
    )
    return {"total": total, "items": items}


def get_grn(grn_name):
    """
    Returns a fully loaded Purchase Receipt document.
    # ERPNext v14+: frappe.get_doc("Purchase Receipt", name)
    """
    if not frappe.db.exists("Purchase Receipt", grn_name):
        frappe.throw(f"Purchase Receipt '{grn_name}' not found.", frappe.DoesNotExistError)
    return frappe.get_doc("Purchase Receipt", grn_name)


def insert_and_submit_grn(pr_doc):
    """
    Persists and submits a Purchase Receipt.
    ERPNext on_submit creates Stock Ledger Entries — SMRITI never creates SLE directly.

    Returns the submitted GRN name.
    """
    try:
        pr_doc.insert(ignore_permissions=True)
        pr_doc.submit()
        frappe.db.commit()
        return pr_doc.name
    except Exception:
        frappe.db.rollback()
        raise


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE INVOICE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def list_purchase_invoices(filters, fields, page=1, page_size=50):
    """Returns paginated list of Purchase Invoices."""
    limit_start = (page - 1) * page_size
    total = frappe.db.count("Purchase Invoice", filters)
    items = frappe.get_all(
        "Purchase Invoice",
        filters=filters,
        fields=fields,
        order_by="posting_date desc",
        limit_start=limit_start,
        limit_page_length=page_size
    )
    return {"total": total, "items": items}


def get_pi(pi_name):
    """
    Returns a fully loaded Purchase Invoice document.
    # ERPNext v14+: frappe.get_doc("Purchase Invoice", name)
    """
    if not frappe.db.exists("Purchase Invoice", pi_name):
        frappe.throw(f"Purchase Invoice '{pi_name}' not found.", frappe.DoesNotExistError)
    return frappe.get_doc("Purchase Invoice", pi_name)


def insert_and_submit_pi(pi_doc):
    """
    Persists and submits a Purchase Invoice.
    ERPNext on_submit creates GL Entries — SMRITI never creates GL directly.

    Returns the submitted PI name.
    """
    try:
        pi_doc.insert(ignore_permissions=True)
        pi_doc.submit()
        frappe.db.commit()
        return pi_doc.name
    except Exception:
        frappe.db.rollback()
        raise


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE RETURN OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def make_purchase_return(grn_name):
    """
    Builds a Purchase Return document from an existing submitted GRN.
    # ERPNext v14+: erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return
    # Verify function signature on ERPNext major version upgrade.
    Returns the return document (not yet inserted).
    """
    from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_return
    return make_purchase_return(grn_name)


def insert_and_submit_return(ret_doc):
    """
    Persists and submits a Purchase Return (negative Purchase Receipt).
    ERPNext on_submit creates reversing Stock Ledger Entries.

    Returns the submitted return name.
    """
    try:
        ret_doc.insert(ignore_permissions=True)
        ret_doc.submit()
        # Note: commit is deferred to the caller (purchase_service) which
        # wraps return + debit note in a single transaction.
        return ret_doc.name
    except Exception:
        frappe.db.rollback()
        raise


def make_purchase_return_pi(pi_name):
    """
    Builds a Debit Note (Purchase Invoice return) from an existing submitted PI.
    # ERPNext v14+: erpnext.accounts.doctype.purchase_invoice.purchase_invoice.make_return_doc
    # Verify function signature on ERPNext major version upgrade.
    Returns the debit note document (not yet inserted).
    """
    from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import make_return_doc
    return make_return_doc("Purchase Invoice", pi_name)


def insert_and_submit_debit_note(dn_doc):
    """
    Persists and submits a Debit Note (Purchase Invoice return).
    ERPNext on_submit creates reversing GL Entries.

    Returns the submitted debit note name.
    """
    try:
        dn_doc.insert(ignore_permissions=True)
        dn_doc.submit()
        # commit is deferred to purchase_service (single transaction with return)
        return dn_doc.name
    except Exception:
        frappe.db.rollback()
        raise


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER LEDGER (READ-ONLY — GL is ERPNext property)
# ─────────────────────────────────────────────────────────────────────────────

def get_supplier_gl_entries(supplier, from_date, to_date, company):
    """
    Reads GL Entries for a supplier from ERPNext.
    SMRITI reads GL — never writes. GL is ERPNext's domain.

    Returns list of dicts: posting_date, voucher_type, voucher_no,
                           debit, credit, remarks
    """
    rows = frappe.db.sql("""
        SELECT
            posting_date,
            voucher_type,
            voucher_no,
            debit,
            credit,
            remarks
        FROM `tabGL Entry`
        WHERE
            party_type = 'Supplier'
            AND party = %(supplier)s
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND company = %(company)s
            AND is_cancelled = 0
        ORDER BY posting_date ASC, creation ASC
    """, {
        "supplier": supplier,
        "from_date": from_date,
        "to_date": to_date,
        "company": company
    }, as_dict=True)
    return rows


def get_supplier_outstanding(supplier, company):
    """
    Returns total outstanding payable for a supplier from ERPNext GL.
    """
    result = frappe.db.sql("""
        SELECT
            SUM(debit - credit) AS outstanding
        FROM `tabGL Entry`
        WHERE
            party_type = 'Supplier'
            AND party = %(supplier)s
            AND company = %(company)s
            AND is_cancelled = 0
    """, {"supplier": supplier, "company": company}, as_dict=True)
    return flt(result[0].outstanding) if result else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD READ OPERATIONS (Batch 1 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def count_open_purchase_orders(company):
    """
    Returns the number of submitted, uncompleted/unclosed POs for a company.
    """
    return frappe.db.count(
        "Purchase Order",
        {"docstatus": 1, "status": ["not in", ["Closed", "Completed", "Cancelled"]], "company": company}
    )


def count_pending_grns(company):
    """
    Returns the count of submitted GRNs with per_billed < 100%.
    """
    return frappe.db.count(
        "Purchase Receipt",
        {"docstatus": 1, "per_billed": ["<", 100], "is_return": 0, "company": company}
    )


def get_outstanding_payables_total(company):
    """
    Returns the total outstanding amount for all submitted Purchase Invoices.
    """
    result = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as total
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND outstanding_amount > 0 AND company=%s
    """, company, as_dict=True)
    return flt(result[0].total) if result else 0.0


def get_monthly_spend_total(company, start_date):
    """
    Returns the total grand_total sum of submitted PIs posted since start_date.
    """
    result = frappe.db.sql("""
        SELECT SUM(grand_total) as total
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND posting_date >= %s AND company=%s
    """, (start_date, company), as_dict=True)
    return flt(result[0].total) if result else 0.0


def get_recent_activities(company, limit=4):
    """
    Fetches recent submitted records for PO, GRN, and PI.
    Returns a unified sorted list of activity dicts.
    """
    recent = []
    for doctype, label in [("Purchase Order", "PO"), ("Purchase Receipt", "GRN"), ("Purchase Invoice", "PI")]:
        date_field = "transaction_date" if doctype == "Purchase Order" else "posting_date"
        rows = frappe.get_all(
            doctype,
            filters={"docstatus": 1, "company": company},
            fields=["name", "supplier", "supplier_name", date_field, "grand_total", "status"],
            order_by=f"{date_field} desc",
            limit_page_length=limit
        )
        for r in rows:
            recent.append({
                "doctype": label,
                "name": r.name,
                "supplier": r.supplier_name or r.supplier,
                "date": str(r.get(date_field, "")),
                "amount": flt(r.grand_total),
                "status": r.status or ""
            })
    return recent


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER & MASTER DATA READ OPERATIONS (Batch 2 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def supplier_exists(supplier):
    """
    Returns True if the supplier exists in the database.
    """
    return bool(frappe.db.exists("Supplier", supplier))


def get_supplier_doc(supplier):
    """
    Returns the cached Supplier document.
    Raises DoesNotExistError if supplier doesn't exist.
    """
    return frappe.get_cached_doc("Supplier", supplier)


def get_supplier_name(supplier):
    """
    Returns the supplier_name field for a supplier.
    """
    return frappe.db.get_value("Supplier", supplier, "supplier_name")


def get_supplier_overdue_payable(supplier, company):
    """
    Returns the sum of outstanding overdue payable amounts for a supplier.
    """
    overdue = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as overdue
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND supplier=%s AND company=%s
              AND outstanding_amount > 0 AND due_date < CURDATE()
    """, (supplier, company), as_dict=True)
    return flt(overdue[0].overdue) if overdue else 0.0


def get_suppliers_list(search_term=None, limit=50):
    """
    Queries the list of suppliers filtered by search_term.
    """
    filters = []
    if search_term:
        filters.append(["supplier_name", "like", f"%{search_term}%"])
    rows = frappe.get_all(
        "Supplier",
        filters=filters if filters else {},
        fields=["name", "supplier_name", "supplier_group", "country"],
        order_by="supplier_name asc",
        limit_page_length=limit
    )
    return rows


def search_suppliers(query, limit=20):
    """
    Returns list of suppliers matching query for search utility.
    """
    return frappe.get_all(
        "Supplier",
        filters=[["supplier_name", "like", f"%{query}%"]],
        fields=["name", "supplier_name", "supplier_group"],
        limit_page_length=limit
    )


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE ORDER OPERATIONS (Batch 3 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def create_purchase_order_document():
    """
    Instantiates an unsaved Purchase Order document.
    """
    return frappe.new_doc("Purchase Order")


def lock_and_get_po_status(po_name):
    """
    Locks the Purchase Order row and returns its smriti_approval_status.
    """
    result = frappe.db.sql(
        "SELECT smriti_approval_status FROM `tabPurchase Order` WHERE name=%s FOR UPDATE",
        po_name, as_dict=True
    )
    return result[0].smriti_approval_status if result else None


def set_po_approval_status(po_name, status, reason=None):
    """
    Updates the smriti_approval_status and rejection reason for a PO.
    """
    values = {"smriti_approval_status": status}
    if reason is not None:
        values["smriti_rejection_reason"] = reason
    frappe.db.set_value("Purchase Order", po_name, values)


def purchase_order_exists(po_name):
    """
    Returns True if the Purchase Order exists in the database.
    """
    return bool(frappe.db.exists("Purchase Order", po_name))


def get_po_supplier(po_name):
    """
    Returns the supplier field of a Purchase Order.
    """
    return frappe.db.get_value("Purchase Order", po_name, "supplier")


def lock_and_get_po_received_qty(po_name):
    """
    Locks the Purchase Order row and returns its per_received percentage.
    """
    result = frappe.db.sql(
        "SELECT per_received FROM `tabPurchase Order` WHERE name=%s FOR UPDATE",
        po_name, as_dict=True
    )
    return flt(result[0].per_received) if result else 0.0


def get_po_item_lines(po_name):
    """
    Returns item lines for a Purchase Order.
    """
    return frappe.get_all(
        "Purchase Order Item",
        filters={"parent": po_name},
        fields=["item_code", "qty", "received_qty", "name"]
    )



