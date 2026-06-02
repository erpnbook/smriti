# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/company_api.py
# @description: Centralised company utilities and SMRITI Company Settings CRUD.
#               Replaces the duplicated company-resolution pattern found in 15+
#               API files and provides per-company retail configuration storage.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
from frappe import _
from frappe.utils import flt, cint

# ─── Permission helper ───────────────────────────────────────────────────────

def _check_manager_permission():
    """Raises PermissionError if caller is not a Store Manager / System Manager."""
    if frappe.session.user in ("Administrator",):
        return
    roles = set(frappe.get_roles(frappe.session.user))
    allowed = {"SMRITI Store Manager", "System Manager"}
    if not (roles & allowed):
        frappe.throw(
            _("Only SMRITI Store Managers can modify Company Settings."),
            frappe.PermissionError
        )

# ─── Core company resolution ─────────────────────────────────────────────────

def get_active_company():
    """
    Centralised company resolver — use this everywhere instead of duplicating:
        frappe.defaults.get_user_default("company") or
        frappe.get_all("Company", limit=1)[0].name

    Returns:
        str: Name of the active company, or None if no company exists.
    """
    company = frappe.defaults.get_user_default("company")
    if not company:
        companies = frappe.get_all("Company", limit=1, pluck="name")
        company = companies[0] if companies else None
    return company


@frappe.whitelist()
def list_companies():
    """Return all companies for multi-company selector UI."""
    return frappe.get_all(
        "Company",
        fields=["name", "company_name", "country", "default_currency", "gstin"],
        order_by="company_name asc"
    )

# ─── SMRITI Company Settings CRUD ───────────────────────────────────────────

_SETTINGS_DOCTYPE = "SMRITI Company Settings"

def _default_settings(company):
    """Return a blank settings dict for a company that has no record yet."""
    return {
        "company": company,
        "store_trade_name": company,
        "store_logo_url": "",
        "brand_color": "#1a73e8",
        "receipt_footer_text": "Thank you for shopping with us!",
        "invoice_series_prefix": "SINV-",
        "default_warehouse": "",
        "default_pos_profile": "",
        "default_walk_in_customer": "",
        "default_intrastate_tax_template": "",
        "default_interstate_tax_template": "",
        "loyalty_enabled": 0,
        "loyalty_points_per_rupee": 1.0,
        # Migrate global defaults to per-company on first access
        "size_groups_json": frappe.db.get_default("smriti_size_groups") or "[]",
        "destinationwise_taxes_json": frappe.db.get_default("smriti_destinationwise_taxes") or "[]",
        "backup_settings_json": frappe.db.get_default("smriti_backup_settings") or "{}",
    }


@frappe.whitelist()
def get_company_settings(company=None):
    """
    Return SMRITI Company Settings for the given (or active) company.
    Creates a blank record on-the-fly if none exists yet.

    Returns:
        dict: Flat settings dictionary safe for JSON serialisation.
    """
    if not company:
        company = get_active_company()
    if not company:
        return {}

    if frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company}):
        doc = frappe.get_doc(_SETTINGS_DOCTYPE, {"company": company})
        return doc.as_dict()
    else:
        # Return in-memory defaults — do NOT auto-save (avoid side-effects on read)
        return _default_settings(company)


@frappe.whitelist()
def save_company_settings(company=None, settings=None):
    """
    Upsert SMRITI Company Settings for the given company.

    Args:
        company (str): Company name.
        settings (str | dict): JSON string or dict of field→value pairs.

    Returns:
        dict: Saved settings as dict.
    """
    _check_manager_permission()

    if not company:
        company = get_active_company()
    if not company:
        frappe.throw(_("No company found. Please create a Company first."))

    if isinstance(settings, str):
        settings = json.loads(settings)

    # Sanitise — only allow known writable fields
    allowed_fields = {
        "store_trade_name", "store_logo_url", "brand_color",
        "receipt_footer_text", "invoice_series_prefix",
        "default_warehouse", "default_pos_profile", "default_walk_in_customer",
        "default_intrastate_tax_template", "default_interstate_tax_template",
        "loyalty_enabled", "loyalty_points_per_rupee",
        "size_groups_json", "destinationwise_taxes_json", "backup_settings_json"
    }
    clean = {k: v for k, v in (settings or {}).items() if k in allowed_fields}

    existing = frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company})
    if existing:
        doc = frappe.get_doc(_SETTINGS_DOCTYPE, existing)
        doc.update(clean)
        doc.save(ignore_permissions=True)
    else:
        defaults = _default_settings(company)
        defaults.update(clean)
        doc = frappe.new_doc(_SETTINGS_DOCTYPE)
        doc.update(defaults)
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    return doc.as_dict()


@frappe.whitelist()
def get_store_address(company=None):
    """
    Return standard Company Address details in a flat dict.
    Treats ERPNext standard Address DocType as Single Source of Truth.
    """
    if not company:
        company = get_active_company()
    if not company:
        return {}
        
    address_name = f"{company}-Registered"
    if not frappe.db.exists("Address", address_name):
        # Search links
        res = frappe.db.sql("""
            SELECT parent FROM `tabAddress Link` 
            WHERE link_doctype='Company' AND link_name=%s
        """, (company,))
        if res:
            address_name = res[0][0]
        else:
            # Return empty default
            return {
                "address_title": company,
                "address_line1": "",
                "address_line2": "",
                "city": "",
                "state": "",
                "country": "India",
                "pincode": "",
                "gstin": "",
                "gst_state": "",
                "gst_state_number": "",
                "landmark": "",
                "latitude": None,
                "longitude": None
            }
            
    addr = frappe.get_doc("Address", address_name)
    return {
        "address_title": addr.address_title,
        "address_line1": addr.address_line1,
        "address_line2": addr.address_line2,
        "city": addr.city,
        "state": addr.state,
        "country": addr.country or "India",
        "pincode": addr.pincode,
        "gstin": addr.gstin,
        "gst_state": addr.gst_state,
        "gst_state_number": addr.gst_state_number,
        "landmark": addr.landmark,
        "latitude": addr.latitude,
        "longitude": addr.longitude
    }


@frappe.whitelist()
def save_store_address(company=None, address_data=None):
    """
    Saves/Updates the standard Company Address linked to the Company.
    Restricted to SMRITI Store Manager and System Manager.
    """
    _check_manager_permission()
    
    if not company:
        company = get_active_company()
    if not company:
        frappe.throw(_("No company specified."))
        
    if isinstance(address_data, str):
        address_data = json.loads(address_data)
        
    if not address_data:
        address_data = {}
        
    # Mandatory validation
    mandatory = {
        "address_title": "Store Name",
        "address_line1": "Address Line 1",
        "city": "City",
        "state": "State",
        "country": "Country",
        "pincode": "Pincode / ZIP Code"
    }
    for field, label in mandatory.items():
        if not address_data.get(field) or str(address_data.get(field)).strip() == "":
            frappe.throw(_("{0} is mandatory.").format(label))
            
    address_name = f"{company}-Registered"
    
    existing_addr = None
    if frappe.db.exists("Address", address_name):
        existing_addr = address_name
    else:
        res = frappe.db.sql("""
            SELECT parent FROM `tabAddress Link` 
            WHERE link_doctype='Company' AND link_name=%s
        """, (company,))
        if res:
            existing_addr = res[0][0]
            
    if existing_addr:
        addr = frappe.get_doc("Address", existing_addr)
    else:
        addr = frappe.new_doc("Address")
        addr.address_title = address_data.get("address_title") or company
        addr.address_type = "Office"
        addr.is_primary_address = 1
        addr.is_shipping_address = 1
        addr.is_your_company_address = 1
        addr.append("links", {"link_doctype": "Company", "link_name": company})
        
    # Note: Change logging is automatically handled globally by the standard Address DocType event hook!
    addr.address_title = address_data.get("address_title")
    addr.address_line1 = address_data.get("address_line1")
    addr.address_line2 = address_data.get("address_line2")
    addr.city = address_data.get("city")
    addr.state = address_data.get("state")
    addr.country = address_data.get("country") or "India"
    addr.pincode = address_data.get("pincode")
    addr.landmark = address_data.get("landmark")
    
    # Try parsing Lat/Lng safely
    try:
        lat = address_data.get("latitude")
        addr.latitude = flt(lat) if lat is not None and str(lat).strip() != "" else None
    except Exception:
        addr.latitude = None
    try:
        lng = address_data.get("longitude")
        addr.longitude = flt(lng) if lng is not None and str(lng).strip() != "" else None
    except Exception:
        addr.longitude = None
        
    gstin = frappe.db.get_value("Company", company, "gstin")
    if gstin:
        addr.gstin = gstin
        addr.gst_category = "Registered"
    else:
        addr.gst_category = "Unregistered"
        
    addr.gst_state = address_data.get("state")
    addr.gst_state_number = address_data.get("gst_state_number")
    
    addr.save(ignore_permissions=True)
    frappe.db.commit()
    return {
        "success": True,
        "message": "Store primary address updated successfully!"
    }


def ensure_company_settings(doc, method=None):
    """
    Frappe doc_event hook — fires on Company after_insert and on_update.
    Silently creates a blank SMRITI Company Settings record if missing.
    """
    company = doc.name if hasattr(doc, "name") else str(doc)
    if not frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company}):
        try:
            defaults = _default_settings(company)
            new_doc = frappe.new_doc(_SETTINGS_DOCTYPE)
            new_doc.update(defaults)
            new_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(
                f"[SMRITI] Created Company Settings for: {company}"
            )
        except Exception as e:
            frappe.log_error(
                f"[SMRITI] Failed to auto-create Company Settings for {company}: {e}",
                "Company Settings Auto-Provision"
            )


# ─── Convenience getters for other API modules ───────────────────────────────

def get_setting(key, company=None, default=None):
    """
    Shortcut to read a single Company Settings value.

    Usage:
        from smriti_retail_os.company_api import get_setting
        footer = get_setting("receipt_footer_text")
    """
    settings = get_company_settings(company)
    return settings.get(key, default)


def get_size_groups(company=None):
    """Return parsed size groups list (migrated from global smriti_size_groups)."""
    raw = get_setting("size_groups_json", company, "[]")
    try:
        return json.loads(raw)
    except Exception:
        return []


def get_destinationwise_taxes(company=None):
    """Return parsed tax mappings list (migrated from global smriti_destinationwise_taxes)."""
    raw = get_setting("destinationwise_taxes_json", company, "[]")
    try:
        return json.loads(raw)
    except Exception:
        return []


def get_backup_settings(company=None):
    """Return parsed backup settings dict (migrated from global smriti_backup_settings)."""
    raw = get_setting("backup_settings_json", company, "{}")
    try:
        return json.loads(raw)
    except Exception:
        return {}
