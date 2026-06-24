"""
Sprint 3A — Trial Activation & Platform Admin Validation Script
Run:  bench --site smriti_retail execute smriti_retail_os.sprint3_checks.run

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
Sprint:    3A — Platform Admin: Trial Activation & Account Provisioning
"""
import frappe
import os


# ── Paths relative to this file ──────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))


def _check(label, result, hint=''):
    icon = 'OK  ' if result else 'FAIL'
    msg  = f'  {icon}  {label}'
    if not result and hint:
        msg += f'\n         ↳ {hint}'
    print(msg)
    return result


def run():
    print('\n' + '=' * 64)
    print('SPRINT 3A — SMRITI Trial Activation & Platform Admin Validation')
    print('=' * 64)

    results = {}

    # ── CHECK 1: DocType — SMRITI Trial Activation ─────────────────────────
    print('\n[ CHECK 1 ] SMRITI Trial Activation DocType')
    print('-' * 44)

    ta_fields = {r.fieldname: r for r in frappe.db.sql(
        """SELECT fieldname, fieldtype, options
           FROM `tabDocField`
           WHERE parent = 'SMRITI Trial Activation'""",
        as_dict=True,
    )}

    required_ta = [
        'activation_reference', 'activation_type', 'trial_lead',
        'store_name', 'owner_name', 'mobile',
        'company_name', 'activation_status',
        'trial_start_date', 'trial_end_date', 'activated_by',
        'checklist', 'notes',
    ]
    dt_ok = True
    for f in required_ta:
        ok = f in ta_fields
        if not ok:
            dt_ok = False
        _check(f'field: {f}', ok)

    # Verify checklist is a Table pointing to SMRITI Trial Checklist
    ck = ta_fields.get('checklist', {})
    table_ok = ck.get('fieldtype') == 'Table' and ck.get('options') == 'SMRITI Trial Checklist'
    _check('checklist → SMRITI Trial Checklist (Table)', table_ok)
    if not table_ok:
        dt_ok = False

    # Verify autoname
    meta = frappe.db.get_value('DocType', 'SMRITI Trial Activation', ['autoname', 'module'], as_dict=True)
    autoname_ok = meta and meta.get('autoname') == 'field:activation_reference'
    _check('autoname = field:activation_reference', autoname_ok)
    module_ok   = meta and meta.get('module') == 'SMRITI Retail OS'
    _check('module = SMRITI Retail OS', module_ok)

    results['DOCTYPE_ACTIVATION'] = dt_ok and table_ok and bool(autoname_ok) and bool(module_ok)
    print('  DOCTYPE_ACTIVATION =', 'PASS' if results['DOCTYPE_ACTIVATION'] else 'FAIL')

    # ── CHECK 2: DocType — SMRITI Trial Checklist ──────────────────────────
    print('\n[ CHECK 2 ] SMRITI Trial Checklist DocType (child table)')
    print('-' * 44)

    cl_fields = {r.fieldname for r in frappe.db.sql(
        """SELECT fieldname FROM `tabDocField`
           WHERE parent = 'SMRITI Trial Checklist'""",
        as_dict=True,
    )}
    required_cl = ['task_name', 'is_done', 'done_by', 'done_at']
    cl_ok = True
    for f in required_cl:
        ok = f in cl_fields
        if not ok:
            cl_ok = False
        _check(f'field: {f}', ok)

    # Verify istable
    istable = frappe.db.get_value('DocType', 'SMRITI Trial Checklist', 'istable')
    _check('istable = 1', bool(istable))
    if not istable:
        cl_ok = False

    results['DOCTYPE_CHECKLIST'] = cl_ok
    print('  DOCTYPE_CHECKLIST =', 'PASS' if cl_ok else 'FAIL')

    # ── CHECK 3: Trial Lead — Trial Started status ─────────────────────────
    print('\n[ CHECK 3 ] SMRITI Trial Lead — Status Options Migration')
    print('-' * 44)

    tl_status_field = frappe.db.sql(
        """SELECT options FROM `tabDocField`
           WHERE parent = 'SMRITI Trial Lead'
             AND fieldname = 'status'
           LIMIT 1""",
        as_dict=True,
    )
    if tl_status_field:
        options = (tl_status_field[0].get('options') or '').split('\n')
        trial_started_ok = 'Trial Started' in options
        _check('"Trial Started" in status options', trial_started_ok,
               'Run bench migrate to apply doctype JSON changes')
    else:
        trial_started_ok = False
        _check('status field found in SMRITI Trial Lead', False)

    results['TRIAL_LEAD_STATUS'] = trial_started_ok
    print('  TRIAL_LEAD_STATUS =', 'PASS' if trial_started_ok else 'FAIL')

    # ── CHECK 4: API — trial_activation_api endpoints ─────────────────────
    print('\n[ CHECK 4 ] API Permission Audit — trial_activation_api')
    print('-' * 44)

    import smriti_retail_os.api.trial_activation_api as ta_mod

    endpoints_expected = {
        'get_converted_leads':      False,
        'create_activation':        False,
        'activate_account':         False,
        'suspend_activation':       False,
        'extend_trial':             False,
        'get_activations':          False,
        'get_activation_dashboard': False,
    }

    api_ok = True
    for method, expect_guest in endpoints_expected.items():
        fn = getattr(ta_mod, method, None)
        if fn is None:
            _check(method, False, 'function not found in module')
            api_ok = False
            continue
        in_whitelist = fn in frappe.whitelisted
        in_guest     = fn in frappe.guest_methods
        ok = in_whitelist and (in_guest == expect_guest)
        _check(f'{method:<32} whitelisted={in_whitelist}  guest={in_guest}',
               ok, f'Expected guest={expect_guest}')
        if not ok:
            api_ok = False

    results['API_PERMISSIONS'] = api_ok
    print('  API_PERMISSIONS =', 'PASS' if api_ok else 'FAIL')

    # ── CHECK 5: www pages exist ────────────────────────────────────────────
    print('\n[ CHECK 5 ] www Page Files')
    print('-' * 44)

    www_dir  = os.path.join(_BASE, 'www')
    pages_ok = True
    required_pages = [
        'smriti-platform-admin.html',
        'smriti-platform-admin.py',
        'smriti-trial-leads.html',
        'smriti-trial-leads.py',
    ]
    for page in required_pages:
        path = os.path.join(www_dir, page)
        ok   = os.path.isfile(path)
        if not ok:
            pages_ok = False
        _check(f'www/{page}', ok)

    results['WWW_PAGES'] = pages_ok
    print('  WWW_PAGES =', 'PASS' if pages_ok else 'FAIL')

    # ── CHECK 6: Sidebar — Commercial section ─────────────────────────────
    print('\n[ CHECK 6 ] Sidebar — Commercial Section')
    print('-' * 44)

    sidebar_path = os.path.join(
        _BASE, 'templates', 'includes', 'smriti_sidebar.html'
    )
    sidebar_ok = False
    trial_crm_link_ok      = False
    platform_admin_link_ok = False
    if os.path.isfile(sidebar_path):
        content = open(sidebar_path, encoding='utf-8').read()
        sidebar_ok             = 'Commercial' in content
        trial_crm_link_ok      = '/smriti-trial-leads' in content
        platform_admin_link_ok = '/smriti-platform-admin' in content

    _check('Commercial section label in sidebar', sidebar_ok)
    _check('/smriti-trial-leads link present',    trial_crm_link_ok)
    _check('/smriti-platform-admin link present',  platform_admin_link_ok)

    sidebar_all_ok = sidebar_ok and trial_crm_link_ok and platform_admin_link_ok
    results['SIDEBAR_COMMERCIAL'] = sidebar_all_ok
    print('  SIDEBAR_COMMERCIAL =', 'PASS' if sidebar_all_ok else 'FAIL')

    # ── CHECK 7: Start Trial Button in trial-leads page ───────────────────
    print('\n[ CHECK 7 ] Trial Leads CRM — Start Trial Button')
    print('-' * 44)

    leads_html = os.path.join(www_dir, 'smriti-trial-leads.html')
    btn_ok = False
    api_call_ok = False
    if os.path.isfile(leads_html):
        content = open(leads_html, encoding='utf-8').read()
        btn_ok      = 'btn-start-trial' in content and '🚀 Start Trial' in content
        api_call_ok = 'trial_activation_api.create_activation' in content

    _check('btn-start-trial CSS class present',            btn_ok)
    _check('trial_activation_api.create_activation called', api_call_ok)

    start_trial_ok = btn_ok and api_call_ok
    results['START_TRIAL_BUTTON'] = start_trial_ok
    print('  START_TRIAL_BUTTON =', 'PASS' if start_trial_ok else 'FAIL')

    # ── CHECK 8: Platform Admin page — access policy ──────────────────────
    print('\n[ CHECK 8 ] Platform Admin Page Controller')
    print('-' * 44)

    admin_py = os.path.join(www_dir, 'smriti-platform-admin.py')
    admin_ok = False
    if os.path.isfile(admin_py):
        src       = open(admin_py, encoding='utf-8').read()
        admin_ok  = (
            'Administrator' in src and
            'frappe.PermissionError' in src and
            'get_activation_dashboard' in src and
            'no_cache' in src
        )
    _check('Administrator-only guard present',       'Administrator' in open(admin_py).read() if os.path.isfile(admin_py) else False)
    _check('PermissionError raise present',          'frappe.PermissionError' in open(admin_py).read() if os.path.isfile(admin_py) else False)
    _check('get_activation_dashboard() called',      'get_activation_dashboard' in open(admin_py).read() if os.path.isfile(admin_py) else False)
    _check('no_cache = 1 set',                       'no_cache' in open(admin_py).read() if os.path.isfile(admin_py) else False)

    results['PLATFORM_ADMIN_CONTROLLER'] = admin_ok
    print('  PLATFORM_ADMIN_CONTROLLER =', 'PASS' if admin_ok else 'FAIL')

    # ── SUMMARY ───────────────────────────────────────────────────────────
    print('\n' + '=' * 64)
    print('SPRINT 3A VALIDATION SUMMARY')
    print('=' * 64)

    overall = True
    for name, passed in results.items():
        icon = 'PASS' if passed else 'FAIL'
        print(f'  {name:<35} = {icon}')
        if not passed:
            overall = False

    print()
    print('  SPRINT_3A_OVERALL =', 'PASS ✅' if overall else 'FAIL — see above ❌')
    print('=' * 64 + '\n')
