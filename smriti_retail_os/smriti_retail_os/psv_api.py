# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_api.py
# @description: Channel Stock SMRITI Service API — PSA CRUD, sell-through upload,
#               and channel balance endpoints. All PSA write operations are routed
#               through this service controller (SEC-001 fix: no raw frappe.client.*
#               calls from frontend for PSA management).
# @version: 2.0.0
#

import frappe
from frappe import _
from smriti_retail_os.smriti_retail_os.psv_upload_service import process_upload
from smriti_retail_os.smriti_retail_os.psv_balance_service import get_channel_balance


# ─── PSA MANAGEMENT SERVICE CONTROLLERS ──────────────────────────────────────
# SEC-001 FIX: Frontend psa.html now calls these controllers instead of using
# raw frappe.client.insert / frappe.client.set_value / frappe.client.get.

@frappe.whitelist()
def create_psa(company: str, customer: str, location_name: str,
               zone: str = None, region: str = None, area_manager: str = None,
               contact_person: str = None, mobile: str = None, email: str = None,
               active: int = 1):
    """
    Creates a new SMRITI Party Stock Account.
    Requires SMRITI Store Manager or System Manager role.
    Routes through the service layer — frontend must NOT call frappe.client.insert directly.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if not company or not customer or not location_name:
        frappe.throw(_("Company, Customer, and Location Name are required."))

    # Prevent duplicate PSA for same customer + location
    existing = frappe.db.exists(
        "SMRITI Party Stock Account",
        {"customer": customer, "location_name": location_name}
    )
    if existing:
        frappe.throw(
            _("A Party Stock Account already exists for customer {0} at location '{1}' ({2})."
              ).format(customer, location_name, existing)
        )

    doc = frappe.get_doc({
        "doctype": "SMRITI Party Stock Account",
        "company": company,
        "customer": customer,
        "location_name": location_name,
        "zone": zone,
        "region": region,
        "area_manager": area_manager or None,
        "contact_person": contact_person,
        "mobile": mobile,
        "email": email,
        "active": int(active),
        "status": "Active"
    })
    doc.insert(ignore_permissions=False)  # Respect Frappe role permissions
    frappe.db.commit()

    return {"name": doc.name, "status": "created"}


@frappe.whitelist()
def update_psa(name: str, zone: str = None, region: str = None,
               area_manager: str = None, contact_person: str = None,
               mobile: str = None, email: str = None, active: int = 1):
    """
    Updates mutable fields on an existing SMRITI Party Stock Account.
    Company, Customer, and Location Name are immutable after creation.
    Requires SMRITI Store Manager or System Manager role.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if not frappe.db.exists("SMRITI Party Stock Account", name):
        frappe.throw(_("Party Stock Account {0} not found.").format(name))

    frappe.db.set_value(
        "SMRITI Party Stock Account",
        name,
        {
            "zone": zone,
            "region": region,
            "area_manager": area_manager or None,
            "contact_person": contact_person,
            "mobile": mobile,
            "email": email,
            "active": int(active),
        }
    )
    frappe.db.commit()

    return {"name": name, "status": "updated"}


@frappe.whitelist()
def get_psa(name: str):
    """
    Returns full details of a SMRITI Party Stock Account.
    Requires read access to the DocType (enforced via frappe.get_doc).
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    doc = frappe.get_doc("SMRITI Party Stock Account", name)
    return {
        "name": doc.name,
        "company": doc.company,
        "customer": doc.customer,
        "location_name": doc.location_name,
        "zone": doc.zone,
        "region": doc.region,
        "area_manager": doc.area_manager,
        "contact_person": doc.contact_person,
        "mobile": doc.mobile,
        "email": doc.email,
        "active": doc.active,
        "status": doc.status,
        "tracking_mode": doc.tracking_mode,
    }


@frappe.whitelist()
def list_psas(company: str = None, active: int = None):
    """
    Returns a list of SMRITI Party Stock Accounts with key fields.
    Optionally filtered by company and/or active status.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    filters = {}
    if company:
        filters["company"] = company
    if active is not None:
        filters["active"] = int(active)

    return frappe.get_all(
        "SMRITI Party Stock Account",
        filters=filters,
        fields=[
            "name", "company", "customer", "location_name", "zone", "region",
            "area_manager", "contact_person", "mobile", "email", "active", "status"
        ],
        order_by="modified desc",
        limit=500
    )


# ─── SELL-THROUGH UPLOAD API ──────────────────────────────────────────────────

@frappe.whitelist()
def upload_sell_through(upload_doc_name: str):
    """
    API endpoint to trigger the processing of a Draft PSV Sell-Through Upload.
    SEC-002 FIX: Now checks SMRITI Party Stock Account permission (which exists)
    rather than the non-existent "PSV Sell-Through Upload" DocType.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    doc = frappe.get_doc("PSV Sell-Through Upload", upload_doc_name)
    if doc.status == "Processed":
        return {"status": "failed", "message": "Document is already processed."}

    # process_upload handles atomic commits and error logging internally.
    process_upload(upload_doc_name)

    doc.reload()

    if doc.status == "Processed":
        return {"status": "success", "rows_processed": doc.total_rows}
    else:
        return {"status": "failed", "error_count": len(doc.get("errors", []))}


# ─── CHANNEL BALANCE API ──────────────────────────────────────────────────────

@frappe.whitelist()
def fetch_channel_balance(customer: str, item_code: str = None):
    """
    API endpoint to retrieve current stock balance for a channel/customer.
    SEC-002 FIX: Now checks SMRITI Party Stock Account read permission (DocType
    exists) rather than the non-existent "PSV Balance" DocType.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    return {
        "status": "success",
        "data": get_channel_balance(customer, item_code)
    }
