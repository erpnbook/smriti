# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/optimization_service.py
# @description: Network rebalancing optimization service for SMRITI PDT.
#               Evaluates excess stock across PSA network and recommends
#               economically beneficial inter-PSA transfers.
#
#               OPTIMIZATION SCOPE (v1):
#               This service solves the single-source optimization problem:
#               "Find the best individual source for a given transfer need."
#               Multi-source network optimization (combining multiple partial
#               sources) is reserved for PDT v2.
#
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.5
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.balance_engine import get_party_balance, get_reorder_recommendation

def optimize_network_transfer(company, target_psa, item_code, current_stock):
    """
    Evaluates other outlets for excess stock and recommends a transfer if the
    Transfer Benefit Score is positive.
    
    Formula:
        Transfer Benefit Score = (Item Price - Freight Cost - Transit Delay Penalty) * Transfer Qty
        
    Zone Costs:
        - Same zone: Freight = ₹6.0, Delay Penalty = ₹5.0
        - Different zone: Freight = ₹18.0, Delay Penalty = ₹20.0
    """
    # 1. Determine target's needed quantity & item price
    reco = get_reorder_recommendation(company, target_psa, item_code)
    needed_qty = reco.get("recommended_qty", 0.0)
    if needed_qty <= 0.0:
        return {
            "transfer_benefit_score": 0.0,
            "recommended_transfer_source": None,
            "recommended_transfer_qty": 0.0,
            "recommendation_type": "none",
            "reason_codes": "",
            "recommendation_reason": "Stock level is healthy or target cap is met."
        }

    # Fetch item valuation or standard selling rate
    item_rate = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate")
    if not item_rate:
        item_rate = frappe.db.get_value("Item", item_code, "valuation_rate") or 100.0
    item_rate = float(item_rate)

    # 2. Fetch target PSA's zone
    target_zone = frappe.db.get_value("SMRITI Party Stock Account", target_psa, "zone") or "West"

    # 3. Find candidates (all active PSAs for this company, excluding target)
    candidates = frappe.get_all(
        "SMRITI Party Stock Account",
        filters={"company": company, "name": ["!=", target_psa], "active": 1},
        fields=["name", "zone", "location_name"]
    )

    best_source = None
    best_qty = 0.0
    best_score = -999999.0
    best_freight = 0.0
    best_delay = 0.0

    for c in candidates:
        source_psa = c.name
        source_zone = c.zone or "West"
        
        # Get candidate's stock level & safety stock
        source_stock = get_party_balance(source_psa, item_code)
        
        # Safety stock buffer calculation
        safety_stock = 0.0
        rule = frappe.db.get_value(
            "SMRITI PSV Reorder Rule",
            {"company": company, "party_stock_account": source_psa, "item_variant": item_code, "active": 1},
            "safety_stock"
        )
        if rule:
            safety_stock = float(rule)
        else:
            # Fallback to group rule or global default
            settings = frappe.get_cached_doc("SMRITI PSV Settings") if frappe.db.exists("DocType", "SMRITI PSV Settings") else None
            safety_stock = float(settings.default_safety_stock or 0.0) if settings else 0.0

        # Excess stock is stock above safety buffer
        excess_qty = max(0.0, source_stock - safety_stock)
        if excess_qty <= 0.0:
            continue  # No excess stock to transfer
            
        # Determine transit/freight cost per unit
        if source_zone == target_zone:
            freight = 6.0
            delay = 5.0
        else:
            freight = 18.0
            delay = 20.0
            
        transfer_qty = min(needed_qty, excess_qty)
        
        # Economic score: Benefit of avoiding stockout (priced at item value) minus shipping friction
        unit_benefit = item_rate - freight - delay
        benefit_score = unit_benefit * transfer_qty
        
        if benefit_score > best_score:
            best_score = benefit_score
            best_source = source_psa
            best_qty = transfer_qty
            best_freight = freight
            best_delay = delay

    # 4. Final recommendation criteria
    if best_source and best_score > 0.0:
        source_name = frappe.db.get_value("SMRITI Party Stock Account", best_source, "location_name")
        target_name = frappe.db.get_value("SMRITI Party Stock Account", target_psa, "location_name")
        reason_codes = "EXCESS_WOC_AT_SOURCE,POSITIVE_TRANSFER_BENEFIT"
        if reco.get("priority") == "Critical":
            reason_codes += ",STOCKOUT_RISK"
            
        reason = (
            f"Recommended inter-PSA transfer of {int(best_qty)} units from {source_name} to {target_name}. "
            f"Net economic benefit is estimated at ₹{int(best_score)} (Fares: ₹{int(best_freight)}/unit, Delay Penalty: ₹{int(best_delay)}/unit)."
        )
        return {
            "transfer_benefit_score": round(best_score, 2),
            "recommended_transfer_source": best_source,
            "recommended_transfer_qty": best_qty,
            "recommendation_type": "TRANSFER",
            "reason_codes": reason_codes,
            "recommendation_reason": reason
        }
    else:
        # If no economic transfer found, suggest new procurement
        reason_codes = "NEW_PROCUREMENT_REQUIRED"
        if needed_qty > 0.0:
            reason_codes += ",STOCKOUT_RISK"
            reason = (
                f"No cost-effective network transfer option exists. "
                f"New procurement of {int(needed_qty)} units is recommended to prevent stockout."
            )
            return {
                "transfer_benefit_score": 0.0,
                "recommended_transfer_source": None,
                "recommended_transfer_qty": 0.0,
                "recommendation_type": "PURCHASE",
                "reason_codes": reason_codes,
                "recommendation_reason": reason
            }
        else:
            return {
                "transfer_benefit_score": 0.0,
                "recommended_transfer_source": None,
                "recommended_transfer_qty": 0.0,
                "recommendation_type": "none",
                "reason_codes": "",
                "recommendation_reason": "Stock level is healthy."
            }
