# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/dictionary_service.py
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

import json
import frappe
from frappe.utils import now_datetime

def get_active_terms(category=None):
    """
    Returns a list of all active, approved business terms.
    Optionally filtered by term_category.
    """
    filters = {"is_active": 1, "status": "Approved"}
    if category:
        filters["term_category"] = category

    terms = frappe.get_all(
        "SMRITI Business Term",
        filters=filters,
        fields=["name", "term_id", "term_name", "term_category", "definition", "term_version"],
        order_by="term_id asc"
    )
    return terms

def get_term_detail(term_id, version=None):
    """
    Fetches details of a dictionary term, checking Redis cache first.
    Logs an access entry in SMRITI PSV Activity Log.
    """
    if not term_id:
        frappe.throw(frappe._("Term ID is required."))

    # 1. Determine active version if not specified
    if not version:
        version = frappe.db.get_value(
            "SMRITI Business Term",
            {"term_id": term_id, "is_active": 1, "status": "Approved"},
            "term_version"
        )
        if not version:
            frappe.throw(
                frappe._("Active, Approved Business Term not found for ID: {0}").format(term_id)
            )

    # 2. Check Redis Cache
    cache_key = f"smriti:dictionary:{term_id}:{version}"
    cached_data = frappe.cache().get_value(cache_key)
    if cached_data:
        payload = json.loads(cached_data)
        log_dictionary_access(term_id, version, payload.get("term_category"))
        return payload

    # 3. Cache Miss: Fetch from DB
    docs = frappe.get_all(
        "SMRITI Business Term",
        filters={"term_id": term_id, "term_version": version},
        fields=[
            "name", "term_id", "term_name", "term_category", "term_version",
            "replaces_term_id", "term_aliases", "definition", "hinglish_definition",
            "faq", "common_mistakes", "manual_reference", "training_reference",
            "business_owner", "technical_owner", "effective_date"
        ],
        limit=1
    )

    if not docs:
        frappe.throw(
            frappe._("Business Term not found for ID: {0} and Version: {1}").format(term_id, version)
        )

    doc = docs[0]
    parent_name = doc["name"]
    category = doc.get("term_category")

    # 4. Fetch child tables
    formulas_list = frappe.get_all(
        "SMRITI Related Formula",
        filters={"parent": parent_name, "parenttype": "SMRITI Business Term"},
        fields=["formula_id"]
    )
    related_formulas = []
    for f in formulas_list:
        f_id = frappe.db.get_value("SMRITI Formula Definition", f["formula_id"], "formula_id")
        if f_id:
            related_formulas.append(f_id)

    terms_list = frappe.get_all(
        "SMRITI Related Term",
        filters={"parent": parent_name, "parenttype": "SMRITI Business Term"},
        fields=["related_term_id"]
    )
    related_terms = []
    for t in terms_list:
        rt_id = frappe.db.get_value("SMRITI Business Term", t["related_term_id"], "term_id")
        if rt_id:
            related_terms.append(rt_id)

    replaces_term = None
    if doc.get("replaces_term_id"):
        replaces_term = frappe.db.get_value("SMRITI Business Term", doc.get("replaces_term_id"), "term_id")

    # 5. Build payload
    payload = {
        "term_id": doc.get("term_id"),
        "term_name": doc.get("term_name"),
        "term_category": category,
        "term_version": doc.get("term_version"),
        "replaces_term_id": replaces_term,
        "definition": doc.get("definition"),
        "hinglish_definition": doc.get("hinglish_definition"),
        "manual_reference": doc.get("manual_reference"),
        "training_reference": doc.get("training_reference"),
        "business_owner": doc.get("business_owner"),
        "technical_owner": doc.get("technical_owner"),
        "effective_date": str(doc.get("effective_date")) if doc.get("effective_date") else "",
        "term_aliases": [],
        "faq": [],
        "common_mistakes": [],
        "related_formulas": related_formulas,
        "related_terms": related_terms
    }

    if doc.get("term_aliases"):
        try:
            payload["term_aliases"] = json.loads(doc.get("term_aliases"))
        except ValueError:
            payload["term_aliases"] = [doc.get("term_aliases")]

    if doc.get("faq"):
        try:
            payload["faq"] = json.loads(doc.get("faq"))
        except ValueError:
            pass

    if doc.get("common_mistakes"):
        try:
            payload["common_mistakes"] = json.loads(doc.get("common_mistakes"))
        except ValueError:
            pass

    # 6. Save to Redis Cache (TTL = 3600 seconds)
    frappe.cache().set_value(cache_key, json.dumps(payload), expires_in_sec=3600)

    # 7. Log Access Audit Record
    log_dictionary_access(term_id, version, category)

    return payload

def log_dictionary_access(term_id, version, category):
    """
    Writes an entry to SMRITI PSV Activity Log for auditing.
    """
    ip_addr = "127.0.0.1"
    if hasattr(frappe.local, "request_ip") and frappe.local.request_ip:
        ip_addr = frappe.local.request_ip

    log = frappe.get_doc({
        "doctype": "SMRITI PSV Activity Log",
        "timestamp": now_datetime(),
        "user": frappe.session.user or "Administrator",
        "action_type": "Dictionary Accessed",
        "event_type": "DICTIONARY_ACCESSED",
        "reference_doctype": "SMRITI Business Term",
        "reference_name": term_id,
        "ip_address": ip_addr,
        "details": f"Version: {version}, Category: {category}"
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()
