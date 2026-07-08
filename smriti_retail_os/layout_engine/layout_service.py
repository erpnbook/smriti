"""
layout_service.py
-----------------
SMRITI Retail OS — Layout Engine
Server-side preference persistence for the SRLE Layout Engine.

Preferences are stored as a JSON blob on the Frappe User document
via the 'smriti_layout_prefs' custom field added by SMRITI setup.
Falls back gracefully to returning defaults if the field does not exist.

Copyright (c) 2026 AITDL NETWORK. All rights reserved.
"""

import json
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.layout_engine.layout_preferences import (
    validate_and_sanitise,
    defaults as default_prefs,
)

# Custom field name on frappe.User that stores the JSON blob
_PREFS_FIELD = "smriti_layout_prefs"


def _field_exists() -> bool:
    """Returns True if the custom field exists on the User doctype."""
    try:
        return smriti.db.exists(
            "Custom Field",
            {"dt": "User", "fieldname": _PREFS_FIELD}
        )
    except Exception:
        return False


@frappe.whitelist()
def get_layout_preferences() -> dict:
    """
    Returns the saved layout preferences for the current logged-in user.
    Falls back to validated defaults if no preferences are saved or if the
    custom field does not exist.

    API endpoint: smriti_retail_os.layout_engine.layout_service.get_layout_preferences
    """
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            return default_prefs()

        if not _field_exists():
            return default_prefs()

        raw_json = smriti.db.get("User", user, _PREFS_FIELD) or ""
        if not raw_json:
            return default_prefs()

        raw = json.loads(raw_json)
        return validate_and_sanitise(raw)

    except Exception:
        smriti.errors.log_error(frappe.get_traceback(), "SRLE.get_layout_preferences")
        return default_prefs()


@frappe.whitelist()
def save_layout_preferences(prefs: str) -> dict:
    """
    Persists layout preferences for the current logged-in user.

    Args:
        prefs: JSON string of raw preference values.

    Returns:
        The validated, sanitised preferences that were actually stored.

    API endpoint: smriti_retail_os.layout_engine.layout_service.save_layout_preferences
    """
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            return {"status": "skipped", "reason": "guest session"}

        if not _field_exists():
            # Field not yet created — silently succeed, localStorage will hold state
            return {"status": "skipped", "reason": "field_not_configured"}

        raw = json.loads(prefs) if isinstance(prefs, str) else prefs
        clean = validate_and_sanitise(raw)

        smriti.db.set_value(
            "User", user, _PREFS_FIELD, json.dumps(clean),
            update_modified=False
        )
        smriti.db.commit()

        return {"status": "saved", "prefs": clean}

    except Exception:
        smriti.errors.log_error(frappe.get_traceback(), "SRLE.save_layout_preferences")
        return {"status": "error", "reason": "An error occurred saving your layout preferences."}
