"""
SMRITI Trial Signup — www page context
Route: /smriti-trial

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""
import frappe

def get_context(context):
    context.no_cache     = 1
    context.show_sidebar = False
    context.title        = 'Start Free Trial | SMRITI Retail OS'

    # Pre-fill plan from query string (?plan=growth)
    plan = frappe.request.args.get('plan', 'growth')
    context.selected_plan = plan if plan in ('starter', 'growth', 'pro') else 'growth'

    context.plan_labels = {
        'starter': 'SMRITI STARTER — ₹1,999/mo',
        'growth':  'SMRITI GROWTH — ₹3,999/mo (Most Popular)',
        'pro':     'SMRITI PRO — ₹6,999/mo',
    }
    return context
