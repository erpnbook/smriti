# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/seed_default_formulas.py
# @description: SMRITI Formula Registry seed patch — populates core formula definitions.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
import json

def execute():
    # Seeding formulas into the database
    formulas = [
        {
            "formula_id": "INV-001",
            "formula_name": "Sales Velocity",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/forecasting_service.py::calculate_sales_velocity",
            "dependent_features": json.dumps(["PDT Dashboard", "Stockout Prediction", "Transfer Recommendation"]),
            "formula_expression": "weekly_velocity = (total_sales_qty / lookback_days) * 7",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "total_sales_qty": "Total sales quantity in lookback window",
                "lookback_days": "Number of days in the tracking window (usually 30)"
            }),
            "data_sources": "tabSMRITI Party Sales Item",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Sales Velocity calculates how fast a product is selling weekly at an outlet. Hum ye dekhte hain ki pichle 30 dinon mein average kitne pieces har hafte bike.",
            "worked_example": "If a store sells 120 pieces of an item in 30 days:\nweekly_velocity = (120 / 30) * 7 = 28 pieces per week.",
            "interpretation_guide": "Bands:\n- Fast Mover: > 20/week\n- Normal Mover: 5-20/week\n- Slow Mover: < 5/week",
            "recommended_action": "Fast movers require weekly inventory checks, while slow movers should be monitored for markdown promotions.",
            "explainability_json": json.dumps({
                "meaning": "Sales Velocity measures weekly sales velocity based on historical sales quantity.",
                "formula": "weekly_velocity = (total_sales_qty / lookback_days) * 7",
                "example": "(120 pieces / 30 days) * 7 = 28 pieces per week.",
                "bands": [
                    {"min": 0, "max": 5, "label": "Slow Mover"},
                    {"min": 5, "max": 20, "label": "Normal Mover"},
                    {"min": 20, "max": 1000000, "label": "Fast Mover"}
                ],
                "actions": [
                    "Weekly inventory check for fast movers",
                    "Markdown promotions for slow movers"
                ]
            })
        },
        {
            "formula_id": "INV-002",
            "formula_name": "Weeks of Cover (WOC)",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/forecasting_service.py::calculate_weeks_of_cover",
            "dependent_features": json.dumps(["PDT Dashboard", "Outlet Health", "Transfer Recommendation"]),
            "formula_expression": "weeks_of_cover = current_stock / weekly_velocity",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "current_stock": "Current physical stock in store",
                "weekly_velocity": "Weekly sales velocity"
            }),
            "data_sources": "tabSMRITI SKU Twin",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Weeks of Cover (WOC) checks how many weeks our current stock will last based on the weekly sales speed. Hamara stock kitne hafte chalega.",
            "worked_example": "If current stock is 56 pieces and weekly velocity is 28 pieces:\nweeks_of_cover = 56 / 28 = 2 weeks.",
            "interpretation_guide": "Bands:\n- Critical: < 2 weeks (Replenish immediately)\n- Healthy: 2-6 weeks\n- Overstock: > 6 weeks",
            "recommended_action": "For WOC < 2, raise an urgent replenishment purchase or stock transfer request.",
            "explainability_json": json.dumps({
                "meaning": "WOC tells you how long current stock will last in weeks at current sales velocity.",
                "formula": "weeks_of_cover = current_stock / weekly_velocity",
                "example": "56 pieces stock / 28 pieces/week velocity = 2 weeks of cover.",
                "bands": [
                    {"min": 0, "max": 2, "label": "Critical"},
                    {"min": 2, "max": 6, "label": "Healthy"},
                    {"min": 6, "max": 1000000, "label": "Overstock"}
                ],
                "actions": [
                    "Urgent replenishment for critical WOC",
                    "Stock liquidation or transfer for overstocked items"
                ]
            })
        },
        {
            "formula_id": "INV-003",
            "formula_name": "Dead Stock Score",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/forecasting_service.py::calculate_dead_stock_score",
            "dependent_features": json.dumps(["PDT Dashboard", "Stockout Prediction"]),
            "formula_expression": "dead_stock_score = max(0, 100 - (active_days_since_last_sale * (100 / max_inactive_days_allowed)))",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "active_days_since_last_sale": "Days elapsed since the last sale of this item",
                "max_inactive_days_allowed": "Threshold days to qualify as dead stock (e.g. 90 days)"
            }),
            "data_sources": "tabSMRITI SKU Twin, tabSMRITI Party Sales Item",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Dead Stock Score measure indicators of non-moving stock. Jitne zyada din bina sale ke guzarte hain, score utna kam (critical) hota hai.",
            "worked_example": "If last sale was 45 days ago, and max inactive limit is 90 days:\ndead_stock_score = max(0, 100 - (45 * (100 / 90))) = 50.",
            "interpretation_guide": "Bands:\n- Critical: < 30 (Likely Dead Stock)\n- Monitor: 30-70\n- Healthy: > 70 (Active Stock)",
            "recommended_action": "For scores < 30, offer bundle discounts or clear via warehouse consolidation.",
            "explainability_json": json.dumps({
                "meaning": "Scores items based on how long they have remained unsold.",
                "formula": "dead_stock_score = max(0, 100 - (days_inactive * (100 / threshold)))",
                "example": "With 45 days inactive and 90 threshold: 100 - (45 * 1.11) = 50 score.",
                "bands": [
                    {"min": 0, "max": 30, "label": "Critical"},
                    {"min": 30, "max": 70, "label": "Monitor"},
                    {"min": 70, "max": 100, "label": "Healthy"}
                ],
                "actions": [
                    "Trigger promotional discount for critical scores",
                    "Relocate to higher velocity outlets"
                ]
            })
        },
        {
            "formula_id": "FRC-001",
            "formula_name": "Forecast Confidence",
            "formula_version": "1.0.0",
            "formula_category": "Forecasting",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/forecasting_service.py::calculate_forecast_confidence",
            "dependent_features": json.dumps(["PDT Dashboard", "Stockout Prediction"]),
            "formula_expression": "forecast_confidence = max(0, 100 - (coefficient_of_variation * 100))",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "coefficient_of_variation": "Standard deviation divided by the weekly velocity mean"
            }),
            "data_sources": "tabSMRITI SKU Twin",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Forecast Confidence checks the volatility of weekly sales. Agar sales har hafte bohot badalti hain (high volatility), to forecasting confidence low hogi.",
            "worked_example": "If mean weekly velocity is 10 and standard deviation is 2:\nCV = 2 / 10 = 0.2\nforecast_confidence = 100 - (0.2 * 100) = 80%.",
            "interpretation_guide": "Bands:\n- High Confidence: > 80%\n- Medium Confidence: 50-80%\n- Low Confidence: < 50%",
            "recommended_action": "For low confidence forecasts, increase safety stock parameters by 1.5x.",
            "explainability_json": json.dumps({
                "meaning": "Measures stability of weekly sales velocity. Low volatility = high confidence.",
                "formula": "forecast_confidence = max(0, 100 - (CV * 100))",
                "example": "Mean=10, SD=2 -> CV=0.2 -> 100 - 20 = 80% confidence.",
                "bands": [
                    {"min": 0, "max": 50, "label": "Low Confidence"},
                    {"min": 50, "max": 80, "label": "Medium Confidence"},
                    {"min": 80, "max": 100, "label": "High Confidence"}
                ],
                "actions": [
                    "Increase safety stock cover for low confidence predictions",
                    "Rely on baseline rules rather than predictive models for low confidence items"
                ]
            })
        },
        {
            "formula_id": "OHS-001",
            "formula_name": "Outlet Health Score",
            "formula_version": "1.0.0",
            "formula_category": "Outlet Health",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/twin_quality_service.py::calculate_outlet_health",
            "dependent_features": json.dumps(["Outlet Health Score", "PSV Dashboard"]),
            "formula_expression": "outlet_health = 100 - (sync_delay_hours * penalty_factor) - (variance_percentage * variance_penalty)",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "sync_delay_hours": "Hours elapsed since last physical upload or snapshot",
                "variance_percentage": "Physical stock count mismatch percentage"
            }),
            "data_sources": "tabSMRITI Party Stock Account, tabSMRITI Party Stock Ledger Entry",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Outlet Health evaluates data compliance. Agar store daily sales data send nahi karta ya stock audit mein bohot difference aata hai, to health score gir jata hai.",
            "worked_example": "If sync delay is 24 hours (penalty = 0.5) and stock variance is 2% (penalty = 5):\nhealth = 100 - (24 * 0.5) - (2 * 5) = 100 - 12 - 10 = 78.",
            "interpretation_guide": "Bands:\n- Healthy: > 80\n- Monitor: 50-80\n- Critical: < 50",
            "recommended_action": "For critical health scores, block automated inventory transfer recommendations until audit reconciliation is completed.",
            "explainability_json": json.dumps({
                "meaning": "Assesses physical store reporting compliance and stock ledger accuracy.",
                "formula": "outlet_health = 100 - (delay_hours * 0.5) - (variance_pct * 5)",
                "example": "24 hours delay and 2% variance: 100 - 12 - 10 = 78 score.",
                "bands": [
                    {"min": 0, "max": 50, "label": "Critical"},
                    {"min": 50, "max": 80, "label": "Monitor"},
                    {"min": 80, "max": 100, "label": "Healthy"}
                ],
                "actions": [
                    "Suspend automated transfers for critical outlets",
                    "Schedule mandatory physical audit reconciliation"
                ]
            })
        },
        {
            "formula_id": "TRF-001",
            "formula_name": "Transfer Benefit Score",
            "formula_version": "1.0.0",
            "formula_category": "Transfer Optimization",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/optimization_service.py::calculate_transfer_benefit",
            "dependent_features": json.dumps(["Transfer Recommendation", "PDT Dashboard"]),
            "formula_expression": "transfer_benefit = sales_retaining_value - freight_cost - (origin_stockout_risk_penalty * stockout_cost)",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "sales_retaining_value": "Expected profit margin of items retained from stockout",
                "freight_cost": "Cost of transport between origin and destination",
                "origin_stockout_risk_penalty": "Increase in stockout probability at sending outlet after transfer"
            }),
            "data_sources": "tabSMRITI SKU Twin, tabSMRITI Party Stock Account",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Transfer Benefit Score evaluates if a stock transfer is profitable. Hum ye ensure karte hain ki transport cost aur source location pe stock out hone ka risk, transfer ke profit margin se kam ho.",
            "worked_example": "If margin is Rs 1000, freight is Rs 200, and source risk penalty is Rs 150:\nbenefit = 1000 - 200 - 150 = Rs 650.",
            "interpretation_guide": "Bands:\n- Highly Beneficial: > 500\n- Marginal: 0-500\n- Not Recommended: < 0",
            "recommended_action": "Automatically suggest transfers where benefit is Highly Beneficial (> 500). Reject if < 0.",
            "explainability_json": json.dumps({
                "meaning": "Checks if the economics of moving stock from Store A to Store B makes financial sense.",
                "formula": "transfer_benefit = margin - freight - origin_stockout_penalty",
                "example": "Margin Rs 1000 - Freight Rs 200 - Source Risk Rs 150 = Rs 650 Benefit.",
                "bands": [
                    {"min": -100000, "max": 0, "label": "Not Recommended"},
                    {"min": 0, "max": 500, "label": "Marginal"},
                    {"min": 500, "max": 1000000, "label": "Highly Beneficial"}
                ],
                "actions": [
                    "Auto-approve transfer request for highly beneficial scores",
                    "Decline transfer if benefit is negative"
                ]
            })
        },
        {
            "formula_id": "SAL-001",
            "formula_name": "Sell Through %",
            "formula_version": "1.0.0",
            "formula_category": "Sales Analytics",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/twin_quality_service.py::calculate_sell_through",
            "dependent_features": json.dumps(["Sell Through Analytics", "PSV Dashboard"]),
            "formula_expression": "sell_through_percent = (total_sales_qty / (opening_stock + received_stock)) * 100",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "total_sales_qty": "Total items sold during the reporting period",
                "opening_stock": "Inventory balance at beginning of period",
                "received_stock": "Total inventory received during the period"
            }),
            "data_sources": "tabSMRITI Party Sales Item, tabSMRITI Party Stock Ledger Entry",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Sell Through % indicates what percentage of available stock was sold in a month. Humne kitna stock becha compared to total received stock.",
            "worked_example": "If opening stock was 80, received was 20, and sales was 40:\nsell_through = (40 / (80 + 20)) * 100 = 40%.",
            "interpretation_guide": "Bands:\n- Excellent: > 60%\n- Average: 30-60%\n- Slow: < 30%",
            "recommended_action": "For slow items (< 30%), trigger end-of-season clearance schemes.",
            "explainability_json": json.dumps({
                "meaning": "Calculates percentage of total inventory sold in a given time frame.",
                "formula": "sell_through_percent = (sales_qty / (opening + received)) * 100",
                "example": "40 sold / (80 opening + 20 received) * 100 = 40% Sell Through.",
                "bands": [
                    {"min": 0, "max": 30, "label": "Slow"},
                    {"min": 30, "max": 60, "label": "Average"},
                    {"min": 60, "max": 100, "label": "Excellent"}
                ],
                "actions": [
                    "Initiate marketing campaigns for slow categories",
                    "Replenish fast-moving categories with high sell-through"
                ]
            })
        },
        {
            "formula_id": "AUD-001",
            "formula_name": "Stock Accuracy %",
            "formula_version": "1.0.0",
            "formula_category": "Audit",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/twin_quality_service.py::calculate_stock_accuracy",
            "dependent_features": json.dumps(["Audit & Variance Management", "Outlet Health Score"]),
            "formula_expression": "stock_accuracy = (1 - (abs(physical_qty - ledger_qty) / ledger_qty)) * 100",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "physical_qty": "Total quantity counted physically at store",
                "ledger_qty": "Total Inventory Visibility Layer balance recorded in system"
            }),
            "data_sources": "tabSMRITI Party Physical Item, tabSMRITI Party Stock Ledger Entry",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Stock Accuracy % measures audit matching. Physical stock aur Inventory Visibility Layer stock kitna match karta hai.",
            "worked_example": "If ledger has 100 pieces and physical audit counts 97:\naccuracy = (1 - (abs(97 - 100) / 100)) * 100 = (1 - 0.03) * 100 = 97%.",
            "interpretation_guide": "Bands:\n- High Accuracy: > 98%\n- Moderate: 90-98%\n- Poor Accuracy: < 90%",
            "recommended_action": "For poor accuracy (< 90%), trigger a deep reconciliation audit check.",
            "explainability_json": json.dumps({
                "meaning": "Calculates accuracy match between physical count and system records.",
                "formula": "stock_accuracy = (1 - (abs(physical - ledger) / ledger)) * 100",
                "example": "Ledger=100, Physical=97 -> (1 - 0.03) * 100 = 97% Accuracy.",
                "bands": [
                    {"min": 0, "max": 90, "label": "Poor Accuracy"},
                    {"min": 90, "max": 98, "label": "Moderate"},
                    {"min": 98, "max": 100, "label": "High Accuracy"}
                ],
                "actions": [
                    "Trigger detailed security/audit inspection for poor accuracy",
                    "Conduct automated ledger adjustments for minor variances"
                ]
            })
        },
        {
            "formula_id": "INV-004",
            "formula_name": "Inventory Turnover",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/twin_quality_service.py::calculate_inventory_turnover",
            "dependent_features": json.dumps(["Sell Through Analytics", "PSV Dashboard"]),
            "formula_expression": "inventory_turnover = annual_sales_cost / average_inventory_value",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "annual_sales_cost": "Cost of Goods Sold (COGS) over 12 months",
                "average_inventory_value": "Mean inventory value held during the period"
            }),
            "data_sources": "tabSMRITI Party Sales Item, tabSMRITI Party Stock Ledger Entry",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Inventory Turnover calculates how many times a store sells and replaces its inventory over a year. Hamara stock ek saal mein kitni baar naya stock ban kar rotate hua.",
            "worked_example": "If COGS is Rs 12,00,000 and average inventory is Rs 3,00,000:\nturnover = 12,00,000 / 3,00,000 = 4.0 times.",
            "interpretation_guide": "Bands:\n- High Turnover: > 8.0\n- Healthy Turnover: 4.0-8.0\n- Slow Rotation: < 4.0",
            "recommended_action": "For slow rotation (< 4.0), stop replenishing new variants and clear current stock.",
            "explainability_json": json.dumps({
                "meaning": "Annual stock rotation speed. Higher values indicate efficient capital lockup.",
                "formula": "inventory_turnover = annual_sales_cost / average_inventory_value",
                "example": "Rs 12 Lakh COGS / Rs 3 Lakh Average Stock = 4.0 turns.",
                "bands": [
                    {"min": 0, "max": 4, "label": "Slow Rotation"},
                    {"min": 4, "max": 8, "label": "Healthy"},
                    {"min": 8, "max": 1000, "label": "High"}
                ],
                "actions": [
                    "Stop purchasing new variant curves for slow rotating outlets",
                    "Expand variants curves for high rotating outlets"
                ]
            })
        },
        {
            "formula_id": "VAR-001",
            "formula_name": "Variant Curve Health",
            "formula_version": "1.0.0",
            "formula_category": "Forecasting",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/twin_quality_service.py::check_variant_curve_status",
            "dependent_features": json.dumps(["Broken Size Analysis", "PDT Dashboard"]),
            "formula_expression": "variant_health_percent = (active_available_sizes / total_sizes_in_curve) * 100",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "active_available_sizes": "Number of size variants currently in stock (stock > 0)",
                "total_sizes_in_curve": "Total sizes configured in the product size curve"
            }),
            "data_sources": "tabSMRITI SKU Twin, tabItem",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Variant Curve Health checks if sizes of a shoe/apparel model are missing. Agar core sizes (like 7, 8, 9) out of stock hain, to variant health gir jati hai.",
            "worked_example": "If a shoe has 5 sizes (6,7,8,9,10) and only sizes 6 and 10 are in stock:\nhealth = (2 / 5) * 100 = 40% (Broken Curve).",
            "interpretation_guide": "Bands:\n- Complete: > 80%\n- Broken Size Curve: < 80%",
            "recommended_action": "For broken curves, immediately trigger a target transfer for missing sizes from warehouses.",
            "explainability_json": json.dumps({
                "meaning": "Percentage of configured size variants currently in stock.",
                "formula": "variant_health_percent = (available_sizes / total_sizes) * 100",
                "example": "2 sizes available / 5 total sizes * 100 = 40% (Broken Curve).",
                "bands": [
                    {"min": 0, "max": 80, "label": "Broken Size Curve"},
                    {"min": 80, "max": 100, "label": "Complete"}
                ],
                "actions": [
                    "Prioritize size replenishment for broken curves",
                    "Avoid pricing markdowns on single size items if curve is complete"
                ]
            })
        },
        {
            "formula_id": "KGF-001",
            "formula_name": "KGF Coverage %",
            "formula_version": "1.0.0",
            "formula_category": "Audit",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-19",
            "implementation_reference": "services/formula_service.py::calculate_kgf_coverage",
            "dependent_features": json.dumps(["Documentation Center", "Audit & Variance Management"]),
            "formula_expression": "kgf_coverage_percent = (registered_kpis / total_kpis) * 100",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "registered_kpis": "Number of unique active KPIs in the Formula Registry",
                "total_kpis": "Total count of calculated KPI fields exposed in SMRITI dashboards"
            }),
            "data_sources": "tabSMRITI Formula Definition",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "KGF Coverage % measures the compliance of our metrics to the explainability constitution. Hum ye check karte hain ki humare kitne percentage of active dashboard metrics Formula Registry mein registered aur documented hain.",
            "worked_example": "If there are 11 dashboard metrics exposed, and 10 of them are registered in the Formula Registry:\nkgf_coverage_percent = (10 / 11) * 100 = 90.91%.",
            "interpretation_guide": "Bands:\n- Compliant: 100% (Target)\n- High Cover: 90-99%\n- Action Required: < 90%",
            "recommended_action": "If coverage drops below 100%, block production deployments of new metrics and register the missing KPIs immediately.",
            "explainability_json": json.dumps({
                "meaning": "Measures percentage of system metrics that are documented in the registry.",
                "formula": "kgf_coverage_percent = (registered_kpis / total_kpis) * 100",
                "example": "(10 registered / 11 total metrics) * 100 = 90.91% coverage.",
                "bands": [
                    {"min": 0, "max": 90, "label": "Action Required"},
                    {"min": 90, "max": 99.9, "label": "High Cover"},
                    {"min": 100, "max": 100, "label": "Compliant"}
                ],
                "actions": [
                    "Register missing dashboard metrics in the central registry",
                    "Reject PRs containing undocumented KPIs"
                ]
            })
        },
        {
            "formula_id": "TR-HLTH-01",
            "formula_name": "Trial Pipeline Health Score",
            "formula_version": "1.0.0",
            "formula_category": "Trial Operations",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-25",
            "implementation_reference": "services/trial_service.py::calculate_trial_health_score",
            "dependent_features": json.dumps(["Platform Admin Dashboard", "Trial Health Snapshot"]),
            "formula_expression": "health_score = max(0.0, (active / max(1, active + failed)) * 100.0 - penalty)",
            "formula_language": "documentation",
            "variables_and_inputs": json.dumps({
                "active": "Active trial activations count",
                "failed": "Failed trial activations count",
                "penalty": "SLA breach penalty: min(20.0, max(0.0, (avg_sla_hours - target_sla) * penalty_mult))"
            }),
            "data_sources": "tabSMRITI Trial Activation",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Trial Pipeline Health Score measures the overall quality of the trial provisioning system. Hum ye check karte hain ki trial activation kitni jaldi ho raha hai aur koi failure to nahi aa raha pipeline mein.",
            "worked_example": "If there are 8 active trials and 2 failed ones (success rate = 80%), and average SLA time is 6 hours (penalty = (6 - 4) * 5 = 10%):\nhealth_score = 80.0 - 10.0 = 70.0% (Monitor band).",
            "interpretation_guide": "Bands:\n- Healthy: >= 80.0\n- Monitor: 50.0 - 79.9\n- Critical: < 50.0",
            "recommended_action": "For scores < 80 (Monitor), check recent failed activations in Provision Log. For scores < 50 (Critical), immediately investigate server connectivity and SMTP configuration.",
            "explainability_json": json.dumps({
                "meaning": "Measures provisioning success rate and SLA compliance.",
                "formula": "health_score = success_rate - sla_penalty",
                "example": "8 active, 2 failed -> 80% success. SLA 6 hours -> 10% penalty. Score = 70.0%",
                "bands": [
                    {"min": 0, "max": 50, "label": "Critical"},
                    {"min": 50, "max": 80, "label": "Monitor"},
                    {"min": 80, "max": 100, "label": "Healthy"}
                ],
                "actions": [
                    "Investigate Provision Logs for failed trials",
                    "Verify SMTP and server resources if health is critical"
                ]
            })
        }
    ]

    for f in formulas:
        # Check if version exists. If yes, update it. If not, create it.
        doc_name = frappe.db.get_value(
            "SMRITI Formula Definition",
            {"formula_id": f["formula_id"], "formula_version": f["formula_version"]},
            "name"
        )
        if doc_name:
            doc = frappe.get_doc("SMRITI Formula Definition", doc_name)
            doc.update(f)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "SMRITI Formula Definition",
                **f
            })
            doc.insert(ignore_permissions=True)
            
    frappe.db.commit()
    frappe.logger().info("[KGF Patch] Seeded 11 core SMRITI Formula Definitions successfully.")
