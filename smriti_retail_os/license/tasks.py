# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/tasks.py
# @description: SMRITI Tasks — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/tasks.py
# @description: SMRITI License scheduled tasks.
#               Architecture §6a Trigger A — daily evaluation job.
#               Registered in hooks.py scheduler_events["daily"].
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md §6a
# @version: 1.0.0
#

import frappe
from frappe.utils import now_datetime


def evaluate_license_status():
    """
    Daily scheduler job — Architecture §6a Trigger A.
    Performs a full license state recalculation and persists
    the result to the SMRITI License Single DocType.
    Also logs the outcome to validation_history.

    Invoked by hooks.py:
        scheduler_events = {
            "daily": ["smriti_retail_os.license.tasks.evaluate_license_status"]
        }
    """
    try:
        if not frappe.db.exists("DocType", "SMRITI License"):
            return  # Pre-migration: DocType not yet installed

        doc = frappe.get_single("SMRITI License")

        # Capture pre-evaluation state for change detection
        prev_status = doc.license_status
        prev_health  = doc.license_health

        # _recalculate_license_state runs inside validate() on save
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        new_status = doc.license_status
        new_health  = doc.license_health

        # Log to validation_history
        remarks = f"Scheduler evaluation: {prev_status} → {new_status}"
        if prev_health != new_health:
            remarks += f" | Health: {prev_health} → {new_health}"

        doc.reload()
        doc.append("validation_history", {
            "timestamp":              now_datetime(),
            "validation_type":        "Offline",
            "result":                 new_status,
            "signature_check_result": "Not Checked",
            "remarks":                remarks,
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Log status change to activity log if it changed
        if prev_status != new_status:
            doc.reload()
            doc.append("activity_log", {
                "timestamp":    now_datetime(),
                "action":       "Changed",
                "performed_by": "Administrator",
                "result":       new_status,
                "remarks":      f"Auto-evaluated by daily scheduler. Was: {prev_status}",
            })
            doc.save(ignore_permissions=True)
            frappe.db.commit()

        frappe.logger("smriti.license").info(
            f"[SMRITI License] Daily evaluation: {prev_status} → {new_status}"
        )

    except Exception as e:
        frappe.log_error(
            title="SMRITI License — Daily Evaluation Error",
            message=frappe.get_traceback()
        )
