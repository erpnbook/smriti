# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/www/connect.py
# @desc:    Auth and Context loader for SMRITI Connect Admin Dashboard.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.security_api import check_page_access
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

def get_context(context):
    """
    Validates user session permissions and injects initial configuration state
    for SMRITI Connect UI console rendering.
    """
    # 1. Enforce SMRITI Security Access Control
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_to = "/login"
        raise frappe.Redirect
        
    try:
        check_page_access("connect")
    except frappe.PermissionError:
        # Fallback to SMRITI 403 page
        frappe.local.flags.redirect_to = "/smriti-403"
        raise frappe.Redirect

    # 2. Populate context variables
    context.title = _("SMRITI Connect")
    context.username = frappe.session.user
    
    # 3. Pull active providers for Health status dashboard
    providers = QueueRepository.get_active_providers()
    if not providers:
        # Fallback default configuration if DB DocTypes are not registered yet
        providers = [
            {
                "provider_id": "accounting.tally",
                "provider_name": "TallyPrime reference integration",
                "provider_type": "Accounting",
                "adapter_class": "smriti_retail_os.integration.providers.accounting.tally.tally_adapter.TallyAdapter",
                "enabled": 1,
                "version": "1.0.0",
                "status": "Stable",
                "health_status": "Healthy"
            }
        ]
    context.providers = providers

    # 4. Pull recent queue counts to display in monitor cards
    context.queue_stats = get_queue_statistics()
    return context


def get_queue_statistics() -> dict:
    """Helper to return current event queue totals grouped by state."""
    stats = {
        "pending": 0,
        "success": 0,
        "failed": 0,
        "retrying": 0,
        "dead_letter": 0
    }
    
    if not frappe.db.exists("DocType", "SMRITI Integration Queue"):
        return stats
        
    # Delegate to Repository
    data = QueueRepository.get_queue_statistics()
    
    for row in data:
        status_key = row.get("status").lower().replace("-", "_")
        if status_key in stats:
            stats[status_key] = row.get("count")
            
    return stats


# ── Whitelisted APIs for Connect Console UI ───────────────────────────────

@frappe.whitelist()
def get_recent_queue(limit=50):
    """Returns recent log entries for SMRITI Connect dashboard monitor."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)
        
    if not frappe.db.exists("DocType", "SMRITI Integration Queue"):
        return []
        
    return frappe.get_all(
        "SMRITI Integration Queue",
        fields=["name", "event_type", "document_type", "document_name", 
                "adapter_id", "priority", "status", "retry_count", "last_attempt", "error_details"],
        order_by="creation desc",
        limit=int(limit)
    )


@frappe.whitelist()
def trigger_manual_retry(queue_id):
    """Allows administrator to manually trigger execution of a failed/dead-letter item."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)
        
    check_page_access("connect")
    
    if not frappe.db.exists("SMRITI Integration Queue", queue_id):
        frappe.throw(_("Queue entry {0} not found.").format(queue_id))
        
    # Delegate to Repository
    QueueRepository.reset_queue_item(queue_id)
    
    # Process immediately synchronously
    from smriti_retail_os.integration.core.engine import IntegrationEngine
    # Re-run for this queue id specifically by loading worker
    IntegrationEngine.process_queue(limit=100)
    
    # Check new status
    new_status = frappe.db.get_value("SMRITI Integration Queue", queue_id, "status")
    return {
        "success": new_status == "Success",
        "new_status": new_status,
        "error": frappe.db.get_value("SMRITI Integration Queue", queue_id, "error_details") if new_status != "Success" else ""
    }


@frappe.whitelist()
def run_health_checks():
    """Triggers health diagnostics on all enabled providers."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)
        
    check_page_access("connect")
    
    from smriti_retail_os.integration.core.registry import IntegrationRegistry
    adapters = IntegrationRegistry.get_active_adapters()
    results = {}
    
    for provider_id, adapter in adapters.items():
        try:
            check_result = adapter.health_check()
            status = check_result.get("status", "Unhealthy")
            latency = check_result.get("latency_ms", 0)
            error = check_result.get("error", "")
            
            QueueRepository.update_provider_health(provider_id, status, latency, error)
            results[provider_id] = check_result
        except Exception as e:
            results[provider_id] = {"status": "Unhealthy", "latency_ms": 0, "error": str(e)}
            QueueRepository.update_provider_health(provider_id, "Unhealthy", 0, str(e))
            
    return results
