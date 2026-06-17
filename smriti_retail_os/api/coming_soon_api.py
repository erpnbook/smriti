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
    "reconciliation": {
        "title":    "Reconciliation",
        "progress": 0,
        "eta":      "PSV Phase 1.3",
    },
    "exception_analysis": {
        "title":    "Exception Analysis",
        "progress": 0,
        "eta":      "PSV Phase 1.3",
    },

    "release_notes": {
        "title":    "Release Notes",
        "progress": 0,
        "eta":      "Q3 2026",
    },
    "support": {
        "title":    "Support",
        "progress": 0,
        "eta":      "Q3 2026",
    },
    "supplier_payments": {
        "title":    "Supplier Payments",
        "progress": 20,
        "eta":      "Q3 2026",
    },
    "crm": {
        "title":    "CRM & Customer Insights",
        "progress": 10,
        "eta":      "Q4 2026",
    },
    "analytics": {
        "title":    "Advanced Analytics",
        "progress": 30,
        "eta":      "Q3 2026",
    },
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
