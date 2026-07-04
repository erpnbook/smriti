# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/api/print_api.py
# @desc:    Whitelisted REST controllers.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.print_framework.registry.printer_registry import PrinterRegistry
from smriti_retail_os.print_framework.service.print_service import PrintService

@frappe.whitelist()
def get_registered_printers():
    """Returns the metadata profiles of all registered printers."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    printers_list = []
    for pid in PrinterRegistry.get_registered_ids():
        meta = PrinterRegistry.get_printer(pid)
        printers_list.append({
            "printer_id": pid,
            "connection_type": meta["connection_type"],
            "capabilities": meta["capabilities"]
        })
    return printers_list

@frappe.whitelist()
def dispatch_print_job(module_name, printer_id, payload_str):
    """Enqueues and dispatches a print job via SMRITI Print Framework."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    try:
        job_id = PrintService.print_label(module_name, printer_id, payload_str)
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
