# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/cge/api/cge_api.py
# @description: SMRITI CGE API — channel gross earnings endpoints.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/cge/api/cge_api.py
# @description: Whitelisted API endpoints for SMRITI Customer Growth Engine (CGE) POS operations and CGE Studio UI.
# @author: Antigravity AI
# @date: 2026-06-19
#

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, nowdate
import json

from smriti_retail_os.cge.service.cge_service import (
    validate_checkout_rules as service_validate_checkout_rules,
    get_offline_cache as service_get_offline_cache,
    CGEWalletLedger,
    get_active_wallet_balance
)

@frappe.whitelist()
def validate_checkout_rules(invoice_data):
    """
    POS Checkout calculation endpoint.
    """
    return service_validate_checkout_rules(invoice_data)

@frappe.whitelist()
def get_offline_cache():
    """
    Exposes serialized offline POS rules and campaigns.
    """
    return service_get_offline_cache()

@frappe.whitelist()
def get_wallet_ledger(customer=None, transaction_type=None, limit=50):
    """
    Queries SMRITI Wallet Ledger entries.
    Restricted to System Manager, SMRITI Store Manager, and SMRITI Auditor.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager", "SMRITI Auditor"]):
        frappe.throw(_("Not authorized to view Wallet Ledger logs."), frappe.PermissionError)

    filters = {}
    if customer:
        filters["customer"] = customer
    if transaction_type:
        filters["transaction_type"] = transaction_type
        
    return frappe.get_all("SMRITI Wallet Ledger",
        filters=filters,
        fields=[
            "name", "ledger_sequence", "customer", "wallet_type", 
            "transaction_type", "amount", "reference_invoice", 
            "is_reversal", "is_expired", "creation", "journal_entry",
            "remarks", "adjustment_reason_type"
        ],
        order_by="creation desc",
        limit=cint(limit) or 50
    )

@frappe.whitelist()
def post_wallet_adjustment(customer, wallet_type, transaction_type, amount, remarks, adjustment_reason_type, company=None):
    """
    Performs manual wallet adjustment (debit or credit).
    Restricted to SMRITI Store Manager or System Manager.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    
    if not customer:
        frappe.throw(_("Customer is required."))
    if not wallet_type:
        frappe.throw(_("Wallet Type is required."))
    if not transaction_type or transaction_type not in ["Debit", "Credit"]:
        frappe.throw(_("Transaction Type must be either Debit or Credit."))
    if flt(amount) <= 0:
        frappe.throw(_("Amount must be positive."))
    if not remarks:
        frappe.throw(_("Remarks/Reason is required for manual audit logs."))
    if not adjustment_reason_type:
        frappe.throw(_("Adjustment Reason Type is required for reporting classification."))
        
    # Get previous balance for audit log
    old_bal = get_active_wallet_balance(customer)
    
    ledger_doc = CGEWalletLedger.post_transaction(
        customer=customer,
        wallet_type=wallet_type,
        transaction_type=transaction_type,
        amount=flt(amount),
        company=company,
        remarks=remarks,
        adjustment_reason_type=adjustment_reason_type
    )
    
    new_bal = old_bal + (flt(amount) if transaction_type == "Credit" else -flt(amount))
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event(
        "Manual Wallet Adjustment",
        f"Manual adjustment posted by {frappe.session.user} for Customer: {customer}. "
        f"Type: {transaction_type}, Category: {adjustment_reason_type}, "
        f"Amount: ₹{amount}, Remarks: {remarks}. Balance: ₹{old_bal} -> ₹{new_bal}"
    )
    
    return {
        "success": True,
        "name": ledger_doc.name,
        "ledger_sequence": ledger_doc.ledger_sequence,
        "journal_entry": ledger_doc.journal_entry
    }

@frappe.whitelist()
def reverse_wallet_transaction(ledger_seq, reason):
    """
    Performs wallet transaction reversal.
    Restricted to SMRITI Store Manager or System Manager.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    
    if not ledger_seq:
        frappe.throw(_("Ledger sequence is required."))
    if not reason:
        frappe.throw(_("Reason for reversal is required."))
        
    # Find ledger_sequence name in SMRITI Wallet Ledger
    ledger_name = frappe.db.get_value("SMRITI Wallet Ledger", {"ledger_sequence": ledger_seq}, "name")
    if not ledger_name:
        if frappe.db.exists("SMRITI Wallet Ledger", ledger_seq):
            ledger_name = ledger_seq
        else:
            frappe.throw(_("Wallet Ledger entry {0} not found.").format(ledger_seq))
            
    orig_doc = frappe.get_doc("SMRITI Wallet Ledger", ledger_name)
    
    rev_doc = CGEWalletLedger.reverse_transaction(ledger_name, reason)
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event(
        "Manual Wallet Reversal",
        f"Wallet transaction reversal requested by {frappe.session.user} for Ledger ID: {ledger_seq} ({ledger_name}). "
        f"Customer: {orig_doc.customer}, Amount: ₹{orig_doc.amount}, Reversal Reason: {reason}."
    )
    
    return {
        "success": True,
        "name": rev_doc.name,
        "ledger_sequence": rev_doc.ledger_sequence,
        "journal_entry": rev_doc.journal_entry
    }

@frappe.whitelist()
def get_cge_liability_metrics():
    """
    Returns outstanding points liability, wallet liability, active campaign budget exposures, and dynamic warning thresholds.
    """
    roles = frappe.get_roles()
    if not any(r in roles for r in ["System Manager", "SMRITI Store Manager", "SMRITI Auditor"]):
        frappe.throw(_("Not authorized to view CGE liability metrics."), frappe.PermissionError)

    # 1. Loyalty points liability (sum of remaining points of all active unexpired entries)
    loyalty_liability = flt(frappe.db.sql("""
        select sum(remaining_points)
        from `tabLoyalty Point Entry`
        where expiry_date >= %s
    """, (nowdate()))[0][0])
    
    # 2. Wallet liability (total Credit - total Debit)
    credits = flt(frappe.db.sql("""
        select sum(amount)
        from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Credit' and is_expired = 0
          and (expiry_date is null or expiry_date >= %s)
    """, (nowdate()))[0][0])
    debits_res = frappe.db.sql("""
        select sum(amount) from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Debit'
    """)
    debits = flt(debits_res[0][0] if debits_res else 0)
    cashback_liability = max(0.0, credits - debits)
    
    # 3. Coupon campaign budget reserved (active campaigns)
    coupon_exposure_res = frappe.db.sql("""
        select sum(budget_reserved) from `tabSMRITI Coupon Campaign`
        where status = 'Active'
    """)
    coupon_exposure = flt(coupon_exposure_res[0][0] if coupon_exposure_res else 0)
    
    total_liability = loyalty_liability + cashback_liability + coupon_exposure
    
    # 4. Fetch thresholds from SMRITI CGE Settings
    settings = frappe.get_single("SMRITI CGE Settings")
    amber_threshold = flt(settings.amber_liability_threshold) or 100000.0
    red_threshold = flt(settings.red_liability_threshold) or 250000.0
    
    return {
        "loyalty_liability": loyalty_liability,
        "cashback_liability": cashback_liability,
        "coupon_exposure": coupon_exposure,
        "total_liability": total_liability,
        "amber_threshold": amber_threshold,
        "red_threshold": red_threshold
    }

@frappe.whitelist()
def get_dashboard_data():
    """Alias for get_cge_liability_metrics to support client CGE studio calls."""
    return get_cge_liability_metrics()

@frappe.whitelist()
def get_campaigns_with_utilization():
    """
    Returns campaigns with utilization calculations.
    """
    campaigns = frappe.get_all("SMRITI Coupon Campaign",
        fields=[
            "name", "campaign_name", "campaign_type", "start_date", "end_date",
            "budget_limit", "budget_reserved", "budget_consumed", "stop_on_limit", "status"
        ],
        order_by="creation desc"
    )
    for c in campaigns:
        limit = flt(c.budget_limit)
        consumed = flt(c.budget_consumed)
        reserved = flt(c.budget_reserved)
        c["utilization"] = ((consumed + reserved) / limit * 100.0) if limit > 0 else 0.0
        
    return campaigns

@frappe.whitelist()
def save_coupon_campaign(campaign_data):
    """
    Saves a SMRITI Coupon Campaign document.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    
    if isinstance(campaign_data, str):
        campaign_data = json.loads(campaign_data)
        
    name = campaign_data.get("name")
    if name and frappe.db.exists("SMRITI Coupon Campaign", name):
        doc = frappe.get_doc("SMRITI Coupon Campaign", name)
    else:
        doc = frappe.new_doc("SMRITI Coupon Campaign")
        
    for key, val in campaign_data.items():
        if key != "name":
            doc.set(key, val)
            
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def save_loyalty_rule(rule_data):
    """
    Saves a SMRITI Loyalty Rule document.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    
    if isinstance(rule_data, str):
        rule_data = json.loads(rule_data)
        
    name = rule_data.get("name")
    if name and frappe.db.exists("SMRITI Loyalty Rule", name):
        doc = frappe.get_doc("SMRITI Loyalty Rule", name)
    else:
        doc = frappe.new_doc("SMRITI Loyalty Rule")
        
    for key, val in rule_data.items():
        if key != "name":
            doc.set(key, val)
            
    doc.save(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def save_loyalty_tier(tier_data):
    """
    Saves a SMRITI Loyalty Tier document.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    
    if isinstance(tier_data, str):
        tier_data = json.loads(tier_data)
        
    name = tier_data.get("name")
    if name and frappe.db.exists("SMRITI Loyalty Tier", name):
        doc = frappe.get_doc("SMRITI Loyalty Tier", name)
    else:
        doc = frappe.new_doc("SMRITI Loyalty Tier")
        
    for key, val in tier_data.items():
        if key != "name":
            doc.set(key, val)
            
    doc.save(ignore_permissions=True)
    return doc.name


ALLOWED_CGE_DOCTYPES = [
    'SMRITI Benefit Instrument',
    'SMRITI Membership Tier',
    'SMRITI Loyalty Program',
    'SMRITI Campaign',
    'SMRITI Promotion Rule',
    'SMRITI Coupon Rule',
    'SMRITI Loyalty Rule',
    'SMRITI Benefit Wallet',
    'SMRITI Customer Benefit Profile',
    'SMRITI Benefit Resolution Policy',
    'SMRITI Benefit Liability Snapshot',
    'SMRITI Benefit Audit Log',
    'SMRITI Benefit Resolution Sequence Detail'
]

def check_cge_doctype(doctype):
    if doctype not in ALLOWED_CGE_DOCTYPES:
        frappe.throw(_("Access Denied: Invalid CGE DocType {0}.").format(doctype), frappe.PermissionError)

@frappe.whitelist()
def get_cge_generic_fields(doctype):
    """
    Returns field metadata for a CGE DocType.
    Restricted to manager/admin.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    check_cge_doctype(doctype)
    
    from smriti_retail_os.cge.service.cge_service import get_cge_generic_fields_meta
    return get_cge_generic_fields_meta(doctype)

@frappe.whitelist()
def get_cge_generic_list(doctype, filters=None, limit=100):
    """
    Queries records of a CGE DocType.
    Restricted to manager/admin.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    check_cge_doctype(doctype)
    
    if isinstance(filters, str):
        filters = json.loads(filters)
        
    meta = frappe.get_meta(doctype)
    fields = ["name"]
    for f in meta.fields:
        if not f.hidden and f.fieldtype not in ['Section Break', 'Column Break', 'Table', 'Code']:
            fields.append(f.fieldname)
            
    if "creation" not in fields:
        fields.append("creation")
        
    return frappe.get_all(doctype,
        filters=filters,
        fields=fields,
        order_by="modified desc" if "modified" in [f.fieldname for f in meta.fields] else "creation desc",
        limit=cint(limit) or 100
    )

@frappe.whitelist()
def get_cge_generic_doc(doctype, name):
    """
    Gets full document details including child tables.
    Restricted to manager/admin.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    check_cge_doctype(doctype)
    
    doc = frappe.get_doc(doctype, name)
    doc_dict = doc.as_dict()
    
    meta = frappe.get_meta(doctype)
    for f in meta.fields:
        if f.fieldtype == "Table" and f.fieldname in doc_dict:
            doc_dict[f.fieldname] = [row.as_dict() for row in doc.get(f.fieldname)]
            
    return doc_dict

@frappe.whitelist()
def save_cge_generic_doc(doctype, doc_data):
    """
    Creates or updates a CGE document.
    Restricted to manager/admin.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    check_cge_doctype(doctype)
    
    from smriti_retail_os.cge.service.cge_service import save_cge_generic_doc_service
    
    is_new = not frappe.db.exists(doctype, json.loads(doc_data).get("name") if isinstance(doc_data, str) else doc_data.get("name"))
    action = "Create" if is_new else "Update"
    
    doc_name = save_cge_generic_doc_service(doctype, doc_data)
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event(
        f"CGE Generic {action}",
        f"CGE Document of type {doctype} with name {doc_name} was saved by {frappe.session.user}."
    )
    
    return doc_name

@frappe.whitelist()
def delete_cge_generic_doc(doctype, name):
    """
    Deletes a CGE document.
    Restricted to manager/admin.
    """
    from smriti_retail_os.security_api import check_store_manager_or_admin
    check_store_manager_or_admin()
    check_cge_doctype(doctype)
    
    from smriti_retail_os.cge.service.cge_service import delete_cge_generic_doc_service
    res = delete_cge_generic_doc_service(doctype, name)
    
    from smriti_retail_os.backup_api import log_audit_event
    log_audit_event(
        "CGE Generic Delete",
        f"CGE Document of type {doctype} with name {name} was deleted by {frappe.session.user}."
    )
    
    return res
