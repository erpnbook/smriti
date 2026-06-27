import frappe
import json
from smriti_retail_os.services.udne.template_compiler import CompiledTemplate
from smriti_retail_os.services.udne.template_validator import validate_template
from smriti_retail_os.services.udne.gap_scanner import scan_gaps

@frappe.whitelist()
def preview_number(template: str, context_json: str, counter_val: int = 1) -> dict:
    """
    Renders a template preview using the backend compiler & renderer.
    """
    try:
        validate_template(template)
        ctx = json.loads(context_json) if context_json else {}
        compiled = CompiledTemplate(template)
        return {"success": True, "preview": compiled.render(ctx, int(counter_val))}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def save_rule(doc_data: str) -> dict:
    """
    Saves or updates a SMRITI Numbering Rule.
    Validates template syntax and auto-increments version.
    """
    try:
        data = json.loads(doc_data)
        validate_template(data.get("template", ""))
        
        rule_name = data.get("name")
        if rule_name:
            doc = frappe.get_doc("SMRITI Numbering Rule", rule_name)
            doc.version = (doc.version or 1) + 1
            doc.is_active = data.get("is_active", 1)
            doc.priority = data.get("priority", "Global")
            doc.priority_value = data.get("priority_value")
            doc.effective_from = data.get("effective_from")
            doc.effective_until = data.get("effective_until")
            doc.template = data.get("template")
            doc.reset_rule = data.get("reset_rule", "Never")
            doc.allow_manual_override = data.get("allow_manual_override", 0)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "SMRITI Numbering Rule",
                "document_type": data.get("document_type"),
                "is_active": data.get("is_active", 1),
                "priority": data.get("priority", "Global"),
                "priority_value": data.get("priority_value"),
                "version": 1,
                "effective_from": data.get("effective_from"),
                "effective_until": data.get("effective_until"),
                "template": data.get("template"),
                "reset_rule": data.get("reset_rule", "Never"),
                "allow_manual_override": data.get("allow_manual_override", 0)
            })
            doc.insert(ignore_permissions=True)
            
        frappe.db.commit()
        return {"success": True, "name": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_rules() -> list:
    """Gets list of rules."""
    return frappe.get_all("SMRITI Numbering Rule", fields=["*"], order_by="creation desc")

@frappe.whitelist()
def get_reservations() -> list:
    """Gets list of terminal reservations."""
    return frappe.get_all("SMRITI Numbering Reserved Range", fields=["*"], order_by="creation desc")

@frappe.whitelist()
def scan_sequence_gaps(doctype: str, rule_name: str) -> dict:
    """Triggers sequence gap analysis."""
    try:
        gaps = scan_gaps(doctype, rule_name)
        return {"success": True, "gaps": gaps}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def explain_doc(doc_name: str) -> dict:
    """
    Exposes UDNE resolution explainability trace for a given document.
    """
    try:
        from smriti_retail_os.services import udne
        res = udne.explain(doc_name)
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_dashboard_metrics(timespan: str = "Today") -> dict:
    """
    Retrieves full dashboard metrics bundle including performance, health, sequence gaps, and reservations.
    """
    try:
        from smriti_retail_os.services import udne
        m = udne.metrics(timespan)
        h = udne.health()
        g = udne.gaps()
        r = udne.reservations()
        return {
            "success": True,
            "metrics": m,
            "health": h,
            "gaps": g,
            "reservations": r
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
