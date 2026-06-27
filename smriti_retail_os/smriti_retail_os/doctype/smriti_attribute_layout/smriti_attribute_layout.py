# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_attribute_layout/smriti_attribute_layout.py
# @description: Document class controller for SMRITI Attribute Layout.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: MIT
#

import frappe
from frappe.model.document import Document
from frappe import _

class SMRITIAttributeLayout(Document):
    def validate(self):
        # Layer 1 Uniqueness Enforcement: Ensure only one layout entry per company + attribute_id
        duplicate = frappe.db.exists(
            "SMRITI Attribute Layout",
            {
                "company": self.company,
                "attribute_id": self.attribute_id,
                "name": ["!=", self.name]
            }
        )
        if duplicate:
            frappe.throw(
                _("Uniqueness Violation: Attribute '{0}' is already configured for Company '{1}'.").format(
                    self.attribute_id, self.company
                ),
                frappe.ValidationError
            )
