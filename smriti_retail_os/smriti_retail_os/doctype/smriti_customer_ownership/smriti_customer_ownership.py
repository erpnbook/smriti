# -*- coding: utf-8 -*-
#
# @file: smriti_customer_ownership.py
# @description: Document controller class for SMRITI Customer Ownership.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days

class SMRITICustomerOwnership(Document):
    def validate(self):
        # 1. Primary and secondary owners cannot be identical
        if self.primary_owner and self.secondary_owner and self.primary_owner == self.secondary_owner:
            frappe.throw(
                _("Primary Owner and Secondary Owner cannot be the same employee ({0}).").format(self.primary_owner),
                frappe.ValidationError
            )
            
        # 2. Date validations
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw(
                    _("Start Date ({0}) cannot be after End Date ({1}).").format(self.start_date, self.end_date),
                    frappe.ValidationError
                )
                
        # 3. Deactivate previous active ownership timelines on insert/save (Rule SFM-GOV-001)
        if self.is_active:
            self.deactivate_previous_ownerships()

    def deactivate_previous_ownerships(self):
        # Find all other active ownership records for the same customer + company
        filters = {
            "customer": self.customer,
            "company": self.company,
            "is_active": 1,
            "name": ["!=", self.name]
        }
        previous_records = frappe.get_all("SMRITI Customer Ownership", filters=filters, fields=["name", "start_date"])
        
        yesterday = add_days(self.start_date or frappe.utils.nowdate(), -1)
        
        for r in previous_records:
            doc = frappe.get_doc("SMRITI Customer Ownership", r.name)
            doc.is_active = 0
            doc.end_date = yesterday
            doc.save(ignore_permissions=True)
