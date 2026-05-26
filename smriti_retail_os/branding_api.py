"""
SMRITI Retail OS — Branding API
Server-side overrides for Frappe whitelisted methods that would otherwise
expose ERPNext/Frappe branding in the About dialog and version endpoints.
"""

import frappe

# Title overrides for About dialog
_TITLE_MAP = {
    "erpnext":             "SMRITI Retail OS",
    "frappe":              "SMRITI Framework",
    "frappe framework":    "SMRITI Framework",
    "india_compliance":    "India Compliance",
    "smriti_retail_os":   "SMRITI Retail OS",
    "hrms":                "SMRITI HR",
    "payments":            "SMRITI Payments",
}

_DESCRIPTION_MAP = {
    "erpnext":           "Smarter Retail. Built for India.",
    "frappe":            "The application framework powering SMRITI.",
    "smriti_retail_os":  "Smarter Retail. Built for India.",
}


@frappe.whitelist()
def get_versions():
    """
    Override of frappe.utils.change_log.get_versions.
    Returns version info with all ERPNext / Frappe titles replaced by
    SMRITI branding — used by Help → About dialog.
    """
    from frappe.utils.change_log import get_versions as _original_get_versions

    try:
        versions = _original_get_versions() or {}
    except Exception:
        versions = {}

    # Patch titles and descriptions
    for app_name, info in versions.items():
        if not isinstance(info, dict):
            continue
        key = app_name.lower()
        if key in _TITLE_MAP:
            info["title"] = _TITLE_MAP[key]
        if key in _DESCRIPTION_MAP:
            info["description"] = _DESCRIPTION_MAP[key]
        # Strip any remaining ERPNext / Frappe references from title
        title = info.get("title", "")
        if "ERPNext" in title:
            info["title"] = title.replace("ERPNext", "SMRITI Retail OS")
        if "Frappe" in title and key not in ("frappe", "smriti_retail_os"):
            info["title"] = title.replace("Frappe", "SMRITI")

    return versions
