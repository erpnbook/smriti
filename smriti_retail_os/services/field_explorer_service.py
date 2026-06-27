# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/field_explorer_service.py
# @description: SMRITI Universal Field Explorer (UFE) Service — canonical metadata service
#               for all SMRITI field discovery, PRN mapping, print format binding,
#               and report column configuration.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-26
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# Architecture:
#   UI → field_explorer_api.py → FieldExplorerService → frappe.get_meta()
#
# Key design decisions:
#   1. Field ID Registry: Barcode Studio stores ITEM_BARCODE, not Item.barcodes[].barcode
#      If the underlying path changes, only the registry entry changes — templates stay stable.
#   2. Cache: frappe.cache() with 1-hour TTL; auto-invalidated when Custom Field / DocType saved.
#   3. No shadow database: reads Frappe meta live, stores nothing independently.
#   4. Permission enforcement: frappe.has_permission() on every call.

import frappe
import json
import re

# ─────────────────────────────────────────────────────────────────────────────
# FIELD ID REGISTRY — Barcode Studio uses these IDs, not raw paths.
# If the underlying path changes, update ONLY this table. Templates stay stable.
# ─────────────────────────────────────────────────────────────────────────────
FIELD_ID_REGISTRY = {
    # Item fields
    "ITEM_CODE":            {"label": "Item Code",         "doctype": "Item",              "fieldname": "item_code",          "path": "Item.item_code",              "fieldtype": "Data",     "printable": True},
    "ITEM_NAME":            {"label": "Item Name",         "doctype": "Item",              "fieldname": "item_name",          "path": "Item.item_name",              "fieldtype": "Data",     "printable": True},
    "ITEM_MRP":             {"label": "MRP",               "doctype": "Item",              "fieldname": "custom_mrp",         "path": "Item.custom_mrp",             "fieldtype": "Currency", "printable": True},
    "ITEM_HSN":             {"label": "HSN Code",          "doctype": "Item",              "fieldname": "gst_hsn_code",       "path": "Item.gst_hsn_code",           "fieldtype": "Data",     "printable": True},
    "ITEM_BRAND":           {"label": "Brand",             "doctype": "Item",              "fieldname": "brand",              "path": "Item.brand",                  "fieldtype": "Link",     "printable": True},
    "ITEM_GROUP":           {"label": "Item Group",        "doctype": "Item",              "fieldname": "item_group",         "path": "Item.item_group",             "fieldtype": "Link",     "printable": True},
    "ITEM_UOM":             {"label": "UOM",               "doctype": "Item",              "fieldname": "stock_uom",          "path": "Item.stock_uom",              "fieldtype": "Link",     "printable": True},
    "ITEM_DESCRIPTION":     {"label": "Description",       "doctype": "Item",              "fieldname": "description",        "path": "Item.description",            "fieldtype": "Text",     "printable": True},
    "ITEM_BARCODE":         {"label": "Barcode",           "doctype": "Item",              "fieldname": "barcode",            "path": "Item.barcodes[].barcode",     "fieldtype": "Data",     "printable": True,  "child_table": "Item Barcode"},
    "ITEM_BARCODE_TYPE":    {"label": "Barcode Type",      "doctype": "Item",              "fieldname": "barcode_type",       "path": "Item.barcodes[].barcode_type","fieldtype": "Select",   "printable": False, "child_table": "Item Barcode"},
    "ITEM_EXPIRY":          {"label": "Expiry Date",       "doctype": "Item",              "fieldname": "custom_expiry_date", "path": "Item.custom_expiry_date",     "fieldtype": "Date",     "printable": True},
    "ITEM_COUNTRY":         {"label": "Country of Origin", "doctype": "Item",              "fieldname": "country_of_origin",  "path": "Item.country_of_origin",      "fieldtype": "Link",     "printable": True},
    # Sales Invoice fields
    "SI_INVOICE_NO":        {"label": "Invoice No",        "doctype": "Sales Invoice",     "fieldname": "name",               "path": "Sales Invoice.name",          "fieldtype": "Data",     "printable": True},
    "SI_DATE":              {"label": "Invoice Date",      "doctype": "Sales Invoice",     "fieldname": "posting_date",       "path": "Sales Invoice.posting_date",  "fieldtype": "Date",     "printable": True},
    "SI_CUSTOMER":          {"label": "Customer",          "doctype": "Sales Invoice",     "fieldname": "customer",           "path": "Sales Invoice.customer",      "fieldtype": "Link",     "printable": True},
    "SI_GRAND_TOTAL":       {"label": "Grand Total",       "doctype": "Sales Invoice",     "fieldname": "grand_total",        "path": "Sales Invoice.grand_total",   "fieldtype": "Currency", "printable": True},
    "SI_GST":               {"label": "GST Amount",        "doctype": "Sales Invoice",     "fieldname": "total_taxes_and_charges", "path": "Sales Invoice.total_taxes_and_charges", "fieldtype": "Currency", "printable": True},
    # Customer fields
    "CUST_NAME":            {"label": "Customer Name",     "doctype": "Customer",          "fieldname": "customer_name",      "path": "Customer.customer_name",      "fieldtype": "Data",     "printable": True},
    "CUST_GSTIN":           {"label": "GSTIN",             "doctype": "Customer",          "fieldname": "gstin",              "path": "Customer.gstin",              "fieldtype": "Data",     "printable": True},
    "CUST_MOBILE":          {"label": "Mobile",            "doctype": "Customer",          "fieldname": "mobile_no",          "path": "Customer.mobile_no",          "fieldtype": "Data",     "printable": True},
}


# ─────────────────────────────────────────────────────────────────────────────
# Non-printable field types — excluded from Barcode Mode
# ─────────────────────────────────────────────────────────────────────────────
_NON_PRINTABLE_TYPES = {
    "Button", "HTML", "Code", "Signature", "Attach", "Attach Image",
    "Fold", "Column Break", "Section Break", "Tab Break", "Heading",
    "Table", "Table MultiSelect",
}


class FieldExplorerService:
    """
    SMRITI Universal Field Explorer — canonical metadata service.
    Wraps frappe.get_meta() with caching, section grouping, child-table recursion,
    Field ID registry, and blank-field detection.
    """

    CACHE_TTL_SEC = 3600   # 1 hour; invalidated on Custom Field / DocType save

    # ─── Public API Methods ───────────────────────────────────────────────────

    @classmethod
    def get_doctype_list(cls):
        """
        Returns all DocTypes readable by current user, grouped by module.
        Used to populate the DocType selector in the Field Explorer page.
        """
        all_doctypes = frappe.get_all(
            "DocType",
            filters={"istable": 0, "issingle": 0},
            fields=["name", "module"],
            order_by="module asc, name asc"
        )
        # Filter to readable ones only
        readable = []
        for dt in all_doctypes:
            try:
                if frappe.has_permission(dt["name"], "read"):
                    readable.append(dt)
            except Exception:
                pass

        # Group by module
        grouped = {}
        for dt in readable:
            mod = dt.get("module") or "Other"
            grouped.setdefault(mod, []).append(dt["name"])

        return {"modules": grouped, "total": len(readable)}

    @classmethod
    def get_fields(cls, doctype, show_standard=True, show_custom=True,
                   show_hidden=False, show_child_tables=True, search=None):
        """
        Returns all fields for a DocType, grouped by section.
        Recurses into child tables when show_child_tables=True.
        Results are cached for CACHE_TTL_SEC.
        """
        frappe.has_permission(doctype, "read", throw=True)

        cache_key = f"smriti:ufe:fields:{doctype}:{int(show_custom)}:{int(show_hidden)}:{int(show_child_tables)}"
        cached = frappe.cache().get_value(cache_key)
        if cached:
            result = json.loads(cached)
            # Apply search filter on cached result if needed
            if search:
                result = cls._apply_search(result, search)
            return result

        meta = frappe.get_meta(doctype)
        result = cls._build_sections(meta, doctype, show_standard, show_custom,
                                     show_hidden, show_child_tables)

        frappe.cache().set_value(cache_key, json.dumps(result), expires_in_sec=cls.CACHE_TTL_SEC)

        if search:
            result = cls._apply_search(result, search)
        return result

    @classmethod
    def get_document_data(cls, doctype, docname, include_child_tables=True):
        """
        Returns all field values for a specific document.
        Blank fields are flagged. Permission enforced at document level.
        """
        frappe.has_permission(doctype, "read", throw=True)
        frappe.has_permission(doctype, doc=docname, throw=True)

        doc = frappe.get_doc(doctype, docname)
        meta = frappe.get_meta(doctype)

        fields_data = []
        blank_fields = []
        child_tables = {}

        current_section = "General"
        for field in meta.fields:
            if field.fieldtype == "Section Break":
                current_section = field.label or field.fieldname or "Section"
                continue
            if field.fieldtype in {"Column Break", "Tab Break", "Heading", "Fold", "HTML", "Button"}:
                continue

            if field.fieldtype == "Table" and include_child_tables:
                # Recurse into child table
                child_fieldname = field.fieldname
                child_doctype = field.options
                child_rows = doc.get(child_fieldname) or []
                table_data = []
                for row in child_rows:
                    row_dict = {}
                    child_meta = frappe.get_meta(child_doctype)
                    for cf in child_meta.fields:
                        if cf.fieldtype not in _NON_PRINTABLE_TYPES:
                            val = row.get(cf.fieldname)
                            row_dict[cf.fieldname] = val
                    table_data.append(row_dict)
                child_tables[child_fieldname] = table_data
                continue

            val = doc.get(field.fieldname)
            is_blank = val is None or val == "" or val == 0 and field.fieldtype in {"Currency", "Float", "Int"}
            is_custom = field.custom

            field_entry = {
                "label":          field.label or field.fieldname,
                "fieldname":      field.fieldname,
                "fieldtype":      field.fieldtype,
                "section":        current_section,
                "value":          val,
                "blank":          is_blank,
                "is_custom":      bool(is_custom),
                "mandatory":      bool(field.reqd),
            }
            fields_data.append(field_entry)
            if is_blank:
                blank_fields.append(field.fieldname)

        return {
            "doctype":      doctype,
            "docname":      docname,
            "fields":       fields_data,
            "blank_fields": blank_fields,
            "blank_count":  len(blank_fields),
            "child_tables": child_tables,
        }

    @classmethod
    def search_fields(cls, query, doctypes=None):
        """
        Cross-DocType field search. Returns fields matching query by label or fieldname.
        Used by Print Mapping Assistant and cross-module field discovery.
        """
        if not query or len(query) < 2:
            return []

        if not doctypes:
            # Default set for cross-DocType search
            doctypes = ["Item", "Customer", "Supplier", "Sales Invoice",
                        "POS Invoice", "Purchase Order", "Purchase Receipt",
                        "Payment Entry", "Stock Entry", "Delivery Note"]

        query_lower = query.lower()
        results = []

        for doctype in doctypes:
            try:
                if not frappe.has_permission(doctype, "read"):
                    continue
                meta = frappe.get_meta(doctype)
                for field in meta.fields:
                    if field.fieldtype in _NON_PRINTABLE_TYPES:
                        continue
                    label = (field.label or field.fieldname or "").lower()
                    fname = (field.fieldname or "").lower()
                    if query_lower in label or query_lower in fname:
                        is_child = field.fieldtype == "Table"
                        path = f"{doctype}.{field.fieldname}"
                        results.append({
                            "label":     field.label or field.fieldname,
                            "fieldname": field.fieldname,
                            "fieldtype": field.fieldtype,
                            "doctype":   doctype,
                            "path":      path,
                            "is_custom": bool(field.custom),
                            "is_child_table": is_child,
                        })
            except Exception:
                continue

        return results[:200]  # Cap at 200 for performance

    @classmethod
    def get_doctype_tree(cls, doctype, depth=2):
        """
        Returns relationship tree of a DocType — linked doctypes and their fields.
        Depth 1 = immediate links only. Depth 2 = one level deeper.
        """
        frappe.has_permission(doctype, "read", throw=True)
        return cls._build_tree(doctype, depth, visited=set())

    @classmethod
    def resolve_label_preview(cls, doctype, docname, field_paths):
        """
        Resolves a list of field paths to actual values from a document.
        Used by Barcode Studio and Print Templates for blank-field warnings.

        Supports:
          - Direct fields:  "Item.item_code"
          - Child table:    "Item.barcodes[].barcode"
          - Field IDs:      "ITEM_BARCODE" → resolved via FIELD_ID_REGISTRY
        """
        frappe.has_permission(doctype, "read", throw=True)
        frappe.has_permission(doctype, doc=docname, throw=True)

        doc = frappe.get_doc(doctype, docname)
        resolved = []
        blank_count = 0

        for path in field_paths:
            # Resolve Field ID → real path
            real_path = path
            entry_label = path
            if path in FIELD_ID_REGISTRY:
                reg = FIELD_ID_REGISTRY[path]
                real_path = reg["path"]
                entry_label = reg["label"]

            value, err = cls._resolve_path(doc, doctype, real_path)
            is_blank = value is None or value == ""

            if is_blank:
                blank_count += 1

            resolved.append({
                "field_id":  path if path in FIELD_ID_REGISTRY else None,
                "path":      real_path,
                "label":     entry_label,
                "value":     value,
                "blank":     is_blank,
                "error":     err,
            })

        warning = None
        if blank_count:
            warning = f"{blank_count} field(s) will print blank. Review before printing."

        return {
            "resolved":    resolved,
            "blank_count": blank_count,
            "warning":     warning,
        }

    @classmethod
    def get_field_id_registry(cls, doctype_filter=None, printable_only=False):
        """
        Returns the canonical Field ID registry.
        Used by Barcode Studio to populate Barcode Mode.
        """
        result = []
        for field_id, info in FIELD_ID_REGISTRY.items():
            if doctype_filter and info["doctype"] != doctype_filter:
                continue
            if printable_only and not info.get("printable", True):
                continue
            result.append({
                "field_id":    field_id,
                "label":       info["label"],
                "doctype":     info["doctype"],
                "fieldname":   info["fieldname"],
                "path":        info["path"],
                "fieldtype":   info["fieldtype"],
                "printable":   info.get("printable", True),
                "child_table": info.get("child_table"),
            })
        return sorted(result, key=lambda x: (x["doctype"], x["label"]))

    # ─── Private Helpers ─────────────────────────────────────────────────────

    @classmethod
    def _build_sections(cls, meta, doctype, show_standard, show_custom,
                        show_hidden, show_child_tables):
        """Groups meta.fields into sections with optional child-table recursion."""
        sections = []
        current_section_label = "General"
        current_section_fields = []
        linked_doctypes = set()
        total_fields = 0

        def flush_section():
            if current_section_fields:
                sections.append({
                    "section": current_section_label,
                    "fields":  list(current_section_fields),
                })

        for field in meta.fields:
            ft = field.fieldtype

            if ft == "Section Break":
                flush_section()
                current_section_label = field.label or field.fieldname or "Section"
                current_section_fields = []
                continue

            if ft in {"Column Break", "Tab Break", "Heading", "Fold"}:
                continue

            if ft == "Table" and show_child_tables:
                child_doctype = field.options
                if child_doctype:
                    linked_doctypes.add(child_doctype)
                    child_meta = frappe.get_meta(child_doctype)
                    child_fields = []
                    for cf in child_meta.fields:
                        if cf.fieldtype in _NON_PRINTABLE_TYPES:
                            continue
                        if not show_hidden and cf.hidden:
                            continue
                        if cf.custom and not show_custom:
                            continue
                        if not cf.custom and not show_standard:
                            continue
                        child_fields.append(cls._field_entry(cf, child_doctype, f"{doctype}.{field.fieldname}[].{cf.fieldname}"))
                        total_fields += 1

                    if child_fields:
                        flush_section()
                        current_section_label = field.label or field.fieldname
                        current_section_fields = []
                        sections.append({
                            "section":       field.label or field.fieldname,
                            "child_doctype": child_doctype,
                            "fields":        child_fields,
                        })
                continue

            if ft in _NON_PRINTABLE_TYPES:
                continue

            if not show_hidden and field.hidden:
                continue
            if field.custom and not show_custom:
                continue
            if not field.custom and not show_standard:
                continue

            if ft == "Link" and field.options:
                linked_doctypes.add(field.options)

            path = f"{doctype}.{field.fieldname}"
            current_section_fields.append(cls._field_entry(field, doctype, path))
            total_fields += 1

        flush_section()

        return {
            "doctype":         doctype,
            "total_fields":    total_fields,
            "sections":        sections,
            "linked_doctypes": sorted(linked_doctypes),
        }

    @classmethod
    def _field_entry(cls, field, parent_doctype, path):
        """Builds a standardized field dictionary."""
        return {
            "label":          field.label or field.fieldname,
            "fieldname":      field.fieldname,
            "fieldtype":      field.fieldtype,
            "parent_doctype": parent_doctype,
            "mandatory":      bool(field.reqd),
            "is_custom":      bool(field.custom),
            "is_hidden":      bool(field.hidden),
            "read_only":      bool(field.read_only),
            "path":           path,
            "printable":      field.fieldtype not in _NON_PRINTABLE_TYPES,
        }

    @classmethod
    def _apply_search(cls, result, search):
        """Filters sections/fields by search term."""
        query = search.lower()
        filtered_sections = []
        for section in result.get("sections", []):
            matching_fields = [
                f for f in section.get("fields", [])
                if query in (f.get("label") or "").lower()
                or query in (f.get("fieldname") or "").lower()
            ]
            if matching_fields:
                filtered_sections.append({**section, "fields": matching_fields})
        return {**result, "sections": filtered_sections}

    @classmethod
    def _build_tree(cls, doctype, depth, visited):
        """Recursively builds the relationship tree."""
        if doctype in visited or depth < 0:
            return {"doctype": doctype, "truncated": True}
        visited.add(doctype)

        try:
            meta = frappe.get_meta(doctype)
        except Exception:
            return {"doctype": doctype, "error": "Meta not found"}

        children = []
        for field in meta.fields:
            if field.fieldtype in ("Link", "Table") and field.options:
                linked = field.options
                child_node = {
                    "fieldname":      field.fieldname,
                    "label":          field.label or field.fieldname,
                    "linked_doctype": linked,
                    "link_type":      field.fieldtype,
                }
                if depth > 0:
                    child_node["children"] = cls._build_tree(linked, depth - 1, visited)
                children.append(child_node)

        return {"doctype": doctype, "children": children}

    @classmethod
    def _resolve_path(cls, doc, doctype, path):
        """
        Resolves a dot-separated field path to a value.
        Supports direct fields and child-table paths like:
          "Item.barcodes[].barcode"
          "Item.item_code"
        Returns (value, error_message_or_None).
        """
        try:
            # Strip leading doctype prefix
            parts = path.split(".")
            if parts and parts[0] == doctype:
                parts = parts[1:]

            if not parts:
                return None, "Empty path"

            # Check for child table notation: fieldname[]
            table_match = re.match(r"^(\w+)\[\]$", parts[0])
            if table_match and len(parts) > 1:
                table_fieldname = table_match.group(1)
                child_fieldname = parts[1]
                child_rows = doc.get(table_fieldname) or []
                if child_rows:
                    # Return first row value
                    return child_rows[0].get(child_fieldname), None
                return None, None

            # Direct field
            value = doc.get(parts[0])
            return value, None
        except Exception as e:
            return None, str(e)


# ─────────────────────────────────────────────────────────────────────────────
# Cache Invalidation Hook — called by hooks.py on Custom Field / DocType save
# ─────────────────────────────────────────────────────────────────────────────
def invalidate_ufe_cache(doc, method=None):
    """
    Clears UFE metadata cache when a Custom Field or DocType is saved.
    Registered in hooks.py under doc_events for:
      - "Custom Field": {"on_update": ...}
      - "DocType": {"on_update": ...}
    """
    try:
        doctype_name = getattr(doc, "dt", None) or getattr(doc, "name", None)
        if doctype_name:
            # Clear all cache keys for this DocType (all option combinations)
            for custom in (0, 1):
                for hidden in (0, 1):
                    for child in (0, 1):
                        key = f"smriti:ufe:fields:{doctype_name}:{custom}:{hidden}:{child}"
                        frappe.cache().delete_value(key)
            frappe.logger().info(f"UFE cache cleared for DocType: {doctype_name}")
    except Exception:
        pass  # Never raise in a hook — fail silently
