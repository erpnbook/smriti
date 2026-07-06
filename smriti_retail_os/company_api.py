# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/company_api.py
# @description: Centralised company utilities and SMRITI Company Settings CRUD.
#               Replaces the duplicated company-resolution pattern found in 15+
#               API files and provides per-company retail configuration storage.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
from frappe import _
from frappe.utils import flt, cint
from smriti_retail_os.repositories.company_repository import CompanyRepository

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
def get_business_type():
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    try:
        company = frappe.defaults.get_user_default("company") or (frappe.get_all("Company", limit=1)[0].name if frappe.get_all("Company", limit=1) else None)
        if company and frappe.db.exists("SMRITI Company Settings", company):
            bt = frappe.db.get_value("SMRITI Company Settings", company, "custom_business_type")
            return bt or "Footwear"
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SMRITI: get_business_type failed")
    return "Footwear"

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
    Also augments the result with Company-level custom fields
    (custom_smriti_store_type, custom_smriti_gstin_state,
    custom_smriti_settings_configured) so the frontend only needs
    one whitelisted API call instead of two.

    Returns:
        dict: Flat settings dictionary safe for JSON serialisation.
    """
    if not company:
        company = get_active_company()
    if not company:
        return {}

    if frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company}):
        doc = CompanyRepository.get_doc(_SETTINGS_DOCTYPE, {"company": company})
        result = doc.as_dict()
    else:
        # Return in-memory defaults — do NOT auto-save (avoid side-effects on read)
        result = _default_settings(company)

    # Augment with Company-level custom fields so the frontend can get
    # everything in a single call without using frappe.client.get_value.
    company_extras = frappe.db.get_value(
        "Company",
        company,
        ["custom_smriti_store_type", "custom_smriti_gstin_state",
         "custom_smriti_settings_configured", "gstin"],
        as_dict=True
    ) or {}
    result.update(company_extras)
    return result


@frappe.whitelist()
def save_company_settings(company=None, settings=None):
    """
    Upsert SMRITI Company Settings for the given company.
    Also writes Company-level custom fields (e.g. custom_smriti_store_type)
    so the frontend needs only one save call instead of three.

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

    settings = dict(settings or {})

    # Write Company-level custom fields directly to the Company DocType.
    # These are NOT stored in SMRITI Company Settings.
    _COMPANY_DIRECT_FIELDS = {"custom_smriti_store_type", "gstin"}
    for field in _COMPANY_DIRECT_FIELDS:
        if field in settings:
            CompanyRepository.set_value("Company", company, field, settings.pop(field))

    # Sanitise — only allow known writable SMRITI Settings fields
    allowed_fields = {
        "store_trade_name", "store_logo_url", "brand_color",
        "receipt_footer_text", "invoice_series_prefix",
        "default_warehouse", "default_pos_profile", "default_walk_in_customer",
        "default_intrastate_tax_template", "default_interstate_tax_template",
        "loyalty_enabled", "loyalty_points_per_rupee",
        "size_groups_json", "destinationwise_taxes_json", "backup_settings_json"
    }
    clean = {k: v for k, v in settings.items() if k in allowed_fields}

    existing = frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company})
    if existing:
        doc = CompanyRepository.get_doc(_SETTINGS_DOCTYPE, existing)
        doc.update(clean)
        # reviewed-ignore-permissions: company preferences updates, gated by SMRITI Store Manager or System Manager roles
        doc.save(ignore_permissions=True)
    else:
        defaults = _default_settings(company)
        defaults.update(clean)
        doc = CompanyRepository.new_doc(_SETTINGS_DOCTYPE)
        doc.update(defaults)
        # reviewed-ignore-permissions: company preferences updates, gated by SMRITI Store Manager or System Manager roles
        doc.insert(ignore_permissions=True)

    CompanyRepository.commit()
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
        # Use the Frappe ORM Dynamic Link table (tabAddress Link does not
        # exist in Frappe v15+; the correct table is tabDynamic Link).
        links = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
            fields=["parent"],
            limit=1
        )
        if links:
            address_name = links[0].parent
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
            
    addr = CompanyRepository.get_doc("Address", address_name)
    # Use addr.get() for all optional / India-Compliance-specific fields.
    # Direct attribute access (addr.gstin) raises AttributeError when the
    # column does not exist in this ERPNext installation (e.g. migration not run).
    return {
        "address_title": addr.get("address_title", ""),
        "address_line1": addr.get("address_line1", ""),
        "address_line2": addr.get("address_line2", ""),
        "city":          addr.get("city", ""),
        "state":         addr.get("state", ""),
        "country":       addr.get("country") or "India",
        "pincode":       addr.get("pincode", ""),
        "gstin":         addr.get("gstin", ""),
        "gst_state":     addr.get("gst_state", ""),
        "gst_state_number": addr.get("gst_state_number", ""),
        "landmark":      addr.get("landmark", ""),
        "latitude":      addr.get("latitude"),
        "longitude":     addr.get("longitude"),
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
        # Use Frappe ORM Dynamic Link (tabAddress Link removed in Frappe v15+)
        links = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
            fields=["parent"],
            limit=1
        )
        if links:
            existing_addr = links[0].parent
            
    if existing_addr:
        addr = CompanyRepository.get_doc("Address", existing_addr)
    else:
        addr = CompanyRepository.new_doc("Address")
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
    
    # reviewed-ignore-permissions: store location metadata updates, gated by SMRITI Store Manager or System Manager roles
    addr.save(ignore_permissions=True)
    CompanyRepository.commit()
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
            new_doc = CompanyRepository.new_doc(_SETTINGS_DOCTYPE)
            new_doc.update(defaults)
            new_doc.flags.ignore_links = True  # Prevent "Could not find Row #N: Company" — hook fires inside Company.after_insert before outer commit
            new_doc.insert(ignore_permissions=True)
            # NOTE: Do NOT call CompanyRepository.commit() here — this hook fires inside Company.after_insert
            # and committing mid-hook corrupts ERPNext's own chart-of-accounts setup transaction.
            frappe.logger().info(
                f"[SMRITI] Created Company Settings for: {company}"
            )
        except Exception as e:
            frappe.log_error(
                f"[SMRITI] Failed to auto-create Company Settings for {company}: {e}",
                "Company Settings Auto-Provision"
            )


# ─── Company CRUD ──────────────────────────────────────────────────────

@frappe.whitelist()
def create_company(company_name, abbr, country="India", default_currency="INR", gstin=None):
    """
    Create a new ERPNext Company with optional GSTIN.
    Triggers ERPNext chart-of-accounts setup automatically via insert().
    """
    _check_manager_permission()

    company_name = (company_name or "").strip()
    abbr = (abbr or "").strip()

    if not company_name:
        frappe.throw(_("Company Name is mandatory."))
    if not abbr:
        frappe.throw(_("Abbreviation is mandatory."))
    if frappe.db.exists("Company", company_name):
        frappe.throw(_("Company '{0}' already exists.").format(company_name))
    if frappe.db.exists("Company", {"abbr": abbr}):
        frappe.throw(_("Abbreviation '{0}' is already used by another company.").format(abbr))

    doc = CompanyRepository.new_doc("Company")
    doc.company_name = company_name
    doc.abbr = abbr
    doc.country = country or "India"
    doc.default_currency = default_currency or "INR"
    if gstin:
        doc.gstin = gstin.strip().upper()

    # reviewed-ignore-permissions: system provisioning of new organization entity, gated by SMRITI Store Manager or System Manager roles
    doc.insert(ignore_permissions=True)
    CompanyRepository.commit()

    # Auto-provision SMRITI Company Settings
    ensure_company_settings(doc)

    return {
        "name": doc.name,
        "company_name": doc.company_name,
        "abbr": doc.abbr,
        "country": doc.country,
        "default_currency": doc.default_currency,
        "gstin": doc.gstin or ""
    }


@frappe.whitelist()
def update_company(company, company_name=None, gstin=None, default_currency=None):
    """
    Update basic Company fields (display name, GSTIN, currency).
    Abbreviation is intentionally not editable — ERPNext appends it to all
    GL account names and changing it causes data inconsistency.
    """
    _check_manager_permission()

    if not company or not frappe.db.exists("Company", company):
        frappe.throw(_("Company '{0}' not found.").format(company))

    doc = CompanyRepository.get_doc("Company", company)
    changed = False

    if company_name and company_name.strip():
        doc.company_name = company_name.strip()
        changed = True
    if gstin is not None:
        doc.gstin = (gstin.strip().upper() if str(gstin).strip() else "")
        changed = True
    if default_currency and default_currency.strip():
        doc.default_currency = default_currency.strip().upper()
        changed = True

    if changed:
        # reviewed-ignore-permissions: organization entity detail updates, gated by SMRITI Store Manager or System Manager roles
        doc.save(ignore_permissions=True)
        CompanyRepository.commit()

    return {"success": True, "message": _("Company updated successfully.")}


@frappe.whitelist()
def delete_company(company):
    """
    Delete a Company after verifying it has zero transactions.
    Blocks deletion if Sales Invoice, Purchase Invoice, GL Entry,
    or Stock Ledger Entry records exist to prevent data loss.
    Only System Manager / Administrator may delete.
    """
    _check_manager_permission()

    # Extra gate: only System Manager can delete companies
    if frappe.session.user != "Administrator":
        roles = set(frappe.get_roles(frappe.session.user))
        if "System Manager" not in roles:
            frappe.throw(
                _("Only System Managers can delete companies."),
                frappe.PermissionError
            )

    if not company or not frappe.db.exists("Company", company):
        frappe.throw(_("Company '{0}' not found.").format(company))

    # Safety: block if any transactions exist
    blockers = {}
    for doctype in ["Sales Invoice", "Purchase Invoice", "GL Entry", "Stock Ledger Entry"]:
        count = frappe.db.count(doctype, {"company": company})
        if count:
            blockers[doctype] = count

    if blockers:
        details = ", ".join([f"{dt}: {n} record(s)" for dt, n in blockers.items()])
        frappe.throw(
            _("Cannot delete '{0}'. Existing transactions found: {1}. "
              "Archive or manage via ERPNext Desk instead.").format(company, details)
        )

    # Clean up SMRITI Company Settings first
    settings_name = frappe.db.exists(_SETTINGS_DOCTYPE, {"company": company})
    if settings_name:
        # reviewed-ignore-permissions: organization entity deletion, gated by System Manager role
        CompanyRepository.delete_doc(_SETTINGS_DOCTYPE, settings_name, ignore_permissions=True)

    # reviewed-ignore-permissions: organization entity deletion, gated by System Manager role
    CompanyRepository.delete_doc("Company", company, ignore_permissions=True)
    CompanyRepository.commit()
    return {"success": True, "message": _("Company '{0}' deleted.").format(company)}


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


@frappe.whitelist()
def get_item_attributes(company=None):
    """
    Returns the list of standard and custom attributes sorted by SMRITI Attribute Layout weights.
    """
    if not company:
        company = get_active_company()
        
    # Standard attributes
    standard_attrs = [
        {"attribute_id": "COLOR", "label": "Color", "is_custom": 0},
        {"attribute_id": "SIZE", "label": "Size", "is_custom": 0},
        {"attribute_id": "PRODUCT STYLE CODE", "label": "Style/Article No", "is_custom": 0},
        {"attribute_id": "BRAND NAME", "label": "Brand", "is_custom": 0},
        {"attribute_id": "GENDER", "label": "Gender", "is_custom": 0},
        {"attribute_id": "DEPARTMENT", "label": "Department", "is_custom": 0},
        {"attribute_id": "PURCHASE CLASS", "label": "Purch. Class", "is_custom": 0},
        {"attribute_id": "MERCHANDISE CATEGORY", "label": "Merch. Cat.", "is_custom": 0},
        {"attribute_id": "Sub category", "label": "Sub Category", "is_custom": 0},
        {"attribute_id": "HEELS", "label": "Heels", "is_custom": 0},
        {"attribute_id": "UPPER MATERIAL", "label": "Upper Mat.", "is_custom": 0},
        {"attribute_id": "OUTSOLE", "label": "Outsole", "is_custom": 0}
    ]
    
    # Custom attributes from SMRITI Custom Attribute DocType
    custom_attrs = []
    if frappe.db.exists("DocType", "SMRITI Custom Attribute"):
        try:
            db_attrs = frappe.get_all(
                "SMRITI Custom Attribute",
                fields=["attribute_code", "attribute_name"]
            )
            for db_attr in db_attrs:
                custom_attrs.append({
                    "attribute_id": db_attr.attribute_code,
                    "label": db_attr.attribute_name,
                    "is_custom": 1
                })
        except Exception:
            pass
            
    all_attrs = standard_attrs + custom_attrs
    
    # Fetch weights from SMRITI Attribute Layout
    weights = {}
    if company:
        layout_entries = frappe.get_all(
            "SMRITI Attribute Layout",
            filters={"company": company},
            fields=["attribute_id", "weight"]
        )
        weights = {le.attribute_id: le.weight for le in layout_entries}
        
    # Sort them using the deterministic fallback sorting rule:
    # 1. Weighted attributes (by weight)
    # 2. Remaining/unweighted attributes (alphabetically by label)
    
    def sort_key(attr):
        attr_id = attr["attribute_id"]
        label = attr["label"]
        if attr_id in weights:
            # Category 1: Weighted attributes (by weight)
            return (0, weights[attr_id], label.lower())
        else:
            # Category 2: Remaining/unweighted attributes (alphabetically by label)
            return (1, 0, label.lower())
            
    all_attrs.sort(key=sort_key)
    
    # Include weight info in returned objects
    for attr in all_attrs:
        attr["weight"] = weights.get(attr["attribute_id"], None)
        
    return all_attrs


@frappe.whitelist()
def save_item_attributes(company=None, attributes=None):
    """
    Saves the custom attribute weights order for a company.
    Executes as a single atomic transaction. Rollback on any failure.
    """
    _check_manager_permission()
    
    if not company:
        company = get_active_company()
        
    if not company:
        frappe.throw(_("Company is required."))
        
    if isinstance(attributes, str):
        attributes = json.loads(attributes)
        
    if not isinstance(attributes, list):
        frappe.throw(_("Attributes must be a list of dicts/objects."))

    from smriti_retail_os.utils import get_client_ip
    ip_address = get_client_ip()

    try:
        # Step 1: Capture before_state
        existing_entries = frappe.get_all(
            "SMRITI Attribute Layout",
            filters={"company": company},
            fields=["attribute_id", "weight"],
            order_by="weight asc"
        )
        before_state = json.dumps(existing_entries)
        
        # Step 2: Delete existing weights for this company
        CompanyRepository.delete("SMRITI Attribute Layout", {"company": company})
        
        # Step 3: Insert new weights validating uniqueness
        seen_attributes = set()
        after_state_list = []
        
        for idx, attr in enumerate(attributes):
            attr_id = attr.get("attribute_id")
            weight = attr.get("weight")
            if weight is None:
                weight = idx + 1
                
            if not attr_id:
                continue
                
            if attr_id in seen_attributes:
                frappe.throw(
                    _("Duplicate attribute '{0}' detected in layout save request.").format(attr_id),
                    frappe.ValidationError
                )
            seen_attributes.add(attr_id)
            
            doc = CompanyRepository.new_doc("SMRITI Attribute Layout")
            doc.company = company
            doc.attribute_id = attr_id
            doc.weight = weight
            # reviewed-ignore-permissions: attribute layout updates, gated by SMRITI Store Manager or System Manager roles
            doc.insert(ignore_permissions=True)
            
            after_state_list.append({"attribute_id": attr_id, "weight": weight})
            
        after_state = json.dumps(after_state_list)
        
        # Step 4: Invalidate Redis cache key `smriti:item_attributes:{company}`
        cache_key = f"smriti:item_attributes:{company}"
        frappe.cache.delete_key(cache_key)
        
        # Step 5: Log audit event
        audit_doc = CompanyRepository.new_doc("SMRITI Audit Event")
        audit_doc.timestamp = frappe.utils.now_datetime()
        audit_doc.user = frappe.session.user
        audit_doc.event_type = "ATTRIBUTE_LAYOUT_CHANGED"
        audit_doc.before_state = before_state
        audit_doc.after_state = after_state
        audit_doc.company = company
        audit_doc.ip_address = ip_address
        # reviewed-ignore-permissions: attribute layout updates, gated by SMRITI Store Manager or System Manager roles
        audit_doc.insert(ignore_permissions=True)
        
        CompanyRepository.commit()
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Failed to save attribute layout", message=frappe.get_traceback())
        raise e
        
    return {"success": True, "message": _("Attribute layout saved successfully.")}


@frappe.whitelist()
def reset_item_attributes(company=None):
    """
    Resets (deletes) custom attribute order weights for a company.
    Executes as a single atomic transaction. Rollback on failure.
    """
    _check_manager_permission()
    
    if not company:
        company = get_active_company()
        
    if not company:
        frappe.throw(_("Company is required."))
        
    from smriti_retail_os.utils import get_client_ip
    ip_address = get_client_ip()
    
    try:
        # Capture before_state
        existing_entries = frappe.get_all(
            "SMRITI Attribute Layout",
            filters={"company": company},
            fields=["attribute_id", "weight"],
            order_by="weight asc"
        )
        before_state = json.dumps(existing_entries)
        
        # Delete entries
        CompanyRepository.delete("SMRITI Attribute Layout", {"company": company})
        
        # Invalidate Redis cache key `smriti:item_attributes:{company}`
        cache_key = f"smriti:item_attributes:{company}"
        frappe.cache.delete_key(cache_key)
        
        # Log audit event
        audit_doc = CompanyRepository.new_doc("SMRITI Audit Event")
        audit_doc.timestamp = frappe.utils.now_datetime()
        audit_doc.user = frappe.session.user
        audit_doc.event_type = "ATTRIBUTE_LAYOUT_RESET"
        audit_doc.before_state = before_state
        audit_doc.after_state = json.dumps([])
        audit_doc.company = company
        audit_doc.ip_address = ip_address
        # reviewed-ignore-permissions: attribute layout resetting, gated by SMRITI Store Manager or System Manager roles
        audit_doc.insert(ignore_permissions=True)
        
        CompanyRepository.commit()
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Failed to reset attribute layout", message=frappe.get_traceback())
        raise e
        
    return {"success": True, "message": _("Attribute layout reset successfully.")}

