# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/boot.py
# @description: SMRITI Retail OS boot hooks — session creation, desk access
#               guard, setup-wizard interception, and backup download protection.
#
# ═══════════════════════════════════════════════════════════════════
# SMRITI ARCHITECTURE POLICY — LOCKED — DO NOT OVERRIDE
# ═══════════════════════════════════════════════════════════════════
# Rule 7: Every page/module exposed to users MUST be a SMRITI page.
#
# TRIGGER RULE (added 2026-06-10):
#   If a browser shows /desk/setup-wizard, /desk/modules, /app, or ANY
#   Frappe/ERPNext native UI after login, that is a POLICY VIOLATION.
#   Correct action: intercept at before_request and redirect to /smriti.
#   NEVER expose Frappe Desk, ERPNext forms, or setup-wizard to users.
#   ALWAYS create a dedicated SMRITI page instead.
#
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-10
# @version: 1.8.2a
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# TODO: [Jawahar] Verify POS printer connection on startup
import frappe
import fnmatch
import werkzeug.routing.exceptions
from frappe import _
from smriti_retail_os.security_constants import PROTECTED_CONFIG_PATTERNS

# ── Role → SMRITI Route mapping ───────────────────────────────────
SMRITI_ROLE_ROUTES = {
    "System Manager":          "/smriti",
    "SMRITI Store Manager":    "/smriti",
    "SMRITI Inventory User":   "/inventory",
    "SMRITI Reports User":     "/reports",
    "SMRITI Cashier":          "/billing",
}

# ── Roles allowed to access /desk ────────────────────────────────
# Note: "Administrator" is a USER not a role in Frappe
# We check both role AND user for safety
DESK_ALLOWED_ROLES = {"System Manager"}
DESK_ALLOWED_USERS = {"Administrator"}

# ── SMRITI Policy: Frappe-native paths ALWAYS blocked from users ──
# These paths are NEVER shown to any user, regardless of role.
# Any match → immediate redirect to /smriti.
# Rule: if it appears post-login, create a SMRITI page instead.
SMRITI_BLOCKED_DESK_PATHS = [
    "/desk/setup-wizard",   # Frappe setup wizard — ALWAYS blocked
    "/desk/modules",        # Frappe module list
    "/desk#modules",        # Hash-based module route
    "/desk#Form",           # Direct form access
    "/desk#List",           # Direct list access
    "/desk#query-report",   # Direct report access
    "/desk#setup-wizard",   # Hash-based setup wizard
    # ── SMRITI Desk Pages — blocked: use www routes instead ──────────
    # These Frappe Desk pages (/desk/smriti-*) must NEVER reach users.
    # Canonical user routes are www pages: /customers, /suppliers, etc.
    "/desk/smriti-",        # ALL /desk/smriti-* pages (prefix match)
]

# ── Role priority for redirect ────────────────────────────────────
ROLE_PRIORITY = [
    "System Manager",
    "SMRITI Store Manager",
    "SMRITI Inventory User",
    "SMRITI Reports User",
    "SMRITI Cashier",
]


def extend_bootinfo(bootinfo):
    """
    Frappe v16 correct hook: extend_bootinfo
    Called after standard bootinfo is built.
    Injects SMRITI config into every page load.
    """
    # ALWAYS set setup_complete = 1 first, unconditionally, so client-side
    # SPA never redirects to /desk/setup-wizard regardless of any errors below.
    bootinfo.setup_complete = 1

    try:
        user        = frappe.session.user
        user_roles  = frappe.get_roles(user)
        desk_ok     = _is_desk_allowed(user, user_roles)
        smriti_route = _get_smriti_route(user_roles)

        bootinfo.smriti = frappe._dict({
            "app_name":      "SMRITI Retail OS",
            "app_version":   "1.0.0",
            "logo_url":      "/assets/smriti_retail_os/images/smriti_logo.svg",
            "user_roles":    user_roles,
            "default_route": smriti_route,
            "desk_allowed":  desk_ok,
            "company":       frappe.defaults.get_user_default("Company") or "",
            "frontend_enabled": _is_smriti_frontend_enabled(),
        })

        # Override Frappe default route for non-admin
        if not desk_ok:
            bootinfo.default_route = smriti_route

    except Exception as e:
        frappe.log_error(str(e), "SMRITI extend_bootinfo Error")


def on_session_creation(login_manager):
    """
    Frappe v16 hook: on_session_creation
    Called after successful login.
    Sets home_page for redirect.
    """
    try:
        user       = frappe.session.user
        user_roles = frappe.get_roles(user)
        route      = _get_smriti_route(user_roles)
        frappe.local.response["home_page"] = route
    except Exception as e:
        frappe.log_error(str(e), "SMRITI on_session_creation Error")
        frappe.local.response["home_page"] = "/smriti"


def check_desk_access():
    """
    before_request hook — fires on every request.
    Redirects non-desk users away from /desk and /app to /smriti.
    Also blocks Guest sessions and protected config files from /backups/.
    """
    try:
        if not hasattr(frappe, "request") or not frappe.request:
            return

        path = frappe.request.path or ""

        # ─── v1.8.2a: Block /backups/ direct-download for unsafe sessions / protected files
        if path.startswith("/backups/"):
            user = getattr(frappe.session, "user", "Guest")
            filename = path.split("/backups/", 1)[-1].split("/")[0]  # first segment only

            # Block Guest sessions outright
            if user == "Guest":
                _log_blocked_download(filename, user, "Guest session blocked from /backups/")
                frappe.throw(_("Authentication required to download backup files."), frappe.PermissionError)

            # Block any file matching the protected config denylist
            if any(fnmatch.fnmatch(filename, pat) for pat in PROTECTED_CONFIG_PATTERNS):
                _log_blocked_download(filename, user, "Protected config file download blocked.")
                frappe.throw(_("Access denied: protected configuration files cannot be downloaded."), frappe.PermissionError)

            return  # Authenticated user, non-protected file — pass through

        # ─── SMRITI Policy: Block Frappe-owned paths unconditionally ─────────────
        # Any path in SMRITI_BLOCKED_DESK_PATHS → redirect to /smriti.
        # Applies to ALL users including Administrator. No exceptions.
        # Policy: if setup-wizard appears, create a SMRITI page — never expose it.
        for blocked in SMRITI_BLOCKED_DESK_PATHS:
            if path.startswith(blocked):
                raise werkzeug.routing.exceptions.RequestRedirect("/smriti")

        # ─── Desk-access guard for remaining /desk and /app routes ────────────────
        # Non-System-Manager users are redirected to /smriti.
        if path.startswith("/desk") or path.startswith("/app"):
            user = getattr(frappe.session, "user", "Guest")

            # Resolve actual user if Guest + cookies present
            if user == "Guest" and frappe.request.cookies:
                from frappe.auth import validate_auth
                try:
                    validate_auth()
                    user = getattr(frappe.session, "user", "Guest")
                except Exception:
                    pass

            user_roles = frappe.get_roles(user) if user else []

            if not _is_desk_allowed(user, user_roles):
                raise werkzeug.routing.exceptions.RequestRedirect("/smriti")

    except werkzeug.routing.exceptions.RequestRedirect:
        raise
    except (frappe.PermissionError, frappe.AuthenticationError):
        raise  # Intentional security responses — must not be swallowed
    except Exception as e:
        frappe.log_error(str(e), "SMRITI Desk Access Check Error")


def _get_smriti_route(user_roles):
    """Return SMRITI route for highest-priority role."""
    for role in ROLE_PRIORITY:
        if role in user_roles:
            return SMRITI_ROLE_ROUTES.get(role, "/smriti")
    return "/smriti"


def _log_blocked_download(filename, user, reason):
    """Logs a blocked /backups/ download attempt to the Frappe Activity Log."""
    try:
        from smriti_retail_os.backup_api import log_audit_event
        log_audit_event(
            "Blocked Download Attempt",
            f"{reason} File='{filename}' User='{user}' IP={getattr(frappe.local, 'request_ip', 'Unknown')}"
        )
    except Exception:
        frappe.log_error("SMRITI Blocked Download Log Error", frappe.get_traceback())


def _is_desk_allowed(user, user_roles):
    """
    Desk allowed for System Manager role OR Administrator user.
    Administrator is a special USER in Frappe, not always a role.
    """
    if user in DESK_ALLOWED_USERS:
        return True
    return bool(set(user_roles) & DESK_ALLOWED_ROLES)


def _is_smriti_frontend_enabled():
    """
    Feature flag — check System Settings for SMRITI frontend toggle.
    Returns True if enabled or flag doesn't exist yet (default on).
    """
    try:
        # Use db.sql to avoid exceptions when the custom field doesn't exist yet
        result = frappe.db.sql(
            "SELECT value FROM `tabSingles` WHERE doctype='System Settings' AND field='custom_smriti_frontend_enabled'"
        )
        if result:
            return result[0][0] != 0
        return True  # Field not present → default enabled
    except Exception:
        return True  # Default: enabled


@frappe.whitelist()
def get_smriti_session_info():
    """
    Whitelisted API — called by SMRITI frontend on load.
    Returns session info for UI initialization.
    """
    try:
        user       = frappe.session.user
        user_roles = frappe.get_roles(user)
        return {
            "user":              user,
            "full_name":         frappe.db.get_value(
                                     "User", user, "full_name"
                                 ) or user,
            "roles":             user_roles,
            "default_route":     _get_smriti_route(user_roles),
            "desk_allowed":      _is_desk_allowed(user, user_roles),
            "company":           frappe.defaults.get_user_default("Company") or "",
            "app_name":          "SMRITI Retail OS",
            "logo_url":          "/assets/smriti_retail_os/images/smriti_logo.svg",
            "frontend_enabled":  _is_smriti_frontend_enabled(),
        }
    except Exception as e:
        frappe.log_error(str(e), "SMRITI Session Info Error")
        return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def health_check():
    """
    Health check endpoint.
    GET /api/method/smriti_retail_os.boot.health_check
    Returns system status — useful during deployments.
    """
    status = {"status": "ok", "app": "SMRITI Retail OS", "version": "1.0.0"}
    try:
        # Check DB connection
        frappe.db.sql("SELECT 1")
        status["db"] = "ok"
    except Exception as e:
        status["db"] = f"error: {e}"

    try:
        # Check boot module imports
        from smriti_retail_os import psv_service  # noqa
        status["psv_service"] = "ok"
    except Exception as e:
        status["psv_service"] = f"error: {e}"

    try:
        # Check frontend flag
        status["frontend_enabled"] = _is_smriti_frontend_enabled()
    except Exception:
        status["frontend_enabled"] = "unknown"

    return status
