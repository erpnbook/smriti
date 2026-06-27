# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/patches/seed_knowledge_kpi.py
# @description: Seeds the GOV-001 Knowledge Coverage % KPI into Formula Definitions and runs initial search index.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-19
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json

def execute():
    f = {
        "formula_id": "GOV-001",
        "formula_name": "Knowledge Coverage %",
        "formula_version": "1.0.0",
        "formula_category": "Governance",
        "status": "Approved",
        "is_active": 1,
        "effective_date": "2026-06-19",
        "implementation_reference": "services/knowledge_service.py::calculate_knowledge_coverage",
        "dependent_features": json.dumps(["Knowledge Center", "Business Dictionary", "Explain Engine"]),
        "formula_expression": "knowledge_coverage_percent = (complete_terms / total_active_terms) * 100",
        "formula_language": "documentation",
        "variables_and_inputs": json.dumps({
            "complete_terms": "Number of active terms containing definition + FAQ + manual ref + training ref",
            "total_active_terms": "Total count of active glossary terms"
        }),
        "data_sources": "tabSMRITI Business Term",
        "business_owner": "Jawahar R. Mallah",
        "technical_owner": "AITDL Core Team",
        "business_meaning": "Knowledge Coverage % measures the completeness and health of the platform dictionary. Hum check karte hain ki active glossary terms mein se kitne terms mein definitions, FAQs, manual aur training references fully documented hain.",
        "worked_example": "If there are 20 active business terms, and 15 of them have definitions, FAQs, manual and training references configured:\nknowledge_coverage_percent = (15 / 20) * 100 = 75%.",
        "interpretation_guide": "Bands:\n- Critical: < 50% (Action required to document terms)\n- Monitor: 50-80%\n- Healthy: > 80% (Fully complete glossary)",
        "recommended_action": "For terms lacking FAQs, manual links, or training references, complete the missing parameters in the SMRITI Business Dictionary console.",
        "explainability_json": json.dumps({
            "meaning": "Measures glossary completeness based on whether definitions, FAQs, manuals, and training references are fully populated.",
            "formula": "knowledge_coverage_percent = (complete_terms / total_active_terms) * 100",
            "example": "(15 complete / 20 total active terms) * 100 = 75% coverage.",
            "bands": [
                {"min": 0, "max": 50, "label": "Critical"},
                {"min": 50, "max": 80, "label": "Monitor"},
                {"min": 80, "max": 100, "label": "Healthy"}
            ],
            "actions": [
                "Complete missing FAQs or references in the Business Dictionary",
                "Ensure all new terms have standard fields filled out before approval"
            ]
        })
    }

    # Check if exists, update or insert
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
    
    # Run initial index compile
    from smriti_retail_os.services.knowledge_service import rebuild_knowledge_index
    rebuild_knowledge_index()
    frappe.logger().info("[KGF Patch] Seeded GOV-001 and built initial SMRITI knowledge search index.")
