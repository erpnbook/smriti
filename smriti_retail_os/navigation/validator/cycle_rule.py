# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/cycle_rule.py
# @description: Validator rule checking for parent category orphans and loops.
# @author: Jawahar R. Mallah
#

from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class CycleRule(BaseValidator):
    rule_id = "NAV-002"
    severity = "CRITICAL"
    title = "Circular Category Hierarchy"

    def validate(self, nav_config):
        warnings = []
        if not nav_config or "sections" not in nav_config:
            return warnings

        # In a standard two-level sidebar, check if any section id matches its sub-item ids (which would break tree resolver logic)
        sec_ids = {sec.get("id") for sec in nav_config["sections"]}

        for sec in nav_config["sections"]:
            sec_id = sec.get("id")
            for item in sec.get("items", []):
                item_id = item.get("id")
                # 1. Orphan check: parent section ID must exist in target sections
                if not sec_id or sec_id not in sec_ids:
                    warnings.append({
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "module": sec_id,
                        "menu": item.get("label", item_id),
                        "route": item.get("route"),
                        "source": "navigation_service.py",
                        "file": "navigation_service.py",
                        "line": 0,
                        "recommendation": f"Item '{item_id}' references non-existent parent section '{sec_id}'. Ensure sections are declared.",
                        "auto_fix": False
                    })

                # 2. Cycle check: item ID matches parent section ID
                if item_id == sec_id:
                    warnings.append({
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "module": sec_id,
                        "menu": item.get("label", item_id),
                        "route": item.get("route"),
                        "source": "navigation_service.py",
                        "file": "navigation_service.py",
                        "line": 0,
                        "recommendation": f"Circular loop detected: category group ID matches sub-item ID '{item_id}'.",
                        "auto_fix": False
                    })

        return warnings
