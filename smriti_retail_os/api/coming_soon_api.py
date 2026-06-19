# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/coming_soon_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/coming_soon_api.py
# @description: whitelisted API endpoints for feature roadmaps and coming soon registry.
#
import frappe

# Registry of features under development
# Add new features here as they are planned
COMING_SOON_REGISTRY = {
    # Features below are genuinely planned — pages do NOT yet exist
    "crm": {
        "title":    "CRM & Customer Insights",
        "progress": 10,
        "eta":      "Q4 2026",
    },
    "pdt_dashboard": {
        "title":    "Product Digital Twin Dashboard",
        "progress": 75,
        "eta":      "Q3 2026",
    },
    "simulation_sandbox": {
        "title":    "Simulation Sandbox",
        "progress": 60,
        "eta":      "Q3 2026",
    },
    "knowledge_center": {
        "title":    "Knowledge Center Portal",
        "progress": 10,
        "eta":      "Q3 2026",
    },
    # ── Features below are LIVE — removed from registry ──────────────────
    # analytics          → /analytics (live since v1.2.13)
    # supplier_payments  → /payments (live since v1.2.12)
    # reconciliation     → /psv_reconciliation  (live since v1.2.10)
    # exception_analysis → /psv_exception_analysis (live since v1.2.10)
    # release_notes      → /release_notes        (live since v1.2.10)
    # support            → /smriti_support        (live since v1.2.10)
}


@frappe.whitelist()
def get_feature_info(feature_key):
    """
    Returns coming soon info for a feature.
    Used by sidebar/nav to show correct status.
    """
    info = COMING_SOON_REGISTRY.get(feature_key)
    if not info:
        return {
            "title":    feature_key.replace("-", " ").title(),
            "progress": 0,
            "eta":      "Coming Soon",
        }
    return info


@frappe.whitelist()
def get_all_coming_soon():
    """Returns full registry — used by dashboard to show roadmap."""
    return COMING_SOON_REGISTRY
