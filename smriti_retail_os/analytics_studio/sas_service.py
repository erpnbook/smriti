# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/analytics_studio/sas_service.py
# @description: SMRITI Analytics Studio — Service Layer
#               Bridges the Dataset Engine with AG Grid column definitions,
#               grand totals computation, KPI card generation, conditional
#               formatting rules, and metadata expansion.
# @author: Jawahar R. Mallah
# @version: 1.0.0
#

import frappe
import json
from frappe.utils import flt, cint, nowdate

from smriti_retail_os.analytics_studio.dataset_engine import (
    DatasetEngine, DATASET_REGISTRY
)


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT REPORT METADATA EXTENSION
# Augments SMRITI Report Template records with SAS-specific fields that may
# not yet exist as DocType custom fields.
# ─────────────────────────────────────────────────────────────────────────────

SAS_REPORT_DEFAULTS = {
    "daily_sales_summary": {
        "dataset_key": "sales",
        "default_sort": {"field": "posting_date", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "posting_date", "y": "grand_total"},
        "kpi_fields": ["grand_total", "bills_count", "qty_sold", "discount_amount"],
        "conditional_format_rules": [
            {"field": "grand_total", "op": "<", "value": 5000, "css": "sas-cf-danger"},
            {"field": "grand_total", "op": ">=", "value": 50000, "css": "sas-cf-success"},
        ],
        "drill_down": {"field": "posting_date", "child_report": "item_wise_sales"},
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "pivot", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "item_wise_sales": {
        "dataset_key": "sales_items",
        "default_sort": {"field": "qty_sold", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "item_name", "y": "qty_sold"},
        "kpi_fields": ["qty_sold", "taxable_amount", "gross_amount"],
        "conditional_format_rules": [
            {"field": "qty_sold", "op": ">=", "value": 100, "css": "sas-cf-success"},
        ],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "pivot", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "current_stock_position": {
        "dataset_key": "inventory",
        "default_sort": {"field": "actual_qty", "dir": "asc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "item_code", "y": "actual_qty"},
        "kpi_fields": ["actual_qty", "stock_value"],
        "conditional_format_rules": [
            {"field": "stock_status", "op": "==", "value": "Out of Stock", "css": "sas-cf-danger"},
            {"field": "stock_status", "op": "==", "value": "Low Stock", "css": "sas-cf-warning"},
        ],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },

    # ── Purchase Report Defaults ───────────────────────────────────────────────
    "purchase_order_summary": {
        "dataset_key": None,
        "default_sort": {"field": "po_number", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "supplier_name", "y": "grand_total"},
        "kpi_fields": ["grand_total", "balance_amount", "total_qty"],
        "conditional_format_rules": [
            {"field": "status", "op": "==", "value": "Overdue", "css": "sas-cf-danger"},
            {"field": "balance_amount", "op": ">", "value": 0, "css": "sas-cf-warning"},
        ],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "grn_register": {
        "dataset_key": None,
        "default_sort": {"field": "grn_number", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "line", "x": "posting_date", "y": "grand_total"},
        "kpi_fields": ["total_qty", "grand_total"],
        "conditional_format_rules": [],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "purchase_invoice_register": {
        "dataset_key": None,
        "default_sort": {"field": "invoice", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "posting_date", "y": "grand_total"},
        "kpi_fields": ["grand_total", "paid_amount", "outstanding_amount"],
        "conditional_format_rules": [
            {"field": "overdue_days", "op": ">", "value": 0, "css": "sas-cf-danger"},
            {"field": "outstanding_amount", "op": ">", "value": 0, "css": "sas-cf-warning"},
        ],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "supplier_purchase_summary": {
        "dataset_key": None,
        "default_sort": {"field": "grand_total", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "supplier_name", "y": "grand_total"},
        "kpi_fields": ["grand_total", "outstanding_amount"],
        "conditional_format_rules": [
            {"field": "outstanding_amount", "op": ">", "value": 0, "css": "sas-cf-warning"},
        ],
        "drill_down": {"field": "supplier", "child_report": "purchase_invoice_register"},
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "item_wise_purchase": {
        "dataset_key": None,
        "default_sort": {"field": "total_value", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "item_name", "y": "total_value"},
        "kpi_fields": ["total_qty", "total_value"],
        "conditional_format_rules": [],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
    "purchase_return_register": {
        "dataset_key": None,
        "default_sort": {"field": "date", "dir": "desc"},
        "default_group_by": [],
        "default_chart": {"type": "bar", "x": "date", "y": "grand_total"},
        "kpi_fields": ["grand_total", "total_tax"],
        "conditional_format_rules": [],
        "drill_down": None,
        "allowed_export_types": ["csv", "excel", "pdf", "print"],
        "default_page_size": 500,
        "toolbar_options": ["group_by", "columns", "density", "fullscreen", "chart"],
        "explain_enabled": True,
    },
}

# Fallback defaults for reports not in SAS_REPORT_DEFAULTS
DEFAULT_SAS_META = {
    "dataset_key": None,
    "default_sort": None,
    "default_group_by": [],
    "default_chart": {"type": "bar", "x": None, "y": None},
    "kpi_fields": [],
    "conditional_format_rules": [],
    "drill_down": None,
    "allowed_export_types": ["csv", "excel", "pdf", "print"],
    "default_page_size": 500,
    "toolbar_options": ["group_by", "columns", "density", "fullscreen"],
    "explain_enabled": True,
}


def get_sas_report_metadata(report_key):
    """
    Returns the full expanded metadata for a report, merging
    SMRITI Report Template record with SAS-specific defaults.
    """
    template = frappe.db.get_value(
        "SMRITI Report Template",
        {"report_key": report_key},
        ["*"],
        as_dict=True
    )
    if not template:
        frappe.throw(f"Report '{report_key}' not found in SMRITI Report Template.")

    # Parse JSON fields
    columns = []
    filters = []
    try:
        columns = json.loads(template.get("columns_json") or "[]")
    except Exception:
        pass
    try:
        filters = json.loads(template.get("filters_json") or "[]")
    except Exception:
        pass

    # Get SAS-specific meta
    sas_meta = SAS_REPORT_DEFAULTS.get(report_key, DEFAULT_SAS_META).copy()

    return {
        "report_key": report_key,
        "report_name": template.get("report_name", report_key),
        "report_category": template.get("report_category", "General"),
        "columns": columns,
        "filters": filters,
        "dataset_key": sas_meta.get("dataset_key"),
        "default_sort": sas_meta.get("default_sort"),
        "default_group_by": sas_meta.get("default_group_by", []),
        "default_chart": sas_meta.get("default_chart", {}),
        "kpi_fields": sas_meta.get("kpi_fields", []),
        "conditional_format_rules": sas_meta.get("conditional_format_rules", []),
        "drill_down": sas_meta.get("drill_down"),
        "allowed_export_types": sas_meta.get("allowed_export_types", ["csv"]),
        "default_page_size": sas_meta.get("default_page_size", 500),
        "toolbar_options": sas_meta.get("toolbar_options", []),
        "explain_enabled": sas_meta.get("explain_enabled", True),
        "cache_minutes": cint(template.get("cache_minutes", 0)),
        "is_public": cint(template.get("is_public", 1)),
        "company_restricted": cint(template.get("company_restricted", 0)),
    }


def build_ag_column_defs(columns, sas_meta):
    """
    Transforms SMRITI columns_json into AG Grid columnDefs format.
    Applies conditional format rules as cellClassRules.
    """
    cf_rules = {
        rule["field"]: rule
        for rule in sas_meta.get("conditional_format_rules", [])
    }

    col_defs = []
    for col in columns:
        fieldname = col.get("fieldname", "")
        fieldtype = col.get("fieldtype", "Data")
        width = cint(col.get("width", 130))

        ag_col = {
            "field": fieldname,
            "headerName": col.get("label", fieldname),
            "width": width,
            "minWidth": 80,
            "resizable": True,
            "sortable": True,
            "filter": True,
            "enableRowGroup": True,
            "enableValue": True,
        }

        # Numeric types
        if fieldtype in ("Currency", "Float", "Int", "Percent"):
            ag_col["type"] = "numericColumn"
            ag_col["enablePivot"] = True
            if fieldtype == "Currency":
                ag_col["valueFormatter"] = "currencyFormatter"
            elif fieldtype == "Percent":
                ag_col["valueFormatter"] = "percentFormatter"
            elif fieldtype == "Float":
                ag_col["valueFormatter"] = "floatFormatter"

        # Date type
        elif fieldtype == "Date":
            ag_col["filter"] = "agDateColumnFilter"

        # Conditional formatting
        if fieldname in cf_rules:
            ag_col["cellClassRules"] = _build_cell_class_rules(cf_rules[fieldname])

        # Pin first column by default
        if col == columns[0]:
            ag_col["pinned"] = "left"
            ag_col["lockPinned"] = True
            ag_col["checkboxSelection"] = False

        col_defs.append(ag_col)

    return col_defs


def _build_cell_class_rules(rule):
    """
    Returns AG Grid cellClassRules dict for a single conditional format rule.
    The actual comparison happens client-side via JS function strings.
    """
    css_class = rule.get("css", "sas-cf-warning")
    op = rule.get("op", ">=")
    val = rule.get("value")

    if isinstance(val, str):
        js_expr = f'params.value {op} "{val}"'
    else:
        js_expr = f"params.value {op} {val}"

    return {css_class: js_expr}


def compute_grand_totals(rows, columns):
    """
    Computes SUM for all numeric columns across the provided rows.
    Returns a single dict suitable for AG Grid pinnedBottomRowData.
    """
    if not rows:
        return {}

    numeric_types = ("Currency", "Float", "Int", "Percent")
    totals = {"_is_grand_total": True, "_label": "Grand Total"}

    for col in columns:
        fieldname = col.get("fieldname")
        fieldtype = col.get("fieldtype", "Data")
        if fieldtype in numeric_types:
            total = sum(flt(row.get(fieldname, 0)) for row in rows)
            totals[fieldname] = round(total, 2)

    # Label the first column
    if columns:
        totals[columns[0].get("fieldname", "name")] = "Grand Total"

    return totals


def compute_kpi_cards(rows, kpi_fields, columns, compare_rows=None):
    """
    Computes KPI card values for the given kpi_fields.
    Returns list of {label, value, prev_value, change_pct, change_dir}.
    """
    if not rows or not kpi_fields:
        return []

    col_meta = {c.get("fieldname"): c for c in columns}
    cards = []

    for field in kpi_fields:
        col = col_meta.get(field, {})
        label = col.get("label", field)
        fieldtype = col.get("fieldtype", "Data")

        if fieldtype in ("Currency", "Float", "Int", "Percent"):
            current_val = sum(flt(row.get(field, 0)) for row in rows)
        else:
            current_val = len(set(row.get(field) for row in rows if row.get(field)))

        prev_val = None
        change_pct = None
        change_dir = None

        if compare_rows:
            prev_val = sum(flt(row.get(field, 0)) for row in compare_rows)
            if prev_val and prev_val != 0:
                change_pct = round(((current_val - prev_val) / abs(prev_val)) * 100, 1)
                change_dir = "up" if change_pct >= 0 else "down"

        cards.append({
            "fieldname": field,
            "label": label,
            "fieldtype": fieldtype,
            "value": round(current_val, 2),
            "prev_value": round(prev_val, 2) if prev_val is not None else None,
            "change_pct": change_pct,
            "change_dir": change_dir,
        })

    return cards


def get_report_categories_from_nav():
    """
    Returns report categories from CANONICAL_NAV reports section.
    Single source of truth — no hardcoding.
    """
    try:
        from smriti_retail_os.navigation.navigation_service import CANONICAL_NAV
        reports_section = next(
            (s for s in CANONICAL_NAV.get("sections", []) if s.get("id") == "reports"),
            None
        )
        if not reports_section:
            return []

        categories = []
        current_category = None
        for item in reports_section.get("items", []):
            if item.get("type") == "header":
                current_category = {
                    "label": item.get("label"),
                    "items": []
                }
                categories.append(current_category)
            elif current_category is not None:
                current_category["items"].append({
                    "id": item.get("id"),
                    "label": item.get("label"),
                    "route": item.get("route"),
                    "status": item.get("status", "active"),
                })

        return categories

    except Exception as e:
        frappe.log_error(f"SAS: get_report_categories_from_nav error: {str(e)}")
        return []


def get_srs_report_list_for_sas():
    """
    Returns the full report catalog grouped by category,
    enriched with SAS metadata keys.
    """
    try:
        all_templates = frappe.db.get_all(
            "SMRITI Report Template",
            filters={"is_public": 1},
            fields=[
                "name", "report_key", "report_name",
                "report_category", "cache_minutes", "schema_version"
            ],
            order_by="report_category ASC, report_name ASC"
        )
    except Exception:
        return {}

    grouped = {}
    for tmpl in all_templates:
        cat = tmpl.get("report_category") or "General"
        if cat not in grouped:
            grouped[cat] = []
        sas_meta = SAS_REPORT_DEFAULTS.get(tmpl["report_key"], DEFAULT_SAS_META)
        grouped[cat].append({
            "report_key": tmpl["report_key"],
            "report_name": tmpl["report_name"],
            "dataset_key": sas_meta.get("dataset_key"),
            "has_chart": bool(sas_meta.get("default_chart", {}).get("type")),
            "has_kpi": bool(sas_meta.get("kpi_fields")),
            "explain_enabled": sas_meta.get("explain_enabled", True),
        })

    return grouped
