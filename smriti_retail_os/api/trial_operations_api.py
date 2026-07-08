# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/trial_operations_api.py
# @description: SMRITI Trial Operations — Automated daily scheduler jobs for
#               trial expiry, reminder emails, health checks, and stale
#               provisioning cleanup.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @sprint: 3B — Trial Operations & Subscription Lifecycle
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#
# SCHEDULER RESILIENCE DESIGN
# ────────────────────────────
# Each of the four jobs is wrapped in its own try/except block.
# A failure in one job does NOT prevent the others from running.
# All errors are logged to frappe.log_error and smriti.trial logger.
#
# REGISTERED JOBS (hooks.py scheduler_events → daily)
# ────────────────────────────────────────────────────
#   smriti_retail_os.api.trial_operations_api.expire_trials
#   smriti_retail_os.api.trial_operations_api.send_trial_reminders
#   smriti_retail_os.api.trial_operations_api.check_trial_health
#   smriti_retail_os.api.trial_operations_api.cleanup_failed_provisioning

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from datetime import datetime, timedelta

_LOG = frappe.logger('smriti.trial')

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_settings():
    """
    Load SMRITI Trial Settings (singleton).
    Falls back to safe defaults if not configured.
    """
    try:
        return frappe.get_single('SMRITI Trial Settings')
    except Exception:
        # Return a safe default object if settings DocType not yet migrated
        class _Defaults:
            reminder_days              = '7,3,1'
            reminder_email_sender      = 'support@erpnbook.com'
            stale_provisioning_hours   = 24
            admin_notification_email   = 'Administrator'
            enable_health_check        = 1
            health_check_log_days      = 30

            def get_reminder_days(self):
                return [7, 3, 1]

            def get_stale_hours(self):
                return 24

        return _Defaults()


def _write_ops_log(activation_name, step_name, step_status, step_message=''):
    """Write a Provision Log entry from an automated scheduler job."""
    try:
        from smriti_retail_os.api.trial_activation_api import (
            _generate_run_id, _write_provision_log,
        )
        run_id = _generate_run_id()
        _write_provision_log(activation_name, run_id, step_name, step_status,
                             step_message, operator='Administrator')
    except Exception as e:
        _LOG.warning(f'Ops log write failed [{activation_name}/{step_name}]: {e}')


def _update_lead_status(lead_name, new_status, note_line):
    """Update Trial Lead status and append note."""
    try:
        lead = smriti.documents.get('SMRITI Trial Lead', lead_name)
        if lead.status != new_status:
            lead.status = new_status
            lead.notes  = ((lead.notes or '') + '\n' + note_line).strip()
            lead.save(ignore_permissions=True)
    except Exception as e:
        smriti.errors.log_error(f'SMRITI OPS — Lead status update failed for {lead_name}: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# JOB 1: expire_trials
# ─────────────────────────────────────────────────────────────────────────────

def expire_trials():
    """
    Daily job: Mark Active/Activated trials past their trial_end_date as Expired.

    State transitions:
        Active    → Expired
        Activated → Expired

    Lifecycle event: TRIAL_EXPIRED
    Also updates the Trial Lead status → Expired.
    """
    try:
        _LOG.info('TRIAL_OPS: expire_trials() starting')

        expired = smriti.db.sql(
            """
            SELECT name, activation_reference, trial_lead, store_name, trial_end_date
            FROM   `tabSMRITI Trial Activation`
            WHERE  activation_status IN ('Active', 'Activated')
              AND  trial_end_date < NOW()
            """,
            as_dict=True,
        )

        count = 0
        for row in expired:
            try:
                activation = smriti.documents.get('SMRITI Trial Activation', row['name'])
                activation.activation_status = 'Expired'
                ts   = datetime.now().strftime('%Y-%m-%d %H:%M')
                note = (f'[{ts}] Scheduler: Trial expired | '
                        f'Was due: {row["trial_end_date"]}')
                activation.notes = ((activation.notes or '') + '\n' + note).strip()
                activation.save(ignore_permissions=True)

                # Update lead
                _update_lead_status(
                    row['trial_lead'], 'Expired',
                    f'[{ts}] Scheduler: Trial expired — {row["activation_reference"]}'
                )

                # Log
                _write_ops_log(row['name'], 'Trial Expired', 'Pass',
                               f'Expired at {row["trial_end_date"]}')

                _LOG.info(f'TRIAL_EXPIRED: {row["name"]} ({row["store_name"]})')
                count += 1

            except Exception as e:
                smriti.errors.log_error(f'SMRITI expire_trials row error [{row["name"]}]: {e}')

        smriti.db.commit()
        _LOG.info(f'TRIAL_OPS: expire_trials() completed — {count} trial(s) expired')

    except Exception as e:
        smriti.errors.log_error(f'SMRITI expire_trials() failed: {e}')
        _LOG.exception(f'expire_trials() outer exception: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# JOB 2: send_trial_reminders
# ─────────────────────────────────────────────────────────────────────────────

def send_trial_reminders():
    """
    Daily job: Send D-7, D-3, D-1 reminder emails to store owners approaching expiry.

    Duplicate prevention: reminder_Nd_sent flag is checked before sending.
    A reminder is only sent once per trial per interval.

    Configuration: reminder_days loaded from SMRITI Trial Settings (default 7,3,1).
    Lifecycle event: EMAIL_SENT
    """
    try:
        settings     = _get_settings()
        reminder_days = settings.get_reminder_days()
        sender        = getattr(settings, 'reminder_email_sender', 'support@erpnbook.com')

        _LOG.info(f'TRIAL_OPS: send_trial_reminders() starting | Days: {reminder_days}')

        # Reminder day → field name map
        flag_map = {7: 'reminder_7d_sent', 3: 'reminder_3d_sent', 1: 'reminder_1d_sent'}

        total_sent = 0
        today = datetime.now().date()

        for days_before in reminder_days:
            flag_field = flag_map.get(days_before)
            if not flag_field:
                # Dynamic day — add to flag_map if needed; skip for non-standard days
                _LOG.info(f'No flag field for D-{days_before} — skipping duplicate check')
                flag_field = None

            target_date = today + timedelta(days=days_before)

            candidates = smriti.db.sql(
                f"""
                SELECT name, activation_reference, store_name, owner_name,
                       mobile, trial_end_date, trial_lead
                FROM   `tabSMRITI Trial Activation`
                WHERE  activation_status IN ('Active', 'Activated')
                  AND  DATE(trial_end_date) = %s
                  {f"AND ({flag_field} IS NULL OR {flag_field} = 0)" if flag_field else ''}
                """,
                (target_date,),
                as_dict=True,
            )

            for row in candidates:
                try:
                    # Get owner email from Trial Lead
                    lead_email = smriti.db.get(
                        'SMRITI Trial Lead', row['trial_lead'], 'email'
                    ) or ''

                    recipients = [e for e in [lead_email] if e and '@' in e]
                    if not recipients:
                        _LOG.info(f'D-{days_before} reminder: no email for {row["name"]} — skipping')
                        # Still mark as sent to prevent re-processing
                    else:
                        _send_reminder_email(row, days_before, recipients, sender)
                        total_sent += 1
                        _LOG.info(f'D-{days_before} reminder sent: {row["name"]} → {recipients}')

                    # Mark flag to prevent duplicate sends
                    if flag_field:
                        smriti.db.set_value(
                            'SMRITI Trial Activation', row['name'],
                            flag_field, 1,
                            update_modified=False,
                        )

                    _write_ops_log(
                        row['name'], f'Reminder D-{days_before} Sent',
                        'Pass' if recipients else 'Skipped',
                        f'Recipients: {recipients or "none (no email on lead)"}',
                    )

                except Exception as e:
                    smriti.errors.log_error(
                        f'SMRITI send_trial_reminders row error [{row["name"]} D-{days_before}]: {e}'
                    )

        smriti.db.commit()
        _LOG.info(f'TRIAL_OPS: send_trial_reminders() completed — {total_sent} email(s) sent')

    except Exception as e:
        smriti.errors.log_error(f'SMRITI send_trial_reminders() failed: {e}')
        _LOG.exception(f'send_trial_reminders() outer exception: {e}')


def _send_reminder_email(row, days_before, recipients, sender):
    """Compose and queue a trial expiry reminder email."""
    end_str = (
        row['trial_end_date'].strftime('%d %b %Y')
        if hasattr(row['trial_end_date'], 'strftime')
        else str(row['trial_end_date'])
    )

    urgency = '🔴' if days_before == 1 else ('🟡' if days_before == 3 else '🔵')

    frappe.sendmail(
        recipients=recipients,
        sender=sender,
        subject=f'{urgency} Your SMRITI Trial expires in {days_before} day{"s" if days_before > 1 else ""} — {row["store_name"]}',
        message=(
            f'<p>Dear {row["owner_name"] or row["store_name"]},</p>'
            f'<p>This is a reminder that your <strong>SMRITI Retail OS trial</strong> '
            f'for <strong>{row["store_name"]}</strong> expires on '
            f'<strong>{end_str}</strong> — in <strong>{days_before} day{"s" if days_before > 1 else ""}</strong>.</p>'
            f'{"<p><strong>Your trial expires TOMORROW. Please contact us immediately to continue.</strong></p>" if days_before == 1 else ""}'
            f'<p>To upgrade or extend your trial, please contact us at '
            f'<a href="mailto:{sender}">{sender}</a>.</p>'
            f'<br/><p>Team SMRITI Retail OS<br/>AITDL — AI Technology & Development Lab</p>'
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# JOB 3: check_trial_health
# ─────────────────────────────────────────────────────────────────────────────

def check_trial_health():
    """
    Daily job: Aggregate trial pipeline health metrics and log summary.
    Saves an immutable SMRITI Trial Health Snapshot record in the database.
    """
    try:
        settings = _get_settings()
        if not getattr(settings, 'enable_health_check', 1):
            _LOG.info('TRIAL_OPS: check_trial_health() skipped (disabled in settings)')
            return

        _LOG.info('TRIAL_OPS: check_trial_health() starting')

        from smriti_retail_os.services import trial_service
        snapshot = trial_service.generate_health_snapshot(snapshot_type="Daily", operator="Scheduler")

        _LOG.info(
            f'TRIAL_HEALTH Scheduler complete: name={snapshot.name} '
            f'score={snapshot.health_score} interpretation={snapshot.interpretation}'
        )

    except Exception as e:
        smriti.errors.log_error(f'SMRITI check_trial_health() failed: {e}')
        _LOG.exception(f'check_trial_health() outer exception: {e}')


def _count_expiring(days):
    """Count Active/Activated trials expiring within N days from now."""
    rows = smriti.db.sql(
        """
        SELECT COUNT(*) AS cnt FROM `tabSMRITI Trial Activation`
        WHERE  activation_status IN ('Active', 'Activated')
          AND  trial_end_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
        """,
        (days,),
        as_dict=True,
    )
    return rows[0]['cnt'] if rows else 0


# ─────────────────────────────────────────────────────────────────────────────
# JOB 4: cleanup_failed_provisioning
# ─────────────────────────────────────────────────────────────────────────────

def cleanup_failed_provisioning():
    """
    Daily job: Detect activations stuck in 'Provisioning' state for longer than
    the configured stale threshold (default: 24 hours) and mark them Failed.

    Prevents stale records accumulating without administrator awareness.
    Notifies the admin_notification_email configured in SMRITI Trial Settings.

    Lifecycle event: PROVISION_FAILED (stale)
    """
    try:
        settings       = _get_settings()
        stale_hours    = settings.get_stale_hours()
        admin_email    = getattr(settings, 'admin_notification_email', 'Administrator')

        _LOG.info(f'TRIAL_OPS: cleanup_failed_provisioning() starting | Threshold: {stale_hours}h')

        cutoff = datetime.now() - timedelta(hours=stale_hours)

        stale = smriti.db.sql(
            """
            SELECT name, activation_reference, store_name, provision_run_id, modified
            FROM   `tabSMRITI Trial Activation`
            WHERE  activation_status = 'Provisioning'
              AND  modified < %s
            """,
            (cutoff,),
            as_dict=True,
        )

        if not stale:
            _LOG.info('TRIAL_OPS: cleanup_failed_provisioning() — no stale records found')
            return

        failed_names = []
        reason = f'Stale: stuck in Provisioning for > {stale_hours}h with no progress'

        for row in stale:
            try:
                activation = smriti.documents.get('SMRITI Trial Activation', row['name'])
                activation.activation_status  = 'Failed'
                activation.last_failure_reason = reason
                ts   = datetime.now().strftime('%Y-%m-%d %H:%M')
                note = f'[{ts}] Scheduler: {reason} | Run: {row["provision_run_id"] or "unknown"}'
                activation.notes = ((activation.notes or '') + '\n' + note).strip()
                activation.save(ignore_permissions=True)

                _write_ops_log(row['name'], 'Stale Provisioning Cleanup', 'Fail', reason)

                _LOG.warning(f'STALE_PROVISION: {row["name"]} ({row["store_name"]}) marked Failed')
                failed_names.append(f'{row["activation_reference"]} ({row["store_name"]})')

            except Exception as e:
                smriti.errors.log_error(
                    f'SMRITI cleanup_failed_provisioning row error [{row["name"]}]: {e}'
                )

        smriti.db.commit()

        # Notify administrator
        if failed_names:
            _notify_admin_stale(failed_names, stale_hours, admin_email)

        _LOG.info(
            f'TRIAL_OPS: cleanup_failed_provisioning() completed — '
            f'{len(failed_names)} stale record(s) marked Failed'
        )

    except Exception as e:
        smriti.errors.log_error(f'SMRITI cleanup_failed_provisioning() failed: {e}')
        _LOG.exception(f'cleanup_failed_provisioning() outer exception: {e}')


def _notify_admin_stale(failed_names, stale_hours, admin_email):
    """Send an administrator notification about stale provisioning records."""
    try:
        recipient = admin_email if '@' in str(admin_email) else 'support@erpnbook.com'
        frappe.sendmail(
            recipients=[recipient],
            subject=f'⚠️ SMRITI: {len(failed_names)} stale provisioning record(s) marked Failed',
            message=(
                f'<p>The following trial activations were stuck in the <strong>Provisioning</strong> '
                f'state for more than <strong>{stale_hours} hours</strong> and have been '
                f'automatically marked as <strong>Failed</strong>:</p>'
                f'<ul>{"".join(f"<li>{n}</li>" for n in failed_names)}</ul>'
                f'<p>Please review these in the <a href="/smriti-platform-admin">Platform Admin</a> '
                f'console and use the <strong>Retry Provision</strong> button to re-attempt.</p>'
                f'<br/><p>SMRITI Retail OS — Automated Operations Scheduler</p>'
            ),
        )
    except Exception as e:
        smriti.errors.log_error(f'SMRITI stale provisioning admin notification failed: {e}')
