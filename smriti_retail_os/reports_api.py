# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/reports_api.py
# @description: Backend API for SMRITI Reports and Analytics module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

"""
SMRITI Retail OS — Reports API (Phase 6)
All data sourced from existing ERPNext DocTypes.
No custom DocTypes. No duplicate logic.
"""

import frappe
from frappe import _
from frappe.utils import (
    getdate, nowdate, add_days, add_months,
    flt, fmt_money, get_first_day, get_last_day, cint
)
import hashlib
import json
import time


# ─────────────────────────────────────────────
# SALES REPORT
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_sales_report(from_date=None, to_date=None, granularity="daily"):
    """
    Sales summary from POS Invoice (submitted only).
    Returns totals + breakdown by date or hour.
    Uses SQL aggregates (SUM, COUNT, GROUP BY) throughout — zero in-memory
    invoice loading, constant memory regardless of date range width.
    """
    if not from_date:
        from_date = nowdate()
    if not to_date:
        to_date = nowdate()

    # ── Summary totals via single SQL aggregate query ──────────────────────────────
    totals_rows = frappe.db.sql("""
        SELECT
            COUNT(*) AS total_bills,
            COALESCE(SUM(grand_total), 0) AS total_sales,
            COALESCE(SUM(net_total), 0) AS total_net,
            COALESCE(SUM(total_taxes_and_charges), 0) AS total_tax,
            COALESCE(SUM(COALESCE(discount_amount, 0)), 0) AS total_discount
        FROM `tabPOS Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    totals = totals_rows[0] if totals_rows else {}
    total_bills   = int(totals.get("total_bills") or 0)
    total_sales   = flt(totals.get("total_sales") or 0, 2)
    total_net     = flt(totals.get("total_net") or 0, 2)
    total_tax     = flt(totals.get("total_tax") or 0, 2)
    total_discount = flt(totals.get("total_discount") or 0, 2)
    avg_bill      = flt(total_sales / total_bills, 2) if total_bills else 0

    # Payment method breakdown
    payment_totals = _get_payment_breakdown(from_date, to_date)

    # Top items sold
    top_items = _get_top_items(from_date, to_date)

    # Cashier-wise summary
    cashier_summary = _get_cashier_summary(from_date, to_date)

    # Date-wise or hour-wise breakdown via SQL GROUP BY
    if granularity == "hourly" and from_date == to_date:
        breakdown = _get_hourly_breakdown_sql(from_date)
    else:
        breakdown = _get_daily_breakdown_sql(from_date, to_date)

    return {
        "summary": {
            "total_sales":    total_sales,
            "total_net":      total_net,
            "total_tax":      total_tax,
            "total_discount": total_discount,
            "total_bills":    total_bills,
            "avg_bill":       avg_bill
        },
        "payment_breakdown": payment_totals,
        "top_items":         top_items,
        "cashier_summary":   cashier_summary,
        "breakdown":         breakdown,
        "from_date":         from_date,
        "to_date":           to_date
    }


def _get_payment_breakdown(from_date, to_date):
    """Payment mode totals from POS Payment entries."""
    try:
        rows = frappe.db.sql("""
            SELECT pp.mode_of_payment, SUM(pp.amount) as total
            FROM `tabPOS Invoice` pi
            JOIN `tabSales Invoice Payment` pp ON pp.parent = pi.name
            WHERE pi.docstatus = 1
              AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY pp.mode_of_payment
            ORDER BY total DESC
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
        return rows
    except Exception:
        return []


def _get_top_items(from_date, to_date, limit=10):
    """Top selling items by quantity."""
    try:
        rows = frappe.db.sql("""
            SELECT
                pii.item_code,
                pii.item_name,
                SUM(pii.qty) as total_qty,
                SUM(pii.amount) as total_amount
            FROM `tabPOS Invoice` pi
            JOIN `tabPOS Invoice Item` pii ON pii.parent = pi.name
            WHERE pi.docstatus = 1
              AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY pii.item_code
            ORDER BY total_qty DESC
            LIMIT %(limit)s
        """, {"from_date": from_date, "to_date": to_date, "limit": limit}, as_dict=True)
        return rows
    except Exception:
        return []


def _get_cashier_summary(from_date, to_date):
    """Sales totals per cashier."""
    try:
        rows = frappe.db.sql("""
            SELECT
                owner as cashier,
                COUNT(*) as bills,
                SUM(grand_total) as total_sales
            FROM `tabPOS Invoice`
            WHERE docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY owner
            ORDER BY total_sales DESC
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
        return rows
    except Exception:
        return []


def _get_daily_breakdown_sql(from_date, to_date):
    """Group invoices by date using SQL GROUP BY — zero in-memory invoice loading."""
    try:
        rows = frappe.db.sql("""
            SELECT
                posting_date AS date,
                COUNT(*) AS bills,
                COALESCE(SUM(grand_total), 0) AS sales
            FROM `tabPOS Invoice`
            WHERE docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            GROUP BY posting_date
            ORDER BY posting_date ASC
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
        return [{"date": str(r.date), "bills": int(r.bills), "sales": flt(r.sales, 2)} for r in rows]
    except Exception:
        return []


def _get_hourly_breakdown_sql(date):
    """Group invoices by hour for single-day view using SQL GROUP BY."""
    try:
        rows = frappe.db.sql("""
            SELECT
                LPAD(HOUR(posting_time), 2, '0') AS hour,
                COUNT(*) AS bills,
                COALESCE(SUM(grand_total), 0) AS sales
            FROM `tabPOS Invoice`
            WHERE docstatus = 1
              AND posting_date = %(date)s
            GROUP BY HOUR(posting_time)
            ORDER BY HOUR(posting_time) ASC
        """, {"date": date}, as_dict=True)
        return [{"hour": f"{r.hour}:00", "bills": int(r.bills), "sales": flt(r.sales, 2)} for r in rows]
    except Exception:
        return []


# Legacy in-memory breakdown helpers — kept for backward compatibility with existing tests.
# Prefer the SQL variants above for production use.

def _get_daily_breakdown(invoices):
    """DEPRECATED: Group invoices by date (in-memory). Use _get_daily_breakdown_sql() instead."""
    by_date = {}
    for inv in invoices:
        d = str(inv.posting_date)
        if d not in by_date:
            by_date[d] = {"date": d, "bills": 0, "sales": 0}
        by_date[d]["bills"] += 1
        by_date[d]["sales"] = flt(by_date[d]["sales"] + flt(inv.grand_total), 2)
    return sorted(by_date.values(), key=lambda x: x["date"])


def _get_hourly_breakdown(invoices):
    """DEPRECATED: Group invoices by hour (in-memory). Use _get_hourly_breakdown_sql() instead."""
    by_hour = {}
    for inv in invoices:
        if inv.posting_time:
            hour = str(inv.posting_time).split(":")[0].zfill(2)
        else:
            hour = "00"
        label = f"{hour}:00"
        if label not in by_hour:
            by_hour[label] = {"hour": label, "bills": 0, "sales": 0}
        by_hour[label]["bills"] += 1
        by_hour[label]["sales"] = flt(by_hour[label]["sales"] + flt(inv.grand_total), 2)
    return sorted(by_hour.values(), key=lambda x: x["hour"])


# ─────────────────────────────────────────────
# STOCK REPORT
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_stock_report(warehouse=None, item_group=None, show_zero=0):
    """
    Current stock levels from ERPNext Bin doctype.
    No custom logic — pure ERPNext data.
    """
    filters = {}
    if warehouse:
        filters["warehouse"] = warehouse
    if not int(show_zero):
        filters["actual_qty"] = [">", 0]

    bins = frappe.get_all(
        "Bin",
        filters=filters,
        fields=[
            "item_code", "warehouse",
            "actual_qty", "reserved_qty",
            "ordered_qty", "planned_qty",
            "valuation_rate", "stock_value"
        ],
        order_by="item_code asc"
    )

    # Enrich with item details
    # Get all item codes from bins first
    item_codes = [b.item_code for b in bins]

    # Single bulk fetch — replaces N individual DB calls
    item_map = {}
    if item_codes:
        items = frappe.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=["name", "item_name", "item_group",
                    "custom_mrp", "custom_gst_percentage", "stock_uom"]
        )
        item_map = {i.name: i for i in items}

    result = []
    for b in bins:
        item = item_map.get(b.item_code, {})

        # Filter by item_group if set
        if item_group and item.get("item_group") != item_group:
            continue

        available = flt(b.actual_qty) - flt(b.reserved_qty)
        result.append({
            "item_code":       b.item_code,
            "item_name":       item.get("item_name", b.item_code),
            "item_group":      item.get("item_group", ""),
            "uom":             item.get("stock_uom", "Nos"),
            "mrp":             flt(item.get("custom_mrp", 0), 2),
            "gst_pct":         item.get("custom_gst_percentage", ""),
            "warehouse":       b.warehouse,
            "actual_qty":      flt(b.actual_qty, 2),
            "reserved_qty":    flt(b.reserved_qty, 2),
            "available_qty":   flt(available, 2),
            "valuation_rate":  flt(b.valuation_rate, 2),
            "stock_value":     flt(b.stock_value, 2)
        })

    # Summary
    total_items   = len(result)
    total_value   = sum(r["stock_value"] for r in result)
    low_stock     = [r for r in result if r["available_qty"] <= 5]

    return {
        "items":       result,
        "total_items": total_items,
        "total_value": flt(total_value, 2),
        "low_stock":   low_stock,
        "warehouses":  _get_warehouses()
    }


def _get_warehouses():
    """List of all store warehouses."""
    return frappe.get_all(
        "Warehouse",
        filters={"is_group": 0, "disabled": 0},
        fields=["name", "warehouse_name"],
        order_by="name asc"
    )


# ─────────────────────────────────────────────
# GST REPORT (GSTR-1 style summary)
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_gst_report(from_date=None, to_date=None):
    """
    GST summary from submitted POS Invoices.
    Groups by tax rate slab.
    Uses India Compliance tax data already on invoices.
    """
    if not from_date:
        fm = get_first_day(nowdate())
        from_date = str(fm)
    if not to_date:
        to_date = nowdate()

    # Tax detail rows from POS Invoice taxes table
    try:
        tax_rows = frappe.db.sql("""
            SELECT
                pt.account_head,
                pt.description,
                pt.rate,
                SUM(pt.tax_amount) as tax_amount,
                SUM(pt.base_tax_amount) as base_tax_amount,
                SUM(CASE WHEN pi.is_return = 1 THEN -1 ELSE 1 END) as invoice_count
            FROM `tabPOS Invoice` pi
            JOIN `tabSales Taxes and Charges` pt ON pt.parent = pi.name
            WHERE pi.docstatus = 1
              AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
              AND pt.tax_amount != 0
            GROUP BY pt.account_head, pt.rate
            ORDER BY pt.rate ASC
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
    except Exception:
        tax_rows = []

    # Invoice-level totals
    try:
        inv_summary = frappe.db.sql("""
            SELECT
                SUM(CASE WHEN is_return = 1 THEN -1 ELSE 1 END) as total_invoices,
                SUM(net_total) as taxable_value,
                SUM(total_taxes_and_charges) as total_tax,
                SUM(grand_total) as total_with_tax
            FROM `tabPOS Invoice`
            WHERE docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
        summary = inv_summary[0] if inv_summary else {}
    except Exception:
        summary = {}

    # B2C summary (retail — all walk-in / non-GSTIN customers)
    try:
        b2c = frappe.db.sql("""
            SELECT
                SUM(net_total) as taxable,
                SUM(total_taxes_and_charges) as tax,
                SUM(grand_total) as total,
                SUM(CASE WHEN is_return = 1 THEN -1 ELSE 1 END) as bills
            FROM `tabPOS Invoice`
            WHERE docstatus = 1
              AND posting_date BETWEEN %(from_date)s AND %(to_date)s
              AND (billing_address_gstin IS NULL OR billing_address_gstin = '')
        """, {"from_date": from_date, "to_date": to_date}, as_dict=True)
        b2c_data = b2c[0] if b2c else {}
    except Exception:
        b2c_data = {}

    return {
        "summary":       summary,
        "tax_breakdown": tax_rows,
        "b2c":           b2c_data,
        "from_date":     from_date,
        "to_date":       to_date
    }


# ─────────────────────────────────────────────
# OUTSTANDING REPORT
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_outstanding_report(customer=None, days_overdue=0):
    """
    Customer outstanding from ERPNext Sales Invoice.
    Uses native outstanding_amount field.
    """
    filters = {
        "docstatus": 1,
        "outstanding_amount": [">", 0]
    }
    if customer:
        filters["customer"] = customer

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=[
            "name", "customer", "customer_name",
            "posting_date", "due_date",
            "grand_total", "outstanding_amount",
            "currency"
        ],
        order_by="due_date asc"
    )

    today = getdate(nowdate())
    result = []
    for inv in invoices:
        due = getdate(inv.due_date) if inv.due_date else getdate(inv.posting_date)
        overdue_days = (today - due).days

        if int(days_overdue) > 0 and overdue_days < int(days_overdue):
            continue

        result.append({
            "invoice":          inv.name,
            "customer":         inv.customer,
            "customer_name":    inv.customer_name,
            "posting_date":     str(inv.posting_date),
            "due_date":         str(due),
            "grand_total":      flt(inv.grand_total, 2),
            "outstanding":      flt(inv.outstanding_amount, 2),
            "overdue_days":     overdue_days,
            "status":           "Overdue" if overdue_days > 0 else "Due"
        })

    total_outstanding = sum(r["outstanding"] for r in result)
    overdue_count     = len([r for r in result if r["overdue_days"] > 0])

    # Aging buckets
    aging = {
        "current":    sum(r["outstanding"] for r in result if r["overdue_days"] <= 0),
        "1_30":       sum(r["outstanding"] for r in result if 1 <= r["overdue_days"] <= 30),
        "31_60":      sum(r["outstanding"] for r in result if 31 <= r["overdue_days"] <= 60),
        "61_90":      sum(r["outstanding"] for r in result if 61 <= r["overdue_days"] <= 90),
        "above_90":   sum(r["outstanding"] for r in result if r["overdue_days"] > 90),
    }

    return {
        "invoices":          result,
        "total_outstanding": flt(total_outstanding, 2),
        "total_invoices":    len(result),
        "overdue_count":     overdue_count,
        "aging":             aging
    }


# ─────────────────────────────────────────────
# QUICK STATS — for smriti-desk dashboard
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_quick_stats():
    """
    Today's key metrics for the SMRITI dashboard.
    Single call — all four KPIs.
    """
    today = nowdate()
    yesterday = add_days(today, -1)
    month_start = str(get_first_day(today))

    # Today's sales
    today_sales = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total,
               COUNT(*) as bills
        FROM `tabPOS Invoice`
        WHERE docstatus = 1 AND posting_date = %(today)s
    """, {"today": today}, as_dict=True)[0]

    # Yesterday's sales (for comparison)
    yesterday_sales = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabPOS Invoice`
        WHERE docstatus = 1 AND posting_date = %(yesterday)s
    """, {"yesterday": yesterday}, as_dict=True)[0]

    # Month sales
    month_sales = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabPOS Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(start)s AND %(today)s
    """, {"start": month_start, "today": today}, as_dict=True)[0]

    # Stock value
    stock_value = frappe.db.sql("""
        SELECT COALESCE(SUM(stock_value), 0) as total
        FROM `tabBin`
        WHERE actual_qty > 0
    """, as_dict=True)[0]

    # Outstanding
    outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND outstanding_amount > 0
    """, as_dict=True)[0]

    today_total = flt(today_sales.get("total", 0), 2)
    yest_total  = flt(yesterday_sales.get("total", 0), 2)
    growth_pct  = flt(
        ((today_total - yest_total) / yest_total * 100) if yest_total else 0, 1
    )

    return {
        "today_sales":    today_total,
        "today_bills":    today_sales.get("bills", 0),
        "yesterday_sales": yest_total,
        "sales_growth":   growth_pct,
        "month_sales":    flt(month_sales.get("total", 0), 2),
        "stock_value":    flt(stock_value.get("total", 0), 2),
        "outstanding":    flt(outstanding.get("total", 0), 2)
    }


def get_credit_note_deadline(invoice_date):
    """
    Calculates the credit note deadline (November 30 of the following financial year)
    for a given invoice date.
    India FY: April 1 to March 31.
    """
    dt = getdate(invoice_date)
    if dt.month >= 4:
        deadline_year = dt.year + 1
    else:
        deadline_year = dt.year
    return f"{deadline_year}-11-30"


@frappe.whitelist()
def get_sales_return_register(from_date=None, to_date=None):
    """
    Returns Sales Returns (Credit Notes) in bill-by-bill format.
    Filters: Sales Invoices and POS Invoices where is_return = 1 and docstatus = 1.
    """
    if not from_date:
        from_date = str(get_first_day(nowdate()))
    if not to_date:
        to_date = nowdate()

    notes = []
    for doctype in ["Sales Invoice", "POS Invoice"]:
        try:
            invs = frappe.db.get_all(
                doctype,
                filters={
                    "docstatus": 1,
                    "posting_date": ["between", [from_date, to_date]],
                    "is_return": 1
                },
                fields=[
                    "name", "posting_date", "customer", "customer_name",
                    "return_against", "net_total", "total_taxes_and_charges", "grand_total"
                ]
            )
            for inv in invs:
                inv["doc_type"] = doctype
                notes.append(inv)
        except Exception as e:
            frappe.log_error(f"Error in get_sales_return_register for {doctype}", str(e))

    result = []
    for note in notes:
        cgst = 0.0
        sgst = 0.0
        igst = 0.0
        
        taxes = frappe.db.get_all(
            "Sales Taxes and Charges",
            filters={"parent": note.name},
            fields=["account_head", "tax_amount"]
        )
        
        for t in taxes:
            head = (t.account_head or "").upper()
            amt = flt(t.tax_amount)
            if amt > 0:
                amt = -amt
            
            if "CGST" in head:
                cgst += amt
            elif "SGST" in head:
                sgst += amt
            elif "IGST" in head:
                igst += amt

        taxable = flt(note.net_total)
        total_tax = flt(note.total_taxes_and_charges)
        grand = flt(note.grand_total)
        if taxable > 0:
            taxable = -taxable
            total_tax = -total_tax
            grand = -grand

        result.append({
            "date": str(note.posting_date),
            "return_no": note.name,
            "orig_invoice": note.return_against or "",
            "customer_name": note.customer_name or note.customer,
            "taxable_value": taxable,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_tax": total_tax,
            "grand_total": grand
        })

    return result


@frappe.whitelist()
def get_purchase_return_register(from_date=None, to_date=None):
    """
    Returns Purchase Returns (Debit Notes) in bill-by-bill format.
    Filters: Purchase Invoices where is_return = 1 and docstatus = 1.
    """
    if not from_date:
        from_date = str(get_first_day(nowdate()))
    if not to_date:
        to_date = nowdate()

    try:
        invs = frappe.db.get_all(
            "Purchase Invoice",
            filters={
                "docstatus": 1,
                "posting_date": ["between", [from_date, to_date]],
                "is_return": 1
            },
            fields=[
                "name", "posting_date", "supplier", "supplier_name",
                "return_against", "net_total", "total_taxes_and_charges", "grand_total"
            ]
        )
    except Exception as e:
        frappe.log_error("Error in get_purchase_return_register", str(e))
        return []

    result = []
    for inv in invs:
        cgst = 0.0
        sgst = 0.0
        igst = 0.0
        
        taxes = frappe.db.get_all(
            "Purchase Taxes and Charges",
            filters={"parent": inv.name},
            fields=["account_head", "tax_amount"]
        )
        
        for t in taxes:
            head = (t.account_head or "").upper()
            amt = flt(t.tax_amount)
            if amt > 0:
                amt = -amt
            
            if "CGST" in head:
                cgst += amt
            elif "SGST" in head:
                sgst += amt
            elif "IGST" in head:
                igst += amt

        taxable = flt(inv.net_total)
        total_tax = flt(inv.total_taxes_and_charges)
        grand = flt(inv.grand_total)
        if taxable > 0:
            taxable = -taxable
            total_tax = -total_tax
            grand = -grand

        result.append({
            "date": str(inv.posting_date),
            "return_no": inv.name,
            "orig_invoice": inv.return_against or "",
            "supplier_name": inv.supplier_name or inv.supplier,
            "taxable_value": taxable,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_tax": total_tax,
            "grand_total": grand
        })

    return result


@frappe.whitelist()
def get_gstr1_9b_report(from_date=None, to_date=None):
    """
    Returns Credit/Debit Notes issued to customers split into B2B and B2C tables.
    """
    if not from_date:
        from_date = str(get_first_day(nowdate()))
    if not to_date:
        to_date = nowdate()

    b2b_list = []
    b2c_list = []
    
    notes = []
    for doctype in ["Sales Invoice", "POS Invoice"]:
        try:
            invs = frappe.db.get_all(
                doctype,
                filters={
                    "docstatus": 1,
                    "posting_date": ["between", [from_date, to_date]],
                    "is_return": 1
                },
                fields=[
                    "name", "posting_date", "customer", "customer_name",
                    "billing_address_gstin", "place_of_supply", "return_against",
                    "net_total", "total_taxes_and_charges", "grand_total"
                ]
            )
            for inv in invs:
                inv["doc_type"] = doctype
                inv["note_type"] = "C"
                notes.append(inv)
        except Exception as e:
            frappe.log_error(f"Error fetching GSTR-1 9B for {doctype}", str(e))

        if doctype == "Sales Invoice":
            try:
                deb_notes = frappe.db.get_all(
                    doctype,
                    filters={
                        "docstatus": 1,
                        "posting_date": ["between", [from_date, to_date]],
                        "is_debit_note": 1
                    },
                    fields=[
                        "name", "posting_date", "customer", "customer_name",
                        "billing_address_gstin", "place_of_supply",
                        "net_total", "total_taxes_and_charges", "grand_total"
                    ]
                )
                for inv in deb_notes:
                    inv["doc_type"] = doctype
                    inv["note_type"] = "D"
                    inv["return_against"] = ""
                    notes.append(inv)
            except Exception as e:
                frappe.log_error("Error fetching Debit Notes for GSTR-1 9B", str(e))

    for note in notes:
        orig_date = ""
        if note.get("return_against"):
            orig_doctype = "Sales Invoice" if note.doc_type == "Sales Invoice" else "POS Invoice"
            orig_date = frappe.db.get_value(orig_doctype, note.return_against, "posting_date") or ""
        
        cgst = 0.0
        sgst = 0.0
        igst = 0.0
        
        taxes = frappe.db.get_all(
            "Sales Taxes and Charges",
            filters={"parent": note.name},
            fields=["account_head", "tax_amount"]
        )
        
        for t in taxes:
            head = (t.account_head or "").upper()
            amt = flt(t.tax_amount)
            if note.note_type == "C" and amt > 0:
                amt = -amt
            
            if "CGST" in head:
                cgst += amt
            elif "SGST" in head:
                sgst += amt
            elif "IGST" in head:
                igst += amt

        taxable = flt(note.net_total)
        total_tax = flt(note.total_taxes_and_charges)
        grand = flt(note.grand_total)
        if note.note_type == "C" and taxable > 0:
            taxable = -taxable
            total_tax = -total_tax
            grand = -grand

        record = {
            "gstin": note.get("billing_address_gstin") or "",
            "customer_name": note.get("customer_name") or note.get("customer"),
            "note_no": note.name,
            "note_date": str(note.posting_date),
            "note_type": note.note_type,
            "pos": note.get("place_of_supply") or "",
            "orig_invoice": note.get("return_against") or "",
            "orig_date": str(orig_date) if orig_date else "",
            "taxable_value": taxable,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "total_tax": total_tax,
            "grand_total": grand
        }
        
        if record["gstin"]:
            b2b_list.append(record)
        else:
            b2c_list.append(record)

    return {
        "b2b": b2b_list,
        "b2c": b2c_list
    }


@frappe.whitelist()
def get_deadline_alerts():
    """
    Returns returns (Credit/Debit Notes) and original invoices that are approaching
    the November 30 tax adjustment deadline.
    """
    from frappe.utils import getdate, date_diff, nowdate
    current_date = getdate(nowdate())
    alerts = []
    
    doctypes = {
        "Sales Invoice": "Customer",
        "POS Invoice": "Customer",
        "Purchase Invoice": "Supplier"
    }
    
    for doctype, party_field in doctypes.items():
        try:
            fields = ["name", "posting_date", "return_against", "grand_total"]
            if doctype == "Purchase Invoice":
                fields.append("supplier as party")
                fields.append("supplier_name as party_name")
            else:
                fields.append("customer as party")
                fields.append("customer_name as party_name")
                
            invs = frappe.db.get_all(
                doctype,
                filters={"docstatus": 1, "is_return": 1},
                fields=fields
            )
            
            for inv in invs:
                orig_date = None
                if inv.return_against:
                    orig_doctype = "Purchase Invoice" if doctype == "Purchase Invoice" else ("POS Invoice" if doctype == "POS Invoice" else "Sales Invoice")
                    orig_date = frappe.db.get_value(orig_doctype, inv.return_against, "posting_date")
                
                ref_date = orig_date or inv.posting_date
                if not ref_date:
                    continue
                    
                deadline = get_credit_note_deadline(ref_date)
                deadline_dt = getdate(deadline)
                days_left = date_diff(deadline_dt, current_date)
                
                if days_left <= 180:
                    if days_left <= 30:
                        status = "Red"
                    elif days_left <= 90:
                        status = "Amber"
                    else:
                        status = "Green"
                        
                    alerts.append({
                        "doctype": doctype,
                        "name": inv.name,
                        "party": inv.party_name or inv.party,
                        "party_type": party_field,
                        "orig_invoice": inv.return_against or "Direct Return",
                        "orig_date": str(ref_date),
                        "deadline": deadline,
                        "days_left": days_left,
                        "status": status,
                        "grand_total": flt(inv.grand_total)
                    })
        except Exception as e:
            frappe.log_error(f"Error in get_deadline_alerts for {doctype}", str(e))
            
    status_order = {"Red": 0, "Amber": 1, "Green": 2}
    alerts.sort(key=lambda x: (status_order.get(x["status"], 3), x["days_left"]))
    return alerts


# ─────────────────────────────────────────────
# SMRITI REPORT ENGINE (Phase 1)
# ─────────────────────────────────────────────

REPORT_QUERIES = {
    "item_wise_sales": {
        "base_sql": """
            SELECT 
                items.item_code,
                items.item_name,
                items.item_group,
                items.brand,
                SUM(items.qty) as qty_sold,
                SUM(items.net_amount) as taxable_amount,
                SUM(items.amount) as gross_amount
            FROM `tabPOS Invoice Item` items
            INNER JOIN `tabPOS Invoice` parent ON items.parent = parent.name
            LEFT JOIN `tabItem` item ON items.item_code = item.name
            WHERE parent.docstatus = 1 AND parent.is_return = 0
        """,
        "group_by": "items.item_code",
        "order_by": "qty_sold DESC"
    },
    "daily_sales_summary": {
        "base_sql": """
            SELECT 
                parent.posting_date,
                COUNT(parent.name) as bills_count,
                SUM(parent.total_qty) as qty_sold,
                SUM(parent.net_total) as taxable_amount,
                SUM(parent.total_taxes_and_charges) as tax_amount,
                SUM(parent.discount_amount) as discount_amount,
                SUM(parent.grand_total) as grand_total
            FROM `tabPOS Invoice` parent
            WHERE parent.docstatus = 1
        """,
        "group_by": "parent.posting_date",
        "order_by": "parent.posting_date ASC"
    },
    "cash_z_report": {
        "is_custom": True
    },
    "cash_reconciliation": {
        "base_sql": """
            SELECT 
                ce.name as closing_id,
                ce.posting_date,
                ce.user as cashier,
                ce.pos_profile,
                cd.mode_of_payment,
                cd.expected_amount,
                cd.closing_amount as declared_amount,
                (cd.closing_amount - cd.expected_amount) as difference
            FROM `tabPOS Closing Entry` ce
            JOIN `tabPOS Closing Entry Detail` cd ON cd.parent = ce.name
            WHERE ce.docstatus = 1
        """,
        "group_by": None,
        "order_by": "ce.posting_date DESC"
    },
    "current_stock_position": {
        "base_sql": """
            SELECT 
                b.item_code,
                i.item_name,
                b.warehouse,
                b.actual_qty,
                b.valuation_rate,
                b.stock_value,
                CASE 
                    WHEN b.actual_qty <= 0 THEN 'Out of Stock'
                    WHEN b.actual_qty <= 5 THEN 'Low Stock'
                    ELSE 'In Stock'
                END as status
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            WHERE 1=1
        """,
        "group_by": None,
        "order_by": "b.item_code ASC"
    },
    "style_wise_stock": {
        "base_sql": """
            SELECT 
                COALESCE(i.custom_style_code, i.variant_of, i.name) as style_code,
                COALESCE(parent_item.item_name, i.item_name) as style_name,
                SUM(b.actual_qty) as actual_qty,
                SUM(b.stock_value) as stock_value
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabItem` parent_item ON i.variant_of = parent_item.name
            WHERE 1=1
        """,
        "group_by": "style_code",
        "order_by": "actual_qty DESC"
    },
    "size_wise_stock": {
        "base_sql": """
            SELECT 
                COALESCE(i.custom_style_code, i.variant_of, i.name) as style_code,
                COALESCE(parent_item.item_name, i.item_name) as style_name,
                c_attr.attribute_value as color,
                s_attr.attribute_value as size,
                SUM(b.actual_qty) as actual_qty,
                b.warehouse
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            LEFT JOIN `tabItem` parent_item ON i.variant_of = parent_item.name
            LEFT JOIN `tabItem Variant Attribute` c_attr ON c_attr.parent = i.name AND c_attr.attribute = 'Color'
            LEFT JOIN `tabItem Variant Attribute` s_attr ON s_attr.parent = i.name AND s_attr.attribute = 'Size'
            WHERE 1=1
        """,
        "group_by": "style_code, color, size, b.warehouse",
        "order_by": "style_code ASC"
    },
    "payment_mode_summary": {
        "base_sql": """
            SELECT 
                p.mode_of_payment,
                SUM(p.amount) as total_amount
            FROM `tabSales Invoice Payment` p
            JOIN `tabPOS Invoice` i ON p.parent = i.name
            WHERE i.docstatus = 1
        """,
        "group_by": "p.mode_of_payment",
        "order_by": "total_amount DESC"
    },
    "payment_register": {
        "base_sql": """
            SELECT 
                posting_date,
                name as payment_entry_no,
                party_type,
                party,
                payment_type,
                mode_of_payment,
                paid_amount,
                reference_no,
                remarks
            FROM `tabPayment Entry`
            WHERE docstatus = 1 AND payment_type = 'Pay'
        """,
        "group_by": None,
        "order_by": "posting_date DESC"
    },
    "receipt_register": {
        "base_sql": """
            SELECT 
                pe.posting_date,
                pe.name as receipt_no,
                pe.party as customer,
                ref.reference_name as against_invoice,
                pe.mode_of_payment,
                pe.paid_amount as amount_received,
                pe.reference_no as reference_number
            FROM `tabPayment Entry` pe
            LEFT JOIN `tabPayment Entry Reference` ref ON ref.parent = pe.name
            WHERE pe.docstatus = 1 AND pe.payment_type = 'Receive'
        """,
        "group_by": None,
        "order_by": "pe.posting_date DESC"
    },
    "cash_book": {
        "is_custom": True
    },
    "day_book": {
        "is_custom": True
    },
    "customer_outstanding": {
        "base_sql": """
            SELECT 
                customer,
                name as invoice,
                posting_date,
                due_date,
                outstanding_amount,
                DATEDIFF(CURRENT_DATE(), posting_date) as ageing_days
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND outstanding_amount > 0
        """,
        "group_by": None,
        "order_by": "posting_date ASC"
    },
    "supplier_outstanding": {
        "base_sql": """
            SELECT 
                supplier,
                name as invoice,
                posting_date,
                due_date,
                outstanding_amount,
                DATEDIFF(CURRENT_DATE(), posting_date) as ageing_days
            FROM `tabPurchase Invoice`
            WHERE docstatus = 1 AND outstanding_amount > 0
        """,
        "group_by": None,
        "order_by": "posting_date ASC"
    }
}


class SMRITIReportEngine:
    def __init__(self, report_key, filters=None):
        self.report_key = report_key
        self.filters = filters or {}
        self.template = self._load_template()

    def _load_template(self):
        """Loads SMRITI Report Template from DB."""
        if frappe.db.exists("SMRITI Report Template", self.report_key):
            return frappe.get_doc("SMRITI Report Template", self.report_key)
        else:
            frappe.throw(_("Report Template '{0}' not found").format(self.report_key))

    def check_permissions(self):
        """Checks if current user has role permission to run this report."""
        user = frappe.session.user
        if user == "Administrator" or "System Manager" in frappe.get_roles():
            return True
            
        allowed_roles = [r.role for r in self.template.get("role_access", [])]
        if not allowed_roles:
            return True # If no specific roles are defined, permit access
            
        user_roles = frappe.get_roles()
        if not set(allowed_roles).intersection(set(user_roles)):
            frappe.throw(_("Access Denied for Report '{0}'").format(self.template.report_name), frappe.PermissionError)

    def get_cache_key(self):
        """Generates MD5 hash of filter options for secure caching."""
        filter_hash = hashlib.md5(
            json.dumps(self.filters, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return f"smriti:{self.report_key}:{filter_hash}"

    def run(self):
        self.check_permissions()

        # Check Cache
        cache_minutes = cint(self.template.cache_minutes)
        if cache_minutes > 0:
            cache_key = self.get_cache_key()
            cached_data = frappe.cache().get_value(cache_key)
            if cached_data:
                return json.loads(cached_data)

        # Execute
        start_time = time.time()
        
        query_config = REPORT_QUERIES.get(self.report_key)
        if not query_config:
            frappe.throw(_("Query configuration for report '{0}' not defined").format(self.report_key))

        if query_config.get("is_custom"):
            results = self._run_custom_report()
        else:
            results = self._run_sql_report(query_config)

        duration = time.time() - start_time
        
        # Performance Logging in Activity Log
        try:
            log_doc = frappe.new_doc("Activity Log")
            log_doc.user = frappe.session.user
            log_doc.operation = "SMRITI Report Run"
            log_doc.subject = f"Report {self.report_key} executed in {duration:.4f}s returning {len(results)} rows"
            log_doc.remarks = json.dumps({
                "report_key": self.report_key,
                "filters": self.filters,
                "duration_sec": duration,
                "rows_count": len(results)
            })
            log_doc.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error logging report execution: {str(e)}")

        # Write to Cache
        if cache_minutes > 0:
            cache_key = self.get_cache_key()
            frappe.cache().set_value(cache_key, frappe.as_json(results), expires_in_sec=cache_minutes * 60)

        return results

    def _run_custom_report(self):
        """Custom Python-based reporter for Cash Z-Report, Cash Book, and Day Book."""
        if self.report_key == "cash_z_report":
            return self._run_cash_z_report()
        elif self.report_key == "cash_book":
            return self._run_cash_book()
        elif self.report_key == "day_book":
            return self._run_day_book()
        return []

    def _run_cash_book(self):
        from frappe.utils import flt, nowdate
        company = self.filters.get("company")
        if not company:
            company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
            
        from_date = self.filters.get("from_date") or nowdate()
        to_date = self.filters.get("to_date") or nowdate()
        
        # 1. Resolve Cash Accounts
        cash_accounts = frappe.get_all("Account", filters={"company": company, "account_type": "Cash"}, pluck="name")
        if not cash_accounts:
            cash_accounts = frappe.get_all("Account", filters={"company": company, "name": ["like", "%Cash%"]}, pluck="name")
            
        if not cash_accounts:
            return []
            
        # 2. Get opening balance before from_date
        gl_sum = frappe.db.sql("""
            SELECT SUM(debit) as debit, SUM(credit) as credit
            FROM `tabGL Entry`
            WHERE company = %s AND account IN %s AND posting_date < %s AND is_cancelled = 0
        """, (company, cash_accounts, from_date), as_dict=True)
        
        opening_bal = 0.0
        if gl_sum:
            opening_bal = flt(gl_sum[0].get("debit") or 0.0) - flt(gl_sum[0].get("credit") or 0.0)
            
        # 3. Get transactions grouped by date
        entries = frappe.db.sql("""
            SELECT 
                posting_date,
                SUM(debit) as receipts,
                SUM(credit) as payments
            FROM `tabGL Entry`
            WHERE company = %s AND account IN %s AND posting_date BETWEEN %s AND %s AND is_cancelled = 0
            GROUP BY posting_date
            ORDER BY posting_date ASC
        """, (company, cash_accounts, from_date, to_date), as_dict=True)
        
        results = []
        current_bal = opening_bal
        for entry in entries:
            receipts = flt(entry.receipts)
            payments = flt(entry.payments)
            opening = current_bal
            closing = opening + receipts - payments
            
            results.append({
                "date": str(entry.posting_date),
                "opening_balance": opening,
                "cash_receipts": receipts,
                "cash_payments": payments,
                "closing_balance": closing
            })
            current_bal = closing
            
        return results

    def _run_day_book(self):
        from frappe.utils import flt, nowdate, getdate
        from dateutil.rrule import rrule, DAILY
        
        company = self.filters.get("company")
        if not company:
            company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
            
        from_date = self.filters.get("from_date") or nowdate()
        to_date = self.filters.get("to_date") or nowdate()
        
        start = getdate(from_date)
        end = getdate(to_date)
        dates = [d.date() for d in rrule(DAILY, dtstart=start, until=end)]
        
        # Maps for quick indexing
        sales_map = {}
        sales_return_map = {}
        purchase_map = {}
        purchase_return_map = {}
        receipt_map = {}
        payment_map = {}
        
        # 1. Sales (excluding returns)
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(grand_total) as total 
            FROM `tabSales Invoice` 
            WHERE company = %s AND docstatus = 1 AND is_return = 0 AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            sales_map[str(r.posting_date)] = flt(r.total)
            
        if frappe.db.exists("DocType", "POS Invoice"):
            for r in frappe.db.sql("""
                SELECT posting_date, SUM(grand_total) as total 
                FROM `tabPOS Invoice` 
                WHERE company = %s AND docstatus = 1 AND is_return = 0 AND posting_date BETWEEN %s AND %s 
                GROUP BY posting_date
            """, (company, from_date, to_date), as_dict=True):
                sales_map[str(r.posting_date)] = sales_map.get(str(r.posting_date), 0.0) + flt(r.total)
                
        # 2. Sales Returns
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(grand_total) as total 
            FROM `tabSales Invoice` 
            WHERE company = %s AND docstatus = 1 AND is_return = 1 AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            sales_return_map[str(r.posting_date)] = flt(r.total)
            
        if frappe.db.exists("DocType", "POS Invoice"):
            for r in frappe.db.sql("""
                SELECT posting_date, SUM(grand_total) as total 
                FROM `tabPOS Invoice` 
                WHERE company = %s AND docstatus = 1 AND is_return = 1 AND posting_date BETWEEN %s AND %s 
                GROUP BY posting_date
            """, (company, from_date, to_date), as_dict=True):
                sales_return_map[str(r.posting_date)] = sales_return_map.get(str(r.posting_date), 0.0) + flt(r.total)
                
        # 3. Purchases (excluding returns)
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(grand_total) as total 
            FROM `tabPurchase Invoice` 
            WHERE company = %s AND docstatus = 1 AND is_return = 0 AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            purchase_map[str(r.posting_date)] = flt(r.total)
            
        # 4. Purchase Returns
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(grand_total) as total 
            FROM `tabPurchase Invoice` 
            WHERE company = %s AND docstatus = 1 AND is_return = 1 AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            purchase_return_map[str(r.posting_date)] = flt(r.total)
            
        # 5. Receipts
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(paid_amount) as total 
            FROM `tabPayment Entry` 
            WHERE company = %s AND docstatus = 1 AND payment_type = 'Receive' AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            receipt_map[str(r.posting_date)] = flt(r.total)
            
        # 6. Payments
        for r in frappe.db.sql("""
            SELECT posting_date, SUM(paid_amount) as total 
            FROM `tabPayment Entry` 
            WHERE company = %s AND docstatus = 1 AND payment_type = 'Pay' AND posting_date BETWEEN %s AND %s 
            GROUP BY posting_date
        """, (company, from_date, to_date), as_dict=True):
            payment_map[str(r.posting_date)] = flt(r.total)
            
        results = []
        for d in dates:
            ds = str(d)
            sales = sales_map.get(ds, 0.0)
            sales_ret = sales_return_map.get(ds, 0.0)
            purch = purchase_map.get(ds, 0.0)
            purch_ret = purchase_return_map.get(ds, 0.0)
            receipts = receipt_map.get(ds, 0.0)
            payments = payment_map.get(ds, 0.0)
            net_cash = receipts - payments
            
            if sales == 0.0 and sales_ret == 0.0 and purch == 0.0 and purch_ret == 0.0 and receipts == 0.0 and payments == 0.0:
                continue
                
            results.append({
                "date": ds,
                "sales": sales,
                "sales_returns": sales_ret,
                "purchases": purch,
                "purchase_returns": purch_ret,
                "receipts": receipts,
                "payments": payments,
                "net_cash_position": net_cash
            })
            
        return results

    def _run_cash_z_report(self):
        date = self.filters.get("from_date") or self.filters.get("date") or nowdate()
        company = self.filters.get("company")
        warehouse = self.filters.get("warehouse")
        cashier = self.filters.get("cashier")
        
        # 1. Fetch opening entries
        opening_filters = {"posting_date": date, "docstatus": 1}
        if company:
            opening_filters["company"] = company
        if cashier:
            opening_filters["user"] = cashier
            
        opening_entries = frappe.get_all("POS Opening Entry", filters=opening_filters, fields=["name"])
        opening_cash = 0.0
        for oe in opening_entries:
            details = frappe.get_all("POS Opening Entry Detail", filters={"parent": oe.name, "mode_of_payment": "Cash"}, fields=["opening_amount"])
            for d in details:
                opening_cash += flt(d.opening_amount)

        # 2. Build sales and payment aggregates
        sales_where = ["docstatus = 1 AND posting_date = %(date)s"]
        sales_params = {"date": date}
        
        if company:
            sales_where.append("company = %(company)s")
            sales_params["company"] = company
        if cashier:
            sales_where.append("owner = %(cashier)s")
            sales_params["cashier"] = cashier
        if warehouse:
            sales_where.append("(set_warehouse = %(warehouse)s)")
            sales_params["warehouse"] = warehouse
            
        sales_where_str = " AND ".join(sales_where)
        
        # Sales summary
        sales_sum = frappe.db.sql(f"""
            SELECT 
                COUNT(*) as total_bills,
                COALESCE(SUM(grand_total), 0) as total_sales,
                COALESCE(SUM(net_total), 0) as total_net,
                COALESCE(SUM(total_taxes_and_charges), 0) as total_tax,
                COALESCE(SUM(discount_amount), 0) as total_discount
            FROM `tabPOS Invoice`
            WHERE {sales_where_str}
        """, sales_params, as_dict=True)
        
        sales_info = sales_sum[0] if sales_sum else {}
        
        # Payment breakdown
        pay_where = ["pi.docstatus = 1 AND pi.posting_date = %(date)s"]
        if company:
            pay_where.append("pi.company = %(company)s")
        if cashier:
            pay_where.append("pi.owner = %(cashier)s")
        if warehouse:
            pay_where.append("pi.set_warehouse = %(warehouse)s")
        pay_where_str = " AND ".join(pay_where)

        payments = frappe.db.sql(f"""
            SELECT 
                pp.mode_of_payment,
                SUM(pp.amount) as amount
            FROM `tabPOS Invoice` pi
            JOIN `tabSales Invoice Payment` pp ON pp.parent = pi.name
            WHERE {pay_where_str}
            GROUP BY pp.mode_of_payment
        """, sales_params, as_dict=True)
        
        # Refunds/Returns
        refunds_sum = frappe.db.sql(f"""
            SELECT 
                COUNT(*) as total_refund_bills,
                COALESCE(SUM(grand_total), 0) as total_refunds
            FROM `tabPOS Invoice`
            WHERE {sales_where_str} AND is_return = 1
        """, sales_params, as_dict=True)
        
        refund_info = refunds_sum[0] if refunds_sum else {}
        
        # Format payment breakdown
        cash_sales = 0.0
        pay_strings = []
        for p in payments:
            pay_strings.append(f"{p.mode_of_payment}: Rs. {p.amount:.2f}")
            if p.mode_of_payment == "Cash":
                cash_sales = flt(p.amount)
                
        expected_cash = opening_cash + cash_sales - flt(refund_info.get("total_refunds", 0))
        
        results = [{
            "date": date,
            "cashier": cashier or "All Cashiers",
            "opening_cash": opening_cash,
            "total_bills": int(sales_info.get("total_bills") or 0),
            "total_sales": flt(sales_info.get("total_sales") or 0),
            "total_net": flt(sales_info.get("total_net") or 0),
            "total_tax": flt(sales_info.get("total_tax") or 0),
            "total_discount": flt(sales_info.get("total_discount") or 0),
            "total_refunds": flt(refund_info.get("total_refunds") or 0),
            "expected_cash_in_drawer": expected_cash,
            "payment_modes": ", ".join(pay_strings) if pay_strings else "None"
        }]
        return results

    def _run_sql_report(self, config):
        base_sql = config["base_sql"]
        group_by = config.get("group_by")
        order_by = config.get("order_by")

        where_clauses = []
        params = {}

        # Company filter (always applicable if source contains company)
        company = self.filters.get("company")
        if company:
            where_clauses.append("parent.company = %(company)s" if "parent ON" in base_sql else "b.company = %(company)s" if "tabBin" in base_sql else "ce.company = %(company)s" if "tabPOS Closing Entry" in base_sql else "company = %(company)s")
            params["company"] = company
        elif self.template.company_restricted:
            default_company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
            if default_company:
                where_clauses.append("parent.company = %(company)s" if "parent ON" in base_sql else "b.company = %(company)s" if "tabBin" in base_sql else "ce.company = %(company)s" if "tabPOS Closing Entry" in base_sql else "company = %(company)s")
                params["company"] = default_company

        # Warehouse filter
        warehouse = self.filters.get("warehouse")
        if warehouse:
            if "tabBin" in base_sql:
                where_clauses.append("b.warehouse = %(warehouse)s")
            elif "parent ON" in base_sql:
                where_clauses.append("(items.warehouse = %(warehouse)s OR parent.set_warehouse = %(warehouse)s)")
            else:
                where_clauses.append("set_warehouse = %(warehouse)s")
            params["warehouse"] = warehouse

        # Date range filter (not applicable for stock position/ledger)
        if "tabBin" not in base_sql:
            from_date = self.filters.get("from_date")
            to_date = self.filters.get("to_date")
            if from_date and to_date:
                date_field = "pe.posting_date" if "pe." in base_sql else "posting_date" if "tabPayment Entry" in base_sql or "tabSales Invoice" in base_sql or "tabPurchase Invoice" in base_sql else "parent.posting_date" if "parent ON" in base_sql else "ce.posting_date" if "tabPOS Closing Entry" in base_sql else "posting_date" if "tabPOS Invoice" in base_sql else "i.posting_date"
                where_clauses.append(f"{date_field} BETWEEN %(from_date)s AND %(to_date)s")
                params["from_date"] = from_date
                params["to_date"] = to_date

        # Item group & Brand
        item_group = self.filters.get("item_group")
        if item_group:
            field = "items.item_group" if "parent ON" in base_sql else "i.item_group"
            where_clauses.append(f"{field} = %(item_group)s")
            params["item_group"] = item_group

        brand = self.filters.get("brand")
        if brand:
            field = "items.brand" if "parent ON" in base_sql else "i.brand"
            where_clauses.append(f"{field} = %(brand)s")
            params["brand"] = brand

        # Style / Article Code
        style = self.filters.get("style")
        if style:
            if "parent ON" in base_sql:
                where_clauses.append("(item.custom_style_code = %(style)s OR item.variant_of = %(style)s OR items.item_code = %(style)s)")
            else:
                where_clauses.append("(i.custom_style_code = %(style)s OR i.variant_of = %(style)s OR i.name = %(style)s)")
            params["style"] = style

        # Size (via tabItem Variant Attribute child table join)
        size = self.filters.get("size")
        if size:
            if "s_attr" in base_sql:
                # Reports that already JOIN tabItem Variant Attribute with s_attr alias
                where_clauses.append("s_attr.attribute_value = %(size)s")
            elif "parent ON" in base_sql:
                # Reports that use `items` as item table alias (e.g. item_wise_sales, daily_sales_summary)
                where_clauses.append("EXISTS (SELECT 1 FROM `tabItem Variant Attribute` va WHERE va.parent = items.item_code AND va.attribute = 'Size' AND va.attribute_value = %(size)s)")
            else:
                # Reports that use `i` as item table alias (e.g. current_stock_position)
                where_clauses.append("EXISTS (SELECT 1 FROM `tabItem Variant Attribute` va WHERE va.parent = i.name AND va.attribute = 'Size' AND va.attribute_value = %(size)s)")
            params["size"] = size

        # Color (via tabItem Variant Attribute child table join)
        color = self.filters.get("color")
        if color:
            if "c_attr" in base_sql:
                # Reports that already JOIN tabItem Variant Attribute with c_attr alias
                where_clauses.append("c_attr.attribute_value = %(color)s")
            elif "parent ON" in base_sql:
                # Reports that use `items` as item table alias
                where_clauses.append("EXISTS (SELECT 1 FROM `tabItem Variant Attribute` va WHERE va.parent = items.item_code AND va.attribute = 'Color' AND va.attribute_value = %(color)s)")
            else:
                # Reports that use `i` as item table alias
                where_clauses.append("EXISTS (SELECT 1 FROM `tabItem Variant Attribute` va WHERE va.parent = i.name AND va.attribute = 'Color' AND va.attribute_value = %(color)s)")
            params["color"] = color

        # Salesperson filter
        salesperson = self.filters.get("salesperson")
        if salesperson and "parent ON" in base_sql:
            where_clauses.append("EXISTS (SELECT 1 FROM `tabSales Team` st WHERE st.parent = parent.name AND st.sales_person = %(salesperson)s)")
            params["salesperson"] = salesperson

        # Customer filter
        customer = self.filters.get("customer")
        if customer:
            where_clauses.append("customer = %(customer)s")
            params["customer"] = customer

        # Supplier filter
        supplier = self.filters.get("supplier")
        if supplier:
            where_clauses.append("supplier = %(supplier)s")
            params["supplier"] = supplier

        # Party filter
        party = self.filters.get("party")
        if party:
            where_clauses.append("party = %(party)s")
            params["party"] = party

        # Payment Mode filter
        payment_mode = self.filters.get("payment_mode")
        if payment_mode:
            where_clauses.append("mode_of_payment = %(payment_mode)s")
            params["payment_mode"] = payment_mode

        # Ageing Bucket filter
        ageing_bucket = self.filters.get("ageing_bucket")
        if ageing_bucket:
            if ageing_bucket == "1-30":
                where_clauses.append("DATEDIFF(CURRENT_DATE(), posting_date) BETWEEN 1 AND 30")
            elif ageing_bucket == "31-60":
                where_clauses.append("DATEDIFF(CURRENT_DATE(), posting_date) BETWEEN 31 AND 60")
            elif ageing_bucket == "61-90":
                where_clauses.append("DATEDIFF(CURRENT_DATE(), posting_date) BETWEEN 61 AND 90")
            elif ageing_bucket == "90+":
                where_clauses.append("DATEDIFF(CURRENT_DATE(), posting_date) > 90")

        # Combine SQL
        full_sql = base_sql
        if where_clauses:
            connector = " AND " if "WHERE" in base_sql else " WHERE "
            full_sql += connector + " AND ".join(where_clauses)

        if group_by:
            full_sql += f" GROUP BY {group_by}"
        if order_by:
            full_sql += f" ORDER BY {order_by}"

        # Large Dataset Protection: limit to 10000 rows
        full_sql += " LIMIT 10000"

        return frappe.db.sql(full_sql, params, as_dict=True)


@frappe.whitelist()
def get_smriti_report_data(report_key, filters=None):
    """API endpoint to run SMRITI reporting engine."""
    if isinstance(filters, str):
        filters = json.loads(filters)
    engine = SMRITIReportEngine(report_key, filters)
    return engine.run()


@frappe.whitelist()
def save_smriti_saved_view(view_name, report_key, applied_filters_json, visible_columns_json, is_default=0):
    """Creates a SMRITI Saved View record for the current user."""
    user = frappe.session.user
    is_default = cint(is_default)
    
    if is_default:
        frappe.db.sql("""
            UPDATE `tabSMRITI Saved View`
            SET is_default = 0
            WHERE report_template = %s AND user = %s
        """, (report_key, user))
        
    doc = frappe.new_doc("SMRITI Saved View")
    doc.view_name = view_name
    doc.report_template = report_key
    doc.user = user
    doc.applied_filters_json = applied_filters_json
    doc.visible_columns_json = visible_columns_json
    doc.is_default = is_default
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc.name


@frappe.whitelist()
def get_smriti_saved_views(report_key):
    """Retrieves all saved views for this report template for the current user."""
    return frappe.get_all(
        "SMRITI Saved View",
        filters={"report_template": report_key, "user": frappe.session.user},
        fields=["name", "view_name", "applied_filters_json", "visible_columns_json", "is_default"],
        order_by="is_default desc, creation desc"
    )


@frappe.whitelist()
def delete_smriti_saved_view(view_name):
    """Deletes a saved view if the user is owner or system manager."""
    doc = frappe.get_doc("SMRITI Saved View", view_name)
    if doc.user == frappe.session.user or "System Manager" in frappe.get_roles():
        frappe.delete_doc("SMRITI Saved View", view_name, ignore_permissions=True)
        frappe.db.commit()
        return {"success": True}
    else:
        frappe.throw(_("Not permitted to delete this saved view"), frappe.PermissionError)


@frappe.whitelist()
def get_smriti_reports_list():
    """Returns all report templates that the current user is permitted to view.
    M-05: Role access is resolved via a single batch query on SMRITI Report Role,
    not one frappe.get_doc() call per template (N+1 pattern).
    """
    user = frappe.session.user
    roles = frappe.get_roles()

    _fields = [
        "name", "report_key", "report_name", "report_category", "filters_json",
        "columns_json", "company_restricted", "branch_restricted",
        "cache_minutes", "schema_version", "is_public"
    ]

    templates = frappe.get_all("SMRITI Report Template", fields=_fields)

    if user == "Administrator" or "System Manager" in roles:
        return templates

    # Batch-fetch ALL role_access rows for ALL templates in one query
    role_rows = frappe.db.get_all(
        "SMRITI Report Role",
        fields=["parent", "role"]
    )
    # Build: template_name → set of allowed roles
    template_roles = {}
    for r in role_rows:
        template_roles.setdefault(r.parent, set()).add(r.role)

    user_roles = set(roles)

    return [
        t for t in templates
        if not template_roles.get(t.name)                       # no role restriction = public
        or template_roles[t.name].intersection(user_roles)      # user has at least one role
    ]


@frappe.whitelist()
def get_smriti_warehouses():
    """Returns list of active warehouses."""
    return frappe.get_all("Warehouse", filters={"is_group": 0}, fields=["name", "warehouse_name", "company"], order_by="warehouse_name asc")


@frappe.whitelist()
def get_smriti_item_groups():
    """Returns list of item groups."""
    return frappe.get_all("Item Group", fields=["name"], order_by="name asc")


@frappe.whitelist()
def get_smriti_brands():
    """Returns list of brands."""
    return frappe.get_all("Brand", fields=["name"], order_by="name asc")


@frappe.whitelist()
def get_smriti_salespersons():
    """Returns list of sales persons."""
    return frappe.get_all("Sales Person", fields=["name", "sales_person_name"], order_by="sales_person_name asc")


@frappe.whitelist()
def get_smriti_cashiers():
    """Returns active SMRITI cashiers/managers."""
    return frappe.db.sql("""
        SELECT DISTINCT u.name, COALESCE(NULLIF(CONCAT(u.first_name, ' ', u.last_name), ' '), u.name) as fullname
        FROM `tabUser` u
        JOIN `tabHas Role` r ON r.parent = u.name
        WHERE r.role IN ('SMRITI Cashier', 'SMRITI Store Manager') AND u.enabled = 1
        ORDER BY fullname ASC
    """, as_dict=True)


