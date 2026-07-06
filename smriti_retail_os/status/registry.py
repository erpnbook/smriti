# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/registry.py
# @description: Registry manager for registering and executing status providers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import datetime
import logging
from smriti_retail_os.status.provider import BaseStatusProvider


class StatusSentinelRegistry(object):
    """
    Registry for status providers. Manages execution and aggregates results
    under strict isolation guarantees.
    """

    def __init__(self, logger=None):
        self.providers = []
        self.logger = logger or logging.getLogger("status_sentinel")

    def register(self, provider):
        """
        Registers a status provider.
        """
        if not isinstance(provider, BaseStatusProvider):
            raise TypeError("Provider must inherit from BaseStatusProvider")
        
        # Avoid duplicate registration
        if any(p.name == provider.name for p in self.providers):
            self.logger.warning("Provider '%s' already registered. Overwriting.", provider.name)
            self.providers = [p for p in self.providers if p.name != provider.name]

        self.providers.append(provider)
        self.logger.debug("Registered status provider: %s", provider.name)

    def execute_all(self, site_path):
        """
        Executes all registered providers and aggregates their results.
        Enforces Rule 5 (Provider Isolation) — failures in individual providers
        will be captured and represented as error statuses, never crashing execution.

        :param site_path: Path to the current active site.
        :return: Dict of provider results keyed by provider name.
        """
        results = {}
        for provider in self.providers:
            try:
                self.logger.info("Executing status provider: %s", provider.name)
                res = provider.get_status(site_path)
                
                # Validate response format
                if not isinstance(res, dict) or "provider" not in res or "status" not in res:
                    raise ValueError("Provider return value does not conform to standardized contract.")
                
                results[provider.name] = res
            except Exception as e:
                # Rule 5: Provider Isolation
                self.logger.error("Provider '%s' failed during execution: %s", provider.name, str(e), exc_info=True)
                results[provider.name] = {
                    "provider": provider.name,
                    "status": "error",
                    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                    "data": {
                        "error": str(e)
                    }
                }
        return results
