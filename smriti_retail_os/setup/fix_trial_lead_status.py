"""
Sprint 2A Fix — Add 'Trial Started' to SMRITI Trial Lead status options.
Run: bench --site smriti_retail execute smriti_retail_os.setup.fix_trial_lead_status.run
"""
import frappe


def run():
    print("\n=== Fix: SMRITI Trial Lead — Status Options ===\n")

    CORRECT_OPTIONS = (
        "New\n"
        "Contacted\n"
        "Demo Scheduled\n"
        "Trial Started\n"
        "Converted\n"
        "Lost"
    )

    # Update DocField for status
    frappe.db.sql("""
        UPDATE `tabDocField`
        SET    options = %s
        WHERE  parent    = 'SMRITI Trial Lead'
          AND  fieldname = 'status'
    """, (CORRECT_OPTIONS,))

    frappe.db.commit()

    # Verify
    result = frappe.db.sql("""
        SELECT options FROM `tabDocField`
        WHERE  parent = 'SMRITI Trial Lead' AND fieldname = 'status'
    """)
    opts = result[0][0].replace('\n', ' | ') if result else 'NOT FOUND'
    print("  Updated status options: " + opts)

    # Clear DocType cache
    frappe.clear_cache(doctype='SMRITI Trial Lead')
    print("  DocType cache cleared.")
    print("\n  STATUS_FIX = DONE\n")
