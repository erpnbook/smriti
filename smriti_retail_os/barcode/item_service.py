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
import frappe
from frappe.utils import flt, cint
from frappe import _


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
        has_barcode = frappe.db.exists("Item Barcode", {"parent": it.item_code})
        creation = frappe.db.get_value("Item", it.item_code, "creation")
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
        items = frappe.db.get_all(
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


def get_items_for_printing(filters=None, source_doctype=None, source_name=None):
    """
    Loads items for barcode printing based on either a transaction source
    (Purchase Receipt or Stock Entry) or manual filter selection.
    """
    items = []

    if source_doctype and source_name:
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
        flt_dict = frappe.parse_json(filters)
        db_filters = {"disabled": 0}

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

        if flt_dict.get("season"):
            season_val = flt_dict.get("season")
            if frappe.db.has_column("Item", "custom_season"):
                db_filters["custom_season"] = season_val
            else:
                items_with_season = frappe.get_all(
                    "Item Variant Attribute",
                    filters={"attribute": ["like", "%season%"], "attribute_value": season_val},
                    fields=["parent"]
                )
                db_filters["name"] = ["in", [i.parent for i in items_with_season]]

        if flt_dict.get("collection"):
            collection_val = flt_dict.get("collection")
            if frappe.db.has_column("Item", "custom_collection"):
                db_filters["custom_collection"] = collection_val
            else:
                items_with_collection = frappe.get_all(
                    "Item Variant Attribute",
                    filters={"attribute": ["like", "%collection%"], "attribute_value": collection_val},
                    fields=["parent"]
                )
                if "name" in db_filters and isinstance(db_filters["name"], list) and db_filters["name"][0] == "in":
                    db_filters["name"][1] = list(set(db_filters["name"][1]) & set([i.parent for i in items_with_collection]))
                else:
                    db_filters["name"] = ["in", [i.parent for i in items_with_collection]]

        if flt_dict.get("supplier"):
            supplier = flt_dict.get("supplier")
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

    # 1. Barcode — primary flag first, then first, then item_code
    barcodes_list = frappe.db.get_all(
        "Item Barcode",
        filters={"parent": item_code},
        fields=["barcode", "custom_is_primary"],
        order_by="custom_is_primary desc, creation asc"
    )
    barcode = item_code
    if barcodes_list:
        barcode = barcodes_list[0].barcode

    # 2. MRP — custom_mrp > MRP price list > Standard Selling > valuation_rate
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

    # 5. Style resolution: variant_of > custom_style_code > style_no > SKU prefix
    style = item_doc.get("variant_of") or ""
    if not style and item_doc.meta.has_field("custom_style_code"):
        style = item_doc.get("custom_style_code") or ""
    if not style and item_doc.meta.has_field("style_no"):
        style = item_doc.get("style_no") or ""
    if not style:
        style = item_code.split("-")[0] if "-" in item_code else item_code

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
