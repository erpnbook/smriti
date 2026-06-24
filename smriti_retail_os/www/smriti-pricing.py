"""
SMRITI Pricing Page — www page context
Route: /smriti-pricing

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""
import frappe

def get_context(context):
    # Public page — no auth required
    context.no_cache     = 1
    context.show_sidebar = False
    context.title        = 'Pricing | SMRITI Retail OS'
    return context
