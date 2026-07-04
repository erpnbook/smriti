# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/batch_service.py
# @description: Async print job queue service for SMRITI Label Studio.
#               Handles job enqueue, background processing, status tracking,
#               retry, and cleanup of old print jobs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import os
import hashlib
import frappe
from frappe.utils import cint
from frappe import _
from smriti_retail_os.barcode.printer_service import _send_to_printer_sync
from smriti_retail_os.barcode.analytics_service import log_print_job


def enqueue_print_job(template_name, printer_ip, printer_port, payload,
                      print_qty=1, labels_count=None, item_code=None, barcode=None):
    """
    Writes payload to disk, creates SMRITI Print Job record, and enqueues
    a background worker to send the print data to the printer.
    """
    if labels_count is not None:
        print_qty = labels_count

    job_id = f"JOB-{frappe.generate_hash(length=12).upper()}"

    prn_dir  = frappe.get_site_path('private', 'print_jobs')
    os.makedirs(prn_dir, exist_ok=True)
    prn_path = os.path.join(prn_dir, f"{job_id}.prn")

    with open(prn_path, 'w', encoding='utf-8') as f:
        f.write(payload)
    os.chmod(prn_path, 0o600)

    # Create job record
    doc = frappe.new_doc("SMRITI Print Job")
    doc.job_id          = job_id
    doc.name            = job_id
    doc.item_code       = item_code
    doc.barcode         = barcode
    doc.template_name   = template_name
    doc.printer_ip      = printer_ip
    doc.printer_port    = cint(printer_port) or 9100
    doc.print_qty       = cint(print_qty) or 1
    doc.status          = "Queued"
    doc.payload_hash    = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    doc.payload_preview = payload[:100]
    doc.created_by      = frappe.session.user
    doc.created_on      = frappe.utils.now_datetime()
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Audit log
    try:
        frappe.get_doc({
            "doctype":   "Activity Log",
            "user":      doc.created_by,
            "operation": "SMRITI Print Job Queued",
            "status":    "Success",
            "subject":   f"Print job {job_id} queued",
            "remarks":   f"Queued {doc.print_qty} labels for template {doc.template_name}"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error logging print job queued: {str(e)}")

    # Realtime notification
    frappe.publish_realtime(
        "smriti.barcode.print_status",
        {"event_version": 1, "job_id": job_id, "status": "Queued"},
        user=doc.created_by
    )

    # Background worker — path stays at barcode_api for backward compat with hooks
    frappe.enqueue(
        "smriti_retail_os.barcode_api._process_print_job",
        print_job_id=job_id,
        queue="barcode",
        timeout=30,
        now=frappe.flags.in_test
    )

    return {"job_id": job_id, "status": "Queued"}


def _process_print_job(job_id=None, print_job_id=None):
    """
    Background worker: reads PRN payload from disk, verifies integrity,
    sends to printer, updates job status, and publishes realtime events.
    """
    if job_id is None:
        job_id = print_job_id

    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)

    doc = frappe.get_doc("SMRITI Print Job", name)
    doc.status = "Sending"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    def _audit(operation, status, subject, remarks):
        try:
            frappe.get_doc({
                "doctype":   "Activity Log",
                "user":      doc.created_by or "System",
                "operation": operation,
                "status":    status,
                "subject":   subject,
                "remarks":   remarks
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error writing audit log: {str(e)}")

    _audit(
        "SMRITI Print Job Sending", "Success",
        f"Print job {job_id} is sending",
        f"Sending payload to {doc.printer_ip}:{doc.printer_port}"
    )

    frappe.publish_realtime(
        "smriti.barcode.print_status",
        {"event_version": 1, "job_id": job_id, "status": "Sending"},
        user=doc.created_by or "Administrator"
    )

    prn_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")

    try:
        if not os.path.exists(prn_path):
            raise FileNotFoundError(f"Payload file missing for job {job_id}")

        with open(prn_path, "r", encoding="utf-8") as f:
            payload = f.read()

        # Integrity check
        actual_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        if actual_hash != doc.payload_hash:
            _audit(
                "SMRITI Visual Template Compilation Failed", "Failed",
                f"Print job {job_id} integrity mismatch",
                "Expected hash does not match actual PRN file content."
            )
            raise RuntimeError("Print payload integrity validation failed.")

        # Resolve _send_to_printer_sync dynamically to support legacy unittest mocking on barcode_api
        send_fn = None
        try:
            import smriti_retail_os.barcode_api as barcode_api
            send_fn = getattr(barcode_api, "_send_to_printer_sync", _send_to_printer_sync)
        except Exception:
            send_fn = _send_to_printer_sync

        send_fn(payload, doc.printer_ip, doc.printer_port)

        doc.status       = "Success"
        doc.completed_on = frappe.utils.now_datetime()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.publish_realtime(
            "smriti.barcode.print_status",
            {"event_version": 1, "job_id": job_id, "status": "Success"},
            user=doc.created_by or "Administrator"
        )

        log_print_job(doc.template_name, doc.printer_ip, doc.print_qty, 1)
        _audit(
            "SMRITI Print Job Success", "Success",
            f"Print job {job_id} printed successfully",
            f"Printed {doc.print_qty} labels on {doc.printer_ip}"
        )

        # Cleanup .prn file
        try:
            os.unlink(prn_path)
        except FileNotFoundError:
            pass

    except Exception as e:
        doc.status        = "Failed"
        doc.error_message = str(e)
        doc.completed_on  = frappe.utils.now_datetime()
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.log_error(
            title=f"SMRITI Print Job Failed: {job_id}",
            message=f"Printer: {doc.printer_ip}:{doc.printer_port}\nTemplate: {doc.template_name}\nError: {str(e)}"
        )

        frappe.publish_realtime(
            "smriti.barcode.print_status",
            {"event_version": 1, "job_id": job_id, "status": "Failed"},
            user=doc.created_by or "Administrator"
        )

        log_print_job(doc.template_name, doc.printer_ip, doc.print_qty, 0, error_message=str(e))
        _audit(
            "SMRITI Print Job Failed", "Failed",
            f"Print job {job_id} failed", str(e)
        )
        raise e


def get_print_job_status(job_id):
    """Returns status of a single print job."""
    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)
    doc = frappe.get_doc("SMRITI Print Job", name)
    return {
        "status":        doc.status,
        "error_message": doc.error_message or "",
        "completed_on":  doc.completed_on
    }


def retry_print_job(job_id):
    """Re-enqueues a failed print job using the original payload file."""
    name = frappe.db.get_value("SMRITI Print Job", {"job_id": job_id}, "name")
    if not name:
        frappe.throw(f"Print job {job_id} not found.", frappe.DoesNotExistError)

    old_doc  = frappe.get_doc("SMRITI Print Job", name)
    old_path = frappe.get_site_path('private', 'print_jobs', f"{job_id}.prn")
    if not os.path.exists(old_path):
        frappe.throw(_("Original payload no longer available. Re-print from worksheet."))

    with open(old_path, 'r', encoding='utf-8') as f:
        payload = f.read()

    res = enqueue_print_job(
        template_name=old_doc.template_name,
        printer_ip=old_doc.printer_ip,
        printer_port=old_doc.printer_port,
        print_qty=old_doc.print_qty,
        payload=payload
    )
    return {"job_id": res["job_id"]}


def get_recent_print_jobs(limit=20):
    """Returns recent print jobs ordered by creation desc."""
    return frappe.get_all(
        "SMRITI Print Job",
        fields=["job_id", "status", "template_name", "print_qty as labels_count", "creation", "printer_ip"],
        order_by="creation desc",
        limit=cint(limit) or 20
    )


def cleanup_old_print_jobs():
    """
    Scheduler task: Success jobs >30 days → delete, Failed jobs >90 days → delete .prn + record.
    """
    try:
        from frappe.utils import add_days, now_datetime
        success_cutoff = add_days(now_datetime(), -30)
        failed_cutoff  = add_days(now_datetime(), -90)

        success_jobs = frappe.get_all(
            "SMRITI Print Job",
            filters={"status": "Success", "completed_on": ["<", success_cutoff]},
            fields=["name", "job_id"]
        )
        success_deleted = 0
        for job in success_jobs:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{job.job_id}.prn")
            if os.path.exists(prn_path):
                try:
                    os.remove(prn_path)
                except Exception:
                    pass
            frappe.delete_doc("SMRITI Print Job", job.name, ignore_permissions=True)
            success_deleted += 1

        failed_jobs = frappe.get_all(
            "SMRITI Print Job",
            filters={"status": "Failed", "completed_on": ["<", failed_cutoff]},
            fields=["name", "job_id"]
        )
        failed_deleted = 0
        for job in failed_jobs:
            prn_path = frappe.get_site_path('private', 'print_jobs', f"{job.job_id}.prn")
            if os.path.exists(prn_path):
                try:
                    os.remove(prn_path)
                except Exception:
                    pass
            frappe.delete_doc("SMRITI Print Job", job.name, ignore_permissions=True)
            failed_deleted += 1

        if success_deleted or failed_deleted:
            frappe.db.commit()

        from smriti_retail_os.backup_api import log_audit_event
        log_audit_event(
            "SMRITI Print Job Cleanup",
            f"Cleaned up {success_deleted} success jobs (>30d) and {failed_deleted} failed jobs (>90d)."
        )
    except Exception as e:
        frappe.log_error(title="SMRITI Print Job Cleanup Error", message=str(e))
