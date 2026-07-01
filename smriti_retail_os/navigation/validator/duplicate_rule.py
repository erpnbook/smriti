# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/duplicate_rule.py
# @description: Validator rule checking for duplicate routes and item IDs.
# @author: Jawahar R. Mallah
#

from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class DuplicateRule(BaseValidator):
    rule_id = "NAV-001"
    severity = "CRITICAL"
    title = "Duplicate Navigation Items"

    def validate(self, nav_config):
        warnings = []
        if not nav_config or "sections" not in nav_config:
            return warnings

        seen_ids = {}
        seen_routes = {}

        for sec in nav_config["sections"]:
            sec_id = sec.get("id")
            for item in sec.get("items", []):
                item_id = item.get("id")
                item_route = item.get("route")
                item_status = item.get("status")

                # Skip header/label type pseudo-items
                if item.get("type") == "header":
                    continue

                # 1. Check duplicate ID
                if item_id:
                    if item_id in seen_ids:
                        warnings.append({
                            "rule_id": self.rule_id,
                            "severity": self.severity,
                            "module": sec_id,
                            "menu": item.get("label", item_id),
                            "route": item_route,
                            "source": "navigation_service.py",
                            "file": "navigation_service.py",
                            "line": 0,
                            "recommendation": f"Duplicate item ID '{item_id}' detected. Ensure item IDs are globally unique.",
                            "auto_fix": False
                        })
                    else:
                        seen_ids[item_id] = sec_id

                # 2. Check duplicate Route (only check active routes)
                if item_route and item_route != "#" and item_status == "active":
                    # Strip parameters for comparison
                    clean_route = item_route.split("?")[0].rstrip("/")
                    if clean_route in seen_routes:
                        prev_module = seen_routes[clean_route]
                        warnings.append({
                            "rule_id": self.rule_id,
                            "severity": self.severity,
                            "module": sec_id,
                            "menu": item.get("label", item_id),
                            "route": item_route,
                            "source": "navigation_service.py",
                            "file": "navigation_service.py",
                            "line": 0,
                            "recommendation": f"Duplicate route '{item_route}' found in sections '{sec_id}' and '{prev_module}'. Merge or redirect duplicates.",
                            "auto_fix": False
                        })
                    else:
                        seen_routes[clean_route] = sec_id

        return warnings
