from smriti_retail_os.services.udne.interfaces import GenerationContext, UDNEResult
from smriti_retail_os.services.udne.engine import generate_number

def generate(doctype: str, context: GenerationContext) -> UDNEResult:
    """
    Unified public entry point for SMRITI Universal Document Numbering Engine (UDNE).
    Returns a rich, immutable UDNEResult metadata object.
    """
    return generate_number(doctype, context)

def explain(doc_name: str) -> dict:
    """
    Exposes UDNE resolution, rules, and context details for a given document name.
    Conforms to the SMRITI Unified Explainability Contract.
    """
    from smriti_retail_os.services.udne.explainability import explain_generation
    return explain_generation(doc_name)

def metrics(timespan: str = "Today") -> dict:
    """
    Retrieves performance and volume metrics for UDNE.
    """
    from smriti_retail_os.services.udne.monitoring import get_metrics
    return get_metrics(timespan)

def health() -> dict:
    """
    Computes overall UDNE subsystem operational health summary.
    """
    from smriti_retail_os.services.udne.monitoring import get_health
    return get_health()

def gaps(target_doctype: str = None) -> list:
    """
    Scans and returns sequence gaps for active numbering rules.
    """
    from smriti_retail_os.services.udne.monitoring import get_gaps
    return get_gaps(target_doctype)

def reservations() -> list:
    """
    Returns detailed reservation lifecycle records with utilization ratios.
    """
    from smriti_retail_os.services.udne.monitoring import get_reservations
    return get_reservations()
