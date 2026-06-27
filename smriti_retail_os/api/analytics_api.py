# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/analytics_api.py
# @description: SMRITI Analytics Dashboard API — thin aggregation layer
#               over existing reports_api.py methods. No new SQL queries.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import (
    flt, nowdate, add_days, add_months,
    get_first_day, get_last_day, getdate
)

# ─── Permission ───────────────────────────────────────────────────────────────

def _check_access():
    roles = frappe.get_roles(frappe.session.user)
    if not ({"SMRITI Store Manager", "System Manager", "Administrator"} & set(roles)):
        frappe.throw(_("Access Denied"), frappe.PermissionError)


# ─── 1. Dashboard KPIs ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_dashboard_kpis():
    """
    Returns all KPI data for the analytics dashboard in a single call.
    Wraps reports_api.get_quick_stats() with period-over-period comparisons.
    """
    _check_access()

    today = nowdate()
    yesterday = add_days(today, -1)
    month_start = str(get_first_day(today))
    prev_month_start = str(get_first_day(add_months(today, -1)))
    prev_month_end = str(get_last_day(add_months(today, -1)))

    # Today's sales
    today_data = _sales_summary(today, today)
    yesterday_data = _sales_summary(yesterday, yesterday)

    # This month vs last month
    mtd_data = _sales_summary(month_start, today)
    prev_month_data = _sales_summary(prev_month_start, prev_month_end)

    # Outstanding receivables
    outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND outstanding_amount > 0
    """, as_dict=True)[0]

    # Stock value
    stock_val = frappe.db.sql("""
        SELECT COALESCE(SUM(stock_value), 0) as total,
               COUNT(DISTINCT item_code) as skus
        FROM `tabBin` WHERE actual_qty > 0
    """, as_dict=True)[0]

    # Low stock count
    low_stock = frappe.db.sql("""
        SELECT COUNT(DISTINCT item_code) as cnt
        FROM `tabBin` WHERE actual_qty > 0 AND actual_qty <= 5
    """, as_dict=True)[0]

    return {
        "today_sales":      flt(today_data["total"], 2),
        "today_bills":      today_data["bills"],
        "yesterday_sales":  flt(yesterday_data["total"], 2),
        "yesterday_bills":  yesterday_data["bills"],
        "sales_growth":     _pct_change(today_data["total"], yesterday_data["total"]),

        "mtd_sales":        flt(mtd_data["total"], 2),
        "mtd_bills":        mtd_data["bills"],
        "prev_month_sales": flt(prev_month_data["total"], 2),
        "mtd_growth":       _pct_change(mtd_data["total"], prev_month_data["total"]),

        "avg_ticket_today": flt(today_data["total"] / today_data["bills"], 2) if today_data["bills"] else 0,
        "avg_ticket_mtd":   flt(mtd_data["total"] / mtd_data["bills"], 2) if mtd_data["bills"] else 0,

        "outstanding":      flt(outstanding.get("total", 0), 2),
        "stock_value":      flt(stock_val.get("total", 0), 2),
        "total_skus":       int(stock_val.get("skus", 0)),
        "low_stock_count":  int(low_stock.get("cnt", 0)),
    }


def _sales_summary(from_date, to_date):
    """Single SQL aggregate for sales between dates."""
    row = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total,
               COUNT(*) as bills
        FROM `tabPOS Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
    """, {"f": from_date, "t": to_date}, as_dict=True)
    return row[0] if row else {"total": 0, "bills": 0}


def _pct_change(current, previous):
    if not previous:
        return 0
    return flt(((current - previous) / previous) * 100, 1)


# ─── 2. Sales Trend ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_sales_trend(days=30):
    """
    Returns daily sales totals for the last N days.
    Used for the trend line/area chart.
    """
    _check_access()
    days = int(days)
    from_date = add_days(nowdate(), -(days - 1))

    rows = frappe.db.sql("""
        SELECT posting_date AS date,
               COUNT(*) AS bills,
               COALESCE(SUM(grand_total), 0) AS sales
        FROM `tabPOS Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY posting_date
        ORDER BY posting_date ASC
    """, {"f": from_date, "t": nowdate()}, as_dict=True)

    return [{"date": str(r.date), "bills": int(r.bills), "sales": flt(r.sales, 2)} for r in rows]


# ─── 3. Payment Mix ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payment_mix(days=30):
    """
    Payment mode distribution for pie/donut chart.
    """
    _check_access()
    from_date = add_days(nowdate(), -(int(days) - 1))

    rows = frappe.db.sql("""
        SELECT pp.mode_of_payment, SUM(pp.amount) as total
        FROM `tabPOS Invoice` pi
        JOIN `tabSales Invoice Payment` pp ON pp.parent = pi.name
        WHERE pi.docstatus = 1
          AND pi.posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY pp.mode_of_payment
        ORDER BY total DESC
    """, {"f": from_date, "t": nowdate()}, as_dict=True)

    return [{"mode": r.mode_of_payment, "total": flt(r.total, 2)} for r in rows]


# ─── 4. Top Performers ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_top_items(days=30, limit=10):
    """Top selling items by quantity."""
    _check_access()
    from_date = add_days(nowdate(), -(int(days) - 1))

    rows = frappe.db.sql("""
        SELECT pii.item_code, pii.item_name,
               SUM(pii.qty) as total_qty,
               SUM(pii.amount) as total_amount
        FROM `tabPOS Invoice` pi
        JOIN `tabPOS Invoice Item` pii ON pii.parent = pi.name
        WHERE pi.docstatus = 1
          AND pi.posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY pii.item_code
        ORDER BY total_qty DESC
        LIMIT %(limit)s
    """, {"f": from_date, "t": nowdate(), "limit": int(limit)}, as_dict=True)

    return [{"item_code": r.item_code, "item_name": r.item_name,
             "qty": flt(r.total_qty, 2), "amount": flt(r.total_amount, 2)} for r in rows]


@frappe.whitelist()
def get_cashier_performance(days=30):
    """Cashier-wise sales rankings."""
    _check_access()
    from_date = add_days(nowdate(), -(int(days) - 1))

    rows = frappe.db.sql("""
        SELECT owner as cashier,
               COUNT(*) as bills,
               COALESCE(SUM(grand_total), 0) as total_sales
        FROM `tabPOS Invoice`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(f)s AND %(t)s
        GROUP BY owner
        ORDER BY total_sales DESC
    """, {"f": from_date, "t": nowdate()}, as_dict=True)

    return [{
        "cashier": r.cashier,
        "bills": int(r.bills),
        "total_sales": flt(r.total_sales, 2),
        "avg_ticket": flt(r.total_sales / r.bills, 2) if r.bills else 0
    } for r in rows]


# ─── 5. Outstanding Aging ────────────────────────────────────────────────────

@frappe.whitelist()
def get_outstanding_aging():
    """Aging buckets for receivables donut/bar chart."""
    _check_access()
    today = getdate(nowdate())

    invoices = frappe.db.get_all(
        "Sales Invoice",
        filters={"docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["outstanding_amount", "posting_date", "due_date"]
    )

    buckets = {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "above_90": 0}
    for inv in invoices:
        due = getdate(inv.due_date) if inv.due_date else getdate(inv.posting_date)
        days = (today - due).days
        amt = flt(inv.outstanding_amount)
        if days <= 0:
            buckets["current"] += amt
        elif days <= 30:
            buckets["1_30"] += amt
        elif days <= 60:
            buckets["31_60"] += amt
        elif days <= 90:
            buckets["61_90"] += amt
        else:
            buckets["above_90"] += amt

    return {k: flt(v, 2) for k, v in buckets.items()}
