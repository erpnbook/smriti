# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/printview.py
# @desc: SMRITI Print Preview guard — validates document existence and logs
#        every print attempt before delegating to standard Frappe printview.
# @author: Jawahar R Mallah
# @version: 1.0.0
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
import json
from frappe import _
from frappe.utils import now_datetime
from smriti_retail_os import smriti

no_cache = 1
title = "SMRITI — Print Preview"


def _log_print_attempt(doctype, docname, exists, user):
    """Append a PRINT_ATTEMPT entry to the Error Log for diagnostics."""
    try:
        entry = {
            "event": "PRINT_ATTEMPT",
            "doctype": doctype or "",
            "docname": docname or "",
            "exists": exists,
            "timestamp": str(now_datetime()),
            "user": user or ""
        }
        frappe.log_error(
            message=json.dumps(entry, indent=2),
            title="SMRITI PRINT_ATTEMPT"
        )
    except Exception:
        pass


def get_context(context):
    """
    SMRITI Print Preview Guard.

    Route: /printview (overrides frappe.www.printview)

    Behaviour:
      - If the requested document does NOT exist in the database
        → set context.error = True and render the branded error template.
      - If the document DOES exist
        → proxy all query-params to the standard Frappe printview page controller.
      - Logs every attempt regardless of outcome.
    """
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    # Strip all Frappe chrome to keep a clean print window
    context.web_include_js = []
    context.web_include_css = []
    context.no_header = True
    context.no_breadcrumbs = True
    context.no_cache = True
    context.show_sidebar = False
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    user = frappe.session.user
    params = frappe.local.request.args

    doctype = params.get("doctype", "").strip()
    docname = params.get("name", "").strip()

    context.doctype = doctype
    context.docname = docname
    context.user = user
    context.error = False
    context.error_reason = ""
    context.error_detail = ""

    # ── Validate inputs ───────────────────────────────────────────────────────
    if not doctype or not docname:
        context.error = True
        context.error_reason = _("Missing document information.")
        context.error_detail = _("Both doctype and document name are required to generate a print preview.")
        _log_print_attempt(doctype, docname, False, user)
        return context

    # ── Check document existence ──────────────────────────────────────────────
    doc_exists = False
    try:
        if smriti.db.exists(doctype, docname):
            # Also verify user has read permission
            smriti.permissions.require_read(doctype, docname)
            doc_exists = True
    except frappe.PermissionError:
        context.error = True
        context.error_reason = _("Access Denied.")
        context.error_detail = _(
            "You do not have permission to print this {0}.").format(_(doctype))
        _log_print_attempt(doctype, docname, False, user)
        return context
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SMRITI printview check_permission error")

    if not doc_exists:
        context.error = True
        context.error_reason = _("The requested voucher could not be found.")
        context.error_detail = _(
            "This usually happens when the voucher has not yet been saved to the database, "
            "or was deleted. Please save the document and try again."
        )
        _log_print_attempt(doctype, docname, False, user)
        return context

    # ── Document exists — render via Frappe's printview.html directly ─────────
    # Frappe's template_page.py resolves the HTML template via context.template.
    # By overriding context.template with Frappe's own printview.html path,
    # Frappe's template_page renderer will use it instead of ours.
    _log_print_attempt(doctype, docname, True, user)

    try:
        from frappe.www import printview as frappe_printview
        # frappe_printview.get_context() RETURNS a dict — it does NOT modify context in-place.
        # We must merge its return value into our context.
        pv_data = frappe_printview.get_context(context)

        # Debug: log what we received
        frappe.log_error(
            message="type={}, keys={}, body_len={}".format(
                type(pv_data).__name__,
                list(pv_data.keys()) if isinstance(pv_data, dict) else "n/a",
                len(pv_data.get("body", "") or "") if isinstance(pv_data, dict) else "n/a"
            ),
            title="SMRITI printview pv_data debug"
        )

        if pv_data and isinstance(pv_data, dict):
            context.update(pv_data)
        elif hasattr(pv_data, "__iter__"):
            context.update(dict(pv_data))

        # Mark as valid print so our template renders the Frappe layout
        context.error = False
        return context

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SMRITI printview delegation error")
        context.error = True
        context.error_reason = _("Print generation failed.")
        context.error_detail = str(e)
        # Restore SMRITI error template settings
        context.base_template_path = "smriti_retail_os/templates/blank.html"
        context.no_header = True

    return context


