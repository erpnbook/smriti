# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode_api.py
# @description: Barcode printing API — ZPL/TSPL generation, LAN printing, template management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 2.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import socket
import datetime
from frappe.utils import flt, cint
from frappe import _


# ---------------------------------------------------------------------------
# FILTER HELPERS
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_barcode_filters():
    """
    Returns available brands, categories, barcode sizes and print templates
    to populate filters/dropdowns on the barcode printing interface, along with
    departments, genders, seasons, collections, and suppliers.
    """
    brands = [b.name for b in frappe.get_all("Brand", fields=["name"], order_by="name asc")]
    categories = [ig.name for ig in frappe.get_all("Item Group", fields=["name"], order_by="name asc")]
    sizes = ["50x25", "50x30", "75x50", "100x50", "106x55"]

    # Load available print templates from SMRITI Print Template DocType
    templates = []
    if frappe.db.exists("DocType", "SMRITI Print Template"):
        templates = frappe.get_all(
            "SMRITI Print Template",
            fields=["name", "template_title", "label_size", "printer_language", "printer_family", "raw_template", "custom_field_mappings_json"],
            order_by="template_title asc"
        )
        for t in templates:
            t["template_name"] = t["template_title"]

    # Retail Fashion Filters
    departments = [d.name for d in frappe.get_all("Department", fields=["name"], order_by="name asc")]
    
    genders = []
    if frappe.db.exists("DocType", "SMRITI Gender"):
        genders = [g.name for g in frappe.get_all("SMRITI Gender", fields=["name"], order_by="name asc")]
    else:
        genders = ["MENS", "LADIES", "BOYS", "GIRLS", "UNISEX", "KIDS"]

    # Seasons from Item Attributes or fallback
    seasons_res = frappe.db.get_all("Item Attribute Value", filters={"parent": ["like", "%season%"]}, fields=["attribute_value"], distinct=True)
    seasons = [s.attribute_value for s in seasons_res] if seasons_res else []
    if not seasons:
        seasons = ["Spring/Summer", "Autumn/Winter", "Festive", "Core", "All Season"]
    seasons = sorted(list(set(seasons)))

    # Collections from Item Attributes or fallback
    collections_res = frappe.db.get_all("Item Attribute Value", filters={"parent": ["like", "%collection%"]}, fields=["attribute_value"], distinct=True)
    collections = [c.attribute_value for c in collections_res] if collections_res else []
    if not collections:
        collections = ["Classic", "Sportswear", "Casuals", "Formal", "Limited Edition"]
    collections = sorted(list(set(collections)))

    suppliers = [s.name for s in frappe.get_all("Supplier", fields=["name"], order_by="name asc")]

    return {
        "brands": brands,
        "categories": categories,
        "sizes": sizes,
        "print_templates": templates,
        "departments": departments,
        "genders": genders,
        "seasons": seasons,
        "collections": collections,
        "suppliers": suppliers
    }


@frappe.whitelist()
def get_print_templates():
    """
    Returns all available SMRITI Print Templates for dropdown selection.
    """
    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        return []

    templates = frappe.get_all(
        "SMRITI Print Template",
        fields=["name", "template_title", "label_size", "printer_language", "printer_family", "raw_template", "custom_field_mappings_json"],
        order_by="template_title asc"
    )
    for t in templates:
        t["template_name"] = t["template_title"]
    return templates



# ---------------------------------------------------------------------------
# ITEM LOADING
# ---------------------------------------------------------------------------

@frappe.whitelist()
def expand_item_variants(item_code, default_print_qty=1):
    """
    Checks if item has variants. If yes, returns list of print details for all
    non-disabled variants. If no, returns list with print details for the item itself.
    """
    has_variants = frappe.db.get_value("Item", item_code, "has_variants")
    if has_variants:
        variants = frappe.db.get_all(
            "Item",
            filters={"variant_of": item_code, "disabled": 0},
            fields=["name"]
        )
        res = []
        for v in variants:
            res.append(get_item_print_details(v.name, default_print_qty))
        return res
    else:
        return [get_item_print_details(item_code, default_print_qty)]


@frappe.whitelist()
def get_transaction_items_checklist(source_doctype, source_name):
    """
    Returns all items in the specified Purchase Receipt or Stock Entry transaction
    to populate the frontend checklist modal.
    """
    if source_doctype not in ["Purchase Receipt", "Stock Entry"]:
        return []
        
    if not frappe.db.exists(source_doctype, source_name):
        return []
        
    items = []
    doc = frappe.get_doc(source_doctype, source_name)
    
    for it in doc.items:
        # Check if barcode exists in child table
        has_barcode = frappe.db.exists("Item Barcode", {"parent": it.item_code})
        # Check if item is recently created (within 30 days)
        creation = frappe.db.get_value("Item", it.item_code, "creation")
        is_new = False
        if creation:
            from frappe.utils import add_days, now_datetime
            is_new = creation >= add_days(now_datetime(), -30)
            
        items.append({
            "item_code": it.item_code,
            "item_name": it.item_name or "",
            "qty": flt(it.qty),
            "has_barcode": bool(has_barcode),
            "is_new": is_new
        })
        
    return items


@frappe.whitelist()
def get_items_by_range(from_article, to_article):
    """
    Returns items in the specified article range.
    Supports numerical range filtering if prefixes match (e.g. BBM-0001 to BBM-0100).
    Otherwise, filters alphabetically on item_code.
    """
    if not from_article or not to_article:
        return []

    from_article = from_article.strip()
    to_article = to_article.strip()

    import re
    def parse_prefix_num(article):
        # Match alphanumeric prefix followed by a hyphen and digits (e.g. BBM-0001)
        match = re.match(r'^([a-zA-Z0-9\-]+?\-)(\d+)$', article)
        if match:
            return match.group(1), int(match.group(2)), len(match.group(2))
        return None, None, None

    prefix_from, num_from, len_from = parse_prefix_num(from_article)
    prefix_to, num_to, len_to = parse_prefix_num(to_article)

    item_codes = []
    if prefix_from and prefix_to and prefix_from == prefix_to:
        # Range is numerical
        lower = min(num_from, num_to)
        upper = max(num_from, num_to)
        
        # Query items with this prefix
        items = frappe.db.get_all(
            "Item",
            filters={"item_code": ["like", f"{prefix_from}%"], "disabled": 0},
            fields=["name"]
        )
        
        for item in items:
            code = item.name
            suffix = code[len(prefix_from):]
            if suffix.isdigit():
                val = int(suffix)
                if lower <= val <= upper:
                    item_codes.append(code)
    else:
        # Range is alphabetical/lexicographical
        items = frappe.db.get_all(
            "Item",
            filters={
                "item_code": [">=", from_article],
                "disabled": 0
            },
            fields=["name"],
            order_by="item_code asc"
        )
        for item in items:
            if item.name <= to_article:
                item_codes.append(item.name)
            else:
                break

    # Expand variants and get print details
    res_items = []
    for code in item_codes:
        res_items.extend(expand_item_variants(code, 1))
        
    return res_items


@frappe.whitelist()
def get_items_for_printing(filters=None, source_doctype=None, source_name=None):
    """
    Loads items for barcode printing based on either a transaction source
    (Purchase Receipt or Stock Entry) or manual filter selection.
    """
    items = []

    if source_doctype and source_name:
        # Transaction-based loading
        if source_doctype == "Purchase Receipt":
            if not frappe.db.exists("Purchase Receipt", source_name):
                frappe.throw(_("Purchase Receipt {0} not found.").format(source_name))

            pr = frappe.get_doc("Purchase Receipt", source_name)
            for it in pr.items:
                items.extend(expand_item_variants(it.item_code, it.qty))

        elif source_doctype == "Stock Entry":
            if not frappe.db.exists("Stock Entry", source_name):
                frappe.throw(_("Stock Entry {0} not found.").format(source_name))

            se = frappe.get_doc("Stock Entry", source_name)
            for it in se.items:
                items.extend(expand_item_variants(it.item_code, it.qty))

    elif filters:
        # Manual bulk filter mode
        flt_dict = frappe.parse_json(filters)
        db_filters = {"disabled": 0}

        if flt_dict.get("brand"):
            db_filters["brand"] = flt_dict.get("brand")
        if flt_dict.get("item_group"):
            db_filters["item_group"] = flt_dict.get("item_group")
        if flt_dict.get("custom_barcode_size"):
            db_filters["custom_barcode_size"] = flt_dict.get("custom_barcode_size")

        # Fashion Retail Filters
        if flt_dict.get("department"):
            db_filters["custom_department"] = flt_dict.get("department")
        if flt_dict.get("gender"):
            db_filters["custom_gender"] = flt_dict.get("gender")

        # Upgrade-safe guards for Season and Collection
        if flt_dict.get("season"):
            season_val = flt_dict.get("season")
            if frappe.db.has_column("Item", "custom_season"):
                db_filters["custom_season"] = season_val
            else:
                # Fallback: search in Item Attributes
                items_with_season = frappe.get_all(
                    "Item Attribute",
                    filters={"attribute": ["like", "%season%"], "attribute_value": season_val},
                    fields=["parent"]
                )
                db_filters["name"] = ["in", [i.parent for i in items_with_season]]

        if flt_dict.get("collection"):
            collection_val = flt_dict.get("collection")
            if frappe.db.has_column("Item", "custom_collection"):
                db_filters["custom_collection"] = collection_val
            else:
                # Fallback: search in Item Attributes
                items_with_collection = frappe.get_all(
                    "Item Attribute",
                    filters={"attribute": ["like", "%collection%"], "attribute_value": collection_val},
                    fields=["parent"]
                )
                if "name" in db_filters and isinstance(db_filters["name"], list) and db_filters["name"][0] == "in":
                    # Intersect existing list
                    db_filters["name"][1] = list(set(db_filters["name"][1]) & set([i.parent for i in items_with_collection]))
                else:
                    db_filters["name"] = ["in", [i.parent for i in items_with_collection]]

        if flt_dict.get("supplier"):
            supplier = flt_dict.get("supplier")
            # Query items that have this supplier in tabItem Supplier child table
            item_list = frappe.db.get_all(
                "Item Supplier",
                filters={"supplier": supplier},
                fields=["parent"]
            )
            item_codes = [i.parent for i in item_list]
            if "name" in db_filters and isinstance(db_filters["name"], list) and db_filters["name"][0] == "in":
                db_filters["name"][1] = list(set(db_filters["name"][1]) & set(item_codes))
            else:
                db_filters["name"] = ["in", item_codes]

        # Style / Article No Filter with schema check-guards
        if flt_dict.get("style"):
            style_val = flt_dict.get("style").strip()
            if frappe.db.has_column("Item", "custom_style_code"):
                db_filters["custom_style_code"] = ["like", f"%{style_val}%"]
            elif frappe.db.has_column("Item", "style_no"):
                db_filters["style_no"] = ["like", f"%{style_val}%"]
            else:
                db_filters["item_code"] = ["like", f"%{style_val}%"]

        or_filters = {}
        if flt_dict.get("search_text"):
            txt = flt_dict.get("search_text")
            or_filters = {
                "item_code": ["like", f"%{txt}%"],
                "item_name": ["like", f"%{txt}%"]
            }

        item_list = frappe.db.get_all(
            "Item",
            filters=db_filters,
            or_filters=or_filters,
            fields=["name"],
            limit=100
        )

        for it in item_list:
            items.extend(expand_item_variants(it.name, 1))

    return items


def get_item_print_details(item_code, default_print_qty):
    """
    Resolves standard printing parameters for a single item.
    Includes all custom Item Master fields used as PRN placeholders.
    """
    item_doc = frappe.get_doc("Item", item_code)

    # 1. Fetch Barcode - prioritize custom_is_primary = 1, then fallback to first, then item_code
    barcodes_list = frappe.db.get_all(
        "Item Barcode",
        filters={"parent": item_code},
        fields=["barcode", "custom_is_primary"],
        order_by="custom_is_primary desc, creation asc"
    )
    
    barcode = item_code
    if barcodes_list:
        barcode = barcodes_list[0].barcode

    # 2. Fetch MRP — custom_mrp > MRP price list > Standard Selling > valuation_rate
    mrp = (
        item_doc.get("custom_mrp")
        or frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": "MRP"}, "price_list_rate")
        or frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate")
        or item_doc.valuation_rate
        or 0.0
    )

    # 3. Size from Item Attributes
    size = "L"
    if item_doc.attributes:
        for attr in item_doc.attributes:
            if attr.attribute.upper() in ["SIZE", "SHOE SIZE", "FOOTWEAR SIZE"]:
                size = attr.attribute_value
                break

    # 4. Color from Item Attributes
    color = ""
    if item_doc.attributes:
        for attr in item_doc.attributes:
            if attr.attribute.lower() in ["color", "colour", "shade"]:
                color = attr.attribute_value
                break

    # 5. Style / Article Number (item_code prefix before first hyphen)
    style = item_code
    if "-" in style:
        style = style.split("-")[0]

    # 6. Packing Date
    pkd_date = datetime.datetime.now().strftime("%m/%y")

    # 7. Pack Size / Carton Size
    pack_size = None
    if item_doc.meta.has_field("custom_pack_size"):
        pack_size = item_doc.get("custom_pack_size")
    elif item_doc.meta.has_field("custom_carton_size"):
        pack_size = item_doc.get("custom_carton_size")

    return {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name or "",
        "brand": item_doc.brand or "SMRITI",
        "item_group": item_doc.item_group or "",
        "barcode": barcode,
        "mrp": flt(mrp),
        "size": size,
        "color": color,
        "style": style,
        "pkd_date": pkd_date,
        "pack_size": flt(pack_size) if pack_size else None,
        # Custom Footwear Attributes
        "gender": item_doc.get("custom_gender") or "",
        "heel_type": item_doc.get("custom_heel_type") or "",
        "outsole": item_doc.get("custom_outsole") or "",
        "upper_material": item_doc.get("custom_upper_material") or "",
        "merchandise_category": item_doc.get("custom_merchandise_category") or "",
        "sub_category": item_doc.get("custom_sub_category") or "",
        "purchase_class": item_doc.get("custom_purchase_class") or "",
        "print_qty": cint(default_print_qty) or 1,
        "label_size": item_doc.get("custom_barcode_size") or "50x25"
    }


# ---------------------------------------------------------------------------
# PRN GENERATION — TEMPLATE-DRIVEN
# ---------------------------------------------------------------------------

@frappe.whitelist()
def generate_prn(items, template_name=None):
    """
    Generates raw ZPL/TSPL PRN content for the given items list.

    If template_name is provided and exists in SMRITI Print Template,
    it uses that template's raw_template with Python .format() substitution.
    Otherwise falls back to built-in hardcoded templates.

    Placeholder tokens in raw_template (all lowercase, wrapped in {}):
        {barcode}       — EAN/UPC barcode number
        {item_code}     — ERPNext Item Code (also used as Style/Article No)
        {item_name}     — Full item name / description
        {brand}         — Brand name
        {mrp}           — MRP price (number only, e.g. 499)
        {size}          — Shoe/garment size (e.g. 7, 8, L, XL)
        {color}         — Color value
        {style}         — Style/Article prefix (item_code before first hyphen)
        {pkd_date}      — Packing date in MM/YY format
        {gender}        — Gender (MENS/LADIES/BOYS/GIRLS/UNISEX/KIDS)
        {heel_type}     — Heel Type (FLAT/BLOCK/WEDGE/PENCIL/PLATFORM)
        {outsole}       — Outsole material (EVA/TPR/PU/RUBBER/PVC)
        {upper_material}— Upper material (SYNTHETIC/LEATHER/MESH etc.)
        {merchandise_category} — Merchandise Category
        {sub_category}  — Sub Category
        {purchase_class}— Purchase Class (FW/MFW/LFW etc.)
    """
    if not items:
        return ""

    items_list = frappe.parse_json(items)
    prn_output = []

    # --- Try to load custom template from DB ---
    db_template = None
    if template_name and frappe.db.exists("DocType", "SMRITI Print Template"):
        if frappe.db.exists("SMRITI Print Template", template_name):
            db_template = frappe.get_doc("SMRITI Print Template", template_name)
        else:
            # Fallback: search by template_title
            matched_name = frappe.db.get_value("SMRITI Print Template", {"template_title": template_name}, "name")
            if matched_name:
                db_template = frappe.get_doc("SMRITI Print Template", matched_name)


    for it in items_list:
        barcode        = it.get("barcode") or ""
        item_name      = (it.get("item_name") or "")[:28]
        item_code      = it.get("item_code") or ""
        mrp            = flt(it.get("mrp"))
        brand          = it.get("brand") or "SMRITI"
        size           = it.get("size") or "Nos"
        color          = it.get("color") or ""
        style          = it.get("style") or item_code.split("-")[0]
        pkd_date       = it.get("pkd_date") or datetime.datetime.now().strftime("%m/%y")
        gender         = it.get("gender") or ""
        heel_type      = it.get("heel_type") or ""
        outsole        = it.get("outsole") or ""
        upper_material = it.get("upper_material") or ""
        merch_cat      = it.get("merchandise_category") or ""
        sub_cat        = it.get("sub_category") or ""
        purch_class    = it.get("purchase_class") or ""
        qty            = cint(it.get("print_qty")) or 1
        label_size     = it.get("label_size") or "50x25"

        # Token substitution dict for user-defined templates
        token_dict = {
            "barcode":              barcode,
            "item_code":            item_code,
            "item_name":            item_name,
            "brand":                brand,
            "mrp":                  f"{int(mrp)}",
            "size":                 size,
            "color":                color,
            "style":                style,
            "pkd_date":             pkd_date,
            "gender":               gender,
            "heel_type":            heel_type,
            "outsole":              outsole,
            "upper_material":       upper_material,
            "merchandise_category": merch_cat,
            "sub_category":         sub_cat,
            "purchase_class":       purch_class,
        }

        # If a DB template matches, use it
        if db_template:
            try:
                raw = db_template.raw_template or ""
                
                # Check for dynamic mappings JSON
                mappings_json = db_template.get("custom_field_mappings_json")
                if mappings_json:
                    mappings = frappe.parse_json(mappings_json)
                    if mappings and isinstance(mappings, list):
                        item_doc = None
                        try:
                            item_doc = frappe.get_doc("Item", item_code)
                        except Exception:
                            import sys
                            _frappe = sys.modules.get('frappe')
                            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:323: {sys.exc_info()[1]}")
                            
                        # Rebuild token dict dynamically using mappings
                        token_dict = {}
                        for m in mappings:
                            lbl_f = m.get("label_field")
                            erp_f = m.get("erp_field")
                            if not lbl_f or not erp_f:
                                continue
                            
                            val = None
                            if item_doc and item_doc.meta.has_field(erp_f):
                                val = item_doc.get(erp_f)
                            elif erp_f == "item_code":
                                val = item_code
                            elif erp_f == "item_name":
                                val = item_name
                            elif erp_f == "barcode":
                                val = barcode
                            elif erp_f == "mrp":
                                val = mrp
                            elif erp_f == "brand":
                                val = brand
                            elif erp_f == "size":
                                val = size
                            elif erp_f == "color":
                                val = color
                            elif erp_f == "style":
                                val = style
                            elif erp_f == "pkd_date":
                                val = pkd_date
                            elif erp_f in it:
                                val = it.get(erp_f)
                            else:
                                # Fallback to pre-resolved footwear attributes
                                val = it.get(lbl_f) or ""
                                
                            # Currency formatting
                            if lbl_f == "mrp" or "mrp" in erp_f or "rate" in erp_f or "price" in erp_f:
                                try:
                                    val = f"{int(flt(val))}"
                                except Exception:
                                    import sys
                                    _frappe = sys.modules.get('frappe')
                                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:365: {sys.exc_info()[1]}")
                                    
                            token_dict[lbl_f] = str(val) if val is not None else ""

                label_str = raw.format(**token_dict)
                for _ in range(qty):
                    prn_output.append(label_str)
                continue
            except Exception as e:
                frappe.log_error(
                    f"PRN template substitution failed for '{template_name}': {e}",
                    "Barcode API"
                )
                # Fall through to built-in templates

        # --- Built-in fallback: TSPL 106x55 3-up label ---
        if label_size == "106x55":
            mrp_str       = f"{int(mrp)}/-/-"
            mrp_str_short = f"{int(mrp)}/-"
            label_tspl = (
                f"SIZE 106.6 mm, 55.4 mm\n"
                f"GAP 3 mm, 0 mm\n"
                f"SPEED 4\n"
                f"DENSITY 14\n"
                f"DIRECTION 0,0\n"
                f"REFERENCE 0,0\n"
                f"OFFSET 0 mm\n"
                f"SET PEEL OFF\n"
                f"SET CUTTER OFF\n"
                f"SET TEAR ON\n"
                f"CLS\n"
                f"CODEPAGE 850\n"
                # --- Column 1: Full MRP label ---
                f'TEXT 820,372,"2",180,2,2,"{color}"\n'
                f'TEXT 702,318,"2",180,3,3,"{size}"\n'
                f'TEXT 820,428,"3",180,2,2,"{style}"\n'
                f'TEXT 556,335,"4",180,1,1,"{mrp_str}"\n'
                f'TEXT 824,260,"3",180,1,1,"{brand}"\n'
                f'TEXT 809,304,"1",180,2,2,"SIZE-"\n'
                f'TEXT 475,401,"1",180,1,1,"Footwear"\n'
                f'TEXT 596,401,"1",180,1,1,"Commodity :"\n'
                f'TEXT 594,381,"1",180,1,1,"Net Contents :"\n'
                f'TEXT 448,381,"1",180,1,1,"1 Pair"\n'
                f'TEXT 600,301,"1",180,1,1,"(Incl of all Taxes)"\n'
                f'TEXT 594,358,"1",180,1,1,"Pkd On :"\n'
                f'TEXT 501,358,"1",180,1,1,"{pkd_date}"\n'
                f'BARCODE 613,279,"128",95,0,180,2,4,"{barcode}"\n'
                f'TEXT 597,176,"3",180,1,1,"{barcode}"\n'
                # --- Column 2: Shoe tag (smaller) ---
                f'TEXT 315,89,"3",180,1,1,"{color}"\n'
                f'TEXT 310,47,"2",180,1,1,"{style}"\n'
                f'TEXT 149,91,"3",180,1,1,"{mrp_str_short}"\n'
                f'TEXT 311,62,"1",180,1,1,"Size:"\n'
                f'TEXT 308,215,"2",180,1,1,"{brand}"\n'
                f'TEXT 259,62,"1",180,1,1,"{size}"\n'
                f'TEXT 226,66,"1",180,1,1,"(Incl of all Taxes)"\n'
                f'TEXT 149,45,"1",180,1,1,"{brand}"\n'
                f'BARCODE 312,190,"39",62,0,180,1,3,"{barcode}"\n'
                f'TEXT 297,120,"3",180,1,1,"{barcode}"\n'
                # --- Column 3: Box tag (smaller) ---
                f'TEXT 307,313,"3",180,1,1,"{color}"\n'
                f'TEXT 302,272,"2",180,1,1,"{style}"\n'
                f'TEXT 141,315,"3",180,1,1,"{mrp_str_short}"\n'
                f'TEXT 302,287,"1",180,1,1,"Size:"\n'
                f'TEXT 300,435,"2",180,1,1,"{brand}"\n'
                f'TEXT 251,287,"1",180,1,1,"{size}"\n'
                f'TEXT 217,290,"1",180,1,1,"(Incl of all Taxes)"\n'
                f'TEXT 141,270,"1",180,1,1,"{brand}"\n'
                f'BARCODE 304,406,"39",58,0,180,1,3,"{barcode}"\n'
                f'TEXT 288,339,"3",180,1,1,"{barcode}"\n'
                # MRP labels in Rs
                f'TEXT 598,335,"0",180,12,12,"Rs."\n'
                f'TEXT 177,315,"0",180,8,8,"Rs."\n'
                f'TEXT 186,91,"0",180,8,8,"Rs."\n'
                f"PRINT 1,1"
            )
            for _ in range(qty):
                prn_output.append(label_tspl)
            continue

        # --- Built-in fallback: Zebra ZPL (50x25, 50x30, 75x50, 100x50) ---
        x_offset      = 20
        y_offset_bc   = 10
        y_offset_name = 80
        y_offset_mrp  = 100
        y_offset_brand = 120

        if label_size == "50x30":
            y_offset_name  = 85
            y_offset_mrp   = 110
            y_offset_brand = 135
        elif label_size == "75x50":
            x_offset       = 40
            y_offset_bc    = 20
            y_offset_name  = 120
            y_offset_mrp   = 155
            y_offset_brand = 190
        elif label_size == "100x50":
            x_offset       = 50
            y_offset_bc    = 20
            y_offset_name  = 130
            y_offset_mrp   = 170
            y_offset_brand = 210

        size_color_line = f"{brand} | Sz:{size}"
        if color:
            size_color_line += f" | {color}"

        label_zpl = (
            f"^XA\n"
            f"^FO{x_offset},{y_offset_bc}^BCN,60,Y,N,N^FD{barcode}^FS\n"
            f"^FO{x_offset},{y_offset_name}^ADN,18,10^FD{item_name}^FS\n"
            f"^FO{x_offset},{y_offset_mrp}^ADN,18,10^FDMRP: Rs.{mrp:.2f}^FS\n"
            f"^FO{x_offset},{y_offset_brand}^ADN,14,8^FD{size_color_line}^FS\n"
            f"^XZ"
        )

        for _ in range(qty):
            prn_output.append(label_zpl)

    return "\n".join(prn_output)


# ---------------------------------------------------------------------------
# NETWORK (LAN) PRINTER — Raw Socket Printing
# ---------------------------------------------------------------------------

@frappe.whitelist()
def send_to_network_printer(items, template_name=None, printer_ip=None, printer_port=9100):
    """
    Generates PRN content and streams it directly to a network label printer
    via a raw TCP/IP socket connection (LAN/Wi-Fi).

    Args:
        items (str):         JSON string of items (same format as generate_prn)
        template_name (str): Name of SMRITI Print Template to use
        printer_ip (str):    IP address of the label printer on the network
        printer_port (int):  TCP port — default 9100 (standard raw printing port)

    Returns:
        dict: { success: bool, message: str, labels_sent: int }
    """
    if not printer_ip:
        frappe.throw(_("Printer IP address is required for LAN printing."))

    prn_data = generate_prn(items, template_name=template_name)
    if not prn_data:
        frappe.throw(_("No PRN data generated. Check items and template."))

    port = cint(printer_port) or 9100
    labels_sent = prn_data.count("^XA") + prn_data.count("PRINT 1,1")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((printer_ip.strip(), port))
            s.sendall(prn_data.encode("utf-8", errors="replace"))

        return {
            "success": True,
            "message": _(
                "Successfully sent {0} label(s) to printer at {1}:{2}"
            ).format(labels_sent, printer_ip, port),
            "labels_sent": labels_sent
        }

    except socket.timeout:
        frappe.throw(
            _("Connection timed out. Verify printer IP {0} and port {1} are reachable.").format(
                printer_ip, port
            )
        )
    except ConnectionRefusedError:
        frappe.throw(
            _("Printer at {0}:{1} refused the connection. Ensure the printer is online and raw TCP port is enabled.").format(
                printer_ip, port
            )
        )
    except Exception as e:
        frappe.throw(_("Printer error: {0}").format(str(e)))


# ---------------------------------------------------------------------------
# FIELD MAPPING REFERENCE (for UI helper dialog)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_field_mapping_reference():
    """
    Returns a structured reference of Item Master fields and their
    corresponding PRN template placeholder tokens.
    Used by the UI to display the mapping helper dialog to operators.
    """
    return [
        {
            "placeholder": "{barcode}",
            "item_master_field": "Item Barcode (child table)",
            "example": "8901030987654",
            "description": "Scanned barcode / EAN-13 number printed as barcode + human-readable text"
        },
        {
            "placeholder": "{item_code}",
            "item_master_field": "Item Code (inventory identification)",
            "example": "BBM-SPORTS-BLK-08",
            "description": "ERPNext Item Code used for inventory identification. May differ from the resolved business Style/Article code."
        },
        {
            "placeholder": "{style}",
            "item_master_field": "Intelligent Style Resolution",
            "example": "BBM-SPORTS",
            "description": "Resolved Style/Article code using priority: variant_of > Explicit Style Code > Import Profile > SKU splitting."
        },
        {
            "placeholder": "{style_code}",
            "item_master_field": "Explicit Style Code / Article Number",
            "example": "BBM-SPORTS",
            "description": "Returns the explicit Style Code / Article Number field exactly as stored in the Item Master without applying Style Resolution."
        },
        {
            "placeholder": "{variant_template}",
            "item_master_field": "ERP Variant Template ID",
            "example": "BBM-SPORTS",
            "description": "Returns the template item ID (variant_of) for variant items."
        },
        {
            "placeholder": "{item_name}",
            "item_master_field": "Item Name",
            "example": "BBM Sports Black",
            "description": "Full product name / description (truncated to 28 chars on label)"
        },
        {
            "placeholder": "{brand}",
            "item_master_field": "Brand",
            "example": "BIG BOSS",
            "description": "Brand name printed prominently on label"
        },
        {
            "placeholder": "{mrp}",
            "item_master_field": "Custom MRP / Item Price (MRP list)",
            "example": "1899",
            "description": "Maximum Retail Price — integer only (e.g. 1899, not 1899.00)"
        },
        {
            "placeholder": "{size}",
            "item_master_field": "Item Attributes → Size",
            "example": "8",
            "description": "Shoe/garment size from Item Attribute table (attribute name: Size)"
        },
        {
            "placeholder": "{color}",
            "item_master_field": "Item Attributes → Color",
            "example": "BLACK",
            "description": "Color from Item Attribute table (attribute names: Color/Colour/Shade)"
        },
        {
            "placeholder": "{pkd_date}",
            "item_master_field": "Auto-generated at print time",
            "example": "06/26",
            "description": "Packing date in MM/YY format — stamped when the PRN is generated"
        },
        {
            "placeholder": "{gender}",
            "item_master_field": "Custom Gender (custom_gender) → SMRITI Gender master",
            "example": "MENS",
            "description": "Target gender — MENS / LADIES / BOYS / GIRLS / UNISEX / KIDS"
        },
        {
            "placeholder": "{heel_type}",
            "item_master_field": "Custom Heel Type (custom_heel_type) → SMRITI Heel Type master",
            "example": "FLAT",
            "description": "Heel construction — FLAT / BLOCK / WEDGE / PENCIL / PLATFORM"
        },
        {
            "placeholder": "{outsole}",
            "item_master_field": "Custom Outsole (custom_outsole) → SMRITI Outsole master",
            "example": "EVA",
            "description": "Outsole material — EVA / TPR / PU / RUBBER / PVC"
        },
        {
            "placeholder": "{upper_material}",
            "item_master_field": "Custom Upper Material (custom_upper_material) → SMRITI Upper Material master",
            "example": "SYNTHETIC",
            "description": "Upper material — SYNTHETIC / LEATHER / MESH / CANVAS / KNITTED"
        },
        {
            "placeholder": "{merchandise_category}",
            "item_master_field": "Custom Merchandise Category (custom_merchandise_category)",
            "example": "CASUAL WEAR",
            "description": "Broad merchandise grouping for reporting and display"
        },
        {
            "placeholder": "{sub_category}",
            "item_master_field": "Custom Sub Category (custom_sub_category)",
            "example": "LOAFERS",
            "description": "Detailed sub-classification within merchandise category"
        },
        {
            "placeholder": "{purchase_class}",
            "item_master_field": "Custom Purchase Class (custom_purchase_class) → SMRITI Purchase Class master",
            "example": "SPORTS",
            "description": "Buying classification — FW/MFW/LFW/BFW/GFW/KFW/SPORTS/ACC/BAG etc."
        },
    ]


# ---------------------------------------------------------------------------
# SMRITI LABEL STUDIO V2 APIS
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_recent_transactions(doctype, limit=15):
    """
    Fetches the latest transacting records of type Purchase Receipt or Stock Entry.
    """
    if doctype not in ["Purchase Receipt", "Stock Entry"]:
        return []

    if doctype == "Purchase Receipt":
        query_res = frappe.db.sql(
            """
            SELECT 
                pr.name, 
                pr.posting_date, 
                pr.supplier_name as extra_info,
                (SELECT COUNT(*) FROM `tabPurchase Receipt Item` pri WHERE pri.parent = pr.name) as items_count
            FROM `tabPurchase Receipt` pr
            ORDER BY pr.creation DESC
            LIMIT %s
            """,
            (cint(limit) or 15,),
            as_dict=True
        )
    else: # Stock Entry
        query_res = frappe.db.sql(
            """
            SELECT 
                se.name, 
                se.posting_date, 
                se.purpose as extra_info,
                (SELECT COUNT(*) FROM `tabStock Entry Detail` sed WHERE sed.parent = se.name) as items_count
            FROM `tabStock Entry` se
            ORDER BY se.creation DESC
            LIMIT %s
            """,
            (cint(limit) or 15,),
            as_dict=True
        )

    for r in query_res:
        if r.posting_date:
            r.posting_date = r.posting_date.strftime("%Y-%m-%d")
    return query_res


@frappe.whitelist()
def test_printer_connection(printer_ip, printer_port=9100):
    """
    TCP ping/connection test to label printer IP/Port.
    """
    import socket
    import time
    
    port = cint(printer_port) or 9100
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((printer_ip.strip(), port))
        elapsed = (time.time() - start_time) * 1000
        return {
            "success": True,
            "latency_ms": round(elapsed, 1),
            "message": f"Connection successful! Response time: {elapsed:.1f} ms"
        }
    except socket.timeout:
        return {"success": False, "latency_ms": None, "message": "Connection timed out. Verify IP and Port."}
    except Exception as e:
        return {"success": False, "latency_ms": None, "message": f"Connection failed: {str(e)}"}


@frappe.whitelist()
def print_test_label(printer_ip, printer_port=9100, printer_language="ZPL"):
    """
    Sends a test print layout directly to raw printer socket.
    """
    import socket
    
    port = cint(printer_port) or 9100
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if printer_language == "TSPL":
        test_code = (
            f"SIZE 50 mm, 25 mm\n"
            f"GAP 3 mm, 0 mm\n"
            f"DIRECTION 1\n"
            f"CLS\n"
            f'TEXT 20,20,"3",0,1,1,"SMRITI TEST"\n'
            f'TEXT 20,60,"2",0,1,1,"IP: {printer_ip}"\n'
            f'TEXT 20,100,"2",0,1,1,"PORT: {printer_port}"\n'
            f'TEXT 20,140,"1",0,1,1,"{now_str}"\n'
            f"PRINT 1,1\n"
        )
    else: # ZPL
        test_code = (
            f"^XA\n"
            f"^FO40,30^ADN,24,14^FDSMRITI PRINTER TEST^FS\n"
            f"^FO40,70^ADN,18,10^FDPrinter IP: {printer_ip}^FS\n"
            f"^FO40,100^ADN,18,10^FDPort: {printer_port}^FS\n"
            f"^FO40,135^ADN,14,8^FDTime: {now_str}^FS\n"
            f"^XZ\n"
        )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((printer_ip.strip(), port))
            s.sendall(test_code.encode("utf-8", errors="replace"))
        return {"success": True, "message": "Test label sent successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def log_print_job(template_name, printer_ip, labels_count, success, error_message=None, print_profile=None, details=None):
    """
    Logs print job activity locally and in Frappe Activity Log for audit-trail.
    """
    success_val = cint(success)
    # 1. Local file log
    try:
        import os
        log_dir = os.path.join(frappe.get_app_path("smriti_retail_os"), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "barcode_print.log")
        log_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {frappe.session.user} - Template: {template_name} - IP: {printer_ip} - Count: {labels_count} - Success: {success_val} - Error: {error_message or 'None'}\n"
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(log_msg)
    except Exception as e:
        frappe.log_error(f"Failed to write local print log: {str(e)}")

    # 2. Frappe Activity Log (Standardized JSON remarks)
    try:
        import json
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
        log_doc = frappe.new_doc("Activity Log")
        log_doc.user = frappe.session.user
        log_doc.operation = "SMRITI Label Studio Print Run"
        log_doc.status = "Success" if success_val else "Failed"
        log_doc.subject = f"Printed {labels_count} label(s) using template {template_name} on {printer_ip}"
        
        remarks_dict = {
            "labels": cint(labels_count),
            "template": template_name,
            "printer": printer_ip,
            "status": "success" if success_val else "failed",
            "error_message": error_message or "",
            "company": company,
            "profile": print_profile or "None",
            "details": details or ""
        }
        log_doc.remarks = json.dumps(remarks_dict)
        log_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to write Activity Log print job: {str(e)}")

    return {"success": True}


@frappe.whitelist()
def get_print_analytics():
    """
    Compiles detailed print analytics by parsing remarks JSON from SMRITI Activity Logs.
    """
    try:
        logs = frappe.db.get_all(
            "Activity Log",
            filters={"operation": "SMRITI Label Studio Print Run"},
            fields=["remarks", "status", "creation"],
            order_by="creation desc"
        )
        
        total_labels = 0
        total_jobs = len(logs)
        failed_jobs = 0
        success_jobs = 0
        
        template_stats = {}
        printer_stats = {}
        history = []
        
        import json
        for log in logs:
            remarks = log.remarks or ""
            data = {}
            if remarks.strip().startswith("{") and remarks.strip().endswith("}"):
                try:
                    data = json.loads(remarks)
                except Exception:
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:852: {sys.exc_info()[1]}")
            
            if not data:
                # Fallback parser for older/legacy logs
                labels = 0
                template = "Unknown"
                printer = "Unknown"
                status = "success" if log.status == "Success" else "failed"
                for line in remarks.split("\n"):
                    if line.startswith("Printer IP:"): printer = line.split("Printer IP:")[1].strip()
                    elif line.startswith("Success:"): status = "success" if line.split("Success:")[1].strip() == "1" else "failed"
                
                # Check subject for labels count
                subj = log.subject or ""
                if "Printed " in subj and " label" in subj:
                    try:
                        labels = cint(subj.split("Printed ")[1].split(" label")[0])
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:870: {sys.exc_info()[1]}")
                if "using template " in subj:
                    try:
                        template = subj.split("using template ")[1].split(" on ")[0]
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:875: {sys.exc_info()[1]}")
                
                data = {
                    "labels": labels,
                    "template": template,
                    "printer": printer,
                    "status": status
                }
            
            labels = cint(data.get("labels", 0))
            template = data.get("template", "Unknown") or "Unknown"
            printer = data.get("printer", "Unknown") or "Unknown"
            status = data.get("status", "success")
            
            total_labels += labels
            if status == "success" or log.status == "Success":
                success_jobs += 1
            else:
                failed_jobs += 1
                
            # Aggregate template usage
            if template not in template_stats:
                template_stats[template] = {"runs": 0, "labels": 0}
            template_stats[template]["runs"] += 1
            template_stats[template]["labels"] += labels
            
            # Aggregate printer usage
            if printer not in printer_stats:
                printer_stats[printer] = {"runs": 0, "labels": 0}
            printer_stats[printer]["runs"] += 1
            printer_stats[printer]["labels"] += labels
            
            # Add to history list (limit to latest 30)
            if len(history) < 30:
                history.append({
                    "date": log.creation.strftime("%Y-%m-%d %H:%M"),
                    "template": template,
                    "printer": printer,
                    "labels": labels,
                    "status": "Success" if (status == "success" or log.status == "Success") else "Failed"
                })
                
        # Find top template
        top_template = "None"
        max_temp_runs = 0
        for t, s in template_stats.items():
            if s["runs"] > max_temp_runs:
                max_temp_runs = s["runs"]
                top_template = t
                
        # Find top printer
        top_printer = "None"
        max_print_runs = 0
        for p, s in printer_stats.items():
            if s["runs"] > max_print_runs:
                max_print_runs = s["runs"]
                top_printer = p
                
        return {
            "total_labels": total_labels,
            "total_jobs": total_jobs,
            "failed_jobs": failed_jobs,
            "success_jobs": success_jobs,
            "failed_percentage": round((failed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0.0,
            "top_template": top_template,
            "top_printer": top_printer,
            "template_stats": template_stats,
            "printer_stats": printer_stats,
            "history": history
        }
    except Exception as e:
        frappe.log_error(f"Error compiling print analytics: {str(e)}")
        return {
            "total_labels": 0,
            "total_jobs": 0,
            "failed_jobs": 0,
            "success_jobs": 0,
            "failed_percentage": 0.0,
            "top_template": "None",
            "top_printer": "None",
            "template_stats": {},
            "printer_stats": {},
            "history": []
        }


@frappe.whitelist()
def get_template_usage_stats():
    """
    Aggregates template usage statistics from the Activity Log database table.
    """
    try:
        logs = frappe.db.get_all(
            "Activity Log",
            filters={"operation": "SMRITI Label Studio Print Run"},
            fields=["subject", "status", "creation"]
        )
        stats = {}
        for log in logs:
            subj = log.subject or ""
            if "using template " in subj:
                parts = subj.split("using template ")
                if len(parts) > 1:
                    temp_part = parts[1].split(" on ")[0]
                    if temp_part not in stats:
                        stats[temp_part] = {"runs": 0, "labels": 0, "success": 0, "failed": 0}
                    
                    stats[temp_part]["runs"] += 1
                    if log.status == "Success":
                        stats[temp_part]["success"] += 1
                    else:
                        stats[temp_part]["failed"] += 1
                        
                    try:
                        lbl_cnt = int(subj.split("Printed ")[1].split(" label")[0])
                        stats[temp_part]["labels"] += lbl_cnt
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:992: {sys.exc_info()[1]}")
        return stats
    except Exception as e:
        frappe.log_error(f"Error compiling template usage stats: {str(e)}")
        return {}


@frappe.whitelist()
def get_print_profiles():
    """
    Retrieves print profiles JSON from SMRITI Company Settings.
    """
    settings_name = frappe.db.get_value("SMRITI Company Settings", {}, "name")
    if not settings_name:
        return {}
    
    profiles_json = frappe.db.get_value("SMRITI Company Settings", settings_name, "custom_print_profiles_json")
    if not profiles_json:
        return {}
        
    try:
        return frappe.parse_json(profiles_json)
    except Exception:
        return {}


@frappe.whitelist()
def save_print_profile(profile_name, template_name, printer_ip, printer_port=9100, dpi="203 DPI", copies=1, label_size="50x25", is_default=0):
    """
    Saves a print profile in SMRITI Company Settings as a keyed JSON object.
    """
    import json
    settings_name = frappe.db.get_value("SMRITI Company Settings", {}, "name")
    if not settings_name:
        comp = frappe.db.get_value("Company", {}, "name")
        if not comp:
            frappe.throw(_("Please create a Company record first."))
        doc = frappe.new_doc("SMRITI Company Settings")
        doc.company = comp
        doc.insert(ignore_permissions=True)
        settings_name = doc.name

    doc = frappe.get_doc("SMRITI Company Settings", settings_name)
    profiles = {}
    if doc.custom_print_profiles_json:
        try:
            profiles = frappe.parse_json(doc.custom_print_profiles_json)
        except Exception:
            profiles = {}

    is_default = cint(is_default)
    if is_default:
        for p in profiles.values():
            p["is_default"] = 0

    profiles[profile_name] = {
        "profile_name": profile_name,
        "template_name": template_name,
        "printer_ip": printer_ip,
        "printer_port": cint(printer_port) or 9100,
        "dpi": dpi,
        "copies": cint(copies) or 1,
        "label_size": label_size,
        "is_default": is_default
    }

    doc.custom_print_profiles_json = json.dumps(profiles)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return profiles


@frappe.whitelist()
def delete_print_profile(profile_name):
    """
    Deletes a print profile from SMRITI Company Settings.
    """
    settings_name = frappe.db.get_value("SMRITI Company Settings", {}, "name")
    if not settings_name:
        return {}

    doc = frappe.get_doc("SMRITI Company Settings", settings_name)
    if not doc.custom_print_profiles_json:
        return {}

    try:
        profiles = frappe.parse_json(doc.custom_print_profiles_json)
    except Exception:
        return {}

    if profile_name in profiles:
        del profiles[profile_name]
        doc.custom_print_profiles_json = json.dumps(profiles)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return profiles


@frappe.whitelist()
def save_print_template(template_name, label_size, printer_language, raw_template, field_mappings_json=None, printer_family=None, custom_active=1, custom_is_default=0, custom_version="1.0.0", custom_visual_layout_json=None, version_label=None):
    """
    Saves or updates a SMRITI Print Template record with size validations.
    """
    # 100 KB template size limit validation
    if len(raw_template.encode('utf-8')) > 102400:
        frappe.throw(_("Template exceeds 100KB limit"))

    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        frappe.throw(_("DocType SMRITI Print Template not found."))

    def _slugify_name(val):
        import re
        clean = re.sub(r'[^a-zA-Z0-9\-]', '_', val)
        clean = re.sub(r'_+', '_', clean)
        return clean.strip('_').upper()

    name_id = _slugify_name(template_name)

    if frappe.db.exists("SMRITI Print Template", name_id):
        doc = frappe.get_doc("SMRITI Print Template", name_id)
    elif frappe.db.exists("SMRITI Print Template", {"template_title": template_name}):
        matched_name = frappe.db.get_value("SMRITI Print Template", {"template_title": template_name}, "name")
        doc = frappe.get_doc("SMRITI Print Template", matched_name)
    else:
        doc = frappe.new_doc("SMRITI Print Template")
        doc.name = name_id

    doc.template_title = template_name
    doc.label_size = label_size
    doc.printer_language = printer_language
    doc.printer_family = printer_family or printer_language
    doc.raw_template = raw_template
    doc.custom_field_mappings_json = field_mappings_json
    doc.custom_visual_layout_json = custom_visual_layout_json
    doc.custom_active = int(custom_active)

    if custom_version and custom_version != doc.custom_version:
        doc.custom_version = custom_version

    if version_label:
        doc.flags.version_label = version_label

    if int(custom_is_default) == 1:
        # Unset other defaults for the same label size
        frappe.db.sql(
            "UPDATE `tabSMRITI Print Template` SET custom_is_default = 0 WHERE label_size = %s",
            (label_size,)
        )
        doc.custom_is_default = 1
    else:
        doc.custom_is_default = int(custom_is_default)

    if custom_visual_layout_json:
        val_res = validate_layout_diagnostics(custom_visual_layout_json, label_size)
        score = val_res.get("printability_score", 100.0)
        grade = val_res.get("grade", "A+")
        enforce = get_enforce_printability_threshold()
        if enforce and grade == "F":
            errors = [d["message"] for d in val_res.get("diagnostics", []) if d.get("severity") == "error"]
            err_msg = "; ".join(errors) if errors else "Low printability score"
            frappe.throw(
                _("Template save blocked. Printability Score: {0} (Grade F). Errors: {1}").format(score, err_msg)
            )

    try:
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Log Audit event: SMRITI Visual Template Saved
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": frappe.session.user,
            "operation": "SMRITI Visual Template Saved",
            "status": "Success",
            "subject": f"Saved print template {template_name}",
            "remarks": f"Template saved. Active version: {doc.custom_version}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        # Log Audit event: SMRITI Visual Template Compilation Failed
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": frappe.session.user,
            "operation": "SMRITI Visual Template Compilation Failed",
            "status": "Failed",
            "subject": f"Failed to save print template {template_name}",
            "remarks": str(e)
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        raise e
    
    return get_print_templates()


@frappe.whitelist()
def delete_print_template(name_id):
    """
    Deletes a SMRITI Print Template record.
    """
    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        frappe.throw(_("DocType SMRITI Print Template not found."))

    if frappe.db.exists("SMRITI Print Template", name_id):
        frappe.delete_doc("SMRITI Print Template", name_id, ignore_permissions=True)
        frappe.db.commit()
    return get_print_templates()


@frappe.whitelist()
def search_barcode_items(txt):
    """
    Search against:
    - item_code
    - item_name
    - barcode
    - style/article code
    
    Returns top 20 matches.
    """
    if not txt:
        return []

    search_val = f"%{txt}%"
    
    # Check if custom_style_code or style_no column exists in Item
    style_columns = ["variant_of"]
    if frappe.db.has_column("Item", "custom_style_code"):
        style_columns.append("custom_style_code")
    elif frappe.db.has_column("Item", "style_no"):
        style_columns.append("style_no")
        
    where_clauses = [
        "i.name LIKE %(search_val)s",
        "i.item_name LIKE %(search_val)s",
        "ib.barcode LIKE %(search_val)s"
    ]
    for col in style_columns:
        where_clauses.append(f"i.{col} LIKE %(search_val)s")
        
    query = f"""
        SELECT DISTINCT
            i.name as item_code,
            i.item_name,
            COALESCE(i.variant_of, i.name) as style,
            (
                SELECT b.barcode 
                FROM `tabItem Barcode` b 
                WHERE b.parent = i.name 
                ORDER BY b.custom_is_primary DESC, b.creation ASC 
                LIMIT 1
            ) as barcode
        FROM
            `tabItem` i
        LEFT JOIN
            `tabItem Barcode` ib ON ib.parent = i.name
        WHERE
            i.disabled = 0
            AND i.has_variants = 0
            AND ({" OR ".join(where_clauses)})
        LIMIT 20
    """
    
    results = frappe.db.sql(query, {"search_val": search_val}, as_dict=True)
    return results


def _send_to_printer_sync(payload, printer_ip, printer_port=9100):
    import socket
    port = cint(printer_port) or 9100
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((printer_ip.strip(), port))
            s.sendall(payload.encode("utf-8", errors="replace"))
    except socket.timeout:
        frappe.throw(_("Connection timed out. Verify printer IP {0} and port {1} are reachable.").format(printer_ip, port))
    except ConnectionRefusedError:
        frappe.throw(_("Printer at {0}:{1} refused the connection. Ensure the printer is online and raw TCP port is enabled.").format(printer_ip, port))
    except Exception as e:
        frappe.throw(_("Printer error: {0}").format(str(e)))


@frappe.whitelist()
def enqueue_print_job(template_name, printer_ip, printer_port, payload, print_qty=1, labels_count=None, item_code=None, barcode=None):
    import hashlib
    import os
    
    if labels_count is not None:
        print_qty = labels_count

    # Generate unique job ID
    job_id = f"JOB-{frappe.generate_hash(length=12).upper()}"
    
    # Write payload to file
    prn_dir = frappe.get_site_path('private', 'print_jobs')
    os.makedirs(prn_dir, exist_ok=True)
    
    prn_path = os.path.join(prn_dir, f"{job_id}.prn")
    with open(prn_path, 'w', encoding='utf-8') as f:
        f.write(payload)
    os.chmod(prn_path, 0o600)
    
    # Capture request ip and user agent
    request_ip = None
    request_user_agent = None
    try:
        if getattr(frappe.local, "request", None):
            request_ip = frappe.local.ip
            request_user_agent = frappe.local.request.headers.get("User-Agent")
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:1291: {sys.exc_info()[1]}")

    # Create SMRITI Print Job record
    doc = frappe.new_doc("SMRITI Print Job")
    doc.job_id = job_id
    doc.name = job_id
    doc.item_code = item_code
    doc.barcode = barcode
    doc.template_name = template_name
    doc.printer_ip = printer_ip
    doc.printer_port = cint(printer_port) or 9100
    doc.print_qty = cint(print_qty) or 1
    doc.status = "Queued"
    doc.payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    doc.payload_preview = payload[:100]
    doc.created_by = frappe.session.user
    doc.created_on = frappe.utils.now_datetime()
    
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # Log Audit: SMRITI Print Job Queued
    try:
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": doc.created_by,
            "operation": "SMRITI Print Job Queued",
            "status": "Success",
            "subject": f"Print job {job_id} queued",
            "remarks": f"Queued {doc.print_qty} labels for template {doc.template_name}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error logging print job queued: {str(e)}")

    # Publish realtime queued event
    frappe.publish_realtime(
        "smriti.barcode.print_status",
        {
            "event_version": 1,
            "job_id": job_id,
            "status": "Queued"
        },
        user=doc.created_by
    )

    # Enqueue background worker
    frappe.enqueue(
        "smriti_retail_os.barcode_api._process_print_job",
        print_job_id=job_id,
        queue="barcode",
        timeout=30,
        now=frappe.flags.in_test
    )
    
    return {"job_id": job_id, "status": "Queued"}


@frappe.whitelist()
def _process_print_job(job_id=None, print_job_id=None):
    import os
    import hashlib
    
    if job_id is None:
        job_id = print_job_id

    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)
        
    doc = frappe.get_doc("SMRITI Print Job", name)
    doc.status = "Sending"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    # Log Audit: SMRITI Print Job Sending
    try:
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": doc.created_by or "System",
            "operation": "SMRITI Print Job Sending",
            "status": "Success",
            "subject": f"Print job {job_id} is sending",
            "remarks": f"Sending payload to {doc.printer_ip}:{doc.printer_port}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error logging print job sending: {str(e)}")

    # Publish realtime sending event
    frappe.publish_realtime(
        "smriti.barcode.print_status",
        {
            "event_version": 1,
            "job_id": job_id,
            "status": "Sending"
        },
        user=doc.created_by or "Administrator"
    )
    
    prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
    
    try:
        if not os.path.exists(prn_path):
            raise FileNotFoundError(f"Payload file missing for job {job_id}")
            
        # Read payload
        with open(prn_path, "r", encoding="utf-8") as f:
            payload = f.read()
            
        # Verify Payload Integrity
        actual_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        if actual_hash != doc.payload_hash:
            # Log Audit event: SMRITI Visual Template Compilation Failed
            try:
                frappe.get_doc({
                    "doctype": "Activity Log",
                    "user": doc.created_by or "System",
                    "operation": "SMRITI Visual Template Compilation Failed",
                    "status": "Failed",
                    "subject": f"Print job {job_id} integrity mismatch",
                    "remarks": "Expected hash does not match actual PRN file content."
                }).insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as le:
                frappe.log_error(f"Error logging template compilation failed: {str(le)}")
            raise RuntimeError("Print payload integrity validation failed.")
            
        # Print
        _send_to_printer_sync(payload, doc.printer_ip, doc.printer_port)
        
        doc.status = "Success"
        doc.completed_on = frappe.utils.now_datetime()
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # Publish realtime success event
        frappe.publish_realtime(
            "smriti.barcode.print_status",
            {
                "event_version": 1,
                "job_id": job_id,
                "status": "Success"
            },
            user=doc.created_by or "Administrator"
        )

        # Log Success
        log_print_job(doc.template_name, doc.printer_ip, doc.print_qty, 1)
        
        # Log Audit event: SMRITI Print Job Success
        try:
            frappe.get_doc({
                "doctype": "Activity Log",
                "user": doc.created_by or "System",
                "operation": "SMRITI Print Job Success",
                "status": "Success",
                "subject": f"Print job {job_id} printed successfully",
                "remarks": f"Printed {doc.print_qty} labels on {doc.printer_ip}"
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error logging print job success: {str(e)}")

        # Cleanup .prn file after Success
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass
            
    except Exception as e:
        doc.status = "Failed"
        doc.error_message = str(e)
        doc.completed_on = frappe.utils.now_datetime()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Write to Frappe Error Log — visible at /app/error-log for administrators.
        # log_print_job() writes to local file + Activity Log, but not Error Log.
        frappe.log_error(
            title=f"SMRITI Print Job Failed: {job_id}",
            message=f"Printer: {doc.printer_ip}:{doc.printer_port}\nTemplate: {doc.template_name}\nError: {str(e)}"
        )

        # Publish realtime failed event
        frappe.publish_realtime(
            "smriti.barcode.print_status",
            {
                "event_version": 1,
                "job_id": job_id,
                "status": "Failed"
            },
            user=doc.created_by or "Administrator"
        )

        # Log Failure to local file + Activity Log
        log_print_job(doc.template_name, doc.printer_ip, doc.print_qty, 0, error_message=str(e))

        # Log Audit event: SMRITI Print Job Failed
        try:
            frappe.get_doc({
                "doctype": "Activity Log",
                "user": doc.created_by or "System",
                "operation": "SMRITI Print Job Failed",
                "status": "Failed",
                "subject": f"Print job {job_id} failed",
                "remarks": str(e)
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as le:
            frappe.log_error(f"Error logging print job failed: {str(le)}")

        raise e
    finally:
        # always runs cleanup
        pass



@frappe.whitelist()
def get_print_job_status(job_id):
    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)
        
    doc = frappe.get_doc("SMRITI Print Job", name)
    return {
        "status": doc.status,
        "error_message": doc.error_message or "",
        "completed_on": doc.completed_on
    }


@frappe.whitelist()
def retry_print_job(job_id):
    import os
    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)
        
    old_doc = frappe.get_doc("SMRITI Print Job", name)
    old_prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
    if not os.path.exists(old_prn_path):
        frappe.throw(_("Original payload no longer available. Re-print from worksheet."))
        
    with open(old_prn_path, 'r', encoding='utf-8') as f:
        payload = f.read()
        
    res = enqueue_print_job(
        template_name=old_doc.template_name,
        printer_ip=old_doc.printer_ip,
        printer_port=old_doc.printer_port,
        print_qty=old_doc.print_qty,
        payload=payload
    )
    return {"job_id": res["job_id"]}


@frappe.whitelist()
def get_recent_print_jobs(limit=20):
    return frappe.get_all(
        "SMRITI Print Job",
        fields=["job_id", "status", "template_name", "labels_count", "creation", "printer_ip"],
        order_by="creation desc",
        limit=cint(limit) or 20
    )


@frappe.whitelist()
def get_print_template_versions(template_name):
    """
    Returns linked version history for the specified template.
    """
    name_id = frappe.db.get_value("SMRITI Print Template", {"template_title": template_name}, "name") or template_name
    if not frappe.db.exists("SMRITI Print Template", name_id):
        return []
        
    return frappe.get_all(
        "SMRITI Print Template Version",
        filters={"template": name_id},
        fields=["version_number", "version_label", "change_timestamp", "changed_by", "raw_template", "custom_field_mappings_json", "custom_visual_layout_json", "template_checksum", "restored_from_version"],
        order_by="creation desc"
    )


@frappe.whitelist()
def restore_print_template_version(template_name, version_number, expected_checksum):
    """
    Restores template from a specific version.
    Includes optimistic locking to prevent overwriting intermediate changes.
    """
    name_id = frappe.db.get_value("SMRITI Print Template", {"template_title": template_name}, "name") or template_name
    if not frappe.db.exists("SMRITI Print Template", name_id):
        frappe.throw(_("Template {0} not found.").format(template_name))
        
    doc = frappe.get_doc("SMRITI Print Template", name_id)
    
    # Optimistic Lock Check
    if doc.template_checksum != expected_checksum:
        frappe.throw(
            _("Template changed since loaded. Reload before restoring."),
            frappe.ValidationError
        )
        
    v_name = frappe.db.get_value("SMRITI Print Template Version", {"template": name_id, "version_number": version_number}, "name")
    if not v_name:
        frappe.throw(_("Version {0} of template {1} not found.").format(version_number, template_name))
        
    v_doc = frappe.get_doc("SMRITI Print Template Version", v_name)
    
    # Restore content
    doc.raw_template = v_doc.raw_template
    doc.custom_field_mappings_json = v_doc.custom_field_mappings_json
    doc.custom_visual_layout_json = v_doc.custom_visual_layout_json
    
    # Record restored from version
    doc.flags.restored_from_version = version_number
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    # Log Audit event: SMRITI Print Template Version Restored
    try:
        frappe.get_doc({
            "doctype": "Activity Log",
            "user": frappe.session.user,
            "operation": "SMRITI Print Template Version Restored",
            "status": "Success",
            "subject": f"Restored print template {template_name} to version {version_number}",
            "remarks": f"Restored from version {version_number}. New active version: {doc.custom_version}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error logging template version restored: {str(e)}")
        
    return get_print_templates()




def get_barcode_hrt_reserved_height():
    """Helper to fetch barcode_hrt_reserved_height_mm from settings or fallback to 2.5."""
    try:
        if frappe.db.exists("DocType", "SMRITI Barcode Settings"):
            res = frappe.db.sql(
                "SELECT value FROM `tabSingles` WHERE doctype = 'SMRITI Barcode Settings' AND field = 'barcode_hrt_reserved_height_mm'"
            )
            if res and res[0][0] is not None:
                return float(res[0][0])
    except Exception:
        pass
    return 2.5


def get_enforce_printability_threshold():
    """Helper to fetch enforce_printability_threshold from settings or fallback to 1."""
    try:
        if frappe.db.exists("DocType", "SMRITI Barcode Settings"):
            res = frappe.db.sql(
                "SELECT value FROM `tabSingles` WHERE doctype = 'SMRITI Barcode Settings' AND field = 'enforce_printability_threshold'"
            )
            if res and res[0][0] is not None:
                return int(res[0][0])
    except Exception:
        pass
    return 1


def get_printability_formula_config():
    """
    Fetches the printability score configuration dynamically from SMRITI Formula Definition
    cached for performance (TTL = 3600), with fallback to default weights/grade_bands.
    """
    cache_key = "smriti:barcode_printability_formula_config"
    try:
        cached = frappe.cache().get_value(cache_key)
        if cached:
            return cached
    except Exception:
        pass

    config = {
        "weights": {
            "margin": 25,
            "quiet_zone": 25,
            "overflow": 20,
            "density": 15,
            "collision": 15
        },
        "grade_bands": {
            "A+": [95, 100],
            "A": [90, 94],
            "B": [80, 89],
            "C": [70, 79],
            "F": [0, 69]
        },
        "version": "1.0"
    }

    try:
        if frappe.db.exists("SMRITI Formula Definition", {"formula_id": "SMRITI-PRN-SCORE-01"}):
            formula_json = frappe.db.get_value(
                "SMRITI Formula Definition",
                {"formula_id": "SMRITI-PRN-SCORE-01"},
                "explainability_json"
            )
            if formula_json:
                db_cfg = frappe.parse_json(formula_json)
                if db_cfg.get("weights"):
                    config["weights"].update(db_cfg["weights"])
                if db_cfg.get("grade_bands"):
                    config["grade_bands"] = db_cfg["grade_bands"]
                if db_cfg.get("version"):
                    config["version"] = db_cfg["version"]
            else:
                frappe.log_error(
                    title="SMRITI Formula Registry Warning",
                    message="SMRITI Barcode Studio Formula Registry 'SMRITI-PRN-SCORE-01' has empty explainability_json. Using fallback default config."
                )
        else:
            frappe.log_error(
                title="SMRITI Formula Registry Warning",
                message="SMRITI Barcode Studio Formula Registry 'SMRITI-PRN-SCORE-01' missing. Using fallback default config."
            )
    except Exception as e:
        frappe.log_error(
            title="SMRITI Formula Registry Warning",
            message=f"SMRITI Barcode Studio Formula Registry fetch failed: {str(e)}"
        )

    try:
        frappe.cache().set_value(cache_key, config, expires_in_sec=3600)
    except Exception:
        pass
    return config


@frappe.whitelist()
def validate_layout_diagnostics(layout_json, label_size, item_data=None):
    """
    Validates print template layout and returns a dictionary of diagnostics.
    Diagnostics are categorized as 'warning' or 'error'.
    Includes printability score calculation, grade bands, breakdown, and recommendations.
    """
    if not layout_json:
        return {
            "diagnostics": [],
            "errors_count": 0,
            "warnings_count": 0,
            "printability_score": 100.0,
            "grade": "A+",
            "breakdown": {
                "margin": 25,
                "quiet_zone": 25,
                "overflow": 20,
                "density": 15,
                "collision": 15
            },
            "recommendations": []
        }

    import json

    try:
        parsed = json.loads(layout_json)
        if isinstance(parsed, dict) and "elements" in parsed:
            elements = parsed["elements"]
        elif isinstance(parsed, list):
            elements = parsed
        else:
            elements = []
    except Exception:
        elements = []

    try:
        parts = label_size.split('x')
        lw = float(parts[0])
        lh = float(parts[1])
    except Exception:
        lw = 50.0
        lh = 25.0

    reserved_height_mm = get_barcode_hrt_reserved_height()
    formula_cfg = get_printability_formula_config()
    weights = formula_cfg["weights"]
    grade_bands = formula_cfg["grade_bands"]

    diagnostics = []
    recommendations = []

    def resolve_tokens_py(content, item):
        if not content:
            return ""
        if not item:
            item = {}
        tokens = {
            "barcode": item.get("barcode") or "8901234567890",
            "item_code": item.get("item_code") or "ITEM-12345",
            "item_name": item.get("item_name") or "Sample Item Name Description",
            "brand": item.get("brand") or "SMRITI",
            "mrp": str(int(item.get("mrp") or 499)),
            "size": item.get("size") or "8",
            "color": item.get("color") or "BLACK",
            "style": item.get("style") or "STYLE",
            "pkd_date": item.get("pkd_date") or "06/26"
        }
        res = content
        for k, v in tokens.items():
            res = res.replace(f"{{{k}}}", v)
        return res

    SAFE_MARGIN_MM = 1.5
    margin_errors_count = 0
    margin_warnings_count = 0

    QUIET_ZONE_BUFFER = 2.5
    quiet_zone_errors_count = 0
    quiet_zone_warnings_count = 0

    text_overflows_count = 0
    density_warnings_count = 0
    collision_errors_count = 0

    processed_elements = []
    barcodes = []

    for elem in elements:
        try:
            x = float(elem.get("x", 0))
            y = float(elem.get("y", 0))
            w = float(elem.get("w", 0))
            h = float(elem.get("h", 0))
        except Exception:
            continue
        el_type = elem.get("type", "")
        el_id = elem.get("id", "")
        content = elem.get("content", "")

        processed_elem = {
            "id": el_id,
            "type": el_type,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "content": content,
            "format": elem.get("format") or elem.get("barcode_type") or "code128"
        }
        processed_elements.append(processed_elem)

        if el_type == "barcode":
            barcodes.append(processed_elem)

    # 1. Printable bounds & safe margin check
    for elem in processed_elements:
        x, y, w, h = elem["x"], elem["y"], elem["w"], elem["h"]
        el_type, el_id = elem["type"], elem["id"]

        if x < 0 or y < 0 or (x + w) > lw or (y + h) > lh:
            diagnostics.append({
                "element_id": el_id,
                "severity": "error",
                "message": f"Element {el_id or el_type} exceeds printable area ({lw}x{lh}mm)"
            })
            margin_errors_count += 1
            continue

        if x < SAFE_MARGIN_MM or y < SAFE_MARGIN_MM or (x + w) > (lw - SAFE_MARGIN_MM) or (y + h) > (lh - SAFE_MARGIN_MM):
            if el_type in ["barcode", "qrcode"]:
                diagnostics.append({
                    "element_id": el_id,
                    "severity": "error",
                    "message": f"{el_type.upper()} {el_id} overlaps print-safe margin"
                })
                margin_errors_count += 1
            else:
                diagnostics.append({
                    "element_id": el_id,
                    "severity": "warning",
                    "message": f"Element {el_id or el_type} overlaps print-safe margin"
                })
                margin_warnings_count += 1

    # 2. Quiet Zone Buffer & Barcode Density check
    for bc in barcodes:
        bc_format = bc["format"].lower()
        bc_w = bc["w"]
        is_ean_upc = "ean" in bc_format or "upc" in bc_format
        min_rec = 25.0 if is_ean_upc else 15.0
        if bc_w < min_rec:
            diagnostics.append({
                "element_id": bc["id"],
                "severity": "warning",
                "message": f"Barcode {bc['id']} width ({bc_w}mm) is less than recommended minimum ({min_rec}mm) for {bc['format']}"
            })
            density_warnings_count += 1

        ax, ay, aw, ah = bc["x"], bc["y"], bc["w"], bc["h"]
        q_x = ax - QUIET_ZONE_BUFFER
        q_w = aw + 2 * QUIET_ZONE_BUFFER

        for other in processed_elements:
            if other["id"] == bc["id"]:
                continue
            ox, oy, ow, oh = other["x"], other["y"], other["w"], other["h"]

            # AABB intersection on inflated quiet zone bounding box
            if (q_x < ox + ow) and (q_x + q_w > ox) and (ay < oy + oh) and (ay + ah > oy):
                is_decor = other["type"] in ["box", "bar"]
                is_main_overlap = (ax < ox + ow) and (ax + aw > ox) and (ay < oy + oh) and (ay + ah > oy)
                if not is_main_overlap:
                    if is_decor:
                        diagnostics.append({
                            "element_id": f"{bc['id']}<->{other['id']}",
                            "severity": "warning",
                            "message": f"Decorative element {other['id']} invades quiet zone buffer of barcode {bc['id']}"
                        })
                        quiet_zone_warnings_count += 1
                    else:
                        diagnostics.append({
                            "element_id": f"{bc['id']}<->{other['id']}",
                            "severity": "error",
                            "message": f"Non-decorative element {other['id']} encroaches on quiet zone buffer of barcode {bc['id']}"
                        })
                        quiet_zone_errors_count += 1

    # 3. Text Overflow check
    for elem in processed_elements:
        if elem["type"] == "text":
            resolved = resolve_tokens_py(elem["content"], item_data)
            char_width_mm = 1.8
            est_width = len(resolved) * char_width_mm
            if est_width > elem["w"]:
                diagnostics.append({
                    "element_id": elem["id"],
                    "severity": "warning",
                    "message": f"Text element {elem['id']} content may overflow designed width"
                })
                text_overflows_count += 1

    # 4. Collision check (Main + Virtual HRT)
    non_decorative = [e for e in processed_elements if e["type"] not in ["box", "bar"]]
    for i in range(len(non_decorative)):
        for j in range(i + 1, len(non_decorative)):
            a = non_decorative[i]
            b = non_decorative[j]
            ax, ay, aw, ah = a["x"], a["y"], a["w"], a["h"]
            bx, by, bw, bh = b["x"], b["y"], b["w"], b["h"]

            if (ax < bx + bw) and (ax + aw > bx) and (ay < by + bh) and (ay + ah > by):
                diagnostics.append({
                    "element_id": f"{a['id']}<->{b['id']}",
                    "severity": "error",
                    "message": f"Element collision detected between {a['id'] or a['type']} and {b['id'] or b['type']}"
                })
                collision_errors_count += 1

    for bc in barcodes:
        bx, by, bw, bh = bc["x"], bc["y"], bc["w"], bc["h"]
        vx, vy, vw, vh = bx, by + bh, bw, reserved_height_mm

        if vy + vh > lh:
            diagnostics.append({
                "element_id": bc["id"],
                "severity": "warning",
                "message": f"Virtual HRT area for barcode {bc['id']} exceeds label printable height ({lh}mm)"
            })

        for other in non_decorative:
            if other["id"] == bc["id"]:
                continue
            ox, oy, ow, oh = other["x"], other["y"], other["w"], other["h"]

            if (vx < ox + ow) and (vx + vw > ox) and (vy < oy + oh) and (vy + vh > oy):
                diagnostics.append({
                    "element_id": f"{bc['id']}_hrt<->{other['id']}",
                    "severity": "error",
                    "message": f"Element {other['id']} overlaps virtual HRT reserved space of barcode {bc['id']}"
                })
                collision_errors_count += 1

    # Calculate Printability Score
    margin_score = max(0, weights["margin"] - (margin_errors_count * 10) - (margin_warnings_count * 5))

    quiet_zone_score = weights["quiet_zone"]
    if quiet_zone_errors_count > 0:
        quiet_zone_score = 0
    else:
        quiet_zone_score = max(0, quiet_zone_score - (quiet_zone_warnings_count * 5))

    overflow_score = max(0, weights["overflow"] - (text_overflows_count * 5))
    density_score = max(0, weights["density"] - (density_warnings_count * 5))

    collision_score = weights["collision"]
    if collision_errors_count > 0:
        collision_score = 0

    total_score = float(margin_score + quiet_zone_score + overflow_score + density_score + collision_score)

    grade = "F"
    try:
        # Sort grade bands by min value descending to find the correct band cleanly
        sorted_bands = sorted(grade_bands.items(), key=lambda x: x[1][0], reverse=True)
        for g_name, range_val in sorted_bands:
            if total_score >= range_val[0]:
                grade = g_name
                break
    except Exception:
        pass

    if margin_errors_count > 0 or margin_warnings_count > 0:
        recommendations.append("Adjust layout elements to stay within print safe margins (1.5mm inset).")
    if quiet_zone_errors_count > 0 or quiet_zone_warnings_count > 0:
        recommendations.append("Ensure left and right barcode quiet zones (2.5mm buffer) are free of overlaps.")
    if text_overflows_count > 0:
        recommendations.append("Reduce text font size or increase text field width to prevent content overflow.")
    if density_warnings_count > 0:
        recommendations.append("Increase barcode width to meet minimum density scanning standards.")
    if collision_errors_count > 0:
        recommendations.append("Reposition overlapping design elements and keep the barcode HRT space clear.")

    errors_count = sum(1 for d in diagnostics if d["severity"] == "error")
    warnings_count = sum(1 for d in diagnostics if d["severity"] == "warning")

    return {
        "diagnostics": diagnostics,
        "errors_count": errors_count,
        "warnings_count": warnings_count,
        "printability_score": total_score,
        "grade": grade,
        "breakdown": {
            "margin": margin_score,
            "quiet_zone": quiet_zone_score,
            "overflow": overflow_score,
            "density": density_score,
            "collision": collision_score
        },
        "recommendations": recommendations
    }


@frappe.whitelist()
def cleanup_old_print_jobs():
    """
    Success jobs older than 30 days → delete
    Failed jobs older than 90 days → delete .prn + record
    Log audit event with counts
    Wrap in try/except — never raise
    """
    try:
        from frappe.utils import add_days, now_datetime
        import os
        
        success_cutoff = add_days(now_datetime(), -30)
        failed_cutoff = add_days(now_datetime(), -90)
        
        # 1. Success jobs older than 30 days -> delete record
        success_jobs = frappe.get_all(
            "SMRITI Print Job",
            filters={
                "status": "Success",
                "completed_on": ["<", success_cutoff]
            },
            fields=["name", "job_id"]
        )
        
        success_deleted = 0
        for job in success_jobs:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{job.job_id}.prn")
            if os.path.exists(prn_path):
                try:
                    os.remove(prn_path)
                except Exception:
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:1833: {sys.exc_info()[1]}")
            frappe.delete_doc("SMRITI Print Job", job.name, ignore_permissions=True)
            success_deleted += 1
            
        # 2. Failed jobs older than 90 days -> delete .prn + record
        failed_jobs = frappe.get_all(
            "SMRITI Print Job",
            filters={
                "status": "Failed",
                "completed_on": ["<", failed_cutoff]
            },
            fields=["name", "job_id"]
        )
        
        failed_deleted = 0
        for job in failed_jobs:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{job.job_id}.prn")
            if os.path.exists(prn_path):
                try:
                    os.remove(prn_path)
                except Exception:
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in barcode_api.py:1854: {sys.exc_info()[1]}")
            frappe.delete_doc("SMRITI Print Job", job.name, ignore_permissions=True)
            failed_deleted += 1
            
        if success_deleted or failed_deleted:
            frappe.db.commit()
            
        from smriti_retail_os.backup_api import log_audit_event
        log_audit_event(
            "SMRITI Print Job Cleanup",
            f"Cleaned up {success_deleted} success jobs (>30d) and {failed_deleted} failed jobs (>90d)."
        )
    except Exception as e:
        frappe.log_error(title="SMRITI Print Job Cleanup Error", message=str(e))


def enforce_barcode_scan_event_immutability(doc, method=None):
    """
    Enforces that SMRITI Barcode Scan Event records are read-only after creation.
    Only allows new record insertion.
    """
    if not doc.is_new():
        frappe.throw(frappe.ValidationError("SMRITI Barcode Scan Event records are immutable and cannot be updated."))


@frappe.whitelist()
def get_barcode_feature_flags():
    """
    Returns SMRITI Barcode telemetry and learning feature flags.
    If the settings DocType is missing, returns all False (fail-safe principle).
    Uses caching (TTL = 3600) for performance.
    """
    cache_key = "smriti:barcode_feature_flags"
    try:
        cached = frappe.cache().get_value(cache_key)
        if cached is not None:
            return cached
    except Exception:
        pass

    flags = {
        "capture": False,
        "aggregation": False,
        "learning": False
    }

    try:
        if frappe.db.exists("DocType", "SMRITI Barcode Settings") and frappe.db.exists("SMRITI Barcode Settings", "SMRITI Barcode Settings"):
            capture = frappe.db.get_single_value("SMRITI Barcode Settings", "barcode_telemetry_capture_enabled")
            aggregation = frappe.db.get_single_value("SMRITI Barcode Settings", "barcode_telemetry_aggregation_enabled")
            learning = frappe.db.get_single_value("SMRITI Barcode Settings", "barcode_learning_enabled")
            
            flags["capture"] = bool(cint(capture)) if capture is not None else False
            flags["aggregation"] = bool(cint(aggregation)) if aggregation is not None else False
            flags["learning"] = bool(cint(learning)) if learning is not None else False
    except Exception:
        pass

    try:
        frappe.cache().set_value(cache_key, flags, expires_in_sec=3600)
    except Exception:
        pass

    return flags


def clear_barcode_feature_flags_cache(doc=None, method=None):
    """Clears cached SMRITI Barcode feature flags."""
    try:
        frappe.cache().delete_value("smriti:barcode_feature_flags")
    except Exception:
        pass


@frappe.whitelist()
def log_barcode_scan_event(event_uuid, template_id, barcode_family, printer_profile, scan_method, scan_attempts, scan_success, first_pass_success, store_id=None, pos_invoice=None, pos_invoice_item=None):
    """
    Logs a barcode scan telemetry event. Restricted to users with System Manager, SMRITI POS User, or POS User roles.
    Checks barcode_telemetry_capture_enabled feature flag before logging.
    """
    # Check feature flags first
    flags = get_barcode_feature_flags()
    if not flags.get("capture"):
        return {"status": "disabled", "message": "Barcode telemetry capture is disabled"}

    # 1. Access/Role Verification
    roles = frappe.get_roles(frappe.session.user)
    authorized_roles = {"System Manager", "SMRITI POS User", "POS User", "SMRITI Store Manager", "SMRITI Cashier"}
    if not authorized_roles.intersection(set(roles)):
        frappe.throw(frappe._("Not authorized to log telemetry events."), frappe.PermissionError)

    # 2. Idempotency Check
    existing = frappe.db.get_value("SMRITI Barcode Scan Event", {"event_uuid": event_uuid}, "name")
    if existing:
        return frappe.get_doc("SMRITI Barcode Scan Event", existing)

    # 3. Determine Governance Event ID
    scan_attempts = int(scan_attempts)
    scan_success = int(scan_success)
    first_pass_success = int(first_pass_success)

    if scan_success == 1 and first_pass_success == 1:
        gov_id = "SCAN-EVT-001"
    elif scan_success == 1 and first_pass_success == 0:
        gov_id = "SCAN-EVT-002"
    else:
        gov_id = "SCAN-EVT-003"

    # Default store_id if not provided: retrieve first available non-group warehouse as fallback
    if not store_id:
        store_id = frappe.db.get_value("Warehouse", {"is_group": 0, "disabled": 0}, "name")

    if not store_id:
        frappe.throw(frappe.ValidationError("A valid Store (Warehouse) is required to log telemetry."))

    # 4. Insert raw SMRITI Barcode Scan Event doc
    doc = frappe.get_doc({
        "doctype": "SMRITI Barcode Scan Event",
        "event_uuid": event_uuid,
        "timestamp": frappe.utils.now_datetime(),
        "store_id": store_id,
        "template_id": template_id,
        "barcode_family": barcode_family,
        "printer_profile": printer_profile,
        "scan_method": scan_method,
        "scan_attempts": scan_attempts,
        "scan_success": scan_success,
        "first_pass_success": first_pass_success,
        "governance_event_id": gov_id,
        "pos_invoice": pos_invoice,
        "pos_invoice_item": pos_invoice_item
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc



def delete_expired_scan_events():
    """
    Scheduler task to prune raw telemetry events older than 90 days.
    """
    from frappe.utils import add_days, now_datetime
    cutoff = add_days(now_datetime(), -90)
    
    expired_events = frappe.db.sql("""
        SELECT name FROM `tabSMRITI Barcode Scan Event`
        WHERE timestamp < %(cutoff)s
    """, {"cutoff": cutoff}, as_dict=True)

    count = 0
    for ev in expired_events:
        frappe.delete_doc("SMRITI Barcode Scan Event", ev["name"], ignore_permissions=True)
        count += 1

    if count > 0:
        frappe.db.commit()
        from smriti_retail_os.backup_api import log_audit_event
        log_audit_event(
            "SMRITI Telemetry Cleanup",
            f"Pruned {count} raw scan events older than 90 days."
        )
        print(f"[SMRITI Telemetry] Pruned {count} raw scan events older than 90 days.")


@frappe.whitelist()
def aggregate_scan_telemetry(period="Daily", target_date=None):
    """
    Aggregates raw scan events and calculates Scan Reliability Scores.
    Default period is Daily, aggregating the previous calendar day.
    Checks barcode_telemetry_aggregation_enabled feature flag.
    """
    flags = get_barcode_feature_flags()
    if not flags.get("aggregation"):
        print("[SMRITI Telemetry] Aggregation is disabled in SMRITI Barcode Settings.")
        return

    from frappe.utils import add_days, getdate, flt

    
    if not target_date:
        target_date = add_days(getdate(), -1)
    else:
        target_date = getdate(target_date)

    data = frappe.db.sql("""
        SELECT
            store_id,
            template_id,
            barcode_family,
            printer_profile,
            COUNT(name) as total_scans,
            SUM(CASE WHEN scan_success = 1 THEN 1 ELSE 0 END) as total_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-001' THEN 1 ELSE 0 END) as first_pass_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-002' THEN 1 ELSE 0 END) as retry_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-003' THEN 1 ELSE 0 END) as failures
        FROM
            `tabSMRITI Barcode Scan Event`
        WHERE
            DATE(timestamp) = %(target_date)s
        GROUP BY
            store_id, template_id, barcode_family, printer_profile
    """, {"target_date": target_date}, as_dict=True)

    for row in data:
        total = int(row["total_scans"])
        first_pass = int(row["first_pass_successes"])
        retries = int(row["retry_successes"])
        failures = int(row["failures"])

        if total > 0:
            reliability_score = flt(((first_pass + 0.5 * retries) / total) * 100, 2)
            first_pass_rate = flt(first_pass / total, 4)
        else:
            reliability_score = 0.0
            first_pass_rate = 0.0

        filters = {
            "snapshot_date": target_date,
            "period": period,
            "store_id": row["store_id"],
            "template_id": row["template_id"],
            "barcode_family": row["barcode_family"],
            "printer_profile": row["printer_profile"]
        }

        existing_name = frappe.db.get_value("SMRITI Barcode Telemetry Snapshot", filters, "name")
        if existing_name:
            snapshot = frappe.get_doc("SMRITI Barcode Telemetry Snapshot", existing_name)
        else:
            snapshot = frappe.new_doc("SMRITI Barcode Telemetry Snapshot")
            snapshot.update(filters)

        snapshot.total_scans = total
        snapshot.total_successes = int(row["total_successes"])
        snapshot.first_pass_successes = first_pass
        snapshot.retry_successes = retries
        snapshot.failures = failures
        snapshot.scan_reliability_score = reliability_score
        snapshot.first_pass_success_rate = first_pass_rate
        
        snapshot.save(ignore_permissions=True)

    frappe.db.commit()
    print(f"[SMRITI Telemetry] Completed aggregation for {target_date} ({len(data)} records).")




