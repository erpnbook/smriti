# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/seed_printability_formula.py
# @description: SMRITI Printability Score formula seed patch.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json

def execute():
    formula = {
        "formula_id": "SMRITI-PRN-SCORE-01",
        "formula_name": "Printability Score Engine",
        "formula_version": "1.0.0",
        "formula_category": "Audit",
        "status": "Approved",
        "is_active": 1,
        "effective_date": "2026-06-20",
        "implementation_reference": "barcode_api.py::calculate_printability_score",
        "dependent_features": json.dumps(["Barcode Studio", "Label Customization"]),
        "formula_expression": "printability_score = margin_safety_score + quiet_zone_score + text_overflow_score + density_compliance_score + collision_score",
        "formula_language": "documentation",
        "variables_and_inputs": json.dumps({
            "margin_safety_score": "Score based on elements remaining inside safe margins (max 25)",
            "quiet_zone_score": "Score based on barcode quiet zone intrusion checks (max 25)",
            "text_overflow_score": "Score based on text field overflow validations (max 20)",
            "density_compliance_score": "Score based on barcode density compliance (max 15)",
            "collision_score": "Score based on element collision overlap checks (max 15)"
        }),
        "data_sources": "SMRITI Barcode Studio Template Settings",
        "business_owner": "Jawahar R. Mallah",
        "technical_owner": "AITDL Core Team",
        "business_meaning": "Printability Score Engine evaluates design templates to ensure thermal printer compatibility and scan reliability. Scores reflect compliance with print safe margins, barcode quiet zones, text overflow risks, barcode density, and collision overlaps.",
        "worked_example": "If all checks pass fully:\nscore = 25 (Margin) + 25 (Quiet Zone) + 20 (Text Overflow) + 15 (Density) + 15 (Collision) = 100.",
        "interpretation_guide": "Bands:\n- Production Ready (A+): 95-100\n- Recommended (A): 90-94\n- Acceptable (B): 80-89\n- Warning (C): 70-79\n- Block Save (F): < 70",
        "recommended_action": "For scores < 70 (Grade F), block save if threshold enforcement is active. Optimize layout elements to achieve Grade A/A+.",
        "explainability_json": json.dumps({
            "meaning": "Evaluates template printability score.",
            "formula": "printability_score = margin_safety_score + quiet_zone_score + text_overflow_score + density_compliance_score + collision_score",
            "example": "Margin Safety = 25/25, Quiet Zone = 25/25, Text Overflow = 10/20, Density = 12/15, Collision = 10/15 => Total = 82.",
            "weights": {
                "margin": 25,
                "quiet_zone": 25,
                "overflow": 20,
                "density": 15,
                "collision": 15
            },
            "grade_bands": {
                "A+": [95, 100],
                "A": [90, 94],
                "B": [80, 89],
                "C": [70, 79],
                "F": [0, 69]
            },
            "version": "1.0"
        })
    }

    doc_name = frappe.db.get_value(
        "SMRITI Formula Definition",
        {"formula_id": formula["formula_id"], "formula_version": formula["formula_version"]},
        "name"
    )
    if doc_name:
        doc = frappe.get_doc("SMRITI Formula Definition", doc_name)
        doc.update(formula)
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            **formula
        })
        doc.insert(ignore_permissions=True)
        
    frappe.db.commit()
    frappe.logger().info("[KGF Patch] Seeded Printability Score Formula Definition successfully.")
