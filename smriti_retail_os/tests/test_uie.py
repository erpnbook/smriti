# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from smriti_retail_os.smriti_retail_os.uie.services import dispatcher, payload_builder

class TestUIE(unittest.TestCase):
	def _cleanup_test_data(self):
		# Clean up test queue items and logs
		test_queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters=[["document_name", "like", "SINV-TEST-%"]]
		)
		for q in test_queue_items:
			frappe.db.delete("SMRITI UIE Sync Log", {"queue_item": q.name})
			frappe.delete_doc("SMRITI UIE Sync Queue", q.name, ignore_permissions=True)

		# Clean up credentials
		if frappe.db.exists("SMRITI UIE Credential", "Test Bearer Credential"):
			frappe.delete_doc("SMRITI UIE Credential", "Test Bearer Credential", ignore_permissions=True)

		# Clean up integrations
		if frappe.db.exists("SMRITI UIE Integration", "Unsupported Integration"):
			frappe.delete_doc("SMRITI UIE Integration", "Unsupported Integration", ignore_permissions=True)

		frappe.db.commit()

	def setUp(self):
		# Clear leftover committed test data from previous runs
		self._cleanup_test_data()

		# Create test Credential
		if not frappe.db.exists("SMRITI UIE Credential", "Test UIE Credential"):
			self.cred = frappe.get_doc({
				"doctype": "SMRITI UIE Credential",
				"credential_name": "Test UIE Credential",
				"type": "API Key",
				"api_key_header": "X-API-Key",
				"api_key_value": "testsecret123"
			})
			self.cred.insert(ignore_permissions=True)
		else:
			self.cred = frappe.get_doc("SMRITI UIE Credential", "Test UIE Credential")

		# Create test Endpoint
		if not frappe.db.exists("SMRITI UIE Endpoint", "Test UIE Endpoint"):
			self.endpoint = frappe.get_doc({
				"doctype": "SMRITI UIE Endpoint",
				"endpoint_name": "Test UIE Endpoint",
				"url": "https://httpbin.org/post",
				"method": "POST",
				"content_type": "application/json",
				"timeout": 10
			})
			self.endpoint.insert(ignore_permissions=True)
		else:
			self.endpoint = frappe.get_doc("SMRITI UIE Endpoint", "Test UIE Endpoint")

		# Create test Integration
		mapping_rules = {
			"bill_no": {"source": "name"},
			"date": {"source": "posting_date"},
			"customer": {"source": "customer"},
			"total": {"source": "grand_total"}
		}
		if not frappe.db.exists("SMRITI UIE Integration", "Test UIE Integration"):
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
			self.integration.insert(ignore_permissions=True)
		else:
			self.integration = frappe.get_doc("SMRITI UIE Integration", "Test UIE Integration")

	def tearDown(self):
		self._cleanup_test_data()
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

	def test_idempotency_deduplication(self):
		"""Tests that duplicate documents are skipped by the idempotency key check."""
		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-IDEMP-001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 3000.0
		})

		# Enqueue first time
		dispatcher.enqueue_document_sync(mock_invoice, "on_submit")

		# Check that one item exists in the queue
		queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters={
				"document_type": "Sales Invoice",
				"document_name": "SINV-TEST-IDEMP-001",
				"integration": self.integration.name
			}
		)
		self.assertEqual(len(queue_items), 1)

		# Enqueue second time (should be skipped due to idempotency check)
		dispatcher.enqueue_document_sync(mock_invoice, "on_submit")

		# Should still be only one item
		queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters={
				"document_type": "Sales Invoice",
				"document_name": "SINV-TEST-IDEMP-001",
				"integration": self.integration.name
			}
		)
		self.assertEqual(len(queue_items), 1)

	@patch('requests.request')
	def test_dead_letter_after_retry_limit(self, mock_request):
		"""Tests queue item transitions to Dead-Letter after reaching retry limit."""
		# Mock requests to fail
		mock_request.side_effect = Exception("Connection Failed")

		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-RETRY-001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 4000.0
		})

		# Enqueue the document
		dispatcher.enqueue_document_sync(mock_invoice, "on_submit")

		queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters={
				"document_type": "Sales Invoice",
				"document_name": "SINV-TEST-RETRY-001",
				"integration": self.integration.name
			},
			fields=["name", "status", "retry_count"]
		)
		self.assertEqual(len(queue_items), 1)
		queue_item_name = queue_items[0].name
		
		# First attempt: Retry count 0 -> 1, status "Failed"
		dispatcher.dispatch_queue_item(queue_item_name)
		q_item = frappe.get_doc("SMRITI UIE Sync Queue", queue_item_name)
		self.assertEqual(q_item.retry_count, 1)
		self.assertEqual(q_item.status, "Failed")

		# Second attempt: Retry count 1 -> 2, status "Failed"
		q_item.status = "Pending"  # Reset status so dispatcher picks it up
		q_item.save(ignore_permissions=True)
		dispatcher.dispatch_queue_item(queue_item_name)
		q_item.reload()
		self.assertEqual(q_item.retry_count, 2)
		self.assertEqual(q_item.status, "Failed")

		# Third attempt: Retry count 2 -> 3 >= retry_limit (3), status "Dead-Letter"
		q_item.status = "Pending"
		q_item.save(ignore_permissions=True)
		dispatcher.dispatch_queue_item(queue_item_name)
		q_item.reload()
		self.assertEqual(q_item.retry_count, 3)
		self.assertEqual(q_item.status, "Dead-Letter")
		self.assertEqual(q_item.dead_letter_reason, "Connection Failed")

	@patch('requests.request')
	def test_dispatch_success_flow(self, mock_request):
		"""Tests successful UIE dispatch creates Sync Log with correct fields."""
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.text = '{"success": true}'
		mock_request.return_value = mock_response

		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-SUCCESS-001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 4500.0
		})

		dispatcher.enqueue_document_sync(mock_invoice, "on_submit")
		queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters={
				"document_type": "Sales Invoice",
				"document_name": "SINV-TEST-SUCCESS-001",
				"integration": self.integration.name
			}
		)
		queue_item_name = queue_items[0].name

		# Dispatch
		success = dispatcher.dispatch_queue_item(queue_item_name)
		self.assertTrue(success)

		# Check queue status updated to Success
		q_item = frappe.get_doc("SMRITI UIE Sync Queue", queue_item_name)
		self.assertEqual(q_item.status, "Success")

		# Check that Sync Log is created
		logs = frappe.get_all(
			"SMRITI UIE Sync Log",
			filters={"queue_item": queue_item_name},
			fields=["result", "http_status", "response_content"]
		)
		self.assertEqual(len(logs), 1)
		self.assertEqual(logs[0].result, "Success")
		self.assertEqual(logs[0].http_status, 200)
		self.assertEqual(logs[0].response_content, '{"success": true}')

	def test_credential_auth_api_key(self):
		"""Tests API Key injection from credential vault."""
		from smriti_retail_os.smriti_retail_os.uie.services.sdk.rest_adapter import RestAdapter
		adapter = RestAdapter()
		headers = adapter.authenticate("Test UIE Credential")
		self.assertEqual(headers.get("X-API-Key"), "testsecret123")

	def test_credential_auth_bearer(self):
		"""Tests Bearer Token injection from credential vault."""
		bearer_cred_name = "Test Bearer Credential"
		if frappe.db.exists("SMRITI UIE Credential", bearer_cred_name):
			frappe.delete_doc("SMRITI UIE Credential", bearer_cred_name)

		bearer_cred = frappe.get_doc({
			"doctype": "SMRITI UIE Credential",
			"credential_name": bearer_cred_name,
			"type": "Bearer Token",
			"token": "bearersecret456"
		})
		bearer_cred.insert(ignore_permissions=True)

		from smriti_retail_os.smriti_retail_os.uie.services.sdk.rest_adapter import RestAdapter
		adapter = RestAdapter()
		headers = adapter.authenticate(bearer_cred_name)
		self.assertEqual(headers.get("Authorization"), "Bearer bearersecret456")

	def test_unsupported_connector_graceful(self):
		"""Tests that an unsupported connector type is handled gracefully by transition to Dead-Letter."""
		# Create integration with unsupported connector
		unsupported_integration = frappe.get_doc({
			"doctype": "SMRITI UIE Integration",
			"integration_name": "Unsupported Integration",
			"enabled": 1,
			"connector_type": "SFTP",
			"endpoint": "Test UIE Endpoint",
			"credential": "Test UIE Credential",
			"retry_limit": 3,
			"priority": "Normal",
			"version": "v1"
		})
		if not frappe.db.exists("SMRITI UIE Integration", "Unsupported Integration"):
			unsupported_integration.insert(ignore_permissions=True)

		mock_invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"name": "SINV-TEST-UNSUPPORTED-001",
			"posting_date": "2026-06-28",
			"customer": "Test Customer",
			"grand_total": 1200.0
		})

		dispatcher.enqueue_document_sync(mock_invoice, "on_submit")
		queue_items = frappe.get_all(
			"SMRITI UIE Sync Queue",
			filters={"document_type": "Sales Invoice", "document_name": "SINV-TEST-UNSUPPORTED-001", "integration": "Unsupported Integration"}
		)
		queue_item_name = queue_items[0].name

		# Dispatch - should handle unsupported gracefully, return False, not crash
		success = dispatcher.dispatch_queue_item(queue_item_name)
		self.assertFalse(success)

		# Check status is Dead-Letter
		q_item = frappe.get_doc("SMRITI UIE Sync Queue", queue_item_name)
		self.assertEqual(q_item.status, "Dead-Letter")
		self.assertIn("Unsupported connector", q_item.dead_letter_reason)
