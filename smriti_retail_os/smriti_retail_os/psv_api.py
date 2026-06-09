# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.smriti_retail_os.psv_upload_service import process_upload
from smriti_retail_os.smriti_retail_os.psv_balance_service import get_channel_balance

@frappe.whitelist()
def upload_sell_through(upload_doc_name: str):
    """
    API endpoint to trigger the processing of a Draft PSV Sell-Through Upload.
    Requires roles: Channel Manager, Sales Head, Data Operator.
    """
    frappe.has_permission("PSV Sell-Through Upload", "write", throw=True)
    
    # Optional: ensure status is Validating or Draft before running
    doc = frappe.get_doc("PSV Sell-Through Upload", upload_doc_name)
    if doc.status == "Processed":
        return {"status": "failed", "message": "Document is already processed."}

    # The process_upload function handles atomic commits and error logging internally.
    process_upload(upload_doc_name)
    
    # Reload to get the fresh status and errors
    doc.reload()
    
    if doc.status == "Processed":
        return {
            "status": "success", 
            "rows_processed": doc.total_rows
        }
    else:
        # It failed. Return the error count for UI rendering.
        return {
            "status": "failed", 
            "error_count": len(doc.get("errors"))
        }

@frappe.whitelist()
def fetch_channel_balance(customer: str, item_code: str = None):
    """
    API endpoint to retrieve high-speed current stock balance for a channel.
    Wraps the balance_service function.
    """
    frappe.has_permission("PSV Balance", "read", throw=True)
    
    return {
        "status": "success",
        "data": get_channel_balance(customer, item_code)
    }
