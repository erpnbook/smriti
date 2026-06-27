# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/providers/version.py
# @description: Version status provider.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import os
import re
from smriti_retail_os.status.provider import BaseStatusProvider, PROVIDER_VERSION


class VersionProvider(BaseStatusProvider):
    """
    Status provider that parses version numbers of SMRITI, Frappe, and ERPNext
    directly from files without loading the packages.
    """

    @property
    def name(self):
        return PROVIDER_VERSION

    def get_status(self, site_path):
        # Resolve the bench apps path
        # __file__ is apps/smriti_retail_os/smriti_retail_os/status/providers/version.py
        providers_dir = os.path.dirname(os.path.abspath(__file__))
        status_dir = os.path.dirname(providers_dir)
        smriti_module_dir = os.path.dirname(status_dir)
        smriti_app_dir = os.path.dirname(smriti_module_dir)
        apps_dir = os.path.dirname(smriti_app_dir)

        # Regex for __version__ = "X.Y.Z"
        version_re = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)

        versions = {
            "smriti_retail_os": "unknown",
            "frappe": "unknown",
            "erpnext": "unknown"
        }

        # 1. Parse SMRITI version
        smriti_init = os.path.join(smriti_module_dir, "__init__.py")
        if os.path.exists(smriti_init):
            try:
                with open(smriti_init, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = version_re.search(content)
                    if match:
                        versions["smriti_retail_os"] = match.group(1)
            except Exception:
                pass

        # 2. Parse Frappe version
        frappe_init = os.path.join(apps_dir, "frappe", "frappe", "__init__.py")
        if os.path.exists(frappe_init):
            try:
                with open(frappe_init, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = version_re.search(content)
                    if match:
                        versions["frappe"] = match.group(1)
            except Exception:
                pass

        # 3. Parse ERPNext version
        erpnext_init = os.path.join(apps_dir, "erpnext", "erpnext", "__init__.py")
        if os.path.exists(erpnext_init):
            try:
                with open(erpnext_init, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = version_re.search(content)
                    if match:
                        versions["erpnext"] = match.group(1)
            except Exception:
                pass

        return {
            "provider": self.name,
            "status": "ok",
            "updated_at": self._get_utc_timestamp(),
            "data": {
                "smriti_retail_os": versions["smriti_retail_os"],
                "frappe": versions["frappe"],
                "erpnext": versions["erpnext"],
                "framework_version": "v1.0"
            }
        }
