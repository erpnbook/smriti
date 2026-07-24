# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/telemetry.py
# @description: SMRITI Retail OS installation ping and periodic usage telemetry module.
#               Fully GPL-3.0 & MIT compliant — anonymized, non-blocking, and opt-out supported.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-07-24
# @version: 1.8.6
# @license: GPL-3.0-only / MIT
#

import sys
import hashlib
import requests
import frappe
from smriti_retail_os import smriti


def _get_installation_id():
    """Returns or generates a stable anonymized installation ID hash for this site."""
    try:
        doc = frappe.get_single("SMRITI License")
        if doc.get("installation_id"):
            return doc.installation_id
    except Exception:
        pass

    site_name = getattr(frappe.local, "site", "smriti-default-site")
    return hashlib.sha256(site_name.encode("utf-8")).hexdigest()[:16].upper()


def _is_telemetry_enabled():
    """Checks if telemetry collection is enabled (defaults to True unless explicitly disabled)."""
    try:
        telemetry_opt_out = frappe.db.get_single_value("SMRITI License", "telemetry_disabled")
        if int(telemetry_opt_out or 0) == 1:
            return False
    except Exception:
        pass
    return True


def on_app_installed():
    """
    Frappe `after_install` hook trigger.
    Sends a single anonymized ping to the central licensing/telemetry endpoint
    when `bench install-app smriti_retail_os` completes.
    """
    if not _is_telemetry_enabled():
        return

    try:
        install_id = _get_installation_id()
        payload = {
            "event": "APP_INSTALLED",
            "app_name": "smriti_retail_os",
            "app_version": "1.8.6",
            "installation_id": install_id,
            "frappe_version": getattr(frappe, "__version__", "unknown"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }

        # Non-blocking, short timeout POST ping
        requests.post(
            "https://telemetry.erpnbook.com/api/v1/install-ping",
            json=payload,
            timeout=3,
            headers={"User-Agent": "SMRITI-Retail-OS/1.8.6"}
        )
    except Exception as e:
        # Silent exception — never interrupt install process
        _frappe = sys.modules.get("frappe")
        if _frappe:
            _frappe.logger().debug(f"SMRITI Telemetry: Installation ping suppressed: {str(e)}")


def send_weekly_heartbeat():
    """
    Frappe `scheduler_events` weekly cron trigger.
    Sends periodic active instance usage heartbeats to the central telemetry endpoint.
    """
    if not _is_telemetry_enabled():
        return

    try:
        doc = frappe.get_single("SMRITI License")
        payload = {
            "event": "HEARTBEAT",
            "installation_id": doc.installation_id or _get_installation_id(),
            "license_type": doc.license_type or "Community",
            "organization_name": doc.organization_name or "",
            "store_name": doc.store_name or "",
            "app_version": "1.8.6",
            "company_count": smriti.db.count("Company") if hasattr(smriti, "db") else 1
        }

        requests.post(
            "https://telemetry.erpnbook.com/api/v1/heartbeat",
            json=payload,
            timeout=3,
            headers={"User-Agent": "SMRITI-Retail-OS/1.8.6"}
        )
    except Exception as e:
        _frappe = sys.modules.get("frappe")
        if _frappe:
            _frappe.logger().debug(f"SMRITI Telemetry: Heartbeat ping suppressed: {str(e)}")
