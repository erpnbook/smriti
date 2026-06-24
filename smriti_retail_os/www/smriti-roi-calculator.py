"""
SMRITI ROI Calculator — www page context + auth
Route: /smriti-roi-calculator

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe

def get_context(context):
    if not frappe.session.user or frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login?redirect-to=/smriti-roi-calculator'
        raise frappe.Redirect

    context.no_cache      = 1
    context.show_sidebar  = False
    context.title         = 'ROI Calculator | SMRITI Retail OS'

    # Package pricing (INR/year — annual)
    context.packages = {
        'starter': {
            'name':         'SMRITI STARTER',
            'monthly':      1999,
            'annual':       19999,
            'savings':      3989,
            'description':  'Single store. Inventory + Alerts.',
            'features':     ['Dashboard', 'Dead Stock Alerts', 'Low Stock Alerts',
                             'Fast Mover Report', 'Sales History'],
            'roi_multiple': 17,
        },
        'growth': {
            'name':         'SMRITI GROWTH',
            'monthly':      3999,
            'annual':       39999,
            'savings':      7989,
            'description':  'CGE + PDT. Customer Intelligence + Reorder Engine.',
            'features':     ['Everything in STARTER', 'CGE — Loyal / Lapsed Customers',
                             'PDT — Smart Reorder', 'WhatsApp Alerts', '3 Warehouses'],
            'roi_multiple': 28,
        },
        'pro': {
            'name':         'SMRITI PRO',
            'monthly':      6999,
            'annual':       69999,
            'savings':      13989,
            'description':  'Multi-store. Distributor. AI Forecasting. PSV.',
            'features':     ['Everything in GROWTH', 'Unlimited Stores', 'PSV / Channel Stock',
                             'AI Demand Forecasting', 'Priority Support'],
            'roi_multiple': 55,
        },
    }
    return context
