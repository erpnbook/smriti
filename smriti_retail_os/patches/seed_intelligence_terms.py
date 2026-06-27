# -*- coding: utf-8 -*-
#
# @file: seed_intelligence_terms.py
# @description: SMRITI Business Dictionary seed patch for Customer Intelligence terms.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json

def execute():
    """
    Migration patch to seed 5 new SMRITI Business Dictionary terms for Customer Intelligence.
    Uses a 2-phase approach to avoid forward-reference LinkValidationErrors.
    """
    intelligence_terms = [
        {
            "term_id": "CIG",
            "term_name": "Customer Intelligence Graph",
            "term_category": "Customer",
            "definition": "The Customer Intelligence Graph aggregates party metrics including checkout timelines, purchase histories, product sizing, and promotional responses to generate predictive scores.",
            "hinglish_definition": "Customer ke profile information, checkout history, sizing categories, aur campaign engagement activity ko consolidate karke calculations and predictions run karne wala advanced database engine.",
            "term_aliases": ["CIG", "Customer Intelligence Graph", "Intelligence Graph"],
            "manual_reference": "Volume 2 > Manager Guide",
            "training_reference": "TRN-CIG-001",
            "related_formulas": [],
            "related_terms": ["clienteling"],
            "faq": [
                {"q": "Where does CIG data come from?", "a": "CIG queries checkout sales invoices, campaign responses, and store visits dynamically."}
            ],
            "common_mistakes": [
                {"mistake": "Editing CIG parameters directly in database", "a": "All parameters must resolve from SMRITI Clienteling Settings."}
            ],
            "formula_definition_ref": None,
            "formula_version": None,
            "explainability_note": "Central CIG service layer aggregates transaction events to compile customer profiles dynamically."
        },
        {
            "term_id": "churn_risk_score",
            "term_name": "Churn Risk Score",
            "term_category": "Sales",
            "definition": "Churn Risk Score measures the likelihood that a customer will stop visiting the store based on their visit frequency deviation.",
            "hinglish_definition": "Customer ke normal store visit frequency pattern se deviation ke basis par churn hone ke risk ka score percentage.",
            "term_aliases": ["Churn Risk Score", "Churn Risk", "churn_risk_score"],
            "manual_reference": "Volume 2 > Manager Guide",
            "training_reference": "TRN-CIG-CHURN",
            "related_formulas": ["TST-CHURN"],
            "related_terms": ["CIG"],
            "faq": [
                {"q": "What triggers a Warning churn status?", "a": "A Churn Risk Score between 40% and 70%."}
            ],
            "common_mistakes": [
                {"mistake": "Hardcoding churn math in client scripts", "a": "Churn math must resolve dynamically from SMRITI Formula Registry definition TST-CHURN."}
            ],
            "formula_definition_ref": "TST-CHURN",
            "formula_version": "1.0.0",
            "explainability_note": "Calculated dynamically from Formula Registry definition TST-CHURN based on customer visit deviation."
        },
        {
            "term_id": "vip_candidate_score",
            "term_name": "VIP Candidate Score",
            "term_category": "Sales",
            "definition": "VIP Candidate Score evaluates customer lifetime value (LTV), average basket value (ABV), and checkout transactions volume to rate eligibility for VIP status.",
            "hinglish_definition": "Customer ke total spending volume (LTV), average transaction size (ABV), aur visit counts par calculate kiya gaya VIP check suitability score.",
            "term_aliases": ["VIP Candidate Score", "VIP Score", "vip_candidate_score"],
            "manual_reference": "Volume 2 > Manager Guide",
            "training_reference": "TRN-CIG-VIP",
            "related_formulas": ["TST-VIP"],
            "related_terms": ["CIG"],
            "faq": [
                {"q": "Can I adjust the score required for VIP status?", "a": "Yes, managers can change the VIP Threshold setting in SMRITI Clienteling Settings."}
            ],
            "common_mistakes": [
                {"mistake": "Manually ticking VIP checkbox in customer master", "a": "VIP checkbox is read-only and automatically updated by CIG based on the VIP Threshold setting."}
            ],
            "formula_definition_ref": "TST-VIP",
            "formula_version": "1.0.0",
            "explainability_note": "Calculated dynamically from Formula Registry definition TST-VIP using spending and frequency inputs."
        },
        {
            "term_id": "campaign_affinity_score",
            "term_name": "Campaign Affinity Score",
            "term_category": "Sales",
            "definition": "Campaign Affinity Score measures a customer's responsiveness to promotional touchpoints, coupon redemptions, and loyalty earnings.",
            "hinglish_definition": "Customer ke offers, loyalty conversions, aur campaigns par action points and response rate ka percentage evaluation score.",
            "term_aliases": ["Campaign Affinity Score", "Affinity Score", "campaign_affinity_score"],
            "manual_reference": "Volume 2 > Manager Guide",
            "training_reference": "TRN-CIG-AFFINITY",
            "related_formulas": ["TST-AFFINITY"],
            "related_terms": ["CIG"],
            "faq": [
                {"q": "What count factors go into Campaign Affinity?", "a": "Total coupon scans, wins, and benefits EARN transactions count in ledger."}
            ],
            "common_mistakes": [
                {"mistake": "Ignoring zero-score customers in promotions", "a": "Zero-score customers might just be new; target them with basic onboarding campaigns."}
            ],
            "formula_definition_ref": "TST-AFFINITY",
            "formula_version": "1.0.0",
            "explainability_note": "Calculated dynamically from Formula Registry definition TST-AFFINITY based on response touchpoints."
        },
        {
            "term_id": "clienteling",
            "term_name": "Customer Clienteling",
            "term_category": "Customer",
            "definition": "Clienteling is the personalization process where retail staff use customer insights, preferences, and predictions to drive sales and retention.",
            "hinglish_definition": "Store staff dwara purchase recommendations aur profile statistics use karke personal shopping experience aur retention badhane ki clienteling facility.",
            "term_aliases": ["Clienteling", "Customer Clienteling", "Clienteling Studio"],
            "manual_reference": "Volume 1 > Daily Operations",
            "training_reference": "TRN-CIG-CLIENTELING",
            "related_formulas": [],
            "related_terms": ["CIG"],
            "faq": [
                {"q": "Where do I access the Clienteling Studio?", "a": "Click the 'Clienteling Studio' link in the Navy sidebar navigation."}
            ],
            "common_mistakes": [
                {"mistake": "Sharing customer override PINs for clienteling features", "a": "Counter staff only need Cashier access; manager override PINs are not required for clienteling view."}
            ],
            "formula_definition_ref": None,
            "formula_version": None,
            "explainability_note": "A SMRITI-First interface overlays purchase predictions and customer metrics to assist counter salesman checkout decisions."
        }
    ]

    # Pre-process lists to JSON strings to match DocType schema
    for t in intelligence_terms:
        t.setdefault("dictionary_key", "")
        t.setdefault("projection_path", "")
        t.setdefault("entity_type", "")
        t.setdefault("data_type", "String")
        t.setdefault("measure_or_dimension", "Dimension")
        t.setdefault("is_groupable", 0)
        t.setdefault("is_filterable", 0)
        t.setdefault("is_reportable", 0)
        t.setdefault("default_aggregation", "None")
        t.setdefault("approval_status", "Approved")
        t.setdefault("dictionary_version", "1.0")

    print(f"Phase 1: Seeding {len(intelligence_terms)} SMRITI Business Dictionary intelligence terms...")
    for t in intelligence_terms:
        exists_name = frappe.db.exists("SMRITI Business Term", {"term_id": t["term_id"], "term_version": t["dictionary_version"]})
        
        # Safe lookup for formula definition reference link
        formula_ref_doc = None
        if t["formula_definition_ref"]:
            formula_ref_doc = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": t["formula_definition_ref"]})

        fields_dict = {
            "doctype": "SMRITI Business Term",
            "term_id": t["term_id"],
            "term_name": t["term_name"],
            "term_category": t["term_category"],
            "term_version": t["dictionary_version"],
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-22",
            "definition": t["definition"],
            "hinglish_definition": t["hinglish_definition"],
            "term_aliases": json.dumps(t["term_aliases"]),
            "manual_reference": t["manual_reference"],
            "training_reference": t["training_reference"],
            "faq": json.dumps(t["faq"]),
            "common_mistakes": json.dumps(t["common_mistakes"]),
            "dictionary_key": t["dictionary_key"],
            "projection_path": t["projection_path"],
            "entity_type": t["entity_type"],
            "data_type": t["data_type"],
            "measure_or_dimension": t["measure_or_dimension"],
            "is_groupable": t["is_groupable"],
            "is_filterable": t["is_filterable"],
            "is_reportable": t["is_reportable"],
            "default_aggregation": t["default_aggregation"],
            "approval_status": t["approval_status"],
            "dictionary_version": t["dictionary_version"],
            "formula_definition_ref": formula_ref_doc,
            "formula_version": t["formula_version"],
            "explainability_note": t["explainability_note"]
        }

        if not exists_name:
            doc = frappe.get_doc(fields_dict)
            doc.insert(ignore_permissions=True)
            print(f" - [Phase 1 Seeded] Term: {t['term_id']}")
        else:
            doc = frappe.get_doc("SMRITI Business Term", exists_name)
            doc.update(fields_dict)
            doc.save(ignore_permissions=True)
            print(f" - [Phase 1 Updated] Term: {t['term_id']}")

    frappe.db.commit()

    print("Phase 2: Updating SMRITI Business Dictionary intelligence terms relations...")
    for t in intelligence_terms:
        doc_name = frappe.db.get_value("SMRITI Business Term", {"term_id": t["term_id"], "term_version": t["dictionary_version"]})
        if doc_name:
            doc = frappe.get_doc("SMRITI Business Term", doc_name)
            
            # Clear existing child table rows first to make execution idempotent
            doc.set("related_formulas", [])
            doc.set("related_terms", [])

            # Append formulas
            for fid in t["related_formulas"]:
                formula_doc_name = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": fid})
                if formula_doc_name:
                    doc.append("related_formulas", {
                        "doctype": "SMRITI Related Formula",
                        "formula_id": formula_doc_name
                    })
                else:
                    print(f"   ! [Formula Missing] Skip link for: {fid}")

            # Append related terms
            for rtid in t["related_terms"]:
                related_doc_name = frappe.db.get_value("SMRITI Business Term", {"term_id": rtid, "term_version": "1.0"})
                if not related_doc_name:
                    related_doc_name = frappe.db.get_value("SMRITI Business Term", {"term_id": rtid})
                if related_doc_name:
                    doc.append("related_terms", {
                        "doctype": "SMRITI Related Term",
                        "related_term_id": related_doc_name
                    })
                else:
                    print(f"   ! [Term Missing] Skip link for: {rtid}")

            doc.save(ignore_permissions=True)
            print(f" - [Phase 2 Updated] Term Relations: {t['term_id']}")

    frappe.db.commit()
    print("SMRITI Business Dictionary intelligence terms seeding complete!")
