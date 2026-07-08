# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/api.py
# @desc:    SMRITI Core API — whitelisted backend endpoints for the JS adapter.
#           These are the server-side targets for smriti.api.get/getList/save/delete
#           calls from smriti_core.js. Business code never calls these directly —
#           they exist purely as the HTTP bridge between the JS adapter and the
#           SMRITI Core Framework.
#
#           JS Usage (smriti_core.js):
#               smriti.api.get("Customer", "CUST-001")
#               smriti.api.getList("Customer", { filters: {...}, fields: [...] })
#               smriti.api.save("Customer", data)
#               smriti.api.delete("Customer", "CUST-001")
#               smriti.api.schema("Purchase")
#
#           Architecture:
#               www/ JS  →  smriti.api.*  →  core/api.py  →  smriti.*  →  core/platform/  →  Frappe
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe                            # whitelist decorator only
from frappe import _
from smriti_retail_os import smriti


# ── smriti.api.get ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get(model: str, name: str) -> dict:
    """
    Fetch a single SMRITI document by model name and document name.

    JS: smriti.api.get("Customer", "CUST-001")
        → GET smriti_retail_os.core.api.get?model=Customer&name=CUST-001

    Args:
        model (str): SMRITI model name (e.g. "Customer", "Purchase")
        name (str):  Document name / ID

    Returns:
        dict: Document fields as a JSON-serializable dict
    """
    smriti.permissions.require(model, "read")
    doc = smriti.documents.get(model, name)
    return doc.as_dict()


# ── smriti.api.getField ────────────────────────────────────────────────────────

@frappe.whitelist()
def get_field(model: str, name: str, fieldname: str):
    """
    Fetch a single field value from a SMRITI document.

    JS: smriti.api.getField("Customer", "CUST-001", "credit_limit")

    Args:
        model (str):     SMRITI model name
        name (str):      Document name / ID
        fieldname (str): Field to fetch

    Returns:
        The field value (scalar)
    """
    smriti.permissions.require(model, "read")
    # db.get(model, name, fields) — passing single string field returns scalar
    return smriti.db.get(model, name, fieldname)


# ── smriti.api.getList ─────────────────────────────────────────────────────────

@frappe.whitelist()
def get_list(model: str, filters: dict = None, fields: list = None,
             order_by: str = None, limit: int = 20, start: int = 0) -> list:
    """
    Fetch a filtered list of SMRITI documents.

    JS: smriti.api.getList("Customer", {
            filters: { territory: "South" },
            fields: ["name", "customer_name", "territory"],
            limit: 50
        })

    Args:
        model (str):     SMRITI model name
        filters (dict):  Filter dict {fieldname: value} or Frappe-style list filters
        fields (list):   Fields to include (default: ["name"])
        order_by (str):  Sort expression (e.g. "modified desc")
        limit (int):     Max rows to return (default: 20, max: 200)
        start (int):     Offset for pagination

    Returns:
        list[dict]: List of document dicts
    """
    smriti.permissions.require(model, "read")
    limit = min(int(limit or 20), 200)   # cap at 200 rows
    return smriti.db.get_list(
        model,
        filters=filters or {},
        fields=fields or ["name"],
        order_by=order_by,
        limit=limit,
        start=start,
    )


# ── smriti.api.exists ──────────────────────────────────────────────────────────

@frappe.whitelist()
def exists(model: str, name: str) -> bool:
    """
    Check if a SMRITI document exists.

    JS: smriti.api.exists("Customer", "CUST-001")

    Returns:
        bool
    """
    smriti.permissions.require(model, "read")
    return bool(smriti.db.exists(model, name))


# ── smriti.api.save ────────────────────────────────────────────────────────────

@frappe.whitelist()
def save(model: str, data: dict) -> dict:
    """
    Save (create or update) a SMRITI document.

    JS: smriti.api.save("Customer", { name: "CUST-001", customer_name: "Ravi Stores" })
        → POST smriti_retail_os.core.api.save

    For new documents, omit 'name' or pass name="".
    For existing documents, include 'name'.

    Args:
        model (str):  SMRITI model name
        data (dict):  Document fields

    Returns:
        dict: Saved document as dict (includes name, modified, etc.)
    """
    name = data.get("name")
    if name and smriti.db.exists(model, name):
        smriti.permissions.require(model, "write")
        doc = smriti.documents.get(model, name)
        doc.update(data)
    else:
        smriti.permissions.require(model, "create")
        doc = smriti.documents.new(model)
        doc.update(data)

    doc.save(ignore_permissions=False)
    return doc.as_dict()


# ── smriti.api.submit ──────────────────────────────────────────────────────────

@frappe.whitelist()
def submit(model: str, name: str) -> dict:
    """
    Submit (post) a SMRITI document.

    JS: smriti.api.submit("Purchase", "PO-2026-00001")

    Args:
        model (str): SMRITI model name
        name (str):  Document name to submit

    Returns:
        dict: Submitted document as dict
    """
    smriti.permissions.require(model, "submit")
    doc = smriti.documents.get(model, name)
    smriti.documents.submit(doc)
    return doc.as_dict()


# ── smriti.api.delete ──────────────────────────────────────────────────────────

@frappe.whitelist()
def delete(model: str, name: str) -> dict:
    """
    Delete a SMRITI document.

    JS: smriti.api.delete("Customer", "CUST-001")

    Args:
        model (str): SMRITI model name
        name (str):  Document name to delete

    Returns:
        dict: {"ok": True, "deleted": name}
    """
    smriti.permissions.require(model, "delete")
    smriti.documents.delete(model, name)
    return {"ok": True, "deleted": name}


# ── smriti.api.schema ──────────────────────────────────────────────────────────

@frappe.whitelist()
def schema(model: str) -> dict:
    """
    Return the SMRITI Form Engine schema for a model.
    Used by the JS Form Renderer to build the form UI.

    JS: smriti.api.schema("Purchase")
        → { model: "Purchase", title: "Purchase Order", fields: [...] }

    The schema is cached per model for 60 seconds.

    Args:
        model (str): SMRITI model name

    Returns:
        dict: Form schema (model, title, fields list)
    """
    cache_key = f"smriti_form_schema_{model}"

    def _build():
        from smriti_retail_os.core.forms.retail_forms import (
            PurchaseForm, CustomerForm, ProductForm, GRNForm
        )
        _form_map = {
            "Purchase":  PurchaseForm,
            "Customer":  CustomerForm,
            "Product":   ProductForm,
            "GRN":       GRNForm,
        }
        form_class = _form_map.get(model)
        if not form_class:
            # raise_not_found(model_name, identifier)
            smriti.errors.raise_not_found(model, f"{model} (no schema registered)")
        return form_class().schema()

    return smriti.cache.get_or_set(cache_key, _build, ttl=60)


# ── smriti.api.lookup ──────────────────────────────────────────────────────────

@frappe.whitelist()
def lookup(model: str, query: str = "", filters: dict = None,
           display_field: str = "name", limit: int = 20) -> list:
    """
    Typeahead / lookup search for a SMRITI model.
    Used by LookupField in the JS Form Renderer.

    JS: smriti.api.lookup("Supplier", { query: "raj", display_field: "supplier_name" })
        → [{ value: "SUP-001", label: "Raj Traders" }, ...]

    Args:
        model (str):         SMRITI model name
        query (str):         Search string (applied to 'name' and display_field)
        filters (dict):      Additional static filters
        display_field (str): Field to use as display label
        limit (int):         Max results (default 20, max 50)

    Returns:
        list[dict]: [{"value": name, "label": display_value}, ...]
    """
    smriti.permissions.require(model, "read")
    limit = min(int(limit or 20), 50)

    search_filters = dict(filters or {})
    if query:
        search_filters["name"] = ["like", f"%{query}%"]

    fields = list({"name", display_field})
    rows = smriti.db.get_list(model, filters=search_filters, fields=fields, limit=limit)

    return [
        {"value": r.get("name"), "label": r.get(display_field) or r.get("name")}
        for r in rows
    ]


# ── smriti.api.on_change ───────────────────────────────────────────────────────

@frappe.whitelist()
def on_change(model: str, field_name: str, value=None, data: dict = None) -> dict:
    """
    Delegate a field-change event to the registered form's lifecycle on_change hook.
    Returns dependent field updates for the JS renderer to apply.

    Called automatically by SmritiFormRenderer (smriti_form_renderer.js) when
    any field value changes.

    JS: automatically called — POST smriti_retail_os.core.api.on_change

    Args:
        model (str):      SMRITI model name (e.g. "Purchase")
        field_name (str): Name of the field that changed
        value:            New field value
        data (dict):      Current full form data

    Returns:
        dict: {field_name: new_value} for any dependent fields to update in the UI.
              Returns {} if no updates needed or no lifecycle registered.

    Example (Purchase supplier change auto-fills payment_terms):
        on_change("Purchase", "supplier", "SUP-001", {...})
        → {"payment_terms": "Net 30"}
    """
    from smriti_retail_os.core.forms.retail_forms import (
        PurchaseForm, CustomerForm, ProductForm, GRNForm
    )
    _form_map = {
        "Purchase": PurchaseForm,
        "Customer": CustomerForm,
        "Product":  ProductForm,
        "GRN":      GRNForm,
    }
    form_class = _form_map.get(model)
    if not form_class or not form_class.LIFECYCLE:
        return {}

    try:
        result = form_class.LIFECYCLE.on_change(field_name, value, data or {})
        return result or {}
    except Exception as e:
        smriti.errors.log_error(
            "Form on_change failed",
            exc=e,
            context={"model": model, "field": field_name}
        )
        return {}
