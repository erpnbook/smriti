"""
SMRITI Trial Activation API
Route prefix: smriti_retail_os.api.trial_activation_api

Handles the full activation lifecycle:
  create_activation()   → create a pending activation record
  activate_account()    → provision Company + Warehouse + User
  suspend_activation()  → suspend an active trial
  extend_trial()        → push the trial_end_date forward
  get_converted_leads() → list Converted leads without activation
  get_activations()     → list activation records (filterable)
  get_activation_dashboard() → pipeline summary + SLA metrics

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
Sprint: 3A — Platform Admin: Trial Activation & Account Provisioning
"""

import frappe
from frappe import _
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# READ — Leads awaiting activation
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_converted_leads():
    """
    Return Converted trial leads that have NO activation record yet.
    Used by Platform Admin to populate the Activation Queue.
    """
    # Leads marked Converted
    converted = frappe.get_all(
        'SMRITI Trial Lead',
        filters={'status': 'Converted'},
        fields=['name', 'store_name', 'owner_name', 'mobile', 'city',
                'business_type', 'plan_selected', 'submitted_at'],
        order_by='modified desc',
        limit=200,
    )

    # Exclude those already activated
    activated_leads = set(
        r.trial_lead for r in frappe.get_all(
            'SMRITI Trial Activation',
            fields=['trial_lead'],
        )
    )

    queue = [l for l in converted if l['name'] not in activated_leads]
    return queue


# ─────────────────────────────────────────────────────────────────────────────
# CREATE — Activation record
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_activation(lead_name, activation_type='Trial', trial_days=30):
    """
    Create a SMRITI Trial Activation record (status=Pending).
    Does NOT provision the account yet — that happens in activate_account().
    """
    # Guard: lead must exist and be Converted
    lead = frappe.get_doc('SMRITI Trial Lead', lead_name)
    if lead.status not in ('Converted', 'Trial Started'):
        frappe.throw(_(f'Lead must be Converted to create an activation. Current status: {lead.status}'))

    # Guard: no duplicate
    existing = frappe.db.exists('SMRITI Trial Activation', {'trial_lead': lead_name})
    if existing:
        return {
            'status':     'duplicate',
            'activation': existing,
            'message':    f'Activation already exists: {existing}',
        }

    # Build default checklist
    checklist_items = [
        {'task_name': 'Company Created'},
        {'task_name': 'Warehouse Created'},
        {'task_name': 'User Created'},
        {'task_name': 'Opening Data Imported'},
        {'task_name': 'Training Scheduled'},
        {'task_name': 'Welcome Sent'},
    ]

    activation = frappe.get_doc({
        'doctype':           'SMRITI Trial Activation',
        'activation_type':   activation_type,
        'trial_lead':        lead_name,
        'store_name':        lead.store_name,
        'owner_name':        lead.owner_name,
        'mobile':            lead.mobile,
        'activation_status': 'Pending',
        'checklist':         checklist_items,
    })
    activation.insert(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger('smriti.trial').info(
        f'ACTIVATION CREATED: {activation.name} | Lead: {lead_name} | Type: {activation_type}'
    )

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
    Provision a new ERPNext Company, default Warehouse, Customer Group,
    and trial User, then mark the activation as Active.

    Architecture: Single-site, multi-company (Phase 1).
    NO bench new-site is called here.
    """
    activation = frappe.get_doc('SMRITI Trial Activation', activation_name)

    if activation.activation_status == 'Active':
        frappe.throw(_('This activation is already Active.'))

    # Derive company name from store_name if not provided
    if not company_name:
        company_name = activation.store_name.strip()

    errors = []

    # ── Step 1: Create Company ────────────────────────────────────────────────
    co_name = _ensure_company(company_name, errors)

    # ── Step 2: Create default Warehouse ─────────────────────────────────────
    _ensure_warehouse(co_name, errors)

    # ── Step 3: Create Customer Group ────────────────────────────────────────
    _ensure_customer_group(co_name, errors)

    # ── Step 4: Create trial User ─────────────────────────────────────────────
    _ensure_trial_user(activation, co_name, errors)

    # ── Finalise Activation ───────────────────────────────────────────────────
    now        = datetime.now()
    end_date   = now + timedelta(days=int(trial_days))

    activation.company_name      = co_name
    activation.activation_status = 'Active'
    activation.trial_start_date  = now
    activation.trial_end_date    = end_date
    activation.activated_by      = frappe.session.user

    # Mark checklist items
    for row in activation.checklist:
        if row.task_name == 'Company Created':
            row.is_done = 1; row.done_by = frappe.session.user; row.done_at = now
        elif row.task_name == 'Warehouse Created':
            row.is_done = 1; row.done_by = frappe.session.user; row.done_at = now
        elif row.task_name == 'User Created':
            row.is_done = 1; row.done_by = frappe.session.user; row.done_at = now

    activation.save(ignore_permissions=True)

    # Update Trial Lead status → Trial Started
    lead = frappe.get_doc('SMRITI Trial Lead', activation.trial_lead)
    lead.status = 'Trial Started'
    ts = now.strftime('%Y-%m-%d %H:%M')
    note_line = f'[{ts}] {frappe.session.user}: Converted → Trial Started | Activation: {activation.activation_reference}'
    lead.notes = ((lead.notes or '') + '\n' + note_line).strip()
    lead.save(ignore_permissions=True)

    frappe.db.commit()

    frappe.logger('smriti.trial').info(
        f'ACCOUNT ACTIVATED: {activation.name} | Company: {co_name} | Lead: {activation.trial_lead}'
    )

    return {
        'status':     'success',
        'activation': activation.name,
        'reference':  activation.activation_reference,
        'company':    co_name,
        'trial_days': int(trial_days),
        'trial_end':  str(end_date.date()),
        'errors':     errors,
        'message':    f'Account activated! Trial runs until {end_date.strftime("%d %b %Y")}.',
    }


def _ensure_company(company_name, errors):
    """Create ERPNext Company if not already present. Returns actual company name."""
    if frappe.db.exists('Company', company_name):
        return company_name
    try:
        co = frappe.get_doc({
            'doctype':          'Company',
            'company_name':     company_name,
            'abbr':             _derive_abbr(company_name),
            'default_currency': 'INR',
            'country':          'India',
        })
        co.insert(ignore_permissions=True)
        return co.name
    except Exception as e:
        errors.append(f'Company creation failed: {e}')
        frappe.log_error(f'SMRITI Activation — Company error: {e}')
        return company_name


def _ensure_warehouse(company_name, errors):
    """Create a default Main Warehouse for the company."""
    wh_name = f'Main Store - {_derive_abbr(company_name)}'
    if frappe.db.exists('Warehouse', wh_name):
        return wh_name
    try:
        wh = frappe.get_doc({
            'doctype':      'Warehouse',
            'warehouse_name': 'Main Store',
            'company':      company_name,
        })
        wh.insert(ignore_permissions=True)
        return wh.name
    except Exception as e:
        errors.append(f'Warehouse creation failed: {e}')
        frappe.log_error(f'SMRITI Activation — Warehouse error: {e}')
        return wh_name


def _ensure_customer_group(company_name, errors):
    """Create a default Customer Group for the company's retail customers."""
    cg_name = f'{company_name} — Retail Customers'
    if frappe.db.exists('Customer Group', cg_name):
        return cg_name
    try:
        # Find a valid parent (All Customer Groups)
        parent = 'All Customer Groups' if frappe.db.exists('Customer Group', 'All Customer Groups') else None
        cg = frappe.get_doc({
            'doctype':        'Customer Group',
            'customer_group_name': cg_name,
            'parent_customer_group': parent,
        })
        cg.insert(ignore_permissions=True)
        return cg.name
    except Exception as e:
        errors.append(f'Customer Group creation failed: {e}')
        frappe.log_error(f'SMRITI Activation — Customer Group error: {e}')
        return cg_name


def _ensure_trial_user(activation, company_name, errors):
    """Create a trial User linked to the store's mobile number."""
    # Use mobile as login email placeholder
    mobile = (activation.mobile or '').lstrip('+').replace(' ', '')
    email  = f'trial.{mobile}@smriti.local'

    if frappe.db.exists('User', email):
        return email
    try:
        user = frappe.get_doc({
            'doctype':      'User',
            'email':        email,
            'first_name':   activation.owner_name or activation.store_name,
            'send_welcome_email': 0,
            'roles': [{'role': 'System Manager'}],
        })
        user.insert(ignore_permissions=True)
        return email
    except Exception as e:
        errors.append(f'User creation failed: {e}')
        frappe.log_error(f'SMRITI Activation — User error: {e}')
        return email


def _derive_abbr(company_name):
    """Derive a short company abbreviation (max 4 chars)."""
    words = company_name.strip().split()
    abbr  = ''.join(w[0].upper() for w in words if w)[:4]
    return abbr or 'CO'


# ─────────────────────────────────────────────────────────────────────────────
# MANAGE — Suspend / Extend
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def suspend_activation(activation_name, reason=None):
    """Suspend an active trial. Records reason in notes."""
    activation = frappe.get_doc('SMRITI Trial Activation', activation_name)

    if activation.activation_status != 'Active':
        frappe.throw(_(f'Only Active activations can be suspended. Current: {activation.activation_status}'))

    activation.activation_status = 'Suspended'
    ts      = datetime.now().strftime('%Y-%m-%d %H:%M')
    by      = frappe.session.user
    note    = f'[{ts}] {by}: Suspended'
    if reason:
        note += f' — {reason.strip()}'
    activation.notes = ((activation.notes or '') + '\n' + note).strip()
    activation.save(ignore_permissions=True)
    frappe.db.commit()

    return {'status': 'success', 'message': f'{activation_name} suspended.'}


@frappe.whitelist()
def extend_trial(activation_name, additional_days=7, reason=None):
    """Extend a trial by N additional days."""
    activation = frappe.get_doc('SMRITI Trial Activation', activation_name)

    if activation.activation_status not in ('Active', 'Suspended'):
        frappe.throw(_('Can only extend Active or Suspended trials.'))

    additional_days = int(additional_days)
    old_end = activation.trial_end_date or datetime.now()
    if isinstance(old_end, str):
        old_end = datetime.fromisoformat(old_end)

    new_end = old_end + timedelta(days=additional_days)
    activation.trial_end_date    = new_end
    activation.activation_status = 'Active'

    ts   = datetime.now().strftime('%Y-%m-%d %H:%M')
    by   = frappe.session.user
    note = f'[{ts}] {by}: Trial extended +{additional_days}d → new end {new_end.strftime("%d %b %Y")}'
    if reason:
        note += f' | {reason.strip()}'
    activation.notes = ((activation.notes or '') + '\n' + note).strip()
    activation.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        'status':   'success',
        'new_end':  str(new_end.date()),
        'message':  f'Trial extended to {new_end.strftime("%d %b %Y")}.',
    }


# ─────────────────────────────────────────────────────────────────────────────
# READ — Activations list
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_activations(status=None, limit=100):
    """Return activation records, optionally filtered by status."""
    filters = {}
    if status:
        filters['activation_status'] = status

    rows = frappe.get_all(
        'SMRITI Trial Activation',
        filters=filters,
        fields=[
            'name', 'activation_reference', 'activation_type',
            'trial_lead', 'store_name', 'owner_name', 'mobile',
            'company_name', 'activation_status',
            'trial_start_date', 'trial_end_date',
            'activated_by', 'creation',
        ],
        order_by='creation desc',
        limit=limit,
    )

    # Compute days remaining for each active row
    now = datetime.now()
    for r in rows:
        end = r.get('trial_end_date')
        if end and r.get('activation_status') == 'Active':
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            r['days_remaining'] = max(0, (end - now).days)
        else:
            r['days_remaining'] = None

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — Pipeline summary + SLA
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_activation_dashboard():
    """
    Returns pipeline counts and SLA metric (avg Converted→Active time in hours).
    Used by /smriti-platform-admin pipeline summary widgets.
    """
    # ── Pipeline counts ───────────────────────────────────────────────────────
    lead_counts = {
        'converted_total': frappe.db.count('SMRITI Trial Lead', {'status': 'Converted'}),
        'trial_started':   frappe.db.count('SMRITI Trial Lead', {'status': 'Trial Started'}),
    }

    act_counts = {
        'pending':           frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Pending'}),
        'active':            frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Active'}),
        'suspended':         frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Suspended'}),
        'expired':           frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Expired'}),
        'converted_to_paid': frappe.db.count('SMRITI Trial Activation', {'activation_status': 'Converted to Paid'}),
    }

    # Queue = Converted leads with no activation or Pending activation
    act_counts['activation_queue'] = (
        lead_counts['converted_total'] + act_counts['pending']
    )

    # Expiring soon (within 7 days)
    expiring_rows = frappe.db.sql(
        """
        SELECT COUNT(*) AS cnt
        FROM   `tabSMRITI Trial Activation`
        WHERE  activation_status = 'Active'
          AND  trial_end_date    BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
        """,
        as_dict=True,
    )
    act_counts['expiring_soon'] = expiring_rows[0]['cnt'] if expiring_rows else 0

    # ── SLA: Avg Converted → Active time (hours) ─────────────────────────────
    sla_rows = frappe.db.sql(
        """
        SELECT
            AVG(TIMESTAMPDIFF(MINUTE, tl.modified, ta.trial_start_date)) AS avg_minutes
        FROM `tabSMRITI Trial Activation` ta
        JOIN `tabSMRITI Trial Lead`       tl ON tl.name = ta.trial_lead
        WHERE ta.activation_status IN ('Active', 'Expired', 'Converted to Paid')
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
        'lead_counts':  lead_counts,
        'act_counts':   act_counts,
        'sla': {
            'avg_hours': avg_hours,
            'label':     sla_label,
            'title':     'Avg. Activation Time',
            'subtitle':  'Converted → Active',
        },
    }
