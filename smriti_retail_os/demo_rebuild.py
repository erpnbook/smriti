"""
SMRITI Demo Dataset — Master Rebuild Command
Version: DEMO_FOOTWEAR_V1
Protected: TRUE | Reloadable: TRUE | Rebuildable: TRUE

Usage (from inside container):
    bench --site smriti_retail execute smriti_retail_os.demo_rebuild.rebuild_demo_dataset

Also usable as:
    bench --site smriti_retail execute smriti_retail_os.demo_rebuild.reset_all
    bench --site smriti_retail execute smriti_retail_os.demo_rebuild.rebuild_demo_dataset

What it does:
    1. Cancels + deletes all DEMO Sales Invoices
    2. Re-runs Phase 0 (12 SKUs, 20 SIs)
    3. Re-runs Phase 1A (60 more SKUs, 230 SIs, 35 PIs)
    4. Runs OWNER_DEMO_AUDIT + OWNER_DEMO_HEALTH_SCORE

Use cases:
    - Team member demo chala sakta hai (fresh reset)
    - New installation demo load kar sakta hai
    - Owner video record kar sakta hai
    - Dataset corrupt ho gaya toh 5 minute mein rebuild

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe

COMPANY   = 'SMRITI UAT Footwear Co'
DEMO_TAG  = 'DEMO-'   # All demo items start with this prefix


def reset_all():
    """Cancel + delete all Phase 0 and Phase 1A Sales Invoices for clean rebuild."""
    frappe.set_user('Administrator')
    print('=' * 60)
    print('SMRITI Demo Dataset — RESET')
    print('=' * 60)
    print('Cancelling and deleting demo Sales Invoices...')

    sis = frappe.db.get_all('Sales Invoice', {
        'company': COMPANY,
        'docstatus': ['!=', 2]
    }, ['name', 'docstatus'], order_by='creation desc')

    deleted = 0
    errors  = 0
    for si in sis:
        try:
            doc = frappe.get_doc('Sales Invoice', si.name)
            # First: delete any linked Payment Ledger Entries
            frappe.db.delete('Payment Ledger Entry', {'voucher_no': si.name})
            frappe.db.commit()
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc('Sales Invoice', si.name, ignore_permissions=True, force=True)
            deleted += 1
        except Exception as e:
            errors += 1
            print(f'  WARN {si.name}: {e}')

    frappe.db.commit()
    print(f'  Deleted {deleted} SIs ({errors} errors — safely ignored).')

    # Reset opening stock entries for Phase 0 and 1A
    for remarks in ['DEMO-PHASE0-OPENING', 'DEMO-PHASE1A-OPENING']:
        ste = frappe.db.get_value('Stock Entry', {
            'company': COMPANY, 'docstatus': 1, 'remarks': remarks
        }, 'name')
        if ste:
            try:
                doc = frappe.get_doc('Stock Entry', ste)
                doc.cancel()
                frappe.delete_doc('Stock Entry', ste, ignore_permissions=True, force=True)
                frappe.db.commit()
                print(f'  Reset: {ste} ({remarks})')
            except Exception as e:
                print(f'  WARN {ste}: {e}')

    print('Reset complete.')


def rebuild_demo_dataset():
    """
    Full demo dataset rebuild: Phase 0 + Phase 1A + Audit + Health Score.
    Run time: ~5-8 minutes.
    """
    frappe.set_user('Administrator')
    print()
    print('=' * 60)
    print('SMRITI Demo Dataset — REBUILD')
    print('Version : DEMO_FOOTWEAR_V1')
    print('Company : ' + COMPANY)
    print('=' * 60)
    print()
    print('Protected  : TRUE')
    print('Reloadable : TRUE')
    print('Rebuildable: TRUE')
    print()

    # Step 1: Reset existing SIs
    print('[Step 1/5] Resetting existing demo Sales Invoices...')
    sis = frappe.db.get_all('Sales Invoice', {
        'company': COMPANY,
        'docstatus': ['!=', 2]
    }, ['name', 'docstatus'])

    for si in sis:
        try:
            frappe.db.delete('Payment Ledger Entry', {'voucher_no': si.name})
            frappe.db.commit()
            doc = frappe.get_doc('Sales Invoice', si.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc('Sales Invoice', si.name, ignore_permissions=True, force=True)
        except Exception:
            pass
    frappe.db.commit()
    print(f'  {len(sis)} SIs cleared.')

    # Step 2: Phase 0
    print()
    print('[Step 2/5] Phase 0: Story Validation Dataset (12 SKUs, 20 SIs)...')
    from smriti_retail_os.demo_phase0 import main as phase0_main
    phase0_main()

    # Step 3: Phase 1A.1 (items + suppliers + stock)
    print()
    print('[Step 3/5] Phase 1A.1: 60 new SKUs + 4 suppliers + opening stock...')
    from smriti_retail_os.demo_phase1a import phase1a_1
    phase1a_1()

    # Step 4: Phase 1A.3 (transactions)
    print()
    print('[Step 4/5] Phase 1A.3: 230 SIs + 35 PIs...')
    from smriti_retail_os.demo_phase1a import phase1a_3
    phase1a_3()

    # Step 5: Audit + Health Score
    print()
    print('[Step 5/5] OWNER_DEMO_AUDIT + OWNER_DEMO_HEALTH_SCORE...')
    from smriti_retail_os.demo_verify import verify
    verify()

    print()
    print('=' * 60)
    print('SMRITI Demo Dataset REBUILD COMPLETE')
    print('Version: DEMO_FOOTWEAR_V1')
    print('=' * 60)
