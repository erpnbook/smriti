# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/prn_generator.py
# @description: PRN content generation service for ZPL/TSPL label printers.
#               Handles template-driven token substitution and built-in fallback templates.
#               Uses token_registry.build_token_dict() as single source of truth.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import re
import frappe
from frappe.utils import flt, cint
from frappe import _
from smriti_retail_os.barcode.token_registry import build_token_dict


def _safe_template_substitute(template, token_dict):
    """
    Replaces only known {placeholder} tokens; leaves any other
    literal { or } in the template untouched instead of raising.
    """
    if not template:
        return ""

    def _replace(match):
        key = match.group(1)
        return str(token_dict.get(key, match.group(0)))

    pattern = r"\{(" + "|".join(re.escape(k) for k in token_dict.keys()) + r")\}"
    return re.sub(pattern, _replace, template)


def generate_prn(items, template_name=None):
    """
    Generates raw ZPL/TSPL PRN content for the given items list.

    If template_name is provided and exists in SMRITI Print Template,
    it uses that template's raw_template with substitution via token_registry.
    Otherwise falls back to built-in hardcoded templates.

    Token placeholders are defined centrally in token_registry.BARCODE_TOKEN_REGISTRY.
    """
    if not items:
        return {
            "prn": "",
            "fallback_used": False,
            "fallback_items": [],
        }

    items_list = frappe.parse_json(items)
    prn_output = []
    used_fallback_for = []

    # Load custom template from DB
    db_template = None
    if template_name and frappe.db.exists("DocType", "SMRITI Print Template"):
        if frappe.db.exists("SMRITI Print Template", template_name):
            db_template = frappe.get_doc("SMRITI Print Template", template_name)
        else:
            matched_name = frappe.db.get_value("SMRITI Print Template", {"template_title": template_name}, "name")
            if matched_name:
                db_template = frappe.get_doc("SMRITI Print Template", matched_name)

    for it in items_list:
        item_code  = it.get("item_code") or ""
        qty        = cint(it.get("print_qty")) or 1
        label_size = it.get("label_size") or "50x25"

        # Build token dict from registry (single source of truth)
        token_dict = build_token_dict(it)

        # Convenience aliases for fallback templates
        barcode   = token_dict["barcode"]
        item_name = token_dict["item_name"]
        mrp       = flt(it.get("mrp") or 0)
        brand     = token_dict["brand"]
        size      = token_dict["size"]
        color     = token_dict["color"]
        style     = token_dict["style"]
        pkd_date  = token_dict["pkd_date"]

        # --- Template-driven path ---
        if db_template:
            try:
                raw = db_template.raw_template or ""

                mappings_json = db_template.get("custom_field_mappings_json")
                if mappings_json:
                    mappings = frappe.parse_json(mappings_json)
                    if mappings and isinstance(mappings, list):
                        item_doc = None
                        try:
                            item_doc = frappe.get_doc("Item", item_code)
                        except Exception:
                            import sys
                            _f = sys.modules.get('frappe')
                            if _f:
                                _f.logger().debug(f"SMRITI Debug: Item load failed in prn_generator: {sys.exc_info()[1]}")

                        # Rebuild token dict from dynamic mappings
                        dynamic_token_dict = {}
                        for m in mappings:
                            lbl_f = m.get("label_field")
                            erp_f = m.get("erp_field")
                            if not lbl_f or not erp_f:
                                continue

                            val = None
                            if item_doc and item_doc.meta.has_field(erp_f):
                                val = item_doc.get(erp_f)
                            elif erp_f in token_dict:
                                val = token_dict[erp_f]
                            elif erp_f in it:
                                val = it.get(erp_f)
                            else:
                                val = it.get(lbl_f) or ""

                            # Currency formatting
                            if lbl_f == "mrp" or "mrp" in erp_f or "rate" in erp_f or "price" in erp_f:
                                try:
                                    val = f"{int(flt(val))}"
                                except Exception:
                                    pass

                            dynamic_token_dict[lbl_f] = str(val) if val is not None else ""

                        token_dict = dynamic_token_dict

                label_str = _safe_template_substitute(raw, token_dict)
                for _ in range(qty):
                    prn_output.append(label_str)
                continue

            except Exception as e:
                used_fallback_for.append(item_code)
                frappe.log_error(
                    f"PRN template substitution failed for '{template_name}': {e}",
                    "Barcode PRN Generator"
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
                # Column 1: Full MRP label
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
                # Column 2: Shoe tag
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
                # Column 3: Box tag
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
        x_offset       = 20
        y_offset_bc    = 10
        y_offset_name  = 80
        y_offset_mrp   = 100
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

    return {
        "prn": "\n".join(prn_output),
        "fallback_used": bool(used_fallback_for),
        "fallback_items": used_fallback_for,
    }
