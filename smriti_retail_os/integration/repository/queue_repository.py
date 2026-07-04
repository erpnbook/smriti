# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/repository/queue_repository.py
# @desc:    Data Access Repository Layer for SMRITI Connect Integration Platform.
#           Encapsulates all database reads and writes to Platform Engine integration tables.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _

class QueueRepository:
    """
    Isolates direct database access for SMRITI Connect operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_active_providers() -> list[dict]:
        """Retrieves list of active providers from SMRITI Integration Provider DocType."""
        if not frappe.db.exists("DocType", "SMRITI Integration Provider"):
            return []
        return frappe.get_all(
            "SMRITI Integration Provider",
            filters={"enabled": 1},
            fields=["name", "provider_id", "provider_name", "provider_type", 
                    "adapter_class", "version", "min_platform_version"]
        )

    @staticmethod
    def update_provider_health(provider_id: str, status: str, latency: int, error_msg: str = None):
        """Updates health metrics for a provider."""
        if not frappe.db.exists("SMRITI Integration Provider", provider_id):
            return
        
        frappe.db.set_value(
            "SMRITI Integration Provider",
            provider_id,
            {
                "health_status": status,
                "last_check": frappe.utils.now_datetime(),
                "error_details": error_msg or ""
            },
            update_modified=False
        )
        # Commit immediately if outside main transaction
        frappe.db.commit()

    @staticmethod
    def get_event_definition(event_name: str) -> dict | None:
        """Retrieves event schema definition by event name."""
        if not frappe.db.exists("DocType", "SMRITI Event Definition"):
            return None
        
        defs = frappe.get_all(
            "SMRITI Event Definition",
            filters={"event_name": event_name},
            fields=["name", "event_name", "version", "producer", "consumers", "required_fields"],
            limit=1
        )
        return defs[0] if defs else None

    @staticmethod
    def get_routing_policies() -> list[dict]:
        """Retrieves active routing rules for SMRITI Connect."""
        if not frappe.db.exists("DocType", "SMRITI Integration Policy"):
            return []
        return frappe.get_all(
            "SMRITI Integration Policy",
            filters={"enabled": 1},
            fields=["name", "event_type", "company", "location", "action", "adapter_id"]
        )

    @staticmethod
    def insert_queue_entry(event_type: str, doc_type: str, doc_name: str, adapter_id: str, payload_dict: dict, priority: str) -> str:
        """Inserts pending transaction entry into SMRITI Integration Queue."""
        if not frappe.db.exists("DocType", "SMRITI Integration Queue"):
            frappe.msgprint(_("SMRITI Connect: Integration Queue not active. Event {0} bypassed.").format(event_type), indicator="orange", alert=True)
            return ""
            
        doc = frappe.get_doc({
            "doctype": "SMRITI Integration Queue",
            "event_type": event_type,
            "document_type": doc_type,
            "document_name": doc_name,
            "adapter_id": adapter_id,
            "payload": frappe.as_json(payload_dict),
            "priority": priority,
            "status": "Pending",
            "retry_count": 0
        })
        doc.insert(ignore_permissions=True)
        return doc.name

    @staticmethod
    def get_pending_queue_entries(limit: int = 50) -> list[dict]:
        """
        Retrieves pending or retrying queue items ordered by priority (Critical -> Normal -> Low)
        and creation date to process them in correct order.
        """
        if not frappe.db.exists("DocType", "SMRITI Integration Queue"):
            return []
        
        return frappe.get_all(
            "SMRITI Integration Queue",
            filters={"status": ["in", ["Pending", "Retrying"]]},
            fields=["name", "event_type", "document_type", "document_name", 
                    "adapter_id", "payload", "priority", "status", "retry_count", "last_attempt"],
            order_by="case when priority='Critical' then 1 when priority='Normal' then 2 else 3 end, creation asc",
            limit=limit
        )

    @staticmethod
    def update_queue_status(queue_id: str, status: str, retry_count: int, error_msg: str = None):
        """Updates queue item status, retry increments and errors."""
        frappe.db.set_value(
            "SMRITI Integration Queue",
            queue_id,
            {
                "status": status,
                "retry_count": retry_count,
                "last_attempt": frappe.utils.now_datetime(),
                "error_details": error_msg or ""
            }
        )

    @staticmethod
    def log_audit_entry(queue_id: str, adapter_id: str, event_type: str, doc_type: str, doc_name: str, payload: dict, success: bool, response_id: str = None, error: str = None, duration_ms: int = 0):
        """Writes execution detail log to SMRITI Integration Audit Log."""
        # Check if audit log DocType exists before inserting, fallback to general tally sync log if needed
        doctype_name = "SMRITI Integration Audit Log"
        if not frappe.db.exists("DocType", doctype_name):
            if adapter_id == "accounting.tally" and frappe.db.exists("DocType", "SMRITI Tally Sync Log"):
                doctype_name = "SMRITI Tally Sync Log"
            else:
                # If neither exists, write to standard Frappe Log
                frappe.log_error(
                    title=f"[SMRITI Connect] Sync Log: {event_type} - {doc_name}",
                    message=f"Adapter: {adapter_id}\nSuccess: {success}\nResponse ID: {response_id}\nError: {error}\nDuration: {duration_ms}ms"
                )
                return

        # Insert structured log entry
        log_doc = frappe.get_doc({
            "doctype": doctype_name,
            "queue_reference": queue_id,
            "adapter_id": adapter_id,
            "event_type": event_type,
            "document_type": doc_type,
            "document_name": doc_name,
            "status": "Success" if success else "Failed",
            "response_transaction_id": response_id or "",
            "error_log": error or "",
            "sync_duration": duration_ms,
            "sync_timestamp": frappe.utils.now_datetime()
        })
        log_doc.insert(ignore_permissions=True)

    @staticmethod
    def get_queue_statistics() -> list[dict]:
        """Runs group query to summarize queue totals by status."""
        return frappe.db.sql(
            """
            select status, count(*) as count 
            from `tabSMRITI Integration Queue` 
            group by status
            """, 
            as_dict=True
        )

    @staticmethod
    def reset_queue_item(queue_id: str):
        """Resets the state of a queue item to allow immediate retry."""
        frappe.db.set_value("SMRITI Integration Queue", queue_id, {
            "status": "Pending",
            "retry_count": 0,
            "error_details": ""
        })

