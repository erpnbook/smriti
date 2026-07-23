# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/purchase_service.py
# @desc:    Purchase Studio business logic.
#           Order intent + approval trail: native SMRITI Supplier / SMRITI Purchase Order.
#           Execution documents (GRN, Invoice, Return): real ERPNext DocTypes via
#           purchase_studio.adapter.erp_adapter, so Stock Ledger, GL Entries, GST
#           fields, e-invoice/e-way bill and TDS are handled by ERPNext/india_compliance
#           and never re-implemented natively. See erp_adapter.py for the only file
#           permitted to call ERPNext DocType APIs directly.
#           UI → purchase_api.py → THIS FILE → SMRITI services/repos + erp_adapter.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 4 (Business Logic)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt, cint, nowdate, now_datetime

from smriti_retail_os.purchase_studio.service.purchase_order_service import PurchaseOrderService
from smriti_retail_os.purchase_studio.service.purchase_workflow_service import PurchaseWorkflowService
from smriti_retail_os.purchase_studio.service.purchase_settings_service import get_settings
from smriti_retail_os.purchase_studio.service import audit_service
from smriti_retail_os.purchase_studio.adapter import erp_adapter
from smriti_retail_os.purchase_studio.repository import PurchaseRepository


# ─────────────────────────────────────────────────────────────────────────────
# ROLE GUARD
# ─────────────────────────────────────────────────────────────────────────────

def check_manager_role():
    """Enforces Store Manager or System Manager."""
    from smriti_retail_os.security_api import get_allowed_manager_roles
    roles = set(frappe.get_roles(frappe.session.user))
    if not (roles & get_allowed_manager_roles()):
        frappe.throw(
            _("Access Denied: Only Store Managers or System Managers can perform this action."),
            frappe.PermissionError
        )


def check_any_purchase_role():
    """Allows Cashier, Store Manager, or System Manager (view access)."""
    from smriti_retail_os.security_api import get_allowed_manager_roles, get_allowed_cashier_role
    roles = set(frappe.get_roles(frappe.session.user))
    allowed = get_allowed_manager_roles() | {get_allowed_cashier_role()}
    if not allowed.intersection(roles):
        frappe.throw(_("Access Denied: Purchase Studio requires a SMRITI role."), frappe.PermissionError)


def check_system_manager():
    """Enforces System Manager only (for Settings)."""
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Access Denied: Only System Managers can access Purchase Settings."), frappe.PermissionError)


# ─────────────────────────────────────────────────────────────────────────────
# CORE OPERATIONS delegating to PurchaseOrderService
# ─────────────────────────────────────────────────────────────────────────────

def get_dashboard_data(company=None):
    check_any_purchase_role()
    return PurchaseOrderService.get_dashboard_data(company)


def list_purchase_orders(company=None, supplier=None, status=None,
                          from_date=None, to_date=None,
                          search_term=None, page=1, page_size=50):
    check_any_purchase_role()
    return PurchaseOrderService.list_purchase_orders(
        company=company, supplier=supplier, status=status,
        from_date=from_date, to_date=to_date, search_term=search_term,
        page=page, page_size=page_size
    )


def get_purchase_order_detail(po_name):
    check_any_purchase_role()
    return PurchaseOrderService.get_purchase_order_detail(po_name)


def create_purchase_order(supplier, items_list, schedule_date=None,
                           remarks=None, image_base64=None,
                           image_filename=None, warehouse=None,
                           tc_name=None, terms=None):
    check_manager_role()
    from smriti_retail_os.purchase_studio.service.purchase_validation_service import SmritiValidationError
    try:
        res = PurchaseOrderService.create_purchase_order(
            supplier=supplier,
            items_list=items_list,
            schedule_date=schedule_date,
            remarks=remarks,
            warehouse=warehouse,
            tc_name=tc_name,
            terms=terms
        )
    except SmritiValidationError as e:
        frappe.throw(str(e))
    
    audit_service.log(
        event_type=audit_service.PO_SUBMITTED if res["status"] == "submitted" else audit_service.PO_PENDING_APPROVAL,
        payload={"doctype": "SMRITI Purchase Order", "name": res["name"], "supplier": supplier},
        after={"status": res["status"]}
    )
    return res


def resolve_po_approval(po_name, action, reason=None):
    check_system_manager()
    res = PurchaseOrderService.resolve_po_approval(po_name, action, reason)
    audit_service.log(
        event_type=audit_service.PO_APPROVED if action == "approve" else audit_service.PO_REJECTED,
        payload={"doctype": "SMRITI Purchase Order", "name": po_name},
        reason=reason
    )
    return res


# ─────────────────────────────────────────────────────────────────────────────
# GRN / RECEIPTS — real ERPNext Purchase Receipt, built from a SMRITI PO
# ─────────────────────────────────────────────────────────────────────────────

def list_grns(company=None, supplier=None, po_name=None, status=None,
              from_date=None, to_date=None, mode=None, page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    if supplier:
        erp_supplier = smriti.db.get("SMRITI Supplier", supplier, "erpnext_supplier")
        filters["supplier"] = erp_supplier or supplier
    if po_name:
        filters["smriti_source_po"] = po_name
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    limit_start = (int(page) - 1) * int(page_size)
    result = erp_adapter.list_grns(
        filters=filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "grand_total", "per_billed", "status", "smriti_source_po"],
        page=int(page),
        page_size=int(page_size)
    )
    return result


def get_grn_detail(grn_name):
    check_any_purchase_role()
    pr = erp_adapter.get_grn(grn_name)
    items = [{
        "item_code": row.item_code,
        "item_name": row.item_name,
        "qty": row.qty,
        "rate": row.rate,
        "amount": row.amount,
        "warehouse": row.warehouse,
        "uom": row.uom,
        "batch_no": row.get("batch_no"),
    } for row in pr.items]
    return {
        "name": pr.name,
        "supplier": pr.supplier,
        "supplier_name": pr.supplier_name,
        "company": pr.company,
        "posting_date": pr.posting_date,
        "grand_total": pr.grand_total,
        "status": pr.status,
        "smriti_source_po": pr.get("smriti_source_po"),
        "items": items,
    }


def create_grn(supplier, items_list, po_name=None, warehouse=None):
    check_manager_role()
    if not po_name:
        frappe.throw(_("SMRITI Purchase Studio requires a Purchase Order reference for GRN creation."))

    smriti_po = PurchaseRepository.get_po(po_name)
    received_items = {it["item_code"]: flt(it["qty"]) for it in items_list}

    grn_name = erp_adapter.build_and_submit_grn(smriti_po, received_items, warehouse=warehouse)

    # Keep SMRITI PO received_qty/status in sync for approval-trail reporting
    PurchaseWorkflowService.receive(po_name, received_items)

    audit_service.log(
        event_type=audit_service.GRN_SUBMITTED,
        payload={"doctype": "Purchase Receipt", "name": grn_name, "source_po": po_name, "supplier": supplier, "items_count": len(items_list)}
    )
    return {
        "status": "submitted",
        "name": grn_name,
        "message": _("GRN {0} created against PO {1}.").format(grn_name, po_name)
    }


# ─────────────────────────────────────────────────────────────────────────────
# INVOICES — real ERPNext Purchase Invoice, linked to a submitted GRN
# ─────────────────────────────────────────────────────────────────────────────

def list_invoices(company=None, supplier=None, status=None, from_date=None,
                  to_date=None, mode=None, page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    if supplier:
        erp_supplier = smriti.db.get("SMRITI Supplier", supplier, "erpnext_supplier")
        filters["supplier"] = erp_supplier or supplier
    if status:
        filters["status"] = status
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    limit_start = (int(page) - 1) * int(page_size)
    return erp_adapter.list_purchase_invoices(
        filters=filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "grand_total", "status", "smriti_creation_mode"],
        page=int(page),
        page_size=int(page_size)
    )


def get_invoice_detail(pi_name):
    check_any_purchase_role()
    pi = erp_adapter.get_pi(pi_name)
    items = [{
        "item_code": row.item_code,
        "item_name": row.item_name,
        "qty": row.qty,
        "rate": row.rate,
        "amount": row.amount,
    } for row in pi.items]
    return {
        "name": pi.name,
        "supplier": pi.supplier,
        "supplier_name": pi.supplier_name,
        "company": pi.company,
        "posting_date": pi.posting_date,
        "grand_total": pi.grand_total,
        "status": pi.status,
        "creation_mode": pi.get("smriti_creation_mode"),
        "items": items,
    }


def create_invoice(mode, supplier=None, grn_name=None, items_list=None, posting_date=None):
    check_manager_role()
    if not grn_name:
        frappe.throw(_("GRN reference is required for Invoice creation."))

    pi_name = erp_adapter.build_and_submit_invoice(grn_name, posting_date=posting_date)

    source_po = smriti.db.get("Purchase Receipt", grn_name, "smriti_source_po")
    if source_po:
        PurchaseWorkflowService.close(source_po)

    audit_service.log(
        event_type=audit_service.PI_SUBMITTED,
        payload={"doctype": "Purchase Invoice", "name": pi_name, "grn": grn_name, "supplier": supplier}
    )
    return {
        "status": "submitted",
        "name": pi_name,
        "message": _("Invoice {0} created against GRN {1}.").format(pi_name, grn_name)
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETURNS — real ERPNext Purchase Return, built against a submitted GRN
# ─────────────────────────────────────────────────────────────────────────────

def list_returns(company=None, supplier=None, from_date=None, to_date=None,
                 page=1, page_size=50):
    check_any_purchase_role()
    filters = {"docstatus": 1, "is_return": 1}
    if company:
        filters["company"] = company
    if supplier:
        erp_supplier = smriti.db.get("SMRITI Supplier", supplier, "erpnext_supplier")
        filters["supplier"] = erp_supplier or supplier
    if from_date:
        filters["posting_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("posting_date", ["<=", to_date])

    limit_start = (int(page) - 1) * int(page_size)
    return erp_adapter.list_grns(
        filters=filters,
        fields=["name", "supplier", "supplier_name", "posting_date", "grand_total", "status", "smriti_return_reason"],
        page=int(page),
        page_size=int(page_size)
    )


def create_purchase_return(grn_name, items_list=None, return_reason=None):
    check_manager_role()
    if not return_reason or not return_reason.strip():
        frappe.throw(_("Return reason is mandatory."))

    return_name = erp_adapter.build_and_submit_return(grn_name, return_items=items_list, reason=return_reason)

    audit_service.log(
        event_type=audit_service.RETURN_SUBMITTED,
        payload={"doctype": "Purchase Receipt", "name": return_name, "against_grn": grn_name},
        reason=return_reason
    )
    return {
        "status": "submitted",
        "return_name": return_name,
        "message": _("Purchase Return {0} created against GRN {1}.").format(return_name, grn_name)
    }


def validate_grn_lines(items_list, po_name=None, allow_over_receipt=False):
    """Legacy validation function kept for test backward compatibility."""
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIER LEDGER
# ─────────────────────────────────────────────────────────────────────────────

def get_supplier_ledger(supplier, from_date, to_date, company=None):
    check_manager_role()
    if not supplier:
        frappe.throw(_("Supplier is required."))
    if not from_date or not to_date:
        frappe.throw(_("From Date and To Date are required."))
    company = company or frappe.defaults.get_user_default("Company")

    # Bridge SMRITI Supplier → ERPNext Supplier for GL lookup
    erp_supplier = smriti.db.get("SMRITI Supplier", supplier, "erpnext_supplier") or supplier
    supplier_name = smriti.db.get("SMRITI Supplier", supplier, "supplier_name") or supplier

    # Read actual GL entries — SMRITI reads GL, never writes it
    gl_entries = erp_adapter.get_supplier_gl_entries(erp_supplier, from_date, to_date, company)
    outstanding = erp_adapter.get_supplier_outstanding(erp_supplier, company)
    overdue = erp_adapter.get_supplier_overdue_payable(erp_supplier, company)

    balance = 0.0
    entries = []
    for row in gl_entries:
        debit  = flt(row.get("debit", 0))
        credit = flt(row.get("credit", 0))
        balance += credit - debit
        entries.append({
            "posting_date": str(row.get("posting_date", "")),
            "voucher_type": row.get("voucher_type", ""),
            "voucher_no":   row.get("voucher_no", ""),
            "debit":        debit,
            "credit":       credit,
            "balance":      balance,
            "remarks":      row.get("remarks", "")
        })

    return {
        "supplier":       supplier,
        "supplier_name":  supplier_name,
        "total_payable":  outstanding,
        "overdue":        overdue,
        "entries":        entries
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def search_suppliers(query, company=None):
    """SC-13 — thin alias for get_suppliers; kept for API backward compatibility."""
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    return get_suppliers(company=company, search=query, limit=20)


def get_suppliers(company=None, search=None, limit=50):
    check_any_purchase_role()
    return PurchaseOrderService.list_suppliers(search_term=search, limit=limit)


def search_items(query):
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    return smriti.db.get_list(
        "Item",
        filters={"disabled": 0, "item_code": ["like", f"%{query}%"]},
        fields=["name as item_code", "item_name", "standard_rate", "has_variants", "variant_of", "stock_uom"],
        limit=20
    )


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS & PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────

def get_purchase_analytics(company=None, from_date=None, to_date=None):
    """
    Returns spend analytics based on actual ERPNext Purchase Invoices.
    Data source: tabPurchase Invoice (GST-inclusive, real payments)
    — not SMRITI PO amounts which are pre-GST intent records.
    """
    check_any_purchase_role()
    company = company or frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
    return erp_adapter.get_purchase_spend_analytics(company, from_date=from_date, to_date=to_date)


def get_supplier_performance(company=None, from_date=None, to_date=None, top_n=10):
    """
    Returns supplier KPIs from ERPNext Purchase Orders and Purchase Invoices.
    Delegates to erp_adapter to keep all DocType queries in the adapter layer.
    """
    check_any_purchase_role()
    company = company or frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
    return erp_adapter.get_supplier_performance_data(
        company, from_date=from_date, to_date=to_date, top_n=top_n
    )


def get_items_for_grn(po_name):
    check_any_purchase_role()
    po = PurchaseOrderService.get_purchase_order_detail(po_name)
    items = []
    for item in po["items"]:
        pending = flt(item["qty"]) - flt(item["received_qty"])
        if pending <= 0:
            continue
        items.append({
            "item_code": item["item_code"],
            "item_name": item["item_name"],
            "qty": flt(item["qty"]),
            "received_qty": flt(item["received_qty"]),
            "pending_qty": pending,
            "rate": flt(item["rate"]),
            "uom": item["uom"],
            "warehouse": item["warehouse"],
            "has_batch_no": 0,
            "po_item_name": item["name"]
        })
    return {
        "po_name": po["name"],
        "supplier": po["supplier"],
        "supplier_name": po["supplier_name"],
        "company": po["company"],
        "items": items
    }


# ─────────────────────────────────────────────────────────────────────────────
# SC-22 — Special PO Matrix Print Data
# ─────────────────────────────────────────────────────────────────────────────

def get_po_matrix_print_data(po_name):
    """
    Fetches PO detail and restructures flat items into a Color×Size matrix.
    Returns company info, supplier info, PO meta, matrix data, and image url.
    """
    check_any_purchase_role()

    po = PurchaseOrderService.get_purchase_order_detail(po_name)

    # Load company info
    company = po.get("company") or frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
    comp_doc = smriti.documents.get("Company", company) if smriti.db.exists("Company", company) else None
    cs = smriti.db.get(
        "SMRITI Company Settings", {"company": company},
        ["store_trade_name", "store_logo_url", "receipt_footer_text"],
        as_dict=True
    ) or {}

    company_info = {
        "company_name": cs.get("store_trade_name") or (comp_doc.company_name if comp_doc else company),
        "logo_url": cs.get("store_logo_url") or "",
        "address": getattr(comp_doc, "company_description", "") if comp_doc else "",
        "tax_id": getattr(comp_doc, "tax_id", "") if comp_doc else "",
        "phone_no": getattr(comp_doc, "phone_no", "") if comp_doc else "",
        "email": getattr(comp_doc, "email", "") if comp_doc else "",
    }

    # Supplier info
    supplier_doc = smriti.db.get(
        "SMRITI Supplier", po.get("supplier"),
        ["supplier_name", "billing_address", "tax_id", "mobile_no", "email_id"],
        as_dict=True
    ) or {}

    # Build Color × Size matrix from flat items
    matrix = {}    # { article: { color: { size: {qty, rate} } } }
    all_sizes = set()

    for item in po.get("items", []):
        item_code = item.get("item_code")
        if not item_code:
            continue

        # Read attributes from Item Variant Attribute table
        attrs = smriti.db.get_list(
            "Item Variant Attribute",
            filters={"parent": item_code},
            fields=["attribute", "attribute_value"]
        )
        attr_map = {a.attribute.lower(): a.attribute_value for a in attrs}
        color = attr_map.get("colour") or attr_map.get("color") or "-"
        size  = attr_map.get("size") or attr_map.get("shoe size") or "-"

        # Resolve article from item meta
        article = (
            smriti.db.get("Item", item_code, "custom_style_code")
            or smriti.db.get("Item", item_code, "variant_of")
            or item_code
        )

        all_sizes.add(size)
        if article not in matrix:
            matrix[article] = {}
        if color not in matrix[article]:
            matrix[article][color] = {}
        matrix[article][color][size] = {
            "qty": flt(item.get("qty")),
            "rate": flt(item.get("rate"))
        }

    # Sort sizes numerically where possible
    def size_sort_key(s):
        try:
            return (0, float(s))
        except (ValueError, TypeError):
            return (1, str(s))

    sorted_sizes = sorted(all_sizes, key=size_sort_key)

    # Resolve product image (first attachment on the PO document)
    image_url = smriti.db.get("SMRITI Purchase Order", po_name, "image") or ""
    if not image_url:
        attachments = smriti.db.get_list(
            "File",
            filters={"attached_to_doctype": "SMRITI Purchase Order", "attached_to_name": po_name},
            fields=["file_url"],
            limit=1,
            order_by="creation asc"
        )
        image_url = attachments[0].file_url if attachments else ""

    return {
        "po": {
            "name": po.get("name"),
            "transaction_date": po.get("transaction_date"),
            "schedule_date": po.get("schedule_date"),
            "status": po.get("status"),
            "remarks": po.get("remarks"),
            "grand_total": flt(po.get("grand_total")),
            "total_qty": flt(po.get("total_qty")),
        },
        "company_info": company_info,
        "supplier": {
            "name": po.get("supplier"),
            "supplier_name": supplier_doc.get("supplier_name") or po.get("supplier_name"),
            "address": supplier_doc.get("billing_address") or "",
            "tax_id": supplier_doc.get("tax_id") or "",
            "mobile_no": supplier_doc.get("mobile_no") or "",
            "email_id": supplier_doc.get("email_id") or "",
        },
        "sizes": sorted_sizes,
        "matrix": matrix,
        "image_url": image_url,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SC-23 — Size Presets
# ─────────────────────────────────────────────────────────────────────────────

def get_size_presets():
    """
    Returns size preset definitions from SMRITI Company Settings.
    Falls back to built-in presets when none are configured.
    Returns {"presets": {...}, "using_defaults": bool} so the UI can prompt
    the user to configure size groups when defaults are active.
    """
    import json
    company = frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
    raw = smriti.db.get("SMRITI Company Settings", {"company": company}, "size_groups_json") or ""
    try:
        presets = json.loads(raw) if raw else {}
    except Exception:
        presets = {}

    using_defaults = not bool(presets)
    if using_defaults:
        presets = {
            "Footwear (35-43)": ["35", "36", "37", "38", "39", "40", "41", "42", "43"],
            "Kids (20-30)":     ["20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"],
            "Open (XS-XXL)":    ["XS", "S", "M", "L", "XL", "XXL"],
            "Generic (Single Size)": ["-"],
        }
    return {"presets": presets, "using_defaults": using_defaults}

def resolve_variant_item(article, color, size):
    """
    Returns the item_code for a variant matching article, color, and size.
    Uses a single batch query for attributes instead of N+1 per variant.
    """
    check_any_purchase_role()

    if not article or not color or not size:
        return None

    # Find all variants of the article (by variant_of or custom_style_code)
    items = smriti.db.get_list("Item", filters={"disabled": 0, "variant_of": article}, fields=["name"])
    if not items:
        items = smriti.db.get_list("Item", filters={"disabled": 0, "custom_style_code": article}, fields=["name"])
    if not items:
        return article if smriti.db.exists("Item", article) else None

    # Batch-fetch ALL attributes for ALL variants in a single query (eliminates N+1)
    item_codes = [i.name for i in items]
    all_attrs = smriti.db.get_list(
        "Item Variant Attribute",
        filters={"parent": ["in", item_codes]},
        fields=["parent", "attribute", "attribute_value"]
    )

    # Group by item_code → {item_code: {attribute_lower: value_lower}}
    attr_by_item = {}
    for a in all_attrs:
        attr_by_item.setdefault(a.parent, {})[a.attribute.lower()] = a.attribute_value.lower()

    color_lower = color.lower()
    size_lower  = size.lower()

    for item in items:
        attr_map = attr_by_item.get(item.name, {})
        c_val = attr_map.get("colour") or attr_map.get("color")
        s_val = attr_map.get("size") or attr_map.get("shoe size")
        if c_val == color_lower and s_val == size_lower:
            return item.name

    return None

