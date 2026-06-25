# -*- coding: utf-8 -*-
#
# @file: smriti_psv_exam_attempt.py
# @description: Document controller class for SMRITI PSV Exam Attempt.
#               Validates attempts, enforces single-active-attempt rule, and locks completed attempts.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-23
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
import uuid

class SMRITIPSVExamAttempt(Document):
    def autoname(self):
        self.attempt_id = f"PSV-ATT-{str(uuid.uuid4())[:8].upper()}"
        self.name = self.attempt_id

    def validate(self):
        # 1. Enforce single active attempt constraint (1 active attempt per exam per user)
        if self.is_new() and self.status == "In Progress":
            active_attempt = frappe.db.get_value(
                "SMRITI PSV Exam Attempt",
                filters={
                    "user": self.user,
                    "exam_id": self.exam_id,
                    "status": "In Progress"
                },
                fieldname="name"
            )
            if active_attempt:
                frappe.throw(
                    _("You already have an active exam attempt for this exam ({0}). Please complete or cancel it before starting a new one.").format(active_attempt),
                    frappe.ValidationError
                )

        # 2. Lock completed attempts (prevent modifying passed/failed results)
        if not self.is_new():
            db_status = frappe.db.get_value("SMRITI PSV Exam Attempt", self.name, "status")
            if db_status in ("Passed", "Failed") and self.status != db_status:
                frappe.throw(
                    _("This exam attempt has already been graded and closed. It cannot be modified."),
                    frappe.ValidationError
                )
