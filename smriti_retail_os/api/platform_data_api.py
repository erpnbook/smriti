"""
smriti_retail_os.api.platform_data_api
======================================

Generic data access API for SMRITI standalone pages.

Provides Guard 6-compliant endpoints that wrap frappe.client methods,
so www/ pages never reference ``frappe.client.*`` directly.

SMRITI Architecture:  www/ JS  →  smriti.api.call()  →  this API  →  frappe.client

Author:  SMRITI Architecture Team
License: GPL-3.0-only
"""

import frappe


@frappe.whitelist()
def get_records(doctype: str, fields: list = None, filters: dict = None,
                order_by: str = None, limit: int = 20, start: int = 0) -> list:
    """
    Fetch a list of records from a DocType.

    This is the Guard 6-compliant replacement for ``frappe.client.get_list``
    calls in www/ pages. Internally delegates to ``frappe.get_list``.

    Args:
        doctype:  The DocType name.
        fields:   List of field names to return. Defaults to ["name"].
        filters:  Dict of {field: value} filter conditions.
        order_by: Sort expression, e.g. "creation desc".
        limit:    Max records to return (capped at 500).
        start:    Pagination offset.

    Returns:
        list[dict]: List of matching records.
    """
    limit = min(int(limit or 20), 500)
    return frappe.get_list(
        doctype,
        fields=fields or ["name"],
        filters=filters or {},
        order_by=order_by,
        limit_page_length=limit,
        limit_start=int(start or 0),
        ignore_permissions=False,
    )


@frappe.whitelist()
def get_value(doctype: str, filters: dict = None, fieldname=None, name: str = None) -> dict:
    """
    Fetch a single value or set of values from a DocType or Single DocType.

    Guard 6-compliant replacement for ``frappe.client.get_value``.

    Args:
        doctype:   The DocType name.
        filters:   Dict filter or None if using name.
        fieldname: Field name(s) to return — string or list.
        name:      Document name (alternative to filters).

    Returns:
        dict: The requested field values.
    """
    is_single = False
    try:
        is_single = frappe.get_meta(doctype).issingle
    except Exception:
        pass

    if is_single:
        doc = frappe.get_single(doctype)
        if isinstance(fieldname, list):
            return {fn: doc.get(fn) for fn in fieldname}
        elif fieldname:
            return {fieldname: doc.get(fieldname)}
        else:
            return doc.as_dict()

    if name:
        filters = {"name": name}
    val = frappe.db.get_value(
        doctype,
        filters=filters or {},
        fieldname=fieldname or "name",
        as_dict=True,
    )
    return val or {}


@frappe.whitelist()
def get_count(doctype: str, filters: dict = None) -> int:
    """
    Count records matching a filter.

    Guard 6-compliant replacement for ``frappe.client.get_count``.

    Args:
        doctype: The DocType name.
        filters: Dict filter conditions.

    Returns:
        int: Count of matching records.
    """
    return frappe.db.count(doctype, filters=filters or {})


@frappe.whitelist()
def set_value(doctype: str, name: str, fieldname: str = None, value=None) -> dict:
    """
    Set a field value on a document.

    Guard 6-compliant replacement for ``frappe.client.set_value``.

    Args:
        doctype:   The DocType name.
        name:      The document name.
        fieldname: The field to update.
        value:     The new value.

    Returns:
        dict: The updated document fields.
    """
    frappe.set_value(doctype, name, fieldname, value)
    return frappe.get_doc(doctype, name).as_dict()


@frappe.whitelist()
def delete_record(doctype: str, name: str) -> dict:
    """
    Delete a document.

    Guard 6-compliant replacement for ``frappe.client.delete``.

    Args:
        doctype: The DocType name.
        name:    The document name to delete.

    Returns:
        dict: Status confirmation.
    """
    frappe.delete_doc(doctype, name, ignore_permissions=False)
    return {"status": "ok", "doctype": doctype, "name": name}


@frappe.whitelist()
def cancel_record(doctype: str, name: str) -> dict:
    """
    Cancel a submitted document.

    Guard 6-compliant replacement for ``frappe.client.cancel``.

    Args:
        doctype: The DocType name.
        name:    The document name to cancel.

    Returns:
        dict: The cancelled document.
    """
    doc = frappe.get_doc(doctype, name)
    doc.cancel()
    return doc.as_dict()


@frappe.whitelist()
def get_all(doctype: str, fields: list = None, filters: dict = None,
            order_by: str = None, limit: int = 20) -> list:
    """
    Fetch all records (alias for get_records).

    Guard 6-compliant replacement for ``frappe.client.get_all``.

    Args:
        doctype:  The DocType name.
        fields:   Fields to return.
        filters:  Filter conditions.
        order_by: Sort expression.
        limit:    Max records.

    Returns:
        list[dict]: Matching records.
    """
@frappe.whitelist()
def create_terms_and_conditions(title: str, terms: str) -> dict:
    """
    Creates a new Terms and Conditions master record on the fly.
    """
    if not title or not terms:
        frappe.throw("Both title and terms details are required.")
    
    if frappe.db.exists("Terms and Conditions", title):
        doc = frappe.get_doc("Terms and Conditions", title)
        doc.terms = terms
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Terms and Conditions")
        doc.title = title
        doc.terms = terms
        doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
    return {"name": doc.name, "title": doc.title, "terms": doc.terms}


@frappe.whitelist()
def create_quick_item_master(item_code: str, item_name: str = None, item_group: str = "All Item Groups", rate: float = 0.0) -> dict:
    """
    Creates a new Item master record on the fly.
    """
    if not item_code:
        frappe.throw("Item Code / Article is required.")

    item_code = item_code.strip()
    if frappe.db.exists("Item", item_code):
        doc = frappe.get_doc("Item", item_code)
    else:
        doc = frappe.new_doc("Item")
        doc.item_code = item_code
        doc.item_name = item_name or item_code
        doc.item_group = item_group
        doc.stock_uom = "Nos"
        doc.valuation_rate = float(rate or 0)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

    return {"item_code": doc.item_code, "item_name": doc.item_name, "rate": doc.valuation_rate}

