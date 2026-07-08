# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/field_explorer_api.py
# @description: SMRITI Universal Field Explorer (UFE) API — whitelisted endpoints
#               for field discovery, document data inspection, cross-doctype search,
#               relationship tree, label preview, and Field ID registry.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-26
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# API naming convention: smriti_retail_os.api.field_explorer_api.<method>

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
import json
from smriti_retail_os.services import field_explorer_service as _svc


@frappe.whitelist()
def get_doctype_list():
    """
    Returns all DocTypes readable by the current user, grouped by module.
    Used to populate the DocType selector in the UFE page.
    """
    return _svc.FieldExplorerService.get_doctype_list()


@frappe.whitelist()
def get_doctype_fields(doctype, show_standard=True, show_custom=True,
                       show_hidden=False, show_child_tables=True, search=None):
    """
    Returns all fields for a DocType, grouped by section.
    Recurses into child tables when show_child_tables is True.
    Results are cached; cache is auto-invalidated when Custom Fields change.

    Args:
        doctype (str): e.g. "Item", "POS Invoice"
        show_standard (bool): Include standard Frappe fields (default True)
        show_custom (bool): Include custom fields (default True)
        show_hidden (bool): Include hidden fields (default False)
        show_child_tables (bool): Recurse into child DocTypes (default True)
        search (str): Filter by label or fieldname
    """
    _bool = lambda v: str(v).lower() not in ("0", "false", "no", "")
    return _svc.FieldExplorerService.get_fields(
        doctype=doctype,
        show_standard=_bool(show_standard),
        show_custom=_bool(show_custom),
        show_hidden=_bool(show_hidden),
        show_child_tables=_bool(show_child_tables),
        search=search or None,
    )


@frappe.whitelist()
def get_document_data(doctype, docname, include_child_tables=True):
    """
    Returns all field values for a specific document.
    Blank fields are flagged in blank_fields array.
    Permission enforced at document level.

    Args:
        doctype (str): DocType name
        docname (str): Document name/ID
        include_child_tables (bool): Include child table rows (default True)
    """
    _bool = lambda v: str(v).lower() not in ("0", "false", "no", "")
    return _svc.FieldExplorerService.get_document_data(
        doctype=doctype,
        docname=docname,
        include_child_tables=_bool(include_child_tables),
    )


@frappe.whitelist()
def search_fields(query, doctypes=None):
    """
    Cross-DocType field search.
    Returns fields matching query by label or fieldname across multiple DocTypes.
    Powers the Print Mapping Assistant and UFE Search tab.

    Args:
        query (str): Search term (minimum 2 characters)
        doctypes (str|list): JSON array or comma-separated DocType names.
                             If empty, searches the default UFE DocType set.
    """
    if isinstance(doctypes, str):
        try:
            doctypes = json.loads(doctypes)
        except ValueError:
            doctypes = [d.strip() for d in doctypes.split(",") if d.strip()]

    return _svc.FieldExplorerService.search_fields(query=query, doctypes=doctypes or None)


@frappe.whitelist()
def get_doctype_tree(doctype, depth=2):
    """
    Returns the linked-document relationship tree for a DocType.
    Depth 1 = immediate links, depth 2 = one level deeper.

    Args:
        doctype (str): Root DocType
        depth (int): Traversal depth (max 3 to prevent explosion)
    """
    depth = min(int(depth), 3)
    return _svc.FieldExplorerService.get_doctype_tree(doctype=doctype, depth=depth)


@frappe.whitelist()
def resolve_label_preview(doctype, docname, field_paths):
    """
    Resolves field paths to actual values — for Barcode Studio / Print preview.
    Blank fields are flagged before printing.

    Args:
        doctype (str): e.g. "Item"
        docname (str): e.g. "ITEM-00045"
        field_paths (str|list): JSON array of paths or Field IDs.
                                Accepts:
                                  - Field IDs: "ITEM_BARCODE"
                                  - Direct paths: "Item.item_code"
                                  - Child paths: "Item.barcodes[].barcode"
    """
    if isinstance(field_paths, str):
        try:
            field_paths = json.loads(field_paths)
        except ValueError:
            field_paths = [p.strip() for p in field_paths.split(",") if p.strip()]

    return _svc.FieldExplorerService.resolve_label_preview(
        doctype=doctype,
        docname=docname,
        field_paths=field_paths,
    )


@frappe.whitelist()
def get_field_id_registry(doctype_filter=None, printable_only=False):
    """
    Returns the canonical Field ID registry.
    Barcode Studio uses Field IDs (e.g. ITEM_BARCODE) instead of raw paths,
    so template stability is maintained even if underlying schema changes.

    Args:
        doctype_filter (str): Filter registry to one DocType (e.g. "Item")
        printable_only (bool): Return only fields safe to print on labels
    """
    _bool = lambda v: str(v).lower() not in ("0", "false", "no", "")
    return _svc.FieldExplorerService.get_field_id_registry(
        doctype_filter=doctype_filter or None,
        printable_only=_bool(printable_only),
    )
