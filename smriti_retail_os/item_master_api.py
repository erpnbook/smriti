# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/item_master_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint
from frappe import _


# ─────────────────────────────────────────────────────────────────────────────
#  COLUMN DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE_HEADERS = [
    "BARCODE NO", "PURCHASE CLASS", "DEPARTMENT", "MERCHANDISE CATEGORY",
    "Category", "Sub category", "ITEM DESCRIPTION", "HEELS", "GENDER",
    "UPPER MATERIAL", "OUTSOLE", "VENDOR CODE", "PRODUCT STYLE CODE",
    "BRAND NAME", "COLOR", "SIZE", "COST PRICE", "PLANNED MRP",
    "PRODUCT TAX", "IMAGE LINK", "HSN CODE", "Product Tax Group"
]

REQUIRED_COLS = ["BARCODE NO", "PRODUCT STYLE CODE", "ITEM DESCRIPTION", "COLOR", "SIZE", "PLANNED MRP"]
VALID_GST = {0, 5, 12, 18, 28}


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_import_template_headers():
    """Returns the ordered list of expected column headers for the CSV template."""
    return TEMPLATE_HEADERS


@frappe.whitelist()
def validate_import_rows(rows_json):
    """
    Dry-run validation of pasted/uploaded rows.
    Returns per-row status: 'valid', 'warning', or 'error' with message lists.
    Duplicate barcodes (within sheet OR already in system) are HARD ERRORS.
    """
    rows = frappe.parse_json(rows_json)
    results = []

    # Track barcodes seen within the sheet itself (for intra-sheet duplicate check)
    seen_barcodes = {}

    for idx, row in enumerate(rows):
        errors = []
        warnings = []

        # ── Required field checks ──────────────────────────────────────────
        for col in REQUIRED_COLS:
            if not str(row.get(col, "")).strip():
                errors.append(f"'{col}' is required")

        barcode = str(row.get("BARCODE NO", "")).strip()

        # ── Intra-sheet duplicate barcode → HARD ERROR ─────────────────────
        if barcode:
            if barcode in seen_barcodes:
                errors.append(
                    f"Duplicate barcode in sheet — same barcode at row {seen_barcodes[barcode] + 1}"
                )
            else:
                seen_barcodes[barcode] = idx

                # ── System duplicate barcode → HARD ERROR ─────────────────
                existing_item = frappe.db.get_value(
                    "Item Barcode", {"barcode": barcode}, "parent"
                )
                if existing_item:
                    errors.append(
                        f"Barcode already exists on item '{existing_item}' — barcodes must be unique"
                    )

        # ── GST % validation ───────────────────────────────────────────────
        gst_raw = str(row.get("PRODUCT TAX", "0") or "0").strip()
        try:
            gst_val = int(float(gst_raw))
            if gst_val not in VALID_GST:
                errors.append(f"GST '{gst_raw}%' is not valid — allowed: 0, 5, 12, 18, 28")
        except ValueError:
            errors.append(f"GST '{gst_raw}' is not a number")

        # ── Vendor / Supplier soft check (warning only) ────────────────────
        vendor = str(row.get("VENDOR CODE", "")).strip()
        if vendor:
            supplier_exists = (
                frappe.db.exists("Supplier", vendor) or
                frappe.db.get_value("Supplier", {"supplier_name": vendor}, "name")
            )
            if not supplier_exists:
                warnings.append(f"Supplier '{vendor}' not found in system — link will be skipped")

        # ── Brand soft check ───────────────────────────────────────────────
        brand = str(row.get("BRAND NAME", "")).strip()
        if brand and not frappe.db.exists("Brand", brand):
            warnings.append(f"Brand '{brand}' not found — will be auto-created")

        # ── Attribute Soft Checks (auto-create warnings) ──────────────────
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
            val = str(row.get(row_key, "")).strip()
            if val:
                # Guard: DocType may not exist on fresh installs
                try:
                    if frappe.db.exists("DocType", doctype_name) and not frappe.db.exists(doctype_name, val):
                        warnings.append(f"{label} '{val}' not found — will be auto-created")
                except Exception:
                    pass

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
    rows = frappe.parse_json(rows_json)

    created = 0
    skipped_duplicates = []
    failed = []

    companies = frappe.get_all("Company", limit=1)
    company = (
        frappe.defaults.get_user_default("company") or
        (companies[0].name if companies else None)
    )

    # Collect barcodes already seen in this batch to prevent intra-batch duplication
    batch_barcodes = set()

    for idx, row in enumerate(rows):
        try:
            # ── Parse row ─────────────────────────────────────────────────
            barcode         = str(row.get("BARCODE NO", "")).strip()
            style_code      = str(row.get("PRODUCT STYLE CODE", "")).strip()
            item_name       = str(row.get("ITEM DESCRIPTION", "")).strip()
            color           = str(row.get("COLOR", "")).strip()
            size            = str(row.get("SIZE", "")).strip()
            brand           = str(row.get("BRAND NAME", "")).strip()
            mrp             = flt(row.get("PLANNED MRP", 0))
            cost            = flt(row.get("COST PRICE", 0))
            gst_pct         = str(int(float(str(row.get("PRODUCT TAX", "0") or "0")))).strip()
            hsn_code        = str(row.get("HSN CODE", "")).strip()
            image_link      = str(row.get("IMAGE LINK", "")).strip()
            item_group      = str(row.get("DEPARTMENT", "Products")).strip() or "Products"
            vendor_code     = str(row.get("VENDOR CODE", "")).strip()
            gender          = str(row.get("GENDER", "")).strip().upper()
            upper_material  = str(row.get("UPPER MATERIAL", "")).strip()
            outsole         = str(row.get("OUTSOLE", "")).strip()
            heel_type       = str(row.get("HEELS", "")).strip()
            purchase_class  = str(row.get("PURCHASE CLASS", "")).strip()
            merch_cat       = str(row.get("MERCHANDISE CATEGORY", "")).strip()
            sub_cat         = str(row.get("Sub category", "")).strip()
            tax_group       = str(row.get("Product Tax Group", "")).strip()

            # ── Hard duplicate barcode check ───────────────────────────────
            if barcode in batch_barcodes:
                skipped_duplicates.append({
                    "row": idx + 1,
                    "barcode": barcode,
                    "reason": "Duplicate barcode within import batch"
                })
                continue

            existing_on_system = frappe.db.get_value(
                "Item Barcode", {"barcode": barcode}, "parent"
            )
            if existing_on_system:
                skipped_duplicates.append({
                    "row": idx + 1,
                    "barcode": barcode,
                    "reason": f"Barcode already exists on item '{existing_on_system}'"
                })
                continue

            batch_barcodes.add(barcode)

            # ── Ensure Item Group exists ───────────────────────────────────
            if not frappe.db.exists("Item Group", item_group):
                item_group = "Products"
            # Also guard the fallback — "Products" may not exist either
            if not frappe.db.exists("Item Group", item_group):
                existing_group = frappe.db.get_all("Item Group", pluck="name", limit=1)
                if existing_group:
                    item_group = existing_group[0]
                else:
                    ig = frappe.new_doc("Item Group")
                    ig.item_group_name = "Products"
                    ig.is_group = 0
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
            if not frappe.db.exists("Item", variant_code):
                variant = frappe.new_doc("Item")
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
                if hsn_code:
                    variant.gst_hsn_code = hsn_code
                    _safe_set(variant, "gn_hsn_code", hsn_code)

                variant.append("attributes", {"attribute": "Color", "attribute_value": color})
                variant.append("attributes", {"attribute": "Size",  "attribute_value": str(size)})

                _attach_tax_template(variant, tax_group, gst_pct, company)
                variant.insert(ignore_permissions=True)
            else:
                variant = frappe.get_doc("Item", variant_code)

            # ── Attach barcode to variant ──────────────────────────────────
            already_linked = frappe.db.exists(
                "Item Barcode", {"barcode": barcode, "parent": variant_code}
            )
            if not already_linked:
                variant.append("barcodes", {"barcode": barcode, "uom": "Nos"})
                variant.save(ignore_permissions=True)

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
            frappe.log_error(
                title=f"SMRITI Item Import — Row {idx + 1}",
                message=frappe.get_traceback()
            )

    frappe.db.commit()

    return {
        "created": created,
        "duplicate_errors": skipped_duplicates,
        "failed": failed
    }


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _safe_set(doc, fieldname, value):
    """Set a field on a Frappe doc, silently skipping if the field doesn't exist.
    Prevents AttributeError when custom fields are missing on fresh installs.
    """
    try:
        doc.set(fieldname, value)
    except Exception:
        pass


def _ensure_master_value(doctype_name, value):
    """Checks if a value exists in a Master DocType, and inserts it if not.
    Silently skips if the DocType itself is not installed (fresh installs).
    """
    val_clean = str(value or "").strip()
    if not val_clean:
        return ""
    try:
        # Guard: DocType may not exist on fresh installations
        if not frappe.db.exists("DocType", doctype_name):
            return val_clean
        if not frappe.db.exists(doctype_name, val_clean):
            doc = frappe.new_doc(doctype_name)
            # Try common field names used in SMRITI master doctypes
            for field in ("attribute_value", "name", doctype_name.lower().replace(" ", "_")):
                try:
                    doc.set(field, val_clean)
                    break
                except Exception:
                    pass
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to auto-create {val_clean} in {doctype_name}: {str(e)}")
    return val_clean


def _get_or_create_template(style_code, item_name, item_group, brand, mrp, cost,
                             gst_pct, hsn_code, image_link, gender, upper_material,
                             outsole, heel_type, purchase_class, merch_cat, sub_cat,
                             tax_group, vendor_code, company):
    if frappe.db.exists("Item", style_code):
        return frappe.get_doc("Item", style_code)

    # Auto-create brand if missing
    if brand and not frappe.db.exists("Brand", brand):
        b = frappe.new_doc("Brand")
        b.brand = brand
        b.insert(ignore_permissions=True)

    item = frappe.new_doc("Item")
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
    if hsn_code:
        if not frappe.db.exists("GST HSN Code", hsn_code):
            hsn_doc = frappe.new_doc("GST HSN Code")
            hsn_doc.name = hsn_code
            hsn_doc.hsn_code = hsn_code
            hsn_doc.description = "Auto-created HSN"
            hsn_doc.insert(ignore_permissions=True)
            frappe.db.commit()
        item.gst_hsn_code = hsn_code
        _safe_set(item, "gn_hsn_code", hsn_code)
    if image_link:
        item.image = image_link

    # Variant attribute definitions on template
    item.append("attributes", {"attribute": "Color"})
    item.append("attributes", {"attribute": "Size"})

    _attach_tax_template(item, tax_group, gst_pct, company)
    item.insert(ignore_permissions=True)

    # Link supplier via custom field (supplier_items child needs POS profile / default config)
    if vendor_code:
        supplier_name = (
            frappe.db.get_value("Supplier", vendor_code, "name") or
            frappe.db.get_value("Supplier", {"supplier_name": vendor_code}, "name")
        )
        if supplier_name:
            item_doc = frappe.get_doc("Item", style_code)
            item_doc.append("supplier_items", {
                "supplier": supplier_name,
                "supplier_part_no": vendor_code
            })
            item_doc.save(ignore_permissions=True)

    return frappe.get_doc("Item", style_code)


def _ensure_item_attribute(attribute_name):
    """Create Item Attribute doctype record if it doesn't exist yet."""
    if not frappe.db.exists("Item Attribute", attribute_name):
        attr = frappe.new_doc("Item Attribute")
        attr.attribute_name = attribute_name
        attr.insert(ignore_permissions=True)


def _ensure_attribute_value(attribute, value):
    """Add a new value to an Item Attribute if it is not already present."""
    if not value:
        return
    exists = frappe.db.get_value(
        "Item Attribute Value",
        {"parent": attribute, "attribute_value": value},
        "name"
    )
    if not exists:
        attr_doc = frappe.get_doc("Item Attribute", attribute)
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
        template_name = frappe.db.get_value(
            "Item Tax Template",
            {"name": ["like", f"%{tax_group}%"], "company": company},
            "name"
        )
    if not template_name and gst_pct:
        template_name = frappe.db.get_value(
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
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.enabled  = 1
        pl.selling  = 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list},
        "name"
    )
    if existing:
        frappe.db.set_value("Item Price", existing, "price_list_rate", flt(rate))
    else:
        ip = frappe.new_doc("Item Price")
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
    import random
    body = f"23{random.randint(1000000000, 9999999999)}"
    odds = sum(int(body[i]) for i in range(0, 12, 2))
    evens = sum(int(body[i]) for i in range(1, 12, 2))
    total = odds + (evens * 3)
    check_digit = (10 - (total % 10)) % 10
    barcode = f"{body}{check_digit}"
    
    if frappe.db.exists("Item Barcode", {"barcode": barcode}):
        return generate_ean13_barcode()
    return barcode


@frappe.whitelist()
def get_style_details(article_no):
    if not frappe.db.exists("Item", article_no):
        return {"exists": False}
        
    doc = frappe.get_doc("Item", article_no)
    variants = frappe.get_all("Item", filters={"variant_of": article_no}, fields=["name", "item_name", "custom_mrp", "valuation_rate"])
    
    sizes = []
    color_val = ""
    for var in variants:
        size_val = frappe.db.get_value("Item Variant Attribute", {"parent": var.name, "attribute": "Size"}, "attribute_value") or ""
        color_val = frappe.db.get_value("Item Variant Attribute", {"parent": var.name, "attribute": "Color"}, "attribute_value") or ""
        barcode = frappe.db.get_value("Item Barcode", {"parent": var.name}, "barcode") or ""
        sizes.append({
            "variant_code": var.name,
            "size": size_val,
            "barcode": barcode,
            "mrp": var.custom_mrp,
            "cost": var.valuation_rate
        })
        
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
        "vendor_code": frappe.db.get_value("Item Supplier", {"parent": article_no}, "supplier_part_no") or "",
        "color": color_val or "UNKNOWN",
        "sizes": sizes
    }


@frappe.whitelist()
def create_style_with_variants(base_details, sizes_config):
    check_store_manager_role()
    
    bd = frappe.parse_json(base_details)
    sc = frappe.parse_json(sizes_config)
    
    style_code = bd.get("article_no").strip()
    item_name = bd.get("description").strip()
    item_group = bd.get("item_group", "Products")
    brand = bd.get("brand")
    mrp = flt(bd.get("mrp", 0))
    cost = flt(bd.get("cost_price", 0))
    gst_pct = str(bd.get("gst_percentage", "0")).strip()
    hsn_code = bd.get("hsn_code")
    gender = bd.get("gender")
    purchase_class = bd.get("purchase_class")
    merch_cat = bd.get("merchandise_category")
    sub_cat = bd.get("sub_category")
    tax_group = bd.get("product_tax_group")
    vendor_code = bd.get("vendor_code")
    color = bd.get("color", "UNKNOWN").strip()
    
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    
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
        if hsn_code:
            template.gst_hsn_code = hsn_code
        template.save(ignore_permissions=True)
        frappe.db.commit()

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
        
        # Determine barcode
        if barcode_mode == "manual":
            if not manual_barcode:
                frappe.throw(frappe._("Manual barcode is required for size {0}").format(size))
            barcode = manual_barcode
        else:
            existing_barcode = frappe.db.get_value("Item Barcode", {"parent": variant_code}, "barcode")
            if existing_barcode:
                barcode = existing_barcode
            else:
                barcode = generate_ean13_barcode()

        # Check barcode uniqueness
        duplicate = frappe.db.get_value("Item Barcode", {"barcode": barcode, "parent": ["!=", variant_code]}, "parent")
        if duplicate:
            frappe.throw(frappe._("Barcode '{0}' is already registered on item '{1}'!").format(barcode, duplicate))
            
        # Create or update variant Item doc
        if not frappe.db.exists("Item", variant_code):
            var = frappe.new_doc("Item")
            var.item_code = variant_code
            var.item_name = f"{item_name} ({color} / {size})"
            var.variant_of = style_code
            var.item_group = item_group
            var.stock_uom = "Nos"
            var.is_stock_item = 1
            _safe_set(var, "custom_is_retail_item", 1)
            _safe_set(var, "custom_mrp", mrp)
            _safe_set(var, "custom_gst_percentage", gst_pct)
            if hsn_code:
                var.gst_hsn_code = hsn_code
                _safe_set(var, "gn_hsn_code", hsn_code)
                
            var.append("attributes", {"attribute": "Color", "attribute_value": color})
            var.append("attributes", {"attribute": "Size", "attribute_value": size})
            
            _attach_tax_template(var, tax_group, gst_pct, company)
            var.insert(ignore_permissions=True)
            created_count += 1
        else:
            var = frappe.get_doc("Item", variant_code)
            var.item_name = f"{item_name} ({color} / {size})"
            _safe_set(var, "custom_mrp", mrp)
            _safe_set(var, "custom_gst_percentage", gst_pct)
            if hsn_code:
                var.gst_hsn_code = hsn_code
                _safe_set(var, "gn_hsn_code", hsn_code)
            var.save(ignore_permissions=True)
            updated_count += 1
            
        # Force set barcode child table row
        frappe.db.delete("Item Barcode", {"parent": variant_code})
        var_doc = frappe.get_doc("Item", variant_code)
        var_doc.append("barcodes", {"barcode": barcode, "uom": "Nos"})
        var_doc.save(ignore_permissions=True)
        
        # Standard Selling prices sync
        _upsert_item_price(variant_code, "Standard Selling", mrp)
        _upsert_item_price(variant_code, "MRP", mrp)
        
        results.append({
            "size": size,
            "variant_code": variant_code,
            "barcode": barcode
        })
        
    frappe.db.commit()
    
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
    if not frappe.db.exists("Item", variant_code):
        return {"success": False, "message": "Variant not found"}
        
    frappe.db.delete("Item Barcode", {"parent": variant_code})
    frappe.db.delete("Item Price", {"item_code": variant_code})
    frappe.delete_doc("Item", variant_code, ignore_missing=True, force=True)
    frappe.db.commit()
    return {"success": True, "message": frappe._("Size variant {0} deleted successfully.").format(variant_code)}


@frappe.whitelist()
def import_pivot_item_master(styles_json):
    """
    Saves a batch of Style Templates and their dynamic Size variant items.
    """
    check_store_manager_role()
    styles = frappe.parse_json(styles_json)
    
    created_count = 0
    updated_count = 0
    errors = []
    
    companies = frappe.get_all("Company", limit=1)
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
            gst_pct = str(bd.get("gst_percentage", "18")).strip()
            hsn_code = bd.get("hsn_code")
            gender = bd.get("gender", "UNISEX")
            purchase_class = bd.get("purchase_class", "FW")
            merch_cat = bd.get("merchandise_category")
            sub_cat = bd.get("sub_category")
            tax_group = bd.get("product_tax_group")
            vendor_code = bd.get("vendor_code")
            color = bd.get("color", "UNKNOWN").strip().upper()
            
            # Ensure Item Group exists
            if not frappe.db.exists("Item Group", item_group):
                item_group = "Products"
            if not frappe.db.exists("Item Group", item_group):
                existing_group = frappe.db.get_all("Item Group", pluck="name", limit=1)
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
                
                # Check for existing barcode, or generate mock
                existing_barcode = frappe.db.get_value("Item Barcode", {"parent": variant_code}, "barcode")
                if existing_barcode:
                    barcode = existing_barcode
                else:
                    barcode = generate_ean13_barcode()
                    
                if not frappe.db.exists("Item", variant_code):
                    var = frappe.new_doc("Item")
                    var.item_code = variant_code
                    var.item_name = f"{item_name} ({color} / {size})"
                    var.variant_of = style_code
                    var.item_group = item_group
                    var.stock_uom = "Nos"
                    var.is_stock_item = 1
                    _safe_set(var, "custom_is_retail_item", 1)
                    _safe_set(var, "custom_mrp", mrp)
                    _safe_set(var, "custom_gst_percentage", gst_pct)
                    if hsn_code:
                        var.gst_hsn_code = hsn_code
                        _safe_set(var, "gn_hsn_code", hsn_code)
                    
                    var.append("attributes", {"attribute": "Color", "attribute_value": color})
                    var.append("attributes", {"attribute": "Size", "attribute_value": size})
                    
                    _attach_tax_template(var, tax_group, gst_pct, company)
                    var.insert(ignore_permissions=True)
                    created_count += 1
                else:
                    var = frappe.get_doc("Item", variant_code)
                    var.item_name = f"{item_name} ({color} / {size})"
                    _safe_set(var, "custom_mrp", mrp)
                    _safe_set(var, "custom_gst_percentage", gst_pct)
                    var.save(ignore_permissions=True)
                    updated_count += 1
                    
                # Link Barcode
                frappe.db.delete("Item Barcode", {"parent": variant_code})
                var_doc = frappe.get_doc("Item", variant_code)
                var_doc.append("barcodes", {"barcode": barcode, "uom": "Nos"})
                var_doc.save(ignore_permissions=True)
                
                # Link Prices
                _upsert_item_price(variant_code, "Standard Selling", mrp)
                _upsert_item_price(variant_code, "MRP", mrp)
                
        except Exception as e:
            errors.append({
                "row_idx": idx + 1,
                "article_no": s.get("base_details", {}).get("article_no", ""),
                "error": str(e)
            })
            
    frappe.db.commit()
    
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
    check_store_manager_role()
    
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
        table_name = f"tab{doctype}"
        try:
            frappe.db.sql(f"TRUNCATE `{table_name}`")
            deleted.append(doctype)
        except Exception:
            pass
            
    # Reset Naming Series
    try:
        frappe.db.sql("TRUNCATE `tabSeries`")
    except Exception:
        pass
        
    frappe.db.commit()
    
    return {
        "success": True,
        "message": "All transactions have been cleanly reset to 0. Counters will start from 1!",
        "cleared_doctypes": deleted
    }


@frappe.whitelist()
def reset_all_items():
    """
    DANGER: Wipes all Item Masters, dynamic size variants, barcodes, brand lists,
    price lists, and item variant attributes cleanly from the database.
    """
    check_store_manager_role()
    
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
        table_name = f"tab{doctype}"
        try:
            frappe.db.sql(f"TRUNCATE `{table_name}`")
            deleted.append(doctype)
        except Exception:
            pass
            
    frappe.db.commit()
    
    return {
        "success": True,
        "message": "All Item Masters, variants, prices, and barcodes have been cleanly reset to 0!",
        "cleared_doctypes": deleted
    }




