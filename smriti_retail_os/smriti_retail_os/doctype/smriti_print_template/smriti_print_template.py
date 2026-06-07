# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_print_template/smriti_print_template.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class SMRITIPrintTemplate(Document):
    def autoname(self):
        # Allow explicit setting (like in seeding), otherwise generate slug from template_title
        if not self.name and self.template_title:
            import re
            val = self.template_title
            clean = re.sub(r'[^a-zA-Z0-9\-]', '_', val)
            clean = re.sub(r'_+', '_', clean)
            self.name = clean.strip('_').upper()

    def validate(self):
        self.validate_template_size()
        self.validate_mappings_json()
        self.compute_checksum()

    def compute_checksum(self):
        import hashlib
        raw = self.raw_template or ""
        mappings = self.custom_field_mappings_json or ""
        content = f"{raw}:{mappings}"
        self.template_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()

    def validate_template_size(self):
        MAX_TEMPLATE_SIZE = 100 * 1024
        raw = self.raw_template or ""
        if len(raw.encode("utf-8")) > MAX_TEMPLATE_SIZE:
            frappe.throw(
                _("Template exceeds 100KB limit"),
                title=_("Template Too Large")
            )

    def validate_mappings_json(self):
        if self.custom_field_mappings_json:
            try:
                import json
                parsed = json.loads(self.custom_field_mappings_json)
                if not isinstance(parsed, list):
                    frappe.throw(_("Field Mappings JSON must be a JSON array of mappings."))
            except ValueError:
                frappe.throw(_("Invalid Field Mappings JSON format."))
