# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_negative_stock.py
# @description: Unit tests for SMRITI Negative Stock Management rules and services.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import unittest
import frappe
from smriti_retail_os import smriti
from frappe.utils import today, add_days
from smriti_retail_os.negative_stock.service.policy_resolver import SMRITINegativeStockPolicyResolver
from smriti_retail_os.negative_stock.service.approval_service import SMRITINegativeStockApprovalService
from smriti_retail_os.negative_stock.service.recovery_service import SMRITINegativeStockRecoveryService
from smriti_retail_os.negative_stock.api.negative_stock_api import validate_negative_stock, approve_case, reject_case

class TestSMRITINegativeStock(unittest.TestCase):

	def setUp(self):
		# Clean existing test data to ensure isolated test environment
		smriti.db.delete("SMRITI Negative Stock Policy")
		smriti.db.delete("SMRITI Negative Stock Case")
		smriti.db.delete("SMRITI Negative Stock Recovery")
		smriti.db.commit()

		self.test_company = "_Test Company"
		self.test_item = "_Test Item"
		self.test_item_group = "All Item Groups"

		# Create test company if it doesn't exist
		if not smriti.db.exists("Company", self.test_company):
			doc = smriti.documents.new("Company")
			doc.company_name = self.test_company
			doc.default_currency = "INR"
			doc.abbr = "TC"
			doc.insert()

		abbr = smriti.db.get("Company", self.test_company, "abbr") or "TC"
		self.test_warehouse = f"Stores - {abbr}"

		if not smriti.db.exists("Warehouse", self.test_warehouse):
			# Delete conflicting warehouse
			smriti.db.delete("Warehouse", {"warehouse_name": "Stores", "company": self.test_company})
			doc = smriti.documents.new("Warehouse")
			doc.warehouse_name = "Stores"
			doc.company = self.test_company
			doc.insert()

		if not smriti.db.exists("GST HSN Code", "999900"):
			hsn = smriti.documents.new("GST HSN Code")
			hsn.name = "999900"
			hsn.hsn_code = "999900"
			hsn.description = "Test HSN Code"
			hsn.insert()

		if not smriti.db.exists("Item", self.test_item):
			doc = smriti.documents.new("Item")
			doc.item_code = self.test_item
			doc.item_name = "_Test Item"
			doc.item_group = self.test_item_group
			doc.is_stock_item = 1
			doc.gst_hsn_code = "999900"
			doc.insert()

	def tearDown(self):
		smriti.db.delete("SMRITI Negative Stock Policy")
		smriti.db.delete("SMRITI Negative Stock Case")
		smriti.db.delete("SMRITI Negative Stock Recovery")
		smriti.db.commit()

	def test_policy_resolution_hierarchy(self):
		"""
		Verifies hierarchical resolution: Item Group (with low priority) vs Global (with high priority).
		Item Group should win because of higher specificity in the hierarchy.
		"""
		# Global Policy (Priority 100) -> Allow + Reason
		p_global = smriti.documents.new("SMRITI Negative Stock Policy")
		p_global.apply_to = "Global"
		p_global.policy_mode = "Allow + Reason"
		p_global.priority = 100
		p_global.is_active = 1
		p_global.insert()

		# Item Group Policy (Priority 10) -> Block
		p_group = smriti.documents.new("SMRITI Negative Stock Policy")
		p_group.apply_to = "Item Group"
		p_group.item_group = self.test_item_group
		p_group.policy_mode = "Block"
		p_group.priority = 10
		p_group.is_active = 1
		p_group.insert()

		resolver = SMRITINegativeStockPolicyResolver(self.test_item, self.test_warehouse, self.test_company)
		resolved = resolver.resolve()

		# Assert that Item Group policy is selected because of specificity hierarchy
		self.assertEqual(resolved.apply_to, "Item Group")
		self.assertEqual(resolved.policy_mode, "Block")

	def test_policy_resolution_priority(self):
		"""
		Verifies priority-based conflict resolution at same hierarchy level.
		"""
		# Policy A (Priority 10) -> Warn
		p_a = smriti.documents.new("SMRITI Negative Stock Policy")
		p_a.apply_to = "Global"
		p_a.policy_mode = "Warn"
		p_a.priority = 10
		p_a.is_active = 1
		p_a.insert()

		# Policy B (Priority 50) -> Block
		p_b = smriti.documents.new("SMRITI Negative Stock Policy")
		p_b.apply_to = "Global"
		p_b.policy_mode = "Block"
		p_b.priority = 50
		p_b.is_active = 1
		p_b.insert()

		resolver = SMRITINegativeStockPolicyResolver(self.test_item, self.test_warehouse, self.test_company)
		resolved = resolver.resolve()

		# Assert that Priority 50 policy wins
		self.assertEqual(resolved.policy_mode, "Block")

	def test_case_approval_flow(self):
		"""
		Verifies the 2-tier approval workflow lifecycle.
		"""
		# Policy allowing negative stock with approval
		p = smriti.documents.new("SMRITI Negative Stock Policy")
		p.apply_to = "Global"
		p.policy_mode = "Allow + Reason"
		p.approval_required = 1
		p.priority = 0
		p.is_active = 1
		p.insert()

		# Trigger negative stock case generation via validation API
		res = validate_negative_stock(self.test_item, self.test_warehouse, self.test_company, 5.0)
		case_id = res["case_id"]

		self.assertEqual(res["status"], "Pending Approval")

		# Approve case
		app_res = approve_case(case_id, comment="Approved for immediate dispatch", reference="PO-1002")
		self.assertEqual(app_res["status"], "Approved")

		case_status = smriti.db.get("SMRITI Negative Stock Case", case_id, "status")
		self.assertEqual(case_status, "Approved")

	def test_kgf_explainability(self):
		"""
		Verifies that KGF explainability logs are generated with worked examples.
		"""
		p = smriti.documents.new("SMRITI Negative Stock Policy")
		p.apply_to = "Global"
		p.policy_mode = "Warn"
		p.priority = 10
		p.is_active = 1
		p.insert()

		res = validate_negative_stock(self.test_item, self.test_warehouse, self.test_company, 12.0)
		explanation = res["explanation"]

		self.assertIn("SMRITI NEGATIVE STOCK EXCEPTION TRACE LOG", explanation)
		self.assertIn("Worked Example:", explanation)
		self.assertIn("Global", explanation)

	def test_event_driven_recovery(self):
		"""
		Verifies that recovery engine triggers when balance returns positive.
		"""
		# Create a negative stock case
		case_doc = smriti.documents.new("SMRITI Negative Stock Case")
		case_doc.name = "NS/TEST/2026/00001"
		case_doc.company = self.test_company
		case_doc.warehouse = self.test_warehouse
		case_doc.item_code = self.test_item
		case_doc.negative_qty = -5.0
		case_doc.status = "Open"
		case_doc.insert(ignore_permissions=True)

		# Mock current stock balance by updating Bin actual_qty to positive
		if not smriti.db.exists("Bin", {"item_code": self.test_item, "warehouse": self.test_warehouse}):
			bin_doc = smriti.documents.new("Bin")
			bin_doc.item_code = self.test_item
			bin_doc.warehouse = self.test_warehouse
			bin_doc.actual_qty = 10.0
			bin_doc.insert(ignore_permissions=True)
		else:
			smriti.db.set_value("Bin", {"item_code": self.test_item, "warehouse": self.test_warehouse}, "actual_qty", 10.0)

		# Trigger recovery check
		rec_srv = SMRITINegativeStockRecoveryService(self.test_item, self.test_warehouse)
		rec_srv.check_and_recover(source_doctype="Stock Entry", source_name="STE-00021", recovery_type="Auto")

		case_status = smriti.db.get("SMRITI Negative Stock Case", case_doc.name, "status")
		self.assertEqual(case_status, "Recovered")

		# Verify SMRITI Negative Stock Recovery entry exists
		recovery_exists = smriti.db.exists("SMRITI Negative Stock Recovery", {"case_id": case_doc.name})
		self.assertTrue(recovery_exists)
