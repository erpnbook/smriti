# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/documents.py
# @desc:    SMRITI Platform Document Adapter.
#           Wraps all Frappe document-level operations behind SMRITI model names.
#
#           Usage (correct):
#               from smriti_retail_os.core.platform import documents
#               doc = documents.get("Customer", "CUST-001")
#               orders = documents.get_all("Purchase", filters={"status": "Draft"})
#
#           Usage (forbidden — never do this outside this file):
#               smriti.documents.get("Customer", "CUST-001")     ← VIOLATION
#               smriti.db.get_list("Purchase Order", ...)       ← VIOLATION
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

# smriti-platform-core: this module IS the frappe abstraction layer — Guard 6 exempt by design
from smriti_retail_os.core.platform.registry import resolve


def get(model_name: str, name: str = None, **kwargs):
    """
    Fetch a single document by model name and document name.

    Args:
        model_name (str): SMRITI model name, e.g. "Customer", "Purchase"
        name (str): Document name / ID, e.g. "CUST-001", "PO-2026-00001"
        **kwargs: Additional kwargs forwarded to the ORM layer

    Returns:
        frappe.Document: The loaded document object

    Example:
        doc = documents.get("Customer", "CUST-001")
        print(doc.customer_name)
    """
    import frappe
    if name is None:
        return frappe.get_doc(resolve(model_name), **kwargs)
    return frappe.get_doc(resolve(model_name), name, **kwargs)  # smriti-platform-core


def get_all(model_name: str, filters=None, fields=None, **kwargs):
    """
    Fetch a list of documents matching the given filters.

    Args:
        model_name (str): SMRITI model name, e.g. "Product", "Purchase"
        filters (dict|list): Filter conditions
        fields (list): Fields to return (default: ["name"])
        **kwargs: Additional kwargs forwarded to the ORM layer

    Returns:
        list[dict]: List of matching documents as dicts

    Example:
        products = documents.get_all("Product",
            filters={"item_group": "Electronics"},
            fields=["name", "item_name", "standard_rate"]
        )
    """
    import frappe
    kwargs_merged = {}
    if filters is not None:
        kwargs_merged["filters"] = filters
    if fields is not None:
        kwargs_merged["fields"] = fields
    kwargs_merged.update(kwargs)
    return frappe.get_all(resolve(model_name), **kwargs_merged)


def get_list(model_name: str, filters=None, fields=None, **kwargs):
    """
    Fetch a list of documents with permission enforcement (alias of get_all for
    permission-sensitive calls).
    """
    import frappe
    kwargs_merged = {}
    if filters is not None:
        kwargs_merged["filters"] = filters
    if fields is not None:
        kwargs_merged["fields"] = fields
    kwargs_merged.update(kwargs)
    return frappe.get_list(resolve(model_name), **kwargs_merged)


def new(model_name: str):
    """
    Create a new, unsaved document of the given SMRITI model.

    Args:
        model_name (str): SMRITI model name, e.g. "Purchase"

    Returns:
        frappe.Document: New, unsaved document object

    Example:
        po = documents.new("Purchase")
        po.supplier = "SUP-001"
        po.save()
    """
    import frappe
    return frappe.new_doc(resolve(model_name))


def create(model_name: str, **kwargs):
    """
    Create and insert a new document from keyword arguments.

    Args:
        model_name (str): SMRITI model name
        **kwargs: Document fields

    Returns:
        frappe.Document: The inserted document
    """
    doc_dict = {"doctype": model_name}
    doc_dict.update(kwargs)
    doc = new_from_dict(doc_dict)
    return insert(doc)


def new_from_dict(doc_dict: dict, **kwargs):
    """
    Create a new, unsaved document from a dictionary of fields.

    Args:
        doc_dict (dict): Document dict containing fields and 'doctype'

    Returns:
        frappe.Document: Document object
    """
    import frappe
    if "doctype" in doc_dict:
        doc_dict = doc_dict.copy()
        doc_dict["doctype"] = resolve(doc_dict["doctype"])
    return frappe.get_doc(doc_dict)


def save(doc) -> object:
    """
    Save a document (insert if new, update if existing).

    Args:
        doc (frappe.Document): Document object to save

    Returns:
        frappe.Document: The saved document (same object, with updated fields)

    Example:
        doc = documents.get("Customer", "CUST-001")
        doc.credit_limit = 50000
        documents.save(doc)
    """
    doc.save()
    return doc


def insert(doc) -> object:
    """
    Insert a new document into the database.

    Args:
        doc (frappe.Document): New document to insert

    Returns:
        frappe.Document: The inserted document

    Example:
        po = documents.new("Purchase")
        po.supplier = "SUP-001"
        documents.insert(po)
    """
    doc.insert()
    return doc


def submit(doc) -> object:
    """
    Submit a document (moves it to submitted state, creates accounting entries).

    Args:
        doc (frappe.Document): Document to submit (must be in Saved state)

    Returns:
        frappe.Document: The submitted document

    Example:
        grn = documents.get("PurchaseReceipt", "GRN-2026-00001")
        documents.submit(grn)
    """
    doc.submit()
    return doc


def cancel(doc) -> object:
    """
    Cancel a submitted document.

    Args:
        doc (frappe.Document): Submitted document to cancel

    Returns:
        frappe.Document: The cancelled document
    """
    doc.cancel()
    return doc


def delete(model_name: str, name: str, force: bool = False, ignore_missing: bool = False):
    """
    Delete a document permanently.

    Args:
        model_name (str): SMRITI model name
        name (str): Document name to delete
        force (bool): If True, bypasses permission checks (use sparingly)
        ignore_missing (bool): If True, does not raise if document not found

    Example:
        documents.delete("Customer", "CUST-DRAFT-001")
    """
    import frappe
    frappe.delete_doc(
        resolve(model_name),
        name,
        force=force,
        ignore_missing=ignore_missing
    )


def reload(doc) -> object:
    """
    Reload a document from the database, discarding unsaved local changes.

    Args:
        doc (frappe.Document): Document to reload

    Returns:
        frappe.Document: The reloaded document
    """
    doc.reload()
    return doc


def get_value(model_name: str, name: str, fieldname: str):
    """
    Fetch a single field value from a document.

    Args:
        model_name (str): SMRITI model name
        name (str): Document name
        fieldname (str): Field to read

    Returns:
        The field value

    Example:
        credit_limit = documents.get_value("Customer", "CUST-001", "credit_limit")
    """
    import frappe
    return frappe.db.get_value(resolve(model_name), name, fieldname)


def get_single(model_name: str):
    """
    Fetch a singleton document (DocType with is_single=1).

    Args:
        model_name (str): SMRITI model name of the singleton, e.g. "CGESettings"

    Returns:
        frappe.Document: The singleton document object

    Example:
        settings = documents.get_single("CGESettings")
        settings.some_setting
    """
    import frappe
    return frappe.get_single(resolve(model_name))


def get_raw(model_name: str, name: str) -> dict:
    """
    Fetch a document as a raw Python dictionary (no document object overhead).

    Args:
        model_name (str): SMRITI model name
        name (str): Document name / ID

    Returns:
        dict: Document fields as a plain dictionary

    Example:
        raw = documents.get_raw("Item", "ITEM-001")
        print(raw.get("item_name"))
    """
    import frappe
    doc = frappe.get_doc(resolve(model_name), name)
    return doc.as_dict()

