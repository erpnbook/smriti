# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/api/purchase_api.py
# @desc:    Whitelisted API endpoints for SMRITI Purchase Studio (SC-01 to SC-14).
#           This layer is intentionally thin — no business logic lives here.
#           Every function: parse input → call service → return result.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 5 (API Layer)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from smriti_retail_os.purchase_studio.service import purchase_service as svc
from smriti_retail_os.purchase_studio.service import purchase_settings_service as settings_svc


# ─────────────────────────────────────────────────────────────────────────────
# SC-01 — Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_dashboard(company=None):
    """Returns KPIs and recent activity for the Purchase Studio dashboard."""
    return svc.get_dashboard_data(company)


# ─────────────────────────────────────────────────────────────────────────────
# SC-02 — Purchase Orders List
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_orders(company=None, supplier=None, status=None,
                        from_date=None, to_date=None, search_term=None,
                        page=1, page_size=50):
    return svc.list_purchase_orders(
        company=company, supplier=supplier, status=status,
        from_date=from_date, to_date=to_date, search_term=search_term,
        page=frappe.utils.cint(page), page_size=frappe.utils.cint(page_size)
    )


# ─────────────────────────────────────────────────────────────────────────────
# SC-03 — Purchase Order Detail
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_order_detail(po_name):
    return svc.get_purchase_order_detail(po_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-04 — Create Purchase Order
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_purchase_order(supplier, items, schedule_date=None, remarks=None,
                          image_base64=None, image_filename=None, warehouse=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return svc.create_purchase_order(
        supplier=supplier,
        items_list=items_list,
        schedule_date=schedule_date,
        remarks=remarks,
        image_base64=image_base64,
        image_filename=image_filename,
        warehouse=warehouse
    )


# ─────────────────────────────────────────────────────────────────────────────
# SC-05 — Approval / Rejection
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def resolve_po_approval(po_name, action, reason=None):
    return svc.resolve_po_approval(po_name, action, reason)


# ─────────────────────────────────────────────────────────────────────────────
# SC-06 — GRN List + Detail
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_grns(company=None, supplier=None, po_name=None, status=None,
             from_date=None, to_date=None, mode=None, page=1, page_size=50):
    return svc.list_grns(
        company=company, supplier=supplier, po_name=po_name, status=status,
        from_date=from_date, to_date=to_date, mode=mode,
        page=frappe.utils.cint(page), page_size=frappe.utils.cint(page_size)
    )


@frappe.whitelist()
def get_grn_detail(grn_name):
    return svc.get_grn_detail(grn_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-07 — Create GRN
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_grn(supplier, items, po_name=None, warehouse=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return svc.create_grn(
        supplier=supplier,
        items_list=items_list,
        po_name=po_name,
        warehouse=warehouse
    )


# ─────────────────────────────────────────────────────────────────────────────
# SC-08 — Create Purchase Invoice (unified)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_invoice(mode, supplier=None, grn_name=None, items=None, posting_date=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return svc.create_invoice(
        mode=mode,
        supplier=supplier,
        grn_name=grn_name,
        items_list=items_list,
        posting_date=posting_date
    )


# ─────────────────────────────────────────────────────────────────────────────
# SC-09 — Invoice List + Detail
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_invoices(company=None, supplier=None, status=None, from_date=None,
                 to_date=None, mode=None, page=1, page_size=50):
    return svc.list_invoices(
        company=company, supplier=supplier, status=status,
        from_date=from_date, to_date=to_date, mode=mode,
        page=frappe.utils.cint(page), page_size=frappe.utils.cint(page_size)
    )


@frappe.whitelist()
def get_invoice_detail(pi_name):
    return svc.get_invoice_detail(pi_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-10 — Purchase Return
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_returns(company=None, supplier=None, from_date=None, to_date=None,
                page=1, page_size=50):
    return svc.list_returns(
        company=company, supplier=supplier,
        from_date=from_date, to_date=to_date,
        page=frappe.utils.cint(page), page_size=frappe.utils.cint(page_size)
    )


@frappe.whitelist()
def create_purchase_return(grn_name, items=None, return_reason=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return svc.create_purchase_return(
        grn_name=grn_name,
        items_list=items_list,
        return_reason=return_reason
    )


# ─────────────────────────────────────────────────────────────────────────────
# SC-11 — Supplier Ledger
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_supplier_ledger(supplier, from_date, to_date, company=None):
    return svc.get_supplier_ledger(supplier, from_date, to_date, company)


# ─────────────────────────────────────────────────────────────────────────────
# SC-12 — Settings
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_settings():
    svc.check_system_manager()
    return settings_svc.get_settings()


@frappe.whitelist()
def save_purchase_settings(fields):
    svc.check_system_manager()
    fields_dict = frappe.parse_json(fields) if isinstance(fields, str) else fields
    settings_svc.save_settings(fields_dict)
    return {"status": "saved", "message": "Settings updated successfully."}


# ─────────────────────────────────────────────────────────────────────────────
# SC-13 — Supplier Search
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def search_suppliers(query, company=None):
    return svc.search_suppliers(query, company)


# ─────────────────────────────────────────────────────────────────────────────
# SC-14 — Item Search
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def search_items(query):
    return svc.search_items(query)


# ─────────────────────────────────────────────────────────────────────────────
# BACKWARD COMPATIBILITY — Existing purchase.html still calls purchase_api.py
# These endpoints are NOT deprecated — they delegate to the new service layer.
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_open_purchase_orders(supplier=None):
    """
    Legacy endpoint used by purchase.html.
    Delegates to purchase_service — no direct ERPNext calls.
    """
    result = svc.list_purchase_orders(supplier=supplier, status="Submitted")
    return result.get("items", [])


@frappe.whitelist()
def get_po_details(po_name):
    """Legacy endpoint used by purchase.html. Delegates to service."""
    return svc.get_purchase_order_detail(po_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-15 — Warehouse List
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_warehouses(company=None):
    """Returns non-group warehouses for use in return-form warehouse picker."""
    filters = {"is_group": 0}
    if company:
        filters["company"] = company
    rows = frappe.get_all(
        "Warehouse",
        filters=filters,
        fields=["name", "warehouse_name"],
        order_by="warehouse_name asc",
        limit=200
    )
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# SC-16 — Purchase Analytics
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_analytics(company=None, from_date=None, to_date=None):
    """Returns spend analytics: by supplier, by month, by item group."""
    return svc.get_purchase_analytics(company, from_date, to_date)


# ─────────────────────────────────────────────────────────────────────────────
# SC-17 — Supplier Performance
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_supplier_performance(company=None, from_date=None, to_date=None, top_n=10):
    """Returns supplier-wise on-time delivery rate, fill rate, and spend."""
    return svc.get_supplier_performance(company, from_date, to_date, frappe.utils.cint(top_n))


# ─────────────────────────────────────────────────────────────────────────────
# SC-18 — Items for GRN (pending items from a PO)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_items_for_grn(po_name):
    """Returns pending (not yet received) items from a Purchase Order for GRN entry."""
    return svc.get_items_for_grn(po_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-19 — Landed Cost Vouchers
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_landed_cost_vouchers(company=None, from_date=None, to_date=None, page=1, page_size=50):
    """Returns paginated Landed Cost Vouchers."""
    return svc.list_landed_cost_vouchers(
        company=company, from_date=from_date, to_date=to_date,
        page=frappe.utils.cint(page), page_size=frappe.utils.cint(page_size)
    )


@frappe.whitelist()
def create_landed_cost_voucher(grn_name, charges):
    """Creates a Landed Cost Voucher linked to a GRN."""
    charges_list = frappe.parse_json(charges) if isinstance(charges, str) else charges
    return svc.create_landed_cost_voucher(grn_name, charges_list)


# ─────────────────────────────────────────────────────────────────────────────
# SC-20 — Purchase Return Detail
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_return_detail(return_name):
    """Returns full detail of a Purchase Return (negative Purchase Receipt)."""
    return svc.get_return_detail(return_name)


# ─────────────────────────────────────────────────────────────────────────────
# SC-21 — Supplier List (for dropdowns)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_suppliers(company=None, search=None, limit=50):
    """Returns list of suppliers for dropdown selection."""
    return svc.get_suppliers(company, search, frappe.utils.cint(limit))
