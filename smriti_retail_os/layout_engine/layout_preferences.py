"""
layout_preferences.py
---------------------
SMRITI Retail OS — Layout Engine
Validates and sanitises raw layout preference dicts before persistence.

Copyright (c) 2026 AITDL NETWORK. All rights reserved.
"""

VALID_POSITIONS = {"left", "right", "top", "bottom"}
SIDEBAR_WIDTH_MIN = 180
SIDEBAR_WIDTH_MAX = 480


def validate_and_sanitise(raw: dict) -> dict:
    """
    Accepts a raw preference dict (from localStorage sync or API call),
    validates each field, and returns a clean, safe version.

    Unknown keys are dropped. Missing keys fall back to defaults.
    """
    prefs = {}

    # --- dock position ---
    pos = raw.get("position", "left")
    prefs["position"] = pos if pos in VALID_POSITIONS else "left"

    # --- collapsed state ---
    collapsed = raw.get("collapsed", False)
    prefs["collapsed"] = bool(collapsed)

    # --- icon-only mode ---
    icon_only = raw.get("icon_only", False)
    prefs["icon_only"] = bool(icon_only)

    # --- sidebar width (pixels as int) ---
    try:
        width = int(raw.get("sidebar_width", 260))
    except (TypeError, ValueError):
        width = 260
    prefs["sidebar_width"] = max(SIDEBAR_WIDTH_MIN, min(SIDEBAR_WIDTH_MAX, width))

    # --- last active workspace id ---
    workspace = raw.get("last_workspace", "")
    prefs["last_workspace"] = str(workspace)[:128] if workspace else ""

    # --- collapsed group ids (list of strings) ---
    groups = raw.get("collapsed_groups", [])
    if not isinstance(groups, list):
        groups = []
    prefs["collapsed_groups"] = [str(g)[:64] for g in groups if g][:50]  # cap at 50 groups

    # --- favorites (list of url strings) ---
    favs = raw.get("favorites", [])
    if not isinstance(favs, list):
        favs = []
    prefs["favorites"] = [str(f)[:256] for f in favs if f][:20]  # cap at 20 favorites

    return prefs


def defaults() -> dict:
    """Returns a clean default preference set."""
    return validate_and_sanitise({})
