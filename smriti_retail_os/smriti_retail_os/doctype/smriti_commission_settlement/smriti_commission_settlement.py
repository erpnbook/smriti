# -*- coding: utf-8 -*-
#
# @file: smriti_commission_settlement.py
# @description: Document controller class for SMRITI Commission Settlement.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

class SMRITICommissionSettlement(Document):
    def validate(self):
        # 1. Enforce uniqueness: one settlement per employee, company, fiscal_year, month
        duplicate = frappe.db.exists("SMRITI Commission Settlement", {
            "employee": self.employee,
            "company": self.company,
            "fiscal_year": self.fiscal_year,
            "month": self.month,
            "name": ["!=", self.name]
        })
        if duplicate:
            frappe.throw(
                _("A SMRITI Commission Settlement already exists for Employee {0} in {1} ({2}) for {3}.")
                .format(self.employee, self.fiscal_year, self.month, self.company),
                frappe.ValidationError
            )

        # 2. Immutability checks
        if not self.is_new():
            db_status = frappe.db.get_value("SMRITI Commission Settlement", self.name, "status")
            if db_status in ["Approved", "Paid"]:
                if db_status == "Paid":
                    frappe.throw(
                        _("Paid Commission Settlements are completely locked and cannot be edited."),
                        frappe.ValidationError
                    )
                # If status is Approved, only allow transition to Paid, block other changes
                if db_status == "Approved" and self.status == "Draft":
                    frappe.throw(
                        _("Approved Commission Settlements cannot be reverted back to Draft."),
                        frappe.ValidationError
                    )
                # Check if other fields are modified
                db_doc = frappe.get_doc("SMRITI Commission Settlement", self.name)
                for field in ["employee", "company", "fiscal_year", "month", "gross_commission"]:
                    if self.get(field) != db_doc.get(field):
                        frappe.throw(
                            _("Field '{0}' is read-only because the settlement is already {1}.").format(field, db_status),
                            frappe.ValidationError
                        )
                # Also prevent editing adjustments
                if len(self.adjustments or []) != len(db_doc.adjustments or []):
                    frappe.throw(_("Manual adjustments cannot be modified on approved settlements."), frappe.ValidationError)
                for a1, a2 in zip(self.adjustments or [], db_doc.adjustments or []):
                    if a1.amount != a2.amount or a1.reason != a2.reason:
                        frappe.throw(_("Manual adjustments cannot be modified on approved settlements."), frappe.ValidationError)

        # 3. Auto calculate net_commission and settled_commission_amount
        adj_total = sum(flt(row.amount) for row in (self.adjustments or []))
        self.net_commission = flt(self.gross_commission or 0.0) + adj_total
        self.settled_commission_amount = self.net_commission

        # Populate date range if missing
        if not self.settlement_from_date or not self.settlement_to_date:
            from smriti_retail_os.sfm.service.target_service import get_month_date_range
            try:
                start_date, end_date = get_month_date_range(self.fiscal_year, self.month)
                self.settlement_from_date = start_date
                self.settlement_to_date = end_date
            except Exception:
                pass

        # 4. If Paid, validate payment details
        if self.status == "Paid":
            if not self.payment_date:
                self.payment_date = nowdate()
            if not self.payment_reference:
                frappe.throw(_("Payment Reference is required when marking settlement as Paid."), frappe.ValidationError)

        # 5. Populate adjustment approvals for new adjustments
        for row in (self.adjustments or []):
            if not row.approved_by:
                row.approved_by = frappe.session.user
            if not row.approved_on:
                row.approved_on = nowdate()
