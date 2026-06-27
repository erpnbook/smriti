# -*- coding: utf-8 -*-
#
# @file: target_service.py
# @description: Service layer logic for SMRITI sales target vs achievement calculation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import getdate, flt
import calendar

def get_month_date_range(fiscal_year, month_name):
    """
    Computes calendar start and end dates for a given month inside a fiscal year.
    Supports split financial years (e.g. 2026-2027 where Apr-Dec is 2026, Jan-Mar is 2027).
    """
    dates = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
    if not dates:
        # Fallback to current year if fiscal year not found
        current_year = getdate().year
        ys, ye = current_year, current_year
    else:
        ys = getdate(dates.year_start_date).year
        ye = getdate(dates.year_end_date).year

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    m_num = month_map.get(month_name, 1)

    # Standard Indian financial year mapping (Apr-Dec in ys, Jan-Mar in ye)
    year = ys if m_num >= 4 else ye

    last_day = calendar.monthrange(year, m_num)[1]
    start_date = f"{year}-{m_num:02d}-01"
    end_date = f"{year}-{m_num:02d}-{last_day:02d}"

    return start_date, end_date

def get_employee_target_vs_achievement(employee, fiscal_year, month, company):
    """
    Calculates target vs achievement for a specific employee, month, and fiscal year.
    Returns a dict with target, achievement, and achievement percentage.
    """
    # 1. Fetch Target
    target = frappe.db.get_value(
        "SMRITI Sales Target",
        {"employee": employee, "fiscal_year": fiscal_year, "month": month, "company": company},
        ["target_amount", "target_qty"],
        as_dict=True
    )
    
    target_amt = flt(target.target_amount) if target else 0.0
    
    # 2. Resolve date range
    start_date, end_date = get_month_date_range(fiscal_year, month)
    
    # 3. Sum achievement from daily snapshots
    res = frappe.db.sql("""
        select sum(revenue) from `tabSMRITI Sales KPI Snapshot`
        where employee = %s and company = %s and date >= %s and date <= %s
    """, (employee, company, start_date, end_date))
    achievement_amt = flt(res[0][0]) if res and res[0][0] else 0.0
    
    achievement_pct = (flt(achievement_amt) / target_amt * 100.0) if target_amt > 0 else 0.0
    
    return {
        "employee": employee,
        "fiscal_year": fiscal_year,
        "month": month,
        "target_amount": target_amt,
        "achievement_amount": flt(achievement_amt),
        "achievement_percentage": flt(achievement_pct)
    }
