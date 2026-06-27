# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/pdt_service.py
# @description: Main coordinator service for SMRITI Product Twin (PDT) builds.
#               Calculates SKU analytics, health scores, dead stock probability,
#               network transfer optimization, and variant curve health.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.2.15
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
import time
from frappe.utils import now_datetime, getdate, today, add_days
from smriti_retail_os.balance_engine import get_party_balance
from smriti_retail_os.services.forecasting_service import (
    calculate_weekly_velocity_stats,
    calculate_weeks_of_cover,
    calculate_predicted_stockout_date
)
from smriti_retail_os.services.optimization_service import optimize_network_transfer
from smriti_retail_os.services.twin_quality_service import evaluate_twin_quality, evaluate_variant_curve

def _get_rebuild_lock_key(company, party_stock_account, item_code):
    return f"pdt_rebuild:{company}:{party_stock_account}:{item_code}"

def _get_redis_cache_key(company, party_stock_account, item_code):
    return f"smriti:pdt:{company}:{party_stock_account}:{item_code}"

def enqueue_rebuild_twin_cache(company, party_stock_account, item_code, source_event="FULL_REBUILD"):
    """
    Checks rebuild lock to prevent queue storms. If lock does not exist, sets lock and enqueues job.
    """
    if not company or not party_stock_account or not item_code:
        return
        
    lock_key = _get_rebuild_lock_key(company, party_stock_account, item_code)
    try:
        # Check if already locked in queue
        if frappe.cache().get_value(lock_key):
            return  # Lock exists — skip to prevent queue storm
        
        # Set lock with 5 minutes expiry
        frappe.cache().set_value(lock_key, 1, expires_in_sec=300)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SMRITI: Exception in services/pdt_service.py")
        
    frappe.enqueue(
        "smriti_retail_os.services.pdt_service.rebuild_twin_cache",
        queue="long",
        company=company,
        party_stock_account=party_stock_account,
        item_code=item_code,
        source_event=source_event,
        enqueue_after_commit=True
    )

def rebuild_twin_cache(company, party_stock_account=None, item_code=None, source_event="FULL_REBUILD"):
    """
    Calculates Product Twin metrics and updates SMRITI SKU Twin database and Redis cache.
    Rebuilds target inputs or processes full database sweep.
    """
    start_time = time.time()
    
    # 1. Handle full sweep vs delta rebuild targets
    if not party_stock_account or not item_code:
        # Fetch all active PSAs for this company
        psas = frappe.get_all(
            "SMRITI Party Stock Account",
            filters={"company": company, "active": 1},
            fields=["name"]
        )
        for p in psas:
            # Fetch all items with ledger activity in this PSA
            items = frappe.db.sql("""
                SELECT DISTINCT item_code 
                FROM `tabSMRITI Party Stock Ledger Entry`
                WHERE party_stock_account = %s
            """, (p.name,), as_dict=True)
            for itm in items:
                rebuild_twin_cache(company, p.name, itm.item_code, source_event)
        return

    try:
        # 2. Retrieve inventory & forecast stats
        current_stock = get_party_balance(party_stock_account, item_code)
        
        stats = calculate_weekly_velocity_stats(company, party_stock_account, item_code)
        weekly_velocity = stats["weekly_velocity"]
        
        weeks_of_cover = calculate_weeks_of_cover(current_stock, weekly_velocity)
        predicted_stockout = calculate_predicted_stockout_date(current_stock, weekly_velocity)
        
        # 3. Calculate Dead Stock metrics
        # Fetch last sale date
        last_sale = frappe.db.sql("""
            SELECT MAX(posting_datetime)
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s
              AND item_code = %s
              AND qty < 0
        """, (party_stock_account, item_code))
        
        if last_sale and last_sale[0][0]:
            no_sale_days = (getdate(today()) - getdate(last_sale[0][0])).days
        else:
            no_sale_days = 90.0
            
        # Fetch first receipt date
        first_receipt = frappe.db.sql("""
            SELECT MIN(posting_datetime)
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s
              AND item_code = %s
              AND qty > 0
        """, (party_stock_account, item_code))
        
        if first_receipt and first_receipt[0][0]:
            aging_days = (getdate(today()) - getdate(first_receipt[0][0])).days
        else:
            aging_days = 90.0
            
        # Sales lookback total
        sales_qty = float(frappe.db.sql("""
            SELECT COALESCE(SUM(ABS(qty)), 0)
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s
              AND item_code = %s
              AND posting_datetime >= %s
              AND qty < 0
        """, (party_stock_account, item_code, add_days(today(), -28)))[0][0] or 0.0)
        
        # Dead Stock Score Formula: No Sale Days (40% weight) + Aging Days (30% weight) + Turnover + Coverage
        turnover_score = max(0.0, 30.0 - sales_qty)
        dead_stock_score = (no_sale_days * 0.4) + (aging_days * 0.3) + turnover_score + (weeks_of_cover * 2.0)
        dead_stock_score = round(min(100.0, max(0.0, dead_stock_score)), 2)
        
        if dead_stock_score > 75.0:
            dead_stock_prob = "High"
        elif dead_stock_score > 45.0:
            dead_stock_prob = "Medium"
        else:
            dead_stock_prob = "Low"
            
        # 4. Optimize network transfer & variant curves
        opt = optimize_network_transfer(company, party_stock_account, item_code, current_stock)
        curve = evaluate_variant_curve(item_code, party_stock_account)
        quality = evaluate_twin_quality(party_stock_account, item_code)
        
        # 5. Determine State Machine
        if current_stock <= 0.0:
            twin_state = "Stockout"
        elif dead_stock_prob == "High":
            twin_state = "Dead Stock"
        elif weeks_of_cover > 12.0:
            twin_state = "Overstock"
        elif weeks_of_cover < 2.0:
            twin_state = "Critical"
        elif weeks_of_cover < 4.0:
            twin_state = "Replenish Soon"
        elif weeks_of_cover < 6.0:
            twin_state = "Monitor"
        else:
            twin_state = "Healthy"
            
        # Recalculate SLA and Metadata
        rebuild_duration_ms = int((time.time() - start_time) * 1000)
        redis_key = _get_redis_cache_key(company, party_stock_account, item_code)
        
        metadata = {
            "cache_version": "PDT-2.0.0",
            "builder_version": "2.0.3",
            "rebuild_duration_ms": rebuild_duration_ms,
            "redis_key": redis_key,
            "source_event": source_event
        }
        
        # 6. Database Persistence (Read Model Write)
        twin_name = frappe.db.get_value(
            "SMRITI SKU Twin",
            {"company": company, "party_stock_account": party_stock_account, "item_code": item_code}
        )
        
        vals = {
            "doctype": "SMRITI SKU Twin",
            "company": company,
            "party_stock_account": party_stock_account,
            "item_code": item_code,
            "current_stock": current_stock,
            "weekly_velocity": weekly_velocity,
            "velocity_confidence": stats["velocity_confidence"],
            "velocity_std_dev": stats["velocity_std_dev"],
            "weeks_of_cover": weeks_of_cover,
            "dead_stock_score": dead_stock_score,
            "dead_stock_probability": dead_stock_prob,
            "reorder_suggestion": opt.get("recommended_transfer_qty") or 0.0,
            "transfer_benefit_score": opt.get("transfer_benefit_score") or 0.0,
            "recommended_transfer_source": opt.get("recommended_transfer_source"),
            "recommended_transfer_qty": opt.get("recommended_transfer_qty") or 0.0,
            "twin_state": twin_state,
            "forecast_version": "PDT-2.0.1",
            "forecast_date": today(),
            "forecast_model": "EMA",
            "forecast_parameters": json.dumps(stats["forecast_parameters"]),
            "recommendation_type": opt.get("recommendation_type", "none"),
            "reason_codes": opt.get("reason_codes", ""),
            "recommendation_reason": opt.get("recommendation_reason", ""),
            "last_recalculated": now_datetime(),
            "freshness_status": "Fresh",
            "twin_quality_score": quality["twin_quality_score"],
            "twin_quality_status": quality["twin_quality_status"],
            "variant_curve_status": curve["variant_curve_status"],
            "missing_sizes": curve["missing_sizes"],
            "cache_version": "PDT-2.0.0",
            "next_recalculation_due": add_days(now_datetime(), 1), # Recalculate daily
            "source_event": source_event,
            "seasonality_factor": 1.0,
            "supplier_lead_days": 7,
            "predicted_stockout_date": predicted_stockout,
            "metadata_json": json.dumps(metadata)
        }
        
        if twin_name:
            doc = frappe.get_doc("SMRITI SKU Twin", twin_name)
            doc.update(vals)
            doc.flags.ignore_permissions = True
            doc.save()
        else:
            doc = frappe.get_doc(vals)
            doc.flags.ignore_permissions = True
            doc.insert()
            
        # 7. Redis Cache Acceleration Layer Write
        try:
            frappe.cache().set_value(redis_key, doc.as_dict(), expires_in_sec=3600)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "SMRITI: Exception in services/pdt_service.py")
            
    except Exception as e:
        frappe.log_error(f"PDT Rebuild Failure for {party_stock_account} / {item_code}: {str(e)}", "SMRITI PDT Error")
        
    finally:
        # 8. Release Rebuild Lock
        # Infrastructure cleanup — failure here must NOT propagate.
        # The lock will expire naturally via Redis TTL (300s) if delete fails.
        lock_key = _get_rebuild_lock_key(company, party_stock_account, item_code)
        try:
            frappe.cache().delete_key(lock_key)
        except Exception:
            frappe.logger().debug(f"PDT: lock release failed for {lock_key} — will expire via TTL")


# ─── Hook Handlers ───────────────────────────────────────────────────────────

def on_delivery_note_submit(doc, method=None):
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return
    for item in doc.items:
        if item.item_code:
            enqueue_rebuild_twin_cache(doc.company, psa, item.item_code, "DELIVERY_NOTE")

def on_delivery_note_cancel(doc, method=None):
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return
    for item in doc.items:
        if item.item_code:
            enqueue_rebuild_twin_cache(doc.company, psa, item.item_code, "DELIVERY_NOTE")

def on_sales_upload_submit(doc, method=None):
    psa = doc.get("party_stock_account")
    if not psa:
        return
    for item in doc.items:
        if item.item_code:
            enqueue_rebuild_twin_cache(doc.company, psa, item.item_code, "SALES_UPLOAD")

def on_physical_snapshot_submit(doc, method=None):
    psa = doc.get("party_stock_account")
    if not psa:
        return
    for item in doc.items:
        if item.item_code:
            enqueue_rebuild_twin_cache(doc.company, psa, item.item_code, "SNAPSHOT")
