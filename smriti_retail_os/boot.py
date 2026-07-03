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
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
import frappe
import fnmatch
import werkzeug.routing.exceptions
from frappe import _
from smriti_retail_os import __version__
from smriti_retail_os.security_constants import PROTECTED_CONFIG_PATTERNS
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

class ServiceWorkerResponse(HTTPException):
    def __init__(self, content):
        self.content = content
        super(ServiceWorkerResponse, self).__init__()

    def get_response(self, environ=None):
        response = Response(
            self.content,
            content_type='application/javascript; charset=utf-8',
        )
        response.headers['Service-Worker-Allowed'] = '/'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

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
            "app_version":   __version__,
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

        # Injects licensing summary for License validation gate (Level 7 check)
        from smriti_retail_os.license.manager import get_license_summary
        bootinfo.smriti_license = get_license_summary()
        # SMRITI Navigation Manager (SNM) dynamic resolution
        try:
            from smriti_retail_os.navigation.navigation_service import get_user_navigation
            bootinfo.smriti_navigation = get_user_navigation(user)
        except Exception as e:
            frappe.log_error(str(e), "SMRITI Navigation Manager Resolution Error")
            try:
                import json
                from smriti_retail_os.navigation.navigation_service import CANONICAL_NAV
                bootinfo.smriti_navigation = json.loads(json.dumps(CANONICAL_NAV))
            except Exception:
                pass

        # Injects site config for Store defaults (Level 6 resolution)
        from smriti_retail_os.company_api import get_company_settings, get_active_company
        comp = get_active_company()
        comp_settings = get_company_settings(comp) if comp else {}

        # Read and parse smriti_site_config from frappe.conf
        cge_enabled = False
        raw_config = frappe.conf.get("smriti_site_config")
        if raw_config:
            if isinstance(raw_config, dict):
                cge_enabled = raw_config.get("cge_enabled")
            elif isinstance(raw_config, str):
                import re
                match = re.search(r"cge_enabled\s*:\s*(true|1|false|0)", raw_config, re.IGNORECASE)
                if match:
                    cge_enabled = match.group(1).lower() in ("true", "1")
                else:
                    import json
                    try:
                        parsed = json.loads(raw_config)
                        if isinstance(parsed, dict):
                            cge_enabled = parsed.get("cge_enabled")
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in boot.py:147: {sys.exc_info()[1]}")

        bootinfo.smriti_site_config = frappe._dict({
            "store_theme": comp_settings.get("store_theme") or "hybrid",
            "store_experience": comp_settings.get("store_experience") or "standard",
            "terminal_type": comp_settings.get("terminal_type") or "standard",
            "brand_overrides": comp_settings.get("brand_overrides") or {},
            "cge_enabled": True,
            "ai_hub_enabled": True,
            "intelligence_enabled": True
        })

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


def _map_smriti_path(path):
    """
    Maps legacy/custom Desk route names to SMRITI standalone web routes.
    Example: /app/smriti-barcode -> /barcode
    """
    clean = path
    if clean.startswith("/app/"):
        clean = clean[5:]
    elif clean.startswith("/desk/"):
        clean = clean[6:]

    if clean.startswith("smriti-"):
        clean = clean[7:]
    elif clean.startswith("smriti_"):
        clean = clean[7:]

    if clean in ("desk", "sidebar"):
        return "/smriti"
    if clean == "psv-dashboard":
        return "/smriti-psv-dashboard"

    mapping = {
        "barcode": "/barcode",
        "shift": "/shift",
        "billing": "/billing",
        "inventory": "/inventory",
        "purchase": "/purchase",
        "reports": "/reports",
        "backup": "/backup",
        "customers": "/customers",
        "suppliers": "/suppliers",
        "payments": "/payments",
        "sales-invoices": "/sales_invoices",
        "sales_invoices": "/sales_invoices",
        "sales-return": "/sales_return",
        "sales_return": "/sales_return",
        "supplier-returns": "/supplier_returns",
        "supplier_returns": "/supplier_returns",
        "purchase-invoice": "/purchase_invoice",
        "purchase_invoice": "/purchase_invoice",
        "purchase-receipt": "/purchase_receipt",
        "purchase_receipt": "/purchase_receipt",
        "delivery-challan": "/delivery_challan",
        "delivery_challan": "/delivery_challan",
        "grn": "/smriti-grn",
        "purchase-order": "/smriti-purchase-order",
        "cge": "/smriti-cge",
        "sfm": "/smriti-sfm",
        "sfc": "/smriti-sfc",
        "pdt": "/smriti-pdt",
        "uie": "/smriti-uie",
        "pos-profiles": "/smriti-pos-profiles",
        "pos_profiles": "/smriti-pos-profiles",
        "loyalty": "/smriti-cge",
        "negative-stock": "/inventory",
        "negative_stock": "/inventory",
    }

    if clean in mapping:
        return mapping[clean]

    return f"/{clean}"


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

        # Serve sw.js directly at root scope with correct MIME type to bypass Frappe website HTML rendering
        if path == "/sw.js":
            sw_path = frappe.get_app_path('smriti_retail_os', 'public', 'js', 'sw.js')
            try:
                with open(sw_path, 'rb') as f:
                    sw_content = f.read()
            except Exception:
                sw_content = b""
            raise ServiceWorkerResponse(sw_content)

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

        # ─── SMRITI Policy: Redirect legacy /desk/smriti-* and /app/smriti-* to dedicated standalone routes
        if path.startswith(("/desk/smriti-", "/desk/smriti_")):
            raise werkzeug.routing.exceptions.RequestRedirect(_map_smriti_path(path))
        if path.startswith(("/app/smriti-", "/app/smriti_")):
            raise werkzeug.routing.exceptions.RequestRedirect(_map_smriti_path(path))

        # ─── SMRITI Policy: Redirect sidebar template pages direct access to home
        if path in ("/smriti-sidebar", "/smriti_sidebar", "/sidebar", "/app/sidebar", "/desk/sidebar"):
            raise werkzeug.routing.exceptions.RequestRedirect("/smriti")

        # ─── SMRITI Policy: Redirect PSV Enablement shortcut paths to SMRITI Help Tab
        if path in ("/app/knowledge-center/psv", "/app/enablement/psv", "/knowledge-center/psv", "/enablement/psv") or path.startswith(("/app/knowledge-center/psv/", "/app/enablement/psv/", "/knowledge-center/psv/", "/enablement/psv/")):
            raise werkzeug.routing.exceptions.RequestRedirect("/smriti-help?tab=enablement")

        # ─── SMRITI Policy: Redirect any remaining /desk or /desk/ paths to SMRITI
        if path == "/desk" or path.startswith("/desk/"):
            raise werkzeug.routing.exceptions.RequestRedirect("/smriti")

        # ─── SMRITI Policy: Block Frappe-owned paths for non-administrative users ─
        # For business users, any path in SMRITI_BLOCKED_DESK_PATHS → redirect to /smriti.
        # This preserves legitimate administrative workflows for Administrator / System Manager.
        user = getattr(frappe.session, "user", "Guest")
        user_roles = frappe.get_roles(user) if user else []
        is_admin_or_sys_mgr = (user == "Administrator" or "System Manager" in user_roles)

        for blocked in SMRITI_BLOCKED_DESK_PATHS:
            if path.startswith(blocked) and not is_admin_or_sys_mgr:
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
                    import sys
                    _frappe = sys.modules.get('frappe')
                    if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in boot.py:250: {sys.exc_info()[1]}")

            user_roles = frappe.get_roles(user) if user else []

            if not _is_desk_allowed(user, user_roles):
                raise werkzeug.routing.exceptions.RequestRedirect("/smriti")

    except (werkzeug.routing.exceptions.RequestRedirect, HTTPException):
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

        # Read and parse smriti_site_config from frappe.conf
        cge_enabled = False
        raw_config = frappe.conf.get("smriti_site_config")
        if raw_config:
            if isinstance(raw_config, dict):
                cge_enabled = raw_config.get("cge_enabled")
            elif isinstance(raw_config, str):
                import re
                match = re.search(r"cge_enabled\s*:\s*(true|1|false|0)", raw_config, re.IGNORECASE)
                if match:
                    cge_enabled = match.group(1).lower() in ("true", "1")
                else:
                    import json
                    try:
                        parsed = json.loads(raw_config)
                        if isinstance(parsed, dict):
                            cge_enabled = parsed.get("cge_enabled")
                    except Exception:
                        import sys
                        _frappe = sys.modules.get('frappe')
                        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in boot.py:340: {sys.exc_info()[1]}")

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
            "smriti_site_config": {
                "cge_enabled": True,
                "ai_hub_enabled": True,
                "intelligence_enabled": True
            }
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
    status = {"status": "ok", "app": "SMRITI Retail OS", "version": __version__}

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
