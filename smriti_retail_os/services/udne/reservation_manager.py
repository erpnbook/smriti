import datetime
import json
import frappe
from smriti_retail_os import smriti
from smriti_retail_os.services.udne.exceptions import UDNEExhaustedError

def reserve_range(doctype: str, terminal_id: str, count: int, rule_name: str, reset_rule: str, context_dict: dict, expiry_hours: int = 24) -> dict:
    """
    Allocates a block of numbers for an offline terminal by pre-incrementing the counter.
    """
    if count <= 0:
        raise ValueError("Reservation count must be greater than zero.")
        
    from smriti_retail_os.services.udne.counter_manager import get_context_hash
    context_hash, details = get_context_hash(rule_name, reset_rule, context_dict)
    counter_name = context_hash
    
    if not smriti.db.exists("SMRITI Numbering Counter", counter_name):
        try:
            doc = smriti.documents.new("NumberingCounter")
            doc.update({
                "name": counter_name,
                "rule": rule_name,
                "context_hash": context_hash,
                "context_details": json.dumps(details),
                "current_value": 0
            })
            doc.insert(ignore_permissions=True)
            smriti.db.commit()
        except Exception:
            smriti.db.rollback()
            
    # Row lock for counter block allocation
    res = smriti.db.sql(
        "select current_value from `tabSMRITI Numbering Counter` where name = %s for update",
        (counter_name,)
    )
    current_val = res[0][0] if res else 0
    start_number = current_val + 1
    end_number = current_val + count
    
    smriti.db.sql(
        "update `tabSMRITI Numbering Counter` set current_value = %s where name = %s",
        (end_number, counter_name)
    )
    
    expiry_datetime = datetime.datetime.now() + datetime.timedelta(hours=expiry_hours)
    
    res_doc = smriti.documents.new("NumberingReservedRange")
    res_doc.update({
        "document_type": doctype,
        "terminal_id": terminal_id,
        "start_number": start_number,
        "end_number": end_number,
        "current_counter": start_number,
        "status": "Allocated",
        "expiry_datetime": expiry_datetime
    })
    res_doc.insert(ignore_permissions=True)
    smriti.db.commit()
    
    return {
        "reservation_id": res_doc.name,
        "start": start_number,
        "end": end_number,
        "expiry": expiry_datetime.isoformat()
    }

def reclaim_expired_reservations():
    """
    Scans and transitions expired Allocated/Active ranges to Expired.
    """
    now = datetime.datetime.now()
    expired = smriti.db.get_list(
        "SMRITI Numbering Reserved Range",
        filters={
            "expiry_datetime": ["<", now],
            "status": ["in", ["Allocated", "Active"]]
        }
    )
    for row in expired:
        smriti.db.set_value("SMRITI Numbering Reserved Range", row.name, "status", "Expired")
    if expired:
        smriti.db.commit()
