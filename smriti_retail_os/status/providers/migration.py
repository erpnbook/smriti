# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/providers/migration.py
# @description: Migration status provider checking for migration.lock.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import json
import os
from smriti_retail_os.status.provider import BaseStatusProvider, PROVIDER_MIGRATION


class MigrationProvider(BaseStatusProvider):
    """
    Checks for the presence of migration.lock JSON file in the site directory.
    Degrades gracefully if file is corrupt.
    """

    @property
    def name(self):
        return PROVIDER_MIGRATION

    def get_status(self, site_path):
        lock_path = os.path.join(site_path, "migration.lock")
        active = False
        reason = None
        started_at = None
        current_step = None
        progress_pct = 0
        status = "ok"
        provider_data = {}

        if os.path.exists(lock_path):
            active = True
            try:
                with open(lock_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        reason = data.get("reason", "Database Schema Migrations")
                        started_at = data.get("started_at")
                        current_step = data.get("current_step", "Updating schemas...")
                        progress_pct = data.get("progress_pct", 0)
                        try:
                            progress_pct = int(progress_pct)
                        except (ValueError, TypeError):
                            progress_pct = 0
                    else:
                        reason = "Schema Migrations (Empty Lock File)"
                        current_step = "Updating schemas..."
            except Exception as e:
                # Corruption handling: degrade gracefully by treating migration as active
                status = "warning"
                reason = "Schema Migrations (Corrupt Lock File)"
                current_step = "Updating schemas..."
                progress_pct = 0
                provider_data["corruption_error"] = str(e)

        provider_data.update({
            "active": active,
            "reason": reason,
            "started_at": started_at,
            "current_step": current_step,
            "progress_pct": progress_pct
        })

        return {
            "provider": self.name,
            "status": status,
            "updated_at": self._get_utc_timestamp(),
            "data": provider_data
        }
