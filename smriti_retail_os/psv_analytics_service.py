# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_analytics_service.py
# @description: SMRITI PSV Analytics Service — redistribution, WOC risks, sell-in/out, productivity metrics.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: Extracted from psv_service.py (Phase 4 remediation).
#       psv_service.py re-imports all public names for backward compatibility.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import today, now_datetime, add_days

from smriti_retail_os.psv_snapshot_service import get_landing_cost


ACTION_INCREASE_STOCK = "Increase Stock"
ACTION_MAINTAIN = "Maintain"
ACTION_IMPROVE_MARGIN = "Improve Margin"
ACTION_LIQUIDATE = "Liquidate / Review"
ACTION_REPLENISH_URGENT = "Replenish Urgent"


@frappe.whitelist()
def get_redistribution_suggestions(company=None):
    """
    Returns stock redistribution suggestions across channel partners for a company.
    """
    from frappe.utils import add_days
    settings = frappe.get_single("PSV System Settings")
    scope = settings.redistribution_scope or "Same Territory"
    critical_woc = settings.weeks_of_cover_critical or 2
    healthy_woc = settings.weeks_of_cover_healthy or 8
    
    filters = {"active": 1}
    if company:
        filters["company"] = company
        
    partners = smriti.db.get_list(
        "PSV Channel Partner",
        filters=filters,
        fields=["name", "company", "territory", "region", "zone"]
    )
    
    if not partners:
        partners = smriti.db.get_list(
            "SMRITI Party Stock Account",
            filters=filters,
            fields=["name", "company", "zone", "region"]
        )
        for p in partners:
            p["territory"] = "All Territories"
            
    if not partners:
        return []
        
    date_28_days_ago = add_days(today(), -28)
    
    balances = smriti.db.sql("""
        SELECT channel_partner, item_variant, SUM(qty) as balance
        FROM `tabPSV Ledger Entry`
        GROUP BY channel_partner, item_variant
        HAVING SUM(qty) != 0
    """, as_dict=True)
    
    if not balances:
        balances = smriti.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            GROUP BY party_stock_account, item_code
            HAVING SUM(qty) != 0
        """, as_dict=True)
        
    sales_data = smriti.db.sql("""
        SELECT channel_partner, item_variant, SUM(ABS(qty)) as total_sales
        FROM `tabPSV Ledger Entry`
        WHERE qty < 0 AND posting_datetime >= %s
          AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
        GROUP BY channel_partner, item_variant
    """, (date_28_days_ago,), as_dict=True)
    
    if not sales_data:
        sales_data = smriti.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY party_stock_account, item_code
        """, (date_28_days_ago,), as_dict=True)
        
    velocity_map = {}
    for s in sales_data:
        key = (s["channel_partner"], s["item_variant"])
        velocity_map[key] = float(s["total_sales"] or 0.0) / 4.0
        
    partner_info = {p.name: p for p in partners}
    
    sources = []
    sinks = []
    
    for b in balances:
        partner_name = b["channel_partner"]
        if partner_name not in partner_info:
            continue
            
        variant = b["item_variant"]
        balance = float(b["balance"] or 0.0)
        
        if balance <= 0:
            continue
            
        vel = velocity_map.get((partner_name, variant), 0.0)
        
        if vel > 0:
            woc = balance / vel
        else:
            woc = 999.0
            
        if woc > healthy_woc:
            excess = balance - (healthy_woc * vel)
            if excess > 0:
                sources.append({
                    "partner": partner_name,
                    "item": variant,
                    "balance": balance,
                    "velocity": vel,
                    "woc": woc,
                    "excess": excess
                })
        elif woc < critical_woc:
            shortage = (healthy_woc * vel) - balance
            if shortage > 0:
                sinks.append({
                    "partner": partner_name,
                    "item": variant,
                    "balance": balance,
                    "velocity": vel,
                    "woc": woc,
                    "shortage": shortage
                })
                
    suggestions = []
    for sink in sinks:
        for source in sources:
            if sink["item"] != source["item"]:
                continue
                
            p_sink = partner_info[sink["partner"]]
            p_source = partner_info[source["partner"]]
            
            match_geo = False
            if scope == "Same Territory":
                match_geo = (p_sink.territory == p_source.territory)
            elif scope == "Same Region":
                match_geo = (str(p_sink.region).strip().lower() == str(p_source.region).strip().lower())
            else:
                match_geo = True
                
            if match_geo:
                transfer_qty = min(source["excess"], sink["shortage"])
                if transfer_qty > 0:
                    suggestions.append({
                        "item_code": sink["item"],
                        "source_partner": source["partner"],
                        "target_partner": sink["partner"],
                        "suggested_transfer_qty": round(transfer_qty, 2),
                        "source_woc": round(source["woc"], 1),
                        "target_woc": round(sink["woc"], 1)
                    })
                    
    suggestions.sort(key=lambda x: x["suggested_transfer_qty"], reverse=True)
    return suggestions


@frappe.whitelist()
def get_channel_health_score(channel_partner, from_date=None, to_date=None):
    """
    Returns the channel health score for a channel partner.
    """
    enabled = smriti.db.get_single("PSV System Settings", "channel_health_enabled")
    if not enabled:
        return {
            "enabled": False,
            "score": 0.0,
            "status": "Disabled",
            "message": "Channel Health features are scheduled for Phase 1.2"
        }
    else:
        open_alerts = smriti.db.count("SMRITI PSV Exception Record", {
            "party_stock_account": channel_partner,
            "status": "Pending Reconciliation"
        })
        score = max(0.0, 100.0 - (open_alerts * 10.0))
        status = "Good" if score >= 80 else ("Average" if score >= 50 else "Poor")
        return {
            "enabled": True,
            "score": score,
            "status": status,
            "message": f"Channel Health: {status} ({score} pts)"
        }


@frappe.whitelist()
def get_sellin_sellout_summary(company, channel_partner=None):
    """
    Returns a summary of sell-in, sell-out, current stock balance, and WOC.
    """
    from frappe.utils import add_days
    date_28_days_ago = add_days(today(), -28)
    
    balance_res = smriti.db.sql("""
        SELECT SUM(qty) FROM `tabPSV Ledger Entry`
        WHERE company = %s {0}
    """.format("AND channel_partner = %s" if channel_partner else ""), 
    tuple(x for x in [company, channel_partner] if x))
    
    is_legacy = False
    if not balance_res or balance_res[0][0] is None:
        balance_res = smriti.db.sql("""
            SELECT SUM(qty) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, channel_partner] if x))
        is_legacy = True
        
    current_balance = float(balance_res[0][0]) if balance_res and balance_res[0][0] is not None else 0.0
    
    if not is_legacy:
        sellin_res = smriti.db.sql("""
            SELECT SUM(qty) FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty > 0 AND posting_datetime >= %s {0}
        """.format("AND channel_partner = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
    else:
        sellin_res = smriti.db.sql("""
            SELECT SUM(qty) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty > 0 AND posting_datetime >= %s {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
        
    sell_in_qty = float(sellin_res[0][0]) if sellin_res and sellin_res[0][0] is not None else 0.0
    
    if not is_legacy:
        sellout_res = smriti.db.sql("""
            SELECT SUM(ABS(qty)) FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales') {0}
        """.format("AND channel_partner = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
    else:
        sellout_res = smriti.db.sql("""
            SELECT SUM(ABS(qty)) FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload') {0}
        """.format("AND party_stock_account = %s" if channel_partner else ""),
        tuple(x for x in [company, date_28_days_ago, channel_partner] if x))
        
    sell_out_qty = float(sellout_res[0][0]) if sellout_res and sellout_res[0][0] is not None else 0.0
    
    weekly_sales_velocity = sell_out_qty / 4.0
    
    if weekly_sales_velocity > 0:
        weeks_of_cover = current_balance / weekly_sales_velocity
    else:
        weeks_of_cover = 999.0 if current_balance > 0 else 0.0
        
    return {
        "current_balance": current_balance,
        "sell_in_qty": sell_in_qty,
        "sell_out_qty": sell_out_qty,
        "weekly_sales_velocity": weekly_sales_velocity,
        "weeks_of_cover": weeks_of_cover
    }


@frappe.whitelist()
def get_stock_cover_risks(company):
    """
    Returns a list of all item variants at channel partners that have warning or critical Weeks of Cover.
    """
    from frappe.utils import add_days
    settings = frappe.get_single("PSV System Settings")
    critical_woc = settings.weeks_of_cover_critical or 2
    warning_woc = settings.weeks_of_cover_warning or 4
    
    partners = smriti.db.get_list("PSV Channel Partner", filters={"company": company, "active": 1}, fields=["name"])
    if not partners:
        partners = smriti.db.get_list("SMRITI Party Stock Account", filters={"company": company, "active": 1}, fields=["name"])
    if not partners:
        return []
        
    date_28_days_ago = add_days(today(), -28)
    
    use_new = smriti.db.exists("PSV Ledger Entry", {"company": company})
    if use_new:
        balances = smriti.db.sql("""
            SELECT channel_partner, item_variant, SUM(qty) as balance
            FROM `tabPSV Ledger Entry`
            WHERE company = %s
            GROUP BY channel_partner, item_variant
            HAVING SUM(qty) > 0
        """, (company,), as_dict=True)
        
        sales_data = smriti.db.sql("""
            SELECT channel_partner, item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
            GROUP BY channel_partner, item_variant
        """, (company, date_28_days_ago), as_dict=True)
    else:
        balances = smriti.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s
            GROUP BY party_stock_account, item_code
            HAVING SUM(qty) > 0
        """, (company,), as_dict=True)
        
        sales_data = smriti.db.sql("""
            SELECT party_stock_account as channel_partner, item_code as item_variant, SUM(ABS(qty)) as total_sales
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY party_stock_account, item_code
        """, (company, date_28_days_ago), as_dict=True)
        
    velocity_map = {}
    for s in sales_data:
        velocity_map[(s["channel_partner"], s["item_variant"])] = float(s["total_sales"] or 0.0) / 4.0
        
    risks = []
    for b in balances:
        partner = b["channel_partner"]
        variant = b["item_variant"]
        qty = float(b["balance"])
        
        vel = velocity_map.get((partner, variant), 0.0)
        if vel > 0:
            woc = qty / vel
        else:
            woc = 999.0
            
        if woc < warning_woc:
            status = "Critical" if woc < critical_woc else "Warning"
            risks.append({
                "item_code": variant,
                "channel_partner": partner,
                "weeks_cover": round(woc, 1),
                "status": status,
                "balance": qty,
                "velocity": round(vel, 2)
            })
            
    risks.sort(key=lambda x: x["weeks_cover"])
    return risks


@frappe.whitelist()
def get_channel_stock_trend(company):
    """
    Returns the historical total channel stock value trend.
    """
    dates = smriti.db.sql("""
        SELECT DISTINCT snapshot_date
        FROM `tabPSV Stock Aging Snapshot`
        ORDER BY snapshot_date DESC
        LIMIT 10
    """, as_dict=False)
    
    trend = []
    if dates:
        dates = list(dates)
        dates.reverse()
        for row in dates:
            date_val = row[0]
            snaps = smriti.db.sql("""
                SELECT item_variant, qty
                FROM `tabPSV Stock Aging Snapshot`
                WHERE snapshot_date = %s
            """, (date_val,), as_dict=True)
            
            total_val = 0.0
            for s in snaps:
                cost = get_landing_cost(s["item_variant"])
                total_val += float(s["qty"]) * cost
                
            trend.append({
                "date": str(date_val),
                "value": round(total_val, 2)
            })
            
    return trend


# Action Recommendation Constants


@frappe.whitelist()
def get_inventory_productivity_metrics(company, timespan_days=30):
    """
    Computes GMROI and SKU Rationalization metrics in bulk.
    Returns: {
        "summary": {
            "star": int,
            "cash_cow": int,
            "underperformer": int,
            "slow_mover": int,
            "stockout_winner": int
        },
        "top_skus": list of dicts,
        "all_items": list of dicts
    }
    """
    from frappe.utils import add_days, now_datetime
    
    timespan_days = int(timespan_days or 30)
    start_date = add_days(now_datetime(), -timespan_days)
    
    # 1. Fetch velocity threshold
    star_velocity_threshold = float(smriti.db.get_single("PSV System Settings", "star_velocity_threshold") or 1.0)
    
    # Check if new schema/ledger exists
    use_new = smriti.db.exists("PSV Ledger Entry", {"company": company})
    
    # 2. Get current stock balances
    if use_new:
        bal_res = smriti.db.sql("""
            SELECT item_variant, SUM(qty) as balance
            FROM `tabPSV Ledger Entry`
            WHERE company = %s
            GROUP BY item_variant
        """, (company,), as_dict=True)
    else:
        bal_res = smriti.db.sql("""
            SELECT item_code as item_variant, SUM(qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s
            GROUP BY item_code
        """, (company,), as_dict=True)
        
    balances = {r["item_variant"]: float(r["balance"] or 0.0) for r in bal_res}
    
    # 3. Get sales quantities and transaction counts
    if use_new:
        sales_res = smriti.db.sql("""
            SELECT item_variant, SUM(ABS(qty)) as sales_qty, COUNT(DISTINCT voucher_no) as txn_count
            FROM `tabPSV Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (transaction_type = 'Sales' OR transaction_type = 'Sales Upload' OR voucher_type = 'Sales')
            GROUP BY item_variant
        """, (company, start_date), as_dict=True)
    else:
        sales_res = smriti.db.sql("""
            SELECT item_code as item_variant, SUM(ABS(qty)) as sales_qty, COUNT(DISTINCT voucher_no) as txn_count
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE company = %s AND qty < 0 AND posting_datetime >= %s
              AND (voucher_type = 'Sales' OR voucher_type = 'Sales Upload')
            GROUP BY item_code
        """, (company, start_date), as_dict=True)
        
    sales = {r["item_variant"]: float(r["sales_qty"] or 0.0) for r in sales_res}
    sales_txns = {r["item_variant"]: int(r["txn_count"] or 0) for r in sales_res}
    
    # Get all distinct SKUs that have either stock or sales
    all_skus = set(balances.keys()).union(sales.keys())
    if not all_skus:
        return {
            "summary": {"star": 0, "cash_cow": 0, "underperformer": 0, "slow_mover": 0, "stockout_winner": 0},
            "top_skus": [],
            "all_items": []
        }
        
    # 4. Get realized selling prices in bulk
    realized_prices_res = smriti.db.sql("""
        SELECT item_code as item_variant, SUM(base_amount) as total_amount, SUM(qty) as total_qty
        FROM `tabSales Invoice Item`
        WHERE docstatus = 1 AND parent IN (
            SELECT name FROM `tabSales Invoice` WHERE company = %s
        )
        GROUP BY item_code
    """, (company,), as_dict=True)
    
    realized_prices = {}
    for r in realized_prices_res:
        if r["total_qty"] and float(r["total_qty"]) > 0:
            realized_prices[r["item_variant"]] = float(r["total_amount"]) / float(r["total_qty"])
            
    # 5. Get standard prices in bulk
    std_prices_res = smriti.db.sql("""
        SELECT item_code as item_variant, price_list_rate
        FROM `tabItem Price`
        WHERE price_list = 'Standard Selling'
    """, as_dict=True)
    std_prices = {r["item_variant"]: float(r["price_list_rate"] or 0.0) for r in std_prices_res}
    
    # 6. Get item costs and templates in bulk
    item_info_res = smriti.db.sql("""
        SELECT name, valuation_rate, standard_rate, variant_of
        FROM `tabItem`
    """, as_dict=True)
    item_info = {r["name"]: r for r in item_info_res}
    
    # Helper to resolve cost (valuation/landing cost)
    def resolve_cost(sku):
        info = item_info.get(sku)
        if not info:
            return 0.0
        if info.get("valuation_rate"):
            return float(info["valuation_rate"])
        if info.get("standard_rate"):
            return float(info["standard_rate"])
        if info.get("variant_of"):
            p_info = item_info.get(info["variant_of"])
            if p_info:
                if p_info.get("valuation_rate"):
                    return float(p_info["valuation_rate"])
                if p_info.get("standard_rate"):
                    return float(p_info["standard_rate"])
        return 0.0

    # Helper to resolve price with fallbacks
    def resolve_price(sku):
        if sku in realized_prices:
            return realized_prices[sku]
        if sku in std_prices and std_prices[sku] > 0:
            return std_prices[sku]
        info = item_info.get(sku)
        if info and info.get("standard_rate"):
            return float(info["standard_rate"])
        if info and info.get("variant_of"):
            p_info = item_info.get(info["variant_of"])
            if p_info and p_info.get("standard_rate"):
                return float(p_info["standard_rate"])
        c = resolve_cost(sku)
        return c * 1.5
        
    # 7. Compute metrics for each SKU
    items_metrics = []
    summary_counts = {"star": 0, "cash_cow": 0, "underperformer": 0, "slow_mover": 0, "stockout_winner": 0}
    
    for sku in all_skus:
        bal = balances.get(sku, 0.0)
        s_qty = sales.get(sku, 0.0)
        s_txn = sales_txns.get(sku, 0)
        cost = resolve_cost(sku)
        price = resolve_price(sku)
        
        # Calculate velocity (units per week)
        weeks = timespan_days / 7.0
        velocity = s_qty / weeks if weeks > 0 else 0.0
        
        gross_margin = s_qty * (price - cost)
        inventory_value = bal * cost
        
        # Data Quality Warnings
        warnings = []
        if cost <= 0:
            warnings.append("Cost Data Missing")
        if sku not in realized_prices:
            warnings.append("Using Fallback Selling Price")
        if bal < 0:
            warnings.append("Inventory Adjustment Required")
            
        # Confidence Indicator
        if s_qty >= 20 and s_txn >= 5:
            confidence = "High"
        elif s_qty > 0 and s_txn > 0:
            confidence = "Medium"
        else:
            confidence = "Low"
            
        # GMROI calculation with empty/depleted stockout winner check
        is_depleted = (bal <= 0) and (s_qty > 0)
        
        if is_depleted:
            gmroi = None
            category = "Stockout Winner"
            action = ACTION_REPLENISH_URGENT
            summary_counts["stockout_winner"] += 1
        else:
            if inventory_value > 0:
                gmroi = gross_margin / inventory_value
            else:
                gmroi = 0.0
                
            # Classify based on velocity threshold and GMROI >= 2.0
            if velocity >= star_velocity_threshold:
                if gmroi >= 2.0:
                    category = "Star"
                    action = ACTION_INCREASE_STOCK
                    summary_counts["star"] += 1
                else:
                    category = "Underperformer"
                    action = ACTION_IMPROVE_MARGIN
                    summary_counts["underperformer"] += 1
            else:
                if gmroi >= 2.0:
                    category = "Cash Cow"
                    action = ACTION_MAINTAIN
                    summary_counts["cash_cow"] += 1
                else:
                    category = "Slow Mover"
                    action = ACTION_LIQUIDATE
                    summary_counts["slow_mover"] += 1
                    
        # Compute Inventory Productivity Score (0-100)
        g_val = gmroi if gmroi is not None else 3.0  # Give Stockout Winners top score for GMROI
        norm_gmroi = min(g_val / 3.0, 1.0) * 100.0
        norm_vel = min(velocity / 5.0, 1.0) * 100.0
        productivity_score = round((0.6 * norm_gmroi) + (0.4 * norm_vel), 2)
        
        items_metrics.append({
            "item_code": sku,
            "sales_qty": s_qty,
            "txn_count": s_txn,
            "velocity": round(velocity, 2),
            "cost": round(cost, 2),
            "price": round(price, 2),
            "gross_margin": round(gross_margin, 2),
            "inventory_value": round(inventory_value, 2),
            "current_stock": round(bal, 2),
            "gmroi": round(gmroi, 2) if gmroi is not None else None,
            "category": category,
            "action": action,
            "score": productivity_score,
            "confidence": confidence,
            "warnings": warnings
        })
        
    # Sort: productivity score descending
    items_metrics.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "summary": summary_counts,
        "top_skus": items_metrics[:10],
        "all_items": items_metrics
    }


@frappe.whitelist()
def get_inventory_productivity_methodology():
    """
    Returns the central, single source of truth for inventory productivity formulas,
    classification rules, and score explanations in SMRITI Retail OS.
    """
    import smriti_retail_os
    from frappe.utils import now_datetime
    smriti_version = getattr(smriti_retail_os, "__version__", "1.2.10")
    
    return {
        "title": _("Inventory Productivity & SKU Rationalization"),
        "category": _("Analytics Guides"),
        "version": "1.0",
        "effective_date": "2026-06-11",
        "smriti_version": smriti_version,
        "generated_datetime": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": "Founder – AITDL (AI Technology & Development Lab)",
            "quote": _("Software should not merely record transactions. It should help businesses make better decisions.")
        },
        "about_smriti": _(
            "SMRITI Retail OS was created from decades of observation, implementation experience, "
            "operational learning, business process analysis, and real-world retail challenges.\n\n"
            "The platform has been shaped through continuous interaction with retailers, distributors, "
            "warehouse operators, accountants, store managers, and business owners."
        ),
        "summary": _("This guide explains the analytical framework used to calculate and classify inventory productivity and SKU performance in SMRITI Retail OS."),
        "formulas": [
            {
                "name": "GMROI (Gross Margin Return on Investment)",
                "business_meaning": _("Measures the profitability of inventory. Tells you how many rupees of gross margin are generated for every rupee invested in stock."),
                "formula": "GMROI = Gross Margin / Current Inventory Value",
                "example": _("Gross Margin = ₹46,680, Inventory Value = ₹27,450. GMROI = 46,680 / 27,450 = 1.70"),
                "interpretation": _("A GMROI of 1.70 means every ₹1.00 invested in inventory generated ₹1.70 of gross margin. GMROI >= 2.0 is considered high-performing.")
            },
            {
                "name": "Gross Margin",
                "business_meaning": _("The net profit made from selling the item after subtracting its cost."),
                "formula": "Gross Margin = Sales Qty * (Average Realized Selling Price - Landing Cost)",
                "example": _("Sales Qty = 120, Price = ₹999, Cost = ₹610. Gross Margin = 120 * (999 - 610) = ₹46,680"),
                "interpretation": _("The total direct profit contributed by the SKU to the business.")
            },
            {
                "name": "Inventory Value",
                "business_meaning": _("The total capital tied up in the stock of this SKU."),
                "formula": "Inventory Value = Current Stock * Landing Cost",
                "example": _("Current Stock = 45, Cost = ₹610. Inventory Value = 45 * 610 = ₹27,450"),
                "interpretation": _("Represents the opportunity cost of locked capital in warehouse/store inventory.")
            },
            {
                "name": "Weekly Velocity",
                "business_meaning": _("The rate at which the item sells per week."),
                "formula": "Weekly Velocity = Sales Qty / (Timespan Days / 7)",
                "example": _("Sales Qty = 120, Timespan = 30 Days. Weekly Velocity = 120 / (30 / 7) = 28.0 units/week"),
                "interpretation": _("Measures product demand speed. Compared against the velocity threshold (default 1.0/wk) to classify demand speed.")
            },
            {
                "name": "Productivity Score",
                "business_meaning": _("A composite index (0-100) combining profitability (60% weight) and demand speed (40% weight)."),
                "formula": "Productivity Score = (0.6 * Normalized GMROI) + (0.4 * Normalized Velocity)",
                "example": _("Normalized GMROI = min(1.70 / 3.0, 1.0) * 100 = 56.7. Normalized Velocity = min(28.0 / 5.0, 1.0) * 100 = 100.0. Score = (0.6 * 56.7) + (0.4 * 100.0) = 74.0"),
                "interpretation": _("A single unified ranking to compare SKU efficiency across different categories and items.")
            }
        ],
        "classification_rules": [
            {
                "category": "Star (Core SKU)",
                "velocity": ">= star_velocity_threshold (Default 1.0/wk)",
                "gmroi": ">= 2.0 (200%)",
                "action": ACTION_INCREASE_STOCK,
                "description": _("High margin and high volume items. Ensure maximum stock availability.")
            },
            {
                "category": "Cash Cow",
                "velocity": "< star_velocity_threshold",
                "gmroi": ">= 2.0 (200%)",
                "action": ACTION_MAINTAIN,
                "description": _("High margin but low volume. Maintain steady inventory levels.")
            },
            {
                "category": "Underperformer",
                "velocity": ">= star_velocity_threshold",
                "gmroi": "< 2.0 (200%)",
                "action": ACTION_IMPROVE_MARGIN,
                "description": _("Low margin but high volume. Negotiate better buying rates or increase selling price.")
            },
            {
                "category": "Slow Mover",
                "velocity": "< star_velocity_threshold",
                "gmroi": "< 2.0 (200%)",
                "action": ACTION_LIQUIDATE,
                "description": _("Low margin and low volume. Liquidate excess stock or rationalize SKU from catalog.")
            },
            {
                "category": "Stockout Winner",
                "velocity": "Any",
                "gmroi": "Depleted (Stock <= 0 & Margin > 0)",
                "action": ACTION_REPLENISH_URGENT,
                "description": _("High-demand items currently out of stock. Replenish immediately to capture demand.")
            }
        ],
        "confidence_levels": [
            {
                "level": "High",
                "criteria": _("Sales Qty >= 20 and Transaction Count >= 5"),
                "description": _("Indicates highly reliable historical demand trends.")
            },
            {
                "level": "Medium",
                "criteria": _("Sales Qty > 0 and Transaction Count > 0 (excluding High)"),
                "description": _("Moderate reliability. The SKU has transaction history but limited volume.")
            },
            {
                "level": "Low",
                "criteria": _("No sales or transaction history"),
                "description": _("Low reliability. The metrics are mostly based on opening stock or standard rates without sales validation.")
            }
        ],
        "data_quality_warnings": [
            {
                "warning": "Cost Data Missing",
                "trigger": _("Item valuation rate and standard rate are both zero"),
                "action": _("Update the item cost in Item master or purchase transaction to ensure accurate margin calculations.")
            },
            {
                "warning": "Using Fallback Selling Price",
                "trigger": _("No sales invoices found for the item during the period"),
                "action": _("The system uses Item standard selling price list or markup rates as a fallback realized price.")
            },
            {
                "warning": "Inventory Adjustment Required",
                "trigger": _("Current stock balance in Inventory Visibility Layer is negative"),
                "action": _("A stock reconciliation or transaction correction is required to fix the negative balance.")
            }
        ],
        "interpretation_guide": [
            {
                "title": _("Star (Core SKU)"),
                "guidance": _("High margin and high volume. Focus on maximizing stock availability, reducing reorder lead times, and giving them priority placement in warehouses.")
            },
            {
                "title": _("Cash Cow"),
                "guidance": _("High margin but low volume. Maintain a steady stock level to capture profit but avoid over-ordering, as velocity is slow.")
            },
            {
                "title": _("Underperformer"),
                "guidance": _("Low margin but high volume. Focus on improving gross margin by negotiating bulk discounts with vendors or increasing selling prices.")
            },
            {
                "title": _("Slow Mover"),
                "guidance": _("Low margin and low volume. Avoid replenishment. Run promotions, bundle deals, or liquidation campaigns to recover locked capital.")
            },
            {
                "title": _("Stockout Winner"),
                "guidance": _("Out of stock but has active demand. Place replenishment orders immediately to prevent lost sales and capture active market demand.")
            }
        ],
        "faqs": [
            {
                "question": _("Why is my GMROI shown as None / DEPLETED?"),
                "answer": _("If the current stock balance of a SKU is zero or negative, the inventory value is zero. Dividing gross margin by zero is mathematically undefined. If the item has sales history during this period, it is classified as a 'Stockout Winner' with GMROI set to None.")
            },
            {
                "question": _("What timespan is used for calculations?"),
                "answer": _("By default, the dashboard calculates velocity and margin metrics over a trailing 30-day window. You can change this period in the dashboard filters or system settings.")
            },
            {
                "question": _("How is the Normalized GMROI calculated?"),
                "answer": _("To prevent extreme GMROI values from distorting the composite score, GMROI is normalized on a scale from 0 to 100, where a GMROI of 3.0 (300%) or above receives the maximum score of 100.")
            }
        ],
        "about": _(
            "This analytical framework is part of SMRITI Retail OS. "
            "Designed by Jawahar R. Mallah, Founder – AITDL (AI Technology & Development Lab). "
            "Built from practical business operations, inventory management experience, "
            "retail workflows, implementation learnings, and real-world business requirements."
        )
    }
