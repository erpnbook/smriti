# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/__init__.py
# @description: SMRITI Retail OS -- Frappe app package initializer.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.5
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

__version__ = "1.8.5"

# Advanced PDF Resilience: Monkey-patch get_pdf to automatically fallback
# and strip broken image links/external assets to prevent transaction crashes.
try:
    import frappe
    import frappe.utils.pdf
    from bs4 import BeautifulSoup

    original_get_pdf = frappe.utils.pdf.get_pdf
    original_prepare_options = frappe.utils.pdf.prepare_options

    # 1. Inject load-error-handling ignore by default
    def patched_prepare_options(html, options):
        html, options = original_prepare_options(html, options)
        if options is None:
            options = {}
        options["load-error-handling"] = "ignore"
        return html, options

    frappe.utils.pdf.prepare_options = patched_prepare_options

    # 2. Resilient fallback wrapper for get_pdf
    def patched_get_pdf(html, options=None, output=None):
        try:
            return original_get_pdf(html, options, output)
        except Exception as e:
            err_str = str(e).lower()
            if "broken image" in err_str or "wkhtmltopdf reported" in err_str or "validationerror" in err_str or "contentnotfound" in err_str:
                try:
                    # Parse HTML and replace all img src attributes with a blank inline GIF
                    soup = BeautifulSoup(html, "html.parser")
                    for img in soup.find_all("img"):
                        img["src"] = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
                    
                    cleaned_html = str(soup)
                    # Retry PDF generation with cleaned inline images
                    return original_get_pdf(cleaned_html, options, output)
                except Exception as inner_e:
                    # If fallback fails, log inner error and raise original
                    frappe.logger("pdf").error(f"[SMRITI PDF Fallback Error]: {inner_e}")
                    raise e
            raise e

    frappe.utils.pdf.get_pdf = patched_get_pdf

    # 3. Patch get_locale_value in frappe.locale to prevent UnboundLocalError
    import frappe.locale
    def patched_get_locale_value(key, language=None):
        value = None
        lang = language or getattr(frappe.local, "lang", None)
        if lang:
            try:
                value = frappe.client_cache.get_doc("Language", lang).get(key)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in __init__.py:66: {sys.exc_info()[1]}")
        return value or frappe.db.get_default(key)

    frappe.locale.get_locale_value = patched_get_locale_value

except Exception as e:
    import logging
    logging.getLogger("frappe").warning(f"Failed to apply SMRITI PDF or Locale patches: {e}")

# Dynamic queue registration for SMRITI async printer queue
try:
    import frappe.utils.background_jobs
    if hasattr(frappe.utils.background_jobs, "default_queue_list"):
        if "barcode" not in frappe.utils.background_jobs.default_queue_list:
            frappe.utils.background_jobs.default_queue_list.append("barcode")
except Exception as e:
    import logging
    logging.getLogger("frappe").warning(f"Failed to register barcode queue: {e}")

