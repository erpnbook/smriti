# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/inventory_api.py
# @description: Backend API for SMRITI Inventory Operations terminal.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import flt, cint, nowdate
from frappe import _
from smriti_retail_os import smriti
from smriti_retail_os.utils.invoice_utils import get_barcode_candidates
from smriti_retail_os.security_api import check_administrator_only

# Security: allowlist for admin-only factory-reset TRUNCATE operations.
# Table names in reset_db MUST come from this set — never from user input.
# Architecture: H-7 remediation (hardcoding audit 2026-07-03)
_RESET_DB_SAFE_TABLES = frozenset([
    "tabStock Reconciliation", "tabStock Reconciliation Item",
    "tabStock Entry", "tabStock Entry Detail",
    "tabPurchase Receipt", "tabPurchase Receipt Item",
    "tabPurchase Invoice", "tabPurchase Invoice Item",
    "tabPurchase Order", "tabPurchase Order Item",
    "tabSales Invoice", "tabSales Invoice Item",
    "tabPOS Invoice", "tabPOS Invoice Item",
    "tabPayment Entry", "tabPayment Entry Reference", "tabPayment Entry Deduction",
    "tabGL Entry", "tabStock Ledger Entry", "tabPayment Ledger Entry",
    "tabBin", "tabSeries",
])

def _get_default_warehouse(company):
    """Company ke saath matching warehouse lo."""
    if not company:
        return None
    warehouse = smriti.db.get(
        "Warehouse",
        {"company": company, "is_group": 0, "warehouse_name": "Stores"},
        "name"
    )
    if not warehouse:
        warehouse = smriti.db.get(
            "Warehouse",
            {"company": company, "is_group": 0},
            "name",
            order_by="creation asc"
        )
    if not warehouse:
        warehouse = smriti.db.get(
            "Warehouse",
            {"company": company},
            "name"
        )
    if warehouse and smriti.db.get("Warehouse", warehouse, "company") == company:
        return warehouse
    return None

def check_store_manager_role():
    """
    Enforces that only SMRITI Store Manager or System Manager can perform submissions.
    """
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(_("Access Denied: Cashiers can only view. Only Store Managers or System Managers can submit inventory transactions."))

def get_or_create_batch(item_code, expiry_date=None):
    """
    Finds or creates a batch for an item, optionally with an expiry date.
    """
    if expiry_date:
        existing = smriti.db.get("Batch", {"item": item_code, "expiry_date": expiry_date, "disabled": 0}, "name")
        if existing:
            return existing
        
        batch_doc = smriti.documents.new("Batch")
        batch_doc.item = item_code
        batch_doc.expiry_date = expiry_date
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name
    else:
        # Check if any active batch exists
        existing = smriti.db.get("Batch", {"item": item_code, "disabled": 0}, "name", order_by="creation desc")
        if existing:
            return existing
        
        batch_doc = smriti.documents.new("Batch")
        batch_doc.item = item_code
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name

def get_active_batch_for_transfer(item_code, warehouse):
    """
    Locates the oldest batch with positive inventory in the given warehouse,
    or falls back to any active batch for this item.
    """
    batch = smriti.db.sql("""
        SELECT batch_no FROM `tabStock Ledger Entry` 
        WHERE item_code=%s AND warehouse=%s AND batch_no IS NOT NULL AND batch_no != ''
        GROUP BY batch_no HAVING SUM(actual_qty) > 0 
        LIMIT 1
    """, (item_code, warehouse))
    
    if batch:
        return batch[0][0]
    
    return get_or_create_batch(item_code)


@frappe.whitelist()
def scan_item_for_inventory(barcode, warehouse=None):
    """
    Barcode scanner search for inventory screens.
    Returns details including current warehouse stock.
    """
    if not barcode:
        return None

    candidates = get_barcode_candidates(barcode)
    
    item_code = None
    for cand in candidates:
        item_code = smriti.db.get("Item Barcode", {"barcode": cand}, "parent")
        if item_code:
            break
            
    if not item_code:
        for cand in candidates:
            if smriti.db.exists("Item", cand):
                item_code = cand
                break

    if not item_code:
        return None

    item_doc = smriti.documents.get("Item", item_code)
    
    # Resolve warehouse
    if not warehouse:
        company = frappe.defaults.get_user_default("company") or smriti.db.get_single("Global Defaults", "default_company") or (smriti.db.get_list("Company", limit=1)[0].name if smriti.db.get_list("Company", limit=1) else None)
        warehouse = _get_default_warehouse(company)
        
    # Get bin stock
    stock_res = smriti.db.sql(
        "SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse=%s",
        (item_code, warehouse)
    )
    stock_qty = stock_res[0][0] if stock_res and stock_res[0][0] is not None else 0.0

    return {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name,
        "stock_uom": item_doc.stock_uom,
        "brand": item_doc.brand,
        "available_qty": flt(stock_qty),
        "has_batch_no": cint(item_doc.has_batch_no),
        "rate": flt(item_doc.valuation_rate or 0.0)
    }


@frappe.whitelist()
def create_grn(supplier, invoice_no, items, warehouse=None):
    """
    Creates and submits a standard Purchase Receipt (GRN) in ERPNext.
    Cashiers are blocked from submitting.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create GRN with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or smriti.db.get_single("Global Defaults", "default_company") or (smriti.db.get_list("Company", limit=1)[0].name if smriti.db.get_list("Company", limit=1) else None)
    warehouse = warehouse or _get_default_warehouse(company)

    pr = smriti.documents.new("Purchase Receipt")
    pr.supplier = supplier
    pr.bill_no = invoice_no
    pr.posting_date = nowdate()
    pr.company = company

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse") or warehouse

        # Handle batch & expiry tracking
        batch_no = None
        has_batch_no = smriti.db.get("Item", item_code, "has_batch_no")
        if has_batch_no:
            expiry_date = it.get("expiry_date")
            batch_no = get_or_create_batch(item_code, expiry_date)

        pr.append("items", {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "batch_no": batch_no,
            "uom": it.get("stock_uom") or smriti.db.get("Item", item_code, "stock_uom")
        })

    try:
        # reviewed-ignore-permissions: stock receipt validation, gated by SMRITI Store Manager or System Manager roles
        pr.insert(ignore_permissions=True)
        pr.submit()  # Triggers before_submit, on_submit, Stock Ledger, GL Entries
        smriti.db.commit()
    except Exception:
        smriti.db.rollback()
        smriti.errors.log_error(title="SMRITI GRN Submit Failed", message=frappe.get_traceback())
        raise

    return {
        "name": pr.name,
        "message": _("Goods Receipt Note {0} submitted successfully.").format(pr.name)
    }


@frappe.whitelist()
def create_stock_transfer(from_warehouse, to_warehouse, items):
    """
    Creates and submits a standard Material Transfer Stock Entry in ERPNext.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create stock transfer with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or smriti.db.get_list("Company", limit=1)[0].name

    se = smriti.documents.new("Stock Entry")
    se.purpose = "Material Transfer"
    se.stock_entry_type = "Material Transfer"
    se.company = company
    se.posting_date = nowdate()

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        uom = it.get("stock_uom") or smriti.db.get("Item", item_code, "stock_uom")

        # Resolve batch if needed
        batch_no = None
        has_batch_no = smriti.db.get("Item", item_code, "has_batch_no")
        if has_batch_no:
            batch_no = get_active_batch_for_transfer(item_code, from_warehouse)

        se.append("items", {
            "item_code": item_code,
            "qty": qty,
            "s_warehouse": from_warehouse,
            "t_warehouse": to_warehouse,
            "uom": uom,
            "batch_no": batch_no,
            "allow_zero_valuation_rate": 1
        })

    try:
        # reviewed-ignore-permissions: stock transfer validation, gated by SMRITI Store Manager or System Manager roles
        se.insert(ignore_permissions=True)
        se.submit()  # Triggers Stock Ledger + GL Entries for the transfer
        smriti.db.commit()
    except Exception:
        smriti.db.rollback()
        smriti.errors.log_error(title="SMRITI Stock Transfer Submit Failed", message=frappe.get_traceback())
        raise

    return {
        "name": se.name,
        "message": _("Stock Transfer {0} submitted successfully.").format(se.name)
    }


@frappe.whitelist()
def create_stock_adjustment(items, reason):
    """
    Creates and submits a Stock Entry of type Material Issue or Material Receipt.
    Maps standard reasons to the company expense account.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create stock adjustment with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or smriti.db.get_list("Company", limit=1)[0].name

    # Determine purpose
    if reason == "Stock Surplus":
        purpose = "Material Receipt"
    else:
        purpose = "Material Issue"

    # Map account
    account = (
        smriti.db.get("Company", company, "default_inventory_account")
        or smriti.db.get("Company", company, "stock_adjustment_account")
        or smriti.db.get("Account", {"account_name": "Stock Adjustment", "company": company}, "name")
        or smriti.db.get("Account", {"account_name": "Cost of Goods Sold", "company": company}, "name")
        or smriti.db.get("Account", {"account_type": "Stock Adjustment", "company": company}, "name")
        or smriti.db.get("Account", {"account_type": "Expense", "company": company}, "name")
        or smriti.db.get("Account", {"account_type": "Expense Account", "company": company}, "name")
        or smriti.db.get("Account", {"root_type": "Expense", "company": company, "is_group": 0}, "name")
        or smriti.db.get("Account", {"company": company, "is_group": 0}, "name")
    )

    se = smriti.documents.new("Stock Entry")
    se.purpose = purpose
    se.stock_entry_type = purpose
    se.company = company
    se.posting_date = nowdate()

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        wh = it.get("warehouse")
        uom = it.get("stock_uom") or smriti.db.get("Item", item_code, "stock_uom")

        row = {
            "item_code": item_code,
            "qty": qty,
            "uom": uom,
            "expense_account": account,
            "allow_zero_valuation_rate": 1
        }

        if purpose == "Material Issue":
            row["s_warehouse"] = wh
        else:
            row["t_warehouse"] = wh

        # Resolve batch if needed
        has_batch_no = smriti.db.get("Item", item_code, "has_batch_no")
        if has_batch_no:
            if purpose == "Material Issue":
                row["batch_no"] = get_active_batch_for_transfer(item_code, wh)
            else:
                row["batch_no"] = get_or_create_batch(item_code)

        se.append("items", row)

    try:
        # reviewed-ignore-permissions: inventory adjustment, gated by SMRITI Store Manager or System Manager roles
        se.insert(ignore_permissions=True)
        se.submit()  # Triggers Stock Ledger + GL Entries for the adjustment
        smriti.db.commit()
    except Exception:
        smriti.db.rollback()
        smriti.errors.log_error(title="SMRITI Stock Adjustment Submit Failed", message=frappe.get_traceback())
        raise

    return {
        "name": se.name,
        "message": _("Stock Adjustment ({0}) {1} submitted successfully.").format(purpose, se.name)
    }


@frappe.whitelist()
def create_stock_audit(items):
    """
    Creates and submits a Stock Reconciliation to align system stock with physical inventory count.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create stock reconciliation with an empty audit list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or smriti.db.get_list("Company", limit=1)[0].name
    # Resolve asset/liability difference account for opening entries (strictly must be Asset or Liability root type)
    difference_account = (
        smriti.db.get("Account", {"account_type": "Temporary", "company": company, "root_type": ["in", ["Asset", "Liability"]]}, "name")
        or smriti.db.get("Account", {"account_name": "Temporary Opening", "company": company, "root_type": ["in", ["Asset", "Liability"]]}, "name")
        or smriti.db.get("Account", {"root_type": "Asset", "company": company, "is_group": 0}, "name")
        or smriti.db.get("Account", {"root_type": "Liability", "company": company, "is_group": 0}, "name")
    )

    sr = smriti.documents.new("Stock Reconciliation")
    sr.purpose = "Stock Reconciliation"
    sr.company = company
    sr.posting_date = nowdate()
    sr.expense_account = difference_account

    for it in items_list:
        item_code = it.get("item_code")
        wh = it.get("warehouse")
        qty = flt(it.get("qty"))
        
        val_rate = smriti.db.get("Item", item_code, "valuation_rate") or 1.0

        sr.append("items", {
            "item_code": item_code,
            "warehouse": wh,
            "qty": qty,
            "valuation_rate": val_rate
        })

    try:
        # reviewed-ignore-permissions: physical inventory reconciliation audit, gated by SMRITI Store Manager or System Manager roles
        sr.insert(ignore_permissions=True)
        sr.submit()  # Triggers Stock Ledger + GL Entries for the reconciliation
        smriti.db.commit()
    except Exception:
        smriti.db.rollback()
        smriti.errors.log_error(title="SMRITI Stock Audit Submit Failed", message=frappe.get_traceback())
        raise

    return {
        "name": sr.name,
        "message": _("Stock Reconciliation {0} submitted successfully.").format(sr.name)
    }


@frappe.whitelist()
def get_stock_summary(warehouse=None):
    """
    Returns item-wise stock. Filters by warehouse if provided.
    """
    filters = {}
    if warehouse:
        filters["warehouse"] = warehouse

    bins = smriti.db.get_list(
        "Bin",
        filters=filters,
        fields=["item_code", "warehouse", "actual_qty"]
    )

    results = []
    for b in bins:
        if flt(b.actual_qty) != 0.0:
            item_details = smriti.db.get("Item", b.item_code, ["item_name", "stock_uom", "brand"], as_dict=1)
            if item_details:
                results.append({
                    "item_code": b.item_code,
                    "item_name": item_details.item_name,
                    "stock_uom": item_details.stock_uom,
                    "brand": item_details.brand,
                    "warehouse": b.warehouse,
                    "actual_qty": flt(b.actual_qty)
                })
    return results


@frappe.whitelist()
def reset_db(confirmation_token=None):
    """
    Resets all SMRITI Retail OS transaction tables and balance ledgers to zero,
    allowing naming series to restart from 1. Bypasses constraint checks for speed.

    DANGER: This is a destructive, irreversible operation.
    Requires Administrator role AND a matching confirmation_token for safety.
    """
    # Restrict to Administrator only — System Manager is NOT enough for destructive wipe
    if frappe.session.user != "Administrator":
        frappe.throw(
            _("Access Denied: Only the Administrator account can reset transactions."),
            frappe.PermissionError
        )

    # Require an explicit confirmation nonce to prevent accidental / scripted calls
    EXPECTED_TOKEN = "SMRITI_CONFIRM_RESET"
    if confirmation_token != EXPECTED_TOKEN:
        frappe.throw(
            _("Safety check failed. Pass confirmation_token='SMRITI_CONFIRM_RESET' to proceed."),
            frappe.ValidationError
        )

    frappe.logger().warning(
        f"[SMRITI] reset_db() initiated by {frappe.session.user} — truncating transaction tables."
    )

    smriti.db.sql("SET FOREIGN_KEY_CHECKS = 0;")

    tables = [
        "tabStock Reconciliation",
        "tabStock Reconciliation Item",
        "tabStock Entry",
        "tabStock Entry Detail",
        "tabPurchase Receipt",
        "tabPurchase Receipt Item",
        "tabPurchase Invoice",
        "tabPurchase Invoice Item",
        "tabPurchase Order",
        "tabPurchase Order Item",
        "tabSales Invoice",
        "tabSales Invoice Item",
        "tabPOS Invoice",
        "tabPOS Invoice Item",
        "tabPayment Entry",
        "tabPayment Entry Reference",
        "tabPayment Entry Deduction",
        "tabGL Entry",
        "tabStock Ledger Entry",
        "tabPayment Ledger Entry",
        "tabBin",
        "tabSeries"
    ]

    failed_tables = []
    for t in tables:
        if t not in _RESET_DB_SAFE_TABLES:
            smriti.errors.log_error(title="SMRITI: Rejected unexpected TRUNCATE", message=f"Refused to truncate unlisted table: {t}")
            failed_tables.append(t)
            continue
        try:
            smriti.db.sql(f"TRUNCATE TABLE `{t}`")
        except Exception:
            failed_tables.append(t)
            smriti.errors.log_error(
                title=f"SMRITI reset_db: Failed to truncate {t}",
                message=frappe.get_traceback()
            )

    smriti.db.sql("SET FOREIGN_KEY_CHECKS = 1;")
    smriti.db.commit()

    msg = "All transactions reset to zero successfully. Starting from 1."
    if failed_tables:
        msg = f"Reset completed with {len(failed_tables)} table failure(s): {', '.join(failed_tables)}. Check error logs."

    frappe.logger().warning(
        f"[SMRITI] reset_db() completed. Failed tables: {failed_tables or 'None'}."
    )
    return {"status": "success" if not failed_tables else "partial", "message": msg}

