# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from frappe import _
from smriti_retail_os import smriti
import time
import datetime
from smriti_retail_os.smriti_retail_os.uie.services.sdk.rest_adapter import RestAdapter

def dispatch_queue_item(queue_name):
	"""Processes a single queue item from SMRITI UIE Sync Queue."""
	queue_item = smriti.documents.get("SMRITI UIE Sync Queue", queue_name)
	if queue_item.status not in ("Pending", "Retrying", "Failed"):
		return
		
	integration = smriti.documents.get("SMRITI UIE Integration", queue_item.integration)
	if not integration.enabled:
		return

	# Set status to sending
	queue_item.status = "Sending"
	queue_item.last_attempt = datetime.datetime.now()
	queue_item.save(ignore_permissions=True)

	start_time = time.time()
	success = False
	http_status = 500
	response_content = ""

	# Resolve adapter class based on connector type
	if integration.connector_type == "REST":
		adapter = RestAdapter()
	else:
		smriti.errors.log_error(f"Unsupported connector type: {integration.connector_type}", "UIE Dispatch Error")
		queue_item.status = "Dead-Letter"
		queue_item.dead_letter_reason = f"Unsupported connector: {integration.connector_type}"
		queue_item.save(ignore_permissions=True)
		
		# Log the failure in UIE Sync Log
		log = smriti.documents.new("UIESyncLog")
		log.update({
			"timestamp": datetime.datetime.now(),
			"queue_item": queue_item.name,
			"request_payload": queue_item.payload,
			"response_content": f"Unsupported connector: {integration.connector_type}",
			"duration_ms": 0,
			"http_status": 500,
			"result": "Failed"
		})
		log.insert(ignore_permissions=True)
		return False

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
	log = smriti.documents.new("UIESyncLog")
	log.update({
		"timestamp": datetime.datetime.now(),
		"queue_item": queue_item.name,
		"request_payload": queue_item.payload,
		"response_content": response_content[:1000],
		"duration_ms": duration_ms,
		"http_status": http_status,
		"result": "Success" if success else "Failed"
	})
	log.insert(ignore_permissions=True)

	return success

import hashlib

def enqueue_document_sync(doc, method=None):
	"""Appends document payload to UIE Sync Queue for all enabled integrations."""
	DOCTYPE_EVENT_MAP = {
		"Sales Invoice": {"on_submit": "SALE_CREATED", "on_cancel": "SALE_CANCELLED"},
		"Purchase Order": {"on_submit": "PO_CREATED", "on_cancel": "PO_CANCELLED"},
		"Payment Entry": {"on_submit": "PAYMENT_CREATED"}
	}
	method_str = method or "on_submit"
	event_type = DOCTYPE_EVENT_MAP.get(doc.doctype, {}).get(
		method_str, 
		f"{doc.doctype.upper().replace(' ', '_')}_{method_str.upper()}"
	)

	integrations = smriti.db.get_list(
		"SMRITI UIE Integration",
		filters={"enabled": 1},
		fields=["name", "priority", "mapping_rules", "schema_validator"]
	)
	if not integrations:
		return

	from smriti_retail_os.smriti_retail_os.uie.services import payload_builder

	for integration in integrations:
		try:
			payload = payload_builder.build_payload(doc, integration)
		except Exception as ex:
			smriti.errors.log_error(f"UIE payload creation failed for {doc.name}: {str(ex)}")
			continue

		# Compute deterministic idempotency key
		idemp_str = f"{doc.doctype}:{doc.name}:{integration.name}"
		idempotency_key = hashlib.md5(idemp_str.encode("utf-8")).hexdigest()

		if smriti.db.exists("SMRITI UIE Sync Queue", {"idempotency_key": idempotency_key}):
			continue

		queue_item = smriti.documents.new("UIESyncQueue")
		queue_item.update({
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
		smriti.db.commit()

		smriti.tasks.enqueue(
			"smriti_retail_os.smriti_retail_os.uie.services.dispatcher.dispatch_queue_item",
			queue_name=queue_item.name,
			queue="long" if integration.priority == "Low" else "default",
			timeout=60
		)
