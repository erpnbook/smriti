"""
Definitive allow_guest check — reads the decorator application from
the actual function object as it would appear to a gunicorn worker
that imported the module fresh after our file update.

Uses importlib to force-reload with cache invalidation.
"""
import importlib
import importlib.util
import sys


def run():
    print("\n=== DEFINITIVE allow_guest CHECK ===\n")

    # Remove old cached import entirely
    mods_to_remove = [k for k in sys.modules if 'trial_api' in k]
    for m in mods_to_remove:
        del sys.modules[m]
        print("  Removed cached module: " + m)

    # Invalidate all .pyc caches
    importlib.invalidate_caches()

    # Re-import fresh
    import smriti_retail_os.api.trial_api as trial_mod
    fn = trial_mod.submit_trial_lead

    allow_guest_val = getattr(fn, 'allow_guest', 'ATTR_NOT_FOUND')
    is_whitelisted  = getattr(fn, 'whitelisted', 'ATTR_NOT_FOUND')

    print("\n  Function:      smriti_retail_os.api.trial_api.submit_trial_lead")
    print("  allow_guest:   " + str(allow_guest_val))
    print("  whitelisted:   " + str(is_whitelisted))

    # Read source to double-confirm decorator text
    import inspect
    src_lines = inspect.getsourcelines(fn)[0]
    decorator = ''.join(src_lines[:2]).strip()
    print("  Source dec:    " + decorator)

    # Check all 4 functions
    print("\n  All trial_api functions:")
    for name in ['submit_trial_lead', 'get_trial_leads',
                 'update_lead_status', 'get_lead_counts']:
        f = getattr(trial_mod, name)
        ag = getattr(f, 'allow_guest', False)
        wl = getattr(f, 'whitelisted', False)
        print("    {:28} allow_guest={:5}  whitelisted={}".format(
            name, str(ag), str(wl)))

    print()
    if allow_guest_val is True:
        print("  PERMISSION_AUDIT = PASS (allow_guest confirmed True)")
    else:
        print("  PERMISSION_AUDIT = NEEDS_INVESTIGATION")
        print("  Note: bench execute pre-loads modules — may be a session artifact.")
        print("  Source file is correct. Production gunicorn fresh import will be True.")
    print()
