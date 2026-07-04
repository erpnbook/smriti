# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode_api.py
# @description: Barcode printing routing shell — exposes all whitelisted and hook APIs
#               by delegating to underlying focused services.
#               Maintains 100% backward compatibility.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.9.0
#

import frappe

# ---------------------------------------------------------------------------
# SERVICE LAYER IMPORTS
# ---------------------------------------------------------------------------
from smriti_retail_os.barcode.item_service import (
    expand_item_variants as _expand_item_variants,
    get_transaction_items_checklist as _get_transaction_items_checklist,
    get_items_by_range as _get_items_by_range,
    get_items_for_printing as _get_items_for_printing,
    get_item_print_details as _get_item_print_details
)
from smriti_retail_os.barcode.prn_generator import (
    generate_prn as _generate_prn
)
from smriti_retail_os.barcode.printer_service import (
    send_to_network_printer as _send_to_network_printer,
    get_field_mapping_reference as _get_field_mapping_reference,
    get_recent_transactions as _get_recent_transactions,
    test_printer_connection as _test_printer_connection,
    print_test_label as _print_test_label
)
from smriti_retail_os.barcode.analytics_service import (
    log_print_job as _log_print_job,
    get_print_analytics as _get_print_analytics,
    get_template_usage_stats as _get_template_usage_stats
)
from smriti_retail_os.barcode.template_service import (
    get_barcode_filters as _get_barcode_filters,
    get_print_templates as _get_print_templates,
    get_print_profiles as _get_print_profiles,
    save_print_profile as _save_print_profile,
    delete_print_profile as _delete_print_profile,
    save_print_template as _save_print_template,
    delete_print_template as _delete_print_template,
    search_barcode_items as _search_barcode_items,
    get_print_template_versions as _get_print_template_versions,
    restore_print_template_version as _restore_print_template_version
)
from smriti_retail_os.barcode.batch_service import (
    enqueue_print_job as _enqueue_print_job,
    _process_print_job as __process_print_job,
    get_print_job_status as _get_print_job_status,
    retry_print_job as _retry_print_job,
    get_recent_print_jobs as _get_recent_print_jobs,
    cleanup_old_print_jobs as _cleanup_old_print_jobs
)
from smriti_retail_os.barcode.diagnostics_service import (
    get_barcode_hrt_reserved_height as _get_barcode_hrt_reserved_height,
    get_enforce_printability_threshold as _get_enforce_printability_threshold,
    get_printability_formula_config as _get_printability_formula_config,
    validate_layout_diagnostics as _validate_layout_diagnostics
)
from smriti_retail_os.barcode.telemetry_service import (
    enforce_barcode_scan_event_immutability as _enforce_barcode_scan_event_immutability,
    get_barcode_feature_flags as _get_barcode_feature_flags,
    clear_barcode_feature_flags_cache as _clear_barcode_feature_flags_cache,
    log_barcode_scan_event as _log_barcode_scan_event,
    delete_expired_scan_events as _delete_expired_scan_events,
    aggregate_scan_telemetry as _aggregate_scan_telemetry
)


# ---------------------------------------------------------------------------
# WHITELISTED ROUTING ENDPOINTS
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_barcode_filters():
    return _get_barcode_filters()


@frappe.whitelist()
def get_print_templates():
    return _get_print_templates()


@frappe.whitelist()
def expand_item_variants(item_code, default_print_qty=1):
    return _expand_item_variants(item_code, default_print_qty)


@frappe.whitelist()
def get_transaction_items_checklist(source_doctype, source_name):
    return _get_transaction_items_checklist(source_doctype, source_name)


@frappe.whitelist()
def get_items_by_range(from_article, to_article):
    return _get_items_by_range(from_article, to_article)


@frappe.whitelist()
def get_items_for_printing(filters=None, source_doctype=None, source_name=None):
    return _get_items_for_printing(filters, source_doctype, source_name)


def get_item_print_details(item_code, default_print_qty):
    return _get_item_print_details(item_code, default_print_qty)


@frappe.whitelist()
def generate_prn(items, template_name=None):
    return _generate_prn(items, template_name)


@frappe.whitelist()
def send_to_network_printer(items, template_name=None, printer_ip=None, printer_port=9100):
    return _send_to_network_printer(items, template_name, printer_ip, printer_port)


@frappe.whitelist()
def get_field_mapping_reference():
    return _get_field_mapping_reference()


@frappe.whitelist()
def get_recent_transactions(doctype, limit=15):
    return _get_recent_transactions(doctype, limit)


@frappe.whitelist()
def test_printer_connection(printer_ip, printer_port=9100):
    return _test_printer_connection(printer_ip, printer_port)


@frappe.whitelist()
def print_test_label(printer_ip, printer_port=9100, printer_language="ZPL"):
    return _print_test_label(printer_ip, printer_port, printer_language)


@frappe.whitelist()
def log_print_job(template_name, printer_ip, labels_count, success, error_message=None, print_profile=None, details=None):
    return _log_print_job(template_name, printer_ip, labels_count, success, error_message, print_profile, details)


@frappe.whitelist()
def get_print_analytics():
    return _get_print_analytics()


@frappe.whitelist()
def get_template_usage_stats():
    return _get_template_usage_stats()


@frappe.whitelist()
def get_print_profiles():
    return _get_print_profiles()


@frappe.whitelist()
def save_print_profile(profile_name, template_name, printer_ip, printer_port=9100, dpi="203 DPI", copies=1, label_size="50x25", is_default=0):
    return _save_print_profile(profile_name, template_name, printer_ip, printer_port, dpi, copies, label_size, is_default)


@frappe.whitelist()
def delete_print_profile(profile_name):
    return _delete_print_profile(profile_name)


@frappe.whitelist()
def save_print_template(template_name, label_size, printer_language, raw_template, field_mappings_json=None, printer_family=None, custom_active=1, custom_is_default=0, custom_version="1.0.0", custom_visual_layout_json=None, version_label=None):
    return _save_print_template(template_name, label_size, printer_language, raw_template, field_mappings_json, printer_family, custom_active, custom_is_default, custom_version, custom_visual_layout_json, version_label)


@frappe.whitelist()
def delete_print_template(name_id):
    return _delete_print_template(name_id)


@frappe.whitelist()
def search_barcode_items(txt):
    return _search_barcode_items(txt)


@frappe.whitelist()
def get_print_template_versions(template_name):
    return _get_print_template_versions(template_name)


@frappe.whitelist()
def restore_print_template_version(template_name, version_number, expected_checksum):
    return _restore_print_template_version(template_name, version_number, expected_checksum)


@frappe.whitelist()
def enqueue_print_job(template_name, printer_ip, printer_port, payload, print_qty=1, labels_count=None, item_code=None, barcode=None):
    return _enqueue_print_job(template_name, printer_ip, printer_port, payload, print_qty, labels_count, item_code, barcode)


@frappe.whitelist()
def _process_print_job(job_id=None, print_job_id=None):
    return __process_print_job(job_id, print_job_id)


@frappe.whitelist()
def get_print_job_status(job_id):
    return _get_print_job_status(job_id)


@frappe.whitelist()
def retry_print_job(job_id):
    return _retry_print_job(job_id)


@frappe.whitelist()
def get_recent_print_jobs(limit=20):
    return _get_recent_print_jobs(limit)


def cleanup_old_print_jobs():
    return _cleanup_old_print_jobs()


def get_barcode_hrt_reserved_height():
    return _get_barcode_hrt_reserved_height()


def get_enforce_printability_threshold():
    return _get_enforce_printability_threshold()


def get_printability_formula_config():
    return _get_printability_formula_config()


@frappe.whitelist()
def validate_layout_diagnostics(layout_json, label_size, item_data=None):
    return _validate_layout_diagnostics(layout_json, label_size, item_data)


def enforce_barcode_scan_event_immutability(doc, method=None):
    return _enforce_barcode_scan_event_immutability(doc, method)


@frappe.whitelist()
def get_barcode_feature_flags():
    return _get_barcode_feature_flags()


def clear_barcode_feature_flags_cache(doc=None, method=None):
    return _clear_barcode_feature_flags_cache(doc, method)


@frappe.whitelist()
def log_barcode_scan_event(event_uuid, template_id, barcode_family, printer_profile, scan_method, scan_attempts, scan_success, first_pass_success, store_id=None, pos_invoice=None, pos_invoice_item=None):
    return _log_barcode_scan_event(event_uuid, template_id, barcode_family, printer_profile, scan_method, scan_attempts, scan_success, first_pass_success, store_id, pos_invoice, pos_invoice_item)


def delete_expired_scan_events():
    return _delete_expired_scan_events()


@frappe.whitelist()
def aggregate_scan_telemetry(period="Daily", target_date=None):
    return _aggregate_scan_telemetry(period, target_date)
