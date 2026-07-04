# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/token_registry.py
# @description: Central registry of all label printing tokens used across
#               PRN generation, layout diagnostics preview, and frontend resolveTokens().
#               Single source of truth — eliminates 3-place token duplication.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

"""
SMRITI Label Studio Token Registry
====================================
Every token available for use in ZPL/TSPL raw templates and visual layout
elements is registered here.

Usage:
    from smriti_retail_os.barcode.token_registry import build_token_dict, BARCODE_TOKEN_REGISTRY

    # Build token dict from item data (used in prn_generator and diagnostics_service)
    token_dict = build_token_dict(item_data_dict)

    # Get registry for API exposure (used by get_field_mapping_reference)
    registry = get_registry_for_api()
"""

import datetime


# ---------------------------------------------------------------------------
# REGISTRY DEFINITION
# ---------------------------------------------------------------------------

BARCODE_TOKEN_REGISTRY = {
    "barcode": {
        "source": "item.barcodes[primary].barcode",
        "item_master_field": "Item Barcode (child table)",
        "category": "Barcode",
        "example": "8901234567890",
        "description": (
            "Scanned barcode / EAN-13 number printed as barcode + "
            "human-readable text"
        ),
    },
    "item_code": {
        "source": "item.item_code",
        "item_master_field": "Item Code (inventory identification)",
        "category": "Item",
        "example": "BBM-SPORTS-BLK-08",
        "description": (
            "ERPNext Item Code used for inventory identification. "
            "May differ from the resolved business Style/Article code."
        ),
    },
    "item_name": {
        "source": "item.item_name",
        "item_master_field": "Item Name",
        "category": "Item",
        "example": "BBM Sports Black",
        "description": "Full product name / description (truncated to 28 chars on label)",
    },
    "brand": {
        "source": "item.brand",
        "item_master_field": "Brand",
        "category": "Item",
        "example": "Tattly Threads",
        "description": "Brand name printed prominently on label",
    },
    "mrp": {
        "source": "item.custom_mrp > item_price[MRP] > item_price[Standard Selling] > valuation_rate",
        "item_master_field": "Custom MRP / Item Price (MRP list)",
        "category": "Pricing",
        "example": "1899",
        "description": "Maximum Retail Price — integer only (e.g. 1899, not 1899.00)",
    },
    "size": {
        "source": "item.attributes[Size|Shoe Size|Footwear Size]",
        "item_master_field": "Item Attributes → Size",
        "category": "Variant",
        "example": "8",
        "description": "Shoe/garment size from Item Attribute table",
    },
    "color": {
        "source": "item.attributes[Color|Colour|Shade]",
        "item_master_field": "Item Attributes → Color",
        "category": "Variant",
        "example": "BLACK",
        "description": "Color from Item Attribute table",
    },
    "style": {
        "source": "item.variant_of > item.custom_style_code > item.style_no > item_code.split('-')[0]",
        "item_master_field": "Intelligent Style Resolution",
        "category": "Style",
        "example": "BBM-SPORTS",
        "description": (
            "Resolved Style/Article code using priority: "
            "variant_of > Explicit Style Code > Import Profile > SKU splitting."
        ),
    },
    "style_code": {
        "source": "item.custom_style_code > item.style_no",
        "item_master_field": "Explicit Style Code / Article Number",
        "category": "Style",
        "example": "BBM-SPORTS",
        "description": (
            "Returns the explicit Style Code / Article Number field exactly "
            "as stored in the Item Master without applying Style Resolution."
        ),
    },
    "variant_template": {
        "source": "item.variant_of",
        "item_master_field": "ERP Variant Template ID",
        "category": "Style",
        "example": "BBM-SPORTS",
        "description": "Returns the template item ID (variant_of) for variant items.",
    },
    "pkd_date": {
        "source": "auto-generated at print time",
        "item_master_field": "Auto-generated at print time",
        "category": "Date",
        "example": "06/26",
        "description": "Packing date in MM/YY format — stamped when the PRN is generated",
    },
    "gender": {
        "source": "item.custom_gender",
        "item_master_field": "Custom Gender (custom_gender) → SMRITI Gender master",
        "category": "Fashion",
        "example": "MENS",
        "description": "Gender classification — MENS / LADIES / BOYS / GIRLS / UNISEX / KIDS",
    },
    "heel_type": {
        "source": "item.custom_heel_type",
        "item_master_field": "Custom Heel Type (custom_heel_type)",
        "category": "Fashion",
        "example": "FLAT",
        "description": "Heel type for footwear labels — FLAT / BLOCK / WEDGE / PENCIL / PLATFORM",
    },
    "outsole": {
        "source": "item.custom_outsole",
        "item_master_field": "Custom Outsole (custom_outsole)",
        "category": "Fashion",
        "example": "EVA",
        "description": "Outsole material — EVA / TPR / PU / RUBBER / PVC",
    },
    "upper_material": {
        "source": "item.custom_upper_material",
        "item_master_field": "Custom Upper Material (custom_upper_material)",
        "category": "Fashion",
        "example": "SYNTHETIC",
        "description": "Upper material — SYNTHETIC / LEATHER / MESH / CANVAS / PU",
    },
    "merchandise_category": {
        "source": "item.custom_merchandise_category",
        "item_master_field": "Custom Merchandise Category",
        "category": "Classification",
        "example": "SPORTS",
        "description": "Merchandise category for retail classification",
    },
    "sub_category": {
        "source": "item.custom_sub_category",
        "item_master_field": "Custom Sub Category",
        "category": "Classification",
        "example": "RUNNING",
        "description": "Sub-category under the merchandise category",
    },
    "purchase_class": {
        "source": "item.custom_purchase_class",
        "item_master_field": "Custom Purchase Class",
        "category": "Purchase",
        "example": "FW",
        "description": "Purchase class code — FW / MFW / LFW etc.",
    },
}


# ---------------------------------------------------------------------------
# TOKEN DICT BUILDER
# ---------------------------------------------------------------------------

def build_token_dict(item_data: dict) -> dict:
    """
    Builds the substitution token dict from a flat item data dictionary.
    This is the single function used by:
      - prn_generator.generate_prn() for actual PRN output
      - diagnostics_service.validate_layout_diagnostics() for preview
      - get_field_mapping_reference() API for UI display

    Args:
        item_data: Flat dict of item fields (same shape as get_item_print_details output)

    Returns:
        dict: {token_name: resolved_value, ...}
    """
    from frappe.utils import flt
    import datetime as _dt

    mrp = flt(item_data.get("mrp") or 0)
    item_code = item_data.get("item_code") or ""
    pkd_date = item_data.get("pkd_date") or _dt.datetime.now().strftime("%m/%y")

    # Style resolution: use pre-resolved value from item_service, or fallback
    style = item_data.get("style") or (item_code.split("-")[0] if "-" in item_code else item_code)

    return {
        "barcode":              item_data.get("barcode") or "",
        "item_code":            item_code,
        "item_name":            (item_data.get("item_name") or "")[:28],
        "brand":                item_data.get("brand") or "SMRITI",
        "mrp":                  str(int(mrp)) if mrp else "0",
        "size":                 item_data.get("size") or "Nos",
        "color":                item_data.get("color") or "",
        "style":                style,
        "style_code":           item_data.get("style_code") or "",
        "variant_template":     item_data.get("variant_template") or "",
        "pkd_date":             pkd_date,
        "gender":               item_data.get("gender") or "",
        "heel_type":            item_data.get("heel_type") or "",
        "outsole":              item_data.get("outsole") or "",
        "upper_material":       item_data.get("upper_material") or "",
        "merchandise_category": item_data.get("merchandise_category") or "",
        "sub_category":         item_data.get("sub_category") or "",
        "purchase_class":       item_data.get("purchase_class") or "",
    }


def build_preview_token_dict(item_data: dict) -> dict:
    """
    Builds preview token dict with sensible sample fallbacks for diagnostics.
    Used in validate_layout_diagnostics() when item_data may be sparse.
    """
    sample = {
        "barcode":   "8901234567890",
        "item_code": "ITEM-12345",
        "item_name": "Sample Item Name Description",
        "brand":     "SMRITI",
        "mrp":       "499",
        "size":      "8",
        "color":     "BLACK",
        "style":     "STYLE",
        "pkd_date":  "06/26",
    }
    # Override samples with actual values when present
    base = dict(sample)
    if item_data:
        for k in base:
            val = item_data.get(k)
            if val:
                base[k] = str(val)
    return base


def get_registry_for_api() -> list:
    """
    Returns registry as a list of dicts suitable for the field mapping reference API.
    Replaces the hardcoded list in the old get_field_mapping_reference() function.
    """
    result = []
    for token, meta in BARCODE_TOKEN_REGISTRY.items():
        result.append({
            "placeholder":       "{" + token + "}",
            "item_master_field": meta.get("item_master_field", ""),
            "example":           meta.get("example", ""),
            "description":       meta.get("description", ""),
            "category":          meta.get("category", ""),
        })
    return result
