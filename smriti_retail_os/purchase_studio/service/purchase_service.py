# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/purchase_service.py
# @desc:    All Purchase Studio business logic, completely independent of ERPNext PO/Supplier.
#           UI → purchase_api.py → THIS FILE → new SMRITI services/repos.
#           No ERPNext DocType calls.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 4 (Business Logic)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, cint, nowdate, now_datetime

from smriti_retail_os.purchase_studio.service.purchase_order_service import PurchaseOrderService
from smriti_retail_os.purchase_studio.service.purchase_workflow_service import PurchaseWorkflowService
from smriti_retail_os.purchase_studio.service.purchase_settings_service import get_settings
from smriti_retail_os.purchase_studio.service import audit_service


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
                           image_filename=None, warehouse=None):
    check_manager_role()
    res = PurchaseOrderService.create_purchase_order(
        supplier=supplier,
        items_list=items_list,
        schedule_date=schedule_date,
        remarks=remarks,
        warehouse=warehouse
    )
    
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
# GRN / RECEIPTS Simulation
# ─────────────────────────────────────────────────────────────────────────────

def list_grns(company=None, supplier=None, po_name=None, status=None,
              from_date=None, to_date=None, mode=None, page=1, page_size=50):
    # Simulated GRNs list by listing SMRITI POs that are Partially Received or Completed
    check_any_purchase_role()
    filters = {"status": ["in", ["Partially Received", "Completed"]]}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if po_name:
        filters["name"] = po_name
    if from_date:
        filters["transaction_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("transaction_date", ["<=", to_date])

    limit_start = (int(page) - 1) * int(page_size)
    items = frappe.get_list(
        "SMRITI Purchase Order",
        filters=filters,
        fields=["name", "supplier", "supplier_name", "transaction_date as posting_date", "grand_total", "per_received as per_billed", "status"],
        order_by="modified desc",
        limit_start=limit_start,
        limit_page_length=int(page_size)
    )
    total = frappe.db.count("SMRITI Purchase Order", filters=filters)
    return {"items": items, "total": total}


def get_grn_detail(grn_name):
    # Retrieve PO received quantities as a simulated GRN
    check_any_purchase_role()
    po = PurchaseOrderService.get_purchase_order_detail(grn_name)
    items = []
    for it in po["items"]:
        if flt(it["received_qty"]) > 0:
            items.append({
                "item_code": it["item_code"],
                "item_name": it["item_name"],
                "qty": it["received_qty"],
                "rate": it["rate"],
                "amount": it["received_qty"] * it["rate"],
                "warehouse": it["warehouse"],
                "uom": it["uom"],
                "batch_no": "BATCH-TEMP-SMRITI"
            })
    return {
        "name": po["name"],
        "supplier": po["supplier"],
        "supplier_name": po["supplier_name"],
        "company": po["company"],
        "posting_date": po["transaction_date"],
        "grand_total": sum(i["amount"] for i in items),
        "per_billed": po["per_received"],
        "status": "Submitted" if po["status"] in ("Partially Received", "Completed") else "Draft",
        "items": items
    }


def create_grn(supplier, items_list, po_name=None, warehouse=None):
    check_manager_role()
    if not po_name:
        frappe.throw(_("SMRITI Purchase Studio requires a Purchase Order reference for GRN creation."))
    
    received_items = {it["item_code"]: flt(it["qty"]) for it in items_list}
    po = PurchaseWorkflowService.receive(po_name, received_items)
    
    audit_service.log(
        event_type=audit_service.GRN_SUBMITTED,
        payload={"doctype": "SMRITI Purchase Order", "name": po_name, "supplier": supplier, "items_count": len(items_list)}
    )
    return {
        "status": "submitted",
        "name": po_name,
        "message": _("SMRITI GRN simulated for PO {0} successfully.").format(po_name)
    }


# ─────────────────────────────────────────────────────────────────────────────
# INVOICES Simulation
# ─────────────────────────────────────────────────────────────────────────────

def list_invoices(company=None, supplier=None, status=None, from_date=None,
                  to_date=None, mode=None, page=1, page_size=50):
    check_any_purchase_role()
    return list_grns(company, supplier, None, status, from_date, to_date, mode, page, page_size)


def get_invoice_detail(pi_name):
    check_any_purchase_role()
    return get_grn_detail(pi_name)


def create_invoice(mode, supplier=None, grn_name=None, items_list=None, posting_date=None):
    check_manager_role()
    if not grn_name:
        frappe.throw(_("GRN reference is required for Invoice creation."))
    
    po = PurchaseWorkflowService.close(grn_name)
    audit_service.log(
        event_type=audit_service.PI_SUBMITTED,
        payload={"doctype": "SMRITI Purchase Order", "name": grn_name, "supplier": supplier}
    )
    return {
        "status": "submitted",
        "name": grn_name,
        "message": _("SMRITI Invoice created for PO {0}.").format(grn_name)
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETURNS Simulation
# ─────────────────────────────────────────────────────────────────────────────

def list_returns(company=None, supplier=None, from_date=None, to_date=None,
                 page=1, page_size=50):
    check_any_purchase_role()
    filters = {"status": "Cancelled"}
    if company:
        filters["company"] = company
    if supplier:
        filters["supplier"] = supplier
    if from_date:
        filters["transaction_date"] = [">=", from_date]
    if to_date:
        filters.setdefault("transaction_date", ["<=", to_date])

    limit_start = (int(page) - 1) * int(page_size)
    items = frappe.get_list(
        "SMRITI Purchase Order",
        filters=filters,
        fields=["name", "supplier", "supplier_name", "transaction_date as posting_date", "grand_total", "status"],
        order_by="modified desc",
        limit_start=limit_start,
        limit_page_length=int(page_size)
    )
    total = frappe.db.count("SMRITI Purchase Order", filters=filters)
    return {"items": items, "total": total}


def create_purchase_return(grn_name, items_list=None, return_reason=None):
    check_manager_role()
    if not return_reason or not return_reason.strip():
        frappe.throw(_("Return reason is mandatory."))
    
    po = PurchaseWorkflowService.reject(grn_name, return_reason)
    audit_service.log(
        event_type=audit_service.RETURN_SUBMITTED,
        payload={"doctype": "SMRITI Purchase Order", "name": grn_name},
        reason=return_reason
    )
    return {
        "status": "submitted",
        "return_name": grn_name,
        "message": _("SMRITI Purchase Return processed for PO {0}.").format(grn_name)
    }


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
    pos = frappe.get_all(
        "SMRITI Purchase Order",
        filters={
            "supplier": supplier,
            "company": company,
            "transaction_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["name", "transaction_date", "grand_total", "status", "remarks"]
    )
    
    entries = []
    balance = 0.0
    for po in pos:
        credit = flt(po.grand_total)
        balance += credit
        entries.append({
            "posting_date": po.transaction_date,
            "voucher_type": "Purchase Order",
            "voucher_no": po.name,
            "debit": 0.0,
            "credit": credit,
            "balance": balance,
            "remarks": po.remarks or f"SMRITI PO status: {po.status}"
        })
    
    return {
        "supplier": supplier,
        "supplier_name": frappe.db.get_value("SMRITI Supplier", supplier, "supplier_name") or supplier,
        "total_payable": balance,
        "overdue": 0.0,
        "entries": entries
    }


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def search_suppliers(query, company=None):
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    return PurchaseOrderService.list_suppliers(search_term=query, limit=20)


def search_items(query):
    check_any_purchase_role()
    if not query or len(query) < 2:
        return []
    return frappe.get_all(
        "Item",
        filters={"disabled": 0, "item_code": ["like", f"%{query}%"]},
        fields=["name as item_code", "item_name", "standard_rate"],
        limit=20
    )


def get_suppliers(company=None, search=None, limit=50):
    check_any_purchase_role()
    return PurchaseOrderService.list_suppliers(search_term=search, limit=limit)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS & PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────

def get_purchase_analytics(company=None, from_date=None, to_date=None):
    check_any_purchase_role()
    company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    
    # Aggregation by Supplier
    by_supplier = frappe.db.sql("""
        SELECT 
            supplier_name as supplier,
            supplier_name,
            SUM(grand_total) as total_spend
        FROM `tabSMRITI Purchase Order`
        WHERE company = %s AND docstatus = 1 AND status != 'Cancelled'
        GROUP BY supplier_name
        ORDER BY total_spend DESC
        LIMIT 10
    """, (company,), as_dict=True)

    # Aggregation by Month
    by_month = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(transaction_date, '%Y-%m') as month,
            COUNT(name) as invoice_count,
            SUM(grand_total) as total_spend
        FROM `tabSMRITI Purchase Order`
        WHERE company = %s AND docstatus = 1 AND status != 'Cancelled'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """, (company,), as_dict=True)

    return {
        "by_supplier": by_supplier,
        "by_item_group": [{"item_group": "Footwear", "total_spend": sum(s["total_spend"] for s in by_supplier)}],
        "by_month": by_month
    }


def get_supplier_performance(company=None, from_date=None, to_date=None, top_n=10):
    check_any_purchase_role()
    company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    
    perf = frappe.db.sql("""
        SELECT 
            supplier as supplier,
            supplier_name,
            COUNT(name) as po_count,
            SUM(grand_total) as po_value,
            SUM(grand_total * (per_received / 100)) as received_value,
            AVG(per_received) as fill_rate,
            0.0 as overdue_amount
        FROM `tabSMRITI Purchase Order`
        WHERE company = %s AND docstatus = 1
        GROUP BY supplier
        ORDER BY po_value DESC
        LIMIT %s
    """, (company, int(top_n)), as_dict=True)
    return perf


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
