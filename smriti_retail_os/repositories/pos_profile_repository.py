# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/repositories/pos_profile_repository.py
# @desc:    Data Access Repository Layer for SMRITI POS Profile operations.
#
# @author:  Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 2.0.0  — Migrated to smriti.core.platform (SMRITI Core Framework v1.0)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Migration note:
#   v1.x called frappe.* directly.
#   v2.0 routes all platform calls through smriti_retail_os.core.platform.
#   No frappe.* imports remain in this file.
#

from smriti_retail_os.core.platform import documents as _documents
from smriti_retail_os.core.platform import db as _db


def get_profiles():
    """
    Retrieves all POS Profiles with basic descriptive fields.
    """
    return _documents.get_all(
        "POSProfile",
        fields=["name", "company", "warehouse", "disabled", "modified_by", "modified"]
    )


def get_profile_by_name(name: str):
    """
    Retrieves a single POS Profile document as a dictionary,
    including payment modes and cashier user mappings.
    Returns None if the profile does not exist.
    """
    if not _db.exists("POSProfile", name):
        return None
    doc = _documents.get("POSProfile", name)
    return doc.as_dict()


def save_profile(data: dict):
    """
    Creates or updates a POS Profile document and commits the transaction.
    Returns the document name on success.
    """
    name = data.get("name")

    if name and _db.exists("POSProfile", name):
        doc = _documents.get("POSProfile", name)
    else:
        doc = _documents.new("POSProfile")
        doc.name = name

    # Update primary fields
    doc.update({
        "company":               data.get("company"),
        "warehouse":             data.get("warehouse"),
        "selling_price_list":    data.get("selling_price_list"),
        "currency":              data.get("currency") or "INR",
        "disabled":              data.get("disabled") or 0,
        "write_off_account":     data.get("write_off_account"),
        "write_off_cost_center": data.get("write_off_cost_center"),
    })

    # Sync payments child table
    doc.set("payments", [])
    for p in data.get("payments", []):
        doc.append("payments", {
            "mode_of_payment": p.get("mode_of_payment"),
            "default_account": p.get("default_account"),
            "default":         p.get("default") or 0,
        })

    # Sync applicable_for_users child table
    doc.set("applicable_for_users", [])
    for u in data.get("applicable_for_users", []):
        doc.append("applicable_for_users", {"user": u.get("user")})

    doc.save(ignore_permissions=True)
    _db.commit()
    return doc.name


def disable_profile(name: str) -> bool:
    """
    Soft-deletes a POS Profile by setting disabled=1.
    Preserves audit trail.
    """
    _db.set("POSProfile", name, "disabled", 1)
    _db.commit()
    return True
