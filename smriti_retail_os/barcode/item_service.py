# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/item_service.py
# @description: Item loading and resolution service for SMRITI Label Studio.
#               Handles item lookup, variant expansion, transaction-based loading,
#               and resolution of all item fields needed for label printing.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import datetime
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import flt, cint
from frappe import _
from smriti_retail_os import smriti


def expand_item_variants(item_code, default_print_qty=1):
    """
    Checks if item has variants. If yes, returns list of print details for all
    non-disabled variants. If no, returns list with print details for the item itself.
    """
    has_variants = smriti.db.get("Item", item_code, "has_variants")
    if has_variants:
        variants = smriti.db.get_list(
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


def get_transaction_items_checklist(source_doctype, source_name):
    """
    Returns all items in the specified Purchase Receipt or Stock Entry transaction
    to populate the frontend checklist modal.
    """
    if source_doctype not in ["Purchase Receipt", "Stock Entry"]:
        return []

    if not smriti.db.exists(source_doctype, source_name):
        return []

    items = []
    doc = smriti.documents.get(source_doctype, source_name)

    for it in doc.items:
        has_barcode = smriti.db.exists("Item Barcode", {"parent": it.item_code})
        creation = smriti.db.get("Item", it.item_code, "creation")
        is_new = False
        if creation:
            from frappe.utils import add_days, now_datetime
            is_new = creation >= add_days(now_datetime(), -30)

        items.append({
            "item_code":   it.item_code,
            "item_name":   it.item_name or "",
            "qty":         flt(it.qty),
            "has_barcode": bool(has_barcode),
            "is_new":      is_new
        })

    return items


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
        match = re.match(r'^([a-zA-Z0-9\-]+?\-)(\d+)$', article)
        if match:
            return match.group(1), int(match.group(2)), len(match.group(2))
        return None, None, None

    prefix_from, num_from, len_from = parse_prefix_num(from_article)
    prefix_to, num_to, len_to = parse_prefix_num(to_article)

    item_codes = []
    if prefix_from and prefix_to and prefix_from == prefix_to:
        lower = min(num_from, num_to)
        upper = max(num_from, num_to)
        items = smriti.db.get_list(
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
        items = smriti.db.get_list(
            "Item",
            filters={"item_code": [">=", from_article], "disabled": 0},
            fields=["name"],
            order_by="item_code asc"
        )
        for item in items:
            if item.name <= to_article:
                item_codes.append(item.name)
            else:
                break

    res_items = []
    for code in item_codes:
        res_items.extend(expand_item_variants(code, 1))

    return res_items


def get_items_by_barcode_range(from_barcode, to_barcode):
    """
    Returns items matching the specified Barcode range.
    Supports numerical range filtering (e.g. 89012340001 to 89012340100) or lexicographical range.
    """
    if not from_barcode or not to_barcode:
        return []

    from_barcode = from_barcode.strip()
    to_barcode = to_barcode.strip()

    import re
    def parse_prefix_num(bc):
        match = re.match(r'^([a-zA-Z0-9\-]*?)(\d+)$', bc)
        if match:
            return match.group(1), int(match.group(2))
        return None, None

    p_from, n_from = parse_prefix_num(from_barcode)
    p_to, n_to = parse_prefix_num(to_barcode)

    matching_parents = set()

    if p_from is not None and p_to is not None and p_from == p_to:
        lower = min(n_from, n_to)
        upper = max(n_from, n_to)
        barcodes = smriti.db.get_list(
            "Item Barcode",
            filters={"barcode": ["like", f"{p_from}%"]},
            fields=["barcode", "parent"]
        )
        for b in barcodes:
            suffix = b.barcode[len(p_from):]
            if suffix.isdigit():
                val = int(suffix)
                if lower <= val <= upper:
                    matching_parents.add(b.parent)
    else:
        barcodes = smriti.db.get_list(
            "Item Barcode",
            filters={"barcode": [">=", from_barcode]},
            fields=["barcode", "parent"],
            order_by="barcode asc"
        )
        for b in barcodes:
            if b.barcode <= to_barcode:
                matching_parents.add(b.parent)
            else:
                break

    res_items = []
    for code in list(matching_parents):
        res_items.extend(expand_item_variants(code, 1))

    return res_items


def get_items_for_printing(filters=None, source_doctype=None, source_name=None):
    """
    Loads items for barcode printing based on either a transaction source
    (Purchase Receipt or Stock Entry) or manual filter selection.
    """
    items = []

    if source_doctype and source_name:
        if source_doctype == "Purchase Receipt":
            if not smriti.db.exists("Purchase Receipt", source_name):
                frappe.throw(_("Purchase Receipt {0} not found.").format(source_name))
            pr = smriti.documents.get("Purchase Receipt", source_name)
            for it in pr.items:
                items.extend(expand_item_variants(it.item_code, it.qty))

        elif source_doctype == "Stock Entry":
            if not smriti.db.exists("Stock Entry", source_name):
                frappe.throw(_("Stock Entry {0} not found.").format(source_name))
            se = smriti.documents.get("Stock Entry", source_name)
            for it in se.items:
                items.extend(expand_item_variants(it.item_code, it.qty))

    elif filters:
        flt_dict = frappe.parse_json(filters)
        db_filters = {"disabled": 0}

        # Check for Barcode Range filter first
        if flt_dict.get("from_barcode") and flt_dict.get("to_barcode"):
            return get_items_by_barcode_range(flt_dict.get("from_barcode"), flt_dict.get("to_barcode"))

        if flt_dict.get("brand"):
            db_filters["brand"] = flt_dict.get("brand")
        if flt_dict.get("item_group"):
            db_filters["item_group"] = flt_dict.get("item_group")
        if flt_dict.get("custom_barcode_size"):
            db_filters["custom_barcode_size"] = flt_dict.get("custom_barcode_size")
        if flt_dict.get("department"):
            db_filters["custom_department"] = flt_dict.get("department")
        if flt_dict.get("gender"):
            db_filters["custom_gender"] = flt_dict.get("gender")
        if flt_dict.get("purchase_class") and frappe.db.has_column("Item", "custom_purchase_class"):
            db_filters["custom_purchase_class"] = flt_dict.get("purchase_class")
        if flt_dict.get("merchandise_category") and frappe.db.has_column("Item", "custom_merchandise_category"):
            db_filters["custom_merchandise_category"] = flt_dict.get("merchandise_category")
        if flt_dict.get("sub_category") and frappe.db.has_column("Item", "custom_sub_category"):
            db_filters["custom_sub_category"] = flt_dict.get("sub_category")
        if flt_dict.get("upper_material") and frappe.db.has_column("Item", "custom_upper_material"):
            db_filters["custom_upper_material"] = flt_dict.get("upper_material")
        if flt_dict.get("outsole") and frappe.db.has_column("Item", "custom_outsole"):
            db_filters["custom_outsole"] = flt_dict.get("outsole")
        if flt_dict.get("heel_type") and frappe.db.has_column("Item", "custom_heel_type"):
            db_filters["custom_heel_type"] = flt_dict.get("heel_type")

        if flt_dict.get("season"):
            season_val = flt_dict.get("season")
            if frappe.db.has_column("Item", "custom_season"):
                db_filters["custom_season"] = season_val
            else:
                items_with_season = smriti.db.get_list(
                    "Item Variant Attribute",
                    filters={"attribute": ["like", "%season%"], "attribute_value": season_val},
                    fields=["parent"]
                )
                season_parents = [i.get("parent") if isinstance(i, dict) else getattr(i, "parent", None) for i in items_with_season]
                db_filters["name"] = ["in", [p for p in season_parents if p]]

        if flt_dict.get("collection"):
            collection_val = flt_dict.get("collection")
            if frappe.db.has_column("Item", "custom_collection"):
                db_filters["custom_collection"] = collection_val
            else:
                items_with_collection = smriti.db.get_list(
                    "Item Variant Attribute",
                    filters={"attribute": ["like", "%collection%"], "attribute_value": collection_val},
                    fields=["parent"]
                )
                coll_parents = [i.get("parent") if isinstance(i, dict) else getattr(i, "parent", None) for i in items_with_collection]
                coll_parents = [p for p in coll_parents if p]
                if "name" in db_filters and isinstance(db_filters["name"], list) and db_filters["name"][0] == "in":
                    db_filters["name"][1] = list(set(db_filters["name"][1]) & set(coll_parents))
                else:
                    db_filters["name"] = ["in", coll_parents]

        if flt_dict.get("supplier"):
            supplier = flt_dict.get("supplier")
            item_list = smriti.db.get_list(
                "Item Supplier",
                filters={"supplier": supplier},
                fields=["parent"]
            )
            item_codes = [i.get("parent") if isinstance(i, dict) else getattr(i, "parent", None) for i in item_list]
            item_codes = [p for p in item_codes if p]
            if "name" in db_filters and isinstance(db_filters["name"], list) and db_filters["name"][0] == "in":
                db_filters["name"][1] = list(set(db_filters["name"][1]) & set(item_codes))
            else:
                db_filters["name"] = ["in", item_codes]

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

        item_list = smriti.db.get_list(
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
    item_doc = smriti.documents.get("Item", item_code)

    # 1. Barcode — primary flag first, then first, then auto-generate EAN-13
    barcodes_list = smriti.db.get_list(
        "Item Barcode",
        filters={"parent": item_code},
        fields=["barcode", "custom_is_primary"],
        order_by="custom_is_primary desc, creation asc"
    )
    barcode = None
    if barcodes_list and barcodes_list[0].get("barcode"):
        barcode = barcodes_list[0].get("barcode")

    if not barcode:
        from smriti_retail_os.item_master_api import generate_ean13_barcode
        try:
            gen_barcode = generate_ean13_barcode()
            for b in item_doc.barcodes:
                b.custom_is_primary = 0

            item_doc.append("barcodes", {
                "barcode": gen_barcode,
                "uom": "Nos",
                "custom_is_primary": 1
            })
            item_doc.save(ignore_permissions=True)
            smriti.db.commit()
            barcode = gen_barcode
        except Exception:
            barcode = item_code



    # 2. MRP — custom_mrp > MRP price list > Standard Selling > valuation_rate
    mrp = (
        item_doc.get("custom_mrp")
        or smriti.db.get("Item Price", {"item_code": item_code, "price_list": "MRP"}, "price_list_rate")
        or smriti.db.get("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate")
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

    # 5. Style resolution: custom_style_code > variant_of > style_no > item_code
    #    custom_style_code is the actual Article/Style from import (e.g. CH-01-A)
    style = ""
    if item_doc.meta.has_field("custom_style_code"):
        style = item_doc.get("custom_style_code") or ""
    if not style:
        style = item_doc.get("variant_of") or ""
    if not style and item_doc.meta.has_field("style_no"):
        style = item_doc.get("style_no") or ""
    if not style:
        style = item_code

    style_code = (
        item_doc.get("custom_style_code")
        or item_doc.get("style_no")
        or ""
    )
    variant_template = item_doc.get("variant_of") or ""

    # 6. Packing Date
    pkd_date = datetime.datetime.now().strftime("%m/%y")

    # 7. Pack Size
    pack_size = None
    if item_doc.meta.has_field("custom_pack_size"):
        pack_size = item_doc.get("custom_pack_size")
    elif item_doc.meta.has_field("custom_carton_size"):
        pack_size = item_doc.get("custom_carton_size")

    return {
        "item_code":             item_doc.name,
        "item_name":             item_doc.item_name or "",
        "brand":                 item_doc.brand or "SMRITI",
        "item_group":            item_doc.item_group or "",
        "barcode":               barcode,
        "mrp":                   flt(mrp),
        "size":                  size,
        "color":                 color,
        "style":                 style,
        "style_code":            style_code,
        "variant_template":      variant_template,
        "pkd_date":              pkd_date,
        "pack_size":             flt(pack_size) if pack_size else None,
        "gender":                item_doc.get("custom_gender") or "",
        "heel_type":             item_doc.get("custom_heel_type") or "",
        "outsole":               item_doc.get("custom_outsole") or "",
        "upper_material":        item_doc.get("custom_upper_material") or "",
        "merchandise_category":  item_doc.get("custom_merchandise_category") or "",
        "sub_category":          item_doc.get("custom_sub_category") or "",
        "purchase_class":        item_doc.get("custom_purchase_class") or "",
        "print_qty":             cint(default_print_qty) or 1,
        "label_size":            item_doc.get("custom_barcode_size") or "50x25"
    }


def load_items_from_csv_or_text(csv_text, delimiter=",", barcode_col=0, qty_col=1, price_col=None):
    """
    Parses CSV / Delimited Raw Text containing barcode numbers / item codes and quantities,
    looks up matching items in DB, and returns label details list.
    """
    if not csv_text or not str(csv_text).strip():
        return []

    lines = [l.strip() for l in str(csv_text).strip().splitlines() if l.strip()]
    if not lines:
        return []

    # Select first non-comment line for delimiter auto-detection
    sample_line = lines[0]
    for l in lines:
        if not l.startswith("#"):
            sample_line = l
            break

    if delimiter == "auto" or not delimiter:
        if "\t" in sample_line:
            delimiter = "\t"
        elif ";" in sample_line:
            delimiter = ";"
        elif "|" in sample_line:
            delimiter = "|"
        else:
            delimiter = ","

    parsed_entries = []
    has_header = False

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        parts = [p.strip().strip('"\'') for p in line_str.split(delimiter)]
        if not parts or not any(parts):
            continue

        if idx == 0:
            lower_parts = [p.lower() for p in parts]
            if any(k in lower_parts for k in ["barcode", "item_code", "code", "qty", "quantity", "mrp", "price"]):
                has_header = True
                if "barcode" in lower_parts:
                    barcode_col = lower_parts.index("barcode")
                elif "item_code" in lower_parts:
                    barcode_col = lower_parts.index("item_code")
                elif "code" in lower_parts:
                    barcode_col = lower_parts.index("code")

                if "qty" in lower_parts:
                    qty_col = lower_parts.index("qty")
                elif "quantity" in lower_parts:
                    qty_col = lower_parts.index("quantity")

                if "mrp" in lower_parts:
                    price_col = lower_parts.index("mrp")
                elif "price" in lower_parts:
                    price_col = lower_parts.index("price")
                continue

        b_col = int(barcode_col) if str(barcode_col).isdigit() else 0
        if b_col >= len(parts):
            continue
        bc = parts[b_col]
        if not bc:
            continue

        q_col = int(qty_col) if str(qty_col).isdigit() else 1
        qty_val = 1
        if q_col < len(parts):
            try:
                qty_val = cint(parts[q_col]) or 1
            except Exception:
                qty_val = 1

        mrp_override = None
        if price_col is not None:
            p_col = int(price_col) if str(price_col).isdigit() else None
            if p_col is not None and p_col < len(parts):
                try:
                    mrp_override = flt(parts[p_col])
                except Exception:
                    mrp_override = None

        parsed_entries.append({
            "barcode": bc,
            "qty": max(1, qty_val),
            "mrp": mrp_override
        })

    res_items = []
    for entry in parsed_entries:
        bc = entry["barcode"]
        qty = entry["qty"]
        mrp_override = entry["mrp"]

        item_code = None
        barcode_rec = smriti.db.get("Item Barcode", {"barcode": bc}, "parent")
        if barcode_rec:
            item_code = barcode_rec
        elif smriti.db.exists("Item", bc):
            item_code = bc

        if item_code:
            item_details_list = expand_item_variants(item_code, qty)
            for it in item_details_list:
                it["barcode"] = bc
                if mrp_override is not None and mrp_override > 0:
                    it["mrp"] = mrp_override
                res_items.append(it)
        else:
            res_items.append({
                "item_code": bc,
                "item_name": f"Item {bc}",
                "brand": "SMRITI",
                "item_group": "General",
                "barcode": bc,
                "mrp": mrp_override or 0,
                "size": "-",
                "color": "-",
                "style": bc,
                "style_code": bc,
                "variant_template": "",
                "pkd_date": datetime.date.today().strftime("%m/%y"),
                "pack_size": None,
                "gender": "",
                "heel_type": "",
                "outsole": "",
                "upper_material": "",
                "merchandise_category": "",
                "sub_category": "",
                "purchase_class": "",
                "print_qty": qty,
                "label_size": "50x25"
            })

    return res_items
