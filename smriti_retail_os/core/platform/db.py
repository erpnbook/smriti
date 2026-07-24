# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/db.py
# @desc:    SMRITI Platform Database Adapter.
#           Wraps all Frappe database-level operations (frappe.db.*) behind
#           SMRITI model names and a clean, consistent API.
#
#           Usage (correct):
#               from smriti_retail_os.core.platform import db
#               value = db.get("Customer", "CUST-001", "credit_limit")
#               exists = db.exists("Product", {"item_code": "ITEM-001"})
#
#           Usage (forbidden — never do this outside this file):
#               smriti.db.get(...)   ← VIOLATION
#               smriti.db.exists(...)      ← VIOLATION
#               smriti.db.sql(...)         ← VIOLATION (allowed only here)
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

# smriti-platform-core: this module IS the frappe abstraction layer — Guard 6 exempt by design
from smriti_retail_os.core.platform.registry import resolve


def get(model_name: str, name, fields="name", as_dict: bool = False, **kwargs):
    """
    Fetch one or more field values from a document.

    Args:
        model_name (str): SMRITI model name, e.g. "Customer"
        name (str|dict): Document name or filter dict
        fields (str|list): Single field name or list of field names
        as_dict (bool): If True and multiple fields, returns a dict
        **kwargs: Additional keyword arguments forwarded to the database layer (e.g. order_by, cache)

    Returns:
        Field value (single field) or dict (multiple fields)

    Example:
        limit = db.get("Customer", "CUST-001", "credit_limit")
        info = db.get("Customer", "CUST-001", ["customer_name", "credit_limit"])
    """
    import frappe
    return frappe.db.get_value(resolve(model_name), name, fields, as_dict=as_dict, **kwargs)


def get_single(model_name: str, fieldname: str):
    """
    Fetch a field from a Single DocType (no name required).

    Args:
        model_name (str): SMRITI model name of a Single DocType
        fieldname (str): Field to fetch

    Returns:
        Field value
    """
    import frappe
    return frappe.db.get_single_value(resolve(model_name), fieldname)


def get_list(model_name: str, filters=None, fields=None, order_by: str = None,
             limit: int = None, as_dict: bool = True, **kwargs):
    """
    Fetch multiple records from a document type.

    Args:
        model_name (str): SMRITI model name
        filters (dict|list): Filter conditions
        fields (list): Fields to return
        order_by (str): Order clause, e.g. "creation desc"
        limit (int): Maximum number of records
        as_dict (bool): Return as list of dicts
        **kwargs: Additional keyword arguments forwarded to the database layer (e.g. pluck)

    Returns:
        list[dict]: Matching records

    Example:
        customers = db.get_list("Customer",
            filters={"territory": "India"},
            fields=["name", "customer_name", "credit_limit"],
            order_by="customer_name asc"
        )
    """
    import frappe
    kwargs_merged = {}
    if filters is not None:
        kwargs_merged["filters"] = filters
    if fields is not None:
        kwargs_merged["fields"] = fields
    if order_by is not None:
        kwargs_merged["order_by"] = order_by
    if limit is not None:
        kwargs_merged["limit"] = limit
    if not as_dict:
        kwargs_merged["as_list"] = True
    kwargs_merged.update(kwargs)
    if "ignore_permissions" not in kwargs_merged:
        kwargs_merged["ignore_permissions"] = True
    return frappe.db.get_all(resolve(model_name), **kwargs_merged)



def set(model_name: str, name: str, field, value=None, **kwargs):
    """
    Update a single field value of a document in the database.

    Args:
        model_name (str): SMRITI model name
        name (str): Document name
        field (str): Field name to update
        value: New value
        **kwargs: Additional keyword arguments forwarded to the database layer (e.g. update_modified)

    Example:
        db.set("Customer", "CUST-001", "credit_limit", 150000)
    """
    import frappe
    frappe.db.set_value(resolve(model_name), name, field, value, **kwargs)


set_value = set


def exists(model_name: str, filters):
    """
    Check whether a document matching the given filters exists.

    Args:
        model_name (str): SMRITI model name
        filters (str|dict): Document name or filter dict

    Returns:
        str|None: Document name if exists, else None

    Example:
        if db.exists("Customer", {"mobile_no": "9876543210"}):
            ...
    """
    import frappe
    return frappe.db.exists(resolve(model_name), filters)


def count(model_name: str, filters=None, cache: bool = False) -> int:
    """
    Count documents matching the given filters.

    Args:
        model_name (str): SMRITI model name
        filters (dict|list): Filter conditions
        cache (bool): Use database cache

    Returns:
        int: Count of matching documents
    """
    import frappe
    return frappe.db.count(resolve(model_name), filters, cache=cache)


def delete(model_name: str, filters: dict):
    """
    Delete database records matching the given filters (direct DB delete, no hooks).
    Use sparingly — prefer documents.delete() for hook-aware deletion.

    Args:
        model_name (str): SMRITI model name
        filters (dict): Filter conditions

    Example:
        db.delete("StockTransfer", {"status": "Draft", "owner": "old-user@example.com"})
    """
    import frappe
    frappe.db.delete(resolve(model_name), filters)


def sql(query: str, values=None, as_dict: bool = False) -> list:
    """
    Execute a raw SQL query.

    Convention:
        - Only SELECT statements are permitted by SMRITI convention.
        - INSERT/UPDATE/DELETE must use documents.* or db.set/delete methods.
        - Document type names in raw SQL must still use platform DocType names
          (because SQL operates on table names, not model names).
          Prefix with `tab` as per Frappe convention, e.g. `tabCustomer`.

    Args:
        query (str): SQL query string
        values (dict|tuple): Bind parameters
        as_dict (bool): If True, returns list of dicts

    Returns:
        list: Query results

    Example:
        rows = db.sql(
            "SELECT name, customer_name FROM `tabCustomer` WHERE territory = %(territory)s",
            values={"territory": "North"},
        )
    """
    import frappe
    return frappe.db.sql(query, values or {}, as_dict=as_dict)


def commit():
    """
    Commit the current database transaction.
    Use only when you need an explicit commit outside the normal request lifecycle.
    """
    import frappe
    frappe.db.commit()


def rollback():
    """Roll back the current database transaction."""
    import frappe
    frappe.db.rollback()


def sql_list(query: str, values=None) -> list:
    """
    Execute a raw SQL query and return a flat list of values from the first column.
    Equivalent to frappe.db.sql_list().

    Args:
        query (str): SQL query string (should SELECT a single column)
        values (dict|tuple): Bind parameters

    Returns:
        list: Flat list of values from the first column of results

    Example:
        names = db.sql_list(
            "SELECT name FROM `tabCustomer` WHERE territory = %(territory)s",
            values={"territory": "North"},
        )
    """
    import frappe
    return frappe.db.sql_list(query, values or {})
