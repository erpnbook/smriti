# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/trial_service.py
# @description: SMRITI Trial Operations Service — aggregates pipeline metrics,
#               calculates the pipeline health score, and generates snapshots.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.8.6
# @sprint: 3C — Trial Health Snapshot
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
from datetime import datetime, timedelta

_LOG = frappe.logger('smriti.trial')


def calculate_trial_health_score(active, failed, avg_sla_hours, target_sla=4.0, penalty_mult=5.0, max_penalty=20.0):
    """
    Calculate the Trial Pipeline Health Score (TR-HLTH-01).
    
    Formula:
      Success Rate = (Active / (Active + Failed)) * 100
      Penalty = Min(max_penalty, Max(0.0, (avg_sla_hours - target_sla) * penalty_mult))
      Health Score = Max(0.0, Success Rate - Penalty)
      
    Edge cases:
      - Active = 0, Failed = 0 -> Health = 100.0 (no trials started/failed yet)
      - Active = 0, Failed > 0 -> Health = 0.0
    """
    active = float(active)
    failed = float(failed)
    
    if active == 0.0 and failed == 0.0:
        return 100.0
        
    if active == 0.0 and failed > 0.0:
        return 0.0
        
    success_rate = (active / (active + failed)) * 100.0
    
    if avg_sla_hours is not None and avg_sla_hours > target_sla:
        penalty = min(float(max_penalty), max(0.0, (float(avg_sla_hours) - float(target_sla)) * float(penalty_mult)))
    else:
        penalty = 0.0
        
    health_score = max(0.0, success_rate - penalty)
    return round(health_score, 2)


def get_health_config():
    """
    Load parameters for TR-HLTH-01 from SMRITI Trial Settings.
    Falls back to constitutional defaults if settings or fields are not present.
    """
    defaults = {
        "target_sla": 4.0,
        "penalty_mult": 5.0,
        "max_penalty": 20.0
    }
    try:
        settings = frappe.get_single('SMRITI Trial Settings')
        target = getattr(settings, 'health_target_sla_hours', None)
        mult = getattr(settings, 'health_sla_penalty_multiplier', None)
        mx = getattr(settings, 'health_max_sla_penalty', None)
        
        return {
            "target_sla": float(target) if target is not None else defaults["target_sla"],
            "penalty_mult": float(mult) if mult is not None else defaults["penalty_mult"],
            "max_penalty": float(mx) if mx is not None else defaults["max_penalty"]
        }
    except Exception:
        return defaults


def generate_health_snapshot(snapshot_type="Daily", operator=None):
    """
    Collects raw trial activation metrics, computes the pipeline health score,
    determines the interpretation, and inserts an immutable SMRITI Trial Health Snapshot record.
    """
    try:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = now.replace(hour=23, minute=59, second=59)

        # 1. Collect Metrics
        active = frappe.db.count('SMRITI Trial Activation', {'activation_status': ['in', ['Active', 'Activated']]})
        failed = frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Failed'})
        pending = frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Pending'})
        provisioning = frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Provisioning'})
        converted_total = frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Converted to Paid'})
        
        # Expiring within N days
        expiring_7d = _count_expiring(7)
        expiring_3d = _count_expiring(3)
        expiring_1d = _count_expiring(1)
        
        # Expired today
        expired_today = frappe.db.count('SMRITI Trial Activation', {
            'activation_status': 'Expired',
            'modified': ['between', [today_start, today_end]]
        })

        # Calculate average SLA (Converted modified -> trial_start_date)
        sla_rows = frappe.db.sql(
            """
            SELECT AVG(TIMESTAMPDIFF(MINUTE, tl.modified, ta.trial_start_date)) AS avg_minutes
            FROM `tabSMRITI Trial Activation` ta
            JOIN `tabSMRITI Trial Lead`       tl ON tl.name = ta.trial_lead
            WHERE ta.activation_status IN ('Active', 'Activated', 'Expired', 'Converted to Paid')
              AND ta.trial_start_date IS NOT NULL
            """,
            as_dict=True,
        )
        avg_min = sla_rows[0]['avg_minutes'] if sla_rows and sla_rows[0]['avg_minutes'] else None
        avg_sla_hours = round(float(avg_min) / 60.0, 2) if avg_min is not None else None

        # 2. Compute Health Score
        config = get_health_config()
        health_score = calculate_trial_health_score(
            active, failed, avg_sla_hours,
            target_sla=config["target_sla"],
            penalty_mult=config["penalty_mult"],
            max_penalty=config["max_penalty"]
        )

        # Determine Interpretation Band
        if health_score >= 80.0:
            interpretation = "Healthy"
        elif health_score >= 50.0:
            interpretation = "Monitor"
        else:
            interpretation = "Critical"

        # 3. Create Immutable Snapshot Record
        doc = frappe.get_doc({
            "doctype": "SMRITI Trial Health Snapshot",
            "snapshot_date": now.date(),
            "snapshot_time": now,
            "snapshot_type": snapshot_type,
            "active_trials": active,
            "expiring_7d": expiring_7d,
            "expiring_3d": expiring_3d,
            "expiring_1d": expiring_1d,
            "expired_today": expired_today,
            "failed_provisioning": failed,
            "pending_queue": pending,
            "provisioning": provisioning,
            "converted_total": converted_total,
            "sla_avg_hours": avg_sla_hours or 0.0,
            "health_score": health_score,
            "interpretation": interpretation,
            "snapshot_version": "1.0",
            "formula_version": "1.0",
            "generated_by": operator or frappe.session.user or "Administrator"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        _LOG.info(
            f"TRIAL_HEALTH_SNAPSHOT: Created snapshot ({doc.name}) | "
            f"Type: {snapshot_type} | Score: {health_score} ({interpretation}) | "
            f"Active: {active} | Failed: {failed} | SLA: {avg_sla_hours}h"
        )
        return doc
        
    except Exception as e:
        frappe.log_error(title="SMRITI generate_health_snapshot Failed", message=frappe.get_traceback())
        _LOG.exception(f"generate_health_snapshot error: {e}")
        raise e


def _count_expiring(days):
    """Count Active/Activated trials expiring within N days from now."""
    rows = frappe.db.sql(
        """
        SELECT COUNT(*) AS cnt FROM `tabSMRITI Trial Activation`
        WHERE  activation_status IN ('Active', 'Activated')
          AND  trial_end_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
        """,
        (days,),
        as_dict=True,
    )
    return rows[0]['cnt'] if rows else 0
