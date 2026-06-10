# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/boot.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
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

        # Force setup_complete = 1 in bootinfo to prevent client-side redirect to setup-wizard
        bootinfo.setup_complete = 1

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

        # ─── Original desk-access guard ───────────────────────────────────────────
        # Only restrict /desk and /app routes (including trailing slashes or subpaths)
        if path.startswith("/desk") or path.startswith("/app"):
            user = getattr(frappe.session, "user", "Guest")
            
            # If user is Guest but request has cookies, try validating auth to resolve actual user
            if user == "Guest" and frappe.request.cookies:
                from frappe.auth import validate_auth
                try:
                    validate_auth()
                    user = getattr(frappe.session, "user", "Guest")
                except Exception:
                    pass

            user_roles = frappe.get_roles(user) if user else []

            # Check if user is allowed to access desk
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
        val = frappe.db.get_single_value(
            "System Settings", "custom_smriti_frontend_enabled"
        )
        return val != 0  # None or 1 = enabled, 0 = disabled
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
