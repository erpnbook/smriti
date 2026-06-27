# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""Converts the existing SMRITI Telemetry Event Definition DocType from a Custom DocType to a Standard DocType to prevent migration clashing."""
	if frappe.db.exists("DocType", "SMRITI Telemetry Event Definition"):
		# Set custom to 0 inside tabDocType
		frappe.db.set_value("DocType", "SMRITI Telemetry Event Definition", "custom", 0, update_modified=False)
		frappe.db.commit()
		print("[SMRITI Patch] Converted SMRITI Telemetry Event Definition DocType to standard (custom=0)")
