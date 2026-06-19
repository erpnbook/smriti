# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_business_term/smriti_business_term.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document

class SMRITIBusinessTerm(Document):
    def validate(self):
        # 1. Uniqueness of term_id + term_version
        duplicate = frappe.db.exists(
            "SMRITI Business Term",
            {
                "term_id": self.term_id,
                "term_version": self.term_version,
                "name": ["!=", self.name]
            }
        )
        if duplicate:
            frappe.throw(
                frappe._("A business term definition already exists for ID {0} and version {1} ({2}).")
                .format(self.term_id, self.term_version, duplicate)
            )

        # 2. Status constraint: only 'Approved' terms can be active
        if self.is_active and self.status != "Approved":
            frappe.throw(
                frappe._("Only 'Approved' terms can be marked as Active. Current status is '{0}'.")
                .format(self.status)
            )

        # 3. JSON format validation for term_aliases
        if self.term_aliases:
            try:
                parsed = json.loads(self.term_aliases)
                if not isinstance(parsed, list):
                    frappe.throw(frappe._("Term Aliases must be a valid JSON array of strings."))
            except ValueError:
                frappe.throw(frappe._("Term Aliases must be a valid JSON array string."))

        # 4. JSON format validation for faq
        if self.faq:
            try:
                parsed = json.loads(self.faq)
                if not isinstance(parsed, list):
                    frappe.throw(frappe._("FAQ must be a valid JSON array."))
            except ValueError:
                frappe.throw(frappe._("FAQ must be a valid JSON array string."))

        # 5. JSON format validation for common_mistakes
        if self.common_mistakes:
            try:
                parsed = json.loads(self.common_mistakes)
                if not isinstance(parsed, list):
                    frappe.throw(frappe._("Common Mistakes must be a valid JSON array."))
            except ValueError:
                frappe.throw(frappe._("Common Mistakes must be a valid JSON array string."))

    def on_update(self):
        frappe.cache().delete_value(f"smriti:dictionary:{self.term_id}:{self.term_version}")
        frappe.cache().delete_value(f"smriti:dictionary:{self.term_id}:latest")
        frappe.enqueue(
            "smriti_retail_os.services.knowledge_service.rebuild_knowledge_index",
            queue="short",
            now=frappe.flags.in_test
        )

    def on_trash(self):
        frappe.cache().delete_value(f"smriti:dictionary:{self.term_id}:{self.term_version}")
        frappe.cache().delete_value(f"smriti:dictionary:{self.term_id}:latest")
        frappe.enqueue(
            "smriti_retail_os.services.knowledge_service.rebuild_knowledge_index",
            queue="short",
            now=frappe.flags.in_test
        )
