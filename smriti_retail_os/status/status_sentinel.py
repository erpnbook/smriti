# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/status/status_sentinel.py
# @description: Core execution engine and CLI for the SMRITI Status Sentinel (S³).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import argparse
import datetime
import json
import logging
import os
import sys

# Add apps path to sys.path to enable imports without installing package
status_dir = os.path.dirname(os.path.abspath(__file__))
smriti_module_dir = os.path.dirname(status_dir)
smriti_app_dir = os.path.dirname(smriti_module_dir)
apps_dir = os.path.dirname(smriti_app_dir)
bench_root = os.path.dirname(apps_dir)

if apps_dir not in sys.path:
    sys.path.insert(0, apps_dir)

from smriti_retail_os.status.registry import StatusSentinelRegistry
from smriti_retail_os.status.providers.version import VersionProvider
from smriti_retail_os.status.providers.maintenance import MaintenanceProvider
from smriti_retail_os.status.providers.migration import MigrationProvider
from smriti_retail_os.status.provider import (
    PROVIDER_VERSION, PROVIDER_MAINTENANCE, PROVIDER_MIGRATION, PROVIDER_READONLY
)


def setup_logging():
    """
    Sets up logging to write to bench_root/logs/status_sentinel.log.
    """
    log_dir = os.path.join(bench_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "status_sentinel.log")

    logger = logging.getLogger("status_sentinel")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def resolve_site(site_arg, logger):
    """
    Resolves the active site name from arg, environment, currentsite.txt, or default.
    """
    if site_arg:
        logger.info("Using site from command line: %s", site_arg)
        return site_arg

    env_site = os.environ.get("SMRITI_SITE") or os.environ.get("FRAPPE_SITE")
    if env_site:
        logger.info("Using site from environment: %s", env_site)
        return env_site

    current_site_file = os.path.join(bench_root, "sites", "currentsite.txt")
    if os.path.exists(current_site_file):
        try:
            with open(current_site_file, "r", encoding="utf-8") as f:
                site = f.read().strip()
                if site:
                    logger.info("Using site from currentsite.txt: %s", site)
                    return site
        except Exception as e:
            logger.warning("Could not read currentsite.txt: %s", str(e))

    logger.info("Falling back to default site: smriti_retail")
    return "smriti_retail"


def write_status_atomically(output_path, status_data, logger):
    """
    Writes the status JSON payload atomically using a temp file, flush, fsync, and rename.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    temp_path = output_path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename
        if os.path.exists(output_path):
            os.replace(temp_path, output_path)
        else:
            os.rename(temp_path, output_path)
        logger.info("Wrote status telemetry atomically to: %s", output_path)
    except Exception as e:
        logger.error("Failed to write status file: %s", str(e), exc_info=True)
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise e


def resolve_system_status(provider_results):
    """
    Determines overall system status based on deterministic priority precedence:
    Migration (Highest) > Maintenance > ReadOnly > Online (Lowest).
    """
    # Check migration
    migration_res = provider_results.get(PROVIDER_MIGRATION, {})
    migration_data = migration_res.get("data", {})
    if migration_data.get("active"):
        return "migration"

    # Check maintenance
    maintenance_res = provider_results.get(PROVIDER_MAINTENANCE, {})
    maintenance_data = maintenance_res.get("data", {})
    if maintenance_data.get("active"):
        return "maintenance"

    # Check read-only
    readonly_res = provider_results.get(PROVIDER_READONLY, {})
    readonly_data = readonly_res.get("data", {})
    if readonly_data.get("active"):
        return "readonly"

    return "online"


def run(site=None):
    """
    CLI execution entry point.
    """
    logger = setup_logging()
    logger.info("--- SMRITI Status Sentinel (S³) Started ---")

    parser = argparse.ArgumentParser(description="SMRITI Status Sentinel (S³)")
    parser.add_argument("--site", help="Frappe site name to check")
    args, unknown = parser.parse_known_args()

    # If run as function import (e.g. from sync_assets.py), prioritize parameter
    active_site = resolve_site(site or args.site, logger)
    site_path = os.path.join(bench_root, "sites", active_site)

    if not os.path.exists(site_path):
        logger.error("Site path does not exist: %s", site_path)
        sys.exit(1)

    # Initialize Registry & Register standard providers
    registry = StatusSentinelRegistry(logger)
    registry.register(VersionProvider())
    registry.register(MaintenanceProvider())
    registry.register(MigrationProvider())

    # Dynamically register Read-only mock provider to support standard priority checks
    class ReadOnlyProvider(object):
        @property
        def name(self): return PROVIDER_READONLY
        def get_status(self, s_path):
            ro_lock = os.path.join(s_path, "readonly.lock")
            active = os.path.exists(ro_lock)
            reason = None
            if active:
                try:
                    with open(ro_lock, "r", encoding="utf-8") as f:
                        data = json.loads(f.read().strip())
                        reason = data.get("reason", "License Update")
                except Exception:
                    reason = "License Update"
            return {
                "provider": self.name,
                "status": "ok",
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "data": {"active": active, "reason": reason}
            }
    # Register the class directly by wrapping it to conform to base class check
    from smriti_retail_os.status.provider import BaseStatusProvider
    class WrappedReadOnly(BaseStatusProvider):
        @property
        def name(self): return PROVIDER_READONLY
        def get_status(self, s_path): return ReadOnlyProvider().get_status(s_path)

    registry.register(WrappedReadOnly())

    # Execute all providers
    provider_results = registry.execute_all(site_path)

    # Compute overall status
    system_status = resolve_system_status(provider_results)
    logger.info("Resolved system status: %s", system_status)

    # Compute summary metrics
    summary = {
        "providers_total": len(provider_results),
        "healthy": 0,
        "warning": 0,
        "error": 0
    }
    for res in provider_results.values():
        status = res.get("status", "ok")
        if status == "ok":
            summary["healthy"] += 1
        elif status == "warning":
            summary["warning"] += 1
        elif status == "error":
            summary["error"] += 1

    # Construct final payload
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "generator": "SMRITI Status Sentinel",
        "generator_version": "1.0",
        "status_priority": [
            "migration",
            "maintenance",
            "readonly",
            "online"
        ],
        "system_status": system_status,
        "summary": summary,
        "providers": provider_results
    }

    # Write status_sentinel.json output
    output_file = os.path.join(bench_root, "sites", "assets", "smriti_retail_os", "status", "status_sentinel.json")
    try:
        write_status_atomically(output_file, payload, logger)
    except Exception as e:
        logger.error("S³ execution warning: Failed to write telemetry output: %s", str(e))

    logger.info("--- SMRITI Status Sentinel (S³) Execution Complete ---")


if __name__ == "__main__":
    run()
