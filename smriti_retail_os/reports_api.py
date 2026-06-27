# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/reports_api.py
# @description: Backend API for SMRITI Reports and Analytics module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
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
    "inventory_productivity": {
        "is_custom": True
    },
    "psv_reorder_report": {
        "is_custom": True
    },
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
    },
    "security_audit_log": {
        "base_sql": """
            SELECT 
                creation,
                user,
                operation,
                subject,
                ip_address
            FROM `tabActivity Log`
            WHERE 1=1
        """,
        "group_by": None,
        "order_by": "creation DESC"
    },
    "address_change_log": {
        "base_sql": """
            SELECT 
                changed_at,
                changed_by,
                company,
                field_name,
                old_value,
                new_value
            FROM `tabSMRITI Address Audit Log`
            WHERE 1=1
        """,
        "group_by": None,
        "order_by": "changed_at DESC"
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

    def check_permissions(self, action="run"):
        """Checks if current user has role permission to run or export this report."""
        user = frappe.session.user
        if user == "Administrator" or "System Manager" in frappe.get_roles():
            return True
            
        if action == "run":
            allowed_roles = [r.role for r in self.template.get("role_access", [])]
            if not allowed_roles:
                frappe.throw(_("Access Denied for Report '{0}'").format(self.template.report_name), frappe.PermissionError)
                
            user_roles = frappe.get_roles()
            if not set(allowed_roles).intersection(set(user_roles)):
                frappe.throw(_("Access Denied for Report '{0}'").format(self.template.report_name), frappe.PermissionError)
            return True
            
        elif action == "export":
            self.check_permissions(action="run")
            
            template_export_roles = [r.role for r in self.template.get("role_access", []) if r.get("export_allowed")]
            
            user_roles = frappe.get_roles()
            if template_export_roles:
                if not set(template_export_roles).intersection(set(user_roles)):
                    frappe.throw(_("Export Denied for Report '{0}'").format(self.template.report_name), frappe.PermissionError)
            else:
                platform_default_export_roles = {"System Manager", "SMRITI Store Manager", "SMRITI Admin"}
                if not platform_default_export_roles.intersection(set(user_roles)):
                    frappe.throw(_("Export Denied for Report '{0}'").format(self.template.report_name), frappe.PermissionError)
            return True

    def get_cache_key(self):
        """Generates MD5 hash of filter options, company, user, and roles for secure caching."""
        company = self.filters.get("company") or frappe.defaults.get_user_default("Company") or ""
        user = frappe.session.user or "Guest"
        roles = sorted(frappe.get_roles(user))
        cache_dict = {
            "filters": self.filters,
            "company": company,
            "user": user,
            "roles": roles
        }
        filter_hash = hashlib.md5(
            json.dumps(cache_dict, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return f"smriti:{self.report_key}:{filter_hash}"

    def validate_report_dictionary_bounds(self):
        """
        P0 Governance Validation Rule:
        No dynamic report may execute unless all required columns are active,
        reportable, and approved in the SMRITI Business Dictionary.
        Measures must have a default_aggregation defined.
        """
        bypassed_reports = [
            "payment_register", "receipt_register", "cash_book", "day_book",
            "customer_outstanding", "supplier_outstanding", "security_audit_log", "address_change_log"
        ]
        query_config = REPORT_QUERIES.get(self.report_key)
        if self.report_key in bypassed_reports or (query_config and query_config.get("is_custom")):
            return

        columns = []
        if self.template.columns_json:
            try:
                columns = json.loads(self.template.columns_json)
            except Exception:
                columns = []
        
        for col in columns:
            fieldname = col.get("fieldname")
            if not fieldname:
                continue
            
            # Fetch term from database or cache
            term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": fieldname}, "name")
            if not term_name:
                term_name = frappe.db.get_value("SMRITI Business Term", {"dictionary_key": fieldname}, "name")
                
            if not term_name:
                frappe.throw(
                    frappe._("Governance Violation: Report column '{0}' is not defined in the SMRITI Business Dictionary.")
                    .format(fieldname),
                    frappe.ValidationError
                )
            
            term = frappe.get_doc("SMRITI Business Term", term_name)
            
            # Check approval status and reportable flag
            if term.approval_status != "Approved":
                frappe.throw(
                    frappe._("Governance Violation: Business term '{0}' is not approved (Current status: {1}).")
                    .format(fieldname, term.approval_status),
                    frappe.ValidationError
                )
                
            if term.status == "Deprecated":
                frappe.throw(
                    frappe._("Governance Violation: Business term '{0}' is deprecated.")
                    .format(fieldname),
                    frappe.ValidationError
                )
                
            if not term.is_reportable:
                frappe.throw(
                    frappe._("Governance Violation: Business term '{0}' is marked as non-reportable.")
                    .format(fieldname),
                    frappe.ValidationError
                )
                
            # Check Measure aggregation constraints
            if term.measure_or_dimension == "Measure":
                if not term.default_aggregation or term.default_aggregation == "None":
                    frappe.throw(
                        frappe._("Governance Violation: Measure term '{0}' must define a default aggregation type (None is not allowed).")
                        .format(fieldname),
                        frappe.ValidationError
                    )

    def validate_report_formula_bounds(self):
        """
        P0 Governance Validation Rule:
        Any linked formula in the glossary terms must exist, be active,
        and approved in the Formula Registry.
        """
        bypassed_reports = [
            "payment_register", "receipt_register", "cash_book", "day_book",
            "customer_outstanding", "supplier_outstanding", "security_audit_log", "address_change_log"
        ]
        if self.report_key in bypassed_reports:
            return

        columns = []
        if self.template.columns_json:
            try:
                columns = json.loads(self.template.columns_json)
            except Exception:
                columns = []

        for col in columns:
            fieldname = col.get("fieldname")
            if not fieldname:
                continue
            
            term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": fieldname}) or frappe.db.get_value("SMRITI Business Term", {"dictionary_key": fieldname})
            if not term_name:
                continue
                
            term = frappe.get_doc("SMRITI Business Term", term_name)
            for f_row in term.get("related_formulas", []):
                formula_name = f_row.formula_id
                if not formula_name or not frappe.db.exists("SMRITI Formula Definition", formula_name):
                    frappe.throw(
                        frappe._("Governance Violation: Linked formula definition '{0}' on term '{1}' does not exist in the Formula Registry.")
                        .format(formula_name, fieldname),
                        frappe.ValidationError
                    )
                
                formula = frappe.get_doc("SMRITI Formula Definition", formula_name)
                if formula.status != "Approved":
                    frappe.throw(
                        frappe._("Governance Violation: Linked formula '{0}' is not approved (Current status: {1}).")
                        .format(formula_name, formula.status),
                        frappe.ValidationError
                    )
                if not formula.is_active:
                    frappe.throw(
                        frappe._("Governance Violation: Linked formula '{0}' is inactive.")
                        .format(formula_name),
                        frappe.ValidationError
                    )

    def run(self):
        self.check_permissions()

        # Enforce SMRITI P0 Governance validations
        self.validate_report_dictionary_bounds()
        self.validate_report_formula_bounds()

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

        # Log to SMRITI PSV Activity Log for Explainability & Audit
        try:
            ip_addr = "127.0.0.1"
            if hasattr(frappe.local, "request_ip") and frappe.local.request_ip:
                ip_addr = frappe.local.request_ip
            
            columns = []
            if self.template.columns_json:
                try:
                    columns = json.loads(self.template.columns_json)
                except Exception:
                    columns = []
            
            selected_terms = [c.get("fieldname") for c in columns if c.get("fieldname")]
            aggregations = {}
            group_by_fields = []
            
            for col in columns:
                fieldname = col.get("fieldname")
                term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": fieldname}) or frappe.db.get_value("SMRITI Business Term", {"dictionary_key": fieldname})
                if term_name:
                    term = frappe.get_doc("SMRITI Business Term", term_name)
                    if term.measure_or_dimension == "Measure":
                        aggregations[fieldname] = term.default_aggregation
                    else:
                        group_by_fields.append(fieldname)
            
            explain_log = frappe.get_doc({
                "doctype": "SMRITI PSV Activity Log",
                "timestamp": frappe.utils.now_datetime(),
                "user": frappe.session.user or "Administrator",
                "action_type": "Formula Explained",
                "event_type": "REPORT_QUERY_EXECUTED",
                "reference_doctype": "SMRITI Report Template",
                "reference_name": self.report_key,
                "ip_address": ip_addr,
                "details": json.dumps({
                    "dictionary_version": self.template.schema_version or "1.0",
                    "selected_terms": selected_terms,
                    "aggregation": aggregations,
                    "group_by": group_by_fields
                })
            })
            explain_log.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error logging report execution explain audit: {str(e)}")

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
        elif self.report_key == "psv_reorder_report":
            return self._run_psv_reorder_report()
        elif self.report_key == "inventory_productivity":
            return self._run_inventory_productivity()
        return []

    def _run_inventory_productivity(self):
        company = self.filters.get("company")
        if not company:
            company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
        timespan_days = self.filters.get("timespan_days") or 30
        
        from smriti_retail_os.psv_service import get_inventory_productivity_metrics
        res = get_inventory_productivity_metrics(company, timespan_days=timespan_days)
        return res.get("all_items") or []

    def _run_psv_reorder_report(self):
        from smriti_retail_os.smriti_retail_os.report.psv_reorder_report.psv_reorder_report import get_data
        return get_data(self.filters)

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
        validate_query_safety(base_sql)
        group_by = config.get("group_by")
        order_by = config.get("order_by")

        # Safe SQL Resolver & Dynamic Auto-Aggregation
        base_alias_map = extract_select_alias_map(base_sql)
        columns = []
        bypassed_reports = [
            "payment_register", "receipt_register", "cash_book", "day_book",
            "customer_outstanding", "supplier_outstanding", "security_audit_log", "address_change_log"
        ]
        if self.template.columns_json and self.report_key not in bypassed_reports:
            try:
                columns = json.loads(self.template.columns_json)
            except Exception:
                columns = []

        dynamic_projections = []
        dimensions = []
        measures = []
        
        alias_map = {
            "POS Invoice Item": "items",
            "POS Invoice": "parent",
            "Item": "item",
            "Bin": "b",
            "SMRITI Party Stock Account": "psa",
            "Sales Invoice Payment": "p",
            "POS Closing Entry Detail": "cd",
            "POS Closing Entry": "ce",
            "Item Variant Attribute": "va"
        }

        for col in columns:
            fieldname = col.get("fieldname")
            if not fieldname:
                continue
            
            term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": fieldname}) or frappe.db.get_value("SMRITI Business Term", {"dictionary_key": fieldname})
            if term_name:
                term = frappe.get_doc("SMRITI Business Term", term_name)
                proj = term.projection_path or ""
                resolved_proj = proj
                if "." in proj:
                    parts = proj.split(".", 1)
                    tbl, col_name = parts[0], parts[1]
                    if tbl in alias_map:
                        resolved_proj = f"{alias_map[tbl]}.{col_name}"
                    else:
                        resolved_proj = f"`tab{tbl}`.{col_name}"
                else:
                    resolved_proj = proj or fieldname

                # Validate table/alias presence in base_sql to prevent MySQLdb.OperationalError: Unknown column
                if "." in resolved_proj:
                    alias_part = resolved_proj.split(".", 1)[0]
                    clean_alias = alias_part.replace("`", "").replace("\"", "").strip()
                    rev_alias_map = {v: k for k, v in alias_map.items()}
                    original_doctype = rev_alias_map.get(clean_alias)
                    
                    import re
                    has_alias = False
                    has_doctype = False
                    if original_doctype:
                        from_idx = find_top_level_from(base_sql)
                        sql_part_for_tables = base_sql[from_idx:] if from_idx != -1 else base_sql
                        normalized_sql = " ".join(sql_part_for_tables.split()).replace("`", "").replace('"', "")
                        alias_pattern = rf"\b(?:tab)?{re.escape(original_doctype)}\s+(?:AS\s+)?\b{re.escape(clean_alias)}\b"
                        has_alias = bool(re.search(alias_pattern, normalized_sql, re.IGNORECASE))
                        
                        doctype_pattern = rf"\b{re.escape(original_doctype)}\b|\b{re.escape('tab' + original_doctype)}\b"
                        has_doctype = bool(re.search(doctype_pattern, normalized_sql, re.IGNORECASE))
                        
                    if not has_alias and not has_doctype:
                        RESERVED_ALIASES = {"*", "__all__", "parent", "idx", "doctype", "owner", "modified", "creation"}
                        if fieldname.lower() in RESERVED_ALIASES:
                            frappe.throw(
                                _("Column '{0}' ({1}) is a framework-reserved alias and cannot be resolved dynamically.")
                                .format(col.get("label") or fieldname, fieldname),
                                frappe.ValidationError
                            )
                        recovered = base_alias_map.get(fieldname)
                        if recovered and not expression_contains_subquery(recovered):
                            log_explain_audit_event(
                                event_type="projection_recovery",
                                report=self.report_key,
                                fieldname=fieldname,
                                recovered_expression=recovered
                            )
                            resolved_proj = recovered
                            dynamic_projections.append(f"{resolved_proj} as {fieldname}")
                            if term.measure_or_dimension == "Measure":
                                measures.append(fieldname)
                            continue
                        else:
                            frappe.throw(
                                _("Column '{0}' ({1}) cannot be displayed in this report because it requires the '{2}' table, which is not part of this report's query configuration.")
                                .format(col.get("label") or fieldname, fieldname, original_doctype or clean_alias),
                                frappe.ValidationError,
                                title=_("Incompatible Report Column")
                            )
                
                if term.measure_or_dimension == "Measure":
                    agg = term.default_aggregation or "Sum"
                    if agg == "None":
                        agg = "Sum"
                    dynamic_projections.append(f"{agg}({resolved_proj}) as {fieldname}")
                    measures.append(fieldname)
                else:
                    dynamic_projections.append(f"{resolved_proj} as {fieldname}")
                    dimensions.append(resolved_proj)
            else:
                dynamic_projections.append(fieldname)

        if dynamic_projections and "FROM" in base_sql.upper():
            select_part = "SELECT " + ", ".join(dynamic_projections)
            from_index = find_top_level_from(base_sql)
            if from_index == -1:
                from_index = base_sql.upper().find("FROM")
            base_sql = select_part + " " + base_sql[from_index:]
            
            if dimensions:
                group_by = ", ".join(dimensions)
            else:
                group_by = None

        where_clauses = []
        params = {}

        # Company filter (always applicable if source contains company)
        company = self.filters.get("company")
        if company and table_supports_company_filter(base_sql):
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
                date_field = (
                    "creation" if "tabActivity Log" in base_sql
                    else "changed_at" if "tabSMRITI Address Audit Log" in base_sql
                    else "pe.posting_date" if "pe." in base_sql
                    else "posting_date" if "tabPayment Entry" in base_sql or "tabSales Invoice" in base_sql or "tabPurchase Invoice" in base_sql
                    else "parent.posting_date" if "parent ON" in base_sql
                    else "ce.posting_date" if "tabPOS Closing Entry" in base_sql
                    else "posting_date" if "tabPOS Invoice" in base_sql
                    else "i.posting_date"
                )
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

        # User filter for Activity Log
        user_filter = self.filters.get("user")
        if user_filter and "tabActivity Log" in base_sql:
            where_clauses.append("user = %(user)s")
            params["user"] = user_filter

        # Changed By filter for SMRITI Address Audit Log
        changed_by = self.filters.get("changed_by")
        if changed_by and "tabSMRITI Address Audit Log" in base_sql:
            where_clauses.append("changed_by = %(changed_by)s")
            params["changed_by"] = changed_by

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

        validate_query_safety(full_sql)

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


def log_explain_audit_event(event_type, report, fieldname, recovered_expression):
    try:
        ip_addr = "127.0.0.1"
        if hasattr(frappe.local, "request_ip") and frappe.local.request_ip:
            ip_addr = frappe.local.request_ip
            
        company = frappe.defaults.get_user_default("Company") or ""
        
        details = {
            "report": report,
            "fieldname": fieldname,
            "recovered_expression": recovered_expression
        }
        
        log_doc = frappe.get_doc({
            "doctype": "SMRITI Audit Event",
            "timestamp": frappe.utils.now_datetime(),
            "user": frappe.session.user or "Administrator",
            "event_type": event_type,
            "company": company,
            "ip_address": ip_addr,
            "before_state": "",
            "after_state": json.dumps(details)
        })
        log_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error in log_explain_audit_event: {str(e)}")


REPORT_FILTER_CAPABILITIES = {
    "tabActivity Log": {
        "company": False
    }
}

def table_supports_company_filter(base_sql):
    for table, capabilities in REPORT_FILTER_CAPABILITIES.items():
        if table in base_sql and not capabilities.get("company", True):
            return False
    return True

def expression_contains_subquery(expr):
    import re
    clean_expr = expr.upper()
    return bool(re.search(r"\bSELECT\b", clean_expr) or re.search(r"\bEXISTS\b", clean_expr))

def find_top_level_from(base_sql):
    sql_upper = base_sql.upper()
    select_index = sql_upper.find("SELECT")
    if select_index == -1:
        return -1

    start_pos = select_index + 6
    depth = 0
    for i in range(start_pos, len(base_sql)):
        char = base_sql[i]
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif depth == 0:
            if base_sql[i:i+4].upper() == "FROM" and (i == 0 or base_sql[i-1].isspace()) and (i+4 == len(base_sql) or base_sql[i+4].isspace() or base_sql[i+4] == '`'):
                return i
    return -1

def extract_select_alias_map(base_sql):
    """
    Parses base_sql to map fieldnames/aliases to their SQL expressions.
    Handles nested functions, CASE statements, and complex formatting.
    """
    import re
    alias_map = {}
    from_index = find_top_level_from(base_sql)
    if from_index == -1:
        return alias_map

    sql_upper = base_sql.upper()
    select_index = sql_upper.find("SELECT")
    start_pos = select_index + 6
    select_clause = base_sql[start_pos:from_index].strip()
    
    # Split select clause by comma at depth 0
    projections = []
    current_proj = []
    depth = 0
    for char in select_clause:
        if char == '(':
            depth += 1
            current_proj.append(char)
        elif char == ')':
            depth -= 1
            current_proj.append(char)
        elif char == ',' and depth == 0:
            projections.append("".join(current_proj).strip())
            current_proj = []
        else:
            current_proj.append(char)
    if current_proj:
        projections.append("".join(current_proj).strip())

    # Map aliases to expressions
    for proj in projections:
        proj = proj.strip()
        # Match "expression as alias"
        match = re.search(r"^(.*?)\s+as\s+([a-zA-Z0-9_`'\"\s]+)$", proj, re.IGNORECASE | re.DOTALL)
        if match:
            expr = match.group(1).strip()
            alias = match.group(2).replace("`", "").replace("\"", "").replace("'", "").strip()
            alias_map[alias] = expr
        else:
            # Fallback for plain column references (e.g., "tbl.col" -> alias is "col")
            parts = proj.split(".")
            last_part = parts[-1].strip().replace("`", "").replace("\"", "").replace("'", "")
            if re.match(r"^[a-zA-Z0-9_]+$", last_part):
                alias_map[last_part] = proj
            
    return alias_map


def validate_query_safety(sql_query):
    """
    Enforces REPORT_QUERY_POLICY_V1 at a behavior level.
    Only single read-only SELECT and WITH queries are allowed.
    All state mutations (DML, DDL), stored procedures, and multi-statements are blocked.
    """
    clean_sql = (sql_query or "").strip().lower()
    
    # 1. Reject multi-statement execution (semicolons)
    if ";" in clean_sql:
        frappe.throw(_("SQL Safety Violation: Multi-statement execution is strictly prohibited."), frappe.ValidationError)
        
    # 2. Must start with SELECT or WITH
    if not (clean_sql.startswith("select") or clean_sql.startswith("with")):
        frappe.throw(_("SQL Safety Violation: Report queries must start with SELECT or WITH (read-only only)."), frappe.ValidationError)
        
    # 3. Reject mutation keywords as standalone tokens
    import re
    forbidden_verbs = ["insert", "update", "delete", "truncate", "drop", "alter", "grant", "revoke", "replace", "create", "into"]
    for verb in forbidden_verbs:
        pattern = rf"\b{verb}\b"
        if re.search(pattern, clean_sql):
            frappe.throw(_("SQL Safety Violation: DDL/DML mutation keywords are prohibited in report queries."), frappe.ValidationError)


@frappe.whitelist()
def export_smriti_report(report_key, filters=None, format_type="csv"):
    """
    Exports report to CSV/Excel on the server. Checks permissions,
    generates CSV content, logs REPORT_EXPORTED, and returns downloadable file.
    """
    if isinstance(filters, str):
        filters = json.loads(filters) if filters else {}
    
    engine = SMRITIReportEngine(report_key, filters)
    engine.check_permissions(action="export")
    
    # Run report to get data
    results = engine.run()
    
    # Generate CSV content
    columns = []
    if engine.template.columns_json:
        try:
            columns = json.loads(engine.template.columns_json)
        except Exception:
            columns = []
            
    fieldnames = [col.get("fieldname") for col in columns if col.get("fieldname")]
    labels = [col.get("label") or col.get("fieldname") for col in columns if col.get("fieldname")]
    
    if not fieldnames and results:
        fieldnames = list(results[0].keys())
        labels = fieldnames
        
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(labels)
    
    for row in results:
        row_val = []
        for field in fieldnames:
            val = row.get(field)
            row_val.append("" if val is None else str(val))
        writer.writerow(row_val)
        
    csv_data = output.getvalue()
    output.close()
    
    # Log export audit event
    company = filters.get("company") or frappe.defaults.get_user_default("Company") or ""
    ip_addr = "127.0.0.1"
    if hasattr(frappe.local, "request_ip") and frappe.local.request_ip:
        ip_addr = frappe.local.request_ip
        
    audit_payload = {
        "report_key": report_key,
        "export_format": format_type,
        "company": company,
        "user": frappe.session.user,
        "rows": len(results),
        "template_version": cint(engine.template.template_version or 1),
        "filters": filters
    }
    
    log_doc = frappe.get_doc({
        "doctype": "SMRITI Audit Event",
        "timestamp": frappe.utils.now_datetime(),
        "user": frappe.session.user,
        "event_type": "REPORT_EXPORTED",
        "company": company,
        "ip_address": ip_addr,
        "before_state": "",
        "after_state": json.dumps(audit_payload)
    })
    log_doc.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # Return file download response
    frappe.response['filename'] = f"{report_key}_{frappe.utils.nowdate()}.csv"
    frappe.response['filecontent'] = csv_data.encode('utf-8')
    frappe.response['type'] = 'download'


@frappe.whitelist()
def get_report_glossary(report_key):
    """
    Returns column definitions, formulas, and worked examples from the SMRITI Business Dictionary
    and Formula Registry, cached in Redis to prevent database performance overhead.
    """
    cache_key = f"smriti:report_glossary:{report_key}"
    cached = frappe.cache().get_value(cache_key)
    if cached:
        return json.loads(cached)
        
    template = frappe.get_doc("SMRITI Report Template", report_key)
    columns = []
    if template.columns_json:
        try:
            columns = json.loads(template.columns_json)
        except Exception:
            columns = []
            
    glossary = {}
    for col in columns:
        fieldname = col.get("fieldname")
        if not fieldname:
            continue
            
        term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": fieldname}, "name")
        if not term_name:
            term_name = frappe.db.get_value("SMRITI Business Term", {"dictionary_key": fieldname}, "name")
            
        if term_name:
            term = frappe.get_doc("SMRITI Business Term", term_name)
            
            # Fetch formulas
            formulas = []
            for f_row in term.get("related_formulas", []):
                if frappe.db.exists("SMRITI Formula Definition", f_row.formula_id):
                    f_doc = frappe.get_doc("SMRITI Formula Definition", f_row.formula_id)
                    formulas.append({
                        "formula_id": f_doc.formula_id,
                        "formula_name": f_doc.formula_name,
                        "formula_expression": f_doc.formula_expression,
                        "formula_meaning": f_doc.formula_meaning
                    })
                    
            glossary[fieldname] = {
                "term_name": term.term_name,
                "definition": term.definition,
                "hinglish_definition": term.hinglish_definition or "",
                "measure_or_dimension": term.measure_or_dimension,
                "default_aggregation": term.default_aggregation or "None",
                "formulas": formulas
            }
            
    frappe.cache().set_value(cache_key, json.dumps(glossary), expires_in_sec=3600)
    return glossary


def invalidate_glossary_cache(doc, method=None):
    """
    Invalidates glossary caches when SMRITI Business Term or SMRITI Formula Definition changes.
    """
    try:
        keys = frappe.cache().get_keys("smriti:report_glossary:*")
        for k in keys:
            k_str = k.decode("utf-8") if isinstance(k, bytes) else k
            if ":" in k_str:
                frappe.cache().delete_key(k_str)
            else:
                frappe.cache().delete_value(k_str)
    except Exception:
        pass


def execute_audit_retention_archival():
    """
    Daily scheduler task to archive/delete SMRITI Audit Event logs older than 365 days.
    """
    try:
        from frappe.utils import add_days, nowdate
        cutoff_date = add_days(nowdate(), -365)
        frappe.db.sql("""
            DELETE FROM `tabSMRITI Audit Event`
            WHERE timestamp < %s
        """, cutoff_date)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error in execute_audit_retention_archival: {str(e)}")



