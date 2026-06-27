import frappe

class UDNEError(frappe.ValidationError):
    """Base exception class for SMRITI Universal Document Numbering Engine (UDNE)."""
    pass

class UDNERuleNotFoundError(UDNEError):
    """Raised when no active rule is matched for the document type and context."""
    pass

class UDNEExhaustedError(UDNEError):
    """Raised when numbering counters or reservations are exhausted."""
    pass

class UDNECollisionError(UDNEError):
    """Raised when a generated number collides with an existing document."""
    pass

class UDNETemplateValidationError(UDNEError):
    """Raised when template validation fails due to invalid syntax or unsupported tokens."""
    pass
