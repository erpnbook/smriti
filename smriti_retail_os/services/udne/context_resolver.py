import datetime
import frappe
from smriti_retail_os.services.udne.interfaces import GenerationContext
from smriti_retail_os.services.udne.fy_resolver import resolve_fy

def resolve_context(context: GenerationContext) -> dict:
    """
    Translates GenerationContext into a dictionary of string values.
    Handles dates, financial years, and warehouse state codes.
    """
    dt = context.transaction_date or datetime.date.today()
    fy_info = resolve_fy(dt)
    
    resolved = {
        "company": context.company or "",
        "branch": context.branch or "",
        "store": context.store or "",
        "terminal": context.terminal_id or "",
        "user": context.user or "",
        "department": context.department or "",
        "year": str(dt.year),
        "month": str(dt.month).zfill(2),
        "day": str(dt.day).zfill(2),
        "weekday": dt.strftime("%A"),
        **fy_info
    }
    
    # Attempt to resolve GST state code if branch is provided
    state_code = ""
    if context.branch:
        try:
            wh_details = frappe.db.get_value("Warehouse", context.branch, ["custom_gst_state", "state"], as_dict=True)
            if wh_details:
                state_code = wh_details.get("custom_gst_state") or wh_details.get("state") or ""
        except Exception:
            pass
            
    resolved["state"] = state_code.upper()[:2] if state_code else "GS"
    
    # Reserved token defaults for future extensibility
    resolved["channel"] = "POS"
    resolved["warehouse"] = context.branch or "WH"
    resolved["quarter"] = f"Q{(dt.month - 1) // 3 + 1}"
    resolved["division"] = "DIV"
    resolved["region"] = "REG"
    resolved["sequence_group"] = "GRP"
    
    # Include extra context overrides
    resolved.update(context.as_dict())
    
    return resolved
