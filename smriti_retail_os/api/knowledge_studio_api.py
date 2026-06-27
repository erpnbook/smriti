# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/knowledge_studio_api.py
# @description: SMRITI Knowledge Studio Backend APIs (Sprint SDC-003)
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.5
# @license: MIT
#

import sys
import os
import io
import json
import datetime
import frappe

# Append SDC directory to sys.path dynamically
def _get_ske_engine():
    app_path = frappe.get_app_path("smriti_retail_os")
    
    # Check for packaged sdc directory inside custom app
    sdc_path = os.path.join(app_path, "sdc")
    if not os.path.exists(sdc_path):
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        sdc_path = os.path.join(repo_root, "sdc")
    
    if sdc_path not in sys.path:
        sys.path.append(sdc_path)
        
    from ske import SMRITIKnowledgeEngine
    
    # Check for packaged docs/discovery inside custom app
    if os.path.exists(os.path.join(app_path, "docs", "discovery")):
        return SMRITIKnowledgeEngine(app_path)
    else:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        return SMRITIKnowledgeEngine(repo_root)

@frappe.whitelist()
def query_ske(query):
    """
    Search-First SKE Resolution: processes a query and returns a list
    of merged and prioritized KnowledgeObject dictionaries.
    """
    try:
        engine = _get_ske_engine()
        results = engine.resolve(query, output_format="structured")
        # Return serialized list of objects
        return [obj.to_dict() for obj in results]
    except Exception as e:
        frappe.log_error(message=str(e), title="SKE Query Resolution Failed")
        frappe.throw(f"Knowledge Engine Error: {str(e)}")

@frappe.whitelist()
def get_knowledge_studio_counts():
    """
    Returns live repository counts for the dashboard cards.
    Loads counts from compiler-generated JSONs to guarantee accuracy.
    """
    try:
        engine = _get_ske_engine()
        glossary = len(engine.get_ir("business_dictionary", []))
        fields = len(engine.get_ir("field_inventory", []))
        doctypes = len(engine.get_ir("doctype_inventory", []))
        apis = len(engine.get_ir("api_inventory", []))
        screens = len(engine.get_ir("screen_inventory", []))
        
        # Static formulas size
        formulas = 3
        
        # Get last scan time from discovery_manifest.json
        manifest_path = os.path.join(engine.discovery_dir, "discovery_manifest.json")
        last_scan = "N/A"
        if os.path.exists(manifest_path):
            mtime = os.path.getmtime(manifest_path)
            last_scan = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "glossary": glossary,
            "fields": fields,
            "doctypes": doctypes,
            "apis": apis,
            "screens": screens,
            "formulas": formulas,
            "last_scan": last_scan
        }
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to resolve Knowledge Studio counts")
        return {
            "glossary": 0, "fields": 0, "doctypes": 0, "apis": 0, "screens": 0, "formulas": 0, "last_scan": "Error"
        }

@frappe.whitelist()
def explain_screen_by_route(route_path):
    """
    Resolves a tiered screen explanation payload based on the route pathname.
    """
    try:
        engine = _get_ske_engine()
        # Find screen matching the route path
        screens = engine.get_ir("screen_inventory", [])
        matched = None
        
        clean_path = route_path.strip("/ ").lower()
        for s in screens:
            s_route = s.get("route", "").strip("/ ").lower()
            s_id = s.get("screen_id", "").lower()
            if clean_path == s_route or clean_path == s_id or clean_path.replace("-", "_") == s_id or clean_path.replace("_", "-") == s_id:
                matched = s
                break
                
        if not matched:
            return {
                "found": False,
                "route": route_path,
                "message": f"No verified screen narratives found for route: {route_path}"
            }
            
        return {
            "found": True,
            "title": matched.get("title"),
            "route": matched.get("route"),
            "doctype": matched.get("doctype"),
            "fields": matched.get("fields", []),
            "apis": matched.get("apis", []),
            "reports": matched.get("reports", []),
            "labels": matched.get("labels", []),
            "beginner": matched.get("beginner", {}),
            "power_user": matched.get("power_user", {}),
            "developer": matched.get("developer", {})
        }
    except Exception as e:
        frappe.log_error(message=str(e), title="Explain Screen Failed")
        frappe.throw(f"Explain Screen Error: {str(e)}")

@frappe.whitelist()
def get_ske_meta():
    """
    Returns SDC/SKE meta version, commit info and registry statistics.
    """
    try:
        engine = _get_ske_engine()
        # Read manifest file directly for commit and scan timestamp
        manifest_path = os.path.join(engine.discovery_dir, "discovery_manifest.json")
        commit_sha = "N/A"
        scan_time = "N/A"
        
        if os.path.exists(manifest_path):
            with io.open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            commit_sha = manifest.get("repository_commit", "N/A")
            scan_time = manifest.get("generated_at", "N/A")

        return {
            "ske_version": "1.1.2-GA",
            "ir_version": "1.2",
            "repository_commit": commit_sha[:8] if commit_sha != "UNKNOWN_COMMIT" else "UNKNOWN",
            "last_scan": scan_time
        }
    except Exception:
        return {
            "ske_version": "1.1.2-GA",
            "ir_version": "1.2",
            "repository_commit": "N/A",
            "last_scan": "N/A"
        }

@frappe.whitelist()
def log_telemetry_event(event_type, query=None, target_asset=None, has_result=1, resolution_time_ms=0, provider_hit=None, confidence_source=None):
    """Logs SMRITI Knowledge platform telemetry search/open/explain events."""
    try:
        doc = frappe.get_doc({
            "doctype": "SMRITI Knowledge Usage Log",
            "event_type": event_type,
            "query": query,
            "target_asset": target_asset,
            "has_result": int(has_result),
            "resolution_time_ms": int(resolution_time_ms),
            "provider_hit": provider_hit,
            "confidence_source": confidence_source,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now_datetime()
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "name": doc.name}
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to log telemetry event")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_telemetry_logs(limit=50, has_result=None):
    """Fetches telemetry usage logs for audit or backlog review."""
    filters = {}
    if has_result is not None:
        filters["has_result"] = int(has_result)
    return frappe.get_all(
        "SMRITI Knowledge Usage Log",
        filters=filters,
        fields=["name", "event_type", "query", "target_asset", "has_result", "resolution_time_ms", "provider_hit", "confidence_source", "user", "timestamp"],
        order_by="timestamp desc",
        limit=int(limit)
    )

@frappe.whitelist()
def trigger_telemetry_cleanup():
    """Manually triggers the daily telemetry cleanup job and returns status."""
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
        
    from smriti_retail_os.tasks import daily_telemetry_cleanup
    daily_telemetry_cleanup()
    return {"success": True, "message": "Telemetry cleanup completed successfully."}

@frappe.whitelist()
def get_explainable_health():
    """Exposes the explainable health score breakdown."""
    try:
        engine = _get_ske_engine()
        return engine.get_health()
    except Exception as e:
        frappe.throw(f"Failed to fetch health status: {str(e)}")

@frappe.whitelist()
def get_collections():
    """Exposes logical collections inventory."""
    try:
        engine = _get_ske_engine()
        return engine.get_ir("collections_inventory", [])
    except Exception as e:
        frappe.throw(f"Failed to fetch collections: {str(e)}")
