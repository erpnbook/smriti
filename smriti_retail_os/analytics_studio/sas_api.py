# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/analytics_studio/sas_api.py
# @description: SMRITI Analytics Studio — Whitelisted API Endpoints
#               All frontend SAS calls route through this module.
# @author: Jawahar R. Mallah
# @version: 1.0.0
#

import frappe
import json
from frappe.utils import flt, cint, nowdate

from smriti_retail_os.analytics_studio.dataset_engine import (
    DatasetEngine, DATASET_REGISTRY, get_dataset_list
)
from smriti_retail_os.analytics_studio.sas_service import (
    get_sas_report_metadata,
    build_ag_column_defs,
    compute_grand_totals,
    compute_kpi_cards,
    get_report_categories_from_nav,
    get_srs_report_list_for_sas,
)


def _check_authenticated():
    """
    Central authentication checker for SAS endpoints.
    M-7/Translation-wrap remediation (hardcoding audit 2026-07-03)
    """
    if frappe.session.user == "Guest":
        frappe.throw(frappe._("Authentication required."), frappe.AuthenticationError)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Parse JSON parameter safely
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json(val, default=None):
    if val is None:
        return default if default is not None else {}
    if isinstance(val, (dict, list)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return default if default is not None else {}


def _check_report_permission(report_key):
    """Delegate to existing report permission check from reports_api."""
    try:
        from smriti_retail_os.reports_api import SmritiReportEngine
        engine = SmritiReportEngine(report_key, filters={})
        engine.check_permissions()
    except frappe.PermissionError:
        frappe.throw(
            frappe._("You do not have permission to access report: {0}").format(report_key),
            frappe.PermissionError
        )
    except Exception:
        pass  # If SmritiReportEngine doesn't exist yet, skip


# ─────────────────────────────────────────────────────────────────────────────
# DATASET ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_get_datasets():
    """Returns the full dataset registry for the SAS UI."""
    _check_authenticated()
    return get_dataset_list()


# ─────────────────────────────────────────────────────────────────────────────
# REPORT CATALOG + METADATA
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_get_categories():
    """
    Returns report categories from Navigation Manager (CANONICAL_NAV).
    Used to build the left panel report library.
    """
    _check_authenticated()

    # First try navigation-driven categories
    nav_cats = get_report_categories_from_nav()

    # Then get all report templates grouped by category
    grouped = get_srs_report_list_for_sas()

    # Merge: nav categories as display order, template data as content
    categories = []
    seen = set()

    # Add nav-order categories first
    for nav_cat in nav_cats:
        label = nav_cat["label"]
        if label in grouped:
            categories.append({
                "label": label,
                "reports": grouped[label],
            })
            seen.add(label)

    # Add remaining categories not in nav
    for label, reports in grouped.items():
        if label not in seen:
            categories.append({
                "label": label,
                "reports": reports,
            })

    return categories


@frappe.whitelist()
def sas_get_report_metadata(report_key):
    """
    Returns full expanded metadata for a report:
    columns (as AG Grid columnDefs), filters, dataset_key,
    chart defaults, KPI fields, conditional format rules, etc.
    """
    _check_authenticated()

    _check_report_permission(report_key)

    meta = get_sas_report_metadata(report_key)
    col_defs = build_ag_column_defs(meta["columns"], meta)

    return {
        **meta,
        "col_defs": col_defs,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_fetch_data(report_key, filters=None, page=1, page_size=500,
                   sort_by=None, sort_dir="desc", group_by=None):
    """
    Primary data endpoint. Returns paginated rows via DatasetEngine
    for dataset-backed reports, or delegates to SmritiReportEngine for
    custom/legacy reports.
    """
    _check_authenticated()

    _check_report_permission(report_key)

    filters = _parse_json(filters, {})
    group_by = _parse_json(group_by, [])
    page = cint(page) or 1
    page_size = min(cint(page_size) or 500, 5000)

    # Get metadata to find dataset_key
    try:
        meta = get_sas_report_metadata(report_key)
        dataset_key = meta.get("dataset_key")
    except Exception:
        dataset_key = None

    if dataset_key and dataset_key in DATASET_REGISTRY:
        # Use DatasetEngine
        engine = DatasetEngine(
            dataset_key=dataset_key,
            filters=filters,
            group_by=group_by,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            page_size=page_size,
        )
        result = engine.fetch()
        return {
            "rows": result["rows"],
            "total_count": result["total_count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "source": "dataset_engine",
            "dataset_key": dataset_key,
        }
    else:
        # Fall back to existing SmritiReportEngine (legacy reports)
        try:
            from smriti_retail_os.reports_api import SmritiReportEngine
            report_engine = SmritiReportEngine(report_key, filters=filters)
            rows = report_engine.run()
        except Exception as e:
            frappe.log_error(f"SAS fallback engine error for {report_key}: {str(e)}")
            rows = []

        # Client-side pagination for legacy reports
        total = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        page_rows = rows[start:end]

        return {
            "rows": page_rows,
            "total_count": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
            "source": "legacy_engine",
            "dataset_key": None,
        }


@frappe.whitelist()
def sas_get_grand_totals(report_key, filters=None):
    """
    Computes server-side grand totals for pinned bottom row in AG Grid.
    """
    _check_authenticated()

    filters = _parse_json(filters, {})

    try:
        meta = get_sas_report_metadata(report_key)
        dataset_key = meta.get("dataset_key")
        columns = meta.get("columns", [])
    except Exception:
        return {}

    if not dataset_key or dataset_key not in DATASET_REGISTRY:
        # For legacy reports: fetch all rows then compute totals
        try:
            from smriti_retail_os.reports_api import SmritiReportEngine
            engine = SmritiReportEngine(report_key, filters=filters)
            rows = engine.run()
            return compute_grand_totals(rows, columns)
        except Exception:
            return {}

    # For dataset-backed reports: use SQL aggregates (faster)
    engine = DatasetEngine(
        dataset_key=dataset_key,
        filters=filters,
        page=1,
        page_size=100000,  # fetch all for totals
    )
    agg = engine.fetch_aggregates()

    totals = {"_is_grand_total": True}
    for col in columns:
        fieldname = col.get("fieldname")
        fieldtype = col.get("fieldtype", "Data")
        if fieldtype in ("Currency", "Float", "Int", "Percent"):
            key = f"sum_{fieldname}"
            if key in agg:
                totals[fieldname] = round(flt(agg[key]), 2)

    if columns:
        totals[columns[0].get("fieldname", "name")] = "Grand Total"

    return totals


@frappe.whitelist()
def sas_get_kpi_summary(report_key, filters=None, compare_filters=None):
    """
    Returns KPI card data for the top panel.
    Supports optional compare_filters for period comparison.
    """
    _check_authenticated()

    filters = _parse_json(filters, {})
    compare_filters = _parse_json(compare_filters, None)

    try:
        meta = get_sas_report_metadata(report_key)
        dataset_key = meta.get("dataset_key")
        kpi_fields = meta.get("kpi_fields", [])
        columns = meta.get("columns", [])
    except Exception:
        return []

    if not kpi_fields:
        return []

    # Fetch current period rows
    if dataset_key and dataset_key in DATASET_REGISTRY:
        engine = DatasetEngine(dataset_key, filters, page=1, page_size=100000)
        current_result = engine.fetch()
        current_rows = current_result["rows"]
    else:
        try:
            from smriti_retail_os.reports_api import SmritiReportEngine
            current_rows = SmritiReportEngine(report_key, filters=filters).run()
        except Exception:
            current_rows = []

    # Fetch compare period rows (if requested)
    compare_rows = None
    if compare_filters:
        try:
            if dataset_key and dataset_key in DATASET_REGISTRY:
                cmp_engine = DatasetEngine(dataset_key, compare_filters, page=1, page_size=100000)
                compare_rows = cmp_engine.fetch()["rows"]
            else:
                from smriti_retail_os.reports_api import SmritiReportEngine
                compare_rows = SmritiReportEngine(report_key, filters=compare_filters).run()
        except Exception:
            compare_rows = None

    return compute_kpi_cards(current_rows, kpi_fields, columns, compare_rows)


# ─────────────────────────────────────────────────────────────────────────────
# SAVED VIEWS
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_save_view(view_name, report_key, state_json):
    """
    Saves a complete SAS view state (column state, filters, sort, group,
    chart, theme, density, page size, etc.) for the current user.
    """
    _check_authenticated()

    state = _parse_json(state_json, {})

    # Check if view already exists for this user+report+name
    existing = frappe.db.get_value(
        "SMRITI Saved View",
        {"view_name": view_name, "report_key": report_key, "owner": frappe.session.user},
        "name"
    )

    if existing:
        frappe.db.set_value("SMRITI Saved View", existing, {
            "applied_filters_json": json.dumps(state.get("filter_model", {})),
            "visible_columns_json": json.dumps(state),
            "modified": frappe.utils.now(),
        })
    else:
        doc = frappe.new_doc("SMRITI Saved View")
        doc.view_name = view_name
        doc.report_key = report_key
        doc.applied_filters_json = json.dumps(state.get("filter_model", {}))
        doc.visible_columns_json = json.dumps(state)
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "saved", "view_name": view_name}


@frappe.whitelist()
def sas_get_views(report_key):
    """Returns all saved views for the current user for this report."""
    if frappe.session.user == "Guest":
        return []

    views = frappe.db.get_all(
        "SMRITI Saved View",
        filters={"report_key": report_key, "owner": frappe.session.user},
        fields=["view_name", "visible_columns_json", "creation", "modified"],
        order_by="modified desc"
    )

    result = []
    for v in views:
        state = _parse_json(v.get("visible_columns_json"), {})
        result.append({
            "view_name": v["view_name"],
            "state": state,
            "created": str(v.get("creation", "")),
            "modified": str(v.get("modified", "")),
        })
    return result


@frappe.whitelist()
def sas_delete_view(view_name, report_key):
    """Deletes a saved view for the current user."""
    if frappe.session.user == "Guest":
        return

    existing = frappe.db.get_value(
        "SMRITI Saved View",
        {"view_name": view_name, "report_key": report_key, "owner": frappe.session.user},
        "name"
    )
    if existing:
        frappe.delete_doc("SMRITI Saved View", existing, ignore_permissions=True)
        frappe.db.commit()
        return {"status": "deleted"}
    return {"status": "not_found"}


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_export_excel(report_key, filters=None, state_json=None):
    """
    Generates and streams an Excel file server-side via openpyxl.
    Called by Export Center when user clicks 'Export Excel'.
    """
    _check_authenticated()

    _check_report_permission(report_key)

    filters = _parse_json(filters, {})
    state = _parse_json(state_json, {})
    view_name = state.get("view_name")

    # Fetch all rows (no pagination for export)
    try:
        meta = get_sas_report_metadata(report_key)
        dataset_key = meta.get("dataset_key")
        columns = meta.get("columns", [])
    except Exception as e:
        frappe.throw(f"Could not load report metadata: {str(e)}")

    if dataset_key and dataset_key in DATASET_REGISTRY:
        engine = DatasetEngine(dataset_key, filters, page=1, page_size=50000)
        rows = engine.fetch()["rows"]
    else:
        try:
            from smriti_retail_os.reports_api import SmritiReportEngine
            rows = SmritiReportEngine(report_key, filters=filters).run()
        except Exception as e:
            frappe.throw(f"Error fetching report data: {str(e)}")

    from smriti_retail_os.analytics_studio.sas_export import stream_excel_response
    stream_excel_response(report_key, rows, columns, filters, view_name)


# ─────────────────────────────────────────────────────────────────────────────
# FORMULA EXPLAIN
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def sas_get_formula_explain(report_key, fieldname):
    """
    Returns the full Explain payload for a column field:
    formula, variables, worked example, business meaning,
    interpretation guide, related KPIs, related reports, source.
    Delegates to existing get_report_glossary() in reports_api.
    """
    _check_authenticated()

    try:
        from smriti_retail_os.reports_api import get_report_glossary
        glossary = get_report_glossary(report_key)
    except Exception:
        glossary = []

    # Find the specific field's glossary entry
    field_entry = None
    if isinstance(glossary, list):
        for entry in glossary:
            if entry.get("fieldname") == fieldname or entry.get("term_id") == fieldname:
                field_entry = entry
                break

    if not field_entry:
        # Return minimal explain for fields without a registered formula
        return {
            "fieldname": fieldname,
            "label": fieldname.replace("_", " ").title(),
            "formula": None,
            "variables": [],
            "worked_example": None,
            "business_meaning": f"This field represents the {fieldname.replace('_', ' ')} value from the report.",
            "interpretation": None,
            "recommended_action": None,
            "related_kpis": [],
            "related_reports": [],
            "data_source": "SMRITI Report Engine",
            "formula_version": "1.0",
            "last_updated": None,
            "approved_by": None,
        }

    # Enrich from Formula Registry if formula_id is linked
    formula_detail = {}
    formula_id = field_entry.get("formula_id") or field_entry.get("linked_formula")
    if formula_id and frappe.db.exists("SMRITI Formula Definition", formula_id):
        fd = frappe.get_doc("SMRITI Formula Definition", formula_id)
        formula_detail = {
            "formula": fd.get("formula_expression"),
            "formula_version": fd.get("version"),
            "last_updated": str(fd.get("modified", "")),
            "approved_by": fd.get("approved_by"),
        }

    return {
        "fieldname": fieldname,
        "label": field_entry.get("label", fieldname),
        "formula": formula_detail.get("formula") or field_entry.get("formula_expression"),
        "variables": field_entry.get("variables", []),
        "worked_example": field_entry.get("worked_example"),
        "business_meaning": field_entry.get("business_meaning") or field_entry.get("description"),
        "interpretation": field_entry.get("interpretation_guide"),
        "recommended_action": field_entry.get("recommended_action"),
        "related_kpis": field_entry.get("related_kpis", []),
        "related_reports": field_entry.get("related_reports", []),
        "data_source": field_entry.get("data_source", "SMRITI Report Engine"),
        "formula_version": formula_detail.get("formula_version", "1.0"),
        "last_updated": formula_detail.get("last_updated") or str(field_entry.get("modified", "")),
        "approved_by": formula_detail.get("approved_by"),
    }
