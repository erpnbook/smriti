# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/master_api.py
# @description: Backend API for SMRITI Master Data -- customers, suppliers, and company settings.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint
from frappe import _

@frappe.whitelist()
def quick_create_item(item_name, barcode, rate, mrp, gst_percentage, style_code=None):
    """
    Creates a new Item, Barcode, and Price List entry in one step.
    Designed for "Dumb User" speed — minimal fields, maximum automation.
    """
    if not item_name or not barcode:
        frappe.throw(_("Item Name and Barcode are required."))

    # 1. Create the Item
    item = frappe.new_doc("Item")
    item.item_code = barcode # For retail, item_code = barcode is the simplest way
    item.item_name = item_name
    item.item_group = "Products"
    item.stock_uom = "Nos"
    item.is_stock_item = 1
    item.opening_stock = 0
    item.standard_rate = flt(rate)
    # Custom fields — use safe setter in case not installed
    try: item.custom_is_retail_item = 1
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: Financial/Data-integrity-adjacent exception in master_api.py:36: {sys.exc_info()[1]}")
    try: item.custom_gst_percentage = str(gst_percentage)
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: Financial/Data-integrity-adjacent exception in master_api.py:38: {sys.exc_info()[1]}")
    try: item.custom_mrp = flt(mrp)
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: Financial/Data-integrity-adjacent exception in master_api.py:40: {sys.exc_info()[1]}")
    try: item.custom_style_code = style_code or barcode
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: exception setting custom_style_code in master_api.py: {sys.exc_info()[1]}")

    # Set default HSN code for India Compliance
    # Domain-neutral: reads from SMRITI Settings.default_hsn_code (C-2 remediation 2026-07-03)
    try:
        default_hsn = frappe.db.get_single_value("SMRITI Settings", "default_hsn_code") or ""
        if not default_hsn:
            # No domain-specific HSN configured — skip HSN assignment rather than use a wrong default
            frappe.logger().warning(
                "SMRITI: default_hsn_code not set in SMRITI Settings. "
                "Configure it to auto-assign HSN codes on item creation."
            )
        else:
            if not frappe.db.exists("GST HSN Code", default_hsn):
                hsn_doc = frappe.new_doc("GST HSN Code")
                hsn_doc.name = default_hsn
                hsn_doc.hsn_code = default_hsn
                hsn_doc.description = "Auto-created default HSN"
                # reviewed-ignore-permissions: no role restriction — any authenticated user may create items, by design
                hsn_doc.insert(ignore_permissions=True)
            item.gst_hsn_code = default_hsn
            try: item.gn_hsn_code = default_hsn
            except Exception: pass
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().warning(f"SMRITI Warning: exception setting default HSN code in master_api.py: {sys.exc_info()[1]}")
    
    # Auto-resolve Item Tax Template from percentage
    template_name = frappe.db.get_value(
        "Item Tax Template", 
        {"name": ["like", f"%{gst_percentage}%"]}, 
        "name"
    )
    if template_name:
        item.append("taxes", {
            "item_tax_template": template_name,
            "tax_category": ""
        })

    # reviewed-ignore-permissions: no role restriction — any authenticated user may create items, by design
    item.insert(ignore_permissions=True)

    # 2. Add Barcode (redundant if item_code = barcode, but good for ERPNext standard)
    item.append("barcodes", {
        "barcode": barcode,
        "uom": "Nos"
    })
    # reviewed-ignore-permissions: no role restriction — any authenticated user may create items, by design
    item.save(ignore_permissions=True)

    # 3. Create Price List entries
    create_item_price(item.name, "Standard Selling", rate)
    create_item_price(item.name, "MRP", mrp)

    frappe.db.commit()

    return {
        "item_code": item.name,
        "item_name": item.item_name,
        "rate": flt(rate),
        "mrp": flt(mrp),
        "gst_percentage": cint(gst_percentage),
        "stock_uom": "Nos"
    }

def create_item_price(item_code, price_list, rate):
    if not frappe.db.exists("Price List", price_list):
        pl = frappe.new_doc("Price List")
        pl.price_list_name = price_list
        pl.enabled = 1
        pl.selling = 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list},
        "name"
    )
    if existing:
        frappe.db.set_value("Item Price", existing, "price_list_rate", flt(rate))
    else:
        ip = frappe.new_doc("Item Price")
        ip.item_code = item_code
        ip.price_list = price_list
        ip.price_list_rate = flt(rate)
        ip.currency = "INR"
        ip.uom = "Nos"
        ip.insert(ignore_permissions=True)

@frappe.whitelist()
def quick_create_customer(customer_name, mobile_no):
    """
    Simplified Customer creation.
    """
    if not customer_name:
        frappe.throw(_("Customer Name is required."))

    cust = frappe.new_doc("Customer")
    cust.customer_name = customer_name
    cust.mobile_no = mobile_no
    
    # Robust Customer Group auto-resolution
    customer_group = "Individual"
    if not frappe.db.exists("Customer Group", customer_group):
        if frappe.db.exists("Customer Group", "All Customer Groups"):
            customer_group = "All Customer Groups"
        else:
            existing = frappe.db.get_all("Customer Group", order_by="creation asc", pluck="name", limit=1)
            if existing:
                customer_group = existing[0]
            else:
                cg = frappe.new_doc("Customer Group")
                cg.customer_group_name = "Individual"
                # reviewed-ignore-permissions: no role restriction — any authenticated user may create a customer record, by design
                cg.insert(ignore_permissions=True)
                customer_group = cg.name
    cust.customer_group = customer_group

    # Robust Territory auto-resolution
    territory = "All Territories"
    if not frappe.db.exists("Territory", territory):
        existing = frappe.db.get_all("Territory", order_by="creation asc", pluck="name", limit=1)
        if existing:
            territory = existing[0]
        else:
            t = frappe.new_doc("Territory")
            t.territory_name = "All Territories"
            # reviewed-ignore-permissions: no role restriction — any authenticated user may create a customer record, by design
            t.insert(ignore_permissions=True)
            territory = t.name
    cust.territory = territory
    
    cust.customer_type = "Individual"
    # reviewed-ignore-permissions: no role restriction — any authenticated user may create a customer record, by design
    cust.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {
        "name": cust.name,
        "customer_name": cust.customer_name,
        "mobile_no": cust.mobile_no
    }

@frappe.whitelist()
def quick_create_supplier(supplier_name, mobile_no=None):
    """
    Simplified Supplier creation.
    """
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    supp = frappe.new_doc("Supplier")
    supp.supplier_name = supplier_name
    
    # Robust Supplier Group auto-resolution
    supplier_group = "Local"
    if not frappe.db.exists("Supplier Group", supplier_group):
        if frappe.db.exists("Supplier Group", "All Supplier Groups"):
            supplier_group = "All Supplier Groups"
        else:
            existing_groups = frappe.db.get_all("Supplier Group", order_by="creation asc", pluck="name", limit=1)
            if existing_groups:
                supplier_group = existing_groups[0]
            else:
                sg = frappe.new_doc("Supplier Group")
                sg.supplier_group_name = "Local"
                # reviewed-ignore-permissions: no role restriction — any authenticated user may create suppliers, by design
                sg.insert(ignore_permissions=True)
                supplier_group = sg.name
    supp.supplier_group = supplier_group
    
    supp.supplier_type = "Individual"
    if mobile_no:
        supp.mobile_no = mobile_no
    # reviewed-ignore-permissions: no role restriction — any authenticated user may create suppliers, by design
    supp.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    return {
        "name": supp.name,
        "supplier_name": supp.supplier_name
    }


@frappe.whitelist()
def save_supplier_on_fly(supplier_name, supplier_group, supplier_type, name=None):
    """
    Allows creating or updating a Supplier on the fly with permissions bypassed.
    """
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    if name:
        doc = frappe.get_doc("Supplier", name)
        doc.supplier_name = supplier_name
        doc.supplier_group = supplier_group
        doc.supplier_type = supplier_type
        # reviewed-ignore-permissions: no role restriction — any authenticated user may create suppliers, by design
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Supplier")
        doc.supplier_name = supplier_name
        doc.supplier_type = supplier_type
        # Robust group resolution — same as quick_create_supplier
        resolved_group = supplier_group
        if not frappe.db.exists("Supplier Group", resolved_group):
            if frappe.db.exists("Supplier Group", "All Supplier Groups"):
                resolved_group = "All Supplier Groups"
            else:
                existing = frappe.db.get_all("Supplier Group", pluck="name", limit=1)
                resolved_group = existing[0] if existing else "Local"
        doc.supplier_group = resolved_group
        # reviewed-ignore-permissions: no role restriction — any authenticated user may create suppliers, by design
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "name": doc.name,
        "supplier_name": doc.supplier_name
    }


@frappe.whitelist()
def get_customer_detail(name):
    """
    Retrieves all details for a Customer, including dynamic custom fields.
    """
    if not frappe.db.exists("Customer", name):
        frappe.throw(_("Customer {0} not found.").format(name))
    
    doc = frappe.get_doc("Customer", name)
    return {
        "name": doc.name,
        "customer_name": doc.customer_name,
        "customer_type": doc.customer_type,
        "customer_group": doc.customer_group,
        "territory": doc.territory,
        "mobile_no": doc.mobile_no,
        "email_id": doc.email_id,
        "tax_id": doc.tax_id,
        "gst_category": doc.gst_category,
        "pan": doc.pan,
        "custom_address_text": doc.get("custom_address_text") or "",
        "custom_shipping_address_text": doc.get("custom_shipping_address_text") or "",
        "custom_tax_inclusive_override": doc.get("custom_tax_inclusive_override") or "Default"
    }


@frappe.whitelist()
def get_supplier_detail(name):
    """
    Retrieves all details for a Supplier, including standard and advanced fields.
    """
    if not frappe.db.exists("Supplier", name):
        frappe.throw(_("Supplier {0} not found.").format(name))
    
    doc = frappe.get_doc("Supplier", name)
    
    # Resolve Contact Person
    contact_person = None
    contact_link = frappe.db.get_value("Dynamic Link", {"link_doctype": "Supplier", "link_name": doc.name, "parenttype": "Contact"}, "parent")
    if contact_link:
        contact_person = frappe.db.get_value("Contact", contact_link, "first_name")

    # Resolve Status
    status = "Active"
    if doc.disabled:
        status = "Disabled"
    elif doc.on_hold:
        status = "On Hold"

    return {
        "name": doc.name,
        "naming_series": doc.naming_series,
        "supplier_name": doc.supplier_name,
        "supplier_type": doc.supplier_type,
        "supplier_group": doc.supplier_group,
        "mobile_no": doc.mobile_no,
        "email_id": doc.email_id,
        "gstin": doc.gstin,
        "gst_category": doc.gst_category,
        "pan": doc.pan,
        "custom_credit_days": doc.get("custom_credit_days") or 0,
        "custom_address_text": doc.get("custom_address_text") or "",
        "custom_shipping_address_text": doc.get("custom_shipping_address_text") or "",
        "contact_person": contact_person,
        "status": status,
        "custom_vendor_code": doc.get("custom_vendor_code") or "",
        
        # Advanced fields
        "default_currency": doc.default_currency,
        "default_bank_account": doc.default_bank_account,
        "default_price_list": doc.default_price_list,
        "payment_terms": doc.payment_terms,
        "is_internal_supplier": doc.is_internal_supplier,
        "represents_company": doc.represents_company,
        "is_transporter": doc.is_transporter,
        "allow_purchase_invoice_creation_without_purchase_order": doc.allow_purchase_invoice_creation_without_purchase_order,
        "allow_purchase_invoice_creation_without_purchase_receipt": doc.allow_purchase_invoice_creation_without_purchase_receipt,
        "is_frozen": doc.is_frozen,
        "hold_type": doc.hold_type,
        "release_date": doc.release_date,
        "warn_rfqs": doc.warn_rfqs,
        "prevent_rfqs": doc.prevent_rfqs,
        "warn_pos": doc.warn_pos,
        "prevent_pos": doc.prevent_pos,
        "website": doc.website,
        "language": doc.language,
        "supplier_details": doc.supplier_details
    }


@frappe.whitelist()
def save_supplier_detail(**kwargs):
    """
    Saves or updates a Supplier with complete operational, India compliance, and advanced fields.
    """
    supplier_name = kwargs.get("supplier_name")
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    name = kwargs.get("name")
    if name:
        doc = frappe.get_doc("Supplier", name)
    else:
        doc = frappe.new_doc("Supplier")

    # Basic fields
    if kwargs.get("naming_series"):
        doc.naming_series = kwargs.get("naming_series")
    doc.supplier_name = supplier_name
    doc.supplier_type = kwargs.get("supplier_type") or "Company"
    doc.supplier_group = kwargs.get("supplier_group") or "Local"
    doc.mobile_no = kwargs.get("mobile_no")
    doc.email_id = kwargs.get("email_id")
    doc.gstin = kwargs.get("gstin")
    doc.gst_category = kwargs.get("gst_category") or "Registered Regular"
    doc.pan = kwargs.get("pan")
    doc.custom_credit_days = cint(kwargs.get("custom_credit_days") or 0)
    doc.custom_address_text = kwargs.get("custom_address_text")
    doc.custom_shipping_address_text = kwargs.get("custom_shipping_address_text")
    # Clean vendor code: treat NA, N/A, None, NULL, DV, etc. as None (NULL) to prevent database uniqueness collisions
    vendor_code = kwargs.get("custom_vendor_code")
    if vendor_code:
        vendor_code_clean = str(vendor_code).strip().upper()
        if vendor_code_clean in ("", "NA", "N/A", "NONE", "NULL", "NAN", "DV"):
            doc.custom_vendor_code = None
        else:
            doc.custom_vendor_code = str(vendor_code).strip()
    else:
        doc.custom_vendor_code = None

    # Status mapping
    status = kwargs.get("status") or "Active"
    if status == "Disabled":
        doc.disabled = 1
        doc.on_hold = 0
    elif status == "On Hold":
        doc.disabled = 0
        doc.on_hold = 1
        doc.hold_type = kwargs.get("hold_type") or "All"
        doc.release_date = kwargs.get("release_date")
    else:
        doc.disabled = 0
        doc.on_hold = 0
        doc.hold_type = None
        doc.release_date = None

    # Advanced fields
    doc.default_currency = kwargs.get("default_currency")
    doc.default_bank_account = kwargs.get("default_bank_account")
    doc.default_price_list = kwargs.get("default_price_list")
    doc.payment_terms = kwargs.get("payment_terms")
    doc.is_internal_supplier = cint(kwargs.get("is_internal_supplier") or 0)
    doc.represents_company = kwargs.get("represents_company")
    doc.is_transporter = cint(kwargs.get("is_transporter") or 0)
    doc.allow_purchase_invoice_creation_without_purchase_order = cint(kwargs.get("allow_purchase_invoice_creation_without_purchase_order") or 0)
    doc.allow_purchase_invoice_creation_without_purchase_receipt = cint(kwargs.get("allow_purchase_invoice_creation_without_purchase_receipt") or 0)
    doc.is_frozen = cint(kwargs.get("is_frozen") or 0)
    if status != "On Hold" and kwargs.get("hold_type"):
        doc.hold_type = kwargs.get("hold_type")
        doc.release_date = kwargs.get("release_date")
    doc.warn_rfqs = cint(kwargs.get("warn_rfqs") or 0)
    doc.prevent_rfqs = cint(kwargs.get("prevent_rfqs") or 0)
    doc.warn_pos = cint(kwargs.get("warn_pos") or 0)
    doc.prevent_pos = cint(kwargs.get("prevent_pos") or 0)
    doc.website = kwargs.get("website")
    doc.language = kwargs.get("language")
    doc.supplier_details = kwargs.get("supplier_details")

    # Defensive group check for fresh installs
    if not frappe.db.exists("Supplier Group", doc.supplier_group):
        sg = frappe.new_doc("Supplier Group")
        sg.supplier_group_name = doc.supplier_group
        # reviewed-ignore-permissions: no role restriction — any authenticated user may update supplier records, by design
        sg.insert(ignore_permissions=True)

    # reviewed-ignore-permissions: no role restriction — any authenticated user may update supplier records, by design
    doc.save(ignore_permissions=True)

    # Contact Person processing
    contact_person = kwargs.get("contact_person")
    if contact_person:
        contact_link = frappe.db.get_value("Dynamic Link", {"link_doctype": "Supplier", "link_name": doc.name, "parenttype": "Contact"}, "parent")
        if contact_link:
            contact = frappe.get_doc("Contact", contact_link)
            contact.first_name = contact_person
            if doc.mobile_no:
                contact.mobile_no = doc.mobile_no
            if doc.email_id:
                contact.email_id = doc.email_id
            # reviewed-ignore-permissions: no role restriction — any authenticated user may update supplier records, by design
            contact.save(ignore_permissions=True)
        else:
            contact = frappe.new_doc("Contact")
            contact.first_name = contact_person
            if doc.mobile_no:
                contact.mobile_no = doc.mobile_no
            if doc.email_id:
                contact.email_id = doc.email_id
            contact.append("links", {
                "link_doctype": "Supplier",
                "link_name": doc.name
            })
            # reviewed-ignore-permissions: no role restriction — any authenticated user may update supplier records, by design
            contact.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "name": doc.name,
        "supplier_name": doc.supplier_name,
        "mobile_no": doc.mobile_no
    }


@frappe.whitelist()
def save_customer_detail(customer_name, customer_type, customer_group, territory, mobile_no, email_id, tax_id, gst_category, pan, custom_address_text, custom_shipping_address_text=None, custom_tax_inclusive_override="Default", name=None):
    """
    Saves or updates a Customer with complete operational and India compliance fields.
    """
    if not customer_name:
        frappe.throw(_("Customer Name is required."))

    if name:
        doc = frappe.get_doc("Customer", name)
    else:
        doc = frappe.new_doc("Customer")

    doc.customer_name = customer_name
    doc.customer_type = customer_type
    doc.customer_group = customer_group or "Individual"
    doc.territory = territory or "All Territories"
    doc.mobile_no = mobile_no
    doc.email_id = email_id
    doc.tax_id = tax_id
    doc.gst_category = gst_category
    doc.pan = pan
    doc.custom_address_text = custom_address_text
    doc.custom_shipping_address_text = custom_shipping_address_text
    doc.custom_tax_inclusive_override = custom_tax_inclusive_override

    # Defensive group and territory check for fresh installs
    if not frappe.db.exists("Customer Group", doc.customer_group):
        cg = frappe.new_doc("Customer Group")
        cg.customer_group_name = doc.customer_group
        # reviewed-ignore-permissions: no role restriction — any authenticated user may update customer records, by design
        cg.insert(ignore_permissions=True)

    if not frappe.db.exists("Territory", doc.territory):
        t = frappe.new_doc("Territory")
        t.territory_name = doc.territory
        # reviewed-ignore-permissions: no role restriction — any authenticated user may update customer records, by design
        t.insert(ignore_permissions=True)

    # reviewed-ignore-permissions: no role restriction — any authenticated user may update customer records, by design
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": doc.name,
        "customer_name": doc.customer_name,
        "mobile_no": doc.mobile_no
    }



# ──────────────────────────────────────────────────────────────────────────────
# Configuration Portal APIs
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_SIZE_GROUPS = [
    {"id": "footwear", "label": "Footwear (Adult)",  "sizes": ["36","37","38","39","40","41","42"]},
    {"id": "garment",  "label": "Garment (Standard)","sizes": ["XS","S","M","L","XL","XXL","3XL"]},
    {"id": "kids",     "label": "Kids Footwear",      "sizes": ["18","20","22","24","26","28","30"]},
]

_DEFAULT_STATE_TAX_MAP = [
    {"state_code": "27", "state_name": "Maharashtra", "tax_type": "intrastate"},
    {"state_code": "29", "state_name": "Karnataka",   "tax_type": "interstate"},
]


def _check_config_permission():
    """Only SMRITI Store Manager and System Manager can edit configurations."""
    if frappe.session.user == "Administrator":
        return
    roles = frappe.get_roles(frappe.session.user)
    if not ({"SMRITI Store Manager", "System Manager"} & set(roles)):
        frappe.throw(
            _("Access Denied: Only Store Managers and System Managers can edit master configurations."),
            frappe.PermissionError
        )


# ── Size Groups ──────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_size_groups():
    """Returns configured size groups for footwear/garment matrix presets."""
    raw = frappe.db.get_default("smriti_size_groups")
    if raw:
        try:
            return frappe.parse_json(raw)
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in master_api.py:519: {sys.exc_info()[1]}")
    return _DEFAULT_SIZE_GROUPS


@frappe.whitelist()
def save_size_groups(size_groups):
    """Saves named size groups to global defaults."""
    _check_config_permission()
    data = frappe.parse_json(size_groups) if isinstance(size_groups, str) else size_groups
    frappe.db.set_default("smriti_size_groups", frappe.as_json(data))
    frappe.db.commit()
    return {"success": True, "count": len(data)}


# ── Destinationwise (State) Tax Mappings ────────────────────────────────────

@frappe.whitelist()
def get_destinationwise_taxes():
    """Returns state-code to tax-type mappings for automatic invoice routing."""
    raw = frappe.db.get_default("smriti_destinationwise_taxes")
    if raw:
        try:
            return frappe.parse_json(raw)
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in master_api.py:543: {sys.exc_info()[1]}")
    return _DEFAULT_STATE_TAX_MAP


@frappe.whitelist()
def save_destinationwise_taxes(mappings):
    """Saves state→tax type mappings to global defaults."""
    _check_config_permission()
    data = frappe.parse_json(mappings) if isinstance(mappings, str) else mappings
    frappe.db.set_default("smriti_destinationwise_taxes", frappe.as_json(data))
    frappe.db.commit()
    return {"success": True, "count": len(data)}


# ── Item Tax Templates ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_item_tax_templates():
    """Returns all Item Tax Templates with their tax account details."""
    from smriti_retail_os.company_api import get_active_company
    company = get_active_company()
    templates = frappe.get_all(
        "Item Tax Template",
        filters={"company": company} if company else {},
        fields=["name", "title", "company", "gst_rate", "gst_treatment"],
        order_by="creation asc"
    )
    for t in templates:
        t["taxes"] = frappe.get_all(
            "Item Tax Template Detail",
            filters={"parent": t["name"]},
            fields=["tax_type", "tax_rate"],
            order_by="idx asc"
        )
    return templates


@frappe.whitelist()
def create_item_tax_template(title, gst_rate, taxes):
    """
    Creates a new Item Tax Template.

    taxes: list of {tax_type: account_name, tax_rate: float}
    """
    _check_config_permission()
    gst_rate = flt(gst_rate)
    taxes_data = frappe.parse_json(taxes) if isinstance(taxes, str) else taxes
    from smriti_retail_os.company_api import get_active_company
    company = get_active_company()

    # Check if already exists
    full_title = f"{title} - {company}"
    existing = frappe.db.get_value("Item Tax Template", {"title": full_title, "company": company}, "name")
    if existing:
        frappe.throw(_(f"Item Tax Template '{full_title}' already exists. Edit it directly in ERPNext."))

    doc = frappe.new_doc("Item Tax Template")
    doc.title = full_title
    doc.company = company
    doc.gst_rate = gst_rate
    doc.gst_treatment = "Taxable"
    for row in taxes_data:
        if row.get("tax_type") and frappe.db.exists("Account", row["tax_type"]):
            doc.append("taxes", {
                "tax_type": row["tax_type"],
                "tax_rate": flt(row.get("tax_rate", 0))
            })

    # reviewed-ignore-permissions: tax configuration creation, gated by SMRITI Store Manager or System Manager roles
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "title": doc.title}


# ── Brand Management ─────────────────────────────────────────────────────────

@frappe.whitelist()
def get_brands():
    """Returns all Brands registered in ERPNext."""
    # Note: ERPNext v16 Brand DocType uses 'description' not 'brand_description'.
    brands = frappe.get_all(
        "Brand",
        fields=["name", "brand", "description", "image"],
        order_by="brand asc"
    )
    return brands


@frappe.whitelist()
def create_brand(brand_name, brand_description=None):
    """Creates a new Brand document in ERPNext."""
    _check_config_permission()
    brand_name = (brand_name or "").strip()
    if not brand_name:
        frappe.throw(_("Brand name is required."))

    if frappe.db.exists("Brand", brand_name):
        frappe.throw(_(f"Brand '{brand_name}' already exists."))

    doc = frappe.new_doc("Brand")
    doc.brand = brand_name
    if brand_description:
        # ERPNext v16 uses 'description'; older versions used 'brand_description'.
        try:
            doc.description = brand_description
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in master_api.py:648: {sys.exc_info()[1]}")
    # reviewed-ignore-permissions: catalog brand creation, gated by SMRITI Store Manager or System Manager roles
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "brand": doc.brand}


@frappe.whitelist()
def delete_brand(brand_name):
    """Deletes a Brand document. Fails if items are linked to it."""
    _check_config_permission()
    if not frappe.db.exists("Brand", brand_name):
        frappe.throw(_(f"Brand '{brand_name}' not found."))
    linked = frappe.db.count("Item", {"brand": brand_name})
    if linked:
        frappe.throw(_(f"Cannot delete brand '{brand_name}': {linked} item(s) are linked to it."))
    # reviewed-ignore-permissions: catalog brand deletion, gated by SMRITI Store Manager or System Manager roles
    frappe.delete_doc("Brand", brand_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


# ── Tax Accounts (for template builder) ─────────────────────────────────────

@frappe.whitelist()
def get_tax_accounts():
    """Returns CGST, SGST, IGST tax accounts for the active company."""
    from smriti_retail_os.company_api import get_active_company
    company = get_active_company()
    accounts = frappe.get_all(
        "Account",
        filters={"company": company, "account_type": "Tax", "is_group": 0},
        fields=["name", "account_name"],
        order_by="account_name asc"
    )
    return accounts
