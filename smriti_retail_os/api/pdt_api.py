# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/pdt_api.py
# @description: REST API endpoints for SMRITI Product Twin (PDT) operations.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#


import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
import json
from frappe.utils import now_datetime, get_datetime

@frappe.whitelist()
def get_twin_status(party_stock_account, item_code):
    """
    Exposes twin state for a PSA/Item pair.
    Uses Redis cache lookup, falling back to MariaDB and auto-initializing if missing.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    company = smriti.db.get("SMRITI Party Stock Account", party_stock_account, "company")
    if not company:
        frappe.throw(frappe._("Party Stock Account {0} not found or has no Company assigned.").format(party_stock_account))

    redis_key = f"smriti:pdt:{company}:{party_stock_account}:{item_code}"
    
    # 1. Try Redis cache lookup first
    try:
        cached_data = frappe.cache().get_value(redis_key)
        if cached_data:
            # Check SLA freshness
            last_recalc = get_datetime(cached_data.get("last_recalculated"))
            elapsed_hours = (get_datetime(now_datetime()) - last_recalc).total_seconds() / 3600.0
            
            if elapsed_hours > 24.0:
                cached_data["freshness_status"] = "Stale"
            elif elapsed_hours > 1.0:
                cached_data["freshness_status"] = "Aging"
            else:
                cached_data["freshness_status"] = "Fresh"
                
            return cached_data
    except Exception:
        smriti.errors.log_error(frappe.get_traceback(), "SMRITI: Exception in api/pdt_api.py")

    # 2. Query MariaDB SMRITI SKU Twin table
    twin_data = smriti.db.get(
        "SMRITI SKU Twin",
        {"company": company, "party_stock_account": party_stock_account, "item_code": item_code},
        "*"
    )

    if not twin_data:
        # 3. Auto-initialize twin on demand
        from smriti_retail_os.services.pdt_service import rebuild_twin_cache
        rebuild_twin_cache(company, party_stock_account, item_code, "FULL_REBUILD")
        
        twin_data = smriti.db.get(
            "SMRITI SKU Twin",
            {"company": company, "party_stock_account": party_stock_account, "item_code": item_code},
            "*"
        )

    if twin_data:
        # Convert row tuple or dict format if returned as dict
        if isinstance(twin_data, tuple):
            # If get_value returned a raw tuple, convert using meta structure
            meta = frappe.get_meta("SMRITI SKU Twin")
            fields = [f.fieldname for f in meta.fields] + ["name", "owner", "creation", "modified", "modified_by", "docstatus"]
            twin_dict = dict(zip(fields, twin_data))
        else:
            twin_dict = dict(twin_data)
            
        # Update SLA freshness
        last_recalc = get_datetime(twin_dict.get("last_recalculated"))
        elapsed_hours = (get_datetime(now_datetime()) - last_recalc).total_seconds() / 3600.0
        
        if elapsed_hours > 24.0:
            twin_dict["freshness_status"] = "Stale"
        elif elapsed_hours > 1.0:
            twin_dict["freshness_status"] = "Aging"
        else:
            twin_dict["freshness_status"] = "Fresh"
            
        # Seed cache
        try:
            frappe.cache().set_value(redis_key, twin_dict, expires_in_sec=3600)
        except Exception:
            smriti.errors.log_error(frappe.get_traceback(), "SMRITI: Exception in api/pdt_api.py")
            
        return twin_dict

    frappe.throw(frappe._("Product Twin could not be calculated for {0} and {1}.").format(party_stock_account, item_code))


@frappe.whitelist()
def trigger_rebuild(party_stock_account, item_code):
    """
    Triggers a synchronous rebuild of the twin record for real-time UI updates.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    company = smriti.db.get("SMRITI Party Stock Account", party_stock_account, "company")
    if not company:
        frappe.throw(frappe._("Party Stock Account {0} not found.").format(party_stock_account))

    from smriti_retail_os.services.pdt_service import rebuild_twin_cache
    rebuild_twin_cache(company, party_stock_account, item_code, "FULL_REBUILD")

    return {"status": "success", "message": "Product Twin recalculated."}


@frappe.whitelist()
def run_simulation(simulation_config):
    """
    Runs scenario sandbox simulation based on pricing, promotions, and lead overrides.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if isinstance(simulation_config, str):
        try:
            config = json.loads(simulation_config)
        except Exception:
            frappe.throw(frappe._("Invalid JSON configuration structure."))
    else:
        config = simulation_config

    from smriti_retail_os.services.simulation_service import run_sandbox_simulation
    results = run_sandbox_simulation(config)
    
    return results


@frappe.whitelist()
def get_pdt_dashboard_list(filters=None):
    """
    Returns list of all SMRITI SKU Twin records matching filters.
    Includes summary metrics for the header cards.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])
    
    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except Exception:
            filters = {}
    elif not filters:
        filters = {}
        
    db_filters = {}
    if filters.get("party_stock_account"):
        db_filters["party_stock_account"] = filters.get("party_stock_account")
    if filters.get("twin_state"):
        db_filters["twin_state"] = filters.get("twin_state")
    if filters.get("item_code"):
        db_filters["item_code"] = ["like", f"%{filters.get('item_code')}%"]
        
    # Read twins
    twins = smriti.db.get_list(
        "SMRITI SKU Twin",
        filters=db_filters,
        fields=[
            "name", "company", "party_stock_account", "item_code", "current_stock",
            "weekly_velocity", "weeks_of_cover", "twin_state", "reorder_suggestion",
            "recommended_transfer_source", "recommended_transfer_qty", "transfer_benefit_score",
            "predicted_stockout_date", "twin_quality_score", "twin_quality_status",
            "variant_curve_status", "last_recalculated", "freshness_status"
        ],
        order_by="weeks_of_cover asc"
    )
    
    # Calculate stats across ALL twins (unfiltered for accurate dashboard counters)
    all_twins = smriti.db.get_list("SMRITI SKU Twin", fields=["twin_state"])
    stats = {
        "total": len(all_twins),
        "healthy": sum(1 for t in all_twins if t.twin_state == "Healthy"),
        "warning": sum(1 for t in all_twins if t.twin_state in ("Warning", "Monitor", "Replenish Soon")),
        "critical": sum(1 for t in all_twins if t.twin_state == "Critical"),
        "stockout": sum(1 for t in all_twins if t.twin_state == "Stockout"),
        "dead_stock": sum(1 for t in all_twins if t.twin_state == "Dead Stock"),
        "overstock": sum(1 for t in all_twins if t.twin_state == "Overstock")
    }
    
    # Fetch active PSAs for filtering dropdowns
    psas = smriti.db.get_list("SMRITI Party Stock Account", filters={"active": 1}, fields=["name", "customer", "location_name"])
    
    return {
        "twins": twins,
        "stats": stats,
        "psas": psas
    }

