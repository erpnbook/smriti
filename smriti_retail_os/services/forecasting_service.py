# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/forecasting_service.py
# @description: SMRITI Forecasting Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/forecasting_service.py
# @description: Forecasting service for SMRITI PDT - EMA, Volatility, and WOC calculations.
# @author: Antigravity AI
# @date: 2026-06-19
#

import frappe
import math
from frappe.utils import add_days, getdate, today

def calculate_weekly_velocity_stats(company, party_stock_account, item_code):
    """
    Retrieves sales ledger entries, aggregates by day, and calculates:
    - weekly_velocity (daily EMA velocity * 7)
    - velocity_std_dev (standard deviation of daily sales)
    - velocity_confidence (forecast reliability percentage based on CV)
    - forecast_parameters (JSON configuration)
    """
    # 1. Resolve lookback window (default 28 days)
    avg_weeks = 4
    try:
        if frappe.db.exists("DocType", "SMRITI PSV Settings"):
            settings = frappe.get_cached_doc("SMRITI PSV Settings")
            avg_weeks = settings.reorder_avg_weeks or 4
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in services/forecasting_service.py:37: {sys.exc_info()[1]}")
    
    lookback_days = avg_weeks * 7
    start_date = add_days(today(), -lookback_days)
    
    # 2. Query sales entries from ledger (sales are represented by negative qty)
    # We support voucher_type as 'Sales' or 'Sales Upload' where qty < 0
    sales_entries = frappe.db.sql("""
        SELECT DATE(posting_datetime) as sale_date, SUM(ABS(qty)) as daily_qty
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE party_stock_account = %s
          AND item_code = %s
          AND posting_datetime >= %s
          AND qty < 0
        GROUP BY DATE(posting_datetime)
    """, (party_stock_account, item_code, start_date), as_dict=True)
    
    # Map sales by date
    sales_map = {getdate(entry.sale_date): float(entry.daily_qty) for entry in sales_entries}
    
    # Construct complete daily sales array for lookback period to capture zero-sales days
    daily_sales = []
    for d in range(lookback_days):
        chk_date = getdate(add_days(start_date, d))
        daily_sales.append(sales_map.get(chk_date, 0.0))
        
    # 3. Calculate EMA (alpha = 0.2)
    alpha = 0.2
    ema = 0.0
    for qty in daily_sales:
        ema = (alpha * qty) + ((1.0 - alpha) * ema)
        
    weekly_velocity = round(ema * 7.0, 2)
    
    # 4. Calculate standard deviation & confidence
    n = len(daily_sales)
    mean_sales = sum(daily_sales) / n if n > 0 else 0.0
    variance = sum((x - mean_sales) ** 2 for x in daily_sales) / n if n > 0 else 0.0
    std_dev = round(math.sqrt(variance), 2)
    
    # Confidence: exponential decay relative to Coefficient of Variation (CV)
    if mean_sales > 0.0:
        cv = std_dev / mean_sales
        # If cv is small (e.g. 0.1), confidence is high (~95%)
        # If cv is high (e.g. 2.0), confidence is lower (~36%)
        confidence = round(100.0 * math.exp(-0.5 * cv), 1)
    else:
        # If no sales at all, standard deviation is 0. This is a certain forecast of zero sales
        confidence = 100.0 if sum(daily_sales) == 0.0 else 50.0
        
    # Standardised parameters structure
    params = {
        "alpha": alpha,
        "span_days": lookback_days,
        "mean_sales_day": round(mean_sales, 2)
    }
    
    return {
        "weekly_velocity": weekly_velocity,
        "velocity_std_dev": std_dev,
        "velocity_confidence": confidence,
        "forecast_parameters": params
    }

def calculate_weeks_of_cover(current_stock, weekly_velocity):
    """
    Calculates Weeks of Cover (WOC).
    WOC = current_stock / weekly_velocity
    Caps at 99.0 if velocity is 0 but stock exists.
    """
    if current_stock <= 0.0:
        return 0.0
    if weekly_velocity <= 0.0:
        return 99.0
    return round(current_stock / weekly_velocity, 2)

def calculate_predicted_stockout_date(current_stock, weekly_velocity):
    """
    Calculates the predicted date of stockout based on daily velocity.
    """
    if current_stock <= 0.0:
        return today()
        
    daily_velocity = weekly_velocity / 7.0
    if daily_velocity <= 0.0:
        return None  # No velocity, stock will not stockout
        
    days_to_stockout = int(current_stock / daily_velocity)
    # Cap extremely long stockouts to prevent overflow (e.g. 3 years)
    days_to_stockout = min(days_to_stockout, 1000)
    return add_days(today(), days_to_stockout)
