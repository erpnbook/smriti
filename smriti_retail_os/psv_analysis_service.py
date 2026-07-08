# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_analysis_service.py
# @description: SMRITI Psv Analysis Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/smriti_retail_os/psv_analysis_service.py
# @description: Channel Stock analysis — broken size detection and reorder suggestions.
#               BUG-005 FIX: Was referencing non-existent DocTypes "PSV Reorder Rule"
#               and "PSV Balance". Now uses correct "SMRITI PSV Reorder Rule" and
#               queries SMRITI Party Stock Ledger Entry for live balances.
# @version: 1.8.6
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances


def _get_all_psas_for_customer(customer: str):
    """Returns list of active PSA names for a customer."""
    return smriti.db.get_list(
        "SMRITI Party Stock Account",
        filters={"customer": customer, "active": 1},
        fields=["name", "company"]
    )


def _get_customer_item_balance(customer: str, item_code: str) -> float:
    """Sums balance across all active PSAs for a customer and item."""
    psas = _get_all_psas_for_customer(customer)
    total = 0.0
    for psa in psas:
        total += get_party_balance(psa.name, item_code)
    return total


def _get_customer_all_balances(customer: str) -> dict:
    """Returns {item_code: qty} dict across all active PSAs for a customer."""
    psas = _get_all_psas_for_customer(customer)
    balances = {}
    for psa in psas:
        psa_bal = get_bulk_party_balances(psa.name)
        for item, qty in psa_bal.items():
            balances[item] = balances.get(item, 0.0) + qty
    return balances


def get_broken_sizes(customer: str):
    """
    Identifies styles where total stock > 0, but one or more core sizes = 0.

    Returns: list of dicts:
        {"style": "Sneaker-X", "stranded_qty": 15, "missing_core": "7,8"}

    BUG-005 FIX:
    - Old: smriti.db.get_list("PSV Reorder Rule", ...) — DocType does not exist
    - Old: smriti.db.get_list("PSV Balance", ...) — DocType does not exist
    - New: Uses SMRITI PSV Reorder Rule + live ledger balance via balance_engine
    """
    if not customer:
        return []

    # Fetch all active reorder rules for this customer's PSAs
    psas = _get_all_psas_for_customer(customer)
    if not psas:
        return []

    psa_names = [p.name for p in psas]

    rules = smriti.db.get_list(
        "SMRITI PSV Reorder Rule",
        filters={"party_stock_account": ["in", psa_names], "active": 1},
        fields=["item_variant", "item_group", "party_stock_account"]
    )

    if not rules:
        return []

    # Get all current balances for this customer (single bulk call)
    all_balances = _get_customer_all_balances(customer)

    results = []

    for rule in rules:
        if not rule.item_variant:
            continue  # Group-level rules don't carry variant-specific core size info

        # Find all item variants under the same template
        item_template = smriti.db.get("Item", rule.item_variant, "variant_of")
        if not item_template:
            continue

        variants = smriti.db.get_list(
            "Item",
            filters={"variant_of": item_template},
            fields=["name", "item_name"]
        )
        variant_codes = [v.name for v in variants]

        if not variant_codes:
            continue

        total_qty = sum(all_balances.get(code, 0.0) for code in variant_codes)

        if total_qty <= 0:
            continue  # Style is sold out — not stranded

        # Determine missing core sizes via attribute values
        # Look for variants with zero balance
        missing_core = [
            code for code in variant_codes
            if all_balances.get(code, 0.0) <= 0
        ]

        if missing_core:
            results.append({
                "style": item_template,
                "stranded_qty": total_qty,
                "missing_core": ", ".join(missing_core)
            })

    return results


def generate_reorder_suggestions(customer: str):
    """
    Calculates replenishment needs based on SMRITI PSV Reorder Rules and live balances.

    Returns: list of dicts:
        {"item_code": "SNK-01-8", "current_qty": 2, "suggested_qty": 8,
         "target_qty": 10, "priority": "High"}

    BUG-005 FIX:
    - Old: smriti.db.get_list("PSV Reorder Rule", ...) — DocType does not exist
    - Old: smriti.db.get("PSV Balance", ...) — DocType does not exist
    - New: Uses SMRITI PSV Reorder Rule + live ledger balance via balance_engine
    """
    if not customer:
        return []

    psas = _get_all_psas_for_customer(customer)
    if not psas:
        return []

    psa_names = [p.name for p in psas]

    # Fetch variant-level reorder rules for this customer's accounts
    rules = smriti.db.get_list(
        "SMRITI PSV Reorder Rule",
        filters={
            "party_stock_account": ["in", psa_names],
            "active": 1,
            "item_variant": ["is", "set"]
        },
        fields=["item_variant", "min_stock", "target_days_cover", "party_stock_account"]
    )

    # Build a per-PSA target from PSV settings as fallback
    settings = _get_psv_settings()
    default_safety_stock = settings.get("default_safety_stock", 0)

    # Get all current balances in one bulk call
    all_balances = _get_customer_all_balances(customer)

    suggestions = []

    for rule in rules:
        item_code = rule.item_variant
        current_balance = all_balances.get(item_code, 0.0)

        # Use min_stock as target if available, else use safety_stock fallback
        target_qty = rule.min_stock or default_safety_stock or 0

        if target_qty <= 0:
            continue

        if current_balance < target_qty:
            suggested_qty = target_qty - current_balance

            # Priority: High if zero stock, Medium if below target
            priority = "High" if current_balance <= 0 else "Medium"

            suggestions.append({
                "item_code": item_code,
                "current_qty": current_balance,
                "target_qty": target_qty,
                "suggested_qty": suggested_qty,
                "priority": priority
            })

    # Sort: High priority first, then by suggested_qty descending
    suggestions.sort(key=lambda x: (0 if x["priority"] == "High" else 1, -x["suggested_qty"]))

    return suggestions


def _get_psv_settings() -> dict:
    """Safely retrieves PSV Settings. Returns empty dict if not configured."""
    try:
        if smriti.db.exists("DocType", "SMRITI PSV Settings"):
            return smriti.documents.get("SMRITI PSV Settings").as_dict()
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in psv_analysis_service.py:208: {sys.exc_info()[1]}")
    return {}
