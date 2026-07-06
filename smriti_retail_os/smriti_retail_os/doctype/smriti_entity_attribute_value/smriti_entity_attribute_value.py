# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_entity_attribute_value/smriti_entity_attribute_value.py
# @description: SMRITI DocType controller for SMRITI Entity Attribute Value.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.model.document import Document

class SMRITIEntityAttributeValue(Document):
    def validate(self):
        # 1. Fetch custom attribute definition
        attr_def = frappe.db.get_value(
            "SMRITI Custom Attribute",
            self.attribute_code,
            ["entity_type", "attribute_type", "options"],
            as_dict=True
        )
        if not attr_def:
            frappe.throw(frappe._("Custom Attribute definition '{0}' not found.").format(self.attribute_code))

        # 2. Verify that parenttype aligns with the attribute's target entity_type
        if self.parenttype != attr_def.entity_type:
            frappe.throw(
                frappe._("Attribute '{0}' is configured for entity type '{1}' but applied to '{2}'.")
                .format(self.attribute_code, attr_def.entity_type, self.parenttype)
            )

        # 3. Validate Select options if configured
        if attr_def.attribute_type == "Select" and attr_def.options:
            allowed_options = [opt.strip() for opt in attr_def.options.split(",") if opt.strip()]
            if self.attribute_value not in allowed_options:
                frappe.throw(
                    frappe._("Value '{0}' is invalid for attribute '{1}'. Allowed values are: {2}.")
                    .format(self.attribute_value, self.attribute_code, ", ".join(allowed_options))
                )
