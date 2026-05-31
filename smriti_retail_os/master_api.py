# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/master_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint
from frappe import _

@frappe.whitelist()
def quick_create_item(item_name, barcode, rate, mrp, gst_percentage):
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
    except Exception: pass
    try: item.custom_gst_percentage = str(gst_percentage)
    except Exception: pass
    try: item.custom_mrp = flt(mrp)
    except Exception: pass
    
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

    item.insert(ignore_permissions=True)

    # 2. Add Barcode (redundant if item_code = barcode, but good for ERPNext standard)
    item.append("barcodes", {
        "barcode": barcode,
        "uom": "Nos"
    })
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
            t.insert(ignore_permissions=True)
            territory = t.name
    cust.territory = territory
    
    cust.customer_type = "Individual"
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
                sg.insert(ignore_permissions=True)
                supplier_group = sg.name
    supp.supplier_group = supplier_group
    
    supp.supplier_type = "Individual"
    if mobile_no:
        supp.mobile_no = mobile_no
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
    Retrieves all details for a Supplier, including dynamic custom fields.
    """
    if not frappe.db.exists("Supplier", name):
        frappe.throw(_("Supplier {0} not found.").format(name))
    
    doc = frappe.get_doc("Supplier", name)
    return {
        "name": doc.name,
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
        "custom_shipping_address_text": doc.get("custom_shipping_address_text") or ""
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
        cg.insert(ignore_permissions=True)

    if not frappe.db.exists("Territory", doc.territory):
        t = frappe.new_doc("Territory")
        t.territory_name = doc.territory
        t.insert(ignore_permissions=True)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": doc.name,
        "customer_name": doc.customer_name,
        "mobile_no": doc.mobile_no
    }


@frappe.whitelist()
def save_supplier_detail(supplier_name, supplier_type, supplier_group, mobile_no, email_id, gstin, gst_category, pan, custom_credit_days, custom_address_text, custom_shipping_address_text=None, name=None):
    """
    Saves or updates a Supplier with complete operational and India compliance fields.
    """
    if not supplier_name:
        frappe.throw(_("Supplier Name is required."))

    if name:
        doc = frappe.get_doc("Supplier", name)
    else:
        doc = frappe.new_doc("Supplier")

    doc.supplier_name = supplier_name
    doc.supplier_type = supplier_type
    doc.supplier_group = supplier_group or "Local"
    doc.mobile_no = mobile_no
    doc.email_id = email_id
    doc.gstin = gstin
    doc.gst_category = gst_category
    doc.pan = pan
    doc.custom_credit_days = cint(custom_credit_days)
    doc.custom_address_text = custom_address_text
    doc.custom_shipping_address_text = custom_shipping_address_text

    # Defensive group check for fresh installs
    if not frappe.db.exists("Supplier Group", doc.supplier_group):
        sg = frappe.new_doc("Supplier Group")
        sg.supplier_group_name = doc.supplier_group
        sg.insert(ignore_permissions=True)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": doc.name,
        "supplier_name": doc.supplier_name,
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
            pass
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
            pass
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
    company = (
        frappe.defaults.get_user_default("company")
        or frappe.db.get_value("Company", {}, "name")
    )
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
    company = (
        frappe.defaults.get_user_default("company")
        or frappe.db.get_value("Company", {}, "name")
    )

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

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "title": doc.title}


# ── Brand Management ─────────────────────────────────────────────────────────

@frappe.whitelist()
def get_brands():
    """Returns all Brands registered in ERPNext."""
    brands = frappe.get_all(
        "Brand",
        fields=["name", "brand", "brand_description", "image"],
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
        doc.brand_description = brand_description
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
    frappe.delete_doc("Brand", brand_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


# ── Tax Accounts (for template builder) ─────────────────────────────────────

@frappe.whitelist()
def get_tax_accounts():
    """Returns CGST, SGST, IGST tax accounts for the default company."""
    company = (
        frappe.defaults.get_user_default("company")
        or frappe.db.get_value("Company", {}, "name")
    )
    accounts = frappe.get_all(
        "Account",
        filters={"company": company, "account_type": "Tax", "is_group": 0},
        fields=["name", "account_name"],
        order_by="account_name asc"
    )
    return accounts
