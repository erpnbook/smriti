# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/api/label_api.py
# @desc:    Whitelisted REST controllers for Label Studio.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.label_studio.repository.label_template_repository import LabelTemplateRepository
from smriti_retail_os.label_studio.service.label_service import LabelService

@frappe.whitelist()
def get_label_templates():
    """Returns the list of configured label templates."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return LabelTemplateRepository.get_templates_list()

@frappe.whitelist()
def generate_preview_canvas(label_data):
    """Compiles browser canvas coordinates for template layout preview."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    if isinstance(label_data, str):
        import json
        label_data = json.loads(label_data)
        
    return LabelService.get_preview(label_data)

@frappe.whitelist()
def print_label(label_data, printer_id, format_type="ZPL"):
    """Generates print commands and dispatches them via SMRITI Print Framework."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
        
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
