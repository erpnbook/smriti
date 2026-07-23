# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/simulation_api.py
# @description: SMRITI Product Twin Simulation Sandbox API.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-07-23
# @version: 2.2.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os import smriti
from smriti_retail_os.services.simulation_service import run_sandbox_simulation


@frappe.whitelist()
def run_simulation(simulation_config=None):
    """
    Whitelisted API endpoint for Product Twin Simulation Sandbox.
    Accepts JSON/dict containing simulation multipliers and overrides.
    """
    if isinstance(simulation_config, str):
        simulation_config = frappe.parse_json(simulation_config) or {}
    elif not simulation_config:
        simulation_config = {}

    results = run_sandbox_simulation(simulation_config)

    # Calculate summary metrics across simulated results
    total_twins = len(results)
    stockouts = sum(1 for r in results if r.get("twin_state") == "Stockout")
    critical = sum(1 for r in results if r.get("twin_state") == "Critical")
    overstock = sum(1 for r in results if r.get("twin_state") == "Overstock")
    healthy = sum(1 for r in results if r.get("twin_state") == "Healthy")

    return {
        "status": "success",
        "summary": {
            "total_twins": total_twins,
            "stockouts": stockouts,
            "critical": critical,
            "overstock": overstock,
            "healthy": healthy,
            "simulation_config": simulation_config
        },
        "twins": results
    }


@frappe.whitelist()
def get_simulation_presets():
    """Returns standard scenario presets for quick testing in UI."""
    return [
        {
            "id": "festive_boost",
            "title": "Festive Demand Surge",
            "velocity_multiplier": 1.75,
            "seasonality_factor": 1.3,
            "supplier_lead_days_override": 14,
            "description": "Simulates 75% sales boost + 30% seasonality with extended festive lead times."
        },
        {
            "id": "monsoon_slowdown",
            "title": "Monsoon Slowdown",
            "velocity_multiplier": 0.65,
            "seasonality_factor": 0.8,
            "supplier_lead_days_override": 21,
            "description": "Simulates 35% velocity reduction with supply chain delays."
        },
        {
            "id": "clearance_sale",
            "title": "End of Season Clearance",
            "velocity_multiplier": 2.5,
            "seasonality_factor": 1.0,
            "supplier_lead_days_override": 7,
            "description": "Simulates rapid inventory liquidation across outlets."
        }
    ]
