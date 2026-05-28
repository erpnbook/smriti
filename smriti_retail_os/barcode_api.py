# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode_api.py
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

@frappe.whitelist()
def get_barcode_filters():
    """
    Returns available brands, categories, and custom barcode sizes
    to populate filters on the printing interface.
    """
    brands = [b.name for b in frappe.get_all("Brand", fields=["name"], order_by="name asc")]
    categories = [ig.name for ig in frappe.get_all("Item Group", fields=["name"], order_by="name asc")]
    sizes = ["50x25", "50x30", "75x50", "100x50", "106x55"]
    return {
        "brands": brands,
        "categories": categories,
        "sizes": sizes
    }

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
                items.append(get_item_print_details(it.item_code, it.qty))

        elif source_doctype == "Stock Entry":
            if not frappe.db.exists("Stock Entry", source_name):
                frappe.throw(_("Stock Entry {0} not found.").format(source_name))
            
            se = frappe.get_doc("Stock Entry", source_name)
            for it in se.items:
                items.append(get_item_print_details(it.item_code, it.qty))
                
    elif filters:
        # Manual bulk filter mode
        flt_dict = frappe.parse_json(filters)
        db_filters = {"disabled": 0, "custom_is_retail_item": 1}
        
        if flt_dict.get("brand"):
            db_filters["brand"] = flt_dict.get("brand")
        if flt_dict.get("item_group"):
            db_filters["item_group"] = flt_dict.get("item_group")
        if flt_dict.get("custom_barcode_size"):
            db_filters["custom_barcode_size"] = flt_dict.get("custom_barcode_size")
            
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
            items.append(get_item_print_details(it.name, 1))

    return items

def get_item_print_details(item_code, default_print_qty):
    """
    Helper function to resolve standard printing parameters for a single item.
    """
    item_doc = frappe.get_doc("Item", item_code)
    
    # 1. Fetch Barcode
    barcode = frappe.db.get_value("Item Barcode", {"parent": item_code}, "barcode") or item_code
    
    # 2. Fetch MRP or standard price
    mrp = item_doc.custom_mrp or frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": "MRP"}, 
        "price_list_rate"
    ) or frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": "Standard Selling"}, 
        "price_list_rate"
    ) or item_doc.valuation_rate or 0.0

    # 3. Resolve Size from attributes or default
    size = "L"
    if item_doc.attributes:
        for attr in item_doc.attributes:
            if attr.attribute in ["Size", "size", "SIZE"]:
                size = attr.attribute_value
                break

    # 4. Resolve Color from attributes or default
    color = "BRONZE"
    if item_doc.attributes:
        for attr in item_doc.attributes:
            if attr.attribute.lower() in ["color", "colour", "shade"]:
                color = attr.attribute_value
                break

    return {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name,
        "brand": item_doc.brand or "SMRITI",
        "item_group": item_doc.item_group,
        "barcode": barcode,
        "mrp": flt(mrp),
        "size": size,
        "color": color,
        "print_qty": cint(default_print_qty) or 1,
        "label_size": item_doc.custom_barcode_size or "50x25"
    }

@frappe.whitelist()
def generate_prn(items):
    """
    Takes a JSON string of items and returns a merged Zebra ZPL PRN instructions string.
    """
    if not items:
        return ""

    items_list = frappe.parse_json(items)
    prn_output = []

    for it in items_list:
        barcode = it.get("barcode")
        item_name = it.get("item_name")[:25]  # Limit to fit label
        item_code = it.get("item_code") or ""
        mrp = flt(it.get("mrp"))
        brand = it.get("brand") or "SMRITI"
        size = it.get("size") or "Nos"
        color = it.get("color") or "BRONZE"
        qty = cint(it.get("print_qty")) or 1
        label_size = it.get("label_size") or "50x25"

        # Check if the requested size is the TSPL 106.6 x 55.4 mm (3-up labels)
        if label_size == "106x55":
            mrp_str = f"{int(mrp)}/-/-"
            mrp_str_short = f"{int(mrp)}/-"
            
            import datetime
            pkd_date = datetime.datetime.now().strftime("%m/%y")
            
            style = item_code
            if "-" in style:
                parts = style.split("-")
                style = parts[0]
                
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
                f'TEXT 596,426,"1",180,1,1,""\n'
                f'TEXT 763,213,"2",180,1,1,""\n'
                f'TEXT 600,301,"1",180,1,1,"(Incl of all Taxes)"\n'
                f'TEXT 594,358,"1",180,1,1,"Pkd On :"\n'
                f'TEXT 501,358,"1",180,1,1,"{pkd_date}"\n'
                f'TEXT 816,140,"3",180,1,1,"Pkd. Big Boss Shoes."\n'
                f'TEXT 816,114,"1",180,1,1,"8/15 Dattatray Shopping Centre, Manikpur"\n'
                f'TEXT 816,91,"1",180,1,1,"Vasai Rd (W), Thane- 401202, Maharashtra"\n'
                f'TEXT 816,70,"1",180,1,1,"For Comments/Feedback please write us to"\n'
                f'TEXT 816,51,"1",180,1,1,"bigboss.gobrani@yahoo.com/Call-07498131219"\n'
                f'BARCODE 613,279,"128",95,0,180,2,4,"{barcode}"\n'
                f'TEXT 597,176,"3",180,1,1,"{barcode}"\n'
                
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
                
                f'TEXT 598,335,"0",180,12,12,"Rs."\n'
                f'TEXT 177,315,"0",180,8,8,"Rs."\n'
                f'TEXT 186,91,"0",180,8,8,"Rs."\n'
                f"PRINT 1,1"
            )
            for _ in range(qty):
                prn_output.append(label_tspl)
            continue

        # Generate ZPL coordinates depending on label size
        # standard 50x25 label (small)
        x_offset = 20
        y_offset_bc = 10
        y_offset_name = 80
        y_offset_mrp = 100
        y_offset_brand = 120
        
        if label_size == "50x30":
            y_offset_name = 85
            y_offset_mrp = 110
            y_offset_brand = 135
        elif label_size == "75x50":
            x_offset = 40
            y_offset_bc = 20
            y_offset_name = 120
            y_offset_mrp = 155
            y_offset_brand = 190
        elif label_size == "100x50":
            x_offset = 50
            y_offset_bc = 20
            y_offset_name = 130
            y_offset_mrp = 170
            y_offset_brand = 210

        label_zpl = (
            f"^XA\n"
            f"^FO{x_offset},{y_offset_bc}^BCN,60,Y,N,N^FD{barcode}^FS\n"
            f"^FO{x_offset},{y_offset_name}^ADN,18,10^FD{item_name}^FS\n"
            f"^FO{x_offset},{y_offset_mrp}^ADN,18,10^FDMRP: Rs.{mrp:.2f}^FS\n"
            f"^FO{x_offset},{y_offset_brand}^ADN,14,8^FD{brand} | {size}^FS\n"
            f"^XZ"
        )

        for _ in range(qty):
            prn_output.append(label_zpl)

    return "\n".join(prn_output)
