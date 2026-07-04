# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/diagnostics_service.py
# @description: Layout validation and printability scoring service for SMRITI Label Studio.
#               Validates visual template layouts and returns a diagnostics report
#               with a graded printability score.
#               Uses token_registry.build_preview_token_dict() for preview resolution.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import json
import frappe
from frappe.utils import cint
from smriti_retail_os.barcode.token_registry import build_preview_token_dict


# ---------------------------------------------------------------------------
# SETTINGS HELPERS
# ---------------------------------------------------------------------------

def get_barcode_hrt_reserved_height():
    """Fetches barcode_hrt_reserved_height_mm from settings or returns 2.5 fallback."""
    try:
        if frappe.db.exists("DocType", "SMRITI Barcode Settings"):
            res = frappe.db.sql(
                "SELECT value FROM `tabSingles` WHERE doctype = 'SMRITI Barcode Settings' "
                "AND field = 'barcode_hrt_reserved_height_mm'"
            )
            if res and res[0][0] is not None:
                return float(res[0][0])
    except Exception:
        pass
    return 2.5


def get_enforce_printability_threshold():
    """Fetches enforce_printability_threshold from settings or returns 1 fallback."""
    try:
        if frappe.db.exists("DocType", "SMRITI Barcode Settings"):
            res = frappe.db.sql(
                "SELECT value FROM `tabSingles` WHERE doctype = 'SMRITI Barcode Settings' "
                "AND field = 'enforce_printability_threshold'"
            )
            if res and res[0][0] is not None:
                return int(res[0][0])
    except Exception:
        pass
    return 1


def get_printability_formula_config():
    """
    Fetches printability score configuration from SMRITI Formula Definition.
    Cached TTL=3600. Falls back to hardcoded defaults.
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
            "margin":     25,
            "quiet_zone": 25,
            "overflow":   20,
            "density":    15,
            "collision":  15
        },
        "grade_bands": {
            "A+": [95, 100],
            "A":  [90, 94],
            "B":  [80, 89],
            "C":  [70, 79],
            "F":  [0, 69]
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
                    message="SMRITI-PRN-SCORE-01 has empty explainability_json. Using fallback."
                )
        else:
            frappe.log_error(
                title="SMRITI Formula Registry Warning",
                message="SMRITI-PRN-SCORE-01 missing from Formula Registry. Using fallback."
            )
    except Exception as e:
        frappe.log_error(
            title="SMRITI Formula Registry Warning",
            message=f"Formula Registry fetch failed: {str(e)}"
        )

    try:
        frappe.cache().set_value(cache_key, config, expires_in_sec=3600)
    except Exception:
        pass
    return config


# ---------------------------------------------------------------------------
# LAYOUT VALIDATION
# ---------------------------------------------------------------------------

def validate_layout_diagnostics(layout_json, label_size, item_data=None):
    """
    Validates print template layout and returns a diagnostics dictionary.
    Diagnostics are categorized as 'warning' or 'error'.
    Includes printability score, grade bands, breakdown, and recommendations.
    """
    if not layout_json:
        return {
            "diagnostics": [],
            "errors_count": 0,
            "warnings_count": 0,
            "printability_score": 100.0,
            "grade": "A+",
            "breakdown": {"margin": 25, "quiet_zone": 25, "overflow": 20, "density": 15, "collision": 15},
            "recommendations": []
        }

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
        lw, lh = 50.0, 25.0

    reserved_height_mm = get_barcode_hrt_reserved_height()
    formula_cfg        = get_printability_formula_config()
    weights            = formula_cfg["weights"]
    grade_bands        = formula_cfg["grade_bands"]

    # Use centralized preview token resolver
    preview_tokens = build_preview_token_dict(item_data or {})

    def resolve_tokens_py(content):
        if not content:
            return ""
        res = content
        for k, v in preview_tokens.items():
            res = res.replace("{" + k + "}", str(v))
        return res

    diagnostics    = []
    recommendations = []

    SAFE_MARGIN_MM   = 1.5
    QUIET_ZONE_BUFFER = 2.5

    margin_errors_count     = 0
    margin_warnings_count   = 0
    quiet_zone_errors_count  = 0
    quiet_zone_warnings_count = 0
    text_overflows_count    = 0
    density_warnings_count  = 0
    collision_errors_count  = 0

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

        el_type   = elem.get("type", "")
        el_id     = elem.get("id", "")
        content   = elem.get("content", "")
        processed = {
            "id": el_id, "type": el_type,
            "x": x, "y": y, "w": w, "h": h,
            "content": content,
            "format": elem.get("format") or elem.get("barcode_type") or "code128"
        }
        processed_elements.append(processed)
        if el_type == "barcode":
            barcodes.append(processed)

    # 1. Printable bounds & safe margin check
    for elem in processed_elements:
        x, y, w, h     = elem["x"], elem["y"], elem["w"], elem["h"]
        el_type, el_id  = elem["type"], elem["id"]

        if x < 0 or y < 0 or (x + w) > lw or (y + h) > lh:
            diagnostics.append({
                "element_id": el_id,
                "severity":   "error",
                "message":    f"Element {el_id or el_type} exceeds printable area ({lw}x{lh}mm)"
            })
            margin_errors_count += 1
            continue

        if (x < SAFE_MARGIN_MM or y < SAFE_MARGIN_MM
                or (x + w) > (lw - SAFE_MARGIN_MM)
                or (y + h) > (lh - SAFE_MARGIN_MM)):
            if el_type in ["barcode", "qrcode"]:
                diagnostics.append({
                    "element_id": el_id,
                    "severity":   "error",
                    "message":    f"{el_type.upper()} {el_id} overlaps print-safe margin"
                })
                margin_errors_count += 1
            else:
                diagnostics.append({
                    "element_id": el_id,
                    "severity":   "warning",
                    "message":    f"Element {el_id or el_type} overlaps print-safe margin"
                })
                margin_warnings_count += 1

    # 2. Quiet Zone Buffer & Barcode Density
    for bc in barcodes:
        bc_format  = bc["format"].lower()
        bc_w       = bc["w"]
        is_ean_upc = "ean" in bc_format or "upc" in bc_format
        min_rec    = 25.0 if is_ean_upc else 15.0
        if bc_w < min_rec:
            diagnostics.append({
                "element_id": bc["id"],
                "severity":   "warning",
                "message":    (
                    f"Barcode {bc['id']} width ({bc_w}mm) is less than "
                    f"recommended minimum ({min_rec}mm) for {bc['format']}"
                )
            })
            density_warnings_count += 1

        ax, ay, aw, ah = bc["x"], bc["y"], bc["w"], bc["h"]
        q_x = ax - QUIET_ZONE_BUFFER
        q_w = aw + 2 * QUIET_ZONE_BUFFER

        for other in processed_elements:
            if other["id"] == bc["id"]:
                continue
            ox, oy, ow, oh = other["x"], other["y"], other["w"], other["h"]
            if (q_x < ox + ow) and (q_x + q_w > ox) and (ay < oy + oh) and (ay + ah > oy):
                is_decor     = other["type"] in ["box", "bar"]
                is_main_over = (ax < ox + ow) and (ax + aw > ox) and (ay < oy + oh) and (ay + ah > oy)
                if not is_main_over:
                    if is_decor:
                        diagnostics.append({
                            "element_id": f"{bc['id']}<->{other['id']}",
                            "severity":   "warning",
                            "message":    f"Decorative element {other['id']} invades quiet zone of barcode {bc['id']}"
                        })
                        quiet_zone_warnings_count += 1
                    else:
                        diagnostics.append({
                            "element_id": f"{bc['id']}<->{other['id']}",
                            "severity":   "error",
                            "message":    f"Element {other['id']} encroaches on quiet zone of barcode {bc['id']}"
                        })
                        quiet_zone_errors_count += 1

    # 3. Text Overflow
    for elem in processed_elements:
        if elem["type"] == "text":
            resolved      = resolve_tokens_py(elem["content"])
            char_width_mm = 1.8
            est_width     = len(resolved) * char_width_mm
            if est_width > elem["w"]:
                diagnostics.append({
                    "element_id": elem["id"],
                    "severity":   "warning",
                    "message":    f"Text element {elem['id']} content may overflow designed width"
                })
                text_overflows_count += 1

    # 4. Collision check (main elements + virtual HRT)
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
                    "severity":   "error",
                    "message":    f"Element collision detected between {a['id'] or a['type']} and {b['id'] or b['type']}"
                })
                collision_errors_count += 1

    for bc in barcodes:
        bx, by, bw, bh = bc["x"], bc["y"], bc["w"], bc["h"]
        vx, vy, vw, vh = bx, by + bh, bw, reserved_height_mm
        if vy + vh > lh:
            diagnostics.append({
                "element_id": bc["id"],
                "severity":   "warning",
                "message":    f"Virtual HRT area for barcode {bc['id']} exceeds label height ({lh}mm)"
            })
        for other in non_decorative:
            if other["id"] == bc["id"]:
                continue
            ox, oy, ow, oh = other["x"], other["y"], other["w"], other["h"]
            if (vx < ox + ow) and (vx + vw > ox) and (vy < oy + oh) and (vy + vh > oy):
                diagnostics.append({
                    "element_id": f"{bc['id']}_hrt<->{other['id']}",
                    "severity":   "error",
                    "message":    f"Element {other['id']} overlaps virtual HRT space of barcode {bc['id']}"
                })
                collision_errors_count += 1

    # Printability Score
    margin_score    = max(0, weights["margin"] - (margin_errors_count * 10) - (margin_warnings_count * 5))
    quiet_zone_score = weights["quiet_zone"]
    if quiet_zone_errors_count > 0:
        quiet_zone_score = 0
    else:
        quiet_zone_score = max(0, quiet_zone_score - (quiet_zone_warnings_count * 5))

    overflow_score  = max(0, weights["overflow"] - (text_overflows_count * 5))
    density_score   = max(0, weights["density"] - (density_warnings_count * 5))
    collision_score = weights["collision"] if collision_errors_count == 0 else 0
    total_score     = float(margin_score + quiet_zone_score + overflow_score + density_score + collision_score)

    grade = "F"
    try:
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

    errors_count   = sum(1 for d in diagnostics if d["severity"] == "error")
    warnings_count = sum(1 for d in diagnostics if d["severity"] == "warning")

    return {
        "diagnostics":        diagnostics,
        "errors_count":       errors_count,
        "warnings_count":     warnings_count,
        "printability_score": total_score,
        "grade":              grade,
        "breakdown": {
            "margin":     margin_score,
            "quiet_zone": quiet_zone_score,
            "overflow":   overflow_score,
            "density":    density_score,
            "collision":  collision_score
        },
        "recommendations": recommendations
    }
