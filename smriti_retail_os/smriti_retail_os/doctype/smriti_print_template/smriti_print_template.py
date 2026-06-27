# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_print_template/smriti_print_template.py
# @description: Document class controller for SMRITI Print Template.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

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

    def before_save(self):
        self.compute_checksum()
        
        # Check if checksum changed
        old_checksum = self.get_db_value("template_checksum")
        if old_checksum and old_checksum != self.template_checksum:
            # Snapshot old state
            old_raw = self.get_db_value("raw_template")
            old_mappings = self.get_db_value("custom_field_mappings_json")
            old_visual = self.get_db_value("custom_visual_layout_json")
            old_version = self.get_db_value("custom_version") or "1.0.0"
            old_modified = self.get_db_value("modified")
            old_modified_by = self.get_db_value("modified_by")
            
            # Retrieve optional version label flags
            v_label = getattr(self.flags, "version_label", None)
            
            # Insert Version record
            v_doc = frappe.new_doc("SMRITI Print Template Version")
            v_doc.template = self.name
            v_doc.version_number = old_version
            v_doc.version_label = v_label
            v_doc.raw_template = old_raw
            v_doc.custom_field_mappings_json = old_mappings
            v_doc.custom_visual_layout_json = old_visual
            v_doc.template_checksum = old_checksum
            v_doc.restored_from_version = getattr(self.flags, "restored_from_version", None)
            v_doc.change_timestamp = old_modified
            v_doc.changed_by = old_modified_by
            
            v_doc.insert(ignore_permissions=True)
            
            # Log Audit: SMRITI Print Template Version Created
            try:
                frappe.get_doc({
                    "doctype": "Activity Log",
                    "user": self.modified_by or frappe.session.user,
                    "operation": "SMRITI Print Template Version Created",
                    "status": "Success",
                    "subject": f"Created version {old_version} of template {self.template_title}",
                    "remarks": f"Template: {self.name}, Version: {old_version}, Checksum: {old_checksum}"
                }).insert(ignore_permissions=True)
            except Exception as le:
                frappe.log_error(f"Error logging version created: {str(le)}")
                
            # If user didn't explicitly override version, auto-increment the patch level
            if self.custom_version == old_version and not getattr(self.flags, "ignore_version_increment", False):
                self.custom_version = self.increment_version(old_version)
                
        elif not old_checksum:
            self.custom_version = "1.0.0"

    def increment_version(self, version_str):
        if not version_str:
            return "1.0.0"
        parts = version_str.split('.')
        if len(parts) == 3:
            try:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{major}.{minor}.{patch + 1}"
            except ValueError:
                pass
        return version_str + ".1"

    def compute_checksum(self):
        import hashlib
        raw = self.raw_template or ""
        mappings = self.custom_field_mappings_json or ""
        visual = self.custom_visual_layout_json or ""
        content = f"{raw}:{mappings}:{visual}"
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
