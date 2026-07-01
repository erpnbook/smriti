# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/icon_rule.py
# @description: Validator rule checking for missing icons.
# @author: Jawahar R. Mallah
#

from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class IconRule(BaseValidator):
    rule_id = "NAV-004"
    severity = "MEDIUM"
    title = "Missing Icon Definitions"

    def validate(self, nav_config):
        warnings = []
        if not nav_config or "sections" not in nav_config:
            return warnings

        # Define the set of registered icons (matching SMRITI's icon mapping in JS sidebar)
        REGISTERED_ICONS = {
            "masters", "cge", "psv", "sales", "purchase", "inventory",
            "barcode_studio", "finance", "reports", "administration",
            "help_desk", "ai_hub", "commercial"
        }

        for sec in nav_config["sections"]:
            sec_id = sec.get("id")
            if not sec_id:
                continue

            # Check if this section ID has a mapped SVG icon
            if sec_id not in REGISTERED_ICONS:
                warnings.append({
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "module": sec_id,
                    "menu": sec.get("label", sec_id),
                    "route": "",
                    "source": "navigation_service.py",
                    "file": "navigation_service.py",
                    "line": 0,
                    "recommendation": f"Section '{sec_id}' does not have a registered SVG icon mapping in the sidebar registry. Render falls back to default circle icon.",
                    "auto_fix": False
                })

        return warnings
