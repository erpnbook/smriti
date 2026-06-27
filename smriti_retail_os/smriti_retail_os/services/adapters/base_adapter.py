# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

class BaseAdapter:
	"""Abstract base class defining the standard interface for SCF adapters."""
	
	def __init__(self, name="BaseAdapter"):
		self.name = name

	def get_connection_status(self, settings):
		"""Verifies connection with target system and returns status dict."""
		raise NotImplementedError("Adapter must implement get_connection_status.")

	def sync_accounting(self, vouchers, settings, force=False):
		"""Syncs accounting vouchers (invoices, payments, returns, etc.).
		Returns standard adapter response dict.
		"""
		raise NotImplementedError("Adapter must implement sync_accounting.")

	def sync_inventory(self, items, settings, force=False):
		"""Syncs inventory (item details, stock positions, godowns, journals).
		Returns standard adapter response dict.
		"""
		raise NotImplementedError("Adapter must implement sync_inventory.")

	def sync_masters(self, masters, settings, force=False):
		"""Syncs master data (customers, suppliers, accounts, cost centres).
		Returns standard adapter response dict.
		"""
		raise NotImplementedError("Adapter must implement sync_masters.")

	def audit_sync(self, from_date, to_date, voucher_type):
		"""Compares SMRITI transactions against target system records to find deltas/missing.
		Returns standard health status metrics dict.
		"""
		raise NotImplementedError("Adapter must implement audit_sync.")
