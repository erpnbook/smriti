# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/policy.py
# @desc:    Policy Engine for SMRITI Connect Integration Platform routing decisions.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.integration.repository.queue_repository import QueueRepository

def evaluate_routing_policy(event_type: str, doc_type: str, doc_name: str, payload: dict) -> bool:
    """
    Evaluates configured SMRITI Integration Policy rules.
    Decides whether the event should get published or bypassed.
    
    Returns:
        bool: True if event is allowed to route/publish, False to bypass.
    """
    policies = QueueRepository.get_routing_policies()
    
    # If no policies are registered, default to True (non-blocking execution)
    if not policies:
        return True
        
    company = payload.get("company")
    location = payload.get("location") or payload.get("warehouse")
    
    # Check matching rules
    for policy in policies:
        # Match event type
        if policy.get("event_type") and policy.get("event_type") != event_type:
            continue
            
        # Match company constraint
        if policy.get("company") and policy.get("company") != company:
            continue
            
        # Match location/warehouse constraint
        if policy.get("location") and policy.get("location") != location:
            continue
            
        # If matching rule found, apply action (Allow / Block)
        action = policy.get("action", "Allow")
        if action == "Block":
            return False
            
    return True
