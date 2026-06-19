# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/formula_service.py
# @description: Handles user login, registration, and JWT token generation.
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
    filters = {"formula_id": formula_id}
    if version:
        filters["formula_version"] = version
    else:
        filters["is_active"] = 1
        filters["status"] = "Approved"

    docs = frappe.get_all(
        "SMRITI Formula Definition",
        filters=filters,
        fields=["name"],
        limit=1
    )

    if not docs:
        frappe.throw(
            frappe._("Formula {0} not found in the registry (version: {1}).")
            .format(formula_id, version or "Active")
        )

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
