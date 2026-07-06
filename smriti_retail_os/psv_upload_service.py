# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_upload_service.py
# @description: SMRITI Psv Upload Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/smriti_retail_os/psv_upload_service.py
# @description: Channel Stock — PSV Sell-Through Upload processing service.
#               Handles validation, CSV parsing, barcode mapping, and ledger writes
#               via the canonical create_transaction() → create_psv_transaction() path.
# @version: 1.8.6  (BUG-002 fix: broken SQL + hash mismatch resolved)
#

import csv
import hashlib

import frappe
from frappe import _
from frappe.utils.file_manager import get_file_path

from smriti_retail_os.psv_ledger_service import create_transaction


def process_upload(upload_doc_name: str):
    """
    Main entry point for processing a PSV Sell-Through Upload document.
    Runs pre-validation guards, parses the CSV, and commits to the ledger atomically.
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
        frappe.throw(
            _("Overlap Error [PSV-001]: Dates overlap with processed upload {0}."
              ).format(overlap[0][0])
        )


def _get_and_validate_file(file_url: str) -> str:
    """Retrieves and validates the physical file path. Returns the path."""
    if not file_url:
        frappe.throw(_("No file attached to upload."))

    file_path = get_file_path(file_url)
    if not file_path.endswith(".csv"):
        # For V1, restrict to CSV to guarantee predictable parsing.
        # Excel support can be added via openpyxl when needed.
        frappe.throw(_("Only .csv files are supported for V1."))

    return file_path


def _check_duplicate_file(file_url: str, current_doc_name: str):
    """[PSV-002] Prevents uploading the exact same physical file twice.

    BUG-002 FIX:
    - Old code: `SELECT parent FROM tabPSV... JOIN tabFile` — wrong column name
      (`parent` does not exist) and MD5 vs SHA-256 hash algorithm mismatch.
    - New code: computes SHA-256 of the physical file and checks the `file_hash`
      field stored on processed upload documents directly. No cross-table JOIN needed.
    """
    file_path = get_file_path(file_url)

    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    # Check against the file_hash field stored on previously processed uploads.
    duplicate = frappe.db.get_value(
        "PSV Sell-Through Upload",
        {
            "file_hash": file_hash,
            "name": ["!=", current_doc_name],
            "status": "Processed"
        },
        "name"
    )

    if duplicate:
        frappe.throw(
            _("Duplicate File Error [PSV-002]: This exact file was already processed in {0}."
              ).format(duplicate)
        )

    # Persist the hash so future duplicate checks can find this upload
    frappe.db.set_value("PSV Sell-Through Upload", current_doc_name, "file_hash", file_hash)


def _parse_and_map_csv(file_path: str):
    """Reads CSV into memory, validates schema, and maps barcodes to item codes."""
    parsed_rows = []
    errors = []

    # Pre-fetch all barcodes into a dict for fast in-memory lookup {barcode: item_code}
    barcode_map = {}
    for b in frappe.get_all("Item Barcode", fields=["barcode", "parent"]):
        barcode_map[str(b.barcode).strip()] = b.parent

    with open(file_path, mode="r", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        # Schema Validation
        if not reader.fieldnames:
            errors.append({"row_number": 0, "error_message": _("CSV file is empty or has no headers.")})
            return [], errors

        headers = [h.strip().lower() for h in reader.fieldnames if h]
        required_cols = ["barcode", "qty"]

        if not all(col in headers for col in required_cols):
            errors.append({
                "row_number": 0,
                "error_message": _("Schema Error [PSV-004]: Required columns 'barcode' and 'qty' missing.")
            })
            return [], errors

        # Ensure correct case for dict access
        barcode_col = next(h for h in reader.fieldnames if h.strip().lower() == "barcode")
        qty_col = next(h for h in reader.fieldnames if h.strip().lower() == "qty")

        for row_idx, row in enumerate(reader, start=2):  # Start at 2 (header = row 1)
            raw_barcode = str(row.get(barcode_col, "")).strip()
            raw_qty = str(row.get(qty_col, "")).strip()

            if not raw_barcode:
                continue  # Skip blank rows

            item_code = barcode_map.get(raw_barcode)

            if not item_code:
                # Fallback: distributor may have sent item_code instead of barcode
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
                # Negative quantities are valid (MBO POS returns); they will ADD back to balance
                qty = float(raw_qty)
            except ValueError:
                errors.append({
                    "row_number": row_idx,
                    "barcode": raw_barcode,
                    "error_message": _("Type Error: Quantity must be a number.")
                })
                continue

            parsed_rows.append({"item_code": item_code, "qty": qty})

    return parsed_rows, errors


def _fail_upload(doc, errors: list):
    """Writes errors to the child errors table and marks document as Failed."""
    frappe.db.rollback()  # Roll back any partial changes
    frappe.db.begin()     # Open fresh transaction for error writes only

    doc.db_set("status", "Failed")
    doc.set("errors", [])  # Clear stale errors from previous attempts

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
    ATOMIC COMMIT: Pushes all parsed rows to the ledger via create_transaction().
    If anything fails, the entire batch is rolled back.

    Note: create_transaction() routes through create_psv_transaction() which
    creates a SMRITI PSV Transaction document (with fingerprint deduplication)
    and then writes immutable ledger entries on submit.
    """
    frappe.db.begin()  # Explicitly begin atomic block

    try:
        for row in parsed_rows:
            # Sell-Through = stock sold by distributor = deduction from channel balance.
            # Pass negative qty so the ledger records it as outflow.
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

        frappe.db.commit()  # Success — commit everything
        frappe.msgprint(
            _("Successfully processed {0} rows and updated PSV Ledger.").format(len(parsed_rows)),
            alert=True
        )

    except Exception as e:
        frappe.db.rollback()  # Abort — revert all ledger entries
        frappe.log_error(frappe.get_traceback(), f"PSV Atomic Commit Failed: {doc.name}")

        frappe.db.begin()
        doc.db_set("status", "Failed")
        doc.append("errors", {
            "row_number": 0,
            "error_message": f"Ledger Commit Failed: {str(e)}"
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.throw(_("Ledger update failed and was rolled back. See Error Log."))
