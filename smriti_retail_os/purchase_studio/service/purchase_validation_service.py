# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Validation Service
# Integrating with the SMRITI Foundation SDK Custom Exceptions

import frappe
from frappe import _
from frappe.utils import flt
from smriti_foundation.common import SmritiValidationError

class PurchaseValidationService:
	@staticmethod
	def validate_po(po_doc):
		"""Validates SMRITI Purchase Order integrity rules using SDK exceptions."""
		if not po_doc.supplier:
			raise SmritiValidationError(_("Supplier is required."))
		
		# Check supplier exists
		if not frappe.db.exists("SMRITI Supplier", po_doc.supplier):
			raise SmritiValidationError(_("Supplier '{0}' not found.").format(po_doc.supplier))
		
		# Check supplier disabled
		disabled = frappe.db.get_value("SMRITI Supplier", po_doc.supplier, "disabled")
		if disabled:
			raise SmritiValidationError(_("Supplier '{0}' is disabled.").format(po_doc.supplier))
			
		if not po_doc.get("items"):
			raise SmritiValidationError(_("Items table cannot be empty."))
			
		for item in po_doc.items:
			if not item.item_code:
				raise SmritiValidationError(_("Item Code is required on all rows."))
			if flt(item.qty) <= 0:
				raise SmritiValidationError(_("Quantity must be greater than 0 for item '{0}'.").format(item.item_code))
			if flt(item.rate) < 0:
				raise SmritiValidationError(_("Rate cannot be negative for item '{0}'.").format(item.item_code))

	@staticmethod
	def validate_state_change(current_state, target_state):
		"""Enforces SMRITI Purchase Order independent workflow transitions."""
		if current_state == target_state:
			return

		valid_transitions = {
			"Draft": ["Submitted", "Cancelled"],
			"Submitted": ["Approved", "Rejected", "Cancelled"],
			"Approved": ["Ordered", "Cancelled"],
			"Ordered": ["Partially Received", "Completed", "Closed"],
			"Partially Received": ["Partially Received", "Completed", "Closed"],
			"Completed": ["Closed"],
			"Rejected": [],
			"Closed": [],
			"Cancelled": []
		}

		allowed = valid_transitions.get(current_state or "Draft", [])
		if target_state not in allowed:
			raise SmritiValidationError(_("Workflow Transition Denied: Cannot move from state '{0}' to '{1}'.").format(
				current_state or "Draft", target_state
			))
