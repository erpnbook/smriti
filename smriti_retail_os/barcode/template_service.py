# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/template_service.py
# @description: Template and print profile management service for SMRITI Label Studio.
#               Handles SMRITI Print Template CRUD, versioning, print profiles,
#               filter metadata, and item search.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import cint
from frappe import _
from smriti_retail_os import smriti


# ---------------------------------------------------------------------------
# FILTER HELPERS
# ---------------------------------------------------------------------------

def get_barcode_filters():
    """
    Returns available brands, categories, barcode sizes and print templates
    to populate filters/dropdowns on the barcode printing interface.
    """
    brands     = [b.name for b in smriti.db.get_list("Brand", fields=["name"], order_by="name asc")]
    categories = [ig.name for ig in smriti.db.get_list("Item Group", fields=["name"], order_by="name asc")]
    sizes      = ["50x25", "50x30", "75x50", "100x50", "106x55"]

    templates = []
    if smriti.db.exists("DocType", "SMRITI Print Template"):
        templates = smriti.db.get_list(
            "SMRITI Print Template",
            fields=["name", "template_title", "label_size", "printer_language",
                    "printer_family", "raw_template", "custom_field_mappings_json"],
            order_by="template_title asc"
        )
        for t in templates:
            t["template_name"] = t["template_title"]

    departments = [d.name for d in smriti.db.get_list("Department", fields=["name"], order_by="name asc")]

    genders = []
    if smriti.db.exists("DocType", "SMRITI Gender"):
        genders = [g.name for g in smriti.db.get_list("SMRITI Gender", fields=["name"], order_by="name asc")]
    else:
        genders = ["MENS", "LADIES", "BOYS", "GIRLS", "UNISEX", "KIDS"]

    seasons_res = smriti.db.get_list("Item Attribute Value",
                                    filters={"parent": ["like", "%season%"]},
                                    fields=["attribute_value"], distinct=True)
    seasons = [s.attribute_value for s in seasons_res] if seasons_res else []
    if not seasons:
        seasons = ["Spring/Summer", "Autumn/Winter", "Festive", "Core", "All Season"]
    seasons = sorted(list(set(seasons)))

    collections_res = smriti.db.get_list("Item Attribute Value",
                                        filters={"parent": ["like", "%collection%"]},
                                        fields=["attribute_value"], distinct=True)
    collections = [c.attribute_value for c in collections_res] if collections_res else []
    if not collections:
        collections = ["Classic", "Sportswear", "Casuals", "Formal", "Limited Edition"]
    collections = sorted(list(set(collections)))

    suppliers = [s.name for s in smriti.db.get_list("Supplier", fields=["name"], order_by="name asc")]

    purchase_classes = ["SIS", "FW", "MFW", "LFW", "BFW", "GFW", "KFW", "ASSTED", "SPORTS", "ACC", "BAG", "FORMAL", "CASUAL"]
    merchandise_categories = ["Footwear", "Apparel", "Accessories", "Luggage", "Sports"]
    sub_categories = ["Running Shoes", "Sneakers", "Sandals", "Formal", "Boots", "Slippers", "Belts", "Wallets"]
    upper_materials = ["Leather", "Mesh", "Canvas", "Synthetic", "PU", "Suede", "Knit", "Textile"]
    outsoles = ["TPR", "EVA", "Rubber", "Phylon", "PU", "Air Cushion", "PVC", "Leather"]
    heel_types = ["Flat", "Low Heel", "Medium Heel", "Wedge", "Block", "Platform"]

    return {
        "brands":                 brands,
        "categories":             categories,
        "sizes":                  sizes,
        "print_templates":        templates,
        "departments":            departments,
        "genders":                genders,
        "seasons":                seasons,
        "collections":            collections,
        "suppliers":              suppliers,
        "purchase_classes":       purchase_classes,
        "merchandise_categories": merchandise_categories,
        "sub_categories":         sub_categories,
        "upper_materials":        upper_materials,
        "outsoles":               outsoles,
        "heel_types":             heel_types
    }


def get_print_templates():
    """Returns all available SMRITI Print Templates for dropdown selection."""
    if not smriti.db.exists("DocType", "SMRITI Print Template"):
        return []
    templates = smriti.db.get_list(
        "SMRITI Print Template",
        fields=["name", "template_title", "label_size", "printer_language",
                "printer_family", "raw_template", "custom_field_mappings_json"],
        order_by="template_title asc"
    )
    for t in templates:
        t["template_name"] = t["template_title"]
    return templates


# ---------------------------------------------------------------------------
# PRINT PROFILES
# ---------------------------------------------------------------------------

def get_print_profiles():
    """Retrieves print profiles JSON from SMRITI Company Settings."""
    settings_name = smriti.db.get("SMRITI Company Settings", {}, "name")
    if not settings_name:
        return {}
    profiles_json = smriti.db.get("SMRITI Company Settings", settings_name, "custom_print_profiles_json")
    if not profiles_json:
        return {}
    try:
        return frappe.parse_json(profiles_json)
    except Exception:
        return {}


def save_print_profile(profile_name, template_name, printer_ip, printer_port=9100,
                       dpi="203 DPI", copies=1, label_size="50x25", is_default=0):
    """Saves a print profile in SMRITI Company Settings as a keyed JSON object."""
    import json
    settings_name = smriti.db.get("SMRITI Company Settings", {}, "name")
    if not settings_name:
        comp = smriti.db.get("Company", {}, "name")
        if not comp:
            frappe.throw(_("Please create a Company record first."))
        doc = smriti.documents.new("SMRITI Company Settings")
        doc.company = comp
        doc.insert(ignore_permissions=True)
        settings_name = doc.name

    doc = smriti.documents.get("SMRITI Company Settings", settings_name)
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
        "profile_name":  profile_name,
        "template_name": template_name,
        "printer_ip":    printer_ip,
        "printer_port":  cint(printer_port) or 9100,
        "dpi":           dpi,
        "copies":        cint(copies) or 1,
        "label_size":    label_size,
        "is_default":    is_default
    }

    doc.custom_print_profiles_json = json.dumps(profiles)
    doc.save(ignore_permissions=True)
    smriti.db.commit()
    return profiles


def delete_print_profile(profile_name):
    """Deletes a print profile from SMRITI Company Settings."""
    import json
    settings_name = smriti.db.get("SMRITI Company Settings", {}, "name")
    if not settings_name:
        return {}
    doc = smriti.documents.get("SMRITI Company Settings", settings_name)
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
        smriti.db.commit()
    return profiles


# ---------------------------------------------------------------------------
# TEMPLATE CRUD
# ---------------------------------------------------------------------------

def save_print_template(template_name, label_size, printer_language, raw_template,
                        field_mappings_json=None, printer_family=None,
                        custom_active=1, custom_is_default=0, custom_version="1.0.0",
                        custom_visual_layout_json=None, version_label=None):
    """
    Saves or updates a SMRITI Print Template record with size validations.
    """
    if len(raw_template.encode('utf-8')) > 102400:
        frappe.throw(_("Template exceeds 100KB limit"))

    if not smriti.db.exists("DocType", "SMRITI Print Template"):
        frappe.throw(_("DocType SMRITI Print Template not found."))

    def _slugify_name(val):
        import re
        clean = re.sub(r'[^a-zA-Z0-9\-]', '_', val)
        clean = re.sub(r'_+', '_', clean)
        return clean.strip('_').upper()

    name_id = _slugify_name(template_name)

    if smriti.db.exists("SMRITI Print Template", name_id):
        doc = smriti.documents.get("SMRITI Print Template", name_id)
    elif smriti.db.exists("SMRITI Print Template", {"template_title": template_name}):
        matched_name = smriti.db.get("SMRITI Print Template", {"template_title": template_name}, "name")
        doc = smriti.documents.get("SMRITI Print Template", matched_name)
    else:
        doc = smriti.documents.new("SMRITI Print Template")
        doc.name = name_id

    doc.template_title            = template_name
    doc.label_size                = label_size
    doc.printer_language          = printer_language
    doc.printer_family            = printer_family or printer_language
    doc.raw_template              = raw_template
    doc.custom_field_mappings_json = field_mappings_json
    doc.custom_visual_layout_json  = custom_visual_layout_json
    doc.custom_active              = int(custom_active)

    if custom_version and custom_version != doc.custom_version:
        doc.custom_version = custom_version
    if version_label:
        doc.flags.version_label = version_label

    if int(custom_is_default) == 1:
        smriti.db.sql(
            "UPDATE `tabSMRITI Print Template` SET custom_is_default = 0 WHERE label_size = %s",
            (label_size,)
        )
        doc.custom_is_default = 1
    else:
        doc.custom_is_default = int(custom_is_default)

    if custom_visual_layout_json:
        from smriti_retail_os.barcode.diagnostics_service import (
            validate_layout_diagnostics,
            get_enforce_printability_threshold
        )
        val_res = validate_layout_diagnostics(custom_visual_layout_json, label_size)
        score   = val_res.get("printability_score", 100.0)
        grade   = val_res.get("grade", "A+")
        enforce = get_enforce_printability_threshold()
        if enforce and grade == "F":
            errors  = [d["message"] for d in val_res.get("diagnostics", []) if d.get("severity") == "error"]
            err_msg = "; ".join(errors) if errors else "Low printability score"
            frappe.throw(
                _("Template save blocked. Printability Score: {0} (Grade F). Errors: {1}").format(score, err_msg)
            )

    try:
        doc.save(ignore_permissions=True)
        smriti.db.commit()
        smriti.documents.new("ActivityLog").update({
            "user":      frappe.session.user,
            "operation": "SMRITI Visual Template Saved",
            "status":    "Success",
            "subject":   f"Saved print template {template_name}",
            "remarks":   f"Template saved. Active version: {doc.custom_version}"
        }).insert(ignore_permissions=True)
        smriti.db.commit()
    except Exception as e:
        smriti.documents.new("ActivityLog").update({
            "user":      frappe.session.user,
            "operation": "SMRITI Visual Template Compilation Failed",
            "status":    "Failed",
            "subject":   f"Failed to save print template {template_name}",
            "remarks":   str(e)
        }).insert(ignore_permissions=True)
        smriti.db.commit()
        raise e

    return get_print_templates()


def delete_print_template(name_id):
    """Deletes a SMRITI Print Template record."""
    if not smriti.db.exists("DocType", "SMRITI Print Template"):
        frappe.throw(_("DocType SMRITI Print Template not found."))
    if smriti.db.exists("SMRITI Print Template", name_id):
        smriti.documents.delete("SMRITI Print Template", name_id, ignore_permissions=True)
        smriti.db.commit()
    return get_print_templates()


def search_barcode_items(txt):
    """
    Searches against item_code, item_name, barcode and style/article code.
    Returns top 20 matches.
    """
    if not txt:
        return []

    search_val = f"%{txt}%"

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
    return smriti.db.sql(query, {"search_val": search_val}, as_dict=True)


# ---------------------------------------------------------------------------
# VERSION HISTORY
# ---------------------------------------------------------------------------

def get_print_template_versions(template_name):
    """Returns linked version history for the specified template."""
    name_id = smriti.db.get("SMRITI Print Template", {"template_title": template_name}, "name") or template_name
    if not smriti.db.exists("SMRITI Print Template", name_id):
        return []
    return smriti.db.get_list(
        "SMRITI Print Template Version",
        filters={"template": name_id},
        fields=[
            "version_number", "version_label", "change_timestamp", "changed_by",
            "raw_template", "custom_field_mappings_json", "custom_visual_layout_json",
            "template_checksum", "restored_from_version"
        ],
        order_by="creation desc"
    )


def restore_print_template_version(template_name, version_number, expected_checksum):
    """
    Restores template from a specific version.
    Includes optimistic locking to prevent overwriting intermediate changes.
    """
    name_id = smriti.db.get("SMRITI Print Template", {"template_title": template_name}, "name") or template_name
    if not smriti.db.exists("SMRITI Print Template", name_id):
        frappe.throw(_("Template {0} not found.").format(template_name))

    doc = smriti.documents.get("SMRITI Print Template", name_id)

    # Optimistic lock
    if doc.template_checksum != expected_checksum:
        frappe.throw(
            _("Template changed since loaded. Reload before restoring."),
            frappe.ValidationError
        )

    v_name = smriti.db.get(
        "SMRITI Print Template Version",
        {"template": name_id, "version_number": version_number},
        "name"
    )
    if not v_name:
        frappe.throw(_("Version {0} of template {1} not found.").format(version_number, template_name))

    v_doc = smriti.documents.get("SMRITI Print Template Version", v_name)
    doc.raw_template              = v_doc.raw_template
    doc.custom_field_mappings_json = v_doc.custom_field_mappings_json
    doc.custom_visual_layout_json  = v_doc.custom_visual_layout_json
    doc.flags.restored_from_version = version_number

    doc.save(ignore_permissions=True)
    smriti.db.commit()

    try:
        smriti.documents.new("ActivityLog").update({
            "user":      frappe.session.user,
            "operation": "SMRITI Print Template Version Restored",
            "status":    "Success",
            "subject":   f"Restored print template {template_name} to version {version_number}",
            "remarks":   f"Restored from version {version_number}. New active version: {doc.custom_version}"
        }).insert(ignore_permissions=True)
        smriti.db.commit()
    except Exception as e:
        smriti.errors.log_error(f"Error logging template version restored: {str(e)}")

    return get_print_templates()
