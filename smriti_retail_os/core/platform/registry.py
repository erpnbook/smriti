# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/registry.py
# @desc:    SMRITI Platform Registry — configuration-driven document model mapper.
#           Maps SMRITI business model names (e.g. "Purchase", "Product") to the
#           underlying platform DocType names (e.g. "Purchase Order", "Item").
#
#           The mapping lives in document_map.yaml — NOT in Python code.
#           To migrate to a different platform or rename a DocType, update
#           document_map.yaml only. No Python service file changes required.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import os
import yaml

_REGISTRY = None
_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "document_map.yaml")


def _load_registry() -> dict:
    """Loads and caches the YAML document registry on first access."""
    global _REGISTRY
    if _REGISTRY is None:
        if not os.path.exists(_REGISTRY_PATH):
            raise FileNotFoundError(
                f"SMRITI Platform Registry not found at: {_REGISTRY_PATH}\n"
                "Ensure core/platform/document_map.yaml exists."
            )
        with open(_REGISTRY_PATH, "r", encoding="utf-8") as f:
            _REGISTRY = yaml.safe_load(f) or {}
    return _REGISTRY


def resolve(smriti_model: str) -> str:
    """
    Resolves a SMRITI business model name to its underlying platform DocType.

    Usage:
        from smriti_retail_os.core.platform.registry import resolve

        resolve("Purchase")   # → "Purchase Order"
        resolve("Product")    # → "Item"
        resolve("Customer")   # → "Customer"
    """
    registry = _load_registry()
    entry = registry.get(smriti_model)
    if entry and entry.get("platform"):
        return entry.get("platform")

    # If model is already a registered platform target (e.g. "Item", "Customer", "Purchase Order")
    for k, v in registry.items():
        if isinstance(v, dict) and v.get("platform") == smriti_model:
            return smriti_model

    # Check if smriti_model is a valid DocType in ERPNext / Frappe database
    import frappe
    try:
        if frappe.db.exists("DocType", smriti_model):
            return smriti_model
    except Exception:
        pass

    raise KeyError(
        f"SMRITI Platform Registry: unknown model '{smriti_model}'.\n"
        f"Register it in core/platform/document_map.yaml."
    )


def resolve_or_passthrough(model_name: str) -> str:
    """
    Resolves a SMRITI model name if registered; returns the name unchanged if not.
    Use ONLY in legacy migration paths where the caller may pass a raw DocType name.
    New code must always use resolve().
    """
    try:
        return resolve(model_name)
    except KeyError:
        return model_name


def list_registered_models() -> list:
    """Returns all registered SMRITI model names (for diagnostics / guard tooling)."""
    return list(_load_registry().keys())


def get_description(smriti_model: str) -> str:
    """Returns the human-readable description of a registered SMRITI model."""
    registry = _load_registry()
    entry = registry.get(smriti_model, {})
    return entry.get("description", "No description registered.")


def reload():
    """Forces a registry reload from disk (use after modifying document_map.yaml)."""
    global _REGISTRY
    _REGISTRY = None
    _load_registry()
