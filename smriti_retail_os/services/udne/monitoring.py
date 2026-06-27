import frappe
import datetime
from smriti_retail_os.services.udne.gap_scanner import scan_gaps

def get_metrics(timespan: str = "Today") -> dict:
    """
    Retrieves performance and volume metrics for UDNE based on timespan.
    """
    filters = {}
    now = datetime.datetime.now()
    
    if timespan == "Today":
        filters["timestamp"] = [">=", now.replace(hour=0, minute=0, second=0, microsecond=0)]
    elif timespan == "Last 7 Days":
        filters["timestamp"] = [">=", now - datetime.timedelta(days=7)]
        
    logs = frappe.get_all(
        "SMRITI Numbering Audit Log",
        fields=["generation_duration_ms", "retry_count", "generation_mode"],
        filters=filters
    )
    
    total = len(logs)
    if not total:
        return {
            "timespan": timespan,
            "total_generations": 0,
            "average_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "slowest_generation_ms": 0.0,
            "collision_retries": 0,
            "manual_overrides": 0
        }
        
    latencies = sorted([float(l.generation_duration_ms or 0.0) for l in logs])
    avg_latency = round(sum(latencies) / total, 2)
    max_latency = round(latencies[-1], 2)
    
    # 95th percentile
    p95_idx = int(total * 0.95)
    p95_latency = round(latencies[p95_idx] if p95_idx < total else latencies[-1], 2)
    
    retries = sum(int(l.retry_count or 0) for l in logs)
    overrides = sum(1 for l in logs if l.generation_mode == "Manual")
    
    return {
        "timespan": timespan,
        "total_generations": total,
        "average_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "slowest_generation_ms": max_latency,
        "collision_retries": retries,
        "manual_overrides": overrides
    }

def get_health() -> dict:
    """
    Computes overall UDNE subsystem operational health summary.
    """
    # Active vs Disabled rules
    active_rules = frappe.db.count("SMRITI Numbering Rule", {"is_active": 1})
    disabled_rules = frappe.db.count("SMRITI Numbering Rule", {"is_active": 0})
    
    # Rules expiring soon (< 30 days)
    now_date = datetime.date.today()
    expiring_soon = frappe.db.count(
        "SMRITI Numbering Rule",
        {
            "is_active": 1,
            "effective_until": ["between", [now_date, now_date + datetime.timedelta(days=30)]]
        }
    )
    
    # Reservations status
    res_status = frappe.db.sql("""
        select status, count(*) as count from `tabSMRITI Numbering Reserved Range` group by status
    """, as_dict=1)
    
    res_counts = {row["status"]: row["count"] for row in res_status}
    
    # Explainability score (based on audit logs explain completeness)
    logs = frappe.get_all("SMRITI Numbering Audit Log", fields=["rule", "template", "context_details"], limit=100)
    total_logs = len(logs)
    score_sum = 0
    if total_logs:
        for l in logs:
            score = 100
            if not l.rule: score -= 20
            if not l.template: score -= 20
            if not l.context_details: score -= 30
            score_sum += score
        avg_explain_score = round(score_sum / total_logs, 1)
    else:
        avg_explain_score = 100.0
        
    return {
        "active_rules": active_rules,
        "disabled_rules": disabled_rules,
        "rules_expiring_soon": expiring_soon,
        "reservations": {
            "active": res_counts.get("Active", 0) + res_counts.get("Allocated", 0),
            "exhausted": res_counts.get("Exhausted", 0),
            "expired": res_counts.get("Expired", 0),
            "recoverable": res_counts.get("Expired", 0)  # Reclaimable
        },
        "explainability_score": avg_explain_score
    }

def get_gaps(target_doctype: str = None) -> list:
    """
    Scans and returns sequence gaps for active numbering rules.
    """
    filters = {"is_active": 1}
    if target_doctype:
        filters["document_type"] = target_doctype
        
    rules = frappe.get_all("SMRITI Numbering Rule", fields=["name", "document_type"], filters=filters)
    all_gaps = []
    
    for r in rules:
        gaps = scan_gaps(r.document_type, r.name)
        for g in gaps:
            g["document_type"] = r.document_type
            g["rule"] = r.name
            all_gaps.append(g)
            
    return all_gaps

def get_reservations() -> list:
    """
    Returns detailed reservation lifecycle records with utilization ratios.
    """
    ranges = frappe.get_all(
        "SMRITI Numbering Reserved Range",
        fields=["name", "document_type", "terminal_id", "start_number", "end_number", "current_counter", "status", "expiry_datetime"],
        order_by="creation desc"
    )
    
    results = []
    for r in ranges:
        total = r.end_number - r.start_number + 1
        consumed = (r.current_counter - r.start_number) if r.current_counter >= r.start_number else 0
        util_ratio = round((consumed / total) * 100.0, 1) if total else 0.0
        
        results.append({
            "reservation_id": r.name,
            "document_type": r.document_type,
            "terminal_id": r.terminal_id,
            "start": r.start_number,
            "end": r.end_number,
            "current": r.current_counter,
            "status": r.status,
            "expiry": str(r.expiry_datetime),
            "utilization": util_ratio
        })
    return results
