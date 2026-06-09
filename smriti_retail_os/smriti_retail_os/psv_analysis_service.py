# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_analysis_service.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe

def get_broken_sizes(customer: str):
    """
    Identifies styles where total stock > 0, but core sizes = 0.
    Returns: list of dicts {"style": "Sneaker-X", "stranded_qty": 15, "missing_core": "7,8"}
    """
    if not customer:
        return []

    # 1. Fetch all active rules for this channel
    rules = frappe.get_all(
        "PSV Reorder Rule",
        filters={"customer": customer, "active": 1},
        fields=["item_template", "core_sizes"]
    )

    if not rules:
        return []

    results = []

    # 2. Iterate through rules and check the high-speed Balance table
    for rule in rules:
        core_sizes = [s.strip() for s in rule.core_sizes.split(",") if s.strip()]
        if not core_sizes:
            continue

        # We assume the Item Master is structured where variant item_codes are e.g., 'TEMPLATE-SIZE'
        # Or, we fetch all variants for the template
        variants = frappe.get_all(
            "Item",
            filters={"variant_of": rule.item_template},
            fields=["name"]
        )
        variant_codes = [v.name for v in variants]

        if not variant_codes:
            continue

        # Query Balance table for all variants of this style
        balances = frappe.get_all(
            "PSV Balance",
            filters={
                "customer": customer,
                "item_code": ["in", variant_codes],
                "qty": [">", 0]
            },
            fields=["item_code", "qty"]
        )

        if not balances:
            continue # Total stock is 0, so it's not "stranded", it's just sold out.

        total_qty = sum(b.qty for b in balances)
        
        # Determine missing core sizes
        stock_map = {b.item_code: b.qty for b in balances}
        
        missing_core = []
        for cs in core_sizes:
            # We need to map the "core size" string (e.g. "8") to the actual variant code (e.g. "SNK-01-8")
            # This logic depends on exact Item Naming conventions. Assuming exact variant code match or suffix match.
            found = False
            for b_code in stock_map.keys():
                if b_code.endswith(f"-{cs}") or b_code == cs:
                    found = True
                    break
            
            if not found:
                missing_core.append(cs)

        # If we have stranded stock but are missing core sizes, flag it
        if total_qty > 0 and missing_core:
            results.append({
                "style": rule.item_template,
                "stranded_qty": total_qty,
                "missing_core": ", ".join(missing_core)
            })

    return results

def generate_reorder_suggestions(customer: str):
    """
    Calculates required replenishments based on PSV Reorder Rules and current balances.
    Returns: list of dicts {"item_code": "SNK-01-8", "current_qty": 2, "suggested_qty": 8, "priority": "High"}
    """
    if not customer:
        return []

    rules = frappe.get_all(
        "PSV Reorder Rule",
        filters={"customer": customer, "active": 1},
        fields=["item_template", "target_qty", "core_sizes"]
    )

    suggestions = []

    for rule in rules:
        variants = frappe.get_all(
            "Item",
            filters={"variant_of": rule.item_template},
            fields=["name"]
        )
        
        for variant in variants:
            current_balance = frappe.db.get_value(
                "PSV Balance", 
                {"customer": customer, "item_code": variant.name}, 
                "qty"
            ) or 0.0

            if current_balance < rule.target_qty:
                suggested_qty = rule.target_qty - current_balance
                
                # Determine Priority
                core_sizes = [s.strip() for s in rule.core_sizes.split(",") if s.strip()]
                is_core = any(variant.name.endswith(f"-{cs}") or variant.name == cs for cs in core_sizes)
                priority = "High" if (is_core and current_balance == 0) else "Medium"

                suggestions.append({
                    "item_code": variant.name,
                    "current_qty": current_balance,
                    "target_qty": rule.target_qty,
                    "suggested_qty": suggested_qty,
                    "priority": priority
                })

    # Sort high priority first
    suggestions.sort(key=lambda x: 0 if x["priority"] == "High" else 1)
    
    return suggestions
