# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/key_validator.py
# @description: SMRITI License Key Validator — HMAC-SHA256 key generation and validation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/license/key_validator.py
# @description: SMRITI License Key Validator — Phase-1 Offline Validation.
#
#   Key Format:
#       SMRT-{VERSION}-{PAYLOAD_B64URL}-{SIG_HEX16}
#
#   PAYLOAD_B64URL = base64url(JSON({
#       "cid":  "<customer_id>",          # ERPNBook customer identifier
#       "tier": "Starter|Professional|Enterprise",
#       "exp":  "YYYY-MM-DD",             # license expiry date
#       "iid":  "<installation_id>|*",    # '*' = any installation (floating)
#       "iss":  "ERPNBOOK"                # issuer tag
#   }))
#
#   SIG_HEX16 = first 16 hex chars of:
#       HMAC-SHA256(SMRITI_LICENSE_SECRET, "SMRT|{VERSION}|{PAYLOAD_B64URL}")
#
#   SMRITI_LICENSE_SECRET is sourced from (in order):
#       1. frappe.conf.smriti_license_secret     (production — set in site_config.json)
#       2. SMRITI_LICENSE_SECRET env variable     (CI / container override)
#       3. _FALLBACK_SECRET                       (development / demo environments only)
#
#   Generating keys (ERPNBook authority side):
#       from smriti_retail_os.license.key_validator import generate_license_key
#       key = generate_license_key("CUST-001", "Professional", "2027-06-17")
#
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md §5
# @version: 1.8.6
#

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
from datetime import date
from typing import TypedDict

import frappe
from frappe import _

# ── Constants ─────────────────────────────────────────────────────────────────

KEY_VERSION  = "1"
KEY_PREFIX   = "SMRT"
VALID_TIERS  = frozenset({"Starter", "Professional", "Enterprise"})
ISSUER_TAG   = "ERPNBOOK"

# Fallback secret — used ONLY when frappe.conf has no smriti_license_secret.
# This allows development/demo activations with the well-known test key.
# NEVER use this in production without setting the real secret in site_config.json.
_FALLBACK_SECRET = "SMRITI-DEV-SECRET-DO-NOT-USE-IN-PRODUCTION"

_KEY_PATTERN = re.compile(
    r"^SMRT-(?P<version>\d+)-(?P<payload>[A-Za-z0-9_\-]+={0,2})-(?P<sig>[0-9a-f]{16})$"
)


# ── Internal helpers ──────────────────────────────────────────────────────────

class LicensePayload(TypedDict):
    cid:  str
    tier: str
    exp:  str   # YYYY-MM-DD
    iid:  str   # installation_id or '*'
    iss:  str


def _get_secret() -> bytes:
    """
    Returns the HMAC signing secret for license key validation.

    Priority order:
      1. frappe.conf.smriti_license_secret  (site_config.json — production)
      2. SMRITI_LICENSE_SECRET env var       (CI / container override)
      3. developer_mode=1 only — fallback to _FALLBACK_SECRET with WARNING logged
         every call so no production instance can silently use the dev key.

    Raises:
        frappe.ValidationError: In non-developer-mode when no secret is configured.
    """
    # 1. site_config.json
    secret = getattr(frappe.conf, "smriti_license_secret", None)
    if secret:
        return secret.encode("utf-8")

    # 2. Environment variable (CI / container)
    secret = os.environ.get("SMRITI_LICENSE_SECRET")
    if secret:
        return secret.encode("utf-8")

    # 3. Fail-closed in production — throw if developer_mode is not set
    if not getattr(frappe.conf, "developer_mode", 0):
        frappe.throw(
            _(
                "SMRITI License: smriti_license_secret is not configured. "
                "Set smriti_license_secret in site_config.json or the "
                "SMRITI_LICENSE_SECRET environment variable before activating "
                "a license key. Contact support@erpnbook.com for assistance."
            ),
            title=_("License Configuration Error"),
        )

    # 4. developer_mode only — fallback with WARNING logged on every call
    frappe.log_error(
        title="SMRITI License: Using Development Secret [WARNING]",
        message=(
            "developer_mode=1 and no smriti_license_secret is configured. "
            "Using fallback development secret. This WARNING is logged on "
            "EVERY validation call. Set smriti_license_secret in "
            "site_config.json before going to production."
        ),
    )
    return _FALLBACK_SECRET.encode("utf-8")


def _compute_sig(version: str, payload_b64: str) -> str:
    """Returns the full HMAC-SHA256 hex digest for the key material."""
    secret  = _get_secret()
    message = f"{KEY_PREFIX}|{version}|{payload_b64}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _b64url_encode(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8").rstrip("=")


def _b64url_decode(token: str) -> dict:
    # Add padding
    padding = 4 - len(token) % 4
    if padding < 4:
        token += "=" * padding
    raw = base64.urlsafe_b64decode(token)
    return json.loads(raw.decode("utf-8"))


# ── Public API ────────────────────────────────────────────────────────────────

class LicenseKeyError(Exception):
    """Raised when a license key fails validation."""
    pass


def parse_license_key(key: str) -> LicensePayload:
    """
    Parses and validates a SMRITI license key.

    Returns the decoded payload dict on success.
    Raises LicenseKeyError with a user-facing message on failure.

    Does NOT check installation_id binding here — the caller (license_api) handles
    that so the error message can be more specific.
    """
    if not key or not isinstance(key, str):
        raise LicenseKeyError(_("License key is required."))

    key = key.strip()

    m = _KEY_PATTERN.match(key)
    if not m:
        raise LicenseKeyError(
            _("Invalid license key format. Expected: SMRT-1-<payload>-<signature>")
        )

    version     = m.group("version")
    payload_b64 = m.group("payload")
    sig_short   = m.group("sig")

    # ── Signature check ───────────────────────────────────────────────────────
    expected_full = _compute_sig(version, payload_b64)
    expected_short = expected_full[:16]

    if not hmac.compare_digest(sig_short, expected_short):
        raise LicenseKeyError(
            _("License key signature is invalid. The key may have been tampered with "
              "or generated for a different licensing authority.")
        )

    # ── Decode payload ────────────────────────────────────────────────────────
    try:
        payload = _b64url_decode(payload_b64)
    except Exception:
        raise LicenseKeyError(_("License key payload is malformed (base64 decode failed)."))

    # ── Validate required fields ──────────────────────────────────────────────
    for field in ("cid", "tier", "exp", "iid", "iss"):
        if field not in payload:
            raise LicenseKeyError(
                _("License key is missing required field: {0}.").format(field)
            )

    if payload.get("iss") != ISSUER_TAG:
        raise LicenseKeyError(
            _("License key issuer is not recognized. Expected: {0}.").format(ISSUER_TAG)
        )

    if payload.get("tier") not in VALID_TIERS:
        raise LicenseKeyError(
            _("License key contains unknown tier: {0}. Valid values: {1}.").format(
                payload.get("tier"), ", ".join(sorted(VALID_TIERS))
            )
        )

    # ── Expiry date format check ───────────────────────────────────────────────
    try:
        exp_date = date.fromisoformat(payload["exp"])
    except (ValueError, KeyError):
        raise LicenseKeyError(
            _("License key expiry date is invalid. Expected YYYY-MM-DD format.")
        )

    if exp_date < date.today():
        raise LicenseKeyError(
            _("This license key expired on {0}. Please contact support@erpnbook.com "
              "for a renewal key.").format(payload["exp"])
        )

    return payload


def validate_installation_binding(payload: LicensePayload, installation_id: str) -> None:
    """
    Checks that the key is bound to this installation (or is a floating '*' key).
    Raises LicenseKeyError if the key is bound to a different installation.
    """
    bound_iid = payload.get("iid", "*")
    if bound_iid == "*":
        return  # floating key — valid for any installation

    if not installation_id:
        return  # installation_id not yet generated — first install

    if bound_iid != installation_id:
        raise LicenseKeyError(
            _("This license key is bound to a different installation "
              "(ID: ****{0}). Contact support@erpnbook.com if you need "
              "to transfer the license.").format(bound_iid[-6:])
        )


# ── Key Generator (ERPNBook authority tool) ───────────────────────────────────

def generate_license_key(
    customer_id: str,
    tier: str,
    expiry_date: str,
    installation_id: str = "*",
) -> str:
    """
    Generates a signed SMRITI license key.

    This function is used by the ERPNBook licensing authority (not by the end-user
    application) to produce keys for distribution to customers.

    Args:
        customer_id:      ERPNBook customer identifier (e.g. "CUST-001")
        tier:             License tier — "Starter", "Professional", or "Enterprise"
        expiry_date:      Expiry date as "YYYY-MM-DD"
        installation_id:  Specific installation UUID to bind the key to,
                          or "*" for a floating key (default).

    Returns:
        A signed license key string in SMRT-{version}-{payload}-{sig} format.

    Example:
        key = generate_license_key("CUST-001", "Professional", "2027-06-17")
        # → "SMRT-1-eyJjaWQiOiJDVVNULTAwMSIsImV4cCI6IjIwMjctMDYtMTciLCJpaWQiOiIqIiwiaXNzIjoiRVJQTkJPT0siLCJ0aWVyIjoiUHJvZmVzc2lvbmFsIn0-a1b2c3d4e5f6a7b8"
    """
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier: {tier!r}. Must be one of {VALID_TIERS}")

    payload = {
        "cid":  customer_id,
        "exp":  expiry_date,
        "iid":  installation_id,
        "iss":  ISSUER_TAG,
        "tier": tier,
    }
    payload_b64 = _b64url_encode(payload)
    sig_full    = _compute_sig(KEY_VERSION, payload_b64)
    sig_short   = sig_full[:16]

    return f"{KEY_PREFIX}-{KEY_VERSION}-{payload_b64}-{sig_short}"
