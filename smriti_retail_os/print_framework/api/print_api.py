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
from smriti_retail_os import smriti

import json
from frappe.utils import now_datetime


@frappe.whitelist()
def check_doc_exists(doctype, docname):
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    exists = False
    permitted = False
    try:
        if smriti.db.exists(doctype, docname):
            exists = True
            if smriti.permissions.has_permission(doctype, "read", docname):
                permitted = True
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SMRITI check_doc_exists error")
    return {"exists": exists, "permitted": permitted}


@frappe.whitelist()
def log_print_attempt(doctype, docname, exists, action="PRINT"):
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    try:
        entry = {
            "event": "PRINT_ATTEMPT:" + str(action),
            "doctype": doctype or "",
            "docname": docname or "",
            "exists": True if str(exists) in ("1","true","True") else False,
            "timestamp": str(now_datetime()),
            "user": frappe.session.user
        }
        frappe.log_error(message=json.dumps(entry, indent=2), title="SMRITI PRINT_ATTEMPT")
    except Exception:
        pass
    return {"logged": True}

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

@frappe.whitelist()
def share_via_email(doctype, docname, email):
    """Generates a document PDF and emails it as an attachment."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    pdf_content = frappe.get_print(doctype, docname, as_pdf=True)
    
    frappe.sendmail(
        recipients=[email],
        subject=f"{doctype} {docname}",
        message=f"Please find attached your {doctype} {docname}.",
        attachments=[{
            "fname": f"{docname.replace('/', '_')}.pdf",
            "fcontent": pdf_content
        }],
        now=True
    )
    return {
        "success": True,
        "message": _("Email sent successfully.")
    }

@frappe.whitelist()
def share_via_whatsapp(doctype, docname, phone):
    """Generates a document PDF, saves it publicly, and returns the public link."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    from frappe.utils.file_manager import save_file
    
    pdf_content = frappe.get_print(doctype, docname, as_pdf=True)
    file_name = f"{docname.replace('/', '_')}.pdf"
    
    existing = smriti.db.get_list("File", filters={"attached_to_doctype": doctype, "attached_to_name": docname, "file_name": file_name}, fields=["file_url"])
    if existing:
        file_url = existing[0].file_url
    else:
        saved_file = save_file(file_name, pdf_content, doctype, docname, is_private=0)
        file_url = saved_file.file_url
        
    base_url = frappe.utils.get_url()
    full_url = f"{base_url}{file_url}"
    
    return {
        "success": True,
        "file_url": full_url
    }

@frappe.whitelist()
def send_pdf_email(email_address, pdf_base64, file_name, subject="Report"):
    """Emails a Base64 encoded PDF report to the specified address."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    import base64
    import frappe
    pdf_content = base64.b64decode(pdf_base64)
    
    frappe.sendmail(
        recipients=[email_address],
        subject=subject,
        message=f"Please find attached the exported PDF: {file_name}.",
        attachments=[{
            "fname": file_name,
            "fcontent": pdf_content
        }],
        now=True
    )
    return {"success": True}

@frappe.whitelist()
def save_pdf_public(pdf_base64, file_name):
    """Saves a Base64 encoded PDF publicly and returns the URL."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
        
    import base64
    import frappe
    from frappe.utils.file_manager import save_file
    
    pdf_content = base64.b64decode(pdf_base64)
    saved_file = save_file(file_name, pdf_content, None, None, is_private=0)
    
    base_url = frappe.utils.get_url()
    full_url = f"{base_url}{saved_file.file_url}"
    
    return {
        "success": True,
        "file_url": full_url
    }
