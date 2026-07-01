# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/purchase_service.py
# @desc:    All Purchase Studio business logic.
#           UI → purchase_api.py → THIS FILE → erp_adapter.py → ERPNext
#           No UI code, no frappe.whitelist, no direct ERPNext DocType calls.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 4 (Business Logic)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, cint, nowdate, now_datetime

from smriti_retail_os.purchase_studio.adapter import erp_adapter
from smriti_retail_os.purchase_studio.service import (
    audit_service,
    purchase_settings_service as settings_svc
)


# ─────────────────────────────────────────────────────────────────────────────
# ROLE GUARD
# ─────────────────────────────────────────────────────────────────────────────

def check_manager_role():
    """Enforces Store Manager or System Manager."""
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(
            _("Access Denied: Only Store Managers or System Managers can perform this action."),
            frappe.PermissionError
        )


def check_any_purchase_role():
    """Allows Cashier, Store Manager, or System Manager (view access)."""
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"SMRITI Cashier", "SMRITI Store Manager", "System Manager"}
    if not allowed.intersection(roles):
        frappe.throw(_("Access Denied: Purchase Studio requires a SMRITI role."), frappe.PermissionError)


def check_system_manager():
    """Enforces System Manager only (for Settings)."""
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Access Denied: Only System Managers can access Purchase Settings."), frappe.PermissionError)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def get_dashboard_data(company=None):
    """Returns KPI summary for Purchase Studio dashboard."""
    check_any_purchase_role()
    company = company or erp_adapter.resolve_company()

    open_pos = frappe.db.count(
        "Purchase Order",
        {"docstatus": 1, "status": ["not in", ["Closed", "Completed", "Cancelled"]], "company": company}
    )
    pending_grns = frappe.db.count(
        "Purchase Receipt",
        {"docstatus": 1, "per_billed": ["<", 100], "is_return": 0, "company": company}
    )

    unpaid_result = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as total
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND outstanding_amount > 0 AND company=%s
    """, company, as_dict=True)
    unpaid_amt = flt(unpaid_result[0].total) if unpaid_result else 0.0

    from datetime import date
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    month_spend_result = frappe.db.sql("""
        SELECT SUM(grand_total) as total
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND posting_date >= %s AND company=%s
    """, (month_start, company), as_dict=True)
    month_spend = flt(month_spend_result[0].total) if month_spend_result else 0.0

    # Recent activity — last 10 docs across PO, GRN, PI
    recent = []
    for doctype, label in [("Purchase Order", "PO"), ("Purchase Receipt", "GRN"), ("Purchase Invoice", "PI")]:
        date_field = "transaction_date" if doctype == "Purchase Order" else "posting_date"
        rows = frappe.get_all(
            doctype,
            filters={"docstatus": 1, "company": company},
            fields=["name", "supplier", "supplier_name", date_field, "grand_total", "status"],
            order_by=f"{date_field} desc",
            limit_page_length=4
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

    recent.sort(key=lambda x: x["date"], reverse=True)
    return {
        "open_pos":            open_pos,
        "pending_grns":        pending_grns,
        "unpaid_invoices_amt": unpaid_amt,
        "month_spend":         month_spend,
        "recent_activity":     recent[:10]
    }


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE ORDERS
# ─────────────────────────────────────────────────────────────────────────────

def list_purchase_orders(company=None, supplier=None, status=None,
                         from_date=None, to_date=None,
                         search_term=None, page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": ["!=", 2]}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if status:
        filters["status"] = status
    if from_date:
        filters["transaction_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("transaction_date", ["<=", to_date])

    fields = ["name", "supplier", "supplier_name", "transaction_date",
              "grand_total", "per_received", "status",
              "smriti_approval_status"]

    result = erp_adapter.list_purchase_orders(filters, fields, page, page_size)

    if search_term:
        q = search_term.lower()
        result["items"] = [
            i for i in result["items"]
            if q in (i.name or "").lower() or q in (i.supplier_name or "").lower()
        ]
        result["total"] = len(result["items"])

    return result


def get_purchase_order_detail(po_name):
    check_any_purchase_role()
    po = erp_adapter.get_po(po_name)
    items = []
    for item in po.items:
        pending = flt(item.qty) - flt(item.received_qty)
        has_batch = frappe.db.get_value("Item", item.item_code, "has_batch_no")
        items.append({
            "item_code":    item.item_code,
            "item_name":    item.item_name,
            "brand":        getattr(item, "brand", ""),
            "qty":          flt(item.qty),
            "received_qty": flt(item.received_qty),
            "pending_qty":  flt(pending),
            "rate":         flt(item.rate),
            "amount":       flt(item.amount),
            "warehouse":    item.warehouse,
            "uom":          item.uom,
            "has_batch_no": cint(has_batch),
            "po_item_name": item.name
        })
    return {
        "name":                   po.name,
        "supplier":               po.supplier,
        "supplier_name":          po.supplier_name,
        "company":                po.company,
        "transaction_date":       str(po.transaction_date or ""),
        "schedule_date":          str(po.schedule_date or ""),
        "terms":                  po.terms or "",
        "status":                 po.status,
        "grand_total":            flt(po.grand_total),
        "per_received":           flt(po.per_received),
        "smriti_approval_status": po.smriti_approval_status or "Draft",
        "smriti_approved_by":     po.smriti_approved_by or "",
        "smriti_approved_on":     str(po.smriti_approved_on or ""),
        "items":                  items
    }


def create_purchase_order(supplier, items_list, schedule_date=None,
                          remarks=None, image_base64=None,
                          image_filename=None, warehouse=None):
    check_manager_role()

    if not items_list:
        frappe.throw(_("Cannot create Purchase Order with an empty items list."))
    if not supplier or not frappe.db.exists("Supplier", supplier):
        frappe.throw(_("Supplier '{0}' not found.").format(supplier))

    company = erp_adapter.resolve_company()
    warehouse = warehouse or settings_svc.get_default_warehouse_setting() \
                or erp_adapter.get_default_warehouse(company)

    # Handle variant image upload
    file_url = _save_variant_image(image_base64, image_filename, items_list)

    # Auto-create missing items if setting allows
    if settings_svc.is_auto_create_items():
        for it in items_list:
            _auto_create_item_if_missing(
                it.get("item_code"), flt(it.get("rate")), file_url
            )

    # Build PO document
    po = frappe.new_doc("Purchase Order")
    po.supplier      = supplier
    po.transaction_date = nowdate()
    po.schedule_date = schedule_date or nowdate()
    po.company       = company
    if remarks:
        po.terms = remarks

    item_flags = erp_adapter.get_item_flags([it.get("item_code") for it in items_list])
    for it in items_list:
        item_code = it.get("item_code")
        qty       = flt(it.get("qty"))
        rate      = flt(it.get("rate"))
        wh        = it.get("warehouse") or warehouse

        if qty <= 0:
            frappe.throw(_("Item '{0}': qty must be greater than 0.").format(item_code))

        po.append("items", {
            "item_code":     item_code,
            "qty":           qty,
            "rate":          rate,
            "warehouse":     wh,
            "schedule_date": schedule_date or nowdate(),
            "uom":           it.get("stock_uom") or (item_flags.get(item_code) or {}).get("stock_uom") or "Nos"
        })

    grand_total = sum(flt(it.get("qty")) * flt(it.get("rate")) for it in items_list)

    # Check approval requirement
    approval_required = settings_svc.check_approval_required(grand_total)

    if approval_required:
        # Save as draft, mark pending approval — do NOT submit yet
        po.smriti_approval_status = "Pending"
        po.insert(ignore_permissions=True)
        frappe.db.commit()
        audit_service.log(
            event_type=audit_service.PO_PENDING_APPROVAL,
            payload={"doctype": "Purchase Order", "name": po.name,
                     "supplier": supplier, "grand_total": grand_total},
            after={"smriti_approval_status": "Pending"}
        )
        return {
            "status":            "pending_approval",
            "name":              po.name,
            "approval_required": True,
            "threshold":         frappe.get_single("SMRITI Purchase Settings").approval_threshold,
            "message":           _("Purchase Order pending approval.")
        }
    else:
        # Submit immediately
        po_name = erp_adapter.insert_and_submit_po(po)
        audit_service.log(
            event_type=audit_service.PO_SUBMITTED,
            payload={"doctype": "Purchase Order", "name": po_name,
                     "supplier": supplier, "grand_total": grand_total}
        )
        return {
            "status":  "submitted",
            "name":    po_name,
            "message": _("Purchase Order {0} submitted successfully.").format(po_name)
        }


def resolve_po_approval(po_name, action, reason=None):
    check_system_manager()

    if action not in ("approve", "reject"):
        frappe.throw(_("Invalid action '{0}'. Must be 'approve' or 'reject'.").format(action))
    if action == "reject" and not reason:
        frappe.throw(_("Rejection reason is mandatory."))

    # Row-level lock to prevent concurrent approval
    result = frappe.db.sql(
        "SELECT smriti_approval_status FROM `tabPurchase Order` WHERE name=%s FOR UPDATE",
        po_name, as_dict=True
    )
    if not result:
        frappe.throw(_("Purchase Order '{0}' not found.").format(po_name), frappe.DoesNotExistError)
    current_status = result[0].smriti_approval_status
    if current_status != "Pending":
        frappe.throw(
            _("Purchase Order '{0}' is not in Pending Approval state (current: {1}).").format(
                po_name, current_status
            )
        )

    po = erp_adapter.get_po(po_name)

    if action == "approve":
        po.smriti_approval_status = "Approved"
        po.smriti_approved_by     = frappe.session.user
        po.smriti_approved_on     = now_datetime()
        po.save(ignore_permissions=True)
        erp_adapter.insert_and_submit_po(po)  # actually submits now
        audit_service.log(
            event_type=audit_service.PO_APPROVED,
            payload={"doctype": "Purchase Order", "name": po_name,
                     "approved_by": frappe.session.user},
            before={"smriti_approval_status": "Pending"},
            after={"smriti_approval_status": "Approved"}
        )
        return {"status": "approved", "name": po_name,
                "message": _("Purchase Order {0} approved and submitted.").format(po_name)}
    else:
        frappe.db.set_value("Purchase Order", po_name, {
            "smriti_approval_status":  "Rejected",
            "smriti_rejection_reason": reason
        })
        frappe.db.commit()
        audit_service.log(
            event_type=audit_service.PO_REJECTED,
            payload={"doctype": "Purchase Order", "name": po_name},
            before={"smriti_approval_status": "Pending"},
            after={"smriti_approval_status": "Rejected"},
            reason=reason
        )
        return {"status": "rejected", "name": po_name,
                "message": _("Purchase Order {0} rejected.").format(po_name)}


# ─────────────────────────────────────────────────────────────────────────────
# GRN / PURCHASE RECEIPT
# ─────────────────────────────────────────────────────────────────────────────

def list_grns(company=None, supplier=None, po_name=None, status=None,
              from_date=None, to_date=None, mode=None, page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1, "is_return": 0}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    fields = ["name", "supplier", "supplier_name", "posting_date",
              "grand_total", "per_billed", "status"]
    return erp_adapter.list_grns(filters, fields, page, page_size)


def get_grn_detail(grn_name):
    check_any_purchase_role()
    pr = erp_adapter.get_grn(grn_name)
    items = []
    for item in pr.items:
        items.append({
            "item_code":          item.item_code,
            "item_name":          item.item_name,
            "qty":                flt(item.qty),
            "rate":               flt(item.rate),
            "amount":             flt(item.amount),
            "warehouse":          item.warehouse,
            "batch_no":           item.batch_no or "",
            "uom":                item.uom,
            "purchase_order":     item.purchase_order or "",
            "purchase_order_item": item.purchase_order_item or ""
        })
    return {
        "name":          pr.name,
        "supplier":      pr.supplier,
        "supplier_name": pr.supplier_name,
        "company":       pr.company,
        "posting_date":  str(pr.posting_date or ""),
        "grand_total":   flt(pr.grand_total),
        "per_billed":    flt(pr.per_billed),
        "status":        pr.status,
        "items":         items
    }


def create_grn(supplier, items_list, po_name=None, warehouse=None):
    check_manager_role()

    if not items_list:
        frappe.throw(_("Cannot create GRN with an empty items list."))
    if not supplier or not frappe.db.exists("Supplier", supplier):
        frappe.throw(_("Supplier '{0}' not found.").format(supplier))

    company = erp_adapter.resolve_company(po_name)
    warehouse = warehouse or settings_svc.get_default_warehouse_setting() \
                or erp_adapter.get_default_warehouse(company)

    # Validate against PO if provided
    if po_name:
        if not frappe.db.exists("Purchase Order", po_name):
            frappe.throw(_("Purchase Order '{0}' not found.").format(po_name))
        po_supplier = frappe.db.get_value("Purchase Order", po_name, "supplier")
        if po_supplier != supplier:
            frappe.throw(_(
                "Supplier mismatch: GRN supplier '{0}' does not match PO supplier '{1}'."
            ).format(supplier, po_supplier))

    # Validate quantities against PO (with row lock for concurrency)
    validate_grn_lines(items_list, po_name, settings_svc.is_over_receipt_allowed())

    # Build PR document
    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier     = supplier
    pr.posting_date = nowdate()
    pr.company      = company

    if po_name and frappe.db.exists("Purchase Order", po_name):
        po_doc = erp_adapter.get_po(po_name)
        pr.buying_price_list = po_doc.buying_price_list
        pr.currency          = po_doc.currency
        pr.conversion_rate   = po_doc.conversion_rate

    item_flags = erp_adapter.get_item_flags([it.get("item_code") for it in items_list])

    for it in items_list:
        item_code = it.get("item_code")
        qty       = flt(it.get("qty"))
        rate      = flt(it.get("rate"))
        wh        = it.get("warehouse") or warehouse

        if qty <= 0:
            frappe.throw(_("Item '{0}': received qty must be greater than 0.").format(item_code))

        flags = item_flags.get(item_code) or frappe._dict()

        # Batch handling
        batch_no = None
        if cint(flags.get("has_batch_no")):
            batch_no = it.get("batch_no")
            if not batch_no:
                expiry_date = it.get("expiry_date")
                batch_no = erp_adapter.get_or_create_batch(item_code, expiry_date)
                audit_service.log(
                    event_type=audit_service.BATCH_ASSIGNED,
                    payload={"doctype": "Batch", "name": batch_no,
                             "item_code": item_code, "expiry_date": expiry_date or ""}
                )

        row = {
            "item_code": item_code,
            "qty":       qty,
            "rate":      rate,
            "warehouse": wh,
            "batch_no":  batch_no,
            "uom":       it.get("stock_uom") or flags.get("stock_uom") or "Nos"
        }
        if po_name:
            row["purchase_order"]      = po_name
            row["purchase_order_item"] = it.get("po_item_name")

        pr.append("items", row)

    grn_name = erp_adapter.insert_and_submit_grn(pr)

    audit_service.log(
        event_type=audit_service.GRN_SUBMITTED,
        payload={
            "doctype":   "Purchase Receipt",
            "name":      grn_name,
            "supplier":  supplier,
            "po_name":   po_name or "",
            "items_count": len(items_list)
        }
    )
    return {
        "status":  "submitted",
        "name":    grn_name,
        "message": _("GRN {0} submitted. Stock updated.").format(grn_name)
    }


def validate_grn_lines(items_list, po_name, allow_over_receipt):
    """
    Validates received qty against PO pending qty.
    Uses FOR UPDATE lock to prevent race conditions.
    """
    if not po_name:
        return  # standalone GRN — no PO validation needed

    # Lock the PO row
    frappe.db.sql(
        "SELECT per_received FROM `tabPurchase Order` WHERE name=%s FOR UPDATE",
        po_name
    )

    # Build pending qty map from PO
    po_items = frappe.db.get_all(
        "Purchase Order Item",
        filters={"parent": po_name},
        fields=["item_code", "qty", "received_qty", "name"]
    )
    pending_map = {
        r.name: flt(r.qty) - flt(r.received_qty)
        for r in po_items
    }
    item_pending = {}
    for r in po_items:
        item_pending[r.item_code] = flt(r.qty) - flt(r.received_qty)

    if not allow_over_receipt:
        tol = flt(frappe.db.get_single_value("SMRITI Purchase Settings", "tolerance_percent") or 0)
        for it in items_list:
            item_code = it.get("item_code")
            recv_qty  = flt(it.get("qty"))
            pending   = item_pending.get(item_code, 0)
            max_allow = pending * (1 + tol / 100.0)
            if recv_qty > max_allow:
                frappe.throw(_(
                    "Item '{0}': received qty {1} exceeds pending PO qty {2} "
                    "(tolerance: {3}%). Enable 'Allow Over-Receipt' in Purchase Settings "
                    "to override."
                ).format(item_code, recv_qty, pending, tol))


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE INVOICE
# ─────────────────────────────────────────────────────────────────────────────

def list_invoices(company=None, supplier=None, status=None, from_date=None,
                  to_date=None, mode=None, page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if status:
        filters["status"] = status
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])
    if mode in ("grn_linked", "standalone"):
        filters["smriti_creation_mode"] = mode

    fields = ["name", "posting_date", "supplier", "supplier_name",
              "grand_total", "outstanding_amount", "status", "smriti_creation_mode"]
    return erp_adapter.list_purchase_invoices(filters, fields, page, page_size)


def get_invoice_detail(pi_name):
    check_any_purchase_role()
    pi = erp_adapter.get_pi(pi_name)
    items = [{"item_code": i.item_code, "item_name": i.item_name,
               "qty": flt(i.qty), "rate": flt(i.rate), "amount": flt(i.amount)}
             for i in pi.items]
    taxes = [{"description": t.description, "rate": flt(t.rate),
               "tax_amount": flt(t.tax_amount)} for t in pi.taxes]
    grn_ref = pi.items[0].purchase_receipt if pi.items and pi.items[0].purchase_receipt else None
    return {
        "name":                  pi.name,
        "supplier":              pi.supplier,
        "supplier_name":         pi.supplier_name,
        "posting_date":          str(pi.posting_date or ""),
        "grand_total":           flt(pi.grand_total),
        "outstanding_amount":    flt(pi.outstanding_amount),
        "status":                pi.status,
        "smriti_creation_mode":  pi.smriti_creation_mode or "",
        "grn_reference":         grn_ref,
        "items":                 items,
        "taxes":                 taxes
    }


def create_invoice(mode, supplier=None, grn_name=None, items_list=None, posting_date=None):
    check_manager_role()

    policy    = settings_svc.check_invoice_policy()
    grn_mand  = settings_svc.is_grn_mandatory()

    # ── Layer 1: Company-wide policy gate ────────────────────────────────────
    if grn_mand and mode == "standalone":
        frappe.throw(_(
            "Standalone Purchase Invoices are disabled. "
            "GRN Mandatory is enabled in Purchase Settings."
        ))
    if policy == "grn_only" and mode == "standalone":
        frappe.throw(_(
            "Standalone Purchase Invoices are disabled. "
            "Policy is set to 'GRN Only' in Purchase Settings."
        ))
    if policy == "standalone" and mode == "grn_linked":
        frappe.throw(_(
            "GRN-linked Purchase Invoices are disabled. "
            "Policy is set to 'Standalone Only' in Purchase Settings."
        ))

    # ── Layer 2: Per-supplier compliance flags ────────────────────────────────
    # These flags can only RESTRICT — they cannot widen beyond company-wide policy.
    # Use case: company policy = "both", but specific supplier requires GRN (e.g.
    # regulated categories, brand compliance, distributor audit requirements).
    if supplier and mode == "standalone":
        try:
            supplier_doc = frappe.get_cached_doc("Supplier", supplier)
        except frappe.DoesNotExistError:
            frappe.throw(_("Supplier '{0}' not found.").format(supplier))

        # Flag 1: Supplier requires a Purchase Order before any invoice
        allow_without_po = cint(
            getattr(supplier_doc, "allow_purchase_invoice_creation_without_purchase_order", 1)
        )
        if not allow_without_po:
            frappe.throw(_(
                "Supplier '{0}' requires a Purchase Order before invoicing. "
                "Please create a PO and GRN first, then use GRN-linked invoicing."
            ).format(supplier))

        # Flag 2: Supplier requires a GRN (Purchase Receipt) before standalone invoice
        allow_without_receipt = cint(
            getattr(supplier_doc, "allow_purchase_invoice_creation_without_purchase_receipt", 1)
        )
        if not allow_without_receipt:
            frappe.throw(_(
                "Supplier '{0}' requires a Goods Receipt Note before invoicing. "
                "Please raise a GRN first, then use GRN-linked invoicing."
            ).format(supplier))

    if mode == "grn_linked":
        return _create_invoice_from_grn(grn_name, posting_date)
    else:
        return _create_standalone_invoice(supplier, items_list, posting_date)


def _create_invoice_from_grn(grn_name, posting_date=None):
    """Builds and submits a Purchase Invoice linked to a submitted GRN."""
    # Lock GRN row to prevent concurrent invoicing
    result = frappe.db.sql(
        "SELECT docstatus, per_billed, supplier FROM `tabPurchase Receipt` WHERE name=%s FOR UPDATE",
        grn_name, as_dict=True
    )
    if not result:
        frappe.throw(_("GRN '{0}' not found.").format(grn_name), frappe.DoesNotExistError)
    row = result[0]
    if row.docstatus != 1:
        frappe.throw(_("GRN '{0}' must be in submitted state.").format(grn_name))
    if flt(row.per_billed) >= 100:
        frappe.throw(_("GRN '{0}' is already fully invoiced.").format(grn_name))

    grn = erp_adapter.get_grn(grn_name)
    company = erp_adapter.resolve_company()

    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier          = grn.supplier
    pi.company           = company
    pi.posting_date      = posting_date or nowdate()
    pi.currency          = grn.currency or "INR"
    pi.smriti_creation_mode = "grn_linked"

    for item in grn.items:
        pi.append("items", {
            "item_code":       item.item_code,
            "qty":             flt(item.qty),
            "rate":            flt(item.rate),
            "purchase_receipt": grn_name,
            "pr_detail":       item.name,
            "warehouse":       item.warehouse,
            "uom":             item.uom
        })

    pi_name = erp_adapter.insert_and_submit_pi(pi)
    audit_service.log(
        event_type=audit_service.PI_SUBMITTED,
        payload={"doctype": "Purchase Invoice", "name": pi_name,
                 "mode": "grn_linked", "grn_ref": grn_name,
                 "supplier": grn.supplier, "grand_total": flt(pi.grand_total)}
    )
    return {
        "status":  "submitted",
        "name":    pi_name,
        "mode":    "grn_linked",
        "message": _("Purchase Invoice {0} submitted.").format(pi_name)
    }


def _create_standalone_invoice(supplier, items_list, posting_date=None):
    """Builds and submits a standalone Purchase Invoice."""
    if not supplier or not frappe.db.exists("Supplier", supplier):
        frappe.throw(_("Supplier '{0}' not found.").format(supplier))
    if not items_list:
        frappe.throw(_("Cannot create Purchase Invoice with an empty items list."))

    company = erp_adapter.resolve_company()
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier             = supplier
    pi.company              = company
    pi.posting_date         = posting_date or nowdate()
    pi.smriti_creation_mode = "standalone"

    item_flags = erp_adapter.get_item_flags([it.get("item_code") for it in items_list])
    for it in items_list:
        item_code = it.get("item_code")
        qty       = flt(it.get("qty"))
        rate      = flt(it.get("rate"))
        if qty <= 0:
            frappe.throw(_("Item '{0}': qty must be greater than 0.").format(item_code))
        flags = item_flags.get(item_code) or frappe._dict()
        pi.append("items", {
            "item_code": item_code,
            "qty":       qty,
            "rate":      rate,
            "warehouse": it.get("warehouse") or erp_adapter.get_default_warehouse(company),
            "uom":       it.get("uom") or flags.get("stock_uom") or "Nos"
        })

    pi_name = erp_adapter.insert_and_submit_pi(pi)
    audit_service.log(
        event_type=audit_service.PI_SUBMITTED,
        payload={"doctype": "Purchase Invoice", "name": pi_name,
                 "mode": "standalone", "supplier": supplier,
                 "grand_total": flt(pi.grand_total)}
    )
    return {
        "status":  "submitted",
        "name":    pi_name,
        "mode":    "standalone",
        "message": _("Purchase Invoice {0} submitted.").format(pi_name)
    }


# ─────────────────────────────────────────────────────────────────────────────
# PURCHASE RETURNS
# ─────────────────────────────────────────────────────────────────────────────

def list_returns(company=None, supplier=None, from_date=None, to_date=None,
                 page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1, "is_return": 1}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    fields = ["name", "supplier", "supplier_name", "posting_date", "grand_total", "status"]
    return erp_adapter.list_grns(filters, fields, page, page_size)


def create_purchase_return(grn_name, items_list=None, return_reason=None):
    """
    Creates a Purchase Return (stock reversal) against a submitted GRN.
    If the GRN was invoiced, also creates a Debit Note (GL reversal).
    Both operations run in a single transaction — if either fails, both roll back.
    """
    check_manager_role()

    if not return_reason or not return_reason.strip():
        frappe.throw(_("Return reason is mandatory (SPC Rule 13: auditability)."))

    # Verify GRN is submitted
    grn_data = frappe.db.sql(
        "SELECT docstatus, per_billed, supplier FROM `tabPurchase Receipt` WHERE name=%s FOR UPDATE",
        grn_name, as_dict=True
    )
    if not grn_data:
        frappe.throw(_("GRN '{0}' not found.").format(grn_name), frappe.DoesNotExistError)
    grn_row = grn_data[0]
    if grn_row.docstatus != 1:
        frappe.throw(_("GRN '{0}' must be submitted to create a return.").format(grn_name))

    grn_was_invoiced = flt(grn_row.per_billed) > 0

    # Build return document
    return_doc = erp_adapter.make_purchase_return(grn_name)
    return_doc.smriti_return_reason = return_reason

    # If partial return — adjust quantities
    if items_list:
        _adjust_return_quantities(return_doc, items_list, grn_name)

    debit_note_name = None
    try:
        # Submit return (stock reversal via ERPNext)
        return_name = erp_adapter.insert_and_submit_return(return_doc)

        # If invoiced — create Debit Note in same transaction
        if grn_was_invoiced:
            pi_name = _find_pi_for_grn(grn_name)
            if pi_name:
                dn_doc = erp_adapter.make_purchase_return_pi(pi_name)
                debit_note_name = erp_adapter.insert_and_submit_debit_note(dn_doc)

        # Single commit covers BOTH return and debit note
        frappe.db.commit()

        audit_service.log(
            event_type=audit_service.RETURN_SUBMITTED,
            payload={"doctype": "Purchase Receipt", "name": return_name,
                     "grn_ref": grn_name, "supplier": grn_row.supplier},
            reason=return_reason
        )
        if debit_note_name:
            audit_service.log(
                event_type=audit_service.DEBIT_NOTE_CREATED,
                payload={"doctype": "Purchase Invoice", "name": debit_note_name,
                         "grn_ref": grn_name, "return_ref": return_name}
            )
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "status":       "submitted",
        "return_name":  return_name,
        "debit_note":   debit_note_name,
        "message":      _("Purchase Return {0} submitted.").format(return_name)
    }


def _adjust_return_quantities(return_doc, items_list, grn_name):
    """Applies partial return quantities to the return document."""
    qty_map = {it.get("item_code"): flt(it.get("qty")) for it in items_list}
    for item in return_doc.items:
        requested_return = qty_map.get(item.item_code, 0)
        original_received = frappe.db.get_value(
            "Purchase Receipt Item",
            {"parent": grn_name, "item_code": item.item_code},
            "qty"
        ) or 0
        if abs(requested_return) > flt(original_received):
            frappe.throw(_(
                "Item '{0}': return qty {1} exceeds originally received qty {2}."
            ).format(item.item_code, requested_return, original_received))
        item.qty = -abs(requested_return)


def _find_pi_for_grn(grn_name):
    """Finds the Purchase Invoice linked to this GRN (if any)."""
    pi = frappe.db.get_value(
        "Purchase Invoice Item",
        {"purchase_receipt": grn_name, "docstatus": 1},
        "parent"
    )
    return pi


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER LEDGER
# ─────────────────────────────────────────────────────────────────────────────

def get_supplier_ledger(supplier, from_date, to_date, company=None):
    check_manager_role()

    if not supplier:
        frappe.throw(_("Supplier is required."))
    if not from_date or not to_date:
        frappe.throw(_("Date range is required for Supplier Ledger."))
    if not frappe.db.exists("Supplier", supplier):
        frappe.throw(_("Supplier '{0}' not found.").format(supplier), frappe.DoesNotExistError)

    company   = company or erp_adapter.resolve_company()
    entries   = erp_adapter.get_supplier_gl_entries(supplier, from_date, to_date, company)
    outstanding = erp_adapter.get_supplier_outstanding(supplier, company)
    supplier_name = frappe.db.get_value("Supplier", supplier, "supplier_name")

    # Compute running balance
    balance = 0.0
    for entry in entries:
        balance += flt(entry.get("debit", 0)) - flt(entry.get("credit", 0))
        entry["balance"] = balance

    overdue = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as overdue
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 AND supplier=%s AND company=%s
              AND outstanding_amount > 0 AND due_date < CURDATE()
    """, (supplier, company), as_dict=True)
    overdue_amt = flt(overdue[0].overdue) if overdue else 0.0

    return {
        "supplier":      supplier,
        "supplier_name": supplier_name or supplier,
        "total_payable": outstanding,
        "overdue":       overdue_amt,
        "entries":       entries
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def search_suppliers(query, company=None):
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    results = frappe.get_all(
        "Supplier",
        filters=[["supplier_name", "like", f"%{query}%"]],
        fields=["name", "supplier_name", "supplier_group"],
        limit_page_length=20
    )
    return results


def search_items(query):
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    results = frappe.get_all(
        "Item",
        filters=[
            ["is_stock_item", "=", 1],
            ["|", ["item_code", "like", f"%{query}%"],
                  ["item_name", "like", f"%{query}%"]]
        ],
        fields=["item_code", "item_name", "stock_uom", "has_batch_no", "standard_rate"],
        limit_page_length=20
    )
    return results


# ─────────────────────────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _save_variant_image(image_base64, image_filename, items_list):
    """Saves a base64 image and returns the file URL. Returns None on failure."""
    if not image_base64 or not image_filename:
        return None
    try:
        import base64
        from frappe.utils.file_manager import save_file
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        file_content  = base64.b64decode(image_base64)
        first_code    = items_list[0].get("item_code") if items_list else "temp_item"
        saved         = save_file(image_filename, file_content, "Item", first_code,
                                  decode=False, is_private=0)
        return saved.file_url
    except Exception as e:
        frappe.log_error(f"SMRITI: Failed to save variant image: {str(e)}")
        return None


def _auto_create_item_if_missing(item_code, rate, file_url=None):
    """
    Auto-creates a footwear variant Item in ERPNext if it does not exist.
    Migrated from purchase_api.py with identical logic — preserved for backward compatibility.
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
    item.item_group           = "Footwear" if frappe.db.exists("Item Group", "Footwear") else "Products"
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

    hsn_code = (frappe.db.get_value("GST HSN Code", {"name": ["like", "64%"]}, "name")
                or frappe.db.get_value("GST HSN Code", {}, "name"))
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
