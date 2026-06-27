# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_saved_view/smriti_saved_view.py
# @description: Document class controller for SMRITI Saved View.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-18
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import json
import frappe
from frappe.model.document import Document

class SMRITISavedView(Document):
    def validate(self):
        # 1. Uniqueness check for (user, report_template, view_name)
        duplicate = frappe.db.exists("SMRITI Saved View", {
            "user": self.user,
            "report_template": self.report_template,
            "view_name": self.view_name,
            "name": ["!=", self.name]
        })
        if duplicate:
            frappe.throw(
                frappe._("Saved View with name '{0}' already exists for this report template.")
                .format(self.view_name),
                frappe.ValidationError
            )
            
        # 2. JSON format validation of applied_filters_json and visible_columns_json
        for field in ["applied_filters_json", "visible_columns_json"]:
            val = self.get(field)
            if val:
                try:
                    json.loads(val)
                except Exception:
                    frappe.throw(
                        frappe._("Invalid JSON format in field '{0}'.")
                        .format(self.meta.get_label(field) if self.meta else field),
                        frappe.ValidationError
                    )
                    
        # 3. Ownership check on edit/write
        if not self.is_new():
            db_user = frappe.db.get_value("SMRITI Saved View", self.name, "user")
            if db_user != frappe.session.user and "System Manager" not in frappe.get_roles():
                frappe.throw(frappe._("Not authorized to modify this saved view."), frappe.PermissionError)

    def on_trash(self):
        # 4. Ownership check on delete
        if self.user != frappe.session.user and "System Manager" not in frappe.get_roles():
            frappe.throw(frappe._("Not authorized to delete this saved view."), frappe.PermissionError)

