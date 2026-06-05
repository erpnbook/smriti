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
    to populate filters/dropdowns on the barcode printing interface.
    """
    brands = [b.name for b in frappe.get_all("Brand", fields=["name"], order_by="name asc")]
    categories = [ig.name for ig in frappe.get_all("Item Group", fields=["name"], order_by="name asc")]
    sizes = ["50x25", "50x30", "75x50", "100x50", "106x55"]

    # Load available print templates from SMRITI Print Template DocType
    templates = []
    if frappe.db.exists("DocType", "SMRITI Print Template"):
        templates = frappe.get_all(
            "SMRITI Print Template",
            fields=["name", "template_name", "label_size", "printer_language", "raw_template", "custom_field_mappings_json"],
            order_by="template_name asc"
        )

    return {
        "brands": brands,
        "categories": categories,
        "sizes": sizes,
        "print_templates": templates
    }


@frappe.whitelist()
def get_print_templates():
    """
    Returns all available SMRITI Print Templates for dropdown selection.
    """
    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        return []

    return frappe.get_all(
        "SMRITI Print Template",
        fields=["name", "template_name", "label_size", "printer_language", "raw_template", "custom_field_mappings_json"],
        order_by="template_name asc"
    )


# ---------------------------------------------------------------------------
# ITEM LOADING
# ---------------------------------------------------------------------------

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
        db_filters = {"disabled": 0}

        if flt_dict.get("brand"):
            db_filters["brand"] = flt_dict.get("brand")
        if flt_dict.get("item_group"):
            db_filters["item_group"] = flt_dict.get("item_group")
        if flt_dict.get("custom_barcode_size"):
            db_filters["custom_barcode_size"] = flt_dict.get("custom_barcode_size")

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
            items.append(get_item_print_details(it.name, 1))

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
                            pass
                            
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
                                    pass
                                    
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
            "item_master_field": "Item Code",
            "example": "BBM-40-BRZ",
            "description": "ERPNext item code — also used as the full Style/Article reference"
        },
        {
            "placeholder": "{style}",
            "item_master_field": "Item Code (prefix before first hyphen)",
            "example": "BBM",
            "description": "Short style/article code — auto-derived from item_code split on '-'"
        },
        {
            "placeholder": "{item_name}",
            "item_master_field": "Item Name",
            "example": "Big Boss Men Casual Loafer",
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
            "example": "499",
            "description": "Maximum Retail Price — integer only (e.g. 499, not 499.00)"
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
            "example": "BRONZE",
            "description": "Color from Item Attribute table (attribute names: Color/Colour/Shade)"
        },
        {
            "placeholder": "{pkd_date}",
            "item_master_field": "Auto-generated at print time",
            "example": "05/26",
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
            "example": "MFW",
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
            "message": f"Connection successful! Response time: {elapsed:.1f} ms"
        }
    except socket.timeout:
        return {"success": False, "message": "Connection timed out. Verify IP and Port."}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


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

    # 2. Frappe Activity Log
    try:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
        log_doc = frappe.new_doc("Activity Log")
        log_doc.user = frappe.session.user
        log_doc.operation = "SMRITI Label Studio Print Run"
        log_doc.status = "Success" if success_val else "Failed"
        log_doc.subject = f"Printed {labels_count} label(s) using template {template_name} on {printer_ip}"
        
        details_str = f"Printer IP: {printer_ip}\nProfile: {print_profile or 'None'}\nSuccess: {success_val}\nError: {error_message or ''}\nCompany: {company}\nDetails: {details or ''}"
        log_doc.remarks = details_str
        log_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to write Activity Log print job: {str(e)}")

    return {"success": True}


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
                        pass
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
def save_print_template(template_name, label_size, printer_language, raw_template, field_mappings_json=None):
    """
    Saves or updates a SMRITI Print Template record with size validations.
    """
    # 100 KB template size limit validation
    if len(raw_template.encode('utf-8')) > 102400:
        frappe.throw(_("Template size exceeds the maximum limit of 100 KB."))

    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        frappe.throw(_("DocType SMRITI Print Template not found."))

    if frappe.db.exists("SMRITI Print Template", template_name):
        doc = frappe.get_doc("SMRITI Print Template", template_name)
    else:
        doc = frappe.new_doc("SMRITI Print Template")
        doc.template_name = template_name

    doc.label_size = label_size
    doc.printer_language = printer_language
    doc.raw_template = raw_template
    doc.custom_field_mappings_json = field_mappings_json
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return get_print_templates()

