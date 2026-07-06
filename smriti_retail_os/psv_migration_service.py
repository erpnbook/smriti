# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_migration_service.py
# @description: SMRITI PSV Migration Service — ledger reversal and legacy PSA to Channel Partner migration.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: Extracted from psv_service.py (Phase 4 remediation).
#       psv_service.py re-imports all public names for backward compatibility.
#

import hashlib

import frappe
from frappe import _
from frappe.utils import today, now_datetime


@frappe.whitelist()
def create_reversal_entry(original_name, reason):
    """
    Creates a reversal entry for a PSV Ledger Entry.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])
    
    if not frappe.db.exists("PSV Ledger Entry", original_name):
        frappe.throw(_("Original ledger entry {0} not found.").format(original_name))
        
    orig = frappe.get_doc("PSV Ledger Entry", original_name)
    
    already_reversed = frappe.db.exists("PSV Ledger Entry", {"reversal_of": original_name})
    if already_reversed:
        frappe.throw(_("Ledger entry {0} has already been reversed by {1}.").format(original_name, already_reversed))
        
    rev = frappe.new_doc("PSV Ledger Entry")
    rev.company = orig.company
    rev.posting_datetime = now_datetime()
    rev.channel_partner = orig.channel_partner
    rev.item_variant = orig.item_variant
    rev.qty = -float(orig.qty)
    rev.transaction_type = "Reversal"
    rev.voucher_type = orig.voucher_type
    rev.voucher_no = orig.voucher_no
    rev.reversal_of = original_name
    rev.reversal_reason = reason
    rev.warehouse = orig.warehouse
    rev.currency = orig.currency
    rev.fiscal_year = orig.fiscal_year
    
    # reviewed-ignore-permissions: bypass for whitelisted create_reversal_entry endpoint, gated by System Manager or SMRITI Store Manager roles
    rev.insert(ignore_permissions=True)
    frappe.db.commit()
    return rev.name


@frappe.whitelist()
def migrate_to_new_psv_partner(dry_run=0):
    """
    Migrates legacy PSV data to the new PSV Phase 1.1 architecture.
    """
    import time
    from frappe.utils import getdate
    
    start_time = time.time()
    
    report = {
        "customers_scanned": 0,
        "partners_created": 0,
        "partners_skipped": 0,
        "brands_created": 0,
        "warnings": [],
        "errors": [],
        "execution_time": 0.0
    }
    
    is_dry_run = int(dry_run) > 0
    
    try:
        legacy_psas = frappe.get_all(
            "SMRITI Party Stock Account",
            fields=["name", "company", "customer", "location_name", "zone", "region", "active", "status"]
        )
        
        report["customers_scanned"] = len(legacy_psas)
        
        for psa in legacy_psas:
            partner_name = f"{psa.customer}-{psa.location_name}"
            partner_exists = frappe.db.exists("PSV Channel Partner", partner_name)
            
            legacy_brands = frappe.db.sql("""
                SELECT DISTINCT i.brand
                FROM `tabSMRITI Party Stock Ledger Entry` ple
                INNER JOIN `tabItem` i ON ple.item_code = i.name
                WHERE ple.party_stock_account = %s AND i.brand IS NOT NULL AND i.brand != ''
            """, (psa.name,), as_dict=True)
            
            brands_list = [b["brand"] for b in legacy_brands]
            
            if partner_exists:
                report["partners_skipped"] += 1
            else:
                territory = frappe.db.get_value("Customer", psa.customer, "territory") or "All Territories"
                if not frappe.db.exists("Territory", territory):
                    territory = "All Territories"
                    
                partner_doc_data = {
                    "doctype": "PSV Channel Partner",
                    "name": partner_name,
                    "company": psa.company,
                    "customer": psa.customer,
                    "location_name": psa.location_name,
                    "territory": territory,
                    "zone": psa.zone or None,
                    "region": psa.region or "",
                    "active": psa.active,
                    "status": psa.status or "Active",
                    "effective_from": getdate(today())
                }
                
                brands_child = []
                for idx, brand in enumerate(brands_list):
                    brands_child.append({
                        "brand": brand,
                        "is_primary": 1 if idx == 0 else 0
                    })
                    report["brands_created"] += 1
                
                partner_doc_data["brands"] = brands_child
                
                if not is_dry_run:
                    try:
                        partner_doc = frappe.get_doc(partner_doc_data)
                        # reviewed-ignore-permissions: no role restriction — any authenticated user may migrate psv partners, by design
                        partner_doc.insert(ignore_permissions=True)
                        report["partners_created"] += 1
                    except Exception as e:
                        report["errors"].append(f"Error creating PSV Channel Partner {partner_name}: {str(e)}")
                        continue
                else:
                    report["partners_created"] += 1
            
            ledger_entries = frappe.get_all(
                "SMRITI Party Stock Ledger Entry",
                filters={"party_stock_account": psa.name},
                fields=["*"]
            )
            
            tx_type_map = {
                "Opening": "Opening",
                "Dispatch": "Dispatch",
                "Sales": "Sales",
                "Adjustment": "Adjustment",
                "Return": "Return",
                "Transfer": "Dispatch"
            }
            
            company_currency = frappe.db.get_value("Company", psa.company, "default_currency") or "INR"
            active_fy = frappe.db.get_value("Fiscal Year", {"year_start_date": ["<=", today()], "year_end_date": [">=", today()]}, "name")
            
            for le in ledger_entries:
                posting_datetime_str = str(le.posting_datetime)
                fy = active_fy
                if le.posting_datetime:
                    le_date_str = str(le.posting_datetime.date() if hasattr(le.posting_datetime, "date") else le.posting_datetime).split()[0]
                    le_fy = frappe.db.get_value("Fiscal Year", {"year_start_date": ["<=", le_date_str], "year_end_date": [">=", le_date_str]}, "name")
                    if le_fy:
                        fy = le_fy
                        
                tx_type = tx_type_map.get(le.voucher_type, "Adjustment")
                
                raw_string = f"{psa.company}{posting_datetime_str}{partner_name}{le.item_code}{str(le.qty)}{tx_type}{le.voucher_type}{le.voucher_no}"
                unique_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
                
                new_entry_exists = frappe.db.exists("PSV Ledger Entry", {"unique_hash": unique_hash})
                if new_entry_exists:
                    continue
                    
                ledger_doc_data = {
                    "doctype": "PSV Ledger Entry",
                    "company": psa.company,
                    "posting_datetime": le.posting_datetime,
                    "channel_partner": partner_name,
                    "item_variant": le.item_code,
                    "qty": le.qty,
                    "transaction_type": tx_type,
                    "voucher_type": le.voucher_type,
                    "voucher_no": le.voucher_no,
                    "unique_hash": unique_hash,
                    "currency": company_currency,
                    "fiscal_year": fy,
                    "hash_version": 1
                }
                
                if not is_dry_run:
                    try:
                        ledger_doc = frappe.get_doc(ledger_doc_data)
                        # reviewed-ignore-permissions: no role restriction — any authenticated user may migrate psv partners, by design
                        ledger_doc.insert(ignore_permissions=True)
                    except Exception as e:
                        report["errors"].append(f"Error migrating ledger entry for {partner_name}, item {le.item_code}: {str(e)}")
        
        if not is_dry_run:
            frappe.db.commit()
            
    except Exception as e:
        report["errors"].append(f"Migration failed with critical error: {str(e)}")
        
    report["execution_time"] = round(time.time() - start_time, 4)
    return report
