import frappe
from frappe.utils import flt, cint
from frappe import _

# Helper to get state from GSTIN using India Compliance utilities
def resolve_address_state(gstin, fallback="Karnataka"):
    if not gstin or len(gstin) < 2:
        return fallback
    try:
        from india_compliance.gst_india.utils import get_state
        state = get_state(gstin[:2])
        return state or fallback
    except ImportError:
        return fallback

# --- Item (Product Master) Hooks ---

def sync_item_taxes_and_prices(doc, method):
    """
    Triggers before_save on Item.
    1. Maps custom_gst_percentage to India Compliance standard Item Tax Templates.
    2. Syncs custom_mrp to standard Item Price.
    3. Handles UOM fallbacks.
    """
    if not doc.stock_uom:
        doc.stock_uom = "Nos"
    
    if doc.custom_gst_percentage:
        pct = cint(doc.custom_gst_percentage)
        template_name = frappe.db.get_value(
            "Item Tax Template", 
            {"name": ["like", f"%{pct}%"]}, 
            "name"
        )
        
        if not template_name:
            details = frappe.db.get_all(
                "Item Tax Template Detail",
                filters={"tax_rate": pct},
                pluck="parent",
                limit=1
            )
            if details:
                template_name = details[0]
                
        if template_name:
            doc.taxes = []
            doc.append("taxes", {
                "item_tax_template": template_name,
                "tax_category": ""
            })

def after_item_save(doc, method):
    """
    Triggers on_update on Item.
    """
    if doc.custom_mrp:
        sync_price_list_rate(doc.name, "MRP", flt(doc.custom_mrp), doc.stock_uom)
        
    if doc.standard_rate:
        sync_price_list_rate(doc.name, "Standard Selling", flt(doc.standard_rate), doc.stock_uom)

def sync_price_list_rate(item_code, price_list, rate, uom):
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.enabled = 1
        pl.buying = 1 if price_list == "Standard Buying" else 0
        pl.selling = 0 if price_list == "Standard Buying" else 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    filters = {
        "item_code": item_code,
        "price_list": price_list,
        "uom": uom
    }
    ip_name = frappe.db.get_value("Item Price", filters, "name")
    
    if ip_name:
        ip = frappe.get_doc("Item Price", ip_name)
        ip.price_list_rate = rate
        ip.save(ignore_permissions=True)
    else:
        ip = frappe.new_doc("Item Price")
        ip.item_code = item_code
        ip.price_list = price_list
        ip.price_list_rate = rate
        ip.uom = uom
        ip.currency = "INR"
        ip.insert(ignore_permissions=True)


# --- Customer Hooks ---

def sync_customer_address(doc, method):
    """
    Triggers on_update on Customer.
    Auto-creates or updates standard linked Address record from custom_address_text.
    """
    if not doc.custom_address_text:
        return

    address_title = f"{doc.customer_name} - Retail Billing"
    address_lines = [line.strip() for line in doc.custom_address_text.split("\n") if line.strip()]
    
    address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
    address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""
    
    # Resolve state from GSTIN or fallback
    state = resolve_address_state(doc.tax_id or doc.get("gstin"))

    existing_address = frappe.db.get_value(
        "Address",
        {
            "links.link_doctype": "Customer",
            "links.link_name": doc.name,
            "address_type": "Billing"
        },
        "name"
    )

    if existing_address:
        addr = frappe.get_doc("Address", existing_address)
        addr.address_line1 = address_line1[:140]
        addr.address_line2 = address_line2[:140] if address_line2 else None
        addr.gstin = doc.tax_id
        addr.state = state
        addr.save(ignore_permissions=True)
    else:
        addr = frappe.new_doc("Address")
        addr.address_title = address_title[:140]
        addr.address_type = "Billing"
        addr.address_line1 = address_line1[:140]
        addr.address_line2 = address_line2[:140] if address_line2 else None
        addr.city = "Unknown"
        addr.country = "India"
        addr.state = state
        addr.gstin = doc.tax_id
        addr.append("links", {
            "link_doctype": "Customer",
            "link_name": doc.name
        })
        addr.insert(ignore_permissions=True)


# --- Supplier Hooks ---

def sync_supplier_address_and_credit_days(doc, method):
    """
    Triggers on_update on Supplier.
    1. Auto-creates standard linked Address from custom_address_text.
    2. Resolves custom_credit_days to a standard Payment Terms Template and links it.
    """
    # 1. Sync Address
    if doc.custom_address_text:
        address_title = f"{doc.supplier_name} - Retail Purchase"
        address_lines = [line.strip() for line in doc.custom_address_text.split("\n") if line.strip()]
        
        address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
        address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""
        
        state = resolve_address_state(doc.gstin or doc.tax_id)

        existing_address = frappe.db.get_value(
            "Address",
            {
                "links.link_doctype": "Supplier",
                "links.link_name": doc.name,
                "address_type": "Billing"
            },
            "name"
        )

        if existing_address:
            addr = frappe.get_doc("Address", existing_address)
            addr.address_line1 = address_line1[:140]
            addr.address_line2 = address_line2[:140] if address_line2 else None
            addr.gstin = doc.gstin
            addr.state = state
            addr.save(ignore_permissions=True)
        else:
            addr = frappe.new_doc("Address")
            addr.address_title = address_title[:140]
            addr.address_type = "Billing"
            addr.address_line1 = address_line1[:140]
            addr.address_line2 = address_line2[:140] if address_line2 else None
            addr.city = "Unknown"
            addr.country = "India"
            addr.state = state
            addr.gstin = doc.gstin
            addr.append("links", {
                "link_doctype": "Supplier",
                "link_name": doc.name
            })
            addr.insert(ignore_permissions=True)

    # 2. Sync Credit Days -> Payment Terms Template
    if doc.custom_credit_days:
        days = cint(doc.custom_credit_days)
        template_name = f"Credit Term - {days} Days"

        if not frappe.db.exists("Payment Terms Template", template_name):
            ptt = frappe.new_doc("Payment Terms Template")
            ptt.template_name = template_name
            ptt.append("terms", {
                "invoice_portion": 100.0,
                "credit_days": days,
                "due_date_based_on": "Day(s) after invoice date"
            })
            ptt.insert(ignore_permissions=True)

        if doc.payment_terms != template_name:
            frappe.db.set_value("Supplier", doc.name, "payment_terms", template_name)
