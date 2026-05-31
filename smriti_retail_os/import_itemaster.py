# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/import_itemaster.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
import frappe
from frappe.utils import flt, cint

grid_data = [
    {
        "base_barcode": "23052026001",
        "article": "20016",
        "color": "BLACK",
        "category": "SANDAL",
        "sub_category": "LASTIC PATTA",
        "mrp": 1899,
    },
    {
        "base_barcode": "23052026002",
        "article": "20016",
        "color": "BEIGE",
        "category": "SANDAL",
        "sub_category": "LASTIC PATTA",
        "mrp": 1899,
    },
    {
        "base_barcode": "23052026003",
        "article": "2006",
        "color": "BLACK",
        "category": "CHAPPAL",
        "sub_category": "BURMY",
        "mrp": 1499,
    },
    {
        "base_barcode": "23052026004",
        "article": "2006",
        "color": "CREAM",
        "category": "CHAPPAL",
        "sub_category": "BURMY",
        "mrp": 1499,
    },
    {
        "base_barcode": "23052026005",
        "article": "20001",
        "color": "BLACK",
        "category": "SANDAL",
        "sub_category": "MUEL",
        "mrp": 1999,
    },
    {
        "base_barcode": "23052026006",
        "article": "20001",
        "color": "BEIGE",
        "category": "SANDAL",
        "sub_category": "MUEL",
        "mrp": 1999,
    },
    {
        "base_barcode": "23052026007",
        "article": "10019",
        "color": "BLACK",
        "category": "CHAPPAL",
        "sub_category": "MUEL",
        "mrp": 1399,
    },
    {
        "base_barcode": "23052026008",
        "article": "10019",
        "color": "BEIGE",
        "category": "CHAPPAL",
        "sub_category": "MUEL",
        "mrp": 1399,
    },
    {
        "base_barcode": "23052026009",
        "article": "2097",
        "color": "BLACK",
        "category": "CHAPPAL",
        "sub_category": "MUEL",
        "mrp": 1499,
    },
    {
        "base_barcode": "23052026010",
        "article": "2097",
        "color": "PISTA",
        "category": "CHAPPAL",
        "sub_category": "MUEL",
        "mrp": 1499,
    }
]

SIZES = ["36", "37", "38", "39", "40", "41", "42"]

def run():
    print("Starting SMRITI Item Master import and barcode regeneration...")

    companies = frappe.get_all("Company")
    if not companies:
        co = frappe.new_doc("Company")
        co.company_name = "SMRITI Retail"
        co.default_currency = "INR"
        co.insert(ignore_permissions=True)
        frappe.db.commit()
        company = co.name
        print(f"Created default company: {company}")
    else:
        company = frappe.defaults.get_user_default("company") or companies[0].name
    gst_pct = "18"
    hsn_code = "64041990"

    # Ensure GST HSN Code exists
    if not frappe.db.exists("GST HSN Code", hsn_code):
        hsn_doc = frappe.new_doc("GST HSN Code")
        hsn_doc.name = hsn_code
        hsn_doc.hsn_code = hsn_code
        hsn_doc.description = "Auto-created HSN"
        hsn_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Created HSN Code: {hsn_code}")

    # Ensure Attributes exist
    for attr in ["Color", "Size"]:
        if not frappe.db.exists("Item Attribute", attr):
            d = frappe.new_doc("Item Attribute")
            d.attribute_name = attr
            d.insert(ignore_permissions=True)
            print(f"Created Item Attribute: {attr}")

    for row in grid_data:
        base_barcode = row["base_barcode"]
        style_code = row["article"]
        color = row["color"]
        category = row["category"]
        sub_cat = row["sub_category"]
        mrp = flt(row["mrp"])
        cost = flt(mrp * 2.0 / 3.0)

        item_name = f"{style_code} {category} {sub_cat}"

        # Ensure Attribute Values exist
        for attr, val in [("Color", color)] + [("Size", s) for s in SIZES]:
            exists = frappe.db.get_value(
                "Item Attribute Value",
                {"parent": attr, "attribute_value": val},
                "name"
            )
            if not exists:
                attr_doc = frappe.get_doc("Item Attribute", attr)
                attr_doc.append("item_attribute_values", {
                    "attribute_value": val,
                    "abbr": val[:4].upper().replace(" ", "")
                })
                attr_doc.save(ignore_permissions=True)
                print(f"Added attribute value: {val} to {attr}")

        # 1. Create or get Template Item
        if not frappe.db.exists("Item", style_code):
            template = frappe.new_doc("Item")
            template.item_code = style_code
            template.item_name = item_name
            template.item_group = "Products"
            template.stock_uom = "Nos"
            template.is_stock_item = 1
            template.has_variants = 1
            template.custom_is_retail_item = 1
            template.custom_mrp = mrp
            template.valuation_rate = cost
            template.custom_gst_percentage = gst_pct
            template.gst_hsn_code = hsn_code
            template.gn_hsn_code = hsn_code
            template.custom_merchandise_category = category
            template.custom_sub_category = sub_cat

            # Attribute list
            template.append("attributes", {"attribute": "Color"})
            template.append("attributes", {"attribute": "Size"})

            _attach_tax_template(template, gst_pct, company)
            template.insert(ignore_permissions=True)
            print(f"Created Template Item: {style_code}")
        else:
            template = frappe.get_doc("Item", style_code)
            template.item_name = item_name
            template.custom_mrp = mrp
            template.valuation_rate = cost
            template.custom_gst_percentage = gst_pct
            template.gst_hsn_code = hsn_code
            template.gn_hsn_code = hsn_code
            template.custom_merchandise_category = category
            template.custom_sub_category = sub_cat
            template.save(ignore_permissions=True)
            print(f"Updated Template Item: {style_code}")

        # 2. Process variants for each size
        for size in SIZES:
            variant_code = f"{style_code}-{color}-{size}"
            variant_name = f"{item_name} ({color} / {size})"
            target_barcode = f"{base_barcode}-{size}"

            # Clean up other items using this target barcode
            existing_barcode_holders = frappe.db.get_all(
                "Item Barcode",
                filters={"barcode": target_barcode, "parent": ["!=", variant_code]},
                pluck="parent"
            )
            for holder in existing_barcode_holders:
                holder_doc = frappe.get_doc("Item", holder)
                holder_doc.barcodes = [b for b in holder_doc.barcodes if b.barcode != target_barcode]
                holder_doc.save(ignore_permissions=True)
                print(f"Cleared duplicate barcode {target_barcode} from {holder}")

            if not frappe.db.exists("Item", variant_code):
                variant = frappe.new_doc("Item")
                variant.item_code = variant_code
                variant.item_name = variant_name
                variant.variant_of = style_code
                variant.item_group = "Products"
                variant.stock_uom = "Nos"
                variant.is_stock_item = 1
                variant.custom_is_retail_item = 1
                variant.custom_mrp = mrp
                variant.custom_gst_percentage = gst_pct
                variant.gst_hsn_code = hsn_code
                variant.gn_hsn_code = hsn_code

                variant.append("attributes", {"attribute": "Color", "attribute_value": color})
                variant.append("attributes", {"attribute": "Size", "attribute_value": size})

                _attach_tax_template(variant, gst_pct, company)
                variant.insert(ignore_permissions=True)
                print(f"Created Variant Item: {variant_code}")
            else:
                variant = frappe.get_doc("Item", variant_code)
                variant.item_name = variant_name
                variant.custom_mrp = mrp
                variant.custom_gst_percentage = gst_pct
                variant.gst_hsn_code = hsn_code
                variant.gn_hsn_code = hsn_code
                variant.save(ignore_permissions=True)
                print(f"Updated Variant Item: {variant_code}")

            # Re-attach barcodes
            variant.barcodes = []
            variant.append("barcodes", {"barcode": target_barcode, "uom": "Nos"})
            variant.save(ignore_permissions=True)
            print(f"Assigned barcode {target_barcode} to {variant_code}")

            # Standard Pricing setup
            _upsert_item_price(variant_code, "Standard Selling", mrp)
            _upsert_item_price(variant_code, "MRP", mrp)

    frappe.db.commit()
    print("SMRITI Item Master import and barcode regeneration completed successfully!")


def _attach_tax_template(item, gst_pct, company):
    template_name = frappe.db.get_value(
        "Item Tax Template",
        {"name": ["like", f"%{gst_pct}%"], "company": company},
        "name"
    )
    if template_name:
        # Clear existing taxes to avoid duplicate child entries
        item.taxes = []
        item.append("taxes", {"item_tax_template": template_name, "tax_category": ""})


def _upsert_item_price(item_code, price_list, rate):
    if not rate:
        return
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.enabled = 1
        pl.selling = 1
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
        ip.item_code = item_code
        ip.price_list = price_list
        ip.price_list_rate = flt(rate)
        ip.currency = "INR"
        ip.uom = "Nos"
        ip.insert(ignore_permissions=True)


def cleanup_gst_settings():
    import frappe
    if frappe.db.exists("DocType", "GST Settings"):
        try:
            doc = frappe.get_doc("GST Settings")
            original_len = len(doc.gst_accounts)
            doc.gst_accounts = [a for a in doc.gst_accounts if a.company != "Test Company"]
            if len(doc.gst_accounts) != original_len:
                doc.save(ignore_permissions=True)
                frappe.db.commit()
                print("SUCCESS: Cleaned up orphaned GST settings.")
        except Exception as e:
            print("WARNING: Could not clean up GST Settings:", str(e))


def create_smriti_company():
    import frappe
    company_name = "SMRITI Retail"
    if frappe.db.exists("Company", company_name):
        print(f"Company '{company_name}' already exists!")
        return
    
    # Self-heal old test residues
    cleanup_gst_settings()
    
    co = frappe.new_doc("Company")
    co.company_name = company_name
    co.default_currency = "INR"
    co.country = "India"
    co.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"SUCCESS: Company '{co.name}' created successfully!")


