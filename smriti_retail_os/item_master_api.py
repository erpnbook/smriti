# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/item_master_api.py
# @description: Backend API for SMRITI Item Master import, creation, and variant management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import flt, cint
from frappe import _
from smriti_retail_os import smriti


# ─────────────────────────────────────────────────────────────────────────────
#  SECURITY: TRUNCATE ALLOWLISTS
#  Raw SQL TRUNCATE is used only in admin factory-reset operations.
#  Table names MUST come from one of these allowlists — never from user input.
#  Architecture: H-7 remediation (hardcoding audit 2026-07-03)
# ─────────────────────────────────────────────────────────────────────────────

_FACTORY_RESET_TRANSACTION_DOCTYPES = frozenset([
    "Sales Invoice", "Sales Invoice Item",
    "POS Invoice", "POS Invoice Item", "POS Invoice Reference",
    "Payment Entry", "Payment Entry Reference", "Payment Entry Deduction",
    "GL Entry", "Stock Ledger Entry", "Stock Entry", "Stock Entry Detail",
    "Purchase Order", "Purchase Order Item",
    "Purchase Receipt", "Purchase Receipt Item",
    "Payment Ledger Entry", "Serial No", "Batch",
])

_FACTORY_RESET_ITEM_DOCTYPES = frozenset([
    "Item", "Item Barcode", "Item Price", "Item Supplier",
    "Item Tax", "Item Attribute Value", "Item Variant Attribute",
    "Brand", "GST HSN Code",
])



# ─────────────────────────────────────────────────────────────────────────────
#  COLUMN DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

IMPORT_COLUMN_DEFS = [
    {"key": "BARCODE NO",           "label": "Barcode",           "width": "150px", "required": False},
    {"key": "PRODUCT STYLE CODE",   "label": "Style/Article No",  "width": "150px", "required": True},
    {"key": "ITEM DESCRIPTION",     "label": "Description",       "width": "220px", "required": True},
    {"key": "BRAND NAME",           "label": "Brand",             "width": "110px", "required": True},
    {"key": "COLOR",                "label": "Color",             "width": "100px", "required": True},
    {"key": "SIZE",                 "label": "Size",              "width": "65px",  "required": True},
    {"key": "PLANNED MRP",          "label": "MRP ₹",             "width": "90px",  "required": True, "type": "number"},
    {"key": "COST PRICE",           "label": "Cost ₹",            "width": "90px",  "required": False, "type": "number"},
    {"key": "PRODUCT TAX",          "label": "GST%",              "width": "65px",  "required": False, "type": "number", "choices": ["", "0", "5", "12", "18", "28"]},
    {"key": "HSN CODE",             "label": "HSN Code",          "width": "100px", "required": False},
    {"key": "GENDER",               "label": "Gender",            "width": "90px",  "required": True, "choices": ["", "MENS", "LADIES", "BOYS", "GIRLS", "UNISEX", "KIDS"]},
    {"key": "VENDOR CODE",          "label": "Vendor/Supplier",   "width": "130px", "required": True},
    {"key": "PURCHASE CLASS",       "label": "Purch. Class",      "width": "110px", "required": True, "choices": ["", "SIS", "FW", "MFW", "LFW", "BFW", "GFW", "KFW", "ASSTED", "SPORTS", "ACC", "BAG", "FORMAL", "CASUAL"]},
    {"key": "DEPARTMENT",           "label": "Department",        "width": "120px", "required": True},
    {"key": "MERCHANDISE CATEGORY", "label": "Merch. Cat.",       "width": "120px", "required": True},
    {"key": "Sub category",         "label": "Sub Category",      "width": "120px", "required": True},
    {"key": "HEELS",                "label": "Heels",             "width": "90px",  "required": True},
    {"key": "UPPER MATERIAL",       "label": "Upper Mat.",        "width": "120px", "required": True},
    {"key": "OUTSOLE",              "label": "Outsole",           "width": "100px", "required": False},
    {"key": "IMAGE LINK",           "label": "Image URL",         "width": "130px", "required": False},
    {"key": "Product Tax Group",    "label": "Tax Group",         "width": "120px", "required": False}
]

TEMPLATE_HEADERS = [c["key"] for c in IMPORT_COLUMN_DEFS]
REQUIRED_COLS = [c["key"] for c in IMPORT_COLUMN_DEFS if c.get("required")]
VALID_GST = {0, 5, 12, 18, 28}


@frappe.whitelist()
def get_import_column_defs():
    """Returns the single source of truth column definitions list for SMRITI Item Master Import."""
    return IMPORT_COLUMN_DEFS


def normalize_lookup(value):
    """Normalize lookups uniformly by stripping whitespace and converting to uppercase."""
    if value is None:
        return ""
    return str(value).strip().upper()


def validate_barcode(barcode, raise_exception=True):
    """
    Centralized validation for barcode value and format.
    Checks:
    - Non-empty
    - Alphanumeric, hyphens, and underscores only (no spaces, special characters)
    - Length between 3 and 30 characters.
    """
    if not barcode:
        msg = _("Barcode cannot be empty.")
        if raise_exception:
            frappe.throw(msg, title=_("Invalid Barcode"))
        return False, msg
        
    import re
    if not re.match(r"^[a-zA-Z0-9\-_]+$", str(barcode)):
        msg = _("Barcode '{0}' contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed (no spaces).").format(barcode)
        if raise_exception:
            frappe.throw(msg, title=_("Invalid Barcode"))
        return False, msg
        
    if len(str(barcode)) < 3 or len(str(barcode)) > 30:
        msg = _("Barcode must be between 3 and 30 characters.")
        if raise_exception:
            frappe.throw(msg, title=_("Invalid Barcode"))
        return False, msg
        
    return True, ""


def _build_import_lookup_cache():
    """
    Pre-loads all lookup sets needed by validate_import_rows and import_item_master
    in a single bulk query pass. This eliminates the N+1 DB query pattern where
    every row in the import grid triggered individual smriti.db.exists() calls.

    Returns a dict with:
      barcode_to_item   : {barcode: parent_item_code}  — from Item Barcode table
      existing_items    : set of all item_codes         — from Item table
      existing_vendors  : set of custom_vendor_code     — from Supplier table
      existing_brands   : set of brand names            — from Brand table
      attr_doctypes     : set of DocType names that exist on this instance
    """
    # 1. Barcode → parent item mapping (covers duplicate barcode check)
    raw_barcodes = smriti.db.sql(
        "SELECT barcode, parent FROM `tabItem Barcode`", as_dict=True
    )
    barcode_to_item = {r.barcode: r.parent for r in raw_barcodes}

    # 2. All item codes (covers item_code namespace collision check)
    existing_items = set(
        r[0] for r in smriti.db.sql("SELECT name FROM `tabItem`")
    )

    # 3. All vendor codes (covers supplier hard check)
    vendor_rows = smriti.db.sql(
        "SELECT custom_vendor_code FROM `tabSupplier` WHERE custom_vendor_code IS NOT NULL AND custom_vendor_code != ''",
        as_dict=True
    )
    existing_vendors = {normalize_lookup(r.custom_vendor_code) for r in vendor_rows}

    # 4. All brand names (covers brand soft check)
    existing_brands = set(
        normalize_lookup(r[0]) for r in smriti.db.sql("SELECT name FROM `tabBrand`")
    )

    # 5. Which attribute DocTypes exist on this install (avoids 7×N DocType exists() checks)
    attr_doctype_names = [
        "SMRITI Gender", "SMRITI Purchase Class", "SMRITI Merchandise Category",
        "SMRITI Sub Category", "SMRITI Upper Material", "SMRITI Outsole", "SMRITI Heel Type"
    ]
    existing_doctypes = set(
        r[0] for r in smriti.db.sql(
            f"SELECT name FROM `tabDocType` WHERE name IN ({','.join(['%s']*len(attr_doctype_names))})",
            attr_doctype_names
        )
    )

    return {
        "barcode_to_item":   barcode_to_item,
        "existing_items":    existing_items,
        "existing_vendors":  existing_vendors,
        "existing_brands":   existing_brands,
        "existing_doctypes": existing_doctypes,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_import_template_headers():
    """Returns the ordered list of expected column headers for the CSV template."""
    return TEMPLATE_HEADERS


@frappe.whitelist()
def get_hsn_gst_rate(hsn_code):
    """Whitelisted wrapper to fetch GST percentage from an HSN code."""
    from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
    rate = get_gst_rate_from_hsn(hsn_code)
    return rate if rate is not None else 0


@frappe.whitelist()
def validate_import_rows(rows_json):
    """
    Dry-run validation of pasted/uploaded rows.
    Returns per-row status: 'valid', 'warning', or 'error' with message lists.
    Duplicate barcodes (within sheet OR already in system) are HARD ERRORS.
    """
    rows = frappe.parse_json(rows_json)
    results = []

    companies = smriti.db.get_list("Company", limit=1)
    company = (
        frappe.defaults.get_user_default("company") or
        (companies[0].name if companies else None)
    )

    _clear_hsn_cache()

    # Pre-load all lookup sets in 5 bulk queries — eliminates N+1 per-row DB hits
    _cache = _build_import_lookup_cache()
    _barcode_to_item   = _cache["barcode_to_item"]
    _existing_items    = _cache["existing_items"]
    _existing_vendors  = _cache["existing_vendors"]
    _existing_brands   = _cache["existing_brands"]
    _existing_doctypes = _cache["existing_doctypes"]

    # Track barcodes seen within the sheet itself (for intra-sheet duplicate check)
    seen_barcodes = {}

    for idx, row in enumerate(rows):
        errors = []
        warnings = []

        # ── Required field checks ──────────────────────────────────────────
        for col in REQUIRED_COLS:
            val_cleaned = _clean_str(row.get(col, ""))
            if not val_cleaned:
                errors.append(f"'{col}' is required")

        barcode = _clean_str(row.get("BARCODE NO", ""))
        # Guard: Excel blank cells arrive as 'nan' or 'None' or '0'
        if barcode.lower() in ("", "0"):
            barcode = ""

        # Centralized barcode validation (VAL-ITEM-002)
        if barcode:
            is_valid, err_msg = validate_barcode(barcode, raise_exception=False)
            if not is_valid:
                errors.append(err_msg)

        # Compute variant_code early to allow re-import of same barcode on same item
        _style  = _clean_str(row.get("PRODUCT STYLE CODE", ""))
        _color  = _clean_str(row.get("COLOR", ""))
        _size   = _clean_str(row.get("SIZE", ""))
        variant_code_early = f"{_style}-{_color}-{_size}" if _style and _color and _size else ""

        # ── Intra-sheet duplicate barcode → HARD ERROR ─────────────────────
        if barcode:
            if barcode in seen_barcodes:
                errors.append(
                    f"Duplicate barcode in sheet — same barcode at row {seen_barcodes[barcode] + 1}"
                )
            else:
                seen_barcodes[barcode] = idx

                # ── System duplicate barcode check (uses pre-loaded cache) ──
                existing_item = _barcode_to_item.get(barcode)
                # Allow re-import: barcode already belongs to THIS exact variant → OK
                if existing_item and existing_item != variant_code_early:
                    errors.append(
                        f"Barcode '{barcode}' already assigned to item '{existing_item}' — barcodes must be unique"
                    )
                elif not existing_item:
                    # Check barcode collision with item_code namespace (uses pre-loaded set)
                    collides_with_item = barcode in _existing_items
                    if collides_with_item and barcode != variant_code_early:
                        errors.append(
                            f"Barcode '{barcode}' collides with existing item_code — cannot use item_code as barcode"
                        )

        # ── GST % validation ───────────────────────────────────────────────
        hsn_raw = row.get("HSN CODE", "")
        hsn_code = None
        if hsn_raw:
            try:
                hsn_code = _resolve_hsn_code_cached(hsn_raw)
            except Exception as e:
                # Capture HSN validation exceptions cleanly in human-readable format
                err_msg = str(e)
                if isinstance(e, frappe.ValidationError) and hasattr(e, "args") and e.args:
                    err_msg = e.args[0]
                errors.append(f"Invalid HSN Code: {err_msg}")
        
        from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
        hsn_derived_rate = get_gst_rate_from_hsn(hsn_code, company) if hsn_code else None
        
        if hsn_derived_rate is not None:
            gst_val = hsn_derived_rate
        else:
            gst_raw = _clean_str(row.get("PRODUCT TAX", "0"))
            try:
                gst_val = int(float(gst_raw or "0"))
            except ValueError:
                errors.append(f"GST '{gst_raw}' is not a number")
                gst_val = None
                
        if gst_val is not None and gst_val not in VALID_GST:
            errors.append(f"GST '{gst_val}%' is not valid — allowed: 0, 5, 12, 18, 28")

        # ── Vendor / Supplier hard check (uses pre-loaded cache) ───────────
        vendor = _clean_str(row.get("VENDOR CODE", ""))
        if vendor:
            vendor_norm = normalize_lookup(vendor)
            if vendor_norm not in ("", "NA", "N/A", "NONE", "NULL", "NAN", "DV"):
                if vendor_norm not in _existing_vendors:
                    errors.append(
                        f"Vendor Code '{vendor}' not found in Supplier Master. "
                        f"Please create a Supplier with Vendor Code '{vendor}' before importing items."
                    )

        # ── Brand soft check (uses pre-loaded cache) ───────────────────────
        brand = _clean_str(row.get("BRAND NAME", ""))
        if brand and normalize_lookup(brand) not in _existing_brands:
            warnings.append(f"Brand '{brand}' not found — will be auto-created")

        # ── Attribute Soft Checks (uses pre-loaded DocType set) ───────────
        attr_checks = [
            ("GENDER", "SMRITI Gender", "Gender"),
            ("PURCHASE CLASS", "SMRITI Purchase Class", "Purchase Class"),
            ("MERCHANDISE CATEGORY", "SMRITI Merchandise Category", "Merchandise Category"),
            ("Sub category", "SMRITI Sub Category", "Sub Category"),
            ("UPPER MATERIAL", "SMRITI Upper Material", "Upper Material"),
            ("OUTSOLE", "SMRITI Outsole", "Outsole"),
            ("HEELS", "SMRITI Heel Type", "Heel Type")
        ]
        for row_key, doctype_name, label in attr_checks:
            val = _clean_str(row.get(row_key, ""))
            if val and doctype_name in _existing_doctypes:
                # Single per-value lookup is still needed here — we can't pre-load all values
                # for every custom attribute, but DocType existence check is now cache-free
                try:
                    if not smriti.db.exists(doctype_name, val):
                        warnings.append(f"{label} '{val}' not found — will be auto-created")
                except Exception:
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:237: {sys.exc_info()[1]}")

        status = "error" if errors else ("warning" if warnings else "valid")
        results.append({
            "row_idx": idx,
            "status": status,
            "errors": errors,
            "warnings": warnings
        })

    return results


@frappe.whitelist()
def import_item_master(rows_json):
    """
    Creates ERPNext Items (Template + Variants) from the validated row list.
    Duplicate barcodes are hard-rejected (should already be filtered by frontend).
    Returns a summary dict: created, skipped, failed.
    """
    check_store_manager_role()
    rows = frappe.parse_json(rows_json)

    # Clear per-batch HSN resolution cache for this import run
    _clear_hsn_cache()

    # Ensure hardcoded standard UOM 'Nos' exists in the database
    _ensure_uom("Nos")

    created = 0
    skipped_duplicates = []
    failed = []

    companies = smriti.db.get_list("Company", limit=1)
    company = (
        frappe.defaults.get_user_default("company") or
        (companies[0].name if companies else None)
    )

    # Collect barcodes already seen in this batch to prevent intra-batch duplication
    batch_barcodes = set()

    for idx, row in enumerate(rows):
        try:
            # ── Parse row ─────────────────────────────────────────────────
            barcode         = _clean_str(row.get("BARCODE NO", ""))
            # Guard: Excel blank cells come through as 'nan' or 'None' or '0'
            if barcode.lower() in ("", "0"):
                barcode = ""
            if barcode:
                validate_barcode(barcode, raise_exception=True)
            style_code      = _clean_str(row.get("PRODUCT STYLE CODE", ""))
            item_name       = _clean_str(row.get("ITEM DESCRIPTION", ""))
            color           = _clean_str(row.get("COLOR", ""))
            size            = _clean_str(row.get("SIZE", ""))
            brand           = _clean_str(row.get("BRAND NAME", ""))
            mrp             = flt(row.get("PLANNED MRP", 0))
            cost            = flt(row.get("COST PRICE", 0))
            
            hsn_code        = _clean_str(row.get("HSN CODE", ""))
            resolved_hsn    = _resolve_hsn_code_cached(hsn_code) if hsn_code else None
            
            # Derive GST percentage (HSN-first)
            from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
            hsn_derived_rate = get_gst_rate_from_hsn(resolved_hsn, company) if resolved_hsn else None
            if hsn_derived_rate is not None:
                gst_pct = str(hsn_derived_rate)
            else:
                gst_raw = _clean_str(row.get("PRODUCT TAX", "0"))
                gst_pct = str(int(float(gst_raw or "0"))).strip() if gst_raw else "0"
            
            image_link      = _clean_str(row.get("IMAGE LINK", ""))
            item_group      = _clean_str(row.get("DEPARTMENT", "Products")) or "Products"
            vendor_code     = _clean_str(row.get("VENDOR CODE", ""))
            gender          = _clean_str(row.get("GENDER", "")).upper()
            upper_material  = _clean_str(row.get("UPPER MATERIAL", ""))
            outsole         = _clean_str(row.get("OUTSOLE", ""))
            heel_type       = _clean_str(row.get("HEELS", ""))
            purchase_class  = _clean_str(row.get("PURCHASE CLASS", ""))
            merch_cat       = _clean_str(row.get("MERCHANDISE CATEGORY", ""))
            sub_cat         = _clean_str(row.get("Sub category", ""))
            tax_group       = _clean_str(row.get("Product Tax Group", ""))

            # ── Vendor Code Validation ─────────────────────────────────────
            _validate_vendor_code(vendor_code)

            # ── Hard duplicate barcode check ───────────────────────────────
            variant_code_early = f"{style_code}-{color}-{size}" if style_code and color and size else ""

            if not barcode:
                # auto-generate EAN-13 barcodes with collision retries (up to 5 attempts)
                max_retries = 5
                for attempt in range(max_retries):
                    generated = generate_ean13_barcode()
                    duplicate = smriti.db.get("Item Barcode", {"barcode": generated}, "parent")
                    collides = smriti.db.exists("Item", generated) and generated != variant_code_early
                    if not duplicate and not collides:
                        barcode = generated
                        break
                else:
                    frappe.throw(
                        _("Could not generate a unique barcode for {0} after 5 attempts.").format(variant_code_early),
                        frappe.ValidationError
                    )

            if barcode:
                if barcode in batch_barcodes:
                    skipped_duplicates.append({
                        "row": idx + 1,
                        "barcode": barcode,
                        "reason": "Duplicate barcode within import batch"
                    })
                    continue

                existing_on_system = smriti.db.get(
                    "Item Barcode", {"barcode": barcode}, "parent"
                )
                # Allow re-import: if barcode already belongs to THIS exact variant, it's fine
                if existing_on_system and existing_on_system != variant_code_early:
                    skipped_duplicates.append({
                        "row": idx + 1,
                        "barcode": barcode,
                        "reason": f"Barcode '{barcode}' already assigned to item '{existing_on_system}'"
                    })
                    continue

                # Prevent barcode from colliding with a DIFFERENT item's item_code
                collides_with_item = smriti.db.exists("Item", barcode)
                if collides_with_item and barcode != variant_code_early:
                    skipped_duplicates.append({
                        "row": idx + 1,
                        "barcode": barcode,
                        "reason": f"Barcode '{barcode}' collides with existing item_code"
                    })
                    continue

                batch_barcodes.add(barcode)

            # ── Ensure Item Group exists ───────────────────────────────────
            if not smriti.db.exists("Item Group", item_group):
                item_group = "Products"
            # Also guard the fallback — "Products" may not exist either
            if not smriti.db.exists("Item Group", item_group):
                existing_group = smriti.db.get_list("Item Group", pluck="name", limit=1)
                if existing_group:
                    item_group = existing_group[0]
                else:
                    ig = smriti.documents.new("Item Group")
                    ig.item_group_name = "Products"
                    ig.is_group = 0
                    # reviewed-ignore-permissions: excel import of products, gated by SMRITI Store Manager or System Manager roles
                    ig.insert(ignore_permissions=True)
                    item_group = "Products"

            # ── Ensure Color / Size attribute values exist ─────────────────
            _ensure_item_attribute("Color")
            _ensure_item_attribute("Size")
            _ensure_attribute_value("Color", color)
            _ensure_attribute_value("Size", str(size))

            # ── Get or create Template Item ────────────────────────────────
            _get_or_create_template(
                style_code=style_code,
                item_name=item_name,
                item_group=item_group,
                brand=brand,
                mrp=mrp,
                cost=cost,
                gst_pct=gst_pct,
                hsn_code=hsn_code,
                image_link=image_link,
                gender=gender,
                upper_material=upper_material,
                outsole=outsole,
                heel_type=heel_type,
                purchase_class=purchase_class,
                merch_cat=merch_cat,
                sub_cat=sub_cat,
                tax_group=tax_group,
                vendor_code=vendor_code,
                company=company
            )

            # ── Create Variant ─────────────────────────────────────────────
            variant_code = f"{style_code}-{color}-{size}"
            if not smriti.db.exists("Item", variant_code):
                variant = smriti.documents.new("Item")
                variant.item_code    = variant_code
                variant.item_name    = f"{item_name} ({color} / {size})"
                variant.variant_of   = style_code
                variant.item_group   = item_group
                variant.stock_uom    = "Nos"
                variant.is_stock_item = 1
                _safe_set(variant, "custom_is_retail_item", 1)
                _safe_set(variant, "custom_mrp", mrp)
                _safe_set(variant, "custom_gst_percentage", gst_pct)
                if image_link:
                    variant.image = image_link
                resolved_hsn = _resolve_hsn_code_cached(hsn_code)
                if resolved_hsn:
                    _ensure_hsn_code(resolved_hsn)
                    variant.gst_hsn_code = resolved_hsn
                    _safe_set(variant, "gn_hsn_code", resolved_hsn)

                variant.append("attributes", {"attribute": "Color", "attribute_value": color})
                variant.append("attributes", {"attribute": "Size",  "attribute_value": str(size)})

                _attach_tax_template(variant, tax_group, gst_pct, company)
                # reviewed-ignore-permissions: excel import of products, gated by SMRITI Store Manager or System Manager roles
                variant.insert(ignore_permissions=True)
            else:
                variant = smriti.documents.get("Item", variant_code)

            # ── Attach barcode to variant (enforcing single primary, preserving secondary barcodes) ──
            var_doc = smriti.documents.get("Item", variant_code)
            _safe_set(var_doc, "custom_style_code", style_code)

            if barcode:
                # Separate existing barcodes: keep secondaries, replace primary
                # Use int() comparison so None/0/False all treated as non-primary safely
                secondaries = [
                    b for b in var_doc.barcodes
                    if not int(b.get("custom_is_primary") or 0)
                ]

                var_doc.barcodes = []
                var_doc.append("barcodes", {
                    "barcode": barcode,
                    "uom": "Nos",
                    "custom_is_primary": 1
                })
                for sec in secondaries:
                    if sec.barcode and sec.barcode != barcode:
                        var_doc.append("barcodes", {
                            "barcode": sec.barcode,
                            "uom": sec.uom or "Nos",
                            "custom_is_primary": 0
                        })

                # Parse and append any new secondary barcodes from sheet row
                secondary_str = str(row.get("SECONDARY BARCODES", "") or "").strip()
                if secondary_str and secondary_str.lower() not in ("nan", "none", "null"):
                    sec_barcodes = [b.strip() for b in secondary_str.split(",") if b.strip()]
                    current_barcodes = {b.barcode for b in var_doc.barcodes}
                    for sb in sec_barcodes:
                        if sb and sb not in current_barcodes:
                            dup_parent = smriti.db.get(
                                "Item Barcode",
                                {"barcode": sb, "parent": ["!=", variant_code]},
                                "parent"
                            )
                            sb_collides = smriti.db.exists("Item", sb) and sb != variant_code
                            if not dup_parent and not sb_collides:
                                var_doc.append("barcodes", {
                                    "barcode": sb,
                                    "uom": "Nos",
                                    "custom_is_primary": 0
                                })

            # reviewed-ignore-permissions: excel import of products, gated by SMRITI Store Manager or System Manager roles
            var_doc.save(ignore_permissions=True)

            # ── Create prices (Standard Selling = MRP, MRP list = MRP) ─────
            _upsert_item_price(variant_code, "Standard Selling", mrp)
            _upsert_item_price(variant_code, "MRP", mrp)

            created += 1

        except Exception:
            failed.append({
                "row": idx + 1,
                "barcode": row.get("BARCODE NO", ""),
                "style_code": row.get("PRODUCT STYLE CODE", ""),
                "error": frappe.get_traceback()
            })
            smriti.errors.log_error(
                title=f"SMRITI Item Import — Row {idx + 1}",
                message=frappe.get_traceback()
            )

    smriti.db.commit()

    return {
        "created": created,
        "duplicate_errors": skipped_duplicates,
        "failed": failed
    }


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _validate_vendor_code(vendor_code):
    if not vendor_code:
        return
    vendor_code_clean = str(vendor_code).strip().upper()
    if vendor_code_clean in ("", "NA", "N/A", "NONE", "NULL", "NAN", "DV"):
        return  # skip validation for empty/placeholder values
    
    vendor_code = str(vendor_code).strip()
    
    exists = smriti.db.exists(
        "Supplier",
        {"custom_vendor_code": vendor_code}
    )
    if not exists:
        frappe.throw(
            f"Vendor Code '{vendor_code}' not found in Supplier Master. "
            f"Please create a Supplier with Vendor Code '{vendor_code}' before importing items.",
            title="Vendor Code Not Found"
        )


def _clean_str(val):
    """Clean a string value from import: strip whitespace, remove wrapping/stray quotes, and handle nulls."""
    s = str(val or "").strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1].strip()
    if s in ('"', 'nan', 'None', 'none', 'null', 'Null'):
        return ""
    return s


def _safe_set(doc, fieldname, value):
    """Set a field on a Frappe doc, silently skipping if the field doesn't exist.
    Prevents AttributeError when custom fields are missing on fresh installs.
    """
    try:
        doc.set(fieldname, value)
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:545: {sys.exc_info()[1]}")


def _ensure_uom(uom_name):
    """Creates a UOM record if it doesn't exist."""
    if not uom_name:
        return
    uom_clean = str(uom_name).strip()
    if not uom_clean:
        return
    try:
        if not smriti.db.exists("UOM", uom_clean):
            doc = smriti.documents.new("UOM")
            doc.uom_name = uom_clean
            doc.insert(ignore_permissions=True)
            smriti.db.commit()
    except Exception as e:
        smriti.errors.log_error(f"Failed to auto-create UOM {uom_clean}: {str(e)}")


def _ensure_hsn_code(hsn_code):
    """Create GST HSN Code record if it doesn't exist yet."""
    if not hsn_code:
        return
    hsn_str = str(hsn_code).strip()
    if not hsn_str:
        return
    try:
        if not smriti.db.exists("GST HSN Code", hsn_str):
            hsn_doc = smriti.documents.new("GST HSN Code")
            hsn_doc.name = hsn_str
            hsn_doc.hsn_code = hsn_str
            hsn_doc.description = "Auto-created HSN"
            hsn_doc.insert(ignore_permissions=True)
            smriti.db.commit()
    except Exception as e:
        smriti.errors.log_error(f"HSN auto-create failed for {hsn_str}: {e}")


def _resolve_hsn_code(hsn_code):
    """Clean, validate length against GST settings, and determine if it can be safely set.
    If the HSN code is empty or invalid, reads the default from SMRITI Settings.default_hsn_code.
    Returns None if no valid HSN can be resolved (caller must handle this — never silently
    assign a domain-specific fallback like '641590' to a non-footwear tenant).
    Also ensures the resolved HSN code is created in the database.

    Architecture: C-2 remediation (hardcoding audit 2026-07-03)
    """
    import re
    # Extract only digits from the input HSN code
    hsn_digits = ""
    if hsn_code:
        hsn_digits = "".join(re.findall(r"\d+", str(hsn_code)))

    # If empty or non-numeric — try configured default, never a domain-specific literal
    if not hsn_digits:
        configured_default = smriti.db.get_single("SMRITI Settings", "default_hsn_code") or ""
        if not configured_default:
            frappe.logger().warning(
                "SMRITI _resolve_hsn_code: HSN code is missing and no default_hsn_code is "
                "configured in SMRITI Settings. HSN will not be set for this item."
            )
            return None
        hsn_digits = "".join(re.findall(r"\d+", str(configured_default)))
        if not hsn_digits:
            frappe.logger().warning(
                f"SMRITI _resolve_hsn_code: default_hsn_code '{configured_default}' in SMRITI Settings "
                "contains no numeric digits. HSN will not be set for this item."
            )
            return None

    # Format length according to valid HSN length settings or default to (6, 8)
    try:
        from india_compliance.gst_india.utils import get_hsn_settings
        validate_enabled, valid_lengths = get_hsn_settings()
    except Exception:
        validate_enabled = True
        valid_lengths = (6, 8)

    if validate_enabled:
        length = len(hsn_digits)
        if length not in valid_lengths:
            frappe.throw(
                _("HSN Code '{0}' has invalid length {1}. Valid HSN lengths are {2}.").format(hsn_code, length, ", ".join(map(str, valid_lengths))),
                title=_("Invalid HSN Code")
            )
    
    # Auto-create in database if missing
    _ensure_hsn_code(hsn_digits)

    return hsn_digits


# Per-batch HSN resolution cache — populated by _resolve_hsn_code_cached(), cleared at
# the start of each import/create call to avoid stale data across separate requests.
_hsn_code_cache: dict = {}


def _resolve_hsn_code_cached(hsn_code):
    """Cached wrapper around _resolve_hsn_code().
    Avoids repeated DB round-trips and regex work for the same HSN value within a single
    import batch. The cache is keyed on the raw input string and is a module-level dict
    cleared at the start of each top-level import function.
    """
    global _hsn_code_cache
    key = str(hsn_code or "")
    if key not in _hsn_code_cache:
        _hsn_code_cache[key] = _resolve_hsn_code(hsn_code)
    return _hsn_code_cache[key]


def _clear_hsn_cache():
    """Clears the per-batch HSN resolution cache. Call at the start of each import function."""
    global _hsn_code_cache
    _hsn_code_cache = {}


def _ensure_master_value(doctype_name, value):
    """Checks if a value exists in a Master DocType, and inserts it if not.
    Silently skips if the DocType itself is not installed (fresh installs).
    """
    val_clean = str(value or "").strip()
    if not val_clean:
        return ""
    try:
        # Guard: DocType may not exist on fresh installations
        if not smriti.db.exists("DocType", doctype_name):
            return val_clean
        if not smriti.db.exists(doctype_name, val_clean):
            doc = smriti.documents.new(doctype_name)
            # Try common field names used in SMRITI master doctypes
            for field in ("attribute_value", "name", doctype_name.lower().replace(" ", "_")):
                try:
                    doc.set(field, val_clean)
                    break
                except Exception:
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:666: {sys.exc_info()[1]}")
            doc.insert(ignore_permissions=True)
            smriti.db.commit()
    except Exception as e:
        smriti.errors.log_error(f"Failed to auto-create {val_clean} in {doctype_name}: {str(e)}")
    return val_clean


def _get_or_create_template(style_code, item_name, item_group, brand, mrp, cost,
                             gst_pct, hsn_code, image_link, gender, upper_material,
                             outsole, heel_type, purchase_class, merch_cat, sub_cat,
                             tax_group, vendor_code, company):
    if smriti.db.exists("Item", style_code):
        item = smriti.documents.get("Item", style_code)
        if not item.get("custom_style_code"):
            _safe_set(item, "custom_style_code", style_code)
            item.save(ignore_permissions=True)
    else:
        # Auto-create brand if missing
        if brand and not smriti.db.exists("Brand", brand):
            b = smriti.documents.new("Brand")
            b.brand = brand
            b.insert(ignore_permissions=True)

        # Ensure Item Group exists
        if not item_group or not smriti.db.exists("Item Group", item_group):
            item_group = "Products"
        if not smriti.db.exists("Item Group", item_group):
            existing_group = smriti.db.get_list("Item Group", pluck="name", limit=1)
            if existing_group:
                item_group = existing_group[0]
            else:
                ig = smriti.documents.new("Item Group")
                ig.item_group_name = "Products"
                ig.is_group = 0
                ig.insert(ignore_permissions=True)
                item_group = "Products"


        item = smriti.documents.new("Item")
        item.item_code              = style_code
        item.item_name              = item_name
        item.item_group             = item_group
        item.stock_uom              = "Nos"
        item.is_stock_item          = 1
        item.has_variants           = 1

        # Core fields — safe even on fresh installs
        _safe_set(item, "custom_is_retail_item", 1)
        _safe_set(item, "custom_mrp", mrp)
        _safe_set(item, "valuation_rate", cost)
        _safe_set(item, "custom_gst_percentage", gst_pct)
        _safe_set(item, "custom_style_code", style_code)

        # Custom SMRITI classification fields — silently skip if field missing
        _safe_set(item, "custom_gender",               _ensure_master_value("SMRITI Gender", gender))
        _safe_set(item, "custom_upper_material",        _ensure_master_value("SMRITI Upper Material", upper_material))
        _safe_set(item, "custom_outsole",               _ensure_master_value("SMRITI Outsole", outsole))
        _safe_set(item, "custom_heel_type",             _ensure_master_value("SMRITI Heel Type", heel_type))
        _safe_set(item, "custom_purchase_class",        _ensure_master_value("SMRITI Purchase Class", purchase_class))
        _safe_set(item, "custom_merchandise_category",  _ensure_master_value("SMRITI Merchandise Category", merch_cat))
        _safe_set(item, "custom_sub_category",          _ensure_master_value("SMRITI Sub Category", sub_cat))

        if brand:
            item.brand = brand
        resolved_hsn = _resolve_hsn_code_cached(hsn_code)
        if resolved_hsn:
            _ensure_hsn_code(resolved_hsn)
            item.gst_hsn_code = resolved_hsn
            _safe_set(item, "gn_hsn_code", resolved_hsn)
        if image_link:
            item.image = image_link

        # Variant attribute definitions on template
        _ensure_item_attribute("Color")
        _ensure_item_attribute("Size")
        item.append("attributes", {"attribute": "Color"})
        item.append("attributes", {"attribute": "Size"})

        _attach_tax_template(item, tax_group, gst_pct, company)
        item.insert(ignore_permissions=True)

    # Always link/sync supplier if vendor_code is present and matches a Supplier
    if vendor_code:
        supplier_name = None
        vendor_code_clean = str(vendor_code).strip()
        vendor_code_clean_upper = vendor_code_clean.upper()
        if vendor_code_clean_upper not in ("", "NA", "N/A", "NONE", "NULL", "NAN", "DV"):
            supplier_name = smriti.db.get(
                "Supplier",
                {"custom_vendor_code": vendor_code_clean},
                "name"
            )
        if supplier_name:
            if not any(d.supplier == supplier_name for d in item.supplier_items):
                item.append("supplier_items", {
                    "supplier": supplier_name,
                    "supplier_part_no": vendor_code
                })
                item.save(ignore_permissions=True)

    return item


def _ensure_item_attribute(attribute_name):
    """Create Item Attribute doctype record if it doesn't exist yet."""
    if not smriti.db.exists("Item Attribute", attribute_name):
        attr = smriti.documents.new("Item Attribute")
        attr.attribute_name = attribute_name
        attr.insert(ignore_permissions=True)



def _ensure_attribute_value(attribute, value):
    """Add a new value to an Item Attribute if it is not already present."""
    if not value:
        return
    exists = smriti.db.get(
        "Item Attribute Value",
        {"parent": attribute, "attribute_value": value},
        "name"
    )
    if not exists:
        attr_doc = smriti.documents.get("Item Attribute", attribute)
        # Build a unique abbr — use full value shortened, with collision avoidance
        base_abbr = value[:6].upper().replace(" ", "").replace("-", "")
        abbr = base_abbr
        counter = 1
        existing_abbrs = {v.abbr for v in attr_doc.item_attribute_values}
        while abbr in existing_abbrs:
            abbr = f"{base_abbr[:4]}{counter}"
            counter += 1
        attr_doc.append("item_attribute_values", {
            "attribute_value": value,
            "abbr": abbr
        })
        attr_doc.save(ignore_permissions=True)


def _attach_tax_template(item, tax_group, gst_pct, company):
    """Resolve and attach an Item Tax Template."""
    if not company:
        return
    template_name = None
    if tax_group:
        template_name = smriti.db.get(
            "Item Tax Template",
            {"name": ["like", f"%{tax_group}%"], "company": company},
            "name"
        )
    if not template_name and gst_pct:
        template_name = smriti.db.get(
            "Item Tax Template",
            {"name": ["like", f"%{gst_pct}%"], "company": company},
            "name"
        )
    if template_name:
        item.append("taxes", {"item_tax_template": template_name, "tax_category": ""})


def _upsert_item_price(item_code, price_list, rate):
    """Create price list entry; update if already exists."""
    if not rate:
        return
    if not smriti.db.exists("Price List", price_list):
        pl = smriti.documents.new("Price List")
        pl.price_list_name = price_list
        pl.enabled  = 1
        pl.selling  = 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    existing = smriti.db.get(
        "Item Price",
        {"item_code": item_code, "price_list": price_list},
        "name"
    )
    if existing:
        smriti.db.set_value("Item Price", existing, "price_list_rate", flt(rate))
    else:
        ip = smriti.documents.new("Item Price")
        ip.item_code       = item_code
        ip.price_list      = price_list
        ip.price_list_rate = flt(rate)
        ip.currency        = "INR"
        ip.uom             = "Nos"
        ip.insert(ignore_permissions=True)


def check_store_manager_role():
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(frappe._("Restricted: Requires Store Manager or System Manager role."), frappe.PermissionError)


@frappe.whitelist()
def generate_ean13_barcode():
    """
    Generates a unique EAN-13 barcode with valid check digit.
    Uses an iterative collision-avoidance loop (max 100 attempts).
    Raises frappe.ValidationError if a unique barcode cannot be found.
    """
    import random
    # C-08 FIX: Replace unbounded recursion with an iterative loop.
    # The old recursive version had no stack depth limit:
    # in a busy system with many barcodes, repeated collisions could overflow
    # Python's default call stack (1000 frames) and crash the gunicorn worker.
    max_attempts = 100
    for attempt in range(max_attempts):
        body = f"23{random.randint(1000000000, 9999999999)}"
        odds  = sum(int(body[i]) for i in range(0, 12, 2))
        evens = sum(int(body[i]) for i in range(1, 12, 2))
        total = odds + (evens * 3)
        check_digit = (10 - (total % 10)) % 10
        barcode = f"{body}{check_digit}"

        # Check both Item Barcode table and Item master (to avoid item_code collisions)
        if (not smriti.db.exists("Item Barcode", {"barcode": barcode})
                and not smriti.db.exists("Item", barcode)):
            return barcode

    frappe.throw(
        _("Could not generate a unique EAN-13 barcode after {0} attempts. "
          "Please contact system administrator.").format(max_attempts)
    )


@frappe.whitelist()
def get_style_details(article_no):
    if not smriti.db.exists("Item", article_no):
        return {"exists": False}
        
    doc = smriti.documents.get("Item", article_no)
    variants = smriti.db.get_list("Item", filters={"variant_of": article_no}, fields=["name", "item_name", "custom_mrp", "valuation_rate"])
    
    sizes = []
    color_val = ""

    if variants:
        variant_names = [v.name for v in variants]

        # Bulk fetch all Size + Color attributes for all variants (1 query instead of 2×N)
        all_attrs = smriti.db.get_list(
            "Item Variant Attribute",
            filters={
                "parent": ["in", variant_names],
                "attribute": ["in", ["Size", "Color"]]
            },
            fields=["parent", "attribute", "attribute_value"]
        )
        attr_map = {}  # {variant_name: {"Size": val, "Color": val}}
        for a in all_attrs:
            attr_map.setdefault(a.parent, {})[a.attribute] = a.attribute_value

        # Bulk fetch primary barcodes for all variants (1 query instead of N)
        all_barcodes = smriti.db.get_list(
            "Item Barcode",
            filters={"parent": ["in", variant_names]},
            fields=["parent", "barcode"],
            order_by="idx asc"  # first barcode = primary
        )
        barcode_map = {}
        for b in all_barcodes:
            if b.parent not in barcode_map:  # first occurrence = primary
                barcode_map[b.parent] = b.barcode

        for var in variants:
            attrs = attr_map.get(var.name, {})
            sizes.append({
                "variant_code": var.name,
                "size":         attrs.get("Size", ""),
                "barcode":      barcode_map.get(var.name, ""),
                "mrp":          var.custom_mrp,
                "cost":         var.valuation_rate,
            })

        # Collect all unique colors across all variants.
        # Most footwear styles are single-color (one style = one color family),
        # but multi-color styles (e.g. combo packs) are handled by joining.
        unique_colors = list(dict.fromkeys(
            attr_map.get(v.name, {}).get("Color", "")
            for v in variants
            if attr_map.get(v.name, {}).get("Color", "")
        ))
        color_val = unique_colors[0] if len(unique_colors) == 1 else ", ".join(unique_colors)


    return {
        "exists": True,
        "description": doc.item_name,
        "brand": doc.brand or "",
        "item_group": doc.item_group,
        "mrp": doc.custom_mrp or 0,
        "cost_price": doc.valuation_rate or 0,
        "gst_percentage": doc.custom_gst_percentage or "0",
        "hsn_code": doc.gst_hsn_code or "",
        "gender": doc.custom_gender or "",
        "purchase_class": doc.custom_purchase_class or "",
        "merchandise_category": doc.custom_merchandise_category or "",
        "sub_category": doc.custom_sub_category or "",
        "vendor_code": smriti.db.get("Item Supplier", {"parent": article_no}, "supplier_part_no") or "",
        "color": color_val or "UNKNOWN",
        "sizes": sizes
    }


@frappe.whitelist()
def create_style_with_variants(base_details, sizes_config):
    check_store_manager_role()
    
    # Clear per-batch HSN resolution cache for this run
    _clear_hsn_cache()
    
    # Ensure hardcoded standard UOM 'Nos' exists in the database
    _ensure_uom("Nos")
    
    bd = frappe.parse_json(base_details)
    sc = frappe.parse_json(sizes_config)
    
    style_code = bd.get("article_no").strip()
    item_name = bd.get("description").strip()
    item_group = bd.get("item_group", "Products")
    brand = bd.get("brand")
    mrp = flt(bd.get("mrp", 0))
    cost = flt(bd.get("cost_price", 0))
    hsn_code = bd.get("hsn_code")
    
    # Resolve company first — needed for HSN GST rate derivation below
    company = frappe.defaults.get_user_default("company") or smriti.db.get_list("Company", limit=1)[0].name

    # Derive GST percentage (HSN-first)
    resolved_hsn = _resolve_hsn_code_cached(hsn_code) if hsn_code else None
    from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
    hsn_derived_rate = get_gst_rate_from_hsn(resolved_hsn, company) if resolved_hsn else None
    if hsn_derived_rate is not None:
        gst_pct = str(hsn_derived_rate)
    else:
        gst_pct = str(bd.get("gst_percentage", "0")).strip()
        
    gender = bd.get("gender")
    purchase_class = bd.get("purchase_class")
    merch_cat = bd.get("merchandise_category")
    sub_cat = bd.get("sub_category")
    tax_group = bd.get("product_tax_group")
    vendor_code = bd.get("vendor_code")
    _validate_vendor_code(vendor_code)
    color = bd.get("color", "UNKNOWN").strip()
    
    # 1. Get or create style template parent item
    template = _get_or_create_template(
        style_code=style_code,
        item_name=item_name,
        item_group=item_group,
        brand=brand,
        mrp=mrp,
        cost=cost,
        gst_pct=gst_pct,
        hsn_code=hsn_code,
        image_link="",
        gender=gender,
        upper_material="",
        outsole="",
        heel_type="",
        purchase_class=purchase_class,
        merch_cat=merch_cat,
        sub_cat=sub_cat,
        tax_group=tax_group,
        vendor_code=vendor_code,
        company=company
    )
    
    # Update base fields if template already existed
    if template.item_name != item_name or flt(template.custom_mrp) != mrp or flt(template.valuation_rate) != cost or template.custom_gst_percentage != gst_pct:
        template.item_name = item_name
        _safe_set(template, "custom_mrp", mrp)
        _safe_set(template, "valuation_rate", cost)
        _safe_set(template, "custom_gst_percentage", gst_pct)
        if brand:
            template.brand = brand
        resolved_hsn = _resolve_hsn_code_cached(hsn_code)
        if resolved_hsn:
            _ensure_hsn_code(resolved_hsn)
            template.gst_hsn_code = resolved_hsn
        # reviewed-ignore-permissions: bulk variant creation, gated by SMRITI Store Manager or System Manager roles
        template.save(ignore_permissions=True)
        smriti.db.commit()

    created_count = 0
    updated_count = 0
    results = []

    # 2. Add / Update active sizes configuration
    for s in sc:
        size = str(s.get("size")).strip()
        active = s.get("active")
        barcode_mode = s.get("barcode_mode", "auto")
        manual_barcode = str(s.get("manual_barcode", "")).strip()
        
        variant_code = f"{style_code}-{color}-{size}"
        
        if not active:
            continue
            
        # Ensure standard attributes and values exist
        _ensure_item_attribute("Size")
        _ensure_attribute_value("Size", size)
        _ensure_item_attribute("Color")
        _ensure_attribute_value("Color", color)
        
        # Determine barcode (VAL-ITEM-002 and ARCH-ITEM-001)
        max_retries = 10
        barcode = None
        for attempt in range(max_retries):
            if barcode_mode == "manual":
                validate_barcode(manual_barcode, raise_exception=True)
                barcode = manual_barcode
            else:
                existing_barcode = smriti.db.get("Item Barcode", {"parent": variant_code, "custom_is_primary": 1}, "barcode")
                if existing_barcode:
                    barcode = existing_barcode
                else:
                    barcode = generate_ean13_barcode()
            
            # Check barcode uniqueness
            duplicate = smriti.db.get("Item Barcode", {"barcode": barcode, "parent": ["!=", variant_code]}, "parent")
            if duplicate:
                if barcode_mode == "manual":
                    frappe.throw(frappe._("Barcode '{0}' is already registered on item '{1}'!").format(barcode, duplicate))
                else:
                    continue  # generated barcode collided, try again
            
            if smriti.db.exists("Item", barcode) and barcode != variant_code:
                if barcode_mode == "manual":
                    frappe.throw(frappe._("Barcode '{0}' collides with an existing Item Code in the system!").format(barcode))
                else:
                    continue  # generated barcode collided, try again
            
            # Uniqueness checks passed
            break
        else:
            frappe.throw(frappe._("Could not generate a unique barcode for size {0} after 10 attempts.").format(size))
            
        # Create or update variant Item doc
        if not smriti.db.exists("Item", variant_code):
            var = smriti.documents.new("Item")
            var.item_code = variant_code
            var.item_name = f"{item_name} ({color} / {size})"
            var.variant_of = style_code
            var.item_group = template.item_group
            var.stock_uom = "Nos"
            var.is_stock_item = 1
            _safe_set(var, "custom_is_retail_item", 1)
            _safe_set(var, "custom_mrp", mrp)
            _safe_set(var, "custom_gst_percentage", gst_pct)
            resolved_hsn = _resolve_hsn_code_cached(hsn_code)
            if resolved_hsn:
                _ensure_hsn_code(resolved_hsn)
                var.gst_hsn_code = resolved_hsn
                _safe_set(var, "gn_hsn_code", resolved_hsn)
                
            var.append("attributes", {"attribute": "Color", "attribute_value": color})
            var.append("attributes", {"attribute": "Size", "attribute_value": size})
            
            _attach_tax_template(var, tax_group, gst_pct, company)
            # reviewed-ignore-permissions: bulk variant creation, gated by SMRITI Store Manager or System Manager roles
            var.insert(ignore_permissions=True)
            created_count += 1
        else:
            var = smriti.documents.get("Item", variant_code)
            var.item_name = f"{item_name} ({color} / {size})"
            _safe_set(var, "custom_mrp", mrp)
            _safe_set(var, "custom_gst_percentage", gst_pct)
            resolved_hsn = _resolve_hsn_code_cached(hsn_code)
            if resolved_hsn:
                _ensure_hsn_code(resolved_hsn)
                var.gst_hsn_code = resolved_hsn
                _safe_set(var, "gn_hsn_code", resolved_hsn)
            # reviewed-ignore-permissions: bulk variant creation, gated by SMRITI Store Manager or System Manager roles
            var.save(ignore_permissions=True)
            updated_count += 1
            
        # Force set barcode child table row (preserving secondary barcodes)
        var_doc = smriti.documents.get("Item", variant_code)
        secondaries = [b for b in var_doc.barcodes if not b.custom_is_primary]
        
        var_doc.barcodes = []
        var_doc.append("barcodes", {
            "barcode": barcode,
            "uom": "Nos",
            "custom_is_primary": 1
        })
        for sec in secondaries:
            if sec.barcode != barcode:
                var_doc.append("barcodes", {
                    "barcode": sec.barcode,
                    "uom": sec.uom or "Nos",
                    "custom_is_primary": 0
                })
        # reviewed-ignore-permissions: bulk variant creation, gated by SMRITI Store Manager or System Manager roles
        var_doc.save(ignore_permissions=True)
        
        # Standard Selling prices sync
        _upsert_item_price(variant_code, "Standard Selling", mrp)
        _upsert_item_price(variant_code, "MRP", mrp)
        
        results.append({
            "size": size,
            "variant_code": variant_code,
            "barcode": barcode
        })
        
    smriti.db.commit()
    
    return {
        "success": True,
        "created_count": created_count,
        "updated_count": updated_count,
        "variants": results,
        "message": frappe._("Successfully created {0} and updated {1} size variants!").format(created_count, updated_count)
    }


@frappe.whitelist()
def delete_size_variant(variant_code):
    check_store_manager_role()
    if not smriti.db.exists("Item", variant_code):
        return {"success": False, "message": "Variant not found"}
        
    smriti.db.delete("Item Barcode", {"parent": variant_code})
    smriti.db.delete("Item Price", {"item_code": variant_code})
    frappe.delete_doc("Item", variant_code, ignore_missing=True, force=True)
    smriti.db.commit()
    return {"success": True, "message": frappe._("Size variant {0} deleted successfully.").format(variant_code)}


@frappe.whitelist()
def delete_style_and_variants(style_code):
    """Delete style template + all variants + barcodes + prices."""
    check_store_manager_role()

    if not smriti.db.exists("Item", style_code):
        frappe.throw(_("Item '{0}' not found").format(style_code))

    # Find all variants of this style
    variants = smriti.db.get_list("Item",
        filters={"variant_of": style_code},
        pluck="name"
    )

    deleted_variants = 0
    for variant in variants:
        # Delete prices for this variant
        smriti.db.delete("Item Price", {"item_code": variant})
        # Delete barcodes for this variant
        smriti.db.delete("Item Barcode", {"parent": variant})
        # Delete the variant item itself
        # reviewed-ignore-permissions: bulk variant removal, gated by SMRITI Store Manager or System Manager roles
        frappe.delete_doc("Item", variant, ignore_permissions=True, force=True)
        deleted_variants += 1

    # Delete prices for the template itself
    smriti.db.delete("Item Price", {"item_code": style_code})
    # Delete barcodes for the template itself
    smriti.db.delete("Item Barcode", {"parent": style_code})
    # Delete the template item
    # reviewed-ignore-permissions: bulk variant removal, gated by SMRITI Store Manager or System Manager roles
    frappe.delete_doc("Item", style_code, ignore_permissions=True, force=True)
    smriti.db.commit()

    return {
        "success": True,
        "deleted_variants": deleted_variants,
        "message": _("Style '{0}' and {1} variants deleted successfully").format(style_code, deleted_variants)
    }


@frappe.whitelist()
def validate_pivot_values(styles_json):
    """
    Pre-import verification: checks all unique category, color, and sub-category
    values from the pasted data against the database.
    Returns new values (not yet in DB) with suggestions from existing records.
    """
    styles = frappe.parse_json(styles_json)

    # ── Collect unique values from payload ────────────────────────────────
    categories   = set()
    colors       = set()
    sub_cats     = set()

    for s in styles:
        bd = s.get("base_details", {})
        cat   = (bd.get("item_group") or "").strip()
        color = (bd.get("color") or "").strip().upper()
        sub   = (bd.get("sub_category") or "").strip()
        if cat:   categories.add(cat)
        if color: colors.add(color)
        if sub:   sub_cats.add(sub)

    # ── Item Groups ────────────────────────────────────────────────────────
    all_groups = smriti.db.get_list(
        "Item Group", fields=["name", "is_group"], order_by="name"
    )
    existing_group_names = {normalize_lookup(g.name) for g in all_groups}
    leaf_groups = [g.name for g in all_groups if not g.is_group]

    new_categories = []
    for cat in sorted(categories):
        if normalize_lookup(cat) not in existing_group_names:
            new_categories.append({"value": cat, "suggestions": leaf_groups[:8]})

    # ── Colors (Item Attribute Values) ─────────────────────────────────────
    existing_colors = []
    if smriti.db.exists("Item Attribute", "Color"):
        existing_colors = smriti.db.get_list(
            "Item Attribute Value",
            filters={"parent": "Color"},
            pluck="attribute_value",
            order_by="attribute_value"
        )
    existing_colors_norm = {normalize_lookup(c) for c in existing_colors}

    new_colors = []
    for color in sorted(colors):
        if normalize_lookup(color) not in existing_colors_norm:
            new_colors.append({"value": color, "suggestions": existing_colors[:10]})

    # ── Sub-Categories (SMRITI Sub Category if doctype exists) ─────────────
    existing_sub_cats = []
    new_sub_cats = []
    if smriti.db.exists("DocType", "SMRITI Sub Category"):
        try:
            existing_sub_cats = smriti.db.get_list(
                "SMRITI Sub Category", pluck="name", order_by="name"
            )
            existing_sub_norm = {normalize_lookup(s) for s in existing_sub_cats}
            for sub in sorted(sub_cats):
                if normalize_lookup(sub) not in existing_sub_norm:
                    new_sub_cats.append({
                        "value": sub,
                        "suggestions": existing_sub_cats[:8]
                    })
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:1252: {sys.exc_info()[1]}")

    return {
        "new_categories":    new_categories,
        "new_colors":        new_colors,
        "new_sub_cats":      new_sub_cats,
        "existing_categories": leaf_groups,
        "existing_colors":   existing_colors,
        "existing_sub_cats": existing_sub_cats,
        "has_issues": bool(new_categories or new_colors or new_sub_cats),
    }


@frappe.whitelist()
def import_pivot_item_master(styles_json):
    """
    Saves a batch of Style Templates and their dynamic Size variant items.
    """
    check_store_manager_role()
    _clear_hsn_cache()
    styles = frappe.parse_json(styles_json)
    
    created_count = 0
    updated_count = 0
    errors = []
    
    companies = smriti.db.get_list("Company", limit=1)
    company = (
        frappe.defaults.get_user_default("company") or
        (companies[0].name if companies else None)
    )

    for idx, s in enumerate(styles):
        try:
            bd = s.get("base_details")
            sc = s.get("sizes_config")
            
            style_code = bd.get("article_no").strip()
            item_name = bd.get("description").strip()
            item_group = bd.get("item_group", "Products").strip() or "Products"
            brand = bd.get("brand")
            mrp = flt(bd.get("mrp", 0))
            cost = flt(bd.get("cost_price", 0))
            hsn_code = bd.get("hsn_code")
            
            # Derive GST percentage (HSN-first)
            resolved_hsn = _resolve_hsn_code_cached(hsn_code) if hsn_code else None
            from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
            hsn_derived_rate = get_gst_rate_from_hsn(resolved_hsn, company) if resolved_hsn else None
            if hsn_derived_rate is not None:
                gst_pct = str(hsn_derived_rate)
            else:
                gst_pct = str(bd.get("gst_percentage", "18")).strip()
                
            gender = bd.get("gender", "UNISEX")
            purchase_class = bd.get("purchase_class", "FW")
            merch_cat = bd.get("merchandise_category")
            sub_cat = bd.get("sub_category")
            tax_group = bd.get("product_tax_group")
            vendor_code = bd.get("vendor_code")
            _validate_vendor_code(vendor_code)
            color = bd.get("color", "UNKNOWN").strip().upper()
            
            # Ensure Item Group exists
            if not smriti.db.exists("Item Group", item_group):
                item_group = "Products"
            if not smriti.db.exists("Item Group", item_group):
                existing_group = smriti.db.get_list("Item Group", pluck="name", limit=1)
                item_group = existing_group[0] if existing_group else "Products"

            # Ensure attributes and values exist
            _ensure_item_attribute("Color")
            _ensure_attribute_value("Color", color)
            
            # Create template parent item if it doesn't exist
            template = _get_or_create_template(
                style_code=style_code,
                item_name=item_name,
                item_group=item_group,
                brand=brand,
                mrp=mrp,
                cost=cost,
                gst_pct=gst_pct,
                hsn_code=hsn_code,
                image_link="",
                gender=gender,
                upper_material="",
                outsole="",
                heel_type="",
                purchase_class=purchase_class,
                merch_cat=merch_cat,
                sub_cat=sub_cat,
                tax_group=tax_group,
                vendor_code=vendor_code,
                company=company
            )
            
            # Update base fields if template already existed
            if template.item_name != item_name or flt(template.custom_mrp) != mrp or template.custom_gst_percentage != gst_pct:
                template.item_name = item_name
                _safe_set(template, "custom_mrp", mrp)
                _safe_set(template, "custom_gst_percentage", gst_pct)
                resolved_hsn = _resolve_hsn_code_cached(hsn_code)
                if resolved_hsn:
                    _ensure_hsn_code(resolved_hsn)
                    template.gst_hsn_code = resolved_hsn
                # reviewed-ignore-permissions: excel import of variations, gated by SMRITI Store Manager or System Manager roles
                template.save(ignore_permissions=True)

            # Process variant sizes
            for sz_info in sc:
                size = str(sz_info.get("size")).strip()
                active = sz_info.get("active")
                
                if not active:
                    continue
                    
                _ensure_item_attribute("Size")
                _ensure_attribute_value("Size", size)
                
                variant_code = f"{style_code}-{color}-{size}"
                
                # Check for existing barcode, or generate mock (ARCH-ITEM-001)
                existing_barcode = smriti.db.get("Item Barcode", {"parent": variant_code, "custom_is_primary": 1}, "barcode")
                if existing_barcode:
                    barcode = existing_barcode
                else:
                    max_retries = 10
                    barcode = None
                    for attempt in range(max_retries):
                        barcode = generate_ean13_barcode()
                        duplicate = smriti.db.get("Item Barcode", {"barcode": barcode, "parent": ["!=", variant_code]}, "parent")
                        collides = smriti.db.exists("Item", barcode) and barcode != variant_code
                        if not duplicate and not collides:
                            break
                    else:
                        frappe.throw(frappe._("Could not generate a unique barcode for size {0} after 10 attempts.").format(size))
                    
                if not smriti.db.exists("Item", variant_code):
                    var = smriti.documents.new("Item")
                    var.item_code = variant_code
                    var.item_name = f"{item_name} ({color} / {size})"
                    var.variant_of = style_code
                    var.item_group = template.item_group
                    var.stock_uom = "Nos"
                    var.is_stock_item = 1
                    _safe_set(var, "custom_is_retail_item", 1)
                    _safe_set(var, "custom_mrp", mrp)
                    _safe_set(var, "custom_gst_percentage", gst_pct)
                    resolved_hsn = _resolve_hsn_code_cached(hsn_code)
                    if resolved_hsn:
                        _ensure_hsn_code(resolved_hsn)
                        var.gst_hsn_code = resolved_hsn
                        _safe_set(var, "gn_hsn_code", resolved_hsn)
                    
                    var.append("attributes", {"attribute": "Color", "attribute_value": color})
                    var.append("attributes", {"attribute": "Size", "attribute_value": size})
                    
                    _attach_tax_template(var, tax_group, gst_pct, company)
                    # reviewed-ignore-permissions: excel import of variations, gated by SMRITI Store Manager or System Manager roles
                    var.insert(ignore_permissions=True)
                    created_count += 1
                else:
                    var = smriti.documents.get("Item", variant_code)
                    var.item_name = f"{item_name} ({color} / {size})"
                    _safe_set(var, "custom_mrp", mrp)
                    _safe_set(var, "custom_gst_percentage", gst_pct)
                    resolved_hsn = _resolve_hsn_code_cached(hsn_code)
                    if resolved_hsn:
                        _ensure_hsn_code(resolved_hsn)
                        var.gst_hsn_code = resolved_hsn
                        _safe_set(var, "gn_hsn_code", resolved_hsn)
                    # reviewed-ignore-permissions: excel import of variations, gated by SMRITI Store Manager or System Manager roles
                    var.save(ignore_permissions=True)
                    updated_count += 1
                    
                # Link Barcode (preserving secondary barcodes)
                var_doc = smriti.documents.get("Item", variant_code)
                secondaries = [b for b in var_doc.barcodes if not b.custom_is_primary]
                
                var_doc.barcodes = []
                var_doc.append("barcodes", {
                    "barcode": barcode,
                    "uom": "Nos",
                    "custom_is_primary": 1
                })
                for sec in secondaries:
                    if sec.barcode != barcode:
                        var_doc.append("barcodes", {
                            "barcode": sec.barcode,
                            "uom": sec.uom or "Nos",
                            "custom_is_primary": 0
                        })
                # reviewed-ignore-permissions: excel import of variations, gated by SMRITI Store Manager or System Manager roles
                var_doc.save(ignore_permissions=True)
                
                # Link Prices
                _upsert_item_price(variant_code, "Standard Selling", mrp)
                _upsert_item_price(variant_code, "MRP", mrp)
                
        except Exception as e:
            import traceback
            errors.append({
                "row_idx": idx + 1,
                "article_no": s.get("base_details", {}).get("article_no", ""),
                "error": str(e),
                "detail": traceback.format_exc()
            })
            smriti.errors.log_error(
                title=f"SMRITI Pivot Import — Row {idx + 1}: {s.get('base_details', {}).get('article_no', '')}",
                message=traceback.format_exc()
            )
            
    smriti.db.commit()
    
    return {
        "success": True,
        "created_count": created_count,
        "updated_count": updated_count,
        "errors": errors
    }


@frappe.whitelist()
def reset_all_transactions():
    """
    DANGER: Wipes all transaction history (Sales, POS, Payments, GL, Stock, Purchase)
    and resets the naming series counters to start fresh from 1.
    """
    roles = frappe.get_roles()
    if "System Manager" not in roles and "Administrator" not in roles:
        frappe.throw(_("Restricted: This destructive operation requires System Manager or Administrator role."), frappe.PermissionError)
    
    # Safety toggle: allow reset only if (developer_mode AND smriti_factory_reset_enabled) OR smriti_demo_site is enabled
    allow_reset = (
        (cint(frappe.conf.get("developer_mode") or 0) == 1 and cint(frappe.conf.get("smriti_factory_reset_enabled") or 0) == 1) or
        cint(frappe.conf.get("smriti_demo_site") or 0) == 1
    )
    if not allow_reset:
        frappe.throw(
            _("Destructive reset operations are disabled on this site. Enable developer_mode AND smriti_factory_reset_enabled, or smriti_demo_site in site config to allow this action."),
            title=_("Action Disabled")
        )

    tables = [
        "Sales Invoice",
        "Sales Invoice Item",
        "POS Invoice",
        "POS Invoice Item",
        "POS Invoice Reference",
        "Payment Entry",
        "Payment Entry Reference",
        "Payment Entry Deduction",
        "GL Entry",
        "Stock Ledger Entry",
        "Stock Entry",
        "Stock Entry Detail",
        "Purchase Order",
        "Purchase Order Item",
        "Purchase Receipt",
        "Purchase Receipt Item",
        "Payment Ledger Entry",
        "Serial No",
        "Batch"
    ]
    
    deleted = []
    for doctype in tables:
        if doctype not in _FACTORY_RESET_TRANSACTION_DOCTYPES:
            smriti.errors.log_error(title="SMRITI: Rejected unexpected TRUNCATE", message=f"Refused to truncate unlisted doctype: {doctype}")
            continue
        table_name = f"tab{doctype}"
        try:
            smriti.db.sql(f"TRUNCATE `{table_name}`")
            deleted.append(doctype)
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:1501: {sys.exc_info()[1]}")
            
    # Reset Naming Series
    try:
        smriti.db.sql("TRUNCATE `tabSeries`")
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:1507: {sys.exc_info()[1]}")
        
    smriti.db.commit()
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event("Factory Reset", f"Wiped all transaction history (cleared: {', '.join(deleted)}). User: {frappe.session.user}")

    return {
        "success": True,
        "message": "All transactions have been cleanly reset to 0. Counters will start from 1!",
        "cleared_doctypes": deleted
    }


@frappe.whitelist()
def reset_all_items():
    """
    DANGER: Wipes ALL Item Master data, variants, barcodes, and prices.
    """
    roles = frappe.get_roles()
    if "System Manager" not in roles and "Administrator" not in roles:
        frappe.throw(_("Restricted: This destructive operation requires System Manager or Administrator role."), frappe.PermissionError)
    
    # Safety toggle: allow reset only if (developer_mode AND smriti_factory_reset_enabled) OR smriti_demo_site is enabled
    allow_reset = (
        (cint(frappe.conf.get("developer_mode") or 0) == 1 and cint(frappe.conf.get("smriti_factory_reset_enabled") or 0) == 1) or
        cint(frappe.conf.get("smriti_demo_site") or 0) == 1
    )
    if not allow_reset:
        frappe.throw(
            _("Destructive reset operations are disabled on this site. Enable developer_mode AND smriti_factory_reset_enabled, or smriti_demo_site in site config to allow this action."),
            title=_("Action Disabled")
        )

    # Check for active transactions first before destroying master data
    transaction_doctypes = [
        "Sales Invoice",
        "Purchase Invoice",
        "Stock Entry",
        "Delivery Note",
        "Purchase Receipt",
        "Stock Ledger Entry",
        "GL Entry"
    ]
    for dt in transaction_doctypes:
        if smriti.db.count(dt) > 0:
            frappe.throw(
                _("Cannot reset Item Master because active transactions exist in {0}. Please reset all transactions first.").format(dt),
                title=_("Active Transactions Found")
            )

    tables = [
        "Item",
        "Item Barcode",
        "Item Price",
        "Item Supplier",
        "Item Tax",
        "Item Attribute Value",
        "Item Variant Attribute",
        "Brand",
        "GST HSN Code"
    ]
    
    deleted = []
    for doctype in tables:
        if doctype not in _FACTORY_RESET_ITEM_DOCTYPES:
            smriti.errors.log_error(title="SMRITI: Rejected unexpected TRUNCATE", message=f"Refused to truncate unlisted doctype: {doctype}")
            continue
        table_name = f"tab{doctype}"
        try:
            smriti.db.sql(f"TRUNCATE `{table_name}`")
            deleted.append(doctype)
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in item_master_api.py:1546: {sys.exc_info()[1]}")
            
    smriti.db.commit()
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event("Factory Reset", f"Wiped all Item Master data (cleared: {', '.join(deleted)}). User: {frappe.session.user}")

    return {
        "success": True,
        "message": "All Item Masters, variants, prices, and barcodes have been cleanly reset to 0!",
        "cleared_doctypes": deleted
    }


@frappe.whitelist()
def get_items_missing_barcodes():
    """
    Returns active non-template items that do not have a barcode registered
    in the Item Barcode child table.
    """
    check_store_manager_role()
    
    # Query active items that are not template items (i.e. has_variants = 0)
    items = smriti.db.get_list(
        "Item",
        filters={
            "disabled": 0,
            "has_variants": 0
        },
        fields=["name", "item_name", "item_group", "brand", "variant_of"]
    )
    
    # Get all parent codes that have barcodes
    barcoded_parents = smriti.db.get_list("Item Barcode", pluck="parent")
    barcoded_set = set(barcoded_parents)
    
    missing = []
    for it in items:
        if it.name not in barcoded_set:
            missing.append({
                "item_code": it.name,
                "item_name": it.item_name,
                "item_group": it.item_group,
                "brand": it.brand or "",
                "variant_of": it.variant_of or ""
            })
            
    return missing




