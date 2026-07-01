# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/route_rule.py
# @description: Validator rule checking for dead / broken routes.
# @author: Jawahar R. Mallah
#

import os
from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class RouteRule(BaseValidator):
    rule_id = "NAV-003"
    severity = "HIGH"
    title = "Broken Routes & Dead Links"

    def validate(self, nav_config):
        import frappe
        warnings = []
        if not nav_config or "sections" not in nav_config:
            return warnings

        app_path = frappe.get_app_path("smriti_retail_os")
        www_dir = os.path.join(app_path, "www")

        for sec in nav_config["sections"]:
            sec_id = sec.get("id")
            for item in sec.get("items", []):
                item_id = item.get("id")
                item_route = item.get("route")
                item_status = item.get("status")

                if item.get("type") == "header" or item_status not in ("active", "coming_soon"):
                    continue

                if not item_route or item_route == "#":
                    continue

                # Skip items that point to the Coming Soon redirect page explicitly
                if "/smriti-coming-soon" in item_route:
                    continue

                # Classify severity: coming_soon routes are planned, not broken
                route_severity = "MEDIUM" if item_status == "coming_soon" else self.severity

                # Clean query parameters
                clean_route = item_route.split("?")[0].rstrip("/")

                # 1. Standalone pages (Jinja / www)
                if not clean_route.startswith("/app/"):
                    # Check if clean_route maps to a file in www/
                    # e.g., /billing -> billing.html or billing.py
                    filename = clean_route.lstrip("/")
                    if not filename:
                        continue # Home page /
                    
                    html_file = os.path.join(www_dir, f"{filename}.html")
                    py_file = os.path.join(www_dir, f"{filename}.py")

                    # Handle directories (e.g. reports/sales -> www/reports/sales.html)
                    if not os.path.exists(html_file) and not os.path.exists(py_file):
                        # Try index files inside folders
                        folder_index_html = os.path.join(www_dir, filename, "index.html")
                        folder_index_py = os.path.join(www_dir, filename, "index.py")
                        
                        if not os.path.exists(folder_index_html) and not os.path.exists(folder_index_py):
                            # Try matching nested routes
                            # e.g., /reports/sales -> check if www/reports.html exists
                            parts = filename.split("/")
                            parent_html = os.path.join(www_dir, f"{parts[0]}.html")
                            parent_py = os.path.join(www_dir, f"{parts[0]}.py")
                            if not os.path.exists(parent_html) and not os.path.exists(parent_py):
                                warnings.append({
                                    "rule_id": self.rule_id,
                                    "severity": route_severity,
                                    "module": sec_id,
                                    "menu": item.get("label", item_id),
                                    "route": item_route,
                                    "source": "navigation_service.py",
                                    "file": "navigation_service.py",
                                    "line": 0,
                                    "recommendation": f"Route '{item_route}' does not map to any www page template on disk. Mark status 'coming_soon' if planned.",
                                    "auto_fix": False
                                })

                # 2. Desk Pages (under /app/)
                else:
                    # Desk route: check if standard page or DocType exists
                    desk_path = clean_route.replace("/app/", "")
                    parts = desk_path.split("/")
                    
                    # parts[0] is typically DocType or Page name (e.g. /app/sales-invoices)
                    target = parts[0]
                    # Convert slug format to DocType format (e.g. sales-invoice -> Sales Invoice)
                    doctype_name = " ".join(word.capitalize() for word in target.split("-"))
                    
                    # Check if target is a valid DocType
                    if not frappe.db.exists("DocType", doctype_name):
                        # Check if target is a valid Page
                        if not frappe.db.exists("Page", target):
                            # Check if matches actual route keys
                            if target not in ["smriti", "masters", "inventory", "purchase", "billing", "reports"]:
                                warnings.append({
                                    "rule_id": self.rule_id,
                                    "severity": route_severity,
                                    "module": sec_id,
                                    "menu": item.get("label", item_id),
                                    "route": item_route,
                                    "source": "navigation_service.py",
                                    "file": "navigation_service.py",
                                    "line": 0,
                                    "recommendation": f"Desk route '{item_route}' target DocType or Page '{target}' does not exist in Frappe database.",
                                    "auto_fix": False
                                })

        return warnings
