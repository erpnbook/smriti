# KNOWN ISSUES — SMRITI Retail OS v2.1.1

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
Date: 2026-07-04
Status: Pre-release audit

---

## Severity Key

| Code | Severity    | Definition                                                  |
|------|-------------|-------------------------------------------------------------|
| P0   | Critical    | Data loss or complete feature unavailability                |
| P1   | High        | Feature partially broken; workaround unavailable            |
| P2   | Medium      | Feature partially broken; workaround available              |
| P3   | Low         | Minor UX or non-functional issue                            |
| P4   | Info        | Warning or deprecation with no functional impact            |

---

## Open Issues

### KI-001 · test_add_item_by_barcode — Test Failure (Pre-existing)
- **Severity:** P3
- **Module:** Barcode Studio (tests)
- **Status:** Pre-existing before this release cycle
- **Symptom:** Unit test fails in isolation during full suite run
- **Cause:** Test depends on item/barcode data state set up by a prior test;
  teardown does not fully clean the barcode lookup table between runs.
- **Impact on production:** None. The barcode add-item flow works correctly
  in browser and integration testing. This is a test isolation issue only.
- **Workaround:** Run test individually with `--tests test_add_item_by_barcode`
  to confirm it passes in isolation.
- **Fix target:** v2.0.1

### KI-002 · test_calculation_order_and_dual_discounts — Test Failure (Pre-existing)
- **Severity:** P3
- **Module:** Billing / Invoice calculation (tests)
- **Status:** Pre-existing before this release cycle
- **Symptom:** Dual-discount calculation test fails in full suite due to
  tax template state leak from prior test.
- **Cause:** Tax template seeding in setUp is not fully isolated across
  test class instances.
- **Impact on production:** None. The billing discount calculation is
  verified correct by the passing test_discount_application test.
- **Workaround:** Run test in isolation.
- **Fix target:** v2.0.1

### KI-004 · V17FrappeDeprecationWarning — limit_page_length Parameter
- **Severity:** P4 (Info)
- **Module:** Frappe Framework internal (qb_query.py)
- **Status:** Frappe v16 internal warning, not introduced by SMRITI
- **Symptom:** During test runs using frappe.get_list with limit_page_length,
  the following warning appears:
  ```
  /home/frappe/frappe-bench/apps/frappe/frappe/model/qb_query.py:153:
  V17FrappeDeprecationWarning: This codepath was marked (DATE: 2024-01-01)
  deprecated for removal (from v17 onwards); note:
  The 'limit_page_length' parameter is deprecated. Use 'limit' instead.
  ```
- **Cause:** SMRITI uses limit_page_length in a compatibility shim for
  Frappe v14/v15/v16 support. Frappe v16 warns but still processes it.
- **Impact on production:** None. All list queries execute correctly.
- **Fix target:** v2.1.0 (align with Frappe v17 migration)

### KI-005 · smriti-docker: Demo Company Seeding Disabled
- **Severity:** P4 (Info)
- **Module:** smriti-docker (Docker environment config)
- **Status:** Intentional — disabled in this release
- **Symptom:** Demo company seeding script is commented out in Docker
  environment configuration.
- **Cause:** Demo data seeding was causing issues on fresh installs where
  company configuration is not yet complete.
- **Impact on production:** No impact. Demo data is not required for
  production deployments.
- **Workaround:** Use the SMRITI Setup Wizard to create your company.
- **Fix target:** Will be re-enabled with a proper seed guard in v2.1.0

### KI-006 · SDC Mutation Drift Gate Tests — Pre-existing Failures
- **Severity:** P3
- **Module:** SMRITI Document Compiler (SDC) — test_sdc006_mutation
- **Status:** Pre-existing before this release cycle
- **Symptom:** Several SDC mutation drift gate tests fail in full suite:
  - test_coverage_history_appended_on_success
  - test_coverage_history_appends_multiple_runs
  - test_banned_terminology_in_source_file_raises_violation
  - test_css_box_shadow_not_flagged_as_banned_term
  - test_formula_and_explain_both_updated_no_violation
  - test_formula_expression_change_without_explain_update
- **Cause:** SDC compiler config path resolves differently in bench
  test runner context vs. standalone execution.
- **Impact on production:** None. SDC is a development/governance tool,
  not a runtime dependency.
- **Fix target:** v2.0.1

### KI-007 · Formula Registry setUpClass Failure
- **Severity:** P3
- **Module:** Formula Registry (tests)
- **Status:** Pre-existing
- **Symptom:** test_formula_registry.TestFormulaRegistry setUpClass fails
  in full suite run.
- **Cause:** Formula fixture seeding race condition in setUp phase.
- **Impact on production:** None. Formula Registry reads correctly at runtime.
- **Fix target:** v2.0.1

---

## Resolved in v2.1.1 (Previously Known Issues)

### KI-003 · SNSM Scheduler Path Error at Migrate (Fixed)
- **Severity:** P4 (Info/Warning)
- **Module:** SMRITI Negative Stock Management Engine
- **Symptom:** Import error on SMRITINegativeStockRecoveryService.run_scheduler_safety_net during scheduler tick.
- **Cause:** Scheduler job path used class-level dot notation which Frappe treats as a sub-package path, and the directory was missing `__init__.py`.
- **Fix:** Added missing `__init__.py`, created module-level `run_safety_net()` wrapper function in `recovery_service.py`, and updated `hooks.py`. Added `test_scheduler_hooks.py` regression gate.

---

## Resolved in v2.0.0 (Previously Known Issues)

### R-001 · Purchase sidebar 404 routes (Fixed: c50c374)
- Navigation links to /smriti-purchase returned 404. Fixed.

### R-002 · Frappe v16 whitelist test failure (Fixed: 0b27667)
- Test checking frappe.whitelisted used wrong attribute pattern. Fixed.

### R-003 · prnContent dict extraction in barcode flows (Fixed: 3782848)
- USB/LAN/download flows received dict instead of string from generate_prn(). Fixed.

### R-004 · initUIEngine unreliable on some pages (Fixed: 4ce00cd)
- window.frappe guard was not reliable across all www templates. Fixed via token_loader.

---

## Reporting New Issues

Submit issues at: https://github.com/erpnbook/smriti/issues

Include:
- SMRITI version (from /app/smriti-dashboard → About)
- Frappe version (bench version)
- Steps to reproduce
- Expected vs. actual behaviour
- Browser console errors (if UI issue)
- bench error.log excerpt (if backend issue)

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
