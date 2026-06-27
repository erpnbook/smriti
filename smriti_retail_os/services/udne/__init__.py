from smriti_retail_os.services.udne.interfaces import GenerationContext, UDNEResult
from smriti_retail_os.services.udne.engine import generate_number

def generate(doctype: str, context: GenerationContext) -> UDNEResult:
    """
    Unified public entry point for SMRITI Universal Document Numbering Engine (UDNE).
    Returns a rich, immutable UDNEResult metadata object.
    """
    return generate_number(doctype, context)
