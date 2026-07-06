# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/provider.py
# @description: Base Status Provider contract interface.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import datetime

# Standard Provider Name Constants
PROVIDER_VERSION = "version"
PROVIDER_MAINTENANCE = "maintenance"
PROVIDER_MIGRATION = "migration"
PROVIDER_READONLY = "readonly"



class BaseStatusProvider(object):
    """
    Base contract for all Status Sentinel telemetry providers.
    Every status provider must inherit from this class and implement get_status().
    """

    @property
    def name(self):
        """
        The unique string identifier for the provider (e.g. 'version', 'maintenance').
        """
        raise NotImplementedError("Provider must define a name attribute.")

    def get_status(self, site_path):
        """
        Executes telemetry status checking and returns a standardized response dict.

        :param site_path: Absolute path to the Frappe site directory (e.g. sites/smriti_retail).
        :return: Standardized dict contract:
                 {
                     "provider": str,
                     "status": "ok" | "warning" | "error",
                     "updated_at": str (ISO-8601 UTC format),
                     "data": dict
                 }
        """
        raise NotImplementedError("Provider must implement get_status(site_path)")

    def _get_utc_timestamp(self):
        """
        Helper method returning current UTC timestamp in ISO-8601 format.
        """
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
