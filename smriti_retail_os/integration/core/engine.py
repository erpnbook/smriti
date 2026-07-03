# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/engine.py
# @desc:    Integration Engine Queue processor executing asynchronous dispatching and backoffs.
# @author:  Jawahar R. Mallah
#

import time
import json
import frappe
from frappe.utils import now_datetime, get_datetime, get_datetime_str
from smriti_retail_os.integration.core.registry import IntegrationRegistry
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

class IntegrationEngine:
    """
    Asynchronous runner for SMRITI Connect.
    
    Processes the outbox queue, handles exponential backoffs,
    and updates sync logs and health indicators.
    """

    @staticmethod
    def process_queue(limit: int = 50):
        """
        Pulls and processes pending integration queue entries.
        Expected to run as a scheduler hook or background worker.
        """
        entries = QueueRepository.get_pending_queue_entries(limit=limit)
        if not entries:
            return

        # Load all active adapters dynamically
        adapters = IntegrationRegistry.get_active_adapters()
        
        for entry in entries:
            queue_id = entry.get("name")
            event_type = entry.get("event_type")
            doc_type = entry.get("document_type")
            doc_name = entry.get("document_name")
            adapter_id = entry.get("adapter_id")
            payload_str = entry.get("payload")
            retry_count = entry.get("retry_count") or 0
            status = entry.get("status")
            last_attempt = entry.get("last_attempt")

            # 1. Backoff Check for Retrying Items
            if status == "Retrying" and last_attempt:
                # wait_seconds = 2^retry_count * 60 seconds
                wait_seconds = (2 ** min(retry_count, 6)) * 60
                elapsed = (now_datetime() - get_datetime(last_attempt)).total_seconds()
                if elapsed < wait_seconds:
                    continue # Skip this attempt, wait for backoff cooldown

            # 2. Check Adapter Availability
            adapter = adapters.get(adapter_id)
            if not adapter:
                # Mark as failed because adapter class is not registered or enabled
                error_msg = f"Adapter '{adapter_id}' is not active or failed to load."
                QueueRepository.update_queue_status(queue_id, "Failed", retry_count + 1, error_msg)
                QueueRepository.log_audit_entry(
                    queue_id=queue_id, adapter_id=adapter_id, event_type=event_type,
                    doc_type=doc_type, doc_name=doc_name, payload={}, success=False, error=error_msg
                )
                frappe.db.commit()
                continue

            # 3. Parse Payload
            try:
                payload = json.loads(payload_str)
            except Exception as e:
                error_msg = f"Invalid JSON payload format in queue: {str(e)}"
                QueueRepository.update_queue_status(queue_id, "Dead-Letter", retry_count, error_msg)
                QueueRepository.log_audit_entry(
                    queue_id=queue_id, adapter_id=adapter_id, event_type=event_type,
                    doc_type=doc_type, doc_name=doc_name, payload={}, success=False, error=error_msg
                )
                frappe.db.commit()
                continue

            # 4. Dispatch transaction through the dynamic adapter
            start_time = time.time()
            outcome = {}
            try:
                # Mark queue as Sending to prevent concurrent runs
                QueueRepository.update_queue_status(queue_id, "Sending", retry_count)
                frappe.db.commit()
                
                # Execute adapter event handler
                outcome = adapter.handle_event(event_type, payload)
                
            except Exception as e:
                outcome = {"success": False, "error": str(e)}

            duration = int((time.time() - start_time) * 1000)

            # 5. Process Outcome
            if outcome.get("success"):
                # Success transition
                transaction_id = outcome.get("transaction_id")
                QueueRepository.update_queue_status(queue_id, "Success", retry_count)
                QueueRepository.log_audit_entry(
                    queue_id=queue_id, adapter_id=adapter_id, event_type=event_type,
                    doc_type=doc_type, doc_name=doc_name, payload=payload, success=True,
                    response_id=transaction_id, duration_ms=duration
                )
                # Auto-update provider health indicators dynamically
                QueueRepository.update_provider_health(adapter_id, "Healthy", duration)
            else:
                # Failure transition
                error_msg = outcome.get("error", "Unknown integration error.")
                next_retry = retry_count + 1
                
                if next_retry >= 5:
                    next_status = "Dead-Letter"
                    # Log critical alert
                    frappe.log_error(
                        title=f"SMRITI Connect Dead-Letter Event: {doc_name}",
                        message=f"Event: {event_type}\nAdapter: {adapter_id}\nRetries exceeded.\nError: {error_msg}"
                    )
                else:
                    next_status = "Retrying"

                QueueRepository.update_queue_status(queue_id, next_status, next_retry, error_msg)
                QueueRepository.log_audit_entry(
                    queue_id=queue_id, adapter_id=adapter_id, event_type=event_type,
                    doc_type=doc_type, doc_name=doc_name, payload=payload, success=False,
                    error=error_msg, duration_ms=duration
                )
                QueueRepository.update_provider_health(adapter_id, "Unhealthy", duration, error_msg)

            # Commit current run to release DB locks
            frappe.db.commit()
