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

    company = (
        frappe.defaults.get_user_default("company") or
        frappe.get_all("Company", limit=1)[0].name
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
                variant.custom_is_retail_item = 1
                variant.custom_mrp   = mrp
                variant.custom_gst_percentage = gst_pct
                if image_link:
                    variant.image = image_link
                if hsn_code:
                    variant.gn_hsn_code = hsn_code

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
    item.custom_is_retail_item  = 1
    item.custom_mrp             = mrp
    item.valuation_rate         = cost
    item.custom_gst_percentage  = gst_pct
    item.custom_gender          = gender
    item.custom_upper_material  = upper_material
    item.custom_outsole         = outsole
    item.custom_heel_type       = heel_type
    item.custom_purchase_class  = purchase_class
    item.custom_merchandise_category = merch_cat
    item.custom_sub_category    = sub_cat

    if brand:
        item.brand = brand
    if hsn_code:
        item.gn_hsn_code = hsn_code
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
        attr_doc.append("item_attribute_values", {
            "attribute_value": value,
            "abbr": value[:4].upper().replace(" ", "")
        })
        attr_doc.save(ignore_permissions=True)


def _attach_tax_template(item, tax_group, gst_pct, company):
    """Resolve and attach an Item Tax Template."""
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
