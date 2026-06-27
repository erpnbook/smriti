# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/formula_service.py
# @description: SMRITI Formula Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
import json

FORMULA_INDEX = {
    "INV-001",
    "INV-002",
    "INV-003",
    "INV-004",
    "INV-005",
    "FRC-001",
    "OHS-001",
    "TRF-001",
    "SAL-001",
    "AUD-001",
    "VAR-001",
    "KGF-001",
    "SMRITI-SCAN-REL-01",
    "SMRITI-PRN-SCORE-01",
    "TR-HLTH-01"
}

@frappe.whitelist()
def get_active_formulas(category=None):
    """
    Returns list of active and approved formula definitions.
    Optionally filters by formula_category.
    """
    filters = {"is_active": 1, "status": "Approved"}
    if category:
        filters["formula_category"] = category

    formulas = frappe.get_all(
        "SMRITI Formula Definition",
        filters=filters,
        fields=[
            "name", "formula_id", "formula_name", "formula_version",
            "formula_category", "formula_expression", "effective_date",
            "business_owner", "technical_owner", "business_meaning",
            "worked_example", "interpretation_guide", "recommended_action",
            "explainability_json", "implementation_reference", "dependent_features"
        ],
        order_by="formula_id asc, formula_version desc"
    )

    # Decode JSON fields
    for f in formulas:
        if f.get("explainability_json"):
            try:
                f["explainability_json"] = json.loads(f["explainability_json"])
            except ValueError:
                pass
        if f.get("dependent_features"):
            try:
                f["dependent_features"] = json.loads(f["dependent_features"])
            except ValueError:
                pass
        if f.get("variables_and_inputs"):
            try:
                f["variables_and_inputs"] = json.loads(f["variables_and_inputs"])
            except ValueError:
                pass

    return formulas

@frappe.whitelist()
def get_formula_detail(formula_id, version=None):
    """
    Retrieves the detailed definition of a specific formula ID.
    If version is not provided, defaults to the active/approved one.
    """
    # 1. Enforce Registry Check (Governance Gate)
    if formula_id not in FORMULA_INDEX:
        is_test_bypass = frappe.flags.in_test and formula_id.startswith("TST-")
        if not is_test_bypass:
            frappe.throw(
                frappe._("Formula {0} is not registered in the Formula Registry.").format(formula_id),
                frappe.PermissionError
            )

    filters = {"formula_id": formula_id}
    if version:
        filters["formula_version"] = version

    docs = frappe.get_all(
        "SMRITI Formula Definition",
        filters=filters,
        fields=["name", "status", "is_active"],
        order_by="is_active desc, status desc, formula_version desc"
    )

    if not docs:
        frappe.throw(
            frappe._("Formula {0} not found in the registry (version: {1}).")
            .format(formula_id, version or "Active")
        )

    # 2. Enforce Role-Based Permissions & Document Status/Active Checks
    if "System Manager" not in frappe.get_roles():
        # Find the first active and approved version
        target_doc_name = None
        for d in docs:
            if d.status == "Approved" and d.is_active == 1:
                target_doc_name = d.name
                break
        
        if not target_doc_name:
            frappe.throw(
                frappe._("Not permitted to view this formula (Draft/Inactive)."),
                frappe.PermissionError
            )
        doc = frappe.get_doc("SMRITI Formula Definition", target_doc_name)
    else:
        # System Managers can view any retrieved version
        doc = frappe.get_doc("SMRITI Formula Definition", docs[0]["name"])

    return doc

def validate_formula_registered(formula_id):
    """
    Checks if a formula_id exists and is active/approved in the registry.
    Returns True if valid, False otherwise.
    """
    if not formula_id:
        return False

    exists = frappe.db.exists(
        "SMRITI Formula Definition",
        {
            "formula_id": formula_id,
            "is_active": 1,
            "status": "Approved"
        }
    )
    return bool(exists)

def calculate_kgf_coverage():
    """
    Calculates KGF Coverage % based on total expected dashboard metrics (12).
    """
    total_kpis = 14
    registered_kpis = frappe.db.count(
        "SMRITI Formula Definition",
        {
            "is_active": 1,
            "status": "Approved"
        }
    )
    if not total_kpis:
        return 0.0
    return round((registered_kpis / total_kpis) * 100, 2)

