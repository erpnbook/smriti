# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

# Author: Jawahar R. Mallah
# Designation: Founder & Chief Architect
# Organization: AITDL – AI Technology & Development Lab

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

def execute():
	"""Ensures the SMRITI UIE Sync Queue database table has an index on 'idempotency_key'."""
	table_name = "tabSMRITI UIE Sync Queue"

	# Guard: table must exist
	if not frappe.db.table_exists(table_name):
		return

	# Check if index exists on the column 'idempotency_key'
	existing = smriti.db.sql(
		"""
		SELECT COUNT(*) 
		FROM information_schema.statistics
		WHERE table_schema = DATABASE()
		  AND table_name = %s
		  AND column_name = 'idempotency_key'
		""",
		(table_name,)
	)

	if not existing or existing[0][0] == 0:
		try:
			smriti.db.sql(
				f"""
				ALTER TABLE `{table_name}`
				ADD INDEX `idempotency_key_idx` (`idempotency_key`)
				"""
			)
			frappe.logger().info(
				f"[UIE Patch] Index `idempotency_key_idx` created successfully on `{table_name}`."
			)
		except Exception as e:
			frappe.logger().warning(
				f"[UIE Patch] Failed to add index on `{table_name}`: {str(e)}"
			)
