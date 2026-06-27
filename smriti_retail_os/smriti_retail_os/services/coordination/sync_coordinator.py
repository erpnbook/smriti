# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.smriti_retail_os.services.adapters.integration_engine import get_active_adapter

class SyncCoordinator:
	"""Orchestration Coordinator for SMRITI Connectivity Framework (SCF)."""
	
	def __init__(self):
		self.adapter = get_active_adapter()

	def get_connection_status(self, settings):
		"""Checks connectivity with the target system."""
		return self.adapter.get_connection_status(settings)

	def sync_accounting(self, vouchers, settings, force=False):
		"""Orchestrates accounting synchronization."""
		return self.adapter.sync_accounting(vouchers, settings, force)

	def sync_inventory(self, items, settings, force=False):
		"""Orchestrates inventory synchronization."""
		return self.adapter.sync_inventory(items, settings, force)

	def sync_masters(self, masters, settings, force=False):
		"""Orchestrates master synchronization."""
		return self.adapter.sync_masters(masters, settings, force)

	def audit_sync(self, from_date, to_date, voucher_type):
		"""Orchestrates sync auditing."""
		return self.adapter.audit_sync(from_date, to_date, voucher_type)
