# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_integration_framework.py
# @desc:    Unit tests for SMRITI Connect Integration Platform core and Tally reference adapter.
# @author:  Jawahar R. Mallah
#

import json
import unittest
import frappe
from smriti_retail_os.integration.core.base_adapter import BaseIntegrationAdapter
from smriti_retail_os.integration.core.validator import validate_event_payload
from smriti_retail_os.integration.core.policy import evaluate_routing_policy
from smriti_retail_os.integration.core.dispatcher import dispatch_event
from smriti_retail_os.integration.core.engine import IntegrationEngine
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

class MockSuccessAdapter(BaseIntegrationAdapter):
    def get_adapter_id(self) -> str:
        return "mock.success"
    def connect(self) -> bool:
        return True
    def disconnect(self) -> bool:
        return True
    def health_check(self) -> dict:
        return {"status": "Healthy", "latency_ms": 15}
    def handle_event(self, event_type: str, payload: dict) -> dict:
        return {"success": True, "transaction_id": "MOCK-TX-SUCCESS"}

class MockFailureAdapter(BaseIntegrationAdapter):
    def get_adapter_id(self) -> str:
        return "mock.failure"
    def connect(self) -> bool:
        return True
    def disconnect(self) -> bool:
        return True
    def health_check(self) -> dict:
        return {"status": "Unhealthy", "latency_ms": 0, "error": "Mock connection failure"}
    def handle_event(self, event_type: str, payload: dict) -> dict:
        return {"success": False, "error": "Mock dispatch failure"}


class TestIntegrationFramework(unittest.TestCase):
    def setUp(self):
        frappe.db.begin()
        
        # Ensure DocTypes exist dynamically in test DB if needed
        self.queue_exists = frappe.db.exists("DocType", "SMRITI Integration Queue")
        
        # Cleanup mock entries
        if self.queue_exists:
            frappe.db.delete("SMRITI Integration Queue", {"adapter_id": ["in", ["mock.success", "mock.failure", "accounting.tally"]]})

    def tearDown(self):
        frappe.db.rollback()

    def test_schema_validator_fails_on_missing_fields(self):
        """Checks validator raises ValueError when required fields are missing from payload."""
        payload = {"grand_total": 100}
        with self.assertRaises(ValueError):
            validate_event_payload("SALE_CREATED", payload)

    def test_schema_validator_passes_on_valid_payload(self):
        """Checks validator passes cleanly when all required fields are populated."""
        payload = {
            "grand_total": 4500.0,
            "posting_date": "2026-07-03",
            "customer": "Test Customer",
            "items": [{"item_code": "NIK-MAX-90-BL", "qty": 1.0}]
        }
        # Should not raise exception
        validate_event_payload("SALE_CREATED", payload)

    def test_routing_policy_defaults_to_true(self):
        """Checks policy engine returns True by default if no rules are registered in DB."""
        payload = {"company": "Test Company", "location": "Test Store"}
        allowed = evaluate_routing_policy("SALE_CREATED", "Sales Invoice", "SINV-001", payload)
        self.assertTrue(allowed)

    def test_event_dispatch_outbox_queue_insert(self):
        """Checks dispatcher registers transactional outbox records properly in DB queue."""
        if not self.queue_exists:
            self.skipTest("SMRITI Integration Queue DocType not installed.")

        payload = {
            "grand_total": 1200.0,
            "posting_date": "2026-07-03",
            "customer": "John Doe",
            "items": [{"item_code": "TEST-ITEM-1", "qty": 2.0}]
        }
        
        # Dispatch event
        dispatch_event(
            event_type="SALE_CREATED",
            doc_type="Sales Invoice",
            doc_name="SINV-TEST-99",
            payload=payload,
            priority="Critical"
        )
        
        # Verify database record
        entries = frappe.get_all(
            "SMRITI Integration Queue",
            filters={"document_name": "SINV-TEST-99"},
            fields=["name", "event_type", "document_type", "document_name", "status", "priority", "adapter_id"]
        )
        self.assertGreater(len(entries), 0)
        self.assertEqual(entries[0]["priority"], "Critical")
        self.assertEqual(entries[0]["status"], "Pending")

    def test_integration_engine_execution_success(self):
        """Checks engine runs successful sync attempts and transitions status to Success."""
        if not self.queue_exists:
            self.skipTest("SMRITI Integration Queue DocType not installed.")

        # Insert manual test queue item
        queue_id = QueueRepository.insert_queue_entry(
            event_type="SALE_CREATED",
            doc_type="Sales Invoice",
            doc_name="SINV-MOCK-OK",
            adapter_id="mock.success",
            payload_dict={"data": "test"},
            priority="Normal"
        )
        frappe.db.commit()

        # Inject mock success adapter dynamically
        from smriti_retail_os.integration.core.registry import IntegrationRegistry
        original_get_active = IntegrationRegistry.get_active_adapters
        
        # Override to inject mock adapter
        IntegrationRegistry.get_active_adapters = lambda: {
            "mock.success": MockSuccessAdapter()
        }

        try:
            # Process queue
            IntegrationEngine.process_queue(limit=10)
            
            # Verify status updated to Success
            status = frappe.db.get_value("SMRITI Integration Queue", queue_id, "status")
            self.assertEqual(status, "Success")
        finally:
            # Restore original registry function
            IntegrationRegistry.get_active_adapters = original_get_active

    def test_integration_engine_execution_failure_retry_management(self):
        """Checks engine increments retry count and sets status to Retrying on failure."""
        if not self.queue_exists:
            self.skipTest("SMRITI Integration Queue DocType not installed.")

        queue_id = QueueRepository.insert_queue_entry(
            event_type="SALE_CREATED",
            doc_type="Sales Invoice",
            doc_name="SINV-MOCK-FAIL",
            adapter_id="mock.failure",
            payload_dict={"data": "test"},
            priority="Normal"
        )
        frappe.db.commit()

        from smriti_retail_os.integration.core.registry import IntegrationRegistry
        original_get_active = IntegrationRegistry.get_active_adapters
        
        IntegrationRegistry.get_active_adapters = lambda: {
            "mock.failure": MockFailureAdapter()
        }

        try:
            # Run first attempt
            IntegrationEngine.process_queue(limit=10)
            
            status = frappe.db.get_value("SMRITI Integration Queue", queue_id, "status")
            retry_count = frappe.db.get_value("SMRITI Integration Queue", queue_id, "retry_count")
            
            self.assertEqual(status, "Retrying")
            self.assertEqual(retry_count, 1)
        finally:
            IntegrationRegistry.get_active_adapters = original_get_active
