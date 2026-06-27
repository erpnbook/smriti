import datetime
import frappe

def log_audit(
    doctype: str,
    docname: str,
    generated_number: str,
    rule_version: int,
    generation_mode: str,
    duration_ms: float,
    retry_count: int,
    conflict_count: int,
    source_module: str,
    terminal_id: str,
    branch: str,
    user: str,
    rule: str = None,
    template: str = None,
    context_details: str = None
) -> None:
    """
    Logs metadata about the generated number into SMRITI Numbering Audit Log.
    """
    try:
        doc = frappe.get_doc({
            "doctype": "SMRITI Numbering Audit Log",
            "document_type": doctype,
            "document_name": docname,
            "generated_number": generated_number,
            "rule": rule,
            "template": template,
            "rule_version": rule_version,
            "context_details": context_details,
            "generation_mode": generation_mode,
            "generation_duration_ms": duration_ms,
            "retry_count": retry_count,
            "conflict_count": conflict_count,
            "source_module": source_module,
            "terminal_id": terminal_id,
            "branch": branch,
            "user": user,
            "timestamp": datetime.datetime.now()
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Error logging UDNE audit: {str(e)}", "UDNE Audit Logger")
