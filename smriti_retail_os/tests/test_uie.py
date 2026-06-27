# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
import unittest
import json
from smriti_retail_os.smriti_retail_os.uie.services import dispatcher, payload_builder

class TestUIE(unittest.TestCase):
	def setUp(self):
		# Create test Credential
		self.cred = frappe.get_doc({
			"doctype": "SMRITI UIE Credential",
			"credential_name": "Test UIE Credential",
			"type": "API Key",
			"api_key_header": "X-API-Key",
			"api_key_value": "testsecret123"
		})
		if not frappe.db.exists("SMRITI UIE Credential", "Test UIE Credential"):
			self.cred.insert(ignore_permissions=True)

		# Create test Endpoint
		self.endpoint = frappe.get_doc({
			"doctype": "SMRITI UIE Endpoint",
			"endpoint_name": "Test UIE Endpoint",
			"url": "https://httpbin.org/post",
			"method": "POST",
			"content_type": "application/json",
			"timeout": 10
		})
		if not frappe.db.exists("SMRITI UIE Endpoint", "Test UIE Endpoint"):
			self.endpoint.insert(ignore_permissions=True)

		# Create test Integration
		mapping_rules = {
			"bill_no": {"source": "name"},
			"date": {"source": "posting_date"},
			"customer": {"source": "customer"},
			"total": {"source": "grand_total"}
		}
		self.integration = frappe.get_doc({
			"doctype": "SMRITI UIE Integration",
			"integration_name": "Test UIE Integration",
			"enabled": 1,
			"connector_type": "REST",
			"endpoint": "Test UIE Endpoint",
			"credential": "Test UIE Credential",
			"retry_limit": 3,
			"priority": "Normal",
			"version": "v1",
			"mapping_rules": json.dumps(mapping_rules)
		})
		if not frappe.db.exists("SMRITI UIE Integration", "Test UIE Integration"):
			self.integration.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def test_payload_builder_mapping(self):
		"""Tests payload builder declarative mapping rules."""
		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-00001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 5000.0
		})
		payload = payload_builder.build_payload(mock_invoice, self.integration)
		payload_dict = json.loads(payload)
		
		self.assertEqual(payload_dict["bill_no"], "SINV-TEST-00001")
		self.assertEqual(payload_dict["customer"], "Test Customer")
		self.assertEqual(payload_dict["total"], 5000.0)

	def test_payload_builder_validation(self):
		"""Tests payload validation with JSON schema."""
		schema = {
			"type": "object",
			"properties": {
				"total": {"type": "number", "minimum": 100}
			},
			"required": ["total"]
		}
		self.integration.schema_validator = json.dumps(schema)
		self.integration.save(ignore_permissions=True)

		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-00001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 50.0
		})
		
		with self.assertRaises(frappe.ValidationError):
			payload_builder.build_payload(mock_invoice, self.integration)
