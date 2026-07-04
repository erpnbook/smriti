# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/negative_stock/service/recovery_service.py
# @description: Recovery checker engine service for SMRITI Negative Stock Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import now_datetime

class SMRITINegativeStockRecoveryService(object):
	"""
	Monitors and processes negative stock recoveries:
	- Listens to transaction submit events (Purchase Receipt, Stock Entry, Stock Reconciliation, Material Transfer).
	- Validates current ledger status and updates Cases to 'Recovered' or 'Closed'.
	"""

	def __init__(self, item_code=None, warehouse=None):
		self.item_code = item_code
		self.warehouse = warehouse

	def check_and_recover(self, source_doctype=None, source_name=None, recovery_type="Auto"):
		"""
		Checks if current stock balance is >= 0 and triggers recovery updates.
		"""
		if not self.item_code or not self.warehouse:
			return

		# Get current actual stock from ERPNext Stock Ledger
		actual_qty = frappe.db.get_value("Bin", {
			"item_code": self.item_code,
			"warehouse": self.warehouse
		}, "actual_qty") or 0.0

		if actual_qty >= 0:
			# Find all cases for this item + warehouse that are Open, Approved, or Pending Approval
			open_cases = frappe.get_all("SMRITI Negative Stock Case", filters={
				"item_code": self.item_code,
				"warehouse": self.warehouse,
				"status": ["in", ["Open", "Approved", "Pending Approval"]]
			}, fields=["name", "negative_qty", "status"])

			for case in open_cases:
				# Trigger recovery document insertion
				rec = frappe.new_doc("SMRITI Negative Stock Recovery")
				rec.case_id = case.name
				rec.recovered_qty = abs(case.negative_qty)
				rec.recovery_source_doctype = source_doctype or "Stock Ledger"
				rec.recovery_source_name = source_name or "Stock Ledger Check"
				rec.recovery_type = recovery_type
				rec.recovery_source = self.map_recovery_source(source_doctype)
				rec.resolved_at = now_datetime()
				rec.insert(ignore_permissions=True)

				# Update Case status to 'Recovered'
				frappe.db.set_value("SMRITI Negative Stock Case", case.name, {
					"status": "Recovered",
					"recovery_reference": rec.name
				})
				
				# Commit the updates
				frappe.db.commit()

				frappe.logger().info(f"[SMRITI SNSM] Case {case.name} successfully recovered via {source_doctype} {source_name}. Current balance: {actual_qty}")

	def map_recovery_source(self, doctype):
		if doctype in ["Purchase Receipt", "Stock Entry", "Stock Reconciliation", "Material Transfer"]:
			return doctype
		# Default map
		if doctype == "Stock Entry":
			return "Stock Entry"
		return "Stock Entry" # Default fallback for miscellaneous movements

	@staticmethod
	def run_scheduler_safety_net():
		"""
		Background task scheduled daily to sweep and recover any orphaned negative stock cases.
		"""
		# Get all cases that are Open or Approved
		cases = frappe.get_all("SMRITI Negative Stock Case", filters={
			"status": ["in", ["Open", "Approved", "Pending Approval"]]
		}, fields=["name", "item_code", "warehouse", "negative_qty"])

		for case in cases:
			srv = SMRITINegativeStockRecoveryService(case.item_code, case.warehouse)
			srv.check_and_recover(source_doctype="Stock Entry", source_name="Daily Scheduler Safety Sweep", recovery_type="Scheduler")


def run_safety_net():
	"""
	Module-level entry point for the scheduler and for `bench execute`.

	KI-003 fix: Frappe's scheduler/get_attr resolution (frappe.utils.get_attr)
	splits a hook string on the LAST dot into (module_path, attr_name) and does
	`importlib.import_module(module_path)`. A path ending in
	"...recovery_service.SMRITINegativeStockRecoveryService.run_scheduler_safety_net"
	resolves module_path to "...recovery_service.SMRITINegativeStockRecoveryService",
	which is a class, not an importable module -> ImportError at every migrate/scheduler tick.

	This wrapper is a plain module-level function so the hook path is
	"smriti_retail_os.negative_stock.service.recovery_service.run_safety_net"
	(module_path = "...recovery_service", attr_name = "run_safety_net"), which
	resolves correctly. It simply delegates to the existing classmethod so no
	business logic is duplicated.
	"""
	SMRITINegativeStockRecoveryService.run_scheduler_safety_net()
