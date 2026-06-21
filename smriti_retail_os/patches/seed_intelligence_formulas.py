# -*- coding: utf-8 -*-
#
# @file: seed_intelligence_formulas.py
# @description: SMRITI Formula Registry seed patch for Customer Intelligence.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json

def execute():
    formulas = [
        {
            "formula_id": "TST-CHURN",
            "formula_name": "Churn Risk Score",
            "formula_version": "1.0.0",
            "formula_category": "Sales Analytics",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-22",
            "formula_expression": "(days_since_last_visit - visit_frequency_days) / visit_frequency_days * 100",
            "formula_language": "python",
            "variables_and_inputs": json.dumps({
                "days_since_last_visit": "Days elapsed since the customer's last checkout visit",
                "visit_frequency_days": "Average visit interval (cycle) in days"
            }),
            "data_sources": "tabSMRITI Customer Graph",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Measures the likelihood of a customer churning based on their deviation from their regular visit cycle.",
            "worked_example": "If Days Since Last Visit is 45 and Visit Frequency is 30:\n(45 - 30) / 30 * 100 = 50% Churn Risk.",
            "interpretation_guide": "Bands:\n- Healthy: < 40%\n- Warning: 40-70%\n- Critical: >= 70%",
            "recommended_action": "Send proactive engagement coupons to Warning and Critical customers.",
            "explainability_json": json.dumps({
                "meaning": "Measures churn probability based on visit recency deviation.",
                "formula": "(days_since_last_visit - visit_frequency_days) / visit_frequency_days * 100",
                "example": "With 45 days since last visit and 30 days cycle: (45-30)/30 * 100 = 50% Churn Risk.",
                "bands": [
                    {"min": 0, "max": 40, "label": "Healthy"},
                    {"min": 40, "max": 70, "label": "Warning"},
                    {"min": 70, "max": 100, "label": "Critical"}
                ],
                "actions": [
                    "No action needed for Healthy",
                    "Send check-in greeting for Warning",
                    "Send discount coupon for Critical"
                ]
            })
        },
        {
            "formula_id": "TST-VIP",
            "formula_name": "VIP Candidate Score",
            "formula_version": "1.0.0",
            "formula_category": "Sales Analytics",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-22",
            "formula_expression": "(net_revenue / 50000 * 50) + (abv / 5000 * 30) + min(20, purchases_count * 2.0)",
            "formula_language": "python",
            "variables_and_inputs": json.dumps({
                "net_revenue": "Lifetime value (LTV) of customer checkout spend",
                "abv": "Average basket value (ABV)",
                "purchases_count": "Total checkout transactions count"
            }),
            "data_sources": "tabSMRITI Customer Graph",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Calculates the score indicating if a customer is eligible for VIP privileges.",
            "worked_example": "LTV = 30000, ABV = 3000, Purchases = 10:\n(30000 / 50000 * 50) + (3000 / 5000 * 30) + min(20, 10 * 2.0) = 30 + 18 + 20 = 68%",
            "interpretation_guide": "Bands:\n- Low: < 40%\n- Medium: 40-80%\n- High: >= 80%",
            "recommended_action": "Convert customers with score >= VIP Threshold to VIP check status.",
            "explainability_json": json.dumps({
                "meaning": "Calculates VIP candidate score based on LTV, ABV, and purchases volume.",
                "formula": "(net_revenue / 50000 * 50) + (abv / 5000 * 30) + min(20, purchases_count * 2.0)",
                "example": "LTV=30000, ABV=3000, Purchases=10: 30 + 18 + 20 = 68% score.",
                "bands": [
                    {"min": 0, "max": 40, "label": "Low"},
                    {"min": 40, "max": 80, "label": "Medium"},
                    {"min": 80, "max": 100, "label": "High"}
                ],
                "actions": [
                    "Standard service for Low",
                    "Add follow-up notes for Medium",
                    "Offer VIP Card and privilege access for High"
                ]
            })
        },
        {
            "formula_id": "TST-AFFINITY",
            "formula_name": "Campaign Affinity Score",
            "formula_version": "1.0.0",
            "formula_category": "Sales Analytics",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-22",
            "formula_expression": "campaign_responses * 20.0",
            "formula_language": "python",
            "variables_and_inputs": json.dumps({
                "campaign_responses": "Total active response touchpoints (responses, benefits, wallet usage, coupon redemptions)"
            }),
            "data_sources": "tabSMRITI Campaign Response, tabSMRITI Benefit Ledger",
            "business_owner": "Jawahar R. Mallah",
            "technical_owner": "AITDL Core Team",
            "business_meaning": "Measures responsiveness to promotional campaigns.",
            "worked_example": "If campaign response count is 3:\n3 * 20.0 = 60% Affinity.",
            "interpretation_guide": "Bands:\n- Low Response: < 30%\n- Moderate: 30-70%\n- High: >= 70%",
            "recommended_action": "Send high-affinity customers targeted premium offers.",
            "explainability_json": json.dumps({
                "meaning": "Calculates campaign response affinity.",
                "formula": "campaign_responses * 20.0",
                "example": "3 responses * 20 = 60% Affinity.",
                "bands": [
                    {"min": 0, "max": 30, "label": "Low Response"},
                    {"min": 30, "max": 70, "label": "Moderate"},
                    {"min": 70, "max": 100, "label": "High"}
                ],
                "actions": [
                    "Include in standard marketing lists for Low",
                    "Target for special events for Moderate",
                    "Send personalized luxury previews for High"
                ]
            })
        }
    ]

    for f in formulas:
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
    frappe.logger().info("[KGF Patch] Seeded 3 Customer Intelligence Formula Definitions successfully.")
