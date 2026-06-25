"""
Frappe v16-compatible permission check.
frappe.whitelisted and frappe.guest_methods are sets of FUNCTION OBJECTS,
not strings. Must check fn in frappe.guest_methods, not string lookup.

Run: bench --site smriti_retail execute smriti_retail_os.setup.check_guest_perm_v2.run
"""
import frappe


def run():
    import smriti_retail_os.api.trial_api as trial_mod
    print("\n=== FRAPPE v16 PERMISSION AUDIT (function-object lookup) ===\n")

    funcs = [
        ('submit_trial_lead',  True),
        ('get_trial_leads',    False),
        ('update_lead_status', False),
        ('get_lead_counts',    False),
    ]

    all_ok = True
    for name, expect_guest in funcs:
        fn              = getattr(trial_mod, name)
        in_whitelisted  = fn in frappe.whitelisted
        in_guest        = fn in frappe.guest_methods
        result          = 'OK' if (in_guest == expect_guest) else 'FAIL'
        if result == 'FAIL':
            all_ok = False
        print("  {:6} {:28} whitelisted={:5}  guest={:5}  expected_guest={}".format(
            result, name,
            str(in_whitelisted), str(in_guest), str(expect_guest)))

    print("\n  PERMISSION_AUDIT = " + ('PASS' if all_ok else 'FAIL'))
    print("  Frappe version: " + (frappe.__version__ if hasattr(frappe, '__version__') else 'unknown'))
    print()
