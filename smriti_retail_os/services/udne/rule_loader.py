import datetime
import frappe
from smriti_retail_os import smriti
from frappe.utils import getdate
from smriti_retail_os.services.udne.exceptions import UDNERuleNotFoundError

def load_active_rule(doctype: str, context_dict: dict) -> dict:
    """
    Finds the active SMRITI Numbering Rule for the given DocType and context.
    Applies resolution hierarchy: Store -> Branch -> Company -> Global
    """
    today = datetime.date.today()
    
    rules = smriti.db.get_list(
        "SMRITI Numbering Rule",
        fields=["name", "priority", "priority_value", "version", "template", "reset_rule", "allow_manual_override", "effective_from", "effective_until"],
        filters={
            "document_type": doctype,
            "is_active": 1
        }
    )
    
    valid_rules = []
    for r in rules:
        if r.effective_from and today < getdate(r.effective_from):
            continue
        if r.effective_until and today > getdate(r.effective_until):
            continue
        valid_rules.append(r)
        
    if not valid_rules:
        raise UDNERuleNotFoundError(f"No active numbering rules found for DocType '{doctype}'.")
        
    store_val = context_dict.get("store")
    branch_val = context_dict.get("branch")
    company_val = context_dict.get("company")
    
    matched = None
    
    # Store Override
    if store_val:
        for r in valid_rules:
            if r.priority == "Store" and r.priority_value == store_val:
                matched = r
                break
                
    # Branch Override
    if not matched and branch_val:
        for r in valid_rules:
            if r.priority == "Branch" and r.priority_value == branch_val:
                matched = r
                break
                
    # Company Override
    if not matched and company_val:
        for r in valid_rules:
            if r.priority == "Company" and r.priority_value == company_val:
                matched = r
                break
                
    # Global Default
    if not matched:
        for r in valid_rules:
            if r.priority == "Global" or not r.priority:
                matched = r
                break
                
    if not matched:
        raise UDNERuleNotFoundError(
            f"No matching numbering rule resolved for DocType '{doctype}' with context: "
            f"Store={store_val}, Branch={branch_val}, Company={company_val}"
        )
        
    return matched
