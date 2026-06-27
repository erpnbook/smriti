import re
from smriti_retail_os.services.udne.exceptions import UDNETemplateValidationError

ALLOWED_TOKENS = {
    "company", "branch", "store", "state", "fy", "month", "year", "terminal", "user", "department",
    "channel", "warehouse", "quarter", "division", "region", "sequence_group", "weekday"
}

def validate_template(template: str) -> None:
    """
    Validates numbering templates at save/update time.
    Ensures balanced braces, valid tokens, and exactly one counter placeholder.
    """
    if not template:
        raise UDNETemplateValidationError("Template cannot be empty.")

    # Check for simple braces matching
    open_braces = template.count("{")
    close_braces = template.count("}")
    if open_braces != close_braces:
        raise UDNETemplateValidationError("Template has unmatched curly braces.")

    placeholders = re.findall(r"\{([^}]+)\}", template)
    if open_braces != len(placeholders):
        raise UDNETemplateValidationError("Template has nested or invalid curly braces.")

    counter_found = False
    for ph in placeholders:
        if ph.startswith("counter"):
            if ph == "counter" or re.match(r"^counter:\d+$", ph):
                counter_found = True
            else:
                raise UDNETemplateValidationError(
                    f"Invalid counter format: '{{{ph}}}'. Must be '{{counter}}' or '{{counter:digits}}' (e.g., '{{counter:6}}')."
                )
        elif ph not in ALLOWED_TOKENS:
            raise UDNETemplateValidationError(
                f"Unsupported token '{{{ph}}}' in template. Allowed tokens: {sorted(list(ALLOWED_TOKENS))}."
            )

    if not counter_found:
        raise UDNETemplateValidationError("Template must contain exactly one '{counter}' or '{counter:digits}' placeholder.")
