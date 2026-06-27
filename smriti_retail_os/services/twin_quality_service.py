# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/twin_quality_service.py
# @description: Evaluates twin quality metrics and variant size curve mismatches.
#               Quality score is based on physical audit and sales upload timeliness.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.5
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#


import frappe
from frappe.utils import now_datetime, getdate, today
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances

def evaluate_twin_quality(party_stock_account, item_code):
    """
    Evaluates data quality metrics for the twin. Returns score (0-100) and status.
    Factors:
    - Physical audit compliance: time elapsed since last SMRITI Party Physical Snapshot.
    - Sales upload timeliness: time elapsed since last SMRITI Party Sales Upload.
    """
    score = 0
    
    # 1. Check last physical snapshot
    last_audit = frappe.db.get_value(
        "SMRITI Party Physical Snapshot",
        {"party_stock_account": party_stock_account, "docstatus": 1},
        "audit_date",
        order_by="audit_date desc"
    )
    if last_audit:
        days_since_audit = (getdate(today()) - getdate(last_audit)).days
        if days_since_audit <= 30:
            score += 50
        elif days_since_audit <= 90:
            score += 30
        else:
            score += 15
    else:
        score += 5  # No audit ever
        
    # 2. Check last sales upload
    last_upload = frappe.db.get_value(
        "SMRITI Party Sales Upload",
        {"party_stock_account": party_stock_account, "docstatus": 1},
        "period_end_date",
        order_by="period_end_date desc"
    )
    if last_upload:
        days_since_upload = (getdate(today()) - getdate(last_upload)).days
        if days_since_upload <= 7:
            score += 50
        elif days_since_upload <= 30:
            score += 30
        else:
            score += 15
    else:
        score += 5  # No upload ever
        
    # Standardised quality status mapping
    if score >= 80:
        status = "Excellent"
    elif score >= 50:
        status = "Good"
    else:
        status = "Poor"
        
    return {
        "twin_quality_score": float(score),
        "twin_quality_status": status
    }

def evaluate_variant_curve(item_code, party_stock_account):
    """
    Determines if the size/variant curve is broken for the style template.
    A variant curve is broken if:
    - Sibling variants exist under the same template item.
    - Total style stock is positive (> 0).
    - One or more core sizes have zero balance.
    """
    item_template = frappe.db.get_value("Item", item_code, "variant_of")
    if not item_template:
        return {
            "variant_curve_status": "Complete",
            "missing_sizes": ""
        }
        
    # Fetch all sibling variants under the same template
    variants = frappe.get_all(
        "Item",
        filters={"variant_of": item_template},
        fields=["name"]
    )
    variant_codes = [v.name for v in variants]
    if not variant_codes:
        return {
            "variant_curve_status": "Complete",
            "missing_sizes": ""
        }
        
    # Fetch bulk balances for the PSA
    balances = get_bulk_party_balances(party_stock_account)
    total_qty = sum(balances.get(code, 0.0) for code in variant_codes)
    
    # If the style is completely out of stock, it is not considered a broken curve
    if total_qty <= 0.0:
        return {
            "variant_curve_status": "Complete",
            "missing_sizes": ""
        }
        
    # Find sibling variants that are out of stock
    missing_variants = [
        code for code in variant_codes
        if balances.get(code, 0.0) <= 0.0
    ]
    
    if missing_variants:
        # Extract the configured variant dimension attribute value (e.g. "Size") for each missing variant.
        # The lookup dimension is configurable via SMRITI PSV Settings > variant_dimension.
        # This prevents ambiguous first-attribute lookup on multi-attribute items (Size + Colour + Width).
        variant_dimension = "Size"  # Sensible retail default
        try:
            if frappe.db.exists("DocType", "SMRITI PSV Settings"):
                settings = frappe.get_cached_doc("SMRITI PSV Settings")
                variant_dimension = settings.get("variant_dimension") or "Size"
        except Exception:
            pass  # Use default dimension — settings read failure is non-critical for this path

        missing_labels = []
        for code in missing_variants:
            attr_val = frappe.db.get_value(
                "Item Variant Attribute",
                {"parent": code, "attribute": variant_dimension},
                "attribute_value"
            )
            missing_labels.append(attr_val or code)  # Fall back to item_code if attribute not found

        return {
            "variant_curve_status": "Broken",
            "missing_sizes": ", ".join(missing_labels)
        }
    else:
        return {
            "variant_curve_status": "Complete",
            "missing_sizes": ""
        }
