# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from frappe import _
import time
import datetime
from smriti_retail_os.smriti_retail_os.uie.services.sdk.rest_adapter import RestAdapter

def dispatch_queue_item(queue_name):
	"""Processes a single queue item from SMRITI UIE Sync Queue."""
	queue_item = frappe.get_doc("SMRITI UIE Sync Queue", queue_name)
	if queue_item.status not in ("Pending", "Retrying", "Failed"):
		return
		
	integration = frappe.get_doc("SMRITI UIE Integration", queue_item.integration)
	if not integration.enabled:
		return

	# Set status to sending
	queue_item.status = "Sending"
	queue_item.last_attempt = datetime.datetime.now()
	queue_item.save(ignore_permissions=True)
	frappe.db.commit()

	start_time = time.time()
	success = False
	http_status = 500
	response_content = ""

	# Resolve adapter class based on connector type
	if integration.connector_type == "REST":
		adapter = RestAdapter()
	else:
		adapter = RestAdapter()

	try:
		success, http_status, response_content = adapter.send(
			queue_item=queue_item,
			integration=integration,
			endpoint=integration.endpoint
		)
	except Exception as ex:
		success = False
		http_status = 500
		response_content = str(ex)

	duration_ms = int((time.time() - start_time) * 1000)

	# Update queue status
	if success:
		queue_item.status = "Success"
	else:
		queue_item.retry_count = (queue_item.retry_count or 0) + 1
		if queue_item.retry_count >= (integration.retry_limit or 5):
			queue_item.status = "Dead-Letter"
			queue_item.dead_letter_reason = response_content[:250]
		else:
			queue_item.status = "Failed"
			
	queue_item.save(ignore_permissions=True)

	# Write Sync Log
	log = frappe.get_doc({
		"doctype": "SMRITI UIE Sync Log",
		"timestamp": datetime.datetime.now(),
		"queue_item": queue_item.name,
		"request_payload": queue_item.payload,
		"response_content": response_content[:1000],
		"duration_ms": duration_ms,
		"http_status": http_status,
		"result": "Success" if success else "Failed"
	})
	log.insert(ignore_permissions=True)
	frappe.db.commit()

	return success

import hashlib

def enqueue_document_sync(doc, method=None):
	"""Appends document payload to UIE Sync Queue for all enabled integrations."""
	event_type = "SALE_CREATED"
	if method == "on_cancel":
		event_type = "SALE_CANCELLED"
	integrations = frappe.get_all(
		"SMRITI UIE Integration",
		filters={"enabled": 1},
		fields=["name", "priority"]
	)
	if not integrations:
		return

	from smriti_retail_os.smriti_retail_os.uie.services import payload_builder

	for integration in integrations:
		integration_doc = frappe.get_doc("SMRITI UIE Integration", integration.name)
		
		try:
			payload = payload_builder.build_payload(doc, integration_doc)
		except Exception as ex:
			frappe.log_error(f"UIE payload creation failed for {doc.name}: {str(ex)}")
			continue

		# Compute deterministic idempotency key
		idemp_str = f"{doc.doctype}:{doc.name}:{integration.name}"
		idempotency_key = hashlib.md5(idemp_str.encode("utf-8")).hexdigest()

		if frappe.db.exists("SMRITI UIE Sync Queue", {"idempotency_key": idempotency_key}):
			continue

		queue_item = frappe.get_doc({
			"doctype": "SMRITI UIE Sync Queue",
			"queue_id": frappe.generate_hash(),
			"event_type": event_type,
			"document_type": doc.doctype,
			"document_name": doc.name,
			"payload": payload,
			"status": "Pending",
			"integration": integration.name,
			"priority": integration.priority or "Normal",
			"idempotency_key": idempotency_key
		})
		queue_item.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.enqueue(
			"smriti_retail_os.smriti_retail_os.uie.services.dispatcher.dispatch_queue_item",
			queue_name=queue_item.name,
			queue="long" if integration.priority == "Low" else "default",
			timeout=60
		)
