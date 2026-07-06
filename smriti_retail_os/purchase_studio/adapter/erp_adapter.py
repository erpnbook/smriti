# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/adapter/erp_adapter.py
# @desc:    ALL ERPNext DocType interactions for Purchase Studio.
#           No other file in purchase_studio may call frappe DocType APIs directly.
#           If ERPNext upgrades a field or function, only this file changes.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 1 (ERPNext Adapter)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
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


# ─────────────────────────────────────────────────────────────────────────────
# GRN / PURCHASE RECEIPT OPERATIONS (Batch 4 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def create_purchase_receipt_document():
    """
    Instantiates an unsaved Purchase Receipt document.
    """
    return frappe.new_doc("Purchase Receipt")


def lock_and_get_grn_status(grn_name):
    """
    Locks the Purchase Receipt row and returns status, per_billed, and supplier.
    """
    result = frappe.db.sql(
        "SELECT docstatus, per_billed, supplier FROM `tabPurchase Receipt` WHERE name=%s FOR UPDATE",
        grn_name, as_dict=True
    )
    return result[0] if result else None


def get_grn_item_qty(grn_name, item_code):
    """
    Returns originally received qty for a GRN item line.
    """
    return frappe.db.get_value(
        "Purchase Receipt Item",
        {"parent": grn_name, "item_code": item_code},
        "qty"
    ) or 0.0


def grn_exists(grn_name):
    """
    Returns True if the Purchase Receipt exists in the database.
    """
    return bool(frappe.db.exists("Purchase Receipt", grn_name))


def get_grn_docstatus(grn_name):
    """
    Returns the docstatus of a Purchase Receipt.
    """
    return frappe.db.get_value("Purchase Receipt", grn_name, "docstatus")


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE INVOICE OPERATIONS (Batch 5 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def create_purchase_invoice_document():
    """
    Instantiates an unsaved Purchase Invoice document.
    """
    return frappe.new_doc("Purchase Invoice")


def get_grn_linked_invoice(grn_name):
    """
    Returns the name of a submitted Purchase Invoice linked to the GRN.
    """
    return frappe.db.get_value(
        "Purchase Invoice Item",
        {"purchase_receipt": grn_name, "docstatus": 1},
        "parent"
    )


# ─────────────────────────────────────────────────────────────────────────────
# ITEM, ANALYTICS & LCV OPERATIONS (Batch 6 Persistence Migration)
# ─────────────────────────────────────────────────────────────────────────────

def search_items(query, limit=20):
    """
    Returns list of stock items matching query.
    """
    return frappe.get_all(
        "Item",
        filters=[
            ["is_stock_item", "=", 1],
            ["|", ["item_code", "like", f"%{query}%"],
                  ["item_name", "like", f"%{query}%"]]
        ],
        fields=["item_code", "item_name", "stock_uom", "has_batch_no", "standard_rate"],
        limit_page_length=limit
    )


def auto_create_item_if_missing(item_code, rate, file_url=None):
    """
    Auto-creates a footwear variant Item in ERPNext if it does not exist.
    """
    if frappe.db.exists("Item", item_code):
        return

    parts = item_code.split("-")
    style = parts[0] if len(parts) > 0 else "UNKNOWN"
    color = parts[1] if len(parts) > 1 else "UNKNOWN"
    size  = parts[2] if len(parts) > 2 else "UNKNOWN"

    item = frappe.new_doc("Item")
    item.item_code            = item_code
    item.item_name            = f"{style} {color} {size}"
    default_group = frappe.db.get_single_value("SMRITI Settings", "default_item_group") or "Products"
    item.item_group           = default_group if frappe.db.exists("Item Group", default_group) else "Products"
    item.stock_uom            = "Nos"
    item.is_stock_item        = 1
    item.standard_rate        = rate
    item.custom_is_retail_item = 1
    item.custom_mrp           = flt(rate * 1.5)

    if file_url:
        item.image = file_url
    else:
        existing_img = frappe.db.get_value(
            "Item",
            {"item_code": ["like", f"{style}-%"], "image": ["is", "set"]},
            "image"
        )
        if existing_img:
            item.image = existing_img

    # Retrieve default GST HSN code from SMRITI Settings
    default_hsn = frappe.db.get_single_value("SMRITI Settings", "default_hsn_code")
    if default_hsn and frappe.db.exists("GST HSN Code", default_hsn):
        item.gst_hsn_code = default_hsn
    else:
        hsn_code = frappe.db.get_value("GST HSN Code", {}, "name")
        if hsn_code:
            item.gst_hsn_code = hsn_code

    template_name = frappe.db.get_value("Item Tax Template", {"name": ["like", "%18%"]}, "name")
    if template_name:
        item.append("taxes", {"item_tax_template": template_name, "tax_category": ""})

    item.insert(ignore_permissions=True)

    for pl_name, pl_rate in [("Standard Selling", rate * 1.2), ("MRP", rate * 1.5)]:
        existing_ip = frappe.db.get_value(
            "Item Price", {"item_code": item_code, "price_list": pl_name}, "name"
        )
        if existing_ip:
            frappe.db.set_value("Item Price", existing_ip, "price_list_rate", flt(pl_rate))
        else:
            ip = frappe.new_doc("Item Price")
            ip.item_code        = item_code
            ip.price_list       = pl_name
            ip.price_list_rate  = flt(pl_rate)
            ip.currency         = "INR"
            ip.uom              = "Nos"
            ip.insert(ignore_permissions=True)


def get_purchase_spend_analytics(company, from_date=None, to_date=None):
    """
    Aggregates Spend by Supplier, Month, and Item Group from DB.
    """
    date_filter = ""
    params = {"company": company}
    if from_date:
        date_filter += " AND pi.posting_date >= %(from_date)s"
        params["from_date"] = from_date
    if to_date:
        date_filter += " AND pi.posting_date <= %(to_date)s"
        params["to_date"] = to_date

    # Spend by supplier
    by_supplier = frappe.db.sql(f"""
        SELECT
            pi.supplier,
            pi.supplier_name,
            SUM(pi.grand_total) AS total_spend,
            COUNT(pi.name)      AS invoice_count
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
          AND pi.company   = %(company)s
          AND pi.is_return  = 0
          {date_filter}
        GROUP BY pi.supplier, pi.supplier_name
        ORDER BY total_spend DESC
        LIMIT 10
    """, params, as_dict=True)

    # Spend by month (last 12 months)
    by_month = frappe.db.sql(f"""
        SELECT
            DATE_FORMAT(pi.posting_date, '%%Y-%%m') AS month,
            SUM(pi.grand_total) AS total_spend,
            COUNT(pi.name)      AS invoice_count
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
          AND pi.company   = %(company)s
          AND pi.is_return  = 0
          AND pi.posting_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
          {date_filter}
        GROUP BY month
        ORDER BY month ASC
    """, params, as_dict=True)

    # Spend by item group
    by_item_group = frappe.db.sql(f"""
        SELECT
            i.item_group,
            SUM(pii.amount) AS total_spend
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        JOIN `tabItem` i ON pii.item_code = i.name
        WHERE pi.docstatus = 1
          AND pi.company   = %(company)s
          AND pi.is_return  = 0
          {date_filter}
        GROUP BY i.item_group
        ORDER BY total_spend DESC
        LIMIT 8
    """, params, as_dict=True)

    # Monthly PO count
    po_trend = frappe.db.sql("""
        SELECT
            DATE_FORMAT(transaction_date, '%%Y-%%m') AS month,
            COUNT(name)      AS po_count,
            SUM(grand_total) AS po_value
        FROM `tabPurchase Order`
        WHERE docstatus = 1
          AND company    = %(company)s
          AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY month
        ORDER BY month ASC
    """, {"company": company}, as_dict=True)

    return {
        "by_supplier":   [dict(r) for r in by_supplier],
        "by_month":      [dict(r) for r in by_month],
        "by_item_group": [dict(r) for r in by_item_group],
        "po_trend":      [dict(r) for r in po_trend]
    }


def get_supplier_performance_data(company, from_date=None, to_date=None, top_n=10):
    """
    Aggregates supplier KPIs and appends outstanding overdue payable metrics from PI.
    """
    date_filter = ""
    params = {"company": company}
    if from_date:
        date_filter += " AND po.transaction_date >= %(from_date)s"
        params["from_date"] = from_date
    if to_date:
        date_filter += " AND po.transaction_date <= %(to_date)s"
        params["to_date"] = to_date
    params["top_n"] = cint(top_n)

    rows = frappe.db.sql(f"""
        SELECT
            po.supplier,
            po.supplier_name,
            COUNT(DISTINCT po.name)              AS po_count,
            SUM(po.grand_total)                  AS po_value,
            SUM(po.grand_total * po.per_received / 100) AS received_value,
            AVG(po.per_received)                 AS avg_fill_rate
        FROM `tabPurchase Order` po
        WHERE po.docstatus = 1
          AND po.company   = %(company)s
          {date_filter}
        GROUP BY po.supplier, po.supplier_name
        ORDER BY po_value DESC
        LIMIT %(top_n)s
    """, params, as_dict=True)

    # Attach overdue amounts from PI
    for row in rows:
        overdue = frappe.db.sql("""
            SELECT SUM(outstanding_amount) as amt
            FROM `tabPurchase Invoice`
            WHERE docstatus=1 AND supplier=%(supplier)s
              AND company=%(company)s
              AND outstanding_amount > 0
              AND due_date < CURDATE()
        """, {"supplier": row.supplier, "company": company}, as_dict=True)
        row["overdue_amount"] = flt(overdue[0].amt) if overdue else 0.0
        row["fill_rate"]      = round(flt(row.avg_fill_rate), 1)
        row["po_value"]       = flt(row.po_value)
        row["received_value"] = flt(row.received_value)

    return [dict(r) for r in rows]


def list_landed_cost_vouchers(company, from_date=None, to_date=None, limit_start=0, limit_page_length=50):
    """
    Queries the list of Landed Cost Vouchers and counts the total.
    """
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    total = frappe.db.count("Landed Cost Voucher", filters)
    items = frappe.get_all(
        "Landed Cost Voucher",
        filters=filters,
        fields=["name", "posting_date", "company", "total_taxes_and_charges", "status"],
        order_by="posting_date desc",
        limit_start=limit_start,
        limit_page_length=limit_page_length
    )
    return {"total": total, "items": items}


def create_landed_cost_voucher_document():
    """
    Instantiates an unsaved Landed Cost Voucher document.
    """
    return frappe.new_doc("Landed Cost Voucher")


def insert_and_submit_lcv(lcv):
    """
    Inserts and submits a Landed Cost Voucher.
    """
    lcv.insert(ignore_permissions=True)
    lcv.submit()
    return lcv.name


def check_item_has_batch(item_code):
    """
    Returns True if the item has a batch number.
    """
    return bool(frappe.db.get_value("Item", item_code, "has_batch_no"))


# ─────────────────────────────────────────────────────────────────────────────
# SMRITI SUPPLIER ↔ ERPNEXT SUPPLIER BRIDGE
#
# SMRITI Purchase Order/Approval workflow lives on the native "SMRITI Supplier"
# and "SMRITI Purchase Order" DocTypes. GST-compliant execution documents
# (Purchase Receipt, Purchase Invoice, Purchase Return) are ERPNext-native and
# require a real ERPNext "Supplier" record. This bridge keeps SMRITI Supplier
# as the single source of truth for SMRITI-side data and provisions/updates a
# linked ERPNext Supplier only through documented Frappe APIs (insert/save) —
# no ERPNext source is copied or modified, only its public DocType API is used.
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_bridge_supplier(smriti_supplier_name):
    """
    Ensures a real ERPNext 'Supplier' exists for a given 'SMRITI Supplier'
    and returns its name. Idempotent — safe to call on every transaction.
    """
    smriti_supplier = frappe.get_doc("SMRITI Supplier", smriti_supplier_name)
    linked = smriti_supplier.get("erpnext_supplier")

    if linked and frappe.db.exists("Supplier", linked):
        # Keep core fields in sync (SMRITI Supplier remains source of truth)
        frappe.db.set_value("Supplier", linked, {
            "supplier_name": smriti_supplier.supplier_name,
            "tax_id": smriti_supplier.tax_id,
            "disabled": smriti_supplier.disabled,
        })
        return linked

    existing = frappe.db.get_value(
        "Supplier",
        {"supplier_name": smriti_supplier.supplier_name},
        "name"
    )
    if existing:
        smriti_supplier.db_set("erpnext_supplier", existing)
        return existing

    erp_supplier = frappe.new_doc("Supplier")
    erp_supplier.supplier_name = smriti_supplier.supplier_name
    erp_supplier.supplier_group = smriti_supplier.supplier_group or _get_default_supplier_group()
    erp_supplier.supplier_type = smriti_supplier.supplier_type or "Company"
    erp_supplier.tax_id = smriti_supplier.tax_id
    erp_supplier.mobile_no = smriti_supplier.mobile_no
    erp_supplier.email_id = smriti_supplier.email_id
    erp_supplier.disabled = smriti_supplier.disabled
    erp_supplier.insert(ignore_permissions=True)

    smriti_supplier.db_set("erpnext_supplier", erp_supplier.name)
    return erp_supplier.name


def _get_default_supplier_group():
    return frappe.db.get_value("Supplier Group", {"is_group": 0}, "name") \
        or frappe.db.get_value("Supplier Group", {}, "name")


# ─────────────────────────────────────────────────────────────────────────────
# REAL GRN / INVOICE / RETURN — built from a SMRITI Purchase Order
#
# SMRITI Purchase Order stays the record of intent + approval trail.
# These functions produce the actual ERPNext execution documents so that
# Stock Ledger, GL Entries, GST fields, e-invoice/e-way bill, and TDS are
# handled by ERPNext/india_compliance — never re-implemented natively.
# ─────────────────────────────────────────────────────────────────────────────

def build_and_submit_grn(smriti_po, received_items, warehouse=None):
    """
    Creates a standalone ERPNext Purchase Receipt (no ERPNext PO link needed)
    from a SMRITI Purchase Order's items.

    smriti_po: a loaded "SMRITI Purchase Order" document
    received_items: {item_code: qty_received}
    """
    supplier = get_or_create_bridge_supplier(smriti_po.supplier)

    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = supplier
    pr.company = smriti_po.company
    pr.posting_date = nowdate()

    for row in smriti_po.items:
        qty = flt(received_items.get(row.item_code))
        if qty <= 0:
            continue
        pr.append("items", {
            "item_code": row.item_code,
            "qty": qty,
            "rate": row.rate,
            "warehouse": warehouse or row.warehouse or get_default_warehouse(smriti_po.company),
            "uom": row.uom,
        })

    if not pr.items:
        frappe.throw(_("No receivable quantity provided for GRN."))

    pr.smriti_source_po = smriti_po.name  # requires custom field, see fixtures
    return insert_and_submit_grn(pr)


def build_and_submit_invoice(grn_name, posting_date=None):
    """
    Creates an ERPNext Purchase Invoice linked to a submitted Purchase Receipt,
    using ERPNext's own get_mapped_doc so tax templates, HSN, and
    india_compliance GST fields are inherited correctly.
    """
    # ERPNext v14+: erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice
    # Verify function signature on ERPNext major version upgrade (same caution as make_purchase_return above).
    from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

    pi = make_purchase_invoice(grn_name)
    if posting_date:
        pi.posting_date = posting_date
    pi.smriti_creation_mode = "grn_linked"  # requires custom field, see fixtures
    return insert_and_submit_pi(pi)


def build_and_submit_return(grn_name, return_items=None, reason=None):
    """
    Creates and submits an ERPNext Purchase Return against a submitted GRN
    using ERPNext's own make_purchase_return — never mutates PO/GRN status
    directly, so partial receipts remain intact.
    """
    return_doc = make_purchase_return(grn_name)

    if return_items:
        wanted = {i["item_code"]: flt(i["qty"]) for i in return_items}
        keep = []
        for row in return_doc.items:
            if row.item_code in wanted:
                row.qty = -abs(wanted[row.item_code])
                keep.append(row)
        return_doc.items = keep

    if reason:
        return_doc.smriti_return_reason = reason  # existing fixture field

    return_doc.insert(ignore_permissions=True)
    return_doc.submit()
    frappe.db.commit()
    return return_doc.name







