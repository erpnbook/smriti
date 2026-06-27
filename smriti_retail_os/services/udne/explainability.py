import frappe
import json

def explain_generation(doc_name: str) -> dict:
    """
    Retrieves and constructs a standardized explanation payload for a document number generation.
    Conforms to the SMRITI Unified Explainability Contract.
    """
    audit = frappe.get_all(
        "SMRITI Numbering Audit Log",
        fields=["name", "document_type", "generated_number", "rule", "template", "rule_version", "context_details", "generation_mode", "generation_duration_ms", "terminal_id", "branch", "user", "timestamp"],
        filters={"document_name": doc_name},
        limit=1
    )
    
    if not audit:
        # Check if the doc_name itself is the business display number
        audit = frappe.get_all(
            "SMRITI Numbering Audit Log",
            fields=["name", "document_name", "document_type", "generated_number", "rule", "template", "rule_version", "context_details", "generation_mode", "generation_duration_ms", "terminal_id", "branch", "user", "timestamp"],
            filters={"generated_number": doc_name},
            limit=1
        )
        
    if not audit:
        return {
            "success": False,
            "schema_version": 1,
            "confidence": 0,
            "summary": f"No UDNE audit trace found for document identifier '{doc_name}'.",
            "evidence": {},
            "metrics": {
                "explainability_score": 0
            },
            "timeline": ["Trace requested", "Search failed in SMRITI Numbering Audit Log"]
        }
        
    log = audit[0]
    actual_doc_name = log.get("document_name") or doc_name
    
    # Resolve context JSON
    ctx = {}
    if log.context_details:
        try:
            ctx = json.loads(log.context_details)
        except Exception:
            pass
            
    # Resolve rule details
    rule_priority = "Global"
    rule_priority_value = ""
    allow_manual = 0
    if log.rule:
        res = frappe.db.get_value("SMRITI Numbering Rule", log.rule, ["priority", "priority_value", "allow_manual_override"])
        if res:
            rule_priority, rule_priority_value, allow_manual = res
            
    # Compute Confidence Score
    confidence = 100
    missing_elements = []
    if not log.rule:
        confidence -= 20
        missing_elements.append("Rule Reference")
    if not log.template:
        confidence -= 20
        missing_elements.append("Template Reference")
    if not log.context_details:
        confidence -= 30
        missing_elements.append("Context Variables")
        
    # Build timeline
    timeline = ["Generation request received"]
    if rule_priority != "Global":
        timeline.append(f"Applied priority override: {rule_priority} ({rule_priority_value})")
    else:
        timeline.append("Applied global default numbering rule")
        
    timeline.append(f"Loaded template version {log.rule_version}: '{log.template}'")
    timeline.append(f"Resolved context variables: {', '.join([f'{k}={v}' for k, v in ctx.items() if v])}")
    
    if log.generation_mode == "Offline":
        timeline.append(f"Allocated from offline reserved range for terminal {log.terminal_id}")
    else:
        timeline.append("Atomically incremented database sequence counter")
        
    timeline.append(f"Formatted display number: '{log.generated_number}'")
    timeline.append("Verified unique database constraints")
    timeline.append(f"Persisted trace name: '{actual_doc_name}'")
    
    summary = f"Document '{actual_doc_name}' was assigned number '{log.generated_number}' using rule version {log.rule_version}."
    
    return {
        "success": True,
        "schema_version": 1,
        "summary": summary,
        "confidence": confidence,
        "evidence": {
            "document_name": actual_doc_name,
            "document_type": log.document_type,
            "generated_number": log.generated_number,
            "rule_id": log.rule,
            "template": log.template,
            "context": ctx,
            "user": log.user,
            "timestamp": str(log.timestamp)
        },
        "metrics": {
            "generation_mode": log.generation_mode,
            "generation_duration_ms": log.generation_duration_ms,
            "rule_version": log.rule_version,
            "explainability_score": confidence,
            "missing_elements": missing_elements
        },
        "timeline": timeline
    }
