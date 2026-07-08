"""
install_srle_layout_prefs_field.py
-----------------------------------
SMRITI Retail OS — SRLE Layout Engine (v1.0)
Migration patch: creates the smriti_layout_prefs Custom Field on the
Frappe User doctype. This enables cross-device SRLE preference persistence
via layout_service.py.

Safe to run multiple times (idempotent via exists check).

Copyright (c) 2026 AITDL NETWORK. All rights reserved.
"""

import frappe


def execute():
    field_name = "User-smriti_layout_prefs"

    if frappe.db.exists("Custom Field", field_name):
        frappe.logger().info(f"SRLE patch: Custom Field '{field_name}' already exists — skipped.")
        return

    custom_field = frappe.get_doc({
        "doctype":     "Custom Field",
        "name":        field_name,
        "dt":          "User",
        "fieldname":   "smriti_layout_prefs",
        "label":       "SMRITI Layout Preferences",
        "fieldtype":   "Small Text",
        "insert_after": "last_active",
        "read_only":   1,
        "hidden":      1,
        "description": (
            "Stores SMRITI Retail OS Layout Engine (SRLE) preferences as a JSON blob. "
            "Managed automatically by the platform — do not edit manually."
        ),
        "module": "Smriti Retail OS",
    })
    custom_field.insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.logger().info(f"SRLE patch: Custom Field '{field_name}' created successfully.")
