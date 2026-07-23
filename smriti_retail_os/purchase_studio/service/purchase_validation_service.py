# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Validation Service

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt


# Local alias — smriti_foundation is not a deployed package; ValidationError
# raised by this service is identical to frappe.ValidationError so all callers
# can catch either type without changes.
class SmritiValidationError(frappe.ValidationError):
	"""SMRITI business validation exception raised by the purchase validation layer."""
	pass

class PurchaseValidationService:
	@staticmethod
	def validate_po(po_doc):
		"""Validates SMRITI Purchase Order integrity rules using SDK exceptions."""
		if not po_doc.supplier:
			raise SmritiValidationError(_("Supplier is required."))
		
		# Check supplier exists in either SMRITI Supplier or standard Supplier DocType
		if not smriti.db.exists("SMRITI Supplier", po_doc.supplier) and not smriti.db.exists("Supplier", po_doc.supplier):
			raise SmritiValidationError(_("Supplier '{0}' not found.").format(po_doc.supplier))
		
		# Check supplier disabled
		disabled = 0
		if smriti.db.exists("SMRITI Supplier", po_doc.supplier):
			disabled = smriti.db.get("SMRITI Supplier", po_doc.supplier, "disabled")
		elif smriti.db.exists("Supplier", po_doc.supplier):
			disabled = smriti.db.get("Supplier", po_doc.supplier, "disabled")

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
