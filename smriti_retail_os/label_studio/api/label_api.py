# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/api/label_api.py
# @desc:    Whitelisted REST controllers for Label Studio.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os import smriti
from smriti_retail_os.label_studio.repository.label_template_repository import LabelTemplateRepository
from smriti_retail_os.label_studio.service.label_service import LabelService


def _guest_guard():
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)


@frappe.whitelist()
def get_label_templates():
    """Returns the list of configured label templates."""
    _guest_guard()
    return LabelTemplateRepository.get_templates_list()


@frappe.whitelist()
def generate_preview_canvas(label_data):
    """Compiles browser canvas coordinates for template layout preview."""
    _guest_guard()

    if isinstance(label_data, str):
        import json
        label_data = json.loads(label_data)

    return LabelService.get_preview(label_data)


@frappe.whitelist()
def print_label(label_data, printer_id, format_type="ZPL"):
    """Generates print commands and dispatches them via SMRITI Print Framework."""
    _guest_guard()

    if isinstance(label_data, str):
        import json
        label_data = json.loads(label_data)

    try:
        job_id = LabelService.dispatch_print(label_data, printer_id, format_type)
        return {
            "success": True,
            "job_id": job_id,
            "message": _("Print job enqueued successfully.")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": _("Failed to dispatch print job.")
        }


@frappe.whitelist()
def get_item_for_label(item_code):
    """
    Returns retail-relevant fields for a given ERPNext Item Code.
    Used by Label Studio to auto-populate label elements from inventory.

    Returns
    -------
    dict with keys: item_code, item_name, barcode, mrp, hsn_code, brand, description
    """
    _guest_guard()

    if not item_code:
        frappe.throw(_("Item Code is required to load label data."))

    if not smriti.db.exists("Item", item_code):
        frappe.throw(
            _("Product not found: {0}. Please check the Item Code and try again.").format(item_code)
        )

    item = smriti.documents.get("Item", item_code)

    # Primary barcode: first entry in Item Barcode child table, else blank
    barcode = ""
    if hasattr(item, "barcodes") and item.barcodes:
        barcode = item.barcodes[0].barcode or ""

    # MRP: standard_rate is the base selling price; valuation_rate is cost
    mrp = smriti.db.get(
        "Item Price",
        {"item_code": item_code, "selling": 1, "price_list": "Standard Selling"},
        "price_list_rate"
    ) or getattr(item, "standard_rate", 0) or 0

    return {
        "item_code":   item.item_code,
        "item_name":   item.item_name or "",
        "barcode":     barcode,
        "mrp":         float(mrp),
        "hsn_code":    getattr(item, "gst_hsn_code", "") or getattr(item, "hsn_code", "") or "",
        "brand":       getattr(item, "brand", "") or "",
        "description": (item.description or "")[:120],
    }


@frappe.whitelist()
def get_printers_list():
    """
    Returns available printers registered in SMRITI Print Framework.
    Falls back to a default ZPL printer entry when none are configured.
    """
    _guest_guard()
    try:
        printers = smriti.db.get_list(
            "SMRITI Printer",
            fields=["name", "printer_name", "format_type", "ip_address"],
            filters={"disabled": 0},
            order_by="printer_name asc"
        )
        if printers:
            return printers
    except Exception:
        pass
    # Fallback when SMRITI Printer doctype not yet configured
    return [{"name": "default", "printer_name": "Default Printer (ZPL)", "format_type": "ZPL", "ip_address": ""}]
