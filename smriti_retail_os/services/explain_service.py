# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/explain_service.py
# @description: SMRITI Explain Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.utils import now_datetime

def get_explain_payload(formula_id, version=None):
    """
    Retrieves the formula definition details, checking Redis cache first.
    Also logs an audit record to SMRITI PSV Activity Log.
    """
    if not formula_id:
        frappe.throw(frappe._("Formula ID is required."))

    # 1. Determine active version if not specified
    if not version:
        version = frappe.db.get_value(
            "SMRITI Formula Definition",
            {"formula_id": formula_id, "is_active": 1, "status": "Approved"},
            "formula_version"
        )
        if not version:
            frappe.throw(
                frappe._("Active, Approved Formula Definition not found for ID: {0}").format(formula_id)
            )

    # 2. Check Redis Cache
    cache_key = f"smriti:explain:{formula_id}:{version}"
    cached_data = frappe.cache().get_value(cache_key)
    if cached_data:
        payload = json.loads(cached_data)
        # Log audit trail for cache hits too
        log_explain_audit(formula_id, version, payload.get("formula_category"))
        return payload

    # 3. Cache Miss: Fetch from DB
    docs = frappe.get_all(
        "SMRITI Formula Definition",
        filters={"formula_id": formula_id, "formula_version": version},
        fields=[
            "name", "formula_id", "formula_name", "formula_version",
            "formula_category", "formula_expression", "formula_language",
            "business_meaning", "worked_example", "interpretation_guide",
            "recommended_action", "implementation_reference", "dependent_features",
            "effective_date", "business_owner", "explainability_json"
        ],
        limit=1
    )

    if not docs:
        frappe.throw(
            frappe._("Formula Definition not found for ID: {0} and Version: {1}").format(formula_id, version)
        )

    doc = docs[0]
    formula_category = doc.get("formula_category")

    # 4. Fetch related formulas (same category, different ID)
    related_docs = frappe.get_all(
        "SMRITI Formula Definition",
        filters={
            "is_active": 1,
            "status": "Approved",
            "formula_category": formula_category,
            "formula_id": ["!=", formula_id]
        },
        fields=["formula_id", "formula_name"],
        limit=3
    )
    related_formula_ids = [r["formula_id"] for r in related_docs]

    # 5. Build payload
    payload = {
        "formula_id": doc.get("formula_id"),
        "formula_name": doc.get("formula_name"),
        "formula_version": doc.get("formula_version"),
        "formula_category": formula_category,
        "formula_expression": doc.get("formula_expression"),
        "formula_language": doc.get("formula_language"),
        "business_meaning": doc.get("business_meaning"),
        "worked_example": doc.get("worked_example"),
        "interpretation_guide": doc.get("interpretation_guide"),
        "recommended_action": doc.get("recommended_action"),
        "implementation_reference": doc.get("implementation_reference"),
        "effective_date": str(doc.get("effective_date")) if doc.get("effective_date") else "",
        "business_owner": doc.get("business_owner"),
        "related_formula_ids": related_formula_ids,
        "dependent_features": [],
        "explainability_json": {}
    }

    if doc.get("dependent_features"):
        try:
            payload["dependent_features"] = json.loads(doc.get("dependent_features"))
        except ValueError:
            payload["dependent_features"] = [doc.get("dependent_features")]

    if doc.get("explainability_json"):
        try:
            payload["explainability_json"] = json.loads(doc.get("explainability_json"))
        except ValueError:
            pass

    # 6. Save to Redis Cache (TTL = 3600 seconds)
    frappe.cache().set_value(cache_key, json.dumps(payload), expires_in_sec=3600)

    # 7. Log Audit Record
    log_explain_audit(formula_id, version, formula_category)

    return payload

def log_explain_audit(formula_id, version, category):
    """
    Helper to write an immutable entry to SMRITI PSV Activity Log.
    """
    # Fetch IP Address
    ip_addr = "127.0.0.1"
    if hasattr(frappe.local, "request_ip") and frappe.local.request_ip:
        ip_addr = frappe.local.request_ip

    log = frappe.get_doc({
        "doctype": "SMRITI PSV Activity Log",
        "timestamp": now_datetime(),
        "user": frappe.session.user or "Administrator",
        "action_type": "Formula Explained",
        "event_type": "FORMULA_EXPLAINED",
        "reference_doctype": "SMRITI Formula Definition",
        "reference_name": formula_id,
        "ip_address": ip_addr,
        "details": f"Version: {version}, Category: {category}"
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()
