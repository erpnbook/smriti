# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/cache.py
# @desc:    SMRITI Platform Cache Adapter.
#           Wraps frappe.cache() (Redis) behind a clean SMRITI API.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   from smriti_retail_os.core.platform import cache
#
#   cache.set("smriti_dashboard_summary", data, ttl=300)
#   data = cache.get("smriti_dashboard_summary")
#   cache.delete("smriti_dashboard_summary")
#

_DEFAULT_TTL = 300  # 5 minutes


def get(key: str):
    """
    Retrieve a value from the Redis cache.

    Args:
        key (str): Cache key

    Returns:
        Cached value or None if expired / not found

    Example:
        summary = cache.get("smriti_dashboard_summary")
        if not summary:
            summary = _build_summary()
            cache.set("smriti_dashboard_summary", summary)
    """
    import frappe
    return frappe.cache().get_value(key)


def set(key: str, value, ttl: int = _DEFAULT_TTL):
    """
    Store a value in the Redis cache with a TTL.

    Args:
        key (str): Cache key (use a namespaced prefix, e.g. "smriti_*")
        value: Serializable Python value to cache
        ttl (int): Time-to-live in seconds (default: 300)

    Example:
        cache.set("smriti_pos_profiles", profiles, ttl=600)
    """
    import frappe
    frappe.cache().set_value(key, value, expires_in_sec=ttl)


def delete(key: str):
    """
    Remove a specific key from the cache.

    Args:
        key (str): Cache key to delete

    Example:
        cache.delete("smriti_dashboard_summary")
    """
    import frappe
    frappe.cache().delete_value(key)


def get_or_set(key: str, builder_fn, ttl: int = _DEFAULT_TTL):
    """
    Cache-aside pattern: return cached value or compute and store it.

    Args:
        key (str): Cache key
        builder_fn (callable): Zero-argument function that builds the value
        ttl (int): Time-to-live in seconds

    Returns:
        Cached or freshly computed value

    Example:
        profiles = cache.get_or_set(
            "smriti_pos_profiles",
            lambda: _fetch_pos_profiles_from_db(),
            ttl=600
        )
    """
    value = get(key)
    if value is None:
        value = builder_fn()
        if value is not None:
            set(key, value, ttl=ttl)
    return value


def flush_prefix(prefix: str):
    """
    Delete all cache keys that start with the given prefix.
    Use when a model update invalidates multiple cached summaries.

    Args:
        prefix (str): Key prefix to flush, e.g. "smriti_dashboard"
    """
    import frappe
    frappe.cache().delete_keys(prefix)


# Explicit method aliases for frappe.cache() compatibility
get_value = get
set_value = set
delete_value = delete

