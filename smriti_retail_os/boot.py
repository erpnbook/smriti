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
import re

# ── Constants ──────────────────────────────────────────────────────────────────
_BRAND_NAME = "SMRITI Retail OS"
_LOGO_URL   = "/assets/smriti_retail_os/images/logo.svg"
_BRAND_HTML = (
    '<img src="{logo}" style="height:32px;width:auto;display:block;" '
    'alt="{name}">'
).format(logo=_LOGO_URL, name=_BRAND_NAME)

# ERPNext / Frappe app names whose titles we override
_REBRAND_APPS = {"erpnext", "frappe"}
_APP_TITLE_OVERRIDES = {
    "erpnext": _BRAND_NAME,
    "frappe":  "SMRITI Framework",
}

# Regex to detect any ERPNext / Frappe branding in string values
_BRAND_RE = re.compile(
    r"ERPNext|Frappe\s+(Technologies|Framework)|Built\s+with\s+Frappe|Powered\s+by\s+Frappe",
    re.IGNORECASE,
)


def _replace(text: str) -> str:
    """Replace all ERPNext/Frappe references with SMRITI branding."""
    text = re.sub(r"ERPNext\s*[—\-]\s*", _BRAND_NAME + " — ", text)
    text = re.sub(r"[—\-]\s*ERPNext", "— " + _BRAND_NAME, text)
    text = re.sub(r"ERPNext", _BRAND_NAME, text)
    text = re.sub(r"Frappe Technologies", "SMRITI", text)
    text = re.sub(r"Frappe Framework", _BRAND_NAME, text)
    text = re.sub(r"Built with Frappe", _BRAND_NAME, text)
    text = re.sub(r"Powered by Frappe", _BRAND_NAME, text)
    return text


def _patch_page(page: dict) -> None:
    """Patch a single workspace/sidebar page dict in-place."""
    if not isinstance(page, dict):
        return
    # app_title is what Frappe renders as subtitle below workspace name in sidebar
    if page.get("app_title") and _BRAND_RE.search(page["app_title"]):
        page["app_title"] = _replace(page["app_title"])
    # If the page belongs to erpnext, override its app_title
    if (page.get("app") or "").lower() in _REBRAND_APPS:
        page["app_title"] = _BRAND_NAME
    # Also patch label/title fields
    for key in ("label", "title", "module_name", "subtitle"):
        if page.get(key) and _BRAND_RE.search(str(page[key])):
            page[key] = _replace(str(page[key]))


def _apply_branding(bootinfo):
    """
    Server-side hook: override ALL branding-related bootinfo keys so that
    Frappe renders the navbar, page titles, sidebar, and About dialog with
    SMRITI branding *before* any HTML is sent to the browser.
    """

    # 1. App name (browser <title> tag, breadcrumbs, system headers)
    bootinfo.app_name = _BRAND_NAME

    # 2. Navbar brand HTML — rendered top-left in the desk
    bootinfo.brand_html = _BRAND_HTML

    # 3. App logo URL
    bootinfo.app_logo_url = _LOGO_URL

    # 4. Splash / loading image
    bootinfo.splash_image = _LOGO_URL

    # 5. Favicon
    bootinfo.favicon = "/assets/smriti_retail_os/favicon.png"

    # 6. System defaults (used by Frappe templates and some desk JS)
    if isinstance(bootinfo.get("sysdefaults"), dict):
        bootinfo.sysdefaults["app_name"] = _BRAND_NAME
        # Also scrub any ERPNext strings in sysdefaults
        for k, v in list(bootinfo.sysdefaults.items()):
            if isinstance(v, str) and _BRAND_RE.search(v):
                bootinfo.sysdefaults[k] = _replace(v)

    # 7. Installed apps list shown in Help → About
    installed = bootinfo.get("installed_apps") or []
    for app in installed:
        if not isinstance(app, dict):
            continue
        name = (app.get("name") or "").lower()
        if name in _APP_TITLE_OVERRIDES:
            app["title"]       = _APP_TITLE_OVERRIDES[name]
            app["description"] = "Smarter Retail. Built for India."

    # 8. ── CRITICAL: sidebar_pages & workspaces ────────────────────────────────
    # Frappe builds the workspace sidebar from bootinfo.sidebar_pages or bootinfo.workspaces.
    # Each entry has { name, title, app, app_title, ... }
    # "app_title" is what appears as the subtitle under each workspace link.
    sidebar_pages = bootinfo.get("sidebar_pages") or {}
    if isinstance(sidebar_pages, dict):
        for key in ("pages", "public_pages", "private_pages"):
            pages = sidebar_pages.get(key) or []
            for page in pages:
                _patch_page(page)
    elif isinstance(sidebar_pages, list):
        for page in sidebar_pages:
            _patch_page(page)

    workspaces = bootinfo.get("workspaces")
    if isinstance(workspaces, dict):
        pages = workspaces.get("pages") or []
        for page in pages:
            _patch_page(page)

    # 9. Also patch top-level workspace_sidebar_items / workspace_sidebar_item if present
    for key in (
        "workspace_sidebar_items",
        "workspace_sidebar_item",
        "allowed_pages",
        "module_wise_workspaces",
    ):
        val = bootinfo.get(key)
        if isinstance(val, list):
            for page in val:
                _patch_page(page)
        elif isinstance(val, dict):
            for page in val.values():
                if isinstance(page, list):
                    for p in page:
                        _patch_page(p)
                elif isinstance(page, dict):
                    _patch_page(page)
            # If key is workspace_sidebar_item, also patch its values/items dicts
            if key == "workspace_sidebar_item":
                for ws_name, ws_data in val.items():
                    if isinstance(ws_data, dict):
                        _patch_page(ws_data)
                        items = ws_data.get("items") or []
                        for item in items:
                            _patch_page(item)

    # 10. nav_items (top navbar links that may carry ERPNext labels)
    nav_items = bootinfo.get("nav_items") or []
    for item in nav_items:
        if isinstance(item, dict):
            for k in ("label", "title"):
                if item.get(k) and _BRAND_RE.search(str(item[k])):
                    item[k] = _replace(str(item[k]))

    # 11. Module info dicts
    module_info = bootinfo.get("module_info") or {}
    if isinstance(module_info, dict):
        for mod_name, mod_data in module_info.items():
            if isinstance(mod_data, dict):
                for k in ("label", "title", "app_title"):
                    if mod_data.get(k) and _BRAND_RE.search(str(mod_data[k])):
                        mod_data[k] = _replace(str(mod_data[k]))

    # 12. desk_settings / user_settings strings
    for key in ("desk_settings", "user_info"):
        val = bootinfo.get(key)
        if isinstance(val, dict):
            for k, v in val.items():
                if isinstance(v, str) and _BRAND_RE.search(v):
                    val[k] = _replace(v)


def extend_bootinfo(bootinfo):
    """
    Main bootinfo extension hook registered in hooks.py.
    Applies branding for ALL users, then handles role-based routing.
    """

    # ── Always apply branding ──────────────────────────────────────────────────
    _apply_branding(bootinfo)

    # ── Role-based routing ─────────────────────────────────────────────────────
    user = frappe.session.user
    roles = frappe.get_roles(user)

    # Cashier redirect:
    if "SMRITI Cashier" in roles:
        bootinfo.default_route = "/billing"

    # Store Manager redirect:
    elif "SMRITI Store Manager" in roles:
        bootinfo.default_route = "/desk"


def boot_session(bootinfo):
    extend_bootinfo(bootinfo)
