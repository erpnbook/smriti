# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/analytics_service.py
# @description: Print analytics and logging service for SMRITI Label Studio.
#               Handles print job activity logging and analytics compilation
#               from the Frappe Activity Log.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import datetime
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import cint
from frappe import _
from smriti_retail_os import smriti


def log_print_job(template_name, printer_ip, labels_count, success,
                  error_message=None, print_profile=None, details=None):
    """
    Logs print job activity locally and in Frappe Activity Log for audit-trail.
    """
    import json
    import os
    success_val = cint(success)

    # 1. Local file log
    try:
        log_dir = os.path.join(frappe.get_app_path("smriti_retail_os"), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "barcode_print.log")
        log_msg = (
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
            f"User: {frappe.session.user} - Template: {template_name} - "
            f"IP: {printer_ip} - Count: {labels_count} - "
            f"Success: {success_val} - Error: {error_message or 'None'}\n"
        )
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(log_msg)
    except Exception as e:
        smriti.errors.log_error(f"Failed to write local print log: {str(e)}")

    # 2. Frappe Activity Log
    try:
        company = frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
        log_doc = smriti.documents.new("Activity Log")
        log_doc.user = frappe.session.user
        log_doc.operation = "SMRITI Label Studio Print Run"
        log_doc.status = "Success" if success_val else "Failed"
        log_doc.subject = f"Printed {labels_count} label(s) using template {template_name} on {printer_ip}"
        remarks_dict = {
            "labels":         cint(labels_count),
            "template":       template_name,
            "printer":        printer_ip,
            "status":         "success" if success_val else "failed",
            "error_message":  error_message or "",
            "company":        company,
            "profile":        print_profile or "None",
            "details":        details or ""
        }
        log_doc.remarks = json.dumps(remarks_dict)
        log_doc.insert(ignore_permissions=True)
        smriti.db.commit()
    except Exception as e:
        smriti.errors.log_error(f"Failed to write Activity Log print job: {str(e)}")

    return {"success": True}


def get_print_analytics():
    """
    Compiles detailed print analytics by parsing remarks JSON from SMRITI Activity Logs.
    """
    import json
    try:
        logs = smriti.db.get_list(
            "Activity Log",
            filters={"operation": "SMRITI Label Studio Print Run"},
            fields=["remarks", "status", "creation"],
            order_by="creation desc"
        )

        total_labels   = 0
        total_jobs     = len(logs)
        failed_jobs    = 0
        success_jobs   = 0
        template_stats = {}
        printer_stats  = {}
        history        = []

        for log in logs:
            remarks = log.remarks or ""
            data = {}
            if remarks.strip().startswith("{") and remarks.strip().endswith("}"):
                try:
                    data = json.loads(remarks)
                except Exception:
                    pass

            if not data:
                labels   = 0
                template = "Unknown"
                printer  = "Unknown"
                status   = "success" if log.status == "Success" else "failed"
                subj     = log.subject or ""
                if "Printed " in subj and " label" in subj:
                    try:
                        labels = cint(subj.split("Printed ")[1].split(" label")[0])
                    except Exception:
                        pass
                if "using template " in subj:
                    try:
                        template = subj.split("using template ")[1].split(" on ")[0]
                    except Exception:
                        pass
                data = {"labels": labels, "template": template, "printer": printer, "status": status}

            labels   = cint(data.get("labels", 0))
            template = data.get("template", "Unknown") or "Unknown"
            printer  = data.get("printer", "Unknown") or "Unknown"
            status   = data.get("status", "success")

            total_labels += labels
            if status == "success" or log.status == "Success":
                success_jobs += 1
            else:
                failed_jobs += 1

            if template not in template_stats:
                template_stats[template] = {"runs": 0, "labels": 0}
            template_stats[template]["runs"]   += 1
            template_stats[template]["labels"] += labels

            if printer not in printer_stats:
                printer_stats[printer] = {"runs": 0, "labels": 0}
            printer_stats[printer]["runs"]   += 1
            printer_stats[printer]["labels"] += labels

            if len(history) < 30:
                history.append({
                    "date":     log.creation.strftime("%Y-%m-%d %H:%M"),
                    "template": template,
                    "printer":  printer,
                    "labels":   labels,
                    "status":   "Success" if (status == "success" or log.status == "Success") else "Failed"
                })

        top_template, max_temp_runs = "None", 0
        for t, s in template_stats.items():
            if s["runs"] > max_temp_runs:
                max_temp_runs = s["runs"]
                top_template  = t

        top_printer, max_print_runs = "None", 0
        for p, s in printer_stats.items():
            if s["runs"] > max_print_runs:
                max_print_runs = s["runs"]
                top_printer    = p

        return {
            "total_labels":      total_labels,
            "total_jobs":        total_jobs,
            "failed_jobs":       failed_jobs,
            "success_jobs":      success_jobs,
            "failed_percentage": round((failed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0.0,
            "top_template":      top_template,
            "top_printer":       top_printer,
            "template_stats":    template_stats,
            "printer_stats":     printer_stats,
            "history":           history
        }
    except Exception as e:
        smriti.errors.log_error(f"Error compiling print analytics: {str(e)}")
        return {
            "total_labels": 0, "total_jobs": 0, "failed_jobs": 0,
            "success_jobs": 0, "failed_percentage": 0.0,
            "top_template": "None", "top_printer": "None",
            "template_stats": {}, "printer_stats": {}, "history": []
        }


def get_template_usage_stats():
    """
    Aggregates template usage statistics from the Activity Log database table.
    """
    try:
        logs = smriti.db.get_list(
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
        smriti.errors.log_error(f"Error compiling template usage stats: {str(e)}")
        return {}
