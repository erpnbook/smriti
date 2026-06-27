# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/repositories/pos_profile_repository.py
# @description: Repository layer for ERPNext standard POS Profile database operations.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.8.6
# @sprint: 3C — POS Profile Custom Manager
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe

def get_profiles():
    """
    Retrieves all POS Profiles with basic descriptive fields.
    """
    return frappe.get_all(
        "POS Profile",
        fields=["name", "company", "warehouse", "disabled", "modified_by", "modified"]
    )

def get_profile_by_name(name):
    """
    Retrieves a single POS Profile document as a dictionary, including payment modes
    and cashier user mappings.
    """
    if not frappe.db.exists("POS Profile", name):
        return None
    doc = frappe.get_doc("POS Profile", name)
    return doc.as_dict()

def save_profile(data):
    """
    Creates or updates a POS Profile document and commits the transaction.
    """
    name = data.get("name")
    
    if name and frappe.db.exists("POS Profile", name):
        doc = frappe.get_doc("POS Profile", name)
    else:
        doc = frappe.new_doc("POS Profile")
        doc.name = name

    # Update primary fields
    doc.update({
        "company": data.get("company"),
        "warehouse": data.get("warehouse"),
        "selling_price_list": data.get("selling_price_list"),
        "currency": data.get("currency") or "INR",
        "disabled": data.get("disabled") or 0,
        "write_off_account": data.get("write_off_account"),
        "write_off_cost_center": data.get("write_off_cost_center")
    })

    # Sync payments child table
    doc.set("payments", [])
    for p in data.get("payments", []):
        doc.append("payments", {
            "mode_of_payment": p.get("mode_of_payment"),
            "default_account": p.get("default_account"),
            "default": p.get("default") or 0
        })

    # Sync applicable_for_users child table
    doc.set("applicable_for_users", [])
    for u in data.get("applicable_for_users", []):
        doc.append("applicable_for_users", {
            "user": u.get("user")
        })

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return doc.name

def disable_profile(name):
    """
    Defensively sets the disabled flag to 1 (soft delete) to preserve audit trails.
    """
    frappe.db.set_value("POS Profile", name, "disabled", 1)
    frappe.db.commit()
    return True
