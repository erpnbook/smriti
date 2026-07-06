# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/providers/maintenance.py
# @description: Maintenance status provider checking for maintenance.lock.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import json
import os
from smriti_retail_os.status.provider import BaseStatusProvider, PROVIDER_MAINTENANCE


class MaintenanceProvider(BaseStatusProvider):
    """
    Checks for the presence of maintenance.lock JSON file in the site directory.
    Degrades gracefully if file is corrupt.
    """

    @property
    def name(self):
        return PROVIDER_MAINTENANCE

    def get_status(self, site_path):
        lock_path = os.path.join(site_path, "maintenance.lock")
        active = False
        reason = None
        started_at = None
        initiated_by = None
        status = "ok"
        provider_data = {}

        if os.path.exists(lock_path):
            active = True
            try:
                with open(lock_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        reason = data.get("reason", "Scheduled Update")
                        started_at = data.get("started_at")
                        initiated_by = data.get("initiated_by")
                    else:
                        reason = "Scheduled Update (Empty Lock File)"
            except Exception as e:
                # Corruption handling: degrade gracefully by treating maintenance as active
                status = "warning"
                reason = "Scheduled Update (Corrupt Lock File)"
                provider_data["corruption_error"] = str(e)

        provider_data.update({
            "active": active,
            "reason": reason,
            "started_at": started_at,
            "initiated_by": initiated_by
        })

        return {
            "provider": self.name,
            "status": status,
            "updated_at": self._get_utc_timestamp(),
            "data": provider_data
        }
