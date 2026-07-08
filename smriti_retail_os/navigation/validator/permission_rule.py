# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/permission_rule.py
# @description: Validator rule checking for role mismatches and guest auth loopholes in www controllers.
# @author: Jawahar R. Mallah
#

import os
import re
from smriti_retail_os.navigation.validator.base_validator import BaseValidator

class PermissionRule(BaseValidator):
    rule_id = "NAV-005"
    severity = "HIGH"
    title = "Permission & Auth Mismatches"

    def validate(self, nav_config):
        import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
        warnings = []
        
        # 1. Verify Role existences for custom SMRITI roles
        SMRITI_ROLES = ["SMRITI Cashier", "SMRITI Store Manager", "SMRITI Auditor", "System Manager"]
        for role in SMRITI_ROLES:
            if not smriti.db.exists("Role", role):
                warnings.append({
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "module": "Roles",
                    "menu": "Role Verification",
                    "route": "",
                    "source": "database",
                    "file": "Role",
                    "line": 0,
                    "recommendation": f"SMRITI Role '{role}' does not exist in the Frappe active roles table.",
                    "auto_fix": False
                })

        # 2. Check www/ python controllers for missing guest authentication checks
        app_path = frappe.get_app_path("smriti_retail_os")
        www_dir = os.path.join(app_path, "www")

        # Whitelisted guest controllers (explicitly allowed for unauthenticated access)
        GUEST_WHITELIST = {
            "smriti-login.py",
            "verify-certificate.py",
            "trial.py",
            "404.py",
            "403.py"
        }

        if os.path.exists(www_dir):
            for filename in os.listdir(www_dir):
                if filename.endswith(".py") and filename not in GUEST_WHITELIST:
                    file_path = os.path.join(www_dir, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Look for auth checks (e.g. frappe.session.user == "Guest" or raise/Redirect)
                    has_auth_check = re.search(r'("Guest"|\'Guest\')', content) is not None
                    
                    if not has_auth_check:
                        warnings.append({
                            "rule_id": self.rule_id,
                            "severity": self.severity,
                            "module": "Authentication",
                            "menu": filename.replace(".py", ""),
                            "route": f"/{filename.replace('.py', '')}",
                            "source": filename,
                            "file": file_path,
                            "line": 1,
                            "recommendation": f"Page controller '{filename}' does not contain an explicit Guest session check. Add auth protection.",
                            "auto_fix": False
                        })

        return warnings
