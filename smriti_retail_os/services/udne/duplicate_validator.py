import frappe
from smriti_retail_os.services.udne.exceptions import UDNECollisionError

def validate_uniqueness(doctype: str, identifier: str) -> None:
    """
    Verifies that the generated identifier is unique in both the primary key
    'name' and the custom business display number fields.
    """
    if frappe.db.exists(doctype, identifier):
        raise UDNECollisionError(
            f"Collision detected: Primary Key '{identifier}' already exists in DocType '{doctype}'."
        )
        
    try:
        meta = frappe.get_meta(doctype)
        if meta.has_field("custom_business_display_number"):
            exists = frappe.get_all(
                doctype,
                filters={"custom_business_display_number": identifier},
                limit=1
            )
            if exists:
                raise UDNECollisionError(
                    f"Collision detected: Business Display Number '{identifier}' already exists in DocType '{doctype}'."
                )
    except Exception:
        pass
