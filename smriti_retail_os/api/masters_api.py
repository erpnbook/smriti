# -*- coding: utf-8 -*-
#
# @file: masters_api.py
# @description: Whitelisted SMRITI Master Data read APIs.
#   Replaces direct frappe.client.get_list calls from suppliers.html and other
#   master data pages. All reads go through this service layer.
# @author: Jawahar R. Mallah
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe import _


@frappe.whitelist()
def get_suppliers(limit=200):
    """
    Return supplier list for SMRITI Suppliers page.
    Replaces frappe.client.get_list('Supplier') from suppliers.html.
    """
    return frappe.get_list(
        "Supplier",
        fields=["name", "supplier_name", "supplier_group", "mobile_no",
                "custom_credit_days", "custom_vendor_code"],
        order_by="creation desc",
        limit_page_length=int(limit),
    )


@frappe.whitelist()
def get_supplier_groups(limit=100):
    """Return Supplier Group list. Replaces frappe.client.get_list('Supplier Group')."""
    return frappe.get_list(
        "Supplier Group",
        fields=["name"],
        order_by="name asc",
        limit_page_length=int(limit),
    )


@frappe.whitelist()
def get_supplier_form_options():
    """
    Return all dropdown options required for the SMRITI Supplier create/edit form
    in a single call — replaces 6 separate frappe.client.get_list calls.
    Returns: payment_terms, currencies, price_lists, bank_accounts, companies, languages, naming_series.
    """
    # Naming series from DocField
    naming_series = ""
    try:
        naming_series = frappe.db.get_value(
            "DocField",
            {"parent": "Supplier", "fieldname": "naming_series"},
            "options"
        ) or ""
    except Exception:
        pass

    payment_terms = frappe.get_list(
        "Payment Terms Template", fields=["name"], limit_page_length=100
    )
    currencies = frappe.get_list(
        "Currency", fields=["name"], filters={"enabled": 1}, limit_page_length=250
    )
    price_lists = frappe.get_list(
        "Price List", fields=["name"],
        filters={"buying": 1, "enabled": 1}, limit_page_length=100
    )
    bank_accounts = frappe.get_list(
        "Bank Account", fields=["name"], limit_page_length=100
    )
    companies = frappe.get_list(
        "Company", fields=["name"], limit_page_length=50
    )
    languages = frappe.get_list(
        "Language", fields=["name"], filters={"enabled": 1}, limit_page_length=200
    )
    groups = frappe.get_list(
        "Supplier Group", fields=["name"], order_by="name asc", limit_page_length=100
    )

    return {
        "naming_series": naming_series,
        "payment_terms": payment_terms,
        "currencies": currencies,
        "price_lists": price_lists,
        "bank_accounts": bank_accounts,
        "companies": companies,
        "languages": languages,
        "supplier_groups": groups,
    }


@frappe.whitelist()
def get_party_stock_accounts(company, active=1):
    """
    Return SMRITI Party Stock Accounts for a company.
    Replaces frappe.client.get_list('SMRITI Party Stock Account') from
    stock-audit.html and sales-upload.html.
    """
    return frappe.get_list(
        "SMRITI Party Stock Account",
        filters={"company": company, "active": int(active)},
        fields=["name", "customer", "location_name"],
    )
