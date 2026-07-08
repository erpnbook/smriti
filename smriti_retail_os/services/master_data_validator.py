# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/master_data_validator.py
# @description: SMRITI Master Data Validator Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import re
import frappe                          # frappe.throw — framework utility
from frappe import _                   # i18n only
from frappe.utils import cint, flt    # framework utilities
from smriti_retail_os import smriti

def validate(doc, strict=True, collect_errors=False):
    """
    Enforces SMRITI Master Data Governance Foundation (MDGF) validations on Item.
    Supports structured collected errors and strict throwing mode.
    """
    errors_list = [] if collect_errors else None
    
    # 1. Always resolve style before checking validations
    resolve_style(doc)
    
    # 2. Run validations
    validate_brand(doc, errors_list)
    validate_category(doc, errors_list)
    validate_uom(doc, errors_list)
    validate_gst(doc, errors_list)
    validate_hsn(doc, errors_list)
    validate_suppliers(doc, errors_list)
    validate_barcodes(doc, errors_list)
    
    if collect_errors and errors_list:
        if strict:
            error_msg = _("Validation Failed:\n") + "\n".join(f"• {err}" for err in errors_list)
            frappe.throw(error_msg, title=_("Master Data Governance Violation"))
        return errors_list
        
    return []

def resolve_style(doc):
    """
    Resolves custom_style_code following precedence:
    custom_style_code -> variant_of -> item_code -> None
    """
    if not doc.get("custom_style_code"):
        if doc.get("variant_of"):
            doc.custom_style_code = doc.variant_of
        elif doc.get("item_code"):
            doc.custom_style_code = doc.item_code
        else:
            doc.custom_style_code = None

def _handle_error(msg, errors, title=None):
    if errors is not None:
        errors.append(msg)
    else:
        frappe.throw(msg, title=title)

def validate_brand(doc, errors=None):
    if doc.brand:
        if not smriti.db.exists("Brand", doc.brand):
            _handle_error(
                _("Brand '{0}' does not exist in the master database.").format(doc.brand),
                errors,
                _("Invalid Brand")
            )

def validate_category(doc, errors=None):
    if doc.item_group:
        if not smriti.db.exists("Category", doc.item_group):
            _handle_error(
                _("Item Group '{0}' does not exist in the master database.").format(doc.item_group),
                errors,
                _("Invalid Item Group")
            )

def validate_uom(doc, errors=None):
    if doc.stock_uom:
        if not smriti.db.exists("UOM", doc.stock_uom):
            _handle_error(
                _("UOM '{0}' does not exist in the master database.").format(doc.stock_uom),
                errors,
                _("Invalid UOM")
            )

def validate_gst(doc, errors=None):
    if doc.get("custom_gst_percentage"):
        allowed_rates = [0, 5, 12, 18, 28]
        if smriti.db.exists("BarcodeSettings", "SMRITI Barcode Settings"):
            try:
                raw_rates = smriti.db.get_single("BarcodeSettings", "allowed_gst_rates")
                if raw_rates:
                    allowed_rates = [cint(r.strip()) for r in raw_rates.split(",") if r.strip().isdigit()]
            except Exception:
                pass
        
        try:
            rate = cint(doc.custom_gst_percentage)
            if rate not in allowed_rates:
                _handle_error(
                    _("GST Rate {0}% is not allowed. Allowed rates: {1}").format(rate, allowed_rates),
                    errors,
                    _("Invalid GST Rate")
                )
        except (ValueError, TypeError):
            _handle_error(
                _("GST Rate '{0}' is invalid.").format(doc.custom_gst_percentage),
                errors,
                _("Invalid GST Rate")
            )

def validate_hsn(doc, errors=None):
    if doc.gst_hsn_code:
        if not smriti.db.exists("GSTHSNCode", doc.gst_hsn_code):
            _handle_error(
                _("HSN Code '{0}' does not exist in the master database.").format(doc.gst_hsn_code),
                errors,
                _("Invalid HSN Code")
            )

def validate_suppliers(doc, errors=None):
    # Check if supplier is required in barcode settings
    require_supplier = False
    if smriti.db.exists("BarcodeSettings", "SMRITI Barcode Settings"):
        try:
            require_supplier = cint(smriti.db.get_single("BarcodeSettings", "require_supplier"))
        except Exception:
            pass

    if require_supplier and not doc.get("supplier_items"):
        _handle_error(
            _("Supplier is required but not provided in Supplier Items."),
            errors,
            _("Missing Supplier")
        )

    for row in doc.get("supplier_items") or []:
        if row.supplier:
            if not smriti.db.exists("Supplier", row.supplier):
                _handle_error(
                    _("Supplier '{0}' does not exist in the master database.").format(row.supplier),
                    errors,
                    _("Invalid Supplier")
                )

def validate_barcodes(doc, errors=None):
    # Check item_code barcode uniqueness
    if doc.is_new() or doc.name != doc.item_code:
        filters = {"barcode": doc.item_code}
        if doc.name:
            filters["parent"] = ["!=", doc.name]
        conflicting_parent = smriti.db.get("ItemBarcode", filters, "parent")
        if conflicting_parent:
            _handle_error(
                _("Item Code '{0}' conflicts with an existing barcode assigned to item '{1}'.").format(doc.item_code, conflicting_parent),
                errors,
                _("Duplicate Barcode")
            )

    for row in doc.get("barcodes") or []:
        if not row.barcode:
            continue
            
        barcode = row.barcode.strip()
        # Format check
        if not re.match(r"^[a-zA-Z0-9\-_]+$", barcode):
            _handle_error(
                _("Barcode '{0}' contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed (no spaces).").format(barcode),
                errors,
                _("Invalid Barcode")
            )
            continue
            
        if len(barcode) < 3 or len(barcode) > 30:
            _handle_error(
                _("Barcode '{0}' must be between 3 and 30 characters.").format(barcode),
                errors,
                _("Invalid Barcode")
            )
            continue
            
        # Global uniqueness check
        filters = {"barcode": barcode}
        if doc.name:
            filters["parent"] = ["!=", doc.name]
        existing_parent = smriti.db.get("ItemBarcode", filters, "parent")
        if existing_parent:
            _handle_error(
                _("Barcode '{0}' is already assigned to item '{1}'.").format(barcode, existing_parent),
                errors,
                _("Duplicate Barcode")
            )
            
        # Conflict check with existing item code
        if barcode != doc.name and barcode != doc.get("item_code"):
            existing_item = smriti.db.get("Product", {"name": barcode}, "name")
            if existing_item:
                _handle_error(
                    _("Barcode '{0}' conflicts with the item code of another item '{1}'.").format(barcode, existing_item),
                    errors,
                    _("Duplicate Barcode")
                )
