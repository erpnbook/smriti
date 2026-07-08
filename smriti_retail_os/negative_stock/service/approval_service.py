# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/negative_stock/service/approval_service.py
# @description: 2-tier Approval service for SMRITI Negative Stock Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import now_datetime

class SMRITINegativeStockApprovalService(object):
	"""
	Manages case approval lifecycle transitions:
	Open -> Pending Approval -> Approved / Rejected -> Closed
	"""

	def __init__(self, case_id):
		self.case_id = case_id
		self.case_doc = smriti.documents.get("SMRITI Negative Stock Case", self.case_id)

	def submit_for_approval(self, user_id=None):
		"""
		Transitions case to Pending Approval state.
		"""
		if self.case_doc.status != "Open":
			frappe.throw(frappe._("Case {0} must be in 'Open' status to request approval.").format(self.case_id))

		self.case_doc.status = "Pending Approval"
		self.case_doc.requested_by = user_id or frappe.session.user
		self.case_doc.save(ignore_permissions=True)
		smriti.db.commit()

		# Optional: Send notification to Store Manager role users
		self.notify_approvers()
		return self.case_doc

	def approve(self, approver_user, comment=None, reference=None):
		"""
		Approves the negative stock allowance request.
		"""
		if self.case_doc.status != "Pending Approval":
			frappe.throw(frappe._("Case {0} is not pending approval.").format(self.case_id))

		# Validate that the user is not the same as requested_by to prevent self-approval (if not System Manager)
		if self.case_doc.requested_by == approver_user and not "System Manager" in frappe.get_roles(approver_user):
			frappe.throw(frappe._("Approver cannot be the same as the requester."))

		self.case_doc.status = "Approved"
		self.case_doc.approved_by = approver_user
		self.case_doc.approval_timestamp = now_datetime()
		self.case_doc.approval_comment = comment or "Approved via SMRITI Approval Panel"
		self.case_doc.approval_action = "Approve"
		self.case_doc.approval_level = "Store Manager"
		self.case_doc.approval_reference = reference

		self.case_doc.save(ignore_permissions=True)
		smriti.db.commit()

		return self.case_doc

	def reject(self, approver_user, comment=None):
		"""
		Rejects the negative stock allowance request.
		"""
		if self.case_doc.status != "Pending Approval":
			frappe.throw(frappe._("Case {0} is not pending approval.").format(self.case_id))

		self.case_doc.status = "Rejected"
		self.case_doc.approved_by = approver_user
		self.case_doc.approval_timestamp = now_datetime()
		self.case_doc.approval_comment = comment or "Rejected via SMRITI Approval Panel"
		self.case_doc.approval_action = "Reject"
		self.case_doc.approval_level = "Store Manager"

		self.case_doc.save(ignore_permissions=True)
		smriti.db.commit()

		return self.case_doc

	def notify_approvers(self):
		"""
		Sends an alert to users with role 'SMRITI Store Manager' or 'System Manager'.
		"""
		# Log a message for background audit/real-time notification layer integration
		frappe.logger().info(f"[SMRITI SNSM] Approval requested for Case {self.case_id}. Item: {self.case_doc.item_code}, Qty: {self.case_doc.negative_qty}")
