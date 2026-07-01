# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/manager.py
# @description: SMRITI LicenseManager — central authority for all feature gating.
#               The ONLY place in the codebase allowed to read license_status directly.
#               All other modules MUST call check_feature() from here.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md §7
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import getdate, date_diff, now_datetime, get_datetime, nowdate, cint




# Sentinel returned when the license record fails to load due to an infrastructure
# error (DB unavailable, PermissionError, corrupt doc). Distinct from None, which
# means "not yet installed" (pre-migration). check_feature() treats LOAD_ERROR as
# blocked to prevent accidental feature unlocking during outages.
_LICENSE_LOAD_ERROR = "LOAD_ERROR"


def _load_license():
    """
    Loads the SMRITI License Single DocType.
    Cached for the duration of the current request (frappe.local scope).

    Returns:
        Document  — the loaded license doc (normal case)
        None      — DocType not yet installed (pre-migration: allow all features)
        "LOAD_ERROR" sentinel — infrastructure failure (fail-closed: block all)
    """
    if hasattr(frappe.local, "_smriti_license_cache"):
        return frappe.local._smriti_license_cache

    try:
        doc = frappe.get_cached_doc("SMRITI License")
        frappe.local._smriti_license_cache = doc
        return doc
    except frappe.DoesNotExistError:
        # DocType not yet created — genuine pre-migration state.
        # Allow all features through so fresh installs work before setup.
        frappe.local._smriti_license_cache = None
        return None
    except Exception:
        # Infrastructure failure: DB hiccup, PermissionError, corrupt doc.
        # Fail CLOSED — do not silently unlock all licensed features.
        frappe.log_error(
            title="SMRITI License: Failed to load license record",
            message=(
                "License could not be loaded due to an infrastructure error.\n"
                "All licensed features will be blocked until this is resolved.\n\n"
                + frappe.get_traceback()
            ),
        )
        frappe.local._smriti_license_cache = _LICENSE_LOAD_ERROR
        return _LICENSE_LOAD_ERROR


def _evaluate_status_lightweight(doc):
    """
    Lightweight date comparison — runs inside check_feature() without DB write.
    Architecture §6a trigger C: guarantees real-time enforcement.
    Returns (status, health, days_remaining).
    """
    today = getdate(nowdate())

    # Priority 0 — Unregistered
    if not doc.license_key:
        return "Unregistered", "Unregistered", None

    # Priority 1 — Tampered
    if doc.tamper_detected:
        return "Tampered", "Tampered", 0

    # Priority 2 — Suspended (persists)
    if doc.license_status == "Suspended":
        return "Suspended", "Suspended", 0

    grace_days = cint(doc.grace_period_days) or 7
    warn_days  = cint(doc.warning_threshold_days) or 14
    days_remaining = None

    if doc.expiry_date:
        expiry = getdate(doc.expiry_date)
        days_remaining = date_diff(expiry, today)

        # Priority 3 — Expired
        if days_remaining < -grace_days:
            return "Expired", "Expired", days_remaining

        # Priority 4 — Grace Period (expiry breach)
        if days_remaining < 0:
            return "Grace Period", "Grace Period", days_remaining

    # Priority 5 — Grace Period (offline too long)
    if doc.last_sync and grace_days:
        offline_days = date_diff(now_datetime(), get_datetime(doc.last_sync))
        if offline_days > grace_days:
            return "Grace Period", "Grace Period", days_remaining

    # Priority 7 — Active
    if days_remaining is not None and days_remaining <= warn_days:
        return "Active", "Warning", days_remaining
    return "Active", "Healthy", days_remaining


def check_feature(feature_code: str) -> dict:
    """
    Single source of truth for feature gating.
    Architecture §7 — the ONLY function allowed to gate features.

    Returns:
        allowed: bool        — can the user proceed?
        mode: str            — "none" | "read_only" | "blocked"
        reason: str | None   — human-readable explanation for UI display
        status: str          — current license_status (for UI badge rendering)
        days_remaining: int  — days until expiry (-N if expired, None if Unregistered)
    """
    doc = _load_license()

    # Pre-migration — DocType not yet installed. Allow all features.
    if doc is None:
        return {
            "allowed": True,
            "mode": "none",
            "reason": None,
            "status": "Active",
            "days_remaining": None,
        }

    # Infrastructure failure loading license record — fail CLOSED.
    # This prevents an unrelated DB error from silently unlocking all features.
    if doc is _LICENSE_LOAD_ERROR:
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": (
                "License system is temporarily unavailable due to an infrastructure error. "
                "Please contact support@erpnbook.com if this persists."
            ),
            "status": "Error",
            "days_remaining": None,
        }

    # §6a Trigger C: lightweight real-time evaluation
    status, health, days_remaining = _evaluate_status_lightweight(doc)

    # System-wide locks — no per-feature logic applies
    if status == "Unregistered":
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": "License not registered. Please activate SMRITI at Settings → License & Registration.",
            "status": status,
            "days_remaining": None,
        }

    if status == "Tampered":
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": "License integrity violation detected. Contact SMRITI Support immediately.",
            "status": status,
            "days_remaining": 0,
        }

    if status == "Suspended":
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": "License suspended. Contact SMRITI Support to restore access.",
            "status": status,
            "days_remaining": 0,
        }

    if status == "Expired":
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": f"License expired. Please renew at Settings → License & Registration.",
            "status": status,
            "days_remaining": days_remaining,
        }

    # Grace Period — per-feature restriction_level applies
    if status == "Grace Period":
        restriction = _get_feature_restriction(doc, feature_code)
        if restriction == "BLOCKED":
            return {
                "allowed": False,
                "mode": "blocked",
                "reason": f"{feature_code} is blocked during grace period. Renew license to restore.",
                "status": status,
                "days_remaining": days_remaining,
            }
        if restriction == "READ_ONLY":
            return {
                "allowed": True,
                "mode": "read_only",
                "reason": f"{feature_code} is in read-only mode. License renewal required for full access.",
                "status": status,
                "days_remaining": days_remaining,
            }
        return {
            "allowed": True,
            "mode": "none",
            "reason": None,
            "status": status,
            "days_remaining": days_remaining,
        }

    # Active (Healthy or Warning) — check tier entitlement
    if not _feature_enabled_for_tier(doc, feature_code):
        return {
            "allowed": False,
            "mode": "blocked",
            "reason": f"{feature_code} is not included in your current plan ({doc.license_type or 'Starter'}). Upgrade to unlock.",
            "status": status,
            "days_remaining": days_remaining,
        }

    return {
        "allowed": True,
        "mode": "none",
        "reason": None,
        "status": status,
        "days_remaining": days_remaining,
    }


def get_license_summary() -> dict:
    """
    Returns a lightweight summary for boot.py injection.
    Used by frontend to render license badges without extra API calls.
    """
    doc = _load_license()
    if doc is None:
        return {"status": "Active", "health": "Healthy", "days_remaining": None, "features": []}
    if doc is _LICENSE_LOAD_ERROR:
        # Infrastructure failure — surface Error state to the frontend badge.
        return {"status": "Error", "health": "Error", "days_remaining": None, "features": []}

    status, health, days_remaining = _evaluate_status_lightweight(doc)
    features = [
        {"code": f.feature_code, "enabled": f.enabled, "restriction": f.restriction_level}
        for f in (doc.features or [])
    ]
    return {
        "status": status,
        "health": health,
        "days_remaining": days_remaining,
        "license_type": doc.license_type or "Starter",
        "organization_name": doc.organization_name or "",
        "expiry_date": str(doc.expiry_date) if doc.expiry_date else None,
        "features": features,
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_feature_restriction(doc, feature_code: str) -> str:
    """Returns restriction_level for a feature during Grace Period."""
    for f in (doc.features or []):
        if f.feature_code == feature_code:
            return f.restriction_level or "NONE"
    # Unknown feature code — log so typos become visible. Default: unrestricted.
    frappe.log_error(
        title=f"SMRITI License: Unknown feature code in grace check — '{feature_code}'",
        message=(
            f"_get_feature_restriction() was called with feature_code='{feature_code}' "
            f"which is not registered in the SMRITI License features table. "
            f"Defaulting to NONE (unrestricted). Register this code to enforce grace-period gating."
        ),
    )
    return "NONE"  # Deliberate forward-compat default — see Finding #5 in audit


def _feature_enabled_for_tier(doc, feature_code: str) -> bool:
    """Returns True if the feature is enabled and within the current plan tier."""
    TIER_ORDER = {"Starter": 0, "Professional": 1, "Enterprise": 2}
    current_tier = TIER_ORDER.get(doc.license_type or "Starter", 0)

    for f in (doc.features or []):
        if f.feature_code == feature_code:
            if not f.enabled:
                return False
            required_tier = TIER_ORDER.get(f.tier_minimum or "Starter", 0)
            return current_tier >= required_tier

    # Unknown feature code — log so typos become visible. Default: allowed.
    # Deliberate forward-compat choice: new features can be deployed before
    # their license registry entry is seeded. See audit Finding #5.
    frappe.log_error(
        title=f"SMRITI License: Unknown feature code in tier check — '{feature_code}'",
        message=(
            f"_feature_enabled_for_tier() was called with feature_code='{feature_code}' "
            f"which is not registered in the SMRITI License features table. "
            f"Defaulting to allowed (True). Register this code in the license DocType "
            f"to enforce per-tier gating."
        ),
    )
    return True  # Deliberate forward-compat default — see Finding #5 in audit
