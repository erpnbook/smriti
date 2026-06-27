# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/audit_log_api.py
# @description: SMRITI Security Audit Log API — serves blocked-download and
#               config-export events from the Frappe Activity Log to the
#               SMRITI-owned audit log page. NO Frappe desk exposure.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-10
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

# Operations written by v1.8.2a security interceptors
SMRITI_SECURITY_OPERATIONS = [
    "Blocked Download Attempt",
    "Config Exported",
]


def _check_access():
    """Only System Manager or Administrator may read security audit logs."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.AuthenticationError)
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and frappe.session.user != "Administrator":
        frappe.throw(
            _("Access denied: Security audit log requires System Manager role."),
            frappe.PermissionError
        )


@frappe.whitelist()
def get_security_events(page=1, page_size=50, operation_filter="All"):
    """
    Returns paginated security events from the Frappe Activity Log.

    Filtered to SMRITI_SECURITY_OPERATIONS only.
    No Frappe desk URL is involved — this is consumed exclusively by
    the /smriti-security-log SMRITI page.
    """
    _check_access()

    page = int(page)
    page_size = min(int(page_size), 200)  # Hard cap
    offset = (page - 1) * page_size

    # Build operation filter
    if operation_filter and operation_filter != "All":
        if operation_filter not in SMRITI_SECURITY_OPERATIONS:
            frappe.throw(_("Invalid operation filter."), frappe.ValidationError)
        ops_filter = [operation_filter]
    else:
        ops_filter = SMRITI_SECURITY_OPERATIONS

    filters = {"operation": ["in", ops_filter]}

    total = frappe.db.count("Activity Log", filters=filters)

    rows = frappe.get_all(
        "Activity Log",
        filters=filters,
        fields=[
            "name",
            "creation",
            "user",
            "operation",
            "subject",
            "ip_address",
            "status",
        ],
        order_by="creation desc",
        limit=page_size,
        start=offset,
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "events": rows,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@frappe.whitelist()
def get_event_detail(event_name):
    """Returns full detail for a single Activity Log entry."""
    _check_access()

    if not event_name or ".." in str(event_name) or "/" in str(event_name):
        frappe.throw(_("Invalid event name."), frappe.ValidationError)

    doc = frappe.db.get_value(
        "Activity Log",
        {"name": event_name, "operation": ["in", SMRITI_SECURITY_OPERATIONS]},
        ["name", "creation", "user", "operation", "subject", "ip_address", "status", "content"],
        as_dict=True,
    )

    if not doc:
        frappe.throw(_("Event not found or not a SMRITI security event."), frappe.DoesNotExistError)

    return doc


@frappe.whitelist()
def get_stats():
    """Returns aggregate stats for the security dashboard card."""
    _check_access()

    stats = {}
    for op in SMRITI_SECURITY_OPERATIONS:
        stats[op] = frappe.db.count("Activity Log", filters={"operation": op})

    # Last 24h blocked attempts
    from frappe.utils import now_datetime, add_to_date
    yesterday = add_to_date(now_datetime(), hours=-24)
    stats["blocked_last_24h"] = frappe.db.count(
        "Activity Log",
        filters={
            "operation": "Blocked Download Attempt",
            "creation": [">", yesterday],
        }
    )

    return stats
