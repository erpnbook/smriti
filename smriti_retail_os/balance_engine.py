# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/balance_engine.py
# @description: Stock Balance & Reorder Intelligence Engine for SMRITI PSV.
#               PERF-001: Redis-backed balance cache added. Cache is invalidated
#               automatically on every ledger write via ledger_engine.py.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

# ─── REDIS CACHE CONFIGURATION ───────────────────────────────────────────────
# Balance cache TTL in seconds. 60s is conservative: if Redis invalidation works
# correctly (see ledger_engine.py), this TTL is just a safety net.
_BALANCE_CACHE_TTL = 60


def _cache_key_single(party_stock_account: str, item_code: str) -> str:
    """Cache key for a single (PSA, item) balance."""
    return f"psv:bal:{party_stock_account}:{item_code}"


def _cache_key_bulk(party_stock_account: str) -> str:
    """Cache key for all items in a PSA (used by get_bulk_party_balances)."""
    return f"psv:balbulk:{party_stock_account}"


def invalidate_balance_cache(party_stock_account: str, item_code: str = None):
    """
    Called by ledger_engine.make_ledger_entry() after every successful ledger write.
    Invalidates both the single-item cache and the bulk PSA cache.

    Args:
        party_stock_account: PSA name (always required)
        item_code:           If provided, also invalidates the single-item key.
    """
    try:
        cache = frappe.cache()
        if item_code:
            cache.delete_key(_cache_key_single(party_stock_account, item_code))
        cache.delete_key(_cache_key_bulk(party_stock_account))
    except Exception:
        # Cache invalidation failure must NEVER propagate and break the ledger write.
        # Log silently; the short TTL (60s) is the safety net.
        frappe.logger("psv_cache").warning(
            f"PSV balance cache invalidation failed for PSA={party_stock_account} item={item_code}"
        )


# ─── BALANCE QUERIES ──────────────────────────────────────────────────────────

def get_party_balance(party_stock_account: str, item_code: str,
                      posting_datetime=None) -> float:
    """
    Returns the current available shadow balance for a given SKU at a location.

    PERF-001: For real-time queries (no posting_datetime), checks Redis first.
    Historical queries (posting_datetime provided) always bypass cache to ensure
    point-in-time accuracy.

    Args:
        party_stock_account: PSA name
        item_code:           SKU / Item code
        posting_datetime:    If set, returns the historical balance at that datetime
    """
    # Historical queries must not use cache (they could return wrong point-in-time data)
    if posting_datetime:
        return _query_single_balance(party_stock_account, item_code, posting_datetime)

    # Real-time query: try cache first
    cache_key = _cache_key_single(party_stock_account, item_code)
    try:
        cached = frappe.cache().get_value(cache_key)
        if cached is not None:
            return float(cached)
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in balance_engine.py:80: {sys.exc_info()[1]}")

    balance = _query_single_balance(party_stock_account, item_code)

    # Store in cache for next request
    try:
        frappe.cache().set_value(cache_key, balance, expires_in_sec=_BALANCE_CACHE_TTL)
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in balance_engine.py:88: {sys.exc_info()[1]}")

    return balance


def _query_single_balance(party_stock_account: str, item_code: str,
                           posting_datetime=None) -> float:
    """Direct DB query — no caching. Used by get_party_balance and historical lookups."""
    use_new = frappe.db.exists("PSV Ledger Entry", {"channel_partner": party_stock_account})
    if use_new:
        query = """
            SELECT SUM(qty)
            FROM `tabPSV Ledger Entry`
            WHERE channel_partner = %s AND item_variant = %s
        """
    else:
        query = """
            SELECT SUM(qty)
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s AND item_code = %s
        """
    params = [party_stock_account, item_code]

    if posting_datetime:
        query += " AND posting_datetime <= %s"
        params.append(posting_datetime)

    result = frappe.db.sql(query, params)
    return float(result[0][0]) if result and result[0][0] is not None else 0.0


def get_bulk_party_balances(party_stock_account: str, item_codes=None) -> dict:
    """
    Returns a {item_code: balance} dict for a location in a single SQL round-trip.

    PERF-001: Full-PSA bulk results are cached when no item_codes filter is applied.
    Filtered queries (specific item_codes) bypass cache to avoid returning stale subset.
    """
    # Only cache the unfiltered full-PSA bulk query
    use_cache = not item_codes
    cache_key = _cache_key_bulk(party_stock_account)

    if use_cache:
        try:
            cached = frappe.cache().get_value(cache_key)
            if cached is not None:
                return cached
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in balance_engine.py:136: {sys.exc_info()[1]}")

    result_dict = _query_bulk_balance(party_stock_account, item_codes)

    if use_cache:
        try:
            frappe.cache().set_value(cache_key, result_dict, expires_in_sec=_BALANCE_CACHE_TTL)
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in balance_engine.py:144: {sys.exc_info()[1]}")

    return result_dict


def _query_bulk_balance(party_stock_account: str, item_codes=None) -> dict:
    """Direct DB query for bulk balances — no caching."""
    use_new = frappe.db.exists("PSV Ledger Entry", {"channel_partner": party_stock_account})
    if use_new:
        query = """
            SELECT item_variant, SUM(qty)
            FROM `tabPSV Ledger Entry`
            WHERE channel_partner = %s
        """
    else:
        query = """
            SELECT item_code, SUM(qty)
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s
        """
    params = [party_stock_account]

    if item_codes:
        if use_new:
            query += " AND item_variant IN %s"
        else:
            query += " AND item_code IN %s"
        params.append(tuple(item_codes))

    if use_new:
        query += " GROUP BY item_variant"
    else:
        query += " GROUP BY item_code"

    result = frappe.db.sql(query, params, as_dict=False)
    return {r[0]: float(r[1]) for r in result}


def get_all_party_balances(company: str) -> list:
    """
    Returns a list of dicts with all non-zero balances across all PSAs for a company.
    Cross-PSA queries are NOT cached (scope too broad for safe TTL-based cache).
    """
    use_new = frappe.db.exists("PSV Ledger Entry", {"company": company})
    if use_new:
        results = frappe.db.sql("""
            SELECT
                psa.name as party_stock_account,
                psa.location_name,
                psa.zone,
                ple.item_variant as item_code,
                SUM(ple.qty) as balance
            FROM `tabPSV Ledger Entry` ple
            INNER JOIN `tabPSV Channel Partner` psa ON ple.channel_partner = psa.name
            WHERE psa.company = %s
            GROUP BY psa.name, ple.item_variant
            HAVING SUM(ple.qty) != 0
        """, (company,), as_dict=True)
    else:
        results = frappe.db.sql("""
            SELECT
                psa.name as party_stock_account,
                psa.location_name,
                psa.zone,
                ple.item_code,
                SUM(ple.qty) as balance
            FROM `tabSMRITI Party Stock Ledger Entry` ple
            INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
            WHERE psa.company = %s
            GROUP BY psa.name, ple.item_code
            HAVING SUM(ple.qty) != 0
        """, (company,), as_dict=True)

    for r in results:
        r["balance"] = float(r["balance"])
    return results


# ─── REORDER INTELLIGENCE ─────────────────────────────────────────────────────

def get_reorder_recommendation(company: str, party_stock_account: str,
                                item_code: str) -> dict:
    """
    V1.1 Reorder Intelligence API.

    Returns a dict with:
        current_balance, weekly_sale_avg, days_cover,
        reorder_level, recommended_qty, priority

    Priority Cascade for parameters:
        1. Variant-specific SMRITI PSV Reorder Rule (highest priority)
        2. Item Group-level SMRITI PSV Reorder Rule
        3. Global defaults from SMRITI PSV Settings (fallback)

    Formula:
        daily_sale = weekly_sale_avg / 7
        reorder_level = (lead_time_days × daily_sale) + safety_stock
        raw_need = max(0, reorder_level - current_balance)
        max_fillable = max(0, max_stock - current_balance)  # Max Stock cap
        recommended_qty = min(raw_need, max_fillable)
    """
    from frappe.utils import getdate, today, add_days

    # ─── Step 1: Get current balance (uses cache) ─────────────────────────
    current_balance = get_party_balance(party_stock_account, item_code)

    # ─── Step 2: Get reorder parameters via priority cascade ─────────────
    params = _get_reorder_params(company, party_stock_account, item_code)
    lead_time_days = params["lead_time_days"]
    safety_stock = params["safety_stock"]
    max_stock = params["max_stock"]

    # ─── Step 3: Calculate weekly sale average ───────────────────────────
    avg_weeks = _get_avg_weeks_lookback()
    cutoff_date = add_days(today(), -(avg_weeks * 7))

    weekly_sales_data = frappe.db.sql("""
        SELECT COALESCE(SUM(ABS(qty)), 0)
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE party_stock_account = %s
          AND item_code = %s
          AND voucher_type = 'Sales'
          AND posting_datetime >= %s
    """, (party_stock_account, item_code, cutoff_date))

    total_sold = float(weekly_sales_data[0][0]) if weekly_sales_data and weekly_sales_data[0][0] else 0.0

    # Count actual weeks of data available (minimum 1 to avoid division by zero)
    first_sale = frappe.db.sql("""
        SELECT MIN(posting_datetime)
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE party_stock_account = %s
          AND item_code = %s
          AND voucher_type = 'Sales'
          AND posting_datetime >= %s
    """, (party_stock_account, item_code, cutoff_date))

    if first_sale and first_sale[0][0]:
        actual_days = max(1, (getdate(today()) - getdate(first_sale[0][0])).days)
        actual_weeks = max(1, actual_days / 7.0)
    else:
        actual_weeks = avg_weeks  # No sales data — use configured window

    weekly_sale_avg = round(total_sold / actual_weeks, 2) if total_sold > 0 else 0.0

    # ─── Step 4: Calculate reorder metrics ───────────────────────────────
    daily_sale = weekly_sale_avg / 7.0

    # Days cover: how many days current stock will last
    if daily_sale > 0:
        days_cover = round(current_balance / daily_sale, 1)
    else:
        days_cover = 999.0 if current_balance > 0 else 0.0

    # Reorder level
    reorder_level = round((lead_time_days * daily_sale) + safety_stock, 2)

    # Recommended qty with Max Stock cap
    raw_need = max(0, reorder_level - current_balance)
    if max_stock and max_stock > 0:
        max_fillable = max(0, max_stock - current_balance)
        recommended_qty = round(min(raw_need, max_fillable), 2)
    else:
        recommended_qty = round(raw_need, 2)

    # ─── Step 5: Priority classification ─────────────────────────────────
    if current_balance <= 0 or days_cover < 3:
        priority = "Critical"
    elif days_cover < 7:
        priority = "High"
    elif days_cover < 14:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "current_balance": current_balance,
        "weekly_sale_avg": weekly_sale_avg,
        "days_cover": days_cover,
        "reorder_level": reorder_level,
        "recommended_qty": recommended_qty,
        "priority": priority
    }


def _get_reorder_params(company: str, party_stock_account: str,
                         item_code: str) -> dict:
    """
    Resolves reorder parameters using the three-level priority cascade:
    1. Variant-specific rule (highest priority)
    2. Item Group-level rule
    3. Global defaults from PSV Settings (fallback)
    """
    # Priority 1: Variant-specific rule
    variant_rule = frappe.db.get_value(
        "SMRITI PSV Reorder Rule",
        {"company": company, "party_stock_account": party_stock_account,
         "item_variant": item_code, "active": 1},
        ["lead_time_days", "safety_stock", "max_stock", "min_stock", "target_days_cover"],
        as_dict=True
    )
    if variant_rule:
        return {
            "lead_time_days": variant_rule.lead_time_days or 7,
            "safety_stock": variant_rule.safety_stock or 0,
            "max_stock": variant_rule.max_stock or 0,
        }

    # Priority 2: Item Group-level rule
    item_group = frappe.db.get_value("Item", item_code, "item_group")
    if item_group:
        group_rule = frappe.db.get_value(
            "SMRITI PSV Reorder Rule",
            {"company": company, "party_stock_account": party_stock_account,
             "item_group": item_group, "item_variant": ["is", "not set"], "active": 1},
            ["lead_time_days", "safety_stock", "max_stock", "min_stock", "target_days_cover"],
            as_dict=True
        )
        if group_rule:
            return {
                "lead_time_days": group_rule.lead_time_days or 7,
                "safety_stock": group_rule.safety_stock or 0,
                "max_stock": group_rule.max_stock or 0,
            }

    # Priority 3: Global defaults from PSV Settings
    settings = _get_psv_settings()
    return {
        "lead_time_days": settings.get("default_lead_time_days") or 7,
        "safety_stock": settings.get("default_safety_stock") or 0,
        "max_stock": 0,  # No global max stock cap
    }


def _get_avg_weeks_lookback() -> int:
    """Returns the configured number of weeks for weekly sale average calculation."""
    settings = _get_psv_settings()
    return settings.get("reorder_avg_weeks") or 4


def _get_psv_settings() -> dict:
    """Safely retrieves PSV Settings (single doctype). Returns empty dict if not configured."""
    try:
        if frappe.db.exists("DocType", "SMRITI PSV Settings"):
            return frappe.get_cached_doc("SMRITI PSV Settings").as_dict()
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in balance_engine.py:390: {sys.exc_info()[1]}")
    return {}
