# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/website_context.py
# @description: Frappe website context override for SMRITI whitelabel branding.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

"""
SMRITI Retail OS — Website Context Hook
Overrides ERPNext/Frappe branding on all web/portal pages (Jinja-rendered).
Registered in hooks.py via: website_context = "smriti_retail_os.website_context.get_context"
"""

_BRAND_NAME = "SMRITI Retail OS"
_LOGO_URL   = "/assets/smriti_retail_os/images/logo.svg"
_FAVICON    = "/assets/smriti_retail_os/favicon.png"


def get_context(context):
    """
    Frappe calls this for every web page render.
    We inject SMRITI branding into the Jinja context so all
    {{ app_name }}, {{ brand_html }}, {{ favicon }} references
    render with SMRITI values — no JS patching needed on web pages.
    """
    import frappe

    # Redirect to setup wizard if no company exists in the database
    current_path = frappe.local.request.path if (hasattr(frappe.local, "request") and frappe.local.request) else ""
    if current_path:
        normalized_path = current_path.rstrip("/").lower()
        if normalized_path not in ["/setup-wizard", "/login"] and not normalized_path.startswith("/assets/") and not normalized_path.startswith("/api/"):
            try:
                companies = frappe.get_all("Company", limit=1)
                if not companies:
                    frappe.local.flags.redirect_location = "/setup-wizard"
                    raise frappe.Redirect
            except frappe.Redirect:
                raise
            except Exception:
                pass

    # Ensure CSRF token is generated and persisted in session database during GET request
    if frappe.session.user != "Guest" and getattr(frappe.local, "session", None) and getattr(frappe.local, "session_obj", None):
        if not frappe.local.session.data.get("csrf_token"):
            frappe.local.session.data.csrf_token = frappe.generate_hash()
        
        # Save session in database/cache by temporarily disabling read_only
        original_read_only = frappe.flags.read_only
        frappe.flags.read_only = False
        try:
            frappe.local.session_obj.update(force=True)
            frappe.db.commit()
        except Exception:
            pass
        finally:
            frappe.flags.read_only = original_read_only

    context.update(
        {
            "app_name":   _BRAND_NAME,
            "brand_html": (
                '<img src="{logo}" style="height:36px;width:auto;" '
                'alt="{name}">'.format(logo=_LOGO_URL, name=_BRAND_NAME)
            ),
            "favicon":          _FAVICON,
            "splash_image":     _LOGO_URL,
            "top_bar_brand":    _BRAND_NAME,
            "meta_description": "SMRITI Retail OS — Smarter Retail, Built for India.",
            "meta_title":       _BRAND_NAME,
            "csrf_token":       frappe.local.session.data.csrf_token if (getattr(frappe.local, "session", None) and frappe.local.session.data.get("csrf_token")) else "",
        }
    )
    return context
