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
    flt, fmt_money, get_first_day, get_last_day
)


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

