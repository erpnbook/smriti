# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/trial_activation_api.py
# @description: SMRITI Trial Activation API — Provisioning lifecycle, state machine,
#               provision log, retry mechanism, and dashboard metrics.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)
# @sprint: 3B — Trial Operations & Subscription Lifecycle
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#
# STATE MACHINE
# ─────────────
# Pending → Provisioning → Provisioned → Activated
#                      ↘ Failed ← (any critical step fails)
# Activated → Suspended → Activated (via extend_trial / retry)
# Activated → Expired (daily scheduler)
# Activated → Converted to Paid (manual)
# Failed → Provisioning (via retry_provision)
# Active (legacy) treated as Activated for backward compatibility
#
# LIFECYCLE EVENTS (for future analytics)
# ────────────────────────────────────────
# TRIAL_CREATED, PROVISION_STARTED, COMPANY_CREATED, WAREHOUSE_CREATED,
# USER_CREATED, EMAIL_SENT, PROVISION_COMPLETED, TRIAL_STARTED,
# TRIAL_SUSPENDED, TRIAL_RESUMED, TRIAL_EXPIRED, TRIAL_CONVERTED

import frappe
from frappe import _
from datetime import datetime, timedelta
from smriti_retail_os import smriti


_LOG = frappe.logger('smriti.trial')


# ─────────────────────────────────────────────────────────────────────────────
# PROVISION LOG HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _generate_run_id():
    """
    Return a unique RUN-YYYY-NNNNNN run identifier.
    Groups all provision log steps for a single activation attempt.
    """
    year = datetime.now().year
    last = smriti.db.sql(
        """
        SELECT name FROM `tabSMRITI Provision Log`
        WHERE  run_id LIKE %s
        ORDER  BY creation DESC
        LIMIT  1
        """,
        (f'RUN-{year}-%',),
    )
    if last and last[0][0]:
        try:
            seq = int(last[0][0].split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'RUN-{year}-{seq:06d}'


_step_sequences = {}  # run_id → current sequence counter


def _write_provision_log(activation_name, run_id, step_name, step_status,
                         step_message='', operator=None):
    """
    Append one step record to SMRITI Provision Log.
    Each call increments step_sequence within the run_id group.

    Parameters
    ----------
    activation_name : str
    run_id          : str   e.g. 'RUN-2026-000001'
    step_name       : str   e.g. 'Company Created'
    step_status     : str   'Pass' | 'Fail' | 'Skipped' | 'Pending'
    step_message    : str   Error detail or success note
    operator        : str   User email (defaults to frappe.session.user)
    """
    global _step_sequences
    seq = _step_sequences.get(run_id, 0) + 1
    _step_sequences[run_id] = seq

    try:
        log = smriti.documents.new("ProvisionLog")
        log.update({
            'activation':    activation_name,
            'run_id':        run_id,
            'step_sequence': seq,
            'step_name':     step_name,
            'step_status':   step_status,
            'step_message':  step_message or '',
            'step_time':     datetime.now(),
            'operator':      operator or frappe.session.user,
        })
        log.insert(ignore_permissions=True)
        smriti.db.commit()
    except Exception as e:
        _LOG.warning(f'PLOG write failed [{run_id}/{step_name}]: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# PREFLIGHT CHECKS
# ─────────────────────────────────────────────────────────────────────────────

def _preflight_checks(activation, company_name):
    """
    Comprehensive duplicate/conflict detection before any provisioning.

    Returns list of conflict strings. Empty list = safe to proceed.

    Checks:
    1.  Company with same name already exists in ERPNext
    2.  Trial User email derived from mobile already exists
    3.  Another Active/Provisioning/Provisioned/Activated activation for same Lead
    4.  Warehouse for this company already exists (warn, not block)
    5.  Customer Group for this company already exists (warn, not block)
    6.  Mobile number collision across existing activations
    7.  Any existing Trial Lead in 'Trial Started' status for same mobile
    """
    conflicts = []
    mobile = (activation.mobile or '').lstrip('+').replace(' ', '')
    abbr   = _derive_abbr(company_name)
    email  = f'trial.{mobile}@smriti.local'

    # 1. Company
    if smriti.db.exists("ERPCompany", company_name):
        conflicts.append(f'ERPNext Company "{company_name}" already exists')

    if smriti.db.exists("SystemUser", email):
        conflicts.append(f'Trial user "{email}" already exists')

    # 3. Duplicate activation for same lead
    existing = smriti.db.get(
        "TrialActivation",
        {
            'trial_lead': activation.trial_lead,
            'activation_status': ['in', ['Active', 'Activated', 'Provisioning', 'Provisioned']],
            'name': ['!=', activation.name],
        },
        'name',
    )
    if existing:
        conflicts.append(f'Another active activation ({existing}) exists for this lead')

    # 4. Warehouse (warn only — prepend W:)
    wh_name = f'Main Store - {abbr}'
    if smriti.db.exists("ERPWarehouse", wh_name):
        conflicts.append(f'W:Warehouse "{wh_name}" already exists — will skip creation')

    # 5. Customer Group (warn only — prepend W:)
    cg_name = f'{company_name} — Retail Customers'
    if smriti.db.exists("ERPCustomerGroup", cg_name):
        conflicts.append(f'W:Customer Group "{cg_name}" already exists — will skip creation')

    # 6. Mobile collision
    if mobile:
        mob_hit = smriti.db.get(
            "TrialActivation",
            {
                'mobile': ['like', f'%{mobile}%'],
                'activation_status': ['in', ['Active', 'Activated']],
                'name': ['!=', activation.name],
            },
            'name',
        )
        if mob_hit:
            conflicts.append(f'Mobile {mobile} already associated with activation {mob_hit}')

    # 7. Lead already Trial Started
    lead_status = smriti.db.get("TrialLead", activation.trial_lead, "status")
    if lead_status in ('Trial Started', 'Expired'):
        conflicts.append(f'Lead status is already "{lead_status}"')

    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
# CREATE — New Activation (Lead → Activation)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_converted_leads():
    """Return Trial Leads with status 'Converted' that have no pending/active activation."""
    converted = smriti.db.get_list(
        "TrialLead",
        filters={'status': 'Converted'},
        fields=['name', 'store_name', 'owner_name', 'mobile', 'city',
                'email', 'plan_selected', 'creation'],
        order_by='creation asc',
    )

    # Filter out leads that already have an activation in progress
    active_statuses = ('Pending', 'Provisioning', 'Provisioned', 'Activated', 'Active')
    result = []
    for lead in converted:
        has_activation = smriti.db.exists(
            "TrialActivation",
            {'trial_lead': lead['name'], 'activation_status': ['in', active_statuses]},
        )
        if not has_activation:
            result.append(lead)
    return result


@frappe.whitelist()
def create_activation(lead_name, activation_type='Trial', trial_days=30):
    """
    Create a new SMRITI Trial Activation record (status=Pending) for a Converted lead.
    Idempotent: returns existing activation if one already exists.

    Lifecycle event: TRIAL_CREATED
    """
    lead = smriti.documents.get("TrialLead", lead_name)

    existing = smriti.db.get(
        "TrialActivation",
        {'trial_lead': lead_name},
        'name',
    )
    if existing:
        return {
            'status':     'duplicate',
            'activation': existing,
            'message':    f'Activation already exists: {existing}',
        }

    activation = smriti.documents.new("TrialActivation")
    activation.update({
        'activation_type':  activation_type,
        'trial_lead':       lead_name,
        'store_name':       lead.store_name,
        'owner_name':       lead.owner_name,
        'mobile':           lead.mobile,
        'activation_status': 'Pending',
        'retry_count':      0,
        'checklist': [
            {'task_name': 'Company Created',        'is_done': 0},
            {'task_name': 'Warehouse Created',       'is_done': 0},
            {'task_name': 'Customer Group Created',  'is_done': 0},
            {'task_name': 'User Created',            'is_done': 0},
            {'task_name': 'Welcome Email Sent',      'is_done': 0},
        ],
    })
    # reviewed-ignore-permissions: trial activation lifecycle, system-controlled status updates
    activation.insert(ignore_permissions=True)
    smriti.db.commit()

    _LOG.info(f'TRIAL_CREATED: {activation.name} for lead {lead_name}')

    return {
        'status':     'success',
        'activation': activation.name,
        'reference':  activation.activation_reference,
        'message':    f'Activation {activation.activation_reference} created.',
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROVISION — Activate account (Company + Warehouse + User)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def activate_account(activation_name, company_name=None, trial_days=30):
    """
    Provision a new ERPNext Company, Warehouse, Customer Group, and trial User,
    then mark the activation as Activated.

    State: Pending → Provisioning → Provisioned → Activated
           Provisioning → Failed (on critical error)

    Lifecycle events: PROVISION_STARTED, COMPANY_CREATED, WAREHOUSE_CREATED,
                      USER_CREATED, PROVISION_COMPLETED, TRIAL_STARTED
    """
    activation = smriti.documents.get('TrialActivation', activation_name)

    if activation.activation_status in ('Active', 'Activated'):
        frappe.throw(_('This activation is already Active/Activated.'))

    # Derive company name from store_name if not provided
    if not company_name:
        company_name = activation.store_name.strip()

    # ── Pre-flight checks ─────────────────────────────────────────────────────
    conflicts = _preflight_checks(activation, company_name)
    hard_conflicts = [c for c in conflicts if not c.startswith('W:')]
    if hard_conflicts:
        return {
            'status':    'conflict',
            'conflicts': hard_conflicts,
            'warnings':  [c[2:] for c in conflicts if c.startswith('W:')],
            'message':   'Pre-flight checks failed. Resolve conflicts before activating.',
        }

    # ── Begin Provision Run ───────────────────────────────────────────────────
    run_id = _generate_run_id()
    operator = frappe.session.user

    # Transition: → Provisioning
    activation.activation_status = 'Provisioning'
    activation.provision_run_id  = run_id
    activation.retry_count       = int(activation.retry_count or 0)
    # reviewed-ignore-permissions: trial activation lifecycle, system-controlled status updates
    activation.save(ignore_permissions=True)
    smriti.db.commit()

    _LOG.info(f'PROVISION_STARTED: {activation_name} | Run: {run_id} | Attempt #{activation.retry_count + 1}')
    _write_provision_log(activation_name, run_id, 'Provision Started', 'Pass',
                         f'Attempt #{activation.retry_count + 1} — Company: {company_name}', operator)

    warnings   = [c[2:] for c in conflicts if c.startswith('W:')]
    step_errors = []

    # ── Step 1: Company ───────────────────────────────────────────────────────
    co_name = _ensure_company(company_name, step_errors)
    if any('Company' in e for e in step_errors):
        _write_provision_log(activation_name, run_id, 'Company Created', 'Fail',
                             step_errors[-1], operator)
        return _fail_activation(activation, run_id, step_errors[-1])
    _write_provision_log(activation_name, run_id, 'Company Created', 'Pass',
                         f'Company: {co_name}', operator)

    # ── Step 2: Warehouse ─────────────────────────────────────────────────────
    wh_name = _ensure_warehouse(co_name, step_errors)
    wh_status = 'Skipped' if any('Warehouse' in e for e in warnings) else 'Pass'
    _write_provision_log(activation_name, run_id, 'Warehouse Created', wh_status,
                         f'Warehouse: {wh_name}', operator)

    # ── Step 3: Customer Group ────────────────────────────────────────────────
    cg_name = _ensure_customer_group(co_name, step_errors)
    cg_status = 'Skipped' if any('Customer Group' in e for e in warnings) else 'Pass'
    _write_provision_log(activation_name, run_id, 'Customer Group Created', cg_status,
                         f'Group: {cg_name}', operator)

    # ── Step 4: Trial User ────────────────────────────────────────────────────
    user_email = _ensure_trial_user(activation, co_name, step_errors)
    if any('User creation' in e for e in step_errors):
        _write_provision_log(activation_name, run_id, 'User Created', 'Fail',
                             step_errors[-1], operator)
        return _fail_activation(activation, run_id, step_errors[-1])
    _write_provision_log(activation_name, run_id, 'User Created', 'Pass',
                         f'User: {user_email}', operator)

    # ── Step 5: Welcome Email (non-critical — failure doesn't block) ──────────
    email_ok = _send_welcome_email(activation, co_name, user_email)
    _write_provision_log(activation_name, run_id, 'Welcome Email Sent',
                         'Pass' if email_ok else 'Fail',
                         'Email queued' if email_ok else 'Email skipped — no SMTP configured',
                         operator)

    # ── Finalize: Provisioned → Activated ────────────────────────────────────
    now      = datetime.now()
    end_date = now + timedelta(days=int(trial_days))

    activation.reload()
    activation.company_name       = co_name
    activation.activation_status  = 'Activated'
    activation.trial_start_date   = now
    activation.trial_end_date     = end_date
    activation.activated_by       = operator
    activation.retry_count        = int(activation.retry_count or 0) + 1
    activation.last_failure_reason = ''

    # Mark checklist items
    _tick_checklist(activation, now, operator, [
        'Company Created', 'Warehouse Created', 'Customer Group Created', 'User Created',
    ] + (['Welcome Email Sent'] if email_ok else []))

    # reviewed-ignore-permissions: no role restriction — any authenticated user may activate account, by design
    activation.save(ignore_permissions=True)

    # Update Trial Lead → Trial Started
    _update_lead_status(activation.trial_lead, 'Trial Started',
                        f'[{now.strftime("%Y-%m-%d %H:%M")}] {operator}: '
                        f'Trial Started | Ref: {activation.activation_reference} | '
                        f'Run: {run_id} | Company: {co_name}')

    smriti.db.commit()

    _write_provision_log(activation_name, run_id, 'Provision Completed', 'Pass',
                         f'Activated → trial until {end_date.strftime("%d %b %Y")}', operator)

    _LOG.info(f'TRIAL_STARTED: {activation_name} | Company: {co_name} | End: {end_date.date()}')

    return {
        'status':     'success',
        'activation': activation.name,
        'reference':  activation.activation_reference,
        'company':    co_name,
        'run_id':     run_id,
        'trial_days': int(trial_days),
        'trial_end':  str(end_date.date()),
        'warnings':   warnings,
        'message':    f'Account activated! Trial runs until {end_date.strftime("%d %b %Y")}.',
    }


def _fail_activation(activation, run_id, reason):
    """Transition activation to Failed state. Records reason for explainability."""
    _write_provision_log(activation.name, run_id, 'Provision Failed', 'Fail', reason)
    activation.reload()
    activation.activation_status  = 'Failed'
    activation.last_failure_reason = reason
    activation.save(ignore_permissions=True)
    smriti.db.commit()
    _LOG.error(f'PROVISION_FAILED: {activation.name} | Run: {run_id} | Reason: {reason}')
    return {
        'status':  'failed',
        'run_id':  run_id,
        'reason':  reason,
        'message': f'Provisioning failed: {reason}',
    }


# ─────────────────────────────────────────────────────────────────────────────
# RETRY — Re-run provisioning for Failed activation
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def retry_provision(activation_name, company_name=None, trial_days=30):
    """
    Idempotent retry of activate_account() for a Failed or stale Provisioning activation.

    Each retry generates a new run_id (Attempt #N preserved in retry_count).
    The _ensure_* helpers are already idempotent — they skip if resource exists.

    Allowed states: Failed, Provisioning (stale)
    """
    activation = smriti.documents.get('TrialActivation', activation_name)

    if activation.activation_status not in ('Failed', 'Provisioning', 'Pending'):
        frappe.throw(_(
            f'Retry is only allowed for Failed or stale Provisioning activations. '
            f'Current status: {activation.activation_status}'
        ))

    # Reset to Pending so activate_account() can proceed cleanly
    activation.activation_status = 'Pending'
    # reviewed-ignore-permissions: trial activation lifecycle, system-controlled status updates
    activation.save(ignore_permissions=True)
    smriti.db.commit()

    _LOG.info(f'RETRY_PROVISION: {activation_name} | Attempt #{int(activation.retry_count or 0) + 1}')

    # Delegate to activate_account — unified provisioning path
    return activate_account(activation_name, company_name=company_name, trial_days=trial_days)


# ─────────────────────────────────────────────────────────────────────────────
# MANAGE — Suspend / Extend
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def suspend_activation(activation_name, reason=None):
    """Suspend an active trial. Records reason in notes for explainability."""
    activation = smriti.documents.get('TrialActivation', activation_name)

    if activation.activation_status not in ('Active', 'Activated'):
        frappe.throw(_(
            f'Only Active/Activated activations can be suspended. '
            f'Current: {activation.activation_status}'
        ))

    activation.activation_status = 'Suspended'
    ts   = datetime.now().strftime('%Y-%m-%d %H:%M')
    by   = frappe.session.user
    note = f'[{ts}] {by}: Suspended'
    if reason:
        note += f' — {reason.strip()}'
    activation.notes = ((activation.notes or '') + '\n' + note).strip()
    # reviewed-ignore-permissions: trial activation lifecycle, system-controlled status updates
    activation.save(ignore_permissions=True)
    smriti.db.commit()

    _LOG.info(f'TRIAL_SUSPENDED: {activation_name} | By: {by} | Reason: {reason}')
    return {'status': 'success', 'message': f'{activation_name} suspended.'}


@frappe.whitelist()
def extend_trial(activation_name, additional_days=7, reason=None):
    """Extend a trial by N additional days. Reactivates Suspended trials."""
    activation = smriti.documents.get('TrialActivation', activation_name)

    if activation.activation_status not in ('Active', 'Activated', 'Suspended'):
        frappe.throw(_('Can only extend Active, Activated, or Suspended trials.'))

    additional_days = int(additional_days)
    old_end = activation.trial_end_date or datetime.now()
    if isinstance(old_end, str):
        old_end = datetime.fromisoformat(old_end)

    new_end = old_end + timedelta(days=additional_days)
    activation.trial_end_date    = new_end
    activation.activation_status = 'Activated'

    ts   = datetime.now().strftime('%Y-%m-%d %H:%M')
    by   = frappe.session.user
    note = f'[{ts}] {by}: Trial extended +{additional_days}d → new end {new_end.strftime("%d %b %Y")}'
    if reason:
        note += f' | {reason.strip()}'
    activation.notes = ((activation.notes or '') + '\n' + note).strip()
    # reviewed-ignore-permissions: trial activation lifecycle, system-controlled status updates
    activation.save(ignore_permissions=True)
    smriti.db.commit()

    _LOG.info(f'TRIAL_RESUMED: {activation_name} | New end: {new_end.date()}')
    return {
        'status':   'success',
        'new_end':  str(new_end.date()),
        'message':  f'Trial extended to {new_end.strftime("%d %b %Y")}.',
    }


@frappe.whitelist()
def mark_converted_to_paid(activation_name):
    """
    Mark an Active/Activated/Suspended trial as Converted to Paid.

    State transition: Active|Activated|Suspended → Converted to Paid
    Also updates Trial Lead status → Converted.

    Lifecycle event: TRIAL_CONVERTED
    """
    activation = smriti.documents.get('TrialActivation', activation_name)

    if activation.activation_status not in ('Active', 'Activated', 'Suspended', 'Expired'):
        frappe.throw(_(
            f'Only Active, Activated, Suspended, or Expired trials can be converted. '
            f'Current: {activation.activation_status}'
        ))

    ts  = datetime.now().strftime('%Y-%m-%d %H:%M')
    by  = frappe.session.user
    note = f'[{ts}] {by}: Trial Converted to Paid subscription.'

    activation.activation_status = 'Converted to Paid'
    activation.notes = ((activation.notes or '') + '\n' + note).strip()
    # reviewed-ignore-permissions: no role restriction — any authenticated user may convert trial subscription, by design
    activation.save(ignore_permissions=True)

    # Update lead
    _update_lead_status(
        activation.trial_lead, 'Converted to Paid',
        f'[{ts}] {by}: Converted to Paid | Ref: {activation.activation_reference}'
    )

    smriti.db.commit()

    _LOG.info(f'TRIAL_CONVERTED: {activation_name} | By: {by}')
    return {
        'status':  'success',
        'message': f'{activation.store_name} successfully marked as Converted to Paid.',
    }


# ─────────────────────────────────────────────────────────────────────────────
# READ — Activations list + Provision Logs
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_activations(status=None, limit=100):
    """Return activation records, optionally filtered by status."""
    filters = {}
    if status:
        filters['activation_status'] = status

    rows = smriti.db.get_list(
        "TrialActivation",
        filters=filters,
        fields=[
            'name', 'activation_reference', 'activation_type',
            'trial_lead', 'store_name', 'owner_name', 'mobile',
            'company_name', 'activation_status',
            'trial_start_date', 'trial_end_date',
            'activated_by', 'creation',
            'provision_run_id', 'retry_count', 'last_failure_reason',
        ],
        order_by='creation desc',
        limit=int(limit),
    )

    now = datetime.now()
    for r in rows:
        end = r.get('trial_end_date')
        if end and r.get('activation_status') in ('Active', 'Activated'):
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            r['days_remaining'] = max(0, (end - now).days)
        else:
            r['days_remaining'] = None

    return rows


@frappe.whitelist()
def get_provision_logs(activation_name, run_id=None):
    """
    Return provision log steps for a given activation.
    If run_id provided, returns only that run.
    Otherwise returns all runs grouped by run_id (latest first).
    """
    filters = {'activation': activation_name}
    if run_id:
        filters['run_id'] = run_id

    logs = smriti.db.get_list(
        "ProvisionLog",
        filters=filters,
        fields=['name', 'run_id', 'step_sequence', 'step_name',
                'step_status', 'step_message', 'step_time', 'operator'],
        order_by='step_time asc',
        limit=500,
    )

    # Group by run_id
    runs = {}
    for row in logs:
        rid = row['run_id']
        if rid not in runs:
            runs[rid] = {'run_id': rid, 'steps': []}
        runs[rid]['steps'].append(row)

    # Return sorted by run_id desc (most recent run first)
    return sorted(runs.values(), key=lambda r: r['run_id'], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_activation_dashboard():
    """
    Pipeline counts, SLA metric, and health summary.
    Formula: SLA = AVG(TIMESTAMPDIFF(MINUTE, lead.modified, activation.trial_start_date)) / 60
    """
    lead_counts = {
        'converted_total': smriti.db.count('TrialLead', {'status': 'Converted'}),
        'trial_started':   smriti.db.count('TrialLead', {'status': 'Trial Started'}),
        'expired':         smriti.db.count('TrialLead', {'status': 'Expired'}),
    }

    act_counts = {
        'pending':           smriti.db.count('TrialActivation', {'activation_status': 'Pending'}),
        'provisioning':      smriti.db.count('TrialActivation', {'activation_status': 'Provisioning'}),
        'provisioned':       smriti.db.count('TrialActivation', {'activation_status': 'Provisioned'}),
        'active':            smriti.db.count('TrialActivation', {'activation_status': ['in', ['Active', 'Activated']]}),
        'suspended':         smriti.db.count('TrialActivation', {'activation_status': 'Suspended'}),
        'expired':           smriti.db.count('TrialActivation', {'activation_status': 'Expired'}),
        'failed':            smriti.db.count('TrialActivation', {'activation_status': 'Failed'}),
        'converted_to_paid': smriti.db.count('TrialActivation', {'activation_status': 'Converted to Paid'}),
    }

    act_counts['activation_queue'] = (
        lead_counts['converted_total'] + act_counts['pending']
    )

    expiring_rows = smriti.db.sql(
        """
        SELECT COUNT(*) AS cnt FROM `tabSMRITI Trial Activation`
        WHERE  activation_status IN ('Active', 'Activated')
          AND  trial_end_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
        """,
        as_dict=True,
    )
    act_counts['expiring_soon'] = expiring_rows[0]['cnt'] if expiring_rows else 0

    # SLA
    sla_rows = smriti.db.sql(
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
    if avg_min is not None:
        avg_hours = round(float(avg_min) / 60, 1)
        sla_label = f'{avg_hours}h'
    else:
        avg_hours = None
        sla_label = '—'

    return {
        'lead_counts': lead_counts,
        'act_counts':  act_counts,
        'sla': {
            'avg_hours': avg_hours,
            'label':     sla_label,
            'title':     'Avg. Activation Time',
            'subtitle':  'Converted → Activated',
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# PRIVATE PROVISIONING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_company(company_name, errors):
    if smriti.db.exists("ERPCompany", company_name):
        return company_name
    try:
        co = smriti.documents.new("ERPCompany")
        co.update({
            'company_name':     company_name,
            'abbr':             _derive_abbr(company_name),
            'default_currency': 'INR',
            'country':          'India',
        })
        co.insert(ignore_permissions=True)
        return co.name
    except Exception as e:
        errors.append(f'Company creation failed: {e}')
        smriti.errors.log_error(f'SMRITI Activation — Company error: {e}', exc=e)
        return company_name


def _ensure_warehouse(company_name, errors):
    wh_name = f'Main Store - {_derive_abbr(company_name)}'
    if smriti.db.exists("ERPWarehouse", wh_name):
        return wh_name
    try:
        wh = smriti.documents.new("ERPWarehouse")
        wh.update({
            'warehouse_name': 'Main Store',
            'company':        company_name,
        })
        wh.insert(ignore_permissions=True)
        return wh.name
    except Exception as e:
        errors.append(f'Warehouse creation failed: {e}')
        smriti.errors.log_error(f'SMRITI Activation — Warehouse error: {e}', exc=e)
        return wh_name


def _ensure_customer_group(company_name, errors):
    cg_name = f'{company_name} — Retail Customers'
    if smriti.db.exists("ERPCustomerGroup", cg_name):
        return cg_name
    try:
        parent = 'All Customer Groups' if smriti.db.exists("ERPCustomerGroup", 'All Customer Groups') else None
        cg = smriti.documents.new("ERPCustomerGroup")
        cg.update({
            'customer_group_name':   cg_name,
            'parent_customer_group': parent,
        })
        cg.insert(ignore_permissions=True)
        return cg.name
    except Exception as e:
        errors.append(f'Customer Group creation failed: {e}')
        smriti.errors.log_error(f'SMRITI Activation — Customer Group error: {e}', exc=e)
        return cg_name


def _ensure_trial_user(activation, company_name, errors):
    mobile = (activation.mobile or '').lstrip('+').replace(' ', '')
    email  = f'trial.{mobile}@smriti.local'
    if smriti.db.exists("SystemUser", email):
        return email
    try:
        user = smriti.documents.new("SystemUser")
        user.update({
            'email':              email,
            'first_name':         activation.owner_name or activation.store_name,
            'send_welcome_email': 0,
            'roles':              [{'role': 'System Manager'}],
        })
        user.insert(ignore_permissions=True)
        return email
    except Exception as e:
        errors.append(f'User creation failed: {e}')
        smriti.errors.log_error(f'SMRITI Activation — User error: {e}', exc=e)
        return email


def _send_welcome_email(activation, company_name, user_email):
    """Send welcome email — non-critical, failure is logged only."""
    try:
        frappe.sendmail(
            recipients=[user_email],
            subject=f'Welcome to SMRITI Retail OS — {company_name}',
            message=(
                f'<p>Dear {activation.owner_name or activation.store_name},</p>'
                f'<p>Your SMRITI Retail OS trial for <strong>{company_name}</strong> '
                f'has been activated successfully.</p>'
                f'<p>Please login at <a href="/smriti">/smriti</a> to begin your trial.</p>'
                f'<p>Your trial runs for <strong>{(activation.trial_end_date.strftime("%d %b %Y") if activation.trial_end_date else "30 days")}</strong>.</p>'
                f'<br/><p>Team SMRITI Retail OS<br/>AITDL — AI Technology & Development Lab</p>'
            ),
        )
        return True
    except Exception as e:
        smriti.errors.log_error(f'SMRITI Welcome Email failed for {user_email}: {e}', exc=e)
        return False


def _tick_checklist(activation, now, operator, done_tasks):
    """Mark checklist items as done."""
    for row in (activation.checklist or []):
        if row.task_name in done_tasks:
            row.is_done = 1
            row.done_by = operator
            row.done_at = now


def _update_lead_status(lead_name, new_status, note_line):
    """Update the Trial Lead status and append note."""
    try:
        lead = smriti.documents.get("TrialLead", lead_name)
        lead.status = new_status
        lead.notes  = ((lead.notes or '') + '\n' + note_line).strip()
        lead.save(ignore_permissions=True)
    except Exception as e:
        smriti.errors.log_error(f'SMRITI — Lead status update failed for {lead_name}: {e}', exc=e)


def _derive_abbr(company_name):
    """Derive a short company abbreviation (max 4 chars)."""
    words = company_name.strip().split()
    abbr  = ''.join(w[0].upper() for w in words if w)[:4]
    return abbr or 'CO'


@frappe.whitelist()
def get_trial_health_snapshots(limit=100):
    """
    Exposes SMRITI Trial Health Snapshots to the frontend.
    Access restricted strictly to the Administrator user.
    """
    if frappe.session.user != "Administrator":
        frappe.throw(
            _("Access Denied: Restricted to Administrator only."),
            frappe.PermissionError
        )
        
    return smriti.db.get_list(
        "TrialHealthSnapshot",
        fields=[
            "name", "snapshot_date", "snapshot_time", "snapshot_type",
            "active_trials", "expiring_7d", "expiring_3d", "expiring_1d",
            "expired_today", "failed_provisioning", "pending_queue",
            "provisioning", "converted_total", "sla_avg_hours", "health_score",
            "interpretation", "snapshot_version", "formula_version", "generated_by"
        ],
        order_by="snapshot_time desc",
        limit=int(limit)
    )


@frappe.whitelist()
def trigger_trial_health_snapshot():
    """
    Triggers generation of a new SMRITI Trial Health Snapshot manually.
    Access restricted strictly to the Administrator user.
    """
    if frappe.session.user != "Administrator":
        frappe.throw(
            _("Access Denied: Restricted to Administrator only."),
            frappe.PermissionError
        )
        
    from smriti_retail_os.services import trial_service
    doc = trial_service.generate_health_snapshot(snapshot_type="Manual", operator=frappe.session.user)
    return doc.as_dict()
