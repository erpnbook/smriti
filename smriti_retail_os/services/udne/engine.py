import time
import frappe
from smriti_retail_os.services.udne.interfaces import GenerationContext, UDNEResult
from smriti_retail_os.services.udne.rule_loader import load_active_rule
from smriti_retail_os.services.udne.context_resolver import resolve_context
from smriti_retail_os.services.udne.cache import get_compiled_template
from smriti_retail_os.services.udne.counter_manager import increment_counter
from smriti_retail_os.services.udne.duplicate_validator import validate_uniqueness
from smriti_retail_os.services.udne.audit_logger import log_audit
from smriti_retail_os.services.udne.exceptions import UDNEExhaustedError

def generate_number(doctype: str, context: GenerationContext) -> UDNEResult:
    """
    Executes the UDNE pipeline to produce a rich UDNEResult object containing
    an immutable internal identity and a formatted business display number.
    """
    start_time = time.perf_counter()
    ctx_dict = resolve_context(context)
    
    # 1. Rule Resolution & Priorities
    rule = load_active_rule(doctype, ctx_dict)
    rule_name = rule["name"]
    version = rule["version"]
    reset_rule = rule["reset_rule"]
    template_str = rule["template"]
    
    # 2. Cache Compiler/Renderer
    compiled = get_compiled_template(rule_name, version, template_str)
    
    retry_count = 0
    conflict_count = 0
    max_retries = 5
    
    reservation_id = ctx_dict.get("reservation_id")
    generation_mode = "Offline" if reservation_id else "Auto"
    
    while retry_count <= max_retries:
        try:
            if reservation_id:
                # 3a. Consuming Offline Reserved Range
                res_doc = frappe.get_doc("SMRITI Numbering Reserved Range", reservation_id)
                if res_doc.status not in ["Allocated", "Active"]:
                    raise frappe.ValidationError(f"Offline reservation range '{reservation_id}' is in '{res_doc.status}' state.")
                
                counter_val = res_doc.current_counter
                if counter_val > res_doc.end_number:
                    res_doc.status = "Exhausted"
                    res_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    raise UDNEExhaustedError(f"Offline reservation range '{reservation_id}' has been exhausted.")
                
                res_doc.current_counter = counter_val + 1
                if res_doc.current_counter > res_doc.end_number:
                    res_doc.status = "Exhausted"
                else:
                    res_doc.status = "Active"
                res_doc.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                # 3b. Atomic Counter Increment
                counter_val = increment_counter(rule_name, reset_rule, ctx_dict)
            
            # 4. Formatter Rendering
            display_num = compiled.render(ctx_dict, counter_val)
            
            # 5. Stable Internal Identity Generation (Decoupled PK)
            abbr = "".join([w[0] for w in doctype.split()]).upper()
            identity = f"{abbr}-{frappe.generate_hash(length=12).upper()}"
            
            # 6. Uniqueness Checks
            validate_uniqueness(doctype, display_num)
            validate_uniqueness(doctype, identity)
            
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            # 7. Persistence and Audit Logging
            log_audit(
                doctype=doctype,
                docname=identity,
                generated_number=display_num,
                rule_version=version,
                generation_mode=generation_mode,
                duration_ms=duration_ms,
                retry_count=retry_count,
                conflict_count=conflict_count,
                source_module=context.department or "Retail",
                terminal_id=context.terminal_id or "Online",
                branch=context.branch or "",
                user=context.user or "Administrator"
            )
            
            return UDNEResult(
                identity=identity,
                display_number=display_num,
                rule=rule_name,
                version=version,
                counter=counter_val,
                context=ctx_dict,
                reservation=reservation_id,
                generated_at=frappe.utils.now_datetime().isoformat(),
                duration_ms=duration_ms
            )
        except Exception as e:
            conflict_count += 1
            retry_count += 1
            if retry_count > max_retries:
                raise e
