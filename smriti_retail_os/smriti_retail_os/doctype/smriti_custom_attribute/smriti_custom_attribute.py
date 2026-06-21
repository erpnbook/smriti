# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_custom_attribute/smriti_custom_attribute.py
# @description: SMRITI DocType controller for SMRITI Custom Attribute.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import re
import frappe
from frappe.model.document import Document

class SMRITICustomAttribute(Document):
    def validate(self):
        # Format/character check on attribute_code (uppercase alphanumeric and underscores only)
        self.attribute_code = str(self.attribute_code).strip().upper()
        if not re.match(r"^[A-Z0-9_]+$", self.attribute_code):
            frappe.throw(
                frappe._("Attribute Code '{0}' is invalid. Only uppercase alphanumeric characters and underscores are allowed.")
                .format(self.attribute_code)
            )

        # Enforce that options exist if type is Select
        if self.attribute_type == "Select" and not self.options:
            frappe.throw(frappe._("Options are required when Attribute Type is set to 'Select'."))
