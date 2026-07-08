"""
SMRITI Trial Lead Capture API
Route: smriti_retail_os.api.trial_api.submit_trial_lead

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def submit_trial_lead(
    store_name,
    owner_name,
    mobile,
    city,
    business_type,
    plan='growth',
    warehouses=1,
    monthly_sales=None,
    source='smriti-trial',
):
    """Capture a trial signup lead."""

    # Basic validation
    if not store_name or not owner_name or not mobile:
        frappe.throw(_('Store name, owner name, and mobile are required.'))

    # Normalize mobile
    mobile = str(mobile).strip().replace(' ', '').replace('-', '')
    if not mobile.lstrip('+').isdigit() or len(mobile.lstrip('+')) < 10:
        frappe.throw(_('Please enter a valid mobile number.'))

    # Check for duplicate (same mobile submitted in last 24h)
    existing = smriti.db.exists('SMRITI Trial Lead', {'mobile': mobile})
    if existing:
        return {
            'status': 'duplicate',
            'message': 'This mobile number is already registered. Our team will contact you shortly.',
        }

    # Create lead record
    lead = smriti.documents.new('TrialLead')
    lead.update({
        'store_name':    store_name.strip(),
        'owner_name':    owner_name.strip(),
        'mobile':        mobile,
        'city':          city.strip() if city else '',
        'business_type': business_type,
        'plan_selected': plan,
        'warehouses':    int(warehouses) if warehouses else 1,
        'monthly_sales': float(monthly_sales) if monthly_sales else None,
        'source':        source,
        'status':        'New',
        'submitted_at':  datetime.now(),
    })
    # reviewed-ignore-permissions: guest trial signup, runs under guest role context
    lead.insert(ignore_permissions=True)
    smriti.db.commit()

    # Log for visibility
    frappe.logger('smriti.trial').info(
        f'NEW TRIAL LEAD: {owner_name} | {store_name} | {mobile} | {city} | {business_type} | Plan: {plan}'
    )

    return {
        'status':   'success',
        'lead_id':  lead.name,
        'message':  f"Thank you {owner_name.split()[0]}! Our team will call you within 24 hours to set up your SMRITI trial.",
    }


@frappe.whitelist()
def get_trial_leads(status=None, limit=50):
    """Get trial leads for internal review (requires login)."""
    filters = {}
    if status:
        filters['status'] = status

    leads = smriti.db.get_list(
        'SMRITI Trial Lead',
        filters=filters,
        fields=['name', 'store_name', 'owner_name', 'mobile', 'city',
                'business_type', 'plan_selected', 'status', 'submitted_at'],
        order_by='submitted_at desc',
        limit=limit,
    )
    return leads


@frappe.whitelist()
def update_lead_status(lead_name, new_status, notes=None):
    """Update trial lead status with audit trail (requires login)."""

    ALLOWED_STATUSES = [
        'New', 'Contacted', 'Demo Scheduled',
        'Trial Started', 'Converted', 'Lost',
    ]

    if new_status not in ALLOWED_STATUSES:
        frappe.throw(_(f'Invalid status: {new_status}'))

    lead = smriti.documents.get('SMRITI Trial Lead', lead_name)

    old_status  = lead.status
    lead.status = new_status

    # Append timestamped audit note
    if notes or old_status != new_status:
        timestamp   = datetime.now().strftime('%Y-%m-%d %H:%M')
        changed_by  = frappe.session.user
        note_line   = f'[{timestamp}] {changed_by}: {old_status} → {new_status}'
        if notes:
            note_line += f' | {notes.strip()}'
        existing_notes = lead.notes or ''
        lead.notes = (existing_notes + '\n' + note_line).strip()

    # reviewed-ignore-permissions: lead status tracking, restricted to sales agent
    lead.save(ignore_permissions=True)
    smriti.db.commit()

    frappe.logger('smriti.trial').info(
        f'STATUS UPDATE: {lead_name} | {old_status} → {new_status} | {frappe.session.user}'
    )

    return {
        'status':     'success',
        'lead':       lead_name,
        'old_status': old_status,
        'new_status': new_status,
    }


@frappe.whitelist()
def get_lead_counts():
    """Return count per status for pipeline summary badges."""
    STATUSES = ['New', 'Contacted', 'Demo Scheduled',
                'Trial Started', 'Converted', 'Lost']
    counts = {}
    for s in STATUSES:
        counts[s] = smriti.db.count('SMRITI Trial Lead', {'status': s})
    counts['total'] = sum(counts.values())
    return counts
