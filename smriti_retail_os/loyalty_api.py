# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/loyalty_api.py
# @description: Backend API for SMRITI Loyalty and Promotions module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, cint, today
from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points

@frappe.whitelist()
def get_loyalty_details(customer):
    """
    Safely retrieves loyalty program and points details for a customer.
    If the customer is not enrolled, returns standard zeroed-out values gracefully.
    """
    if not customer:
        return {
            "enrolled": False,
            "loyalty_program": None,
            "loyalty_points": 0,
            "conversion_factor": 0.0,
            "redeem_amount": 0.0,
            "tier_name": None
        }
        
    try:
        # Check if customer has an enrolled loyalty program
        loyalty_program = frappe.db.get_value("Customer", customer, "loyalty_program")
        if not loyalty_program:
            return {
                "enrolled": False,
                "loyalty_program": None,
                "loyalty_points": 0,
                "conversion_factor": 0.0,
                "redeem_amount": 0.0,
                "tier_name": None
            }
            
        # Get details with points
        lp = get_loyalty_program_details_with_points(customer, silent=True)
        if not lp or not lp.get("loyalty_program"):
            return {
                "enrolled": False,
                "loyalty_program": None,
                "loyalty_points": 0,
                "conversion_factor": 0.0,
                "redeem_amount": 0.0,
                "tier_name": None
            }
            
        conversion_factor = flt(lp.get("conversion_factor") or 0.0)
        # H-14: Guard against negative loyalty points — negative redeem_amount INCREASES invoice total
        points = max(0, cint(lp.get("loyalty_points") or 0))
        redeem_amount = max(0.0, flt(points * conversion_factor))

        return {
            "enrolled": True,
            "loyalty_program": lp.get("loyalty_program"),
            "loyalty_points": points,
            "conversion_factor": conversion_factor,
            "redeem_amount": redeem_amount,
            "tier_name": lp.get("tier_name") or "Regular"
        }
    except Exception as e:
        frappe.log_error(f"SMRITI Loyalty API Error for Customer {customer}: {str(e)}")
        return {
            "enrolled": False,
            "loyalty_program": None,
            "loyalty_points": 0,
            "conversion_factor": 0.0,
            "redeem_amount": 0.0,
            "tier_name": None,
            "error": str(e)
        }

@frappe.whitelist()
def get_loyalty_schemes():
    """
    Returns a list of all active Loyalty Programs for management display.
    """
    programs = frappe.get_all(
        "Loyalty Program",
        fields=["name", "loyalty_program_name", "conversion_factor", "auto_opt_in", "from_date", "to_date"],
        order_by="name asc"
    )
    
    # Enrich with collection details
    for p in programs:
        p["collection_rules"] = frappe.get_all(
            "Loyalty Program Collection",
            filters={"parent": p.name},
            fields=["tier_name", "min_spent", "collection_factor"]
        )
    return programs

@frappe.whitelist()
def save_loyalty_scheme(doc_name=None, loyalty_program_name=None, conversion_factor=1.0, auto_opt_in=1, min_spent=0, collection_factor=1.0, tier_name="Regular"):
    """
    Creates or updates a standard Loyalty Program document.
    Ensures a default expense account and cost center are set to prevent posting issues.
    """
    if not loyalty_program_name:
        frappe.throw(_("Loyalty Program Name is required."))
        
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    
    # M-11: Prefer a Loyalty-named expense account; arbitrary Expense account picks COGS/Rent etc.
    expense_account = (
        frappe.db.get_value(
            "Account",
            {"account_name": ["like", "%Loyalty%"], "root_type": "Expense", "company": company, "is_group": 0},
            "name"
        )
        or frappe.db.get_value(
            "Account",
            {"root_type": "Expense", "company": company, "is_group": 0},
            "name",
            order_by="account_name asc"
        )
        or frappe.db.get_value(
            "Account",
            {"account_type": "Expense Account", "company": company},
            "name"
        )
    )
    
    cost_center = frappe.db.get_value(
        "Cost Center", 
        {"company": company, "is_group": 0}, 
        "name"
    )
    
    if not expense_account or not cost_center:
        frappe.throw(_("Please ensure a valid Expense Account and Cost Center exist for Company: {0}").format(company))
        
    if doc_name and frappe.db.exists("Loyalty Program", doc_name):
        doc = frappe.get_doc("Loyalty Program", doc_name)
    else:
        doc = frappe.new_doc("Loyalty Program")
        doc.from_date = today()
        
    doc.loyalty_program_name = loyalty_program_name
    doc.loyalty_program_type = "Single Tier Program"
    doc.conversion_factor = flt(conversion_factor)
    doc.auto_opt_in = cint(auto_opt_in)
    doc.company = company
    doc.expense_account = expense_account
    doc.cost_center = cost_center
    
    # Force single default rule matching SMRITI collection factors
    doc.collection_rules = []
    doc.append("collection_rules", {
        "tier_name": tier_name or "Regular",
        "min_spent": flt(min_spent) or 0.0,
        "collection_factor": flt(collection_factor) or 1.0
    })
    
    # reviewed-ignore-permissions: bypass for whitelisted api endpoint
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "success": True,
        "name": doc.name,
        "message": _("Loyalty Scheme '{0}' saved successfully.").format(loyalty_program_name)
    }

@frappe.whitelist()
def enroll_customer(customer, program_name):
    """
    Enrolls a customer into a loyalty program.
    M-12: Restricted to Store Manager or Administrator — Cashiers must NOT be able
    to change any customer's loyalty program (financial control requirement).
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()

    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} not found.").format(customer))

    if program_name and not frappe.db.exists("Loyalty Program", program_name):
        frappe.throw(_("Loyalty Program {0} not found.").format(program_name))

    frappe.db.set_value("Customer", customer, "loyalty_program", program_name)
    frappe.db.commit()

    return {
        "success": True,
        "message": _("Customer '{0}' enrolled in Loyalty Program '{1}' successfully.").format(customer, program_name)
    }
