# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/dispatcher.py
# @desc:    Event Bus Dispatcher executing Outbox Pattern for SMRITI Connect.
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os.integration.core.validator import validate_event_payload
from smriti_retail_os.integration.core.policy import evaluate_routing_policy
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

def dispatch_event(event_type: str, doc_type: str, doc_name: str, payload: dict, priority: str = "Normal"):
    """
    Validates and registers an event in the Outbox Integration Queue.
    Must be called inside the active database transaction of the parent document.
    
    If the database transaction rolls back, the event is also rolled back,
    guaranteeing transactional outbox integrity.
    """
    # 1. Evaluate Routing Policy
    if not evaluate_routing_policy(event_type, doc_type, doc_name, payload):
        # Bypassed per policy rules
        return
        
    # 2. Schema Validation
    validate_event_payload(event_type, payload)
    
    # 3. Resolve Consumers (from Event Definition)
    definition = QueueRepository.get_event_definition(event_type)
    consumers = []
    if definition and definition.get("consumers"):
        consumers = [c.strip() for c in definition.get("consumers").split(",") if c.strip()]
        
    # Fallback to tally reference adapter if no consumers registered in DB
    if not consumers:
        # Defaults to Tally reference implementation
        consumers = ["accounting.tally"]

    # 4. Insert into the Outbox Queue for each consumer
    for adapter_id in consumers:
        QueueRepository.insert_queue_entry(
            event_type=event_type,
            doc_type=doc_type,
            doc_name=doc_name,
            adapter_id=adapter_id,
            payload_dict=payload,
            priority=priority
        )
