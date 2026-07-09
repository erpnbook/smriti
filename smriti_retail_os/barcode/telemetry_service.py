# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/telemetry_service.py
# @description: Barcode scan telemetry logging and aggregation service.
#               Provides features flags lookup, raw scan events pruning, and scan 
#               reliability scoring / aggregation snapshots.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import cint


def enforce_barcode_scan_event_immutability(doc, method=None):
    """
    Enforces that SMRITI Barcode Scan Event records are read-only after creation.
    Only allows new record insertion.
    """
    if not doc.is_new():
        frappe.throw(frappe.ValidationError("SMRITI Barcode Scan Event records are immutable and cannot be updated."))


@frappe.whitelist()
def get_barcode_feature_flags():
    """
    Returns SMRITI Barcode telemetry and learning feature flags.
    If the settings DocType is missing, returns all False (fail-safe principle).
    Uses caching (TTL = 3600) for performance.
    """
    cache_key = "smriti:barcode_feature_flags"
    try:
        cached = smriti.cache().get_value(cache_key)
        if cached is not None:
            return cached
    except Exception:
        pass

    flags = {
        "capture": False,
        "aggregation": False,
        "learning": False
    }

    try:
        if smriti.db.exists("DocType", "SMRITI Barcode Settings") and smriti.db.exists("SMRITI Barcode Settings", "SMRITI Barcode Settings"):
            capture = smriti.db.get_single("SMRITI Barcode Settings", "barcode_telemetry_capture_enabled")
            aggregation = smriti.db.get_single("SMRITI Barcode Settings", "barcode_telemetry_aggregation_enabled")
            learning = smriti.db.get_single("SMRITI Barcode Settings", "barcode_learning_enabled")
            
            flags["capture"] = bool(cint(capture)) if capture is not None else False
            flags["aggregation"] = bool(cint(aggregation)) if aggregation is not None else False
            flags["learning"] = bool(cint(learning)) if learning is not None else False
    except Exception:
        pass

    try:
        smriti.cache().set_value(cache_key, flags, expires_in_sec=3600)
    except Exception:
        pass

    return flags


def clear_barcode_feature_flags_cache(doc=None, method=None):
    """Clears cached SMRITI Barcode feature flags."""
    try:
        smriti.cache().delete_value("smriti:barcode_feature_flags")
    except Exception:
        pass


@frappe.whitelist()
def log_barcode_scan_event(event_uuid, template_id, barcode_family, printer_profile, scan_method, scan_attempts, scan_success, first_pass_success, store_id=None, pos_invoice=None, pos_invoice_item=None):
    """
    Logs a barcode scan telemetry event. Restricted to users with System Manager, SMRITI POS User, or POS User roles.
    Checks barcode_telemetry_capture_enabled feature flag before logging.
    """
    # Check feature flags first
    flags = get_barcode_feature_flags()
    if not flags.get("capture"):
        return {"status": "disabled", "message": "Barcode telemetry capture is disabled"}

    # 1. Access/Role Verification
    roles = frappe.get_roles(frappe.session.user)
    authorized_roles = {"System Manager", "SMRITI POS User", "POS User", "SMRITI Store Manager", "SMRITI Cashier"}
    if not authorized_roles.intersection(set(roles)):
        frappe.throw(frappe._("Not authorized to log telemetry events."), frappe.PermissionError)

    # 2. Idempotency Check
    existing = smriti.db.get("SMRITI Barcode Scan Event", {"event_uuid": event_uuid}, "name")
    if existing:
        return smriti.documents.get("SMRITI Barcode Scan Event", existing)

    # 3. Determine Governance Event ID
    scan_attempts = int(scan_attempts)
    scan_success = int(scan_success)
    first_pass_success = int(first_pass_success)

    if scan_success == 1 and first_pass_success == 1:
        gov_id = "SCAN-EVT-001"
    elif scan_success == 1 and first_pass_success == 0:
        gov_id = "SCAN-EVT-002"
    else:
        gov_id = "SCAN-EVT-003"

    # Default store_id if not provided: retrieve first available non-group warehouse as fallback
    if not store_id:
        store_id = smriti.db.get("Warehouse", {"is_group": 0, "disabled": 0}, "name")

    if not store_id:
        frappe.throw(frappe.ValidationError("A valid Store (Warehouse) is required to log telemetry."))

    # 4. Insert raw SMRITI Barcode Scan Event doc
    doc = smriti.documents.new("BarcodeScanEvent")
    doc.update({
        "event_uuid": event_uuid,
        "timestamp": frappe.utils.now_datetime(),
        "store_id": store_id,
        "template_id": template_id,
        "barcode_family": barcode_family,
        "printer_profile": printer_profile,
        "scan_method": scan_method,
        "scan_attempts": scan_attempts,
        "scan_success": scan_success,
        "first_pass_success": first_pass_success,
        "governance_event_id": gov_id,
        "pos_invoice": pos_invoice,
        "pos_invoice_item": pos_invoice_item
    })
    # reviewed-ignore-permissions: barcode scan telemetry logging, no business data modification
    doc.insert(ignore_permissions=True)
    smriti.db.commit()
    return doc


def delete_expired_scan_events():
    """
    Scheduler task to prune raw telemetry events older than 90 days.
    """
    from frappe.utils import add_days, now_datetime
    cutoff = add_days(now_datetime(), -90)
    
    expired_events = smriti.db.sql("""
        SELECT name FROM `tabSMRITI Barcode Scan Event`
        WHERE timestamp < %(cutoff)s
    """, {"cutoff": cutoff}, as_dict=True)

    count = 0
    for ev in expired_events:
        smriti.documents.delete("SMRITI Barcode Scan Event", ev["name"], ignore_permissions=True)
        count += 1

    if count > 0:
        smriti.db.commit()
        from smriti_retail_os.backup_api import log_audit_event
        log_audit_event(
            "SMRITI Telemetry Cleanup",
            f"Pruned {count} raw scan events older than 90 days."
        )
        print(f"[SMRITI Telemetry] Pruned {count} raw scan events older than 90 days.")


@frappe.whitelist()
def aggregate_scan_telemetry(period="Daily", target_date=None):
    """
    Aggregates raw scan events and calculates Scan Reliability Scores.
    Default period is Daily, aggregating the previous calendar day.
    Checks barcode_telemetry_aggregation_enabled feature flag.
    """
    flags = get_barcode_feature_flags()
    if not flags.get("aggregation"):
        print("[SMRITI Telemetry] Aggregation is disabled in SMRITI Barcode Settings.")
        return

    from frappe.utils import add_days, getdate, flt

    if not target_date:
        target_date = add_days(getdate(), -1)
    else:
        target_date = getdate(target_date)

    data = smriti.db.sql("""
        SELECT
            store_id,
            template_id,
            barcode_family,
            printer_profile,
            COUNT(name) as total_scans,
            SUM(CASE WHEN scan_success = 1 THEN 1 ELSE 0 END) as total_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-001' THEN 1 ELSE 0 END) as first_pass_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-002' THEN 1 ELSE 0 END) as retry_successes,
            SUM(CASE WHEN governance_event_id = 'SCAN-EVT-003' THEN 1 ELSE 0 END) as failures
        FROM
            `tabSMRITI Barcode Scan Event`
        WHERE
            DATE(timestamp) = %(target_date)s
        GROUP BY
            store_id, template_id, barcode_family, printer_profile
    """, {"target_date": target_date}, as_dict=True)

    for row in data:
        total = int(row["total_scans"])
        first_pass = int(row["first_pass_successes"])
        retries = int(row["retry_successes"])
        failures = int(row["failures"])

        if total > 0:
            reliability_score = flt(((first_pass + 0.5 * retries) / total) * 100, 2)
            first_pass_rate = flt(first_pass / total, 4)
        else:
            reliability_score = 0.0
            first_pass_rate = 0.0

        filters = {
            "snapshot_date": target_date,
            "period": period,
            "store_id": row["store_id"],
            "template_id": row["template_id"],
            "barcode_family": row["barcode_family"],
            "printer_profile": row["printer_profile"]
        }

        existing_name = smriti.db.get("SMRITI Barcode Telemetry Snapshot", filters, "name")
        if existing_name:
            snapshot = smriti.documents.get("SMRITI Barcode Telemetry Snapshot", existing_name)
        else:
            snapshot = smriti.documents.new("SMRITI Barcode Telemetry Snapshot")
            snapshot.update(filters)

        snapshot.total_scans = total
        snapshot.total_successes = int(row["total_successes"])
        snapshot.first_pass_successes = first_pass
        snapshot.retry_successes = retries
        snapshot.failures = failures
        snapshot.scan_reliability_score = reliability_score
        snapshot.first_pass_success_rate = first_pass_rate
        
        # reviewed-ignore-permissions: periodic barcode telemetry rollup, restricted to system runner
        snapshot.save(ignore_permissions=True)

    smriti.db.commit()
    print(f"[SMRITI Telemetry] Completed aggregation for {target_date} ({len(data)} records).")
