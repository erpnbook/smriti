# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import add_days, today

def daily_telemetry_cleanup():
    """Purge/aggregate telemetry usage logs older than retention period (default 90 days)."""
    retention_days = 90
    try:
        import json
        import os
        config_path = frappe.get_app_path("smriti_retail_os", "sdc", "compiler_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cfg = json.load(f)
            retention_days = cfg.get("telemetry_retention_days", 90)
    except Exception:
        pass

    purge_date = add_days(today(), -retention_days)
    smriti.db.delete("SMRITI Knowledge Usage Log", {"timestamp": ["<", purge_date]})
    smriti.db.commit()
