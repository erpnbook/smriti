# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/license_api.py
# @description: SMRITI License Management API — license activation and status.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/api/license_api.py
# @description: SMRITI License API — whitelisted endpoints for the License UI page.
#               All operations go through this service layer (Rule 2 compliant).
#               No frontend code touches the DocType directly.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md
# @version: 1.8.6
#

import frappe
from frappe import _
from frappe.utils import now_datetime, cint


# ── Permission helper ─────────────────────────────────────────────────────────

def _require_license_admin():
    roles = set(frappe.get_roles(frappe.session.user))
    if not ({"SMRITI System Admin", "System Manager", "Administrator"} & roles):
        frappe.throw(_("Access restricted to SMRITI System Admin."), frappe.PermissionError)


# ── 1. Status & Summary ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_license_status():
    """
    Returns full license summary for the Overview tab.
    Includes real-time status from LicenseManager (§6a Trigger C).
    """
    from smriti_retail_os.license.manager import get_license_summary
    _require_license_admin()
    summary = get_license_summary()

    # Supplement with stored fields not in the summary
    try:
        doc = frappe.get_single("SMRITI License")
        summary["organization_name"]      = doc.organization_name or ""
        summary["store_name"]             = doc.store_name or ""
        summary["owner_name"]             = doc.owner_name or ""
        summary["gstin"]                  = doc.gstin or ""
        summary["license_type"]           = doc.license_type or ""
        summary["activation_date"]        = str(doc.activation_date) if doc.activation_date else ""
        summary["expiry_date"]            = str(doc.expiry_date) if doc.expiry_date else ""
        summary["grace_period_days"]      = cint(doc.grace_period_days) or 7
        summary["warning_threshold_days"] = cint(doc.warning_threshold_days) or 14
        summary["installation_id"]        = doc.installation_id or ""
        summary["customer_id"]            = doc.customer_id or ""
        summary["support_contract_status"]= doc.support_contract_status or ""
        summary["amc_status"]             = doc.amc_status or ""
        summary["last_sync"]              = str(doc.last_sync) if doc.last_sync else ""
        summary["registered_email"]       = doc.registered_email or ""
        summary["registered_mobile"]      = doc.registered_mobile or ""
        # license_key is a Password field — doc.license_key returns the ENCRYPTED hash.
        # license_key_suffix stores the last 4 plaintext chars at activation time.
        suffix = doc.license_key_suffix or ""
        summary["license_key_masked"] = (f"****-****-****-{suffix}") if suffix else ("****-****-****-****" if doc.license_key else "Not Set")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SMRITI: Exception in api/license_api.py")

    return summary


# ── 2. Activate ───────────────────────────────────────────────────────────────

@frappe.whitelist()
def activate_license(license_key, organization_name="", owner_name="",
                     registered_email="", registered_mobile="",
                     license_type="Starter"):
    """
    Activates (or re-activates) the SMRITI License.

    Phase-1 Offline Validation:
        If the key matches the SMRT-{v}-{payload}-{sig} format, the validator
        decodes the embedded payload (tier, expiry, customer_id, installation binding)
        and verifies the HMAC-SHA256 signature. The embedded metadata overrides the
        form fields (license_type, expiry_date, customer_id).

    Legacy / Development Mode:
        If the key does NOT match the SMRT format, it is accepted as-is with a
        1-year default expiry (backward-compatible with pre-validator keys and
        demo/development environments).

    Phase-2 (future): will add online PKI verification against ERPNBook License Server.
    """
    _require_license_admin()

    if not license_key:
        frappe.throw(_("License Key is required."))

    from frappe.utils import nowdate, add_years

    doc = frappe.get_single("SMRITI License")

    # ── Try structured key validation ─────────────────────────────────────────
    key_payload    = None
    sig_result     = "Not Checked"
    validation_msg = "Legacy key accepted (no structured validation)."

    try:
        from smriti_retail_os.license.key_validator import (
            parse_license_key,
            validate_installation_binding,
            LicenseKeyError,
        )

        key_payload = parse_license_key(license_key)
        validate_installation_binding(key_payload, doc.installation_id)

        # Key is valid — extract embedded metadata (overrides form fields)
        license_type = key_payload["tier"]
        expiry_date  = key_payload["exp"]
        customer_id  = key_payload.get("cid", "")
        sig_result   = "Valid"
        validation_msg = (
            f"Structured key validated. Tier: {license_type}, "
            f"Expiry: {expiry_date}, Customer: {customer_id}, "
            f"Binding: {key_payload.get('iid', '*')}"
        )

    except LicenseKeyError as e:
        frappe.throw(str(e))

    except ImportError:
        # key_validator module not available — accept key in legacy mode
        expiry_date = str(add_years(nowdate(), 1))
        customer_id = ""
        validation_msg = "Key validator module not available. Legacy mode."

    except Exception:
        # Unexpected error in validator — accept in legacy mode, log the error
        frappe.log_error(
            title="SMRITI License: Key Validation Error",
            message=frappe.get_traceback()
        )
        expiry_date = str(add_years(nowdate(), 1))
        customer_id = ""
        validation_msg = "Key validation encountered an error. Legacy mode fallback."
        sig_result = "Error"

    # ── If key doesn't match SMRT format at all, use legacy defaults ──────────
    if key_payload is None:
        expiry_date = str(add_years(nowdate(), 1))
        customer_id = ""

    # ── Apply to license document ─────────────────────────────────────────────
    doc.license_key             = license_key
    doc.license_key_suffix      = license_key[-4:] if len(license_key) >= 4 else license_key
    doc.license_type            = license_type
    doc.organization_name       = organization_name or doc.organization_name
    doc.owner_name              = owner_name or doc.owner_name
    doc.registered_email        = registered_email or doc.registered_email
    doc.registered_mobile       = registered_mobile or doc.registered_mobile
    doc.activation_date         = nowdate()
    doc.expiry_date             = expiry_date
    doc.last_license_validation = now_datetime()
    doc.tamper_detected         = 0
    doc.tamper_reason           = ""
    if customer_id:
        doc.customer_id = customer_id

    # _recalculate_license_state runs in validate() on save
    # reviewed-ignore-permissions: bypass for whitelisted api endpoint
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # ── Audit log ─────────────────────────────────────────────────────────────
    doc.reload()
    doc.append("activity_log", {
        "timestamp":    now_datetime(),
        "action":       "Activated",
        "performed_by": frappe.session.user,
        "result":       "Success",
        "remarks":      f"License activated. Type: {license_type}. Key: ****{license_key[-4:]}",
    })
    doc.append("validation_history", {
        "timestamp":              now_datetime(),
        "validation_type":        "Offline",
        "result":                 doc.license_status,
        "signature_check_result": sig_result,
        "remarks":                validation_msg,
    })
    # reviewed-ignore-permissions: bypass for whitelisted api endpoint
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "status":  doc.license_status,
        "health":  doc.license_health,
        "tier":    license_type,
        "expiry":  expiry_date,
    }


# ── 3. Sync from Company ──────────────────────────────────────────────────────

@frappe.whitelist()
def sync_from_company():
    """
    Syncs organization_name, gstin, owner_name from the default Company master.
    Architecture §3 — snapshot fields are synced via this action, not edited manually.
    """
    _require_license_admin()

    company_name = frappe.defaults.get_user_default("Company") or \
                   frappe.db.get_value("Company", {}, "name")
    if not company_name:
        frappe.throw(_("No default company found. Please set a default company first."))

    company = frappe.get_doc("Company", company_name)
    doc = frappe.get_single("SMRITI License")
    doc.organization_name = company.company_name
    doc.gstin = getattr(company, "gstin", "") or getattr(company, "tax_id", "") or ""
    doc.store_name = company.company_name

    # reviewed-ignore-permissions: bypass for whitelisted api endpoint
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    doc.reload()
    doc.append("activity_log", {
        "timestamp":    now_datetime(),
        "action":       "Synced",
        "performed_by": frappe.session.user,
        "result":       "Success",
        "remarks":      f"Synced from Company: {company_name}",
    })
    # reviewed-ignore-permissions: bypass for whitelisted api endpoint
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "organization_name": doc.organization_name, "gstin": doc.gstin}


# ── 4. Get Features ───────────────────────────────────────────────────────────

@frappe.whitelist()
def get_feature_entitlements():
    """Returns the full feature entitlements table for the Feature Entitlements tab."""
    _require_license_admin()
    doc = frappe.get_single("SMRITI License")
    return [
        {
            "feature_code":      f.feature_code,
            "feature_name":      f.feature_name,
            "enabled":           cint(f.enabled),
            "tier_minimum":      f.tier_minimum,
            "restriction_level": f.restriction_level,
        }
        for f in (doc.features or [])
    ]


# ── 5. Get Activity Log ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_activity_log(limit=50):
    """Returns last N activity log entries for the Activity Log tab."""
    _require_license_admin()
    doc = frappe.get_single("SMRITI License")
    entries = sorted(
        doc.activity_log or [],
        key=lambda x: x.timestamp or "",
        reverse=True
    )
    return [
        {
            "timestamp":    str(e.timestamp),
            "action":       e.action,
            "performed_by": e.performed_by,
            "result":       e.result,
            "remarks":      e.remarks,
        }
        for e in entries[:int(limit)]
    ]


# ── 6. Get Validation History ─────────────────────────────────────────────────

@frappe.whitelist()
def get_validation_history(limit=50):
    """Returns last N validation history entries for the Validation History tab."""
    _require_license_admin()
    doc = frappe.get_single("SMRITI License")
    entries = sorted(
        doc.validation_history or [],
        key=lambda x: x.timestamp or "",
        reverse=True
    )
    return [
        {
            "timestamp":              str(e.timestamp),
            "validation_type":        e.validation_type,
            "result":                 e.result,
            "signature_check_result": e.signature_check_result,
            "remarks":                e.remarks,
        }
        for e in entries[:int(limit)]
    ]


# ── 7. check_feature passthrough ──────────────────────────────────────────────

@frappe.whitelist()
def check_feature_access(feature_code):
    """
    Public API passthrough for check_feature().
    Allows frontend to query feature access without importing the manager directly.
    """
    from smriti_retail_os.license.manager import check_feature
    return check_feature(feature_code)


# ── 8. Generate Test Key (Admin-only utility) ─────────────────────────────────

@frappe.whitelist()
def generate_test_key(customer_id="CUST-DEMO-001", tier="Professional",
                      expiry_date=None, installation_id="*"):
    """
    Generates a signed SMRITI license key for testing/demo purposes.
    Restricted to Administrator only — never exposed to end users.
    """
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only Administrator can generate test keys."), frappe.PermissionError)

    if not expiry_date:
        from frappe.utils import add_days, nowdate
        expiry_date = add_days(nowdate(), 90)

    from smriti_retail_os.license.key_validator import generate_license_key
    key = generate_license_key(customer_id, tier, expiry_date, installation_id)
    return {"key": key, "tier": tier, "expiry": expiry_date, "customer_id": customer_id}

