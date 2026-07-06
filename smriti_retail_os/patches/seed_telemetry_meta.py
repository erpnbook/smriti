# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/seed_telemetry_meta.py
# @description: Seeds the Scan Telemetry Event Definitions and the Scan Reliability Score formula.
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
    # 1. Seed Telemetry Event Definitions
    events = [
        {
            "name": "SCAN-EVT-001",
            "event_name": "Barcode Scan Success",
            "description": "Barcode successfully decoded on the first attempt (Scan attempts = 1, Success = 1)."
        },
        {
            "name": "SCAN-EVT-002",
            "event_name": "Barcode Scan Retry",
            "description": "Barcode successfully decoded after multiple attempts (Scan attempts > 1, Success = 1)."
        },
        {
            "name": "SCAN-EVT-003",
            "event_name": "Barcode Scan Failure",
            "description": "Barcode failed to decode or scanning was bypassed by manual keyboard entry (Success = 0)."
        }
    ]

    for ev in events:
        if not frappe.db.exists("SMRITI Telemetry Event Definition", ev["name"]):
            try:
                doc = frappe.get_doc({
                    "doctype": "SMRITI Telemetry Event Definition",
                    **ev
                })
                doc.insert(ignore_permissions=True)
                print(f"[SMRITI Telemetry] Seeded Event Definition: {ev['name']}")
            except Exception as e:
                frappe.log_error(title=f"Error seeding event {ev['name']}", message=str(e))
        else:
            # Update existing to align descriptions
            try:
                doc = frappe.get_doc("SMRITI Telemetry Event Definition", ev["name"])
                doc.event_name = ev["event_name"]
                doc.description = ev["description"]
                doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(title=f"Error updating event {ev['name']}", message=str(e))

    # 2. Seed Scan Reliability Score Formula
    formula = {
        "formula_id": "SMRITI-SCAN-REL-01",
        "formula_name": "Scan Reliability Score",
        "formula_version": "1.0.0",
        "formula_category": "Audit",
        "status": "Approved",
        "is_active": 1,
        "effective_date": "2026-06-20",
        "implementation_reference": "barcode_api.py::aggregate_scan_telemetry",
        "dependent_features": json.dumps(["Barcode Studio", "Operational Telemetry"]),
        "formula_expression": "scan_reliability_score = ((first_pass_successes + 0.5 * retry_successes) / total_scans) * 100",
        "formula_language": "documentation",
        "variables_and_inputs": json.dumps({
            "first_pass_successes": "Count of SCAN-EVT-001 events (decoded on first attempt)",
            "retry_successes": "Count of SCAN-EVT-002 events (decoded on subsequent attempts)",
            "failures": "Count of SCAN-EVT-003 events (failed completely or overridden manually)",
            "total_scans": "Sum of first_pass_successes + retry_successes + failures"
        }),
        "data_sources": "SMRITI Barcode Scan Event telemetry log",
        "business_owner": "Jawahar R. Mallah",
        "technical_owner": "AITDL Core Team",
        "business_meaning": "Scan Reliability Score evaluates the checkout scanning performance of printed barcode templates in physical stores. The score translates raw scan counts and retry frequencies into a clear usability percentage. Lower scores indicate checkout friction and barcode quality issues.",
        "worked_example": "If 80 scans succeed on first try, 15 require retries, and 5 fail:\nTotal Scans = 80 + 15 + 5 = 100.\nScore = ((80 + 0.5 * 15) / 100) * 100 = 87.5%.",
        "interpretation_guide": "Bands:\n- Excellent (Green): 95.0% - 100.0%\n- Monitor (Yellow): 85.0% - 94.9%\n- Critical (Red): < 85.0%",
        "recommended_action": "For scores < 85.0% (Critical), alert store administrators and prompt layout diagnostics in the Barcode Studio or inspect physical printhead condition.",
        "explainability_json": json.dumps({
            "meaning": "Evaluates physical checkout scan reliability rate.",
            "formula": "scan_reliability_score = ((first_pass_successes + 0.5 * retry_successes) / total_scans) * 100",
            "example": "First Pass = 80, Retry Successes = 15, Failures = 5 => Score = 87.5%",
            "grade_bands": {
                "Excellent": [95.0, 100.0],
                "Monitor": [85.0, 94.9],
                "Critical": [0.0, 84.9]
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
        try:
            doc = frappe.get_doc("SMRITI Formula Definition", doc_name)
            doc.update(formula)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(title="Error updating SMRITI-SCAN-REL-01 formula", message=str(e))
    else:
        try:
            doc = frappe.get_doc({
                "doctype": "SMRITI Formula Definition",
                **formula
            })
            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(title="Error inserting SMRITI-SCAN-REL-01 formula", message=str(e))

    frappe.db.commit()
    print("[SMRITI Telemetry] Seeded Scan Reliability Score Formula Definition successfully.")
