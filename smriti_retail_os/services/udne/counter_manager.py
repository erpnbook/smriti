import hashlib
import json
import frappe
from typing import Tuple

def get_context_hash(rule_name: str, reset_rule: str, context_dict: dict) -> Tuple[str, dict]:
    """
    Computes a unique context hash based on the reset scope.
    """
    details = {"rule": rule_name}
    
    if reset_rule == "Yearly":
        details["year"] = context_dict.get("year", "")
    elif reset_rule == "Monthly":
        details["year"] = context_dict.get("year", "")
        details["month"] = context_dict.get("month", "")
    elif reset_rule == "Daily":
        details["year"] = context_dict.get("year", "")
        details["month"] = context_dict.get("month", "")
        details["day"] = context_dict.get("day", "")
    elif reset_rule == "Financial Year":
        details["fy"] = context_dict.get("fy", "")
    elif reset_rule == "Store":
        details["store"] = context_dict.get("store", "")
    elif reset_rule == "Terminal":
        details["terminal"] = context_dict.get("terminal", "")
        
    serialized = json.dumps(details, sort_keys=True)
    context_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return context_hash, details

def increment_counter(rule_name: str, reset_rule: str, context_dict: dict) -> int:
    """
    Atomically increments the context-specific counter using row-level locks.
    """
    context_hash, details = get_context_hash(rule_name, reset_rule, context_dict)
    counter_name = context_hash
    
    if not frappe.db.exists("SMRITI Numbering Counter", counter_name):
        try:
            # Inline transaction to insert and establish the row
            doc = frappe.get_doc({
                "doctype": "SMRITI Numbering Counter",
                "name": counter_name,
                "rule": rule_name,
                "context_hash": context_hash,
                "context_details": json.dumps(details),
                "current_value": 0
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            # Concurrent insertion safety
            frappe.db.rollback()
            
    # Row lock for atomic update
    res = frappe.db.sql(
        "select current_value from `tabSMRITI Numbering Counter` where name = %s for update",
        (counter_name,)
    )
    
    current_val = res[0][0] if res else 0
    next_val = current_val + 1
    
    frappe.db.sql(
        "update `tabSMRITI Numbering Counter` set current_value = %s where name = %s",
        (next_val, counter_name)
    )
    
    return next_val
