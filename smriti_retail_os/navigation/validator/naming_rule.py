# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/naming_rule.py
# @description: Validator rule checking for menu item ID and route naming conventions.
# @author: Jawahar R. Mallah
#

import re
from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class NamingRule(BaseValidator):
    rule_id = "NAV-006"
    severity = "LOW"
    title = "Naming Convention Violations"

    def validate(self, nav_config):
        warnings = []
        if not nav_config or "sections" not in nav_config:
            return warnings

        # Patterns
        id_pattern = re.compile(r"^[a-z0-9_]+$")
        
        for sec in nav_config["sections"]:
            sec_id = sec.get("id")
            
            # Check Section ID
            if sec_id and not id_pattern.match(sec_id):
                warnings.append({
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "module": sec_id,
                    "menu": sec.get("label", sec_id),
                    "route": "",
                    "source": "navigation_service.py",
                    "file": "navigation_service.py",
                    "line": 0,
                    "recommendation": f"Section ID '{sec_id}' violates naming conventions. Use lowercase, numbers, and underscores only.",
                    "auto_fix": False
                })

            for item in sec.get("items", []):
                item_id = item.get("id")
                item_route = item.get("route")

                # Check Item ID
                if item_id and not id_pattern.match(item_id):
                    warnings.append({
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "module": sec_id,
                        "menu": item.get("label", item_id),
                        "route": item_route,
                        "source": "navigation_service.py",
                        "file": "navigation_service.py",
                        "line": 0,
                        "recommendation": f"Item ID '{item_id}' violates naming conventions. Use lowercase, numbers, and underscores only.",
                        "auto_fix": False
                    })

                # Check Route Naming
                if item_route and item_route != "#":
                    # Check that route starts with /
                    if not item_route.startswith("/"):
                        warnings.append({
                            "rule_id": self.rule_id,
                            "severity": self.severity,
                            "module": sec_id,
                            "menu": item.get("label", item_id),
                            "route": item_route,
                            "source": "navigation_service.py",
                            "file": "navigation_service.py",
                            "line": 0,
                            "recommendation": f"Route '{item_route}' must start with a leading slash '/'.",
                            "auto_fix": False
                        })
                    else:
                        # Extract the path part (before query parameters)
                        path_part = item_route.split("?")[0]
                        # Reject uppercase letters in paths (routes should be lowercase)
                        if any(char.isupper() for char in path_part):
                            warnings.append({
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "module": sec_id,
                                "menu": item.get("label", item_id),
                                "route": item_route,
                                "source": "navigation_service.py",
                                "file": "navigation_service.py",
                                "line": 0,
                                "recommendation": f"Route path '{path_part}' contains uppercase letters. Use lowercase only.",
                                "auto_fix": False
                            })

        return warnings
