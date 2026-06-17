# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/payment_api.py
# @description: Whitelisted SMRITI Payment API — all Payment Entry operations
#               must route through this service controller per SMRITI Rule 2.
#               UI must NEVER call frappe.client.get/insert directly.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, nowdate

# ─── Permission helpers ───────────────────────────────────────────────────────

def _check_access():
    """Requires SMRITI Store Manager or System Manager."""
    roles = frappe.get_roles(frappe.session.user)
    if not ({"SMRITI Store Manager", "System Manager", "Administrator"} & set(roles)):
        frappe.throw(_("Access Denied: You do not have permission to view Payments."), frappe.PermissionError)

def _check_write():
    """Requires SMRITI Store Manager or System Manager to create/edit."""
    roles = frappe.get_roles(frappe.session.user)
    if not ({"SMRITI Store Manager", "System Manager", "Administrator"} & set(roles)):
        frappe.throw(_("Access Denied: You do not have permission to create Payments."), frappe.PermissionError)

# ─── 1. List ──────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payments(payment_type="Receive", search=None, date_from=None, date_to=None, limit=200):
    """
    Returns Payment Entries filtered by type, date range, and search term.
    Replaces the direct frappe.client.get_list call in payments.html.
    """
    _check_access()

    filters = {"payment_type": payment_type}

    if date_from:
        filters["posting_date"] = [">=", date_from]
    if date_to:
        if "posting_date" in filters:
            filters["posting_date"] = ["between", [date_from, date_to]]
        else:
            filters["posting_date"] = ["<=", date_to]

    or_filters = None
    if search:
        or_filters = {
            "name":         ["like", f"%{search}%"],
            "party":        ["like", f"%{search}%"],
            "reference_no": ["like", f"%{search}%"],
            "party_name":   ["like", f"%{search}%"],
        }

    rows = frappe.db.get_all(
        "Payment Entry",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name", "posting_date", "payment_type", "party_type",
            "party", "party_name", "paid_amount", "received_amount",
            "mode_of_payment", "reference_no", "remarks",
            "docstatus", "company"
        ],
        order_by="posting_date desc, name desc",
        limit=int(limit)
    )
    return rows


# ─── 2. Detail ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payment_detail(name):
    """
    Returns full Payment Entry document with reference rows.
    Replaces frappe.client.get call in payments.html.
    """
    _check_access()

    if not name or not frappe.db.exists("Payment Entry", name):
        frappe.throw(_("Payment Entry '{0}' not found.").format(name))

    doc = frappe.get_doc("Payment Entry", name)

    refs = []
    for r in doc.references:
        refs.append({
            "reference_doctype": r.reference_doctype,
            "reference_name":    r.reference_name,
            "total_amount":      flt(r.total_amount),
            "outstanding_amount": flt(r.outstanding_amount),
            "allocated_amount":  flt(r.allocated_amount),
        })

    return {
        "name":             doc.name,
        "posting_date":     str(doc.posting_date),
        "payment_type":     doc.payment_type,
        "party_type":       doc.party_type,
        "party":            doc.party,
        "party_name":       doc.party_name or doc.party,
        "mode_of_payment":  doc.mode_of_payment,
        "paid_amount":      flt(doc.paid_amount),
        "received_amount":  flt(doc.received_amount),
        "reference_no":     doc.reference_no or "",
        "reference_date":   str(doc.reference_date) if doc.reference_date else "",
        "remarks":          doc.remarks or "",
        "docstatus":        doc.docstatus,
        "company":          doc.company,
        "references":       refs,
    }


# ─── 3. Create ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_payment(
    payment_type,       # Receive | Pay | Internal Transfer
    party_type,         # Customer | Supplier
    party,
    amount,
    mode_of_payment,
    posting_date=None,
    reference_no=None,
    reference_date=None,
    remarks=None,
    allocate_to=None    # JSON list of {doctype, docname, amount}
):
    """
    Creates and submits a Payment Entry via SMRITI service controller.
    SMRITI UI must call this instead of frappe.new_doc("Payment Entry").
    """
    _check_write()

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Payment amount must be greater than zero."))

    if not party or not frappe.db.exists(party_type, party):
        frappe.throw(_("{0} '{1}' not found.").format(party_type, party))

    company = frappe.defaults.get_user_default("company") or \
              frappe.get_all("Company", limit=1, pluck="name")[0]

    # Resolve accounts
    paid_from, paid_to = _resolve_accounts(payment_type, party_type, party, mode_of_payment, company)

    doc = frappe.get_doc({
        "doctype":          "Payment Entry",
        "payment_type":     payment_type,
        "posting_date":     posting_date or nowdate(),
        "company":          company,
        "party_type":       party_type,
        "party":            party,
        "mode_of_payment":  mode_of_payment,
        "paid_from":        paid_from,
        "paid_to":          paid_to,
        "paid_amount":      amount,
        "received_amount":  amount,
        "reference_no":     reference_no or "",
        "reference_date":   reference_date or (posting_date or nowdate()),
        "remarks":          remarks or "",
    })

    # Optional invoice allocation
    if allocate_to:
        allocs = frappe.parse_json(allocate_to)
        for a in allocs:
            if flt(a.get("amount")) > 0:
                doc.append("references", {
                    "reference_doctype":  a.get("doctype"),
                    "reference_name":     a.get("docname"),
                    "allocated_amount":   flt(a.get("amount")),
                    "total_amount":       flt(a.get("total_amount", a.get("amount"))),
                    "outstanding_amount": flt(a.get("outstanding_amount", a.get("amount"))),
                })

    try:
        doc.insert(ignore_permissions=True)
        doc.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name":      doc.name,
        "message":   _("Payment Entry {0} created and submitted.").format(doc.name),
        "docstatus": doc.docstatus,
    }


def _resolve_accounts(payment_type, party_type, party, mode_of_payment, company):
    """
    Resolves paid_from and paid_to accounts for a Payment Entry.
    """
    mop_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment, "company": company},
        "default_account"
    )
    if not mop_account:
        # Fallback: find any bank/cash account for this company
        mop_account = frappe.db.get_value(
            "Account",
            {"company": company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0},
            "name"
        )

    if party_type == "Customer":
        party_account = frappe.db.get_value(
            "Party Account",
            {"parent": party, "parenttype": "Customer", "company": company},
            "account"
        ) or frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Receivable", "is_group": 0},
            "name"
        )
    else:
        party_account = frappe.db.get_value(
            "Party Account",
            {"parent": party, "parenttype": "Supplier", "company": company},
            "account"
        ) or frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Payable", "is_group": 0},
            "name"
        )

    if payment_type == "Receive":
        return party_account, mop_account
    elif payment_type == "Pay":
        return mop_account, party_account
    else:  # Internal Transfer
        return mop_account, mop_account


# ─── 4. Outstanding Invoices ──────────────────────────────────────────────────

@frappe.whitelist()
def get_outstanding_invoices(party_type, party):
    """
    Returns unpaid/outstanding invoices for a party (for advance/payment allocation).
    """
    _check_access()

    if not party or not frappe.db.exists(party_type, party):
        return []

    doctype = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
    party_field = "customer" if party_type == "Customer" else "supplier"

    invoices = frappe.db.get_all(
        doctype,
        filters={party_field: party, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "posting_date", "grand_total", "outstanding_amount", "currency"],
        order_by="posting_date asc",
        limit=50
    )
    for inv in invoices:
        inv["doctype"] = doctype

    return invoices


# ─── 5. Party Search ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_parties(party_type, search=None):
    """
    Searches Customers or Suppliers for the payment creation form.
    """
    _check_access()

    if party_type not in ("Customer", "Supplier"):
        frappe.throw(_("Invalid party type."))

    filters = {"disabled": 0}
    name_field = "customer_name" if party_type == "Customer" else "supplier_name"
    or_filters = None

    if search:
        or_filters = {
            "name":      ["like", f"%{search}%"],
            name_field:  ["like", f"%{search}%"],
        }

    return frappe.db.get_all(
        party_type,
        filters=filters,
        or_filters=or_filters,
        fields=["name", name_field],
        limit=25
    )


# ─── 6. Modes of Payment ──────────────────────────────────────────────────────

@frappe.whitelist()
def get_modes_of_payment():
    """
    Returns all active modes of payment for the payment creation dropdown.
    """
    _check_access()
    return frappe.db.get_all(
        "Mode of Payment",
        filters={"enabled": 1},
        fields=["name", "type"],
        order_by="name asc"
    )
