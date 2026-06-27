import frappe
from smriti_retail_os.services.udne.interfaces import GenerationContext
from smriti_retail_os.services.udne import generate
from smriti_retail_os.services.udne.exceptions import UDNERuleNotFoundError

def autoname_document(doc, method=None):
    """
    Autoname hook interceptor. Fetches identity and display number from UDNE
    if a rule is configured, falling back to Frappe default autoname otherwise.
    """
    if not frappe.db.exists("SMRITI Numbering Rule", {"document_type": doc.doctype, "is_active": 1}):
        return
        
    try:
        cost_center = getattr(doc, "cost_center", None)
        warehouse = getattr(doc, "set_warehouse", None) or getattr(doc, "warehouse", None)
        
        context = GenerationContext(
            company=getattr(doc, "company", None) or frappe.defaults.get_global_default("company"),
            branch=cost_center or warehouse,
            store=getattr(doc, "custom_store", None) or getattr(doc, "pos_profile", None),
            terminal_id=getattr(doc, "custom_terminal_id", None) or getattr(doc, "pos_profile", None),
            user=doc.owner or frappe.session.user,
            department=getattr(doc, "department", None),
            transaction_date=frappe.utils.to_date(getattr(doc, "posting_date", None) or getattr(doc, "transaction_date", None))
        )
        
        result = generate(doc.doctype, context)
        
        doc.name = result.identity
        
        meta = frappe.get_meta(doc.doctype)
        if meta.has_field("custom_business_display_number"):
            doc.custom_business_display_number = result.display_number
            
    except UDNERuleNotFoundError:
        pass

def before_save_numbering_rule(doc, method=None):
    """
    Auto-increments version of numbering rule on modification.
    """
    if doc.is_new():
        doc.version = 1
    else:
        old_template = doc.get_db_value("template")
        if old_template and old_template != doc.template:
            doc.version = (doc.version or 1) + 1
