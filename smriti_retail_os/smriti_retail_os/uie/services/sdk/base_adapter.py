# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

class BaseAdapter:
	"""Standard interface for UIE adapters."""
	
	def validate(self, payload, schema=None):
		"""Validates the payload. Default implementation returns True."""
		return True

	def authenticate(self, credential):
		"""Resolves and injects credentials/headers for outbound request."""
		return {}

	def send(self, queue_item, integration, endpoint):
		"""Transmits the payload to the partner system.
		Returns (success, http_status, response_content).
		"""
		raise NotImplementedError("Adapter must implement send.")

	def verify(self, queue_item, integration, endpoint):
		"""Verifies if the transaction was successfully received in target system (idempotency check)."""
		return False
