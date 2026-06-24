"""
Sprint 2A — Security & Audit Validation Script
Run: bench --site smriti_retail execute smriti_retail_os.sprint2a_checks.run

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""
import frappe


def run():
    print("\n" + "="*60)
    print("SPRINT 2A — SMRITI Trial Lead Security & Audit Validation")
    print("="*60)

    # ── CHECK 1: DocType Fields ──────────────────────────────────
    print("\n[ CHECK 1 ] DocType Field Audit")
    print("-" * 40)

    required_fields = {
        'store_name', 'owner_name', 'mobile', 'city',
        'plan_selected', 'status', 'notes', 'submitted_at',
        'business_type', 'warehouses', 'source',
    }

    rows = frappe.db.sql("""
        SELECT fieldname, fieldtype, reqd, options
        FROM `tabDocField`
        WHERE parent = 'SMRITI Trial Lead'
        ORDER BY idx
    """, as_dict=True)

    found = {}
    for r in rows:
        found[r.fieldname] = r
        print("  {:22} {:18} reqd={}".format(
            r.fieldname, r.fieldtype, r.reqd or 0))

    # Check mobile unique constraint
    unique_check = frappe.db.sql("""
        SELECT COLUMN_NAME, COLUMN_KEY
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = 'tabSMRITI Trial Lead'
          AND COLUMN_NAME  = 'mobile'
    """, as_dict=True)

    mobile_unique = any(
        c.get('COLUMN_KEY') in ('UNI', 'PRI') for c in unique_check
    )

    print("\n  Required field presence:")
    all_ok = True
    for f in sorted(required_fields):
        if f in found:
            print("  OK  {}".format(f))
        else:
            print("  MISSING  {}".format(f))
            all_ok = False

    # Status options
    status_field = found.get('status', {})
    status_opts  = (status_field.get('options') or '').replace('\n', ' | ')
    print("\n  Status options: {}".format(status_opts or 'NOT SET'))
    print("  Mobile unique (DB level): {}".format(mobile_unique))
    print("\n  DOCTYPE_AUDIT = {}".format('PASS' if all_ok else 'FAIL'))

    # ── CHECK 2: API Permissions (Frappe v16 — function-object lookup) ──────
    print("\n[ CHECK 2 ] API Permission Audit (Frappe v16)")
    print("-" * 40)

    import smriti_retail_os.api.trial_api as trial_mod

    endpoints = [
        ('submit_trial_lead',  True),   # allow_guest=True
        ('get_trial_leads',    False),  # requires login
        ('update_lead_status', False),  # requires login
        ('get_lead_counts',    False),  # requires login
    ]

    perm_ok = True
    for method, expect_guest in endpoints:
        fn             = getattr(trial_mod, method)
        in_whitelisted = fn in frappe.whitelisted
        in_guest       = fn in frappe.guest_methods
        status = 'OK' if (in_guest == expect_guest) else 'FAIL'
        if status == 'FAIL':
            perm_ok = False
        print("  {} {:28} whitelisted={:5}  guest={:5}  expected={}".format(
            status, method,
            str(in_whitelisted), str(in_guest), str(expect_guest)))

    print("\n  PERMISSION_AUDIT = {}".format('PASS' if perm_ok else 'FAIL'))

    # ── CHECK 3: Audit Trail in DB ───────────────────────────────
    print("\n[ CHECK 3 ] Audit Trail Persistence")
    print("-" * 40)

    # Check that 'notes' column exists in the actual DB table
    col_check = frappe.db.sql("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = 'tabSMRITI Trial Lead'
          AND COLUMN_NAME  IN ('notes', 'status', 'submitted_at', 'owner_name', 'mobile')
        ORDER BY COLUMN_NAME
    """, as_dict=True)

    for c in col_check:
        print("  DB_COLUMN: {:20} type={} len={}".format(
            c.get('COLUMN_NAME'),
            c.get('DATA_TYPE'),
            c.get('CHARACTER_MAXIMUM_LENGTH') or 'n/a'))

    notes_in_db = any(c.get('COLUMN_NAME') == 'notes' for c in col_check)

    # Check the update_lead_status function appends to notes field
    import inspect
    import smriti_retail_os.api.trial_api as trial_mod
    src = inspect.getsource(trial_mod.update_lead_status)
    has_audit_append = 'lead.notes' in src and 'note_line' in src
    has_timestamp    = 'datetime.now' in src or 'strftime' in src
    has_user         = 'frappe.session.user' in src
    has_old_status   = 'old_status' in src
    has_save         = 'lead.save' in src

    print("\n  Audit trail code checks (update_lead_status):")
    checks = [
        ('notes field appended',        has_audit_append),
        ('timestamp recorded',          has_timestamp),
        ('user identity recorded',      has_user),
        ('old_status captured',         has_old_status),
        ('lead.save() called',          has_save),
        ('notes column in DB table',    notes_in_db),
    ]
    audit_ok = True
    for label, result in checks:
        icon = 'OK' if result else 'FAIL'
        if not result:
            audit_ok = False
        print("  {} {}".format(icon, label))

    print("\n  AUDIT_TRAIL = {}".format('PASS' if audit_ok else 'FAIL'))

    # ── SUMMARY ─────────────────────────────────────────────────
    print("\n" + "="*60)
    print("SPRINT 2A VALIDATION SUMMARY")
    print("="*60)
    checks_summary = [
        ('DOCTYPE_AUDIT',    all_ok),
        ('PERMISSION_AUDIT', perm_ok),
        ('AUDIT_TRAIL',      audit_ok),
    ]
    overall = all(r for _, r in checks_summary)
    for name, result in checks_summary:
        print("  {:25} = {}".format(name, 'PASS' if result else 'FAIL'))
    print("\n  SPRINT_2A_SECURITY = {}".format(
        'PASS' if overall else 'FAIL - see above'))
    print("="*60 + "\n")
