import re
import datetime
import frappe

def scan_gaps(doctype: str, rule_name: str) -> list:
    """
    Scans the database for sequence gaps in the business display numbers.
    Classifies gaps into Explained, Reserved, Pending, or Unexplained.
    """
    rule = frappe.get_doc("SMRITI Numbering Rule", rule_name)
    template = rule.template
    
    meta = frappe.get_meta(doctype)
    if not meta.has_field("custom_business_display_number"):
        return []
        
    records = frappe.get_all(
        doctype,
        fields=["name", "custom_business_display_number", "docstatus"],
        order_by="creation"
    )
    
    # Convert template into regex pattern to extract counter integer
    pattern = template
    for char in [".", "^", "$", "*", "+", "?", "(", ")", "[", "]", "|", "\\"]:
        pattern = pattern.replace(char, "\\" + char)
        
    pattern_regex = re.sub(r"\{counter(:\d+)?\}", r"(\\d+)", pattern)
    pattern_regex = re.sub(r"\{[^}]+\}", r".*", pattern_regex)
    pattern_regex = f"^{pattern_regex}$"
    
    numbers_seen = []
    for r in records:
        display_num = r.get("custom_business_display_number")
        if not display_num:
            continue
        match = re.match(pattern_regex, display_num)
        if match:
            try:
                num = int(match.group(1))
                numbers_seen.append(num)
            except (IndexError, ValueError):
                pass
                
    if not numbers_seen:
        return []
        
    numbers_seen.sort()
    min_num = numbers_seen[0]
    max_num = numbers_seen[-1]
    seen_set = set(numbers_seen)
    
    gaps = []
    for num in range(min_num, max_num + 1):
        if num not in seen_set:
            status = "Unexplained"
            explanation = "No naming or document trace found."
            
            # Check for range reservations
            reservation = frappe.get_all(
                "SMRITI Numbering Reserved Range",
                fields=["name", "status", "expiry_datetime", "terminal_id"],
                filters={
                    "document_type": doctype,
                    "start_number": ["<=", num],
                    "end_number": [">=", num]
                },
                limit=1
            )
            
            if reservation:
                res = reservation[0]
                res_status = res.status
                if res_status in ["Allocated", "Active"]:
                    if res.expiry_datetime and res.expiry_datetime < datetime.datetime.now():
                        status = "Unexplained"
                        explanation = f"Expired reservation range on terminal {res.terminal_id} without synchronization."
                    else:
                        status = "Pending"
                        explanation = f"Allocated to offline terminal {res.terminal_id} (Sync pending)."
                elif res_status == "Exhausted":
                    status = "Unexplained"
                    explanation = f"Exhausted offline reservation range on terminal {res.terminal_id} but sequence missing."
                elif res_status in ["Released", "Expired", "Archived"]:
                    status = "Reserved"
                    explanation = f"Reserved range on terminal {res.terminal_id} (Status: {res_status})."
            else:
                # Check naming audit logs
                audit = frappe.get_all(
                    "SMRITI Numbering Audit Log",
                    fields=["name", "timestamp"],
                    filters={
                        "document_type": doctype,
                        "generated_number": ["like", f"%{num}%"]
                    },
                    limit=1
                )
                if audit:
                    status = "Explained"
                    explanation = "Recorded in naming audit log but missing from document database (Possibly deleted or voided)."
                    
            gaps.append({
                "number": num,
                "status": status,
                "explanation": explanation
            })
            
    return gaps
