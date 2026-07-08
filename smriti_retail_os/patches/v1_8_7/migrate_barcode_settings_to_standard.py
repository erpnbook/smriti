# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

def execute():
	"""Converts the existing SMRITI Barcode Settings DocType from a Custom DocType to a Standard DocType to prevent migration clashing."""
	if smriti.db.exists("DocType", "SMRITI Barcode Settings"):
		# Set custom to 0 inside tabDocType
		smriti.db.set_value("DocType", "SMRITI Barcode Settings", "custom", 0, update_modified=False)
		smriti.db.commit()
		print("[SMRITI Patch] Converted SMRITI Barcode Settings DocType to standard (custom=0)")
