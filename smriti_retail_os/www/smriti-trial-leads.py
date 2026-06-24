"""
SMRITI Trial Leads CRM — www page context
Route: /smriti-trial-leads

Internal page. Requires login.
Access: System Manager, SMRITI Team

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""
import frappe


def get_context(context):
    # Require login — guests are redirected to /login
    if frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login?redirect-to=/smriti-trial-leads'
        raise frappe.Redirect

    context.no_cache     = 1
    context.show_sidebar = False
    context.title        = 'Trial Leads CRM | SMRITI Retail OS'
    return context
