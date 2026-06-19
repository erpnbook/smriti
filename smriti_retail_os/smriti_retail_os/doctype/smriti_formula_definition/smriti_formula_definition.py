# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_formula_definition/smriti_formula_definition.py
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

import json
import frappe
from frappe.model.document import Document

class SMRITIFormulaDefinition(Document):
    def validate(self):
        # 1. Uniqueness of formula_id + formula_version
        duplicate = frappe.db.exists(
            "SMRITI Formula Definition",
            {
                "formula_id": self.formula_id,
                "formula_version": self.formula_version,
                "name": ["!=", self.name]
            }
        )
        if duplicate:
            frappe.throw(
                frappe._("A formula definition already exists for ID {0} and version {1} ({2}).")
                .format(self.formula_id, self.formula_version, duplicate)
            )

        # 2. Status constraint: only 'Approved' formulas can be active
        if self.is_active and self.status != "Approved":
            frappe.throw(
                frappe._("Only 'Approved' formulas can be marked as Active. Current status is '{0}'.")
                .format(self.status)
            )

        # 3. JSON format validation for explainability_json
        if self.explainability_json:
            try:
                json.loads(self.explainability_json)
            except ValueError:
                frappe.throw(frappe._("Explainability JSON must be a valid JSON string."))

        # 4. JSON format validation for dependent_features
        if self.dependent_features:
            try:
                json.loads(self.dependent_features)
            except ValueError:
                frappe.throw(frappe._("Dependent Features must be a valid JSON array or object."))
