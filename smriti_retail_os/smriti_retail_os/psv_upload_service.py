# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_upload_service.py
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
from frappe import _
from frappe.utils.file_manager import get_file_path
from smriti_retail_os.smriti_retail_os.psv_ledger_service import create_transaction
import csv
import io
import hashlib

def process_upload(upload_doc_name: str):
    """
    Main entry point for processing a PSV Sell-Through Upload document.
    Executes entirely in memory and uses atomic commits.
    """
    doc = frappe.get_doc("PSV Sell-Through Upload", upload_doc_name)
    
    try:
        # Pre-validation guards
        _check_date_overlap(doc)
        file_path = _get_and_validate_file(doc.upload_file)
        _check_duplicate_file(doc.upload_file, upload_doc_name)

        # Parse and Map
        parsed_rows, errors = _parse_and_map_csv(file_path)

        if errors:
            _fail_upload(doc, errors)
            return

        # Atomic Ledger Update
        _commit_to_ledger(doc, parsed_rows)

    except frappe.ValidationError:
        # Expected validation failures (already handled/logged)
        raise
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"PSV Upload Error: {upload_doc_name}")
        _fail_upload(doc, [{"row_number": 0, "error_message": f"System Error: {str(e)}"}])
        raise frappe.ValidationError(_("Upload failed due to a system error. Check Error Log."))

def _check_date_overlap(doc):
    """[PSV-001] Guard against overlapping date ranges for the same channel."""
    overlap = frappe.db.sql("""
        SELECT name FROM `tabPSV Sell-Through Upload`
        WHERE customer = %(customer)s
        AND name != %(name)s
        AND docstatus = 1
        AND status = 'Processed'
        AND (from_date <= %(to_date)s AND to_date >= %(from_date)s)
        LIMIT 1
    """, {
        "customer": doc.customer,
        "name": doc.name,
        "from_date": doc.from_date,
        "to_date": doc.to_date
    })

    if overlap:
        frappe.throw(_("Overlap Error [PSV-001]: Dates overlap with processed upload {0}.").format(overlap[0][0]))

def _get_and_validate_file(file_url: str):
    """Retrieves physical file path."""
    if not file_url:
        frappe.throw(_("No file attached to upload."))
        
    file_path = get_file_path(file_url)
    if not file_path.endswith('.csv'):
        # For V1, restrict to CSV to guarantee predictable parsing. Excel support can be added via openpyxl if needed.
        frappe.throw(_("Only .csv files are supported for V1."))
        
    return file_path

def _check_duplicate_file(file_url: str, current_doc_name: str):
    """[PSV-002] Prevents uploading the exact same physical file twice."""
    file_path = get_file_path(file_url)
    
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        
    # Standard Frappe File doctype holds content_hash
    duplicate = frappe.db.sql("""
        SELECT parent 
        FROM `tabPSV Sell-Through Upload`
        JOIN `tabFile` ON `tabPSV Sell-Through Upload`.upload_file = `tabFile`.file_url
        WHERE `tabFile`.content_hash = %s 
        AND `tabPSV Sell-Through Upload`.name != %s
        AND `tabPSV Sell-Through Upload`.status = 'Processed'
        LIMIT 1
    """, (file_hash, current_doc_name))
    
    if duplicate:
        frappe.throw(_("Duplicate File Error [PSV-002]: This exact file was already processed in {0}.").format(duplicate[0][0]))

def _parse_and_map_csv(file_path: str):
    """Reads CSV into memory, validates schema, and maps barcodes."""
    parsed_rows = []
    errors = []
    
    # Pre-fetch all barcodes into a dict for fast memory lookup {barcode: item_code}
    barcode_map = {}
    for b in frappe.get_all("Item Barcode", fields=["barcode", "parent"]):
        barcode_map[str(b.barcode).strip()] = b.parent
        
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Schema Validation
        headers = [h.strip().lower() for h in reader.fieldnames if h]
        required_cols = ['barcode', 'qty']
        
        if not all(col in headers for col in required_cols):
            errors.append({
                "row_number": 0,
                "error_message": _("Schema Error [PSV-004]: Required columns 'barcode' and 'qty' missing.")
            })
            return [], errors

        # Ensure correct case for dict access
        barcode_col = next(h for h in reader.fieldnames if h.strip().lower() == 'barcode')
        qty_col = next(h for h in reader.fieldnames if h.strip().lower() == 'qty')

        for row_idx, row in enumerate(reader, start=2): # Start at 2 to account for header
            raw_barcode = str(row.get(barcode_col, '')).strip()
            raw_qty = str(row.get(qty_col, '')).strip()
            
            if not raw_barcode:
                continue # Skip empty rows
                
            item_code = barcode_map.get(raw_barcode)
            
            if not item_code:
                # Fallback: maybe they sent the item_code instead of the barcode
                if frappe.db.exists("Item", raw_barcode):
                    item_code = raw_barcode
                else:
                    errors.append({
                        "row_number": row_idx,
                        "barcode": raw_barcode,
                        "error_message": _("Unknown Barcode [PSV-003]: Barcode not found in system.")
                    })
                    continue
                    
            try:
                # Handle negative quantities gracefully (MBO POS returns)
                # By keeping them negative here, when we *subtract* later, it will correctly *add* to PSV balance.
                qty = float(raw_qty)
            except ValueError:
                errors.append({
                    "row_number": row_idx,
                    "barcode": raw_barcode,
                    "error_message": _("Type Error: Quantity must be a number.")
                })
                continue
                
            parsed_rows.append({
                "item_code": item_code,
                "qty": qty
            })
            
    return parsed_rows, errors

def _fail_upload(doc, errors: list):
    """Writes errors to child table and fails the document."""
    # We must roll back any partial DB changes made so far just in case
    frappe.db.rollback()
    
    # Open a new transaction just to save the errors
    frappe.db.begin()
    
    doc.db_set("status", "Failed")
    doc.set("errors", []) # Clear old errors
    
    for err in errors:
        doc.append("errors", {
            "row_number": err.get("row_number"),
            "barcode": err.get("barcode", ""),
            "error_message": err.get("error_message")
        })
        
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    frappe.msgprint(_("Upload failed validation. Check the Error Log table in the document."))

def _commit_to_ledger(doc, parsed_rows: list):
    """
    ATOMIC COMMIT: Loops through parsed rows and pushes to ledger.
    If anything fails here, the entire batch is rolled back.
    """
    frappe.db.begin() # Explicitly begin atomic block
    
    try:
        for row in parsed_rows:
            # Note: We pass the literal qty. 
            # If Reliance sold 5, qty is 5. We pass 5 to create_transaction.
            # However, transaction_type="Sell-Through" implies a deduction.
            # In the ledger service (or here), we must ensure Sell-Through is recorded correctly.
            # We will pass it as a negative to the ledger service so it deducts from balance.
            
            ledger_qty = row["qty"] * -1 
            
            create_transaction(
                customer=doc.customer,
                item_code=row["item_code"],
                qty=ledger_qty,
                trans_type="Sell-Through",
                ref_doctype="PSV Sell-Through Upload",
                ref_name=doc.name
            )
            
        # Update header status
        doc.db_set("status", "Processed")
        doc.db_set("total_rows", len(parsed_rows))
        
        frappe.db.commit() # Success! Commit everything.
        frappe.msgprint(_("Successfully processed {0} rows and updated PSV Ledger.").format(len(parsed_rows)), alert=True)
        
    except Exception as e:
        frappe.db.rollback() # Abort! Revert all ledger entries.
        frappe.log_error(frappe.get_traceback(), f"PSV Atomic Commit Failed: {doc.name}")
        
        # Failsafe: Write generic error
        frappe.db.begin()
        doc.db_set("status", "Failed")
        doc.append("errors", {
            "row_number": 0,
            "error_message": f"Ledger Commit Failed: {str(e)}"
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.throw(_("Ledger update failed and was rolled back. See Error Log."))
