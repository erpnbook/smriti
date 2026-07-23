# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/coming_soon_api.py
# @description: SMRITI Coming Soon registry API — feature readiness tracking.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/api/coming_soon_api.py
# @description: whitelisted API endpoints for feature roadmaps and coming soon registry.
#
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

# Registry of features under development
# All major roadmap features are now LIVE!
COMING_SOON_REGISTRY = {
    # ── Features below are LIVE — updated in v2.2.0 ───────────────────────
    # crm                  → /smriti-crm (live since v2.2.0)
    # simulation_sandbox   → /smriti-simulation-sandbox (live since v2.2.0)
    # demand_forecasts     → /smriti-demand-forecasts (live since v2.2.0)
    # cashier_performance  → /smriti-cashier-performance (live since v2.2.0)
    # knowledge_center     → /smriti-help (live since Sprint 4)
    # pdt_dashboard        → /smriti-pdt (live since Sprint 4)
    # analytics            → /analytics (live since v1.2.13)
    # supplier_payments    → /payments (live since v1.2.12)
    # reconciliation       → /psv_reconciliation (live since v1.2.10)
    # exception_analysis   → /psv_exception_analysis (live since v1.2.10)
    # release_notes        → /release_notes (live since v1.2.10)
    # support              → /smriti_support (live since v1.2.10)
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
