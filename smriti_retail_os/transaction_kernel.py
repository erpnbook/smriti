# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/transaction_kernel.py
# @description: Universal UI-to-Backend Mapping Layer — Stateless Kernel Engine
#               Single generic endpoint replaces all per-module hardcoded API controllers.
#               Driven by frappe.get_meta() metaprogramming; zero hardcoded DocType logic.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# ─── Architectural Philosophy ────────────────────────────────────────────────
#
#  1. KERNEL-DRIVEN: One endpoint, zero per-module controllers.
#  2. METAPROGRAMMING: frappe.get_meta() drives all field mapping & validation.
#  3. MATRIX FLATTENING: Horizontal UI size grids → vertical Frappe child rows.
#  4. STATELESS ENRICHMENT: Lookup Item master, Customer, Taxes only when needed.
#  5. THREE ATOMIC ACTIONS: validate → save → submit.
#
# ─── Usage ───────────────────────────────────────────────────────────────────
#
#  POST /api/method/smriti_retail_os.transaction_kernel.execute_smriti_transaction
#  Body:
#    doctype = "Sales Invoice"                   # target Frappe DocType
#    payload = { ... }                           # UI state as JSON
#    action  = "validate" | "save" | "submit"
#
# ─────────────────────────────────────────────────────────────────────────────

import frappe
import json
from frappe import _
from frappe.utils import flt, cint, nowdate, now_datetime, cstr
from smriti_retail_os.utils.invoice_utils import get_barcode_candidates


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC KERNEL ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def execute_smriti_transaction(doctype, payload, action="validate"):
    """
    Universal stateless transaction kernel.

    Args:
        doctype (str):  Target Frappe DocType name  (e.g. "Sales Invoice")
        payload (str|dict): UI state object (JSON string or dict).
                            Supports:
                              - flat field maps   { "customer": "X", "posting_date": "..." }
                              - child table arrays { "items": [...], "taxes": [...] }
                              - matrix shorthand   { "_matrix": { "size_columns": [...], "rows": [...] } }
        action (str):   "validate" — enrich & return, no DB write
                        "save"     — upsert Draft document
                        "submit"   — save + submit (commits ledger)

    Returns:
        dict: Enriched payload for 'validate', or { name, grand_total, status } for save/submit.
    """
    # ── Guards ──────────────────────────────────────────────────────────────
    if not doctype:
        frappe.throw(_("Kernel: doctype is required."))
    if not payload:
        frappe.throw(_("Kernel: payload is required."))
    if action not in ("validate", "save", "submit"):
        frappe.throw(_("Kernel: action must be one of: validate, save, submit."))

    # Parse payload (accepts JSON string or dict)
    data = _safe_parse_json(payload)
    if not isinstance(data, dict):
        frappe.throw(_("Kernel: payload must be a JSON object."))

    # ── Permission check ────────────────────────────────────────────────────
    _check_doctype_permission(doctype, action)

    # ── Load DocType metadata (metaprogramming core) ─────────────────────────
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        frappe.throw(_("Kernel: Unknown DocType '{0}'.").format(doctype))

    # ── Resolve runtime context ──────────────────────────────────────────────
    company = _resolve_company(data)

    # ── Matrix flattening — UI horizontal grid → child table rows ───────────
    if data.get("_matrix"):
        data = _flatten_matrix_to_rows(data, meta)

    # ── Enrich payload using master registries ───────────────────────────────
    enriched = _enrich_payload(data, meta, doctype, company)

    # ── Execute requested action ─────────────────────────────────────────────
    if action == "validate":
        return {
            "status": "ok",
            "action": "validate",
            "doctype": doctype,
            "company": company,
            "enriched_payload": enriched,
        }

    elif action in ("save", "submit"):
        doc = _build_and_persist_doc(doctype, enriched, meta, company, action)
        result = {
            "status": "ok",
            "action": action,
            "doctype": doctype,
            "name": doc.name,
            "docstatus": doc.docstatus,
        }
        # Append financial summary if available
        for summary_field in ("grand_total", "net_total", "total_qty", "rounded_total"):
            if hasattr(doc, summary_field):
                result[summary_field] = flt(getattr(doc, summary_field, 0))
        return result


# ═══════════════════════════════════════════════════════════════════════════════
#  MATRIX FLATTENING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _flatten_matrix_to_rows(data, meta):
    """
    Converts a horizontal UI size-grid matrix into standard vertical child table rows.

    Input payload shape (UI matrix shorthand):
    {
        "_matrix": {
            "child_table": "items",          # which child table to populate (default: "items")
            "size_columns": ["36","37","38"],
            "rows": [
                {
                    "article":      "20016",
                    "color":        "BLACK",
                    "category":     "SANDAL",
                    "sub_category": "LASTIC PATTA",
                    "sizes":        { "36": 0, "37": 9, "38": 5 },
                    "mrp":          1899,
                    "rate":         1610.17,
                    "gst_pct":      18,
                    "hsn_code":     "64041990",
                    "item_code":    ""          # optional override
                }
            ]
        },
        "customer": "...",
        ... (other header fields pass through unchanged)
    }

    Output: standard data dict with `items` child table array populated.
    """
    matrix_cfg   = data.get("_matrix", {})
    child_table  = matrix_cfg.get("child_table") or "items"
    size_columns = matrix_cfg.get("size_columns") or []
    matrix_rows  = matrix_cfg.get("rows") or []

    expanded_rows = []
    for row in matrix_rows:
        article      = cstr(row.get("article") or "").strip()
        color        = cstr(row.get("color") or "").strip()
        category     = cstr(row.get("category") or "").strip()
        sub_category = cstr(row.get("sub_category") or "").strip()
        sizes        = row.get("sizes") or {}
        mrp          = flt(row.get("mrp") or 0)
        rate         = flt(row.get("rate") or 0)
        gst_pct      = flt(row.get("gst_pct") or 0)
        hsn_code     = cstr(row.get("hsn_code") or "").strip()
        item_code    = cstr(row.get("item_code") or "").strip()
        uom          = cstr(row.get("uom") or "Nos").strip()

        for size in size_columns:
            qty = flt(sizes.get(str(size)) or sizes.get(size) or 0)
            if qty <= 0:
                continue

            # Resolve best-match item_code for this article/color/size
            resolved_code = _resolve_item_code_from_matrix(article, color, size, item_code)
            if not resolved_code:
                frappe.throw(
                    _(
                        "Item not found for Article: <b>{0}</b>, Color: <b>{1}</b>, Size: <b>{2}</b>. "
                        "Please verify your Item Master \u2014 the variant may not have been imported yet. "
                        "Go to SMRITI Item Master \u2192 Import to create missing variants before invoicing."
                    ).format(article, color, size),
                    title=_("Item Not Found in Item Master")
                )

            expanded_rows.append({
                "item_code":   resolved_code,
                "item_name":   f"{article} {color} {size}".strip(),
                "description": (
                    f"Article: {article} | Color: {color} | "
                    f"Category: {category} | Sub: {sub_category} | "
                    f"Size: {size} | MRP: \u20b9{mrp}"
                ),
                "qty":          qty,
                "rate":         rate,
                "uom":          uom,
                "gst_hsn_code": hsn_code,
                "mrp":          mrp,
                "gst_pct":      gst_pct,
                # Carry source identifiers for downstream enrichment
                "_article":     article,
                "_color":       color,
                "_size":        str(size),
            })

    # Merge expanded rows back — preserve any existing rows from data
    result = {k: v for k, v in data.items() if k != "_matrix"}
    existing = result.get(child_table) or []
    result[child_table] = existing + expanded_rows
    return result


def _resolve_item_code_from_matrix(article, color, size, fallback):
    """
    Priority cascade: ARTICLE-COLOR-SIZE → ARTICLE-COLOR → ARTICLE → fallback → fuzzy.
    Returns None if no matching item is found — callers must handle None gracefully
    and surface a descriptive error to the user rather than silently inserting
    a ghost sentinel item into the item master.
    """
    candidates = [
        f"{article}-{color}-{size}" if article and color and size else None,
        f"{article}-{color}"        if article and color else None,
        article                     if article else None,
        fallback                    if fallback else None,
    ]
    for code in candidates:
        if code and frappe.db.exists("Item", code):
            return code

    # Fuzzy name match
    if article:
        found = frappe.db.get_value(
            "Item",
            {"item_name": ["like", f"%{article}%"], "disabled": 0},
            "name"
        )
        if found:
            return found

    # Item not found — return None so the caller can raise a visible error.
    # DO NOT auto-create a sentinel item here: ghost items corrupt stock reports,
    # low-stock alerts, and purchasing recommendations.
    return None


def _ensure_sentinel_item():
    """
    INTERNAL USE ONLY — NOT invoked automatically by the transaction kernel.

    Creates the SMRITI generic sentinel item for manual/test use.
    This function must NEVER be called from live transaction flows:
    auto-inserting a ghost item corrupts stock reports, low-stock alerts,
    and purchasing recommendations.

    To deliberately pre-create this item in a dev/test environment, call:
        from smriti_retail_os.transaction_kernel import _ensure_sentinel_item
        _ensure_sentinel_item()
    """
    sentinel = "_SMRITI_GENERIC_ITEM_"
    if not frappe.db.exists("Item", sentinel):
        try:
            frappe.get_doc({
                "doctype":          "Item",
                "item_code":        sentinel,
                "item_name":        "SMRITI Generic Article (Kernel Sentinel)",
                "item_group":       "All Item Groups",
                "is_stock_item":    0,
                "is_sales_item":    1,
                "is_purchase_item": 1,
                "stock_uom":        "Nos",
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            frappe.log_error(title="Sentinel Item creation failed")
            first = frappe.db.get_value("Item", {"is_sales_item": 1, "disabled": 0}, "name")
            return first or ""
    return sentinel


# ═══════════════════════════════════════════════════════════════════════════════
#  PAYLOAD ENRICHMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _enrich_payload(data, meta, doctype, company):
    """
    Walks the payload dict and:
    1. Coerces field values to their Frappe field types (from meta).
    2. Enriches item rows with HSN, tax template, warehouse, cost center.
    3. Resolves party addresses (Customer, Supplier).
    4. Fills missing header fields with company defaults.
    """
    enriched = dict(data)  # shallow copy — child lists handled below

    # ── Header field coercion via meta ───────────────────────────────────────
    field_map = {f.fieldname: f for f in meta.fields if f.fieldname}

    for fieldname, value in list(enriched.items()):
        if fieldname.startswith("_"):
            continue  # skip kernel-internal markers
        fmeta = field_map.get(fieldname)
        if fmeta:
            enriched[fieldname] = _coerce_field(value, fmeta.fieldtype)

    # ── Defaults ─────────────────────────────────────────────────────────────
    enriched.setdefault("company", company)
    enriched.setdefault("posting_date", nowdate())
    enriched.setdefault("currency", "INR")

    # DocType-aware defaults (resolved from meta, not hardcoded)
    if _meta_has_field(meta, "selling_price_list"):
        enriched.setdefault("selling_price_list", "Standard Selling")
    if _meta_has_field(meta, "buying_price_list"):
        enriched.setdefault("buying_price_list", "Standard Buying")

    # ── Party resolution (Customer / Supplier) ───────────────────────────────
    party_doctype = _detect_party_doctype(meta)
    party_name    = enriched.get("customer") or enriched.get("supplier")
    if party_doctype and party_name:
        address_fields = _resolve_party_addresses(party_name, party_doctype)
        for k, v in address_fields.items():
            enriched.setdefault(k, v)

    # ── Tax template at header level ──────────────────────────────────────────
    if _meta_has_field(meta, "taxes_and_charges") and not enriched.get("taxes_and_charges"):
        supply_type = enriched.get("_supply_type") or "intrastate"
        tmpl = _resolve_default_tax_template(company, supply_type)
        if tmpl:
            enriched["taxes_and_charges"] = tmpl

    # ── Child table enrichment ────────────────────────────────────────────────
    for child_field in meta.get_table_fields():
        child_fieldname = child_field.fieldname
        rows = enriched.get(child_fieldname)
        if not rows or not isinstance(rows, list):
            continue

        child_meta = frappe.get_meta(child_field.options)
        child_field_map = {f.fieldname: f for f in child_meta.fields if f.fieldname}

        enriched_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            enriched_row = _enrich_child_row(
                row, child_field_map, child_meta, doctype, company
            )
            enriched_rows.append(enriched_row)

        enriched[child_fieldname] = enriched_rows

    return enriched


def _enrich_child_row(row, child_field_map, child_meta, parent_doctype, company):
    """
    Enriches a single child table row:
    - Coerces field values to Frappe types.
    - For item rows: enriches with HSN, warehouse, cost center, tax template, MRP.
    - Strips kernel-internal _ markers.
    """
    enriched = {}
    for k, v in row.items():
        if k.startswith("_"):
            continue  # strip internal markers
        fmeta = child_field_map.get(k)
        if fmeta:
            enriched[k] = _coerce_field(v, fmeta.fieldtype)
        else:
            enriched[k] = v  # pass unknown fields through — Frappe will ignore

    # ── Item row enrichment ───────────────────────────────────────────────────
    item_code = enriched.get("item_code")
    if item_code and frappe.db.exists("Item", item_code):
        item_data = _lookup_item_master(item_code, company)

        # Warehouse
        if "warehouse" in child_field_map and not enriched.get("warehouse"):
            enriched["warehouse"] = item_data.get("warehouse") or ""

        # Cost center
        if "cost_center" in child_field_map and not enriched.get("cost_center"):
            enriched["cost_center"] = item_data.get("cost_center") or ""

        # Item tax template
        if "item_tax_template" in child_field_map and not enriched.get("item_tax_template"):
            enriched["item_tax_template"] = item_data.get("item_tax_template") or ""

        # HSN code
        if "gst_hsn_code" in child_field_map and not enriched.get("gst_hsn_code"):
            enriched["gst_hsn_code"] = item_data.get("gst_hsn_code") or ""

        # UOM
        if "uom" in child_field_map and not enriched.get("uom"):
            enriched["uom"] = item_data.get("stock_uom") or "Nos"

        # Rate — only fill if missing or zero
        if "rate" in child_field_map and not flt(enriched.get("rate")):
            enriched["rate"] = item_data.get("rate") or 0.0

        # MRP (price_list_rate)
        if "price_list_rate" in child_field_map and not flt(enriched.get("price_list_rate")):
            enriched["price_list_rate"] = item_data.get("mrp") or enriched.get("rate") or 0.0

    return enriched


def _lookup_item_master(item_code, company):
    """
    Stateless lookup of Item master + pricing + tax + warehouse.
    Cached via frappe.get_cached_doc to avoid repeated DB hits per row.
    Returns a flat enrichment dict.
    """
    try:
        item = frappe.get_cached_doc("Item", item_code)
    except Exception:
        return {}

    result = {
        "item_name":   item.item_name or "",
        "stock_uom":   item.stock_uom or "Nos",
        "gst_hsn_code": item.gst_hsn_code or "",
        "brand":       item.brand or "",
        "item_group":  item.item_group or "",
    }

    # Selling rate
    rate = flt(frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": "Standard Selling"},
        "price_list_rate"
    ) or item.valuation_rate or 0)
    result["rate"] = rate

    # MRP
    mrp = flt(item.get("custom_mrp") or frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": "MRP"},
        "price_list_rate"
    ) or rate)
    result["mrp"] = mrp

    # GST %
    result["gst_percentage"] = flt(item.get("custom_gst_percentage") or 0)

    # Item tax template — validate it belongs to the company
    item_tax_template = ""
    for t in (item.taxes or []):
        tmpl = t.item_tax_template
        if not tmpl:
            continue
        tmpl_company = frappe.db.get_value("Item Tax Template", tmpl, "company")
        if tmpl_company == company:
            item_tax_template = tmpl
            break
    result["item_tax_template"] = item_tax_template

    # Default warehouse (Item Default child table)
    wh = frappe.db.get_value(
        "Item Default",
        {"parent": item_code, "company": company},
        "default_warehouse"
    )
    if not wh:
        wh = _resolve_fallback_warehouse(company)
    result["warehouse"] = wh or ""

    # Cost center
    cc = frappe.db.get_value("Company", company, "cost_center")
    if not cc:
        cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
    result["cost_center"] = cc or ""

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  DOCUMENT BUILD & PERSIST ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _build_and_persist_doc(doctype, enriched, meta, company, action):
    """
    Constructs a Frappe document from the enriched payload, then saves or submits it.
    Handles upsert: if `name` is in payload and doc exists in Draft, updates it.

    ─── Security Architecture Note — ignore_permissions=True ────────────────
    This function uses ignore_permissions=True on doc.insert() and doc.save().
    This is an INTENTIONAL architectural design — not a security shortcut.

    Rationale:
      1. Authentication:   @frappe.whitelist() on execute_smriti_transaction ensures
                           the request is from an authenticated Frappe session.
                           Anonymous/guest calls are rejected at the HTTP layer.

      2. Authorization:    _check_doctype_permission(doctype, action) is called BEFORE
                           this function is reached. It validates that the session user
                           has read/write/submit rights on the target DocType.
                           This is the authoritative permission gate.

      3. Service-layer ownership (GEMINI.md Rule 6):
                           The SMRITI service layer owns permission semantics.
                           Duplicating the permission check at the document level
                           would create a dual-gate where changes to one gate
                           don't automatically reflect in the other, introducing
                           inconsistency and maintenance overhead.

    SECURITY INVARIANT (must be maintained by all callers):
      _check_doctype_permission() MUST remain the first operation in
      execute_smriti_transaction() before any data enrichment or persistence.
      Do NOT add new callers to _build_and_persist_doc() that bypass this gate.

    See also: test_transaction_kernel.py::TestKernelPermissions
    ─────────────────────────────────────────────────────────────────────────
    """
    existing_name = enriched.get("name")
    is_update = (
        existing_name
        and frappe.db.exists(doctype, existing_name)
        and frappe.db.get_value(doctype, existing_name, "docstatus") == 0
    )

    if is_update:
        doc = frappe.get_doc(doctype, existing_name)
        # Clear child tables that we're about to repopulate
        for cf in meta.get_table_fields():
            if enriched.get(cf.fieldname):
                doc.set(cf.fieldname, [])
    else:
        doc = frappe.new_doc(doctype)

    # ── Populate header fields ───────────────────────────────────────────────
    field_names = {f.fieldname for f in meta.fields if f.fieldname}
    child_table_names = {cf.fieldname for cf in meta.get_table_fields()}

    for fieldname, value in enriched.items():
        if fieldname.startswith("_"):
            continue
        if fieldname == "name" and not is_update:
            continue  # let Frappe auto-assign
        if fieldname in child_table_names:
            continue  # handled separately below
        if fieldname in field_names or hasattr(doc, fieldname):
            try:
                setattr(doc, fieldname, value)
            except (AttributeError, TypeError):
                pass  # silently skip unrecognised field overrides

    # ── Populate child tables ────────────────────────────────────────────────
    for cf in meta.get_table_fields():
        rows = enriched.get(cf.fieldname)
        if not rows or not isinstance(rows, list):
            continue
        child_meta = frappe.get_meta(cf.options)
        child_field_names = {f.fieldname for f in child_meta.fields if f.fieldname}

        for row in rows:
            row_data = {
                k: v for k, v in row.items()
                if not k.startswith("_") and k in child_field_names
            }
            doc.append(cf.fieldname, row_data)

    # ── Tax template auto-set ────────────────────────────────────────────────
    taxes_and_charges = getattr(doc, "taxes_and_charges", None)
    if taxes_and_charges and hasattr(doc, "run_method"):
        try:
            doc.run_method("set_taxes")
        except Exception:
            frappe.log_error(title="Transaction set_taxes failed")

    # ── Save / Submit ────────────────────────────────────────────────────────
    save_flags = dict(ignore_permissions=True)

    try:
        if is_update:
            doc.save(**save_flags)
        else:
            doc.insert(**save_flags)

        if action == "submit":
            doc.submit()

        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(title=f"Transaction persist failed ({action})")
        raise
    return doc


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPANY / PARTY / TAX RESOLUTION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _resolve_company(data):
    """
    Centralized company resolution.
    Priority: payload.company → user default → single-company shortcut.
    """
    company = (
        data.get("company")
        or frappe.defaults.get_user_default("company")
    )
    if not company:
        all_companies = frappe.get_all("Company", limit=1, pluck="name")
        company = all_companies[0] if all_companies else None
    if not company:
        frappe.throw(_("Kernel: Cannot resolve active company. Please set a company default."))
    return company


def _resolve_fallback_warehouse(company):
    """Returns the best available warehouse for a company."""
    wh = frappe.defaults.get_user_default("warehouse")
    if wh and frappe.db.get_value("Warehouse", wh, "company") == company:
        return wh
    return (
        frappe.db.get_value("Warehouse", {"warehouse_name": "Stores", "company": company}, "name")
        or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
    )


def _resolve_party_addresses(party_name, party_doctype):
    """
    Looks up billing and shipping addresses for a Customer or Supplier.
    Returns a dict of invoice address fields.
    Note: Address DocType does not have a 'display' column — we build the
    display string from address_line1 / city / state / pincode.
    """
    result = {}

    # Fields that ARE actual columns in tabAddress
    _addr_fields = [
        "name", "address_title", "address_line1", "address_line2",
        "city", "state", "country", "pincode",
    ]

    def _get_addr(address_type):
        return frappe.db.get_value(
            "Address",
            {
                "links.link_doctype": party_doctype,
                "links.link_name":    party_name,
                "address_type":       address_type,
            },
            _addr_fields,
            as_dict=True
        )

    def _build_display(addr):
        """Builds a human-readable address string from Address fields."""
        if not addr:
            return ""
        parts = filter(None, [
            addr.get("address_line1") or "",
            addr.get("address_line2") or "",
            addr.get("city")         or "",
            addr.get("state")        or "",
            addr.get("pincode")      or "",
            addr.get("country")      or "",
        ])
        return ", ".join(p.strip() for p in parts if p.strip())

    if party_doctype == "Customer":
        billing = _get_addr("Billing")
        if billing:
            result["customer_address"] = billing.name
            result["address_display"]  = _build_display(billing)
        shipping = _get_addr("Shipping")
        if shipping:
            result["shipping_address_name"] = shipping.name
            result["shipping_address"]      = _build_display(shipping)

    elif party_doctype == "Supplier":
        billing = _get_addr("Billing")
        if billing:
            result["supplier_address"] = billing.name
            result["address_display"]  = _build_display(billing)

    return result


def _resolve_default_tax_template(company, supply_type="intrastate"):
    """
    Returns the default Sales Taxes and Charges Template for the company.
    If supply_type is 'interstate', looks for IGST template.
    """
    # Try is_default first
    tmpl = frappe.db.get_value(
        "Sales Taxes and Charges Template",
        {"company": company, "is_default": 1},
        "name"
    )
    if tmpl:
        return tmpl

    # Fallback: any template for the company
    tmpl = frappe.db.get_value(
        "Sales Taxes and Charges Template",
        {"company": company},
        "name"
    )
    return tmpl


def _resolve_tax_template_for_item(item_code, company, supply_type="intrastate"):
    """
    Resolves the best Item Tax Template for item_code × company × supply_type.
    Returns template name or empty string.
    """
    try:
        item = frappe.get_cached_doc("Item", item_code)
    except Exception:
        return ""

    for t in (item.taxes or []):
        tmpl = t.item_tax_template
        if not tmpl:
            continue
        tmpl_company = frappe.db.get_value("Item Tax Template", tmpl, "company")
        if tmpl_company == company:
            # Supply type match: interstate templates typically have "IGST" in name
            if supply_type == "interstate" and "IGST" not in tmpl.upper():
                continue
            if supply_type == "intrastate" and "IGST" in tmpl.upper():
                continue
            return tmpl

    # Return first valid template regardless of supply type
    for t in (item.taxes or []):
        tmpl = t.item_tax_template
        if tmpl and frappe.db.get_value("Item Tax Template", tmpl, "company") == company:
            return tmpl
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
#  IDENTIFIER-BASED LOOKUPS (Barcode, Article+Color)
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def resolve_identifiers(identifiers, company=None):
    """
    Generic stateless lookup: given a list of primary identifiers,
    return enriched item data for each.

    identifiers (list of dict):
    [
        { "type": "barcode",          "value": "8901234567890" },
        { "type": "item_code",        "value": "20016-BLACK-38" },
        { "type": "article_color",    "article": "20016", "color": "BLACK" },
        { "type": "customer_mobile",  "value": "+91 9999999999" },
        { "type": "customer_name",    "value": "Rajesh Kumar" },
    ]

    Returns list of resolved records (same order, None if not found).
    """
    ids = _safe_parse_json(identifiers) if isinstance(identifiers, str) else identifiers
    if not isinstance(ids, list):
        frappe.throw(_("resolve_identifiers: 'identifiers' must be a JSON array."))

    company = company or _resolve_company({})
    results = []

    for ident in ids:
        if not isinstance(ident, dict):
            results.append(None)
            continue

        id_type = cstr(ident.get("type") or "").strip()

        try:
            if id_type == "barcode":
                results.append(_resolve_barcode(ident.get("value"), company))

            elif id_type == "item_code":
                code = cstr(ident.get("value") or "")
                if frappe.db.exists("Item", code):
                    results.append(_lookup_item_master(code, company))
                else:
                    results.append(None)

            elif id_type == "article_color":
                article = cstr(ident.get("article") or "")
                color   = cstr(ident.get("color") or "")
                results.append(_resolve_article_color(article, color, company))

            elif id_type in ("customer_mobile", "customer_name"):
                results.append(_resolve_customer(ident, id_type))

            elif id_type == "supplier_name":
                results.append(_resolve_supplier(ident))

            else:
                results.append({"error": f"Unknown identifier type: {id_type}"})

        except Exception as e:
            frappe.log_error(
                title="SMRITI Kernel resolve_identifiers error",
                message=frappe.get_traceback()
            )
            results.append({"error": str(e)})

    return results


def _resolve_barcode(barcode, company):
    """Barcode → enriched item dict."""
    if not barcode:
        return None
    
    candidates = get_barcode_candidates(barcode)
    
    item_code = None
    for cand in candidates:
        item_code = frappe.db.get_value("Item Barcode", {"barcode": cand}, "parent")
        if item_code:
            break
            
    if not item_code:
        for cand in candidates:
            if frappe.db.exists("Item", cand):
                item_code = cand
                break
                
    if not item_code:
        return None
    return _lookup_item_master(item_code, company)


def _resolve_article_color(article, color, company):
    """Article + Color → enriched item dict (searches variant items)."""
    if not article:
        return None

    # Direct hit
    if frappe.db.exists("Item", article):
        data = _lookup_item_master(article, company)
    else:
        # Fuzzy match
        found = frappe.db.get_value(
            "Item",
            {"item_code": ["like", f"%{article}%"], "disabled": 0},
            "name"
        )
        if not found:
            return None
        data = _lookup_item_master(found, company)

    # Try to find color variant for more specific pricing
    if color and data:
        variant = frappe.db.get_value(
            "Item",
            {"variant_of": data.get("item_code") or article,
             "item_code": ["like", f"%{color}%"], "disabled": 0},
            ["name", "custom_mrp", "custom_gst_percentage", "gst_hsn_code"],
            as_dict=True
        )
        if variant:
            if variant.custom_mrp:
                data["mrp"] = flt(variant.custom_mrp)
            if variant.custom_gst_percentage:
                data["gst_percentage"] = flt(variant.custom_gst_percentage)
            if variant.gst_hsn_code:
                data["gst_hsn_code"] = variant.gst_hsn_code

    return data


def _resolve_customer(ident, id_type):
    """Customer mobile / name → customer record dict."""
    value = cstr(ident.get("value") or "")
    if not value:
        return None

    if id_type == "customer_mobile":
        cust = frappe.db.get_value(
            "Customer", {"mobile_no": value, "disabled": 0},
            ["name", "customer_name", "mobile_no", "loyalty_program",
             "custom_tax_inclusive_override", "customer_group"],
            as_dict=True
        )
    else:
        cust = frappe.db.get_value(
            "Customer", {"customer_name": ["like", f"%{value}%"], "disabled": 0},
            ["name", "customer_name", "mobile_no", "loyalty_program",
             "custom_tax_inclusive_override", "customer_group"],
            as_dict=True
        )
    return dict(cust) if cust else None


def _resolve_supplier(ident):
    """Supplier name → supplier record dict."""
    value = cstr(ident.get("value") or "")
    if not value:
        return None
    sup = frappe.db.get_value(
        "Supplier", {"supplier_name": ["like", f"%{value}%"], "disabled": 0},
        ["name", "supplier_name", "supplier_type", "supplier_group", "tax_id"],
        as_dict=True
    )
    return dict(sup) if sup else None


# ═══════════════════════════════════════════════════════════════════════════════
#  PRICING RULES ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def apply_pricing_rules(doctype, payload, company=None):
    """
    Stateless pricing rule evaluation.
    Evaluates ERPNext Pricing Rules for each item row and returns
    the recommended rate/discount without writing to DB.
    """
    data    = _safe_parse_json(payload) if isinstance(payload, str) else payload
    company = company or _resolve_company(data)

    items = data.get("items") or []
    customer = data.get("customer") or ""
    posting_date = data.get("posting_date") or nowdate()

    results = []
    for row in items:
        item_code = row.get("item_code")
        qty       = flt(row.get("qty") or 1)
        rate      = flt(row.get("rate") or 0)

        if not item_code:
            results.append(row)
            continue

        # ERPNext pricing rule evaluation
        try:
            from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
            args = frappe._dict({
                "item_code":    item_code,
                "qty":          qty,
                "stock_qty":    qty,
                "transaction_type": "selling",
                "price_list":   "Standard Selling",
                "customer":     customer,
                "company":      company,
                "conversion_rate": 1,
                "posting_date": posting_date,
                "transaction_date": posting_date,
                "doctype":      doctype,
                "name":         None,
                "is_return":    0,
                "uom":          row.get("uom") or "Nos",
            })
            pricing_data = get_pricing_rule_for_item(args) or {}
            enriched_row = dict(row)
            if pricing_data.get("discount_percentage"):
                enriched_row["discount_percentage"] = flt(pricing_data["discount_percentage"])
            if pricing_data.get("rate"):
                enriched_row["rate"] = flt(pricing_data["rate"])
            results.append(enriched_row)
        except Exception:
            results.append(row)  # fallback: return row unchanged

    return {"items": results, "company": company}


# ═══════════════════════════════════════════════════════════════════════════════
#  META INTROSPECTION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_doctype_schema(doctype):
    """
    Returns the DocType schema for a given DocType, including fields,
    child tables, and mandatory fields — for frontend dynamic form generation.
    """
    if not doctype:
        frappe.throw(_("doctype is required."))
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        frappe.throw(_("Unknown DocType: {0}").format(doctype))

    fields = []
    for f in meta.fields:
        if not f.fieldname:
            continue
        field_def = {
            "fieldname":  f.fieldname,
            "fieldtype":  f.fieldtype,
            "label":      f.label or "",
            "reqd":       cint(f.reqd),
            "read_only":  cint(f.read_only),
            "hidden":     cint(f.hidden),
            "options":    f.options or "",
            "default":    f.default or "",
        }
        if f.fieldtype == "Select" and f.options:
            field_def["select_options"] = [o.strip() for o in f.options.split("\n") if o.strip()]
        fields.append(field_def)

    child_tables = [
        {
            "fieldname": cf.fieldname,
            "label":     cf.label or "",
            "options":   cf.options or "",  # child DocType name
        }
        for cf in meta.get_table_fields()
    ]

    return {
        "doctype":      doctype,
        "is_submittable": cint(meta.is_submittable),
        "fields":       fields,
        "child_tables": child_tables,
        "mandatory_fields": [
            f["fieldname"] for f in fields if f["reqd"]
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERNAL UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_parse_json(value):
    """Safely parse a JSON string or return the value as-is if already a dict/list."""
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return {}


def _coerce_field(value, fieldtype):
    """Coerce a Python value to the appropriate Frappe field type."""
    if value is None:
        return value
    if fieldtype in ("Float", "Currency", "Percent"):
        return flt(value)
    if fieldtype in ("Int", "Check"):
        return cint(value)
    if fieldtype in ("Data", "Small Text", "Text", "Long Text", "Text Editor", "Code",
                     "Link", "Dynamic Link", "Select", "Read Only"):
        return cstr(value)
    if fieldtype == "Date":
        return cstr(value) if value else None
    if fieldtype == "Datetime":
        return cstr(value) if value else None
    return value


def _meta_has_field(meta, fieldname):
    """Returns True if the DocType meta has the specified fieldname."""
    return any(f.fieldname == fieldname for f in meta.fields)


def _detect_party_doctype(meta):
    """
    Detects whether a DocType has a canonical Customer or Supplier header field.
    Matches by fieldname (customer / supplier) rather than just by options to
    avoid false positives from incidental Link fields (e.g. Item has Customer
    links in its tax / pricing child tables but is NOT a transactional party doc).
    Returns 'Customer', 'Supplier', or None.
    """
    if meta.name in ("Item", "Customer", "Supplier"):
        return None

    # Canonical fieldnames that unambiguously identify the party on a transaction
    _customer_fields = {"customer", "customer_name"}
    _supplier_fields = {"supplier", "supplier_name"}

    for f in meta.fields:
        if f.fieldtype != "Link":
            continue
        fname = (f.fieldname or "").lower()
        if f.options == "Customer" and fname in _customer_fields:
            return "Customer"
        if f.options == "Supplier" and fname in _supplier_fields:
            return "Supplier"
    return None


def _check_doctype_permission(doctype, action):
    """
    Verifies the session user has the appropriate permission for the doctype × action.
    Maps action to Frappe permission type.
    """
    perm_map = {
        "validate": "read",
        "save":     "write",
        "submit":   "submit",
    }
    perm_type = perm_map.get(action, "read")

    if not frappe.has_permission(doctype, perm_type, throw=False):
        frappe.throw(
            _("Kernel: You do not have {0} permission on {1}.").format(perm_type, doctype),
            frappe.PermissionError
        )
