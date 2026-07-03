# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/validator.py
# @desc:    Payload Validation logic using SMRITI Event Definition schemas.
# @author:  Jawahar R. Mallah
#

import json
import frappe
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

def validate_event_payload(event_type: str, payload: dict):
    """
    Validates the event payload against the registered SMRITI Event Definition schema.
    Raises ValueError if required fields are missing.
    """
    definition = QueueRepository.get_event_definition(event_type)
    
    # If no definition exists in DB, run default/legacy checks to guarantee non-breaking execution
    if not definition:
        # Default safety checks for standard events
        if event_type in ["SALE_CREATED", "SALE_CANCELLED"]:
            required = ["grand_total", "posting_date", "customer", "items"]
        elif event_type in ["PURCHASE_CREATED", "PURCHASE_CANCELLED"]:
            required = ["grand_total", "posting_date", "supplier", "items"]
        else:
            required = []
    else:
        # Parse required fields from DB record
        req_fields_raw = definition.get("required_fields")
        if req_fields_raw:
            try:
                required = json.loads(req_fields_raw)
            except Exception:
                required = [x.strip() for x in req_fields_raw.split(",") if x.strip()]
        else:
            required = []

    # Run check
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(
            f"SMRITI Connect Schema Validation Error: Event '{event_type}' is missing "
            f"required fields: {', '.join(missing)}"
        )
