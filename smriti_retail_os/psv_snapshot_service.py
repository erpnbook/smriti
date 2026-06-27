# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_snapshot_service.py
# @description: SMRITI PSV Snapshot Service — landing cost resolution, inventory aging, and snapshot generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: Extracted from psv_service.py (Phase 4 remediation).
#       psv_service.py re-imports all public names for backward compatibility.
#

import frappe
from frappe import _
from frappe.utils import today, now_datetime, get_datetime


@frappe.whitelist()
def get_landing_cost(variant):
    """
    Resolves the landing cost (buying/valuation rate) for a variant using a fallback hierarchy:
    1. Variant Item: valuation_rate
    2. Variant Item: standard_rate
    3. Variant Item: Standard Buying Price from Item Price table
    4. Parent Template Item: valuation_rate (if variant_of is set)
    5. Parent Template Item: standard_rate
    6. Parent Template Item: Standard Buying Price from Item Price table
    7. 0.0 (fallback)
    """
    if not variant:
        return 0.0
        
    if not hasattr(frappe.local, "landing_cost_cache"):
        frappe.local.landing_cost_cache = {}
        
    if variant in frappe.local.landing_cost_cache:
        return frappe.local.landing_cost_cache[variant]
        
    cost = _get_landing_cost_from_db(variant)
    frappe.local.landing_cost_cache[variant] = cost
    return cost


def _get_landing_cost_from_db(variant):
    item_details = frappe.db.get_value(
        "Item", variant, ["valuation_rate", "standard_rate", "variant_of", "name"], as_dict=True
    )
    if not item_details:
        return 0.0
    
    if item_details.get("valuation_rate"):
        return float(item_details["valuation_rate"])
        
    if item_details.get("standard_rate"):
        return float(item_details["standard_rate"])
        
    buying_price = frappe.db.get_value(
        "Item Price", {"item_code": variant, "price_list": "Standard Buying"}, "price_list_rate"
    )
    if buying_price:
        return float(buying_price)
        
    parent_code = item_details.get("variant_of")
    if parent_code:
        parent_details = frappe.db.get_value(
            "Item", parent_code, ["valuation_rate", "standard_rate"], as_dict=True
        )
        if parent_details:
            if parent_details.get("valuation_rate"):
                return float(parent_details["valuation_rate"])
                
            if parent_details.get("standard_rate"):
                return float(parent_details["standard_rate"])
                
            parent_buying_price = frappe.db.get_value(
                "Item Price", {"item_code": parent_code, "price_list": "Standard Buying"}, "price_list_rate"
            )
            if parent_buying_price:
                return float(parent_buying_price)
                
    return 0.0


def calculate_aging_for_variant(partner, variant, current_qty, snapshot_date=None):
    """
    Allocates the current_qty to aging buckets (0-30, 31-60, 61-90, 91-180, 180+)
    using FIFO logic on positive ledger entries.
    """
    from frappe.utils import getdate
    if not snapshot_date:
        snapshot_date = getdate(today())
    else:
        snapshot_date = getdate(snapshot_date)
        
    buckets = {
        "qty_0_30": 0.0,
        "qty_31_60": 0.0,
        "qty_61_90": 0.0,
        "qty_91_180": 0.0,
        "qty_180_plus": 0.0
    }
    
    if current_qty <= 0:
        return buckets
        
    # Fetch positive ledger entries ordered by posting_datetime desc (FIFO)
    entries = frappe.db.sql("""
        SELECT qty, posting_datetime
        FROM `tabPSV Ledger Entry`
        WHERE channel_partner = %s AND item_variant = %s AND qty > 0
        ORDER BY posting_datetime DESC
    """, (partner, variant), as_dict=True)
    
    if not entries:
        entries = frappe.db.sql("""
            SELECT qty, posting_datetime
            FROM `tabSMRITI Party Stock Ledger Entry`
            WHERE party_stock_account = %s AND item_code = %s AND qty > 0
            ORDER BY posting_datetime DESC
        """, (partner, variant), as_dict=True)

    remaining = current_qty
    for entry in entries:
        if remaining <= 0:
            break
        
        qty_to_allocate = min(remaining, float(entry["qty"]))
        remaining -= qty_to_allocate
        
        entry_date = getdate(entry["posting_datetime"])
        age_days = (snapshot_date - entry_date).days
        
        if age_days <= 30:
            buckets["qty_0_30"] += qty_to_allocate
        elif age_days <= 60:
            buckets["qty_31_60"] += qty_to_allocate
        elif age_days <= 90:
            buckets["qty_61_90"] += qty_to_allocate
        elif age_days <= 180:
            buckets["qty_91_180"] += qty_to_allocate
        else:
            buckets["qty_180_plus"] += qty_to_allocate
            
    if remaining > 0:
        buckets["qty_180_plus"] += remaining
        
    return buckets


def get_aging_alert(buckets, current_qty):
    if current_qty <= 0:
        return "Healthy"
    critical_qty = buckets["qty_180_plus"]
    warning_qty = buckets["qty_91_180"] + buckets["qty_180_plus"]
    
    if critical_qty > 0 or warning_qty > 0.5 * current_qty:
        return "Critical"
    elif warning_qty > 0.25 * current_qty or buckets["qty_61_90"] > 0:
        return "Warning"
    else:
        return "Healthy"


@frappe.whitelist()
def generate_snapshots():
    """
    Generates stock aging snapshots for all active channel partners.
    This process is incremental and resumable, governed by PSV System Settings.
    Uses a Redis lock to prevent concurrent runs.
    """
    lock_key = "smriti:psv:snapshot_generation"
    cache = frappe.cache()
    
    if cache.get(lock_key):
        frappe.logger().warning("PSV snapshot generation is already running. Skipping execution.")
        return "Skipped: Lock exists"
        
    cache.set(lock_key, 1, ex=3600)  # Lock for 1 hour
    
    try:
        # Ensure single settings doc exists
        settings = frappe.get_single("PSV System Settings")
        batch_size = int(settings.snapshot_batch_size or 500)
        last_processed = settings.last_processed_partner
        
        partners = frappe.get_all(
            "PSV Channel Partner",
            filters={"active": 1},
            fields=["name", "company", "territory", "region"],
            order_by="name"
        )
        
        if not partners:
            partners = frappe.get_all(
                "SMRITI Party Stock Account",
                filters={"active": 1},
                fields=["name", "company", "region"],
                order_by="name"
            )
            for p in partners:
                p["territory"] = "All Territories"
                
        if not partners:
            return "No active partners found"
            
        if last_processed:
            partners_to_process = [p for p in partners if p.name > last_processed]
            if not partners_to_process:
                partners_to_process = partners
                last_processed = ""
        else:
            partners_to_process = partners
            
        batch = partners_to_process[:batch_size]
        if not batch:
            return "No partners to process"
            
        snapshot_date = frappe.utils.getdate(today())
        
        for partner in batch:
            frappe.db.delete("PSV Stock Aging Snapshot", {
                "snapshot_date": snapshot_date,
                "channel_partner": partner.name
            })
            
            balances = frappe.db.sql("""
                SELECT item_variant, SUM(qty) as balance
                FROM `tabPSV Ledger Entry`
                WHERE channel_partner = %s
                GROUP BY item_variant
                HAVING SUM(qty) > 0
            """, (partner.name,), as_dict=True)
            
            if not balances:
                balances = frappe.db.sql("""
                    SELECT item_code as item_variant, SUM(qty) as balance
                    FROM `tabSMRITI Party Stock Ledger Entry`
                    WHERE party_stock_account = %s
                    GROUP BY item_code
                    HAVING SUM(qty) > 0
                """, (partner.name,), as_dict=True)
                
            for bal in balances:
                variant = bal["item_variant"]
                current_qty = float(bal["balance"])
                
                item_info = frappe.db.get_value("Item", variant, ["brand", "item_group"], as_dict=True)
                brand_name = item_info.get("brand") if item_info else ""
                item_group_name = item_info.get("item_group") if item_info else ""
                
                buckets = calculate_aging_for_variant(partner.name, variant, current_qty, snapshot_date)
                aging_alert = get_aging_alert(buckets, current_qty)
                
                snap = frappe.get_doc({
                    "doctype": "PSV Stock Aging Snapshot",
                    "snapshot_date": snapshot_date,
                    "channel_partner": partner.name,
                    "item_variant": variant,
                    "qty": current_qty,
                    "brand_name": brand_name,
                    "item_group_name": item_group_name,
                    "territory_name": partner.territory,
                    "qty_0_30": buckets["qty_0_30"],
                    "qty_31_60": buckets["qty_31_60"],
                    "qty_61_90": buckets["qty_61_90"],
                    "qty_91_180": buckets["qty_91_180"],
                    "qty_180_plus": buckets["qty_180_plus"],
                    "aging_alert": aging_alert
                })
                snap.insert(ignore_permissions=True)
                
        last_partner_processed = batch[-1].name
        
        all_done = False
        if len(batch) < batch_size or partner.name == partners[-1].name:
            all_done = True
            
        settings.last_snapshot_run = now_datetime()
        if all_done:
            settings.last_processed_partner = ""
            settings.last_checkpoint = ""
        else:
            settings.last_processed_partner = last_partner_processed
            settings.last_checkpoint = last_partner_processed
            
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        return f"Success: Processed {len(batch)} partners"
        
    finally:
        cache.delete(lock_key)
