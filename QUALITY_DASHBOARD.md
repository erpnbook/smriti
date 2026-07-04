# SMRITI Retail OS — Quality & Release Dashboard

This dashboard tracks the status, metrics, and health indices of SMRITI Retail OS before tagging a release candidate.

---

## 1. Quality Gates Overview

| Verification Gate | Required Threshold | Current Value / Status | Result |
|---|---|---|---|
| **Architecture Guard** | No regressions against baseline | 770 violations (87 files, 7.9% reduction from baseline) | **PASS** |
| **Backend Unit Tests** | 100% pass rate | All core tests pass | **PASS** |
| **UI Integration Tests** | 100% pass rate | 5/5 tests pass (`test_ui_sidebar_regression.py`) | **PASS** |
| **Scheduler Hook Tests** | 100% pass rate | 1/1 tests pass (`test_scheduler_hooks.py`) | **PASS** |
| **Security Gates** | Authorized role access policies | Centralized check verified on whitelisted APIs | **PASS** |
| **Performance Gates** | Cold <2.5s, Warm <1.0s, UI <100ms | Verified in reference dev environment | **PASS** |
| **Quality & Console** | 0 JS errors, 0 unhandled promise rejections | Checked and verified error-free | **PASS** |
| **Documentation Gates** | 100% audit compliance, 0 blocker errors | Health audit passed successfully | **PASS** |

---

## 2. Test Execution Details

### UI Integration Regression Suite (`test_ui_sidebar_regression.py`)
```
Running 5 unspecified-category tests for smriti_retail_os

smriti_retail_os.tests.test_ui_sidebar_regression.TestUISidebarRegression
    ✔  test_developer_bypass_configuration
    ✔  test_page_access_registry_policy
    ✔  test_sidebar_css_classes
    ✔  test_sidebar_includes_and_layout
    ✔  test_sidebar_js_hashchange_and_popout
----------------------------------------------------------------------
Ran 5 tests in 0.792s

OK
```

### Scheduler Hook Resolution Suite (`test_scheduler_hooks.py`)
```
Running 1 unspecified-category tests for smriti_retail_os

smriti_retail_os.tests.test_scheduler_hooks.TestSchedulerAndDocEventHooksResolve
    ✔  test_every_hook_path_resolves_to_a_callable
----------------------------------------------------------------------
Ran 1 test in 1.189s

OK
```

---

## 3. Reference Test Environment Specifications
* **Operating System**: Windows 11 / WSL2
* **Container Environment**: Docker (Frappe/ERPNext Backend v16)
* **Target Web Browser**: Chrome v138+
* **Database Engine**: MariaDB 10.6

---

## 4. Release History & Quality Ledger
* **SMRITI v2.1.1** (Current Build):
  * **Status**: Stable
  * **Automated Guard Run**: Successful
  * **Roles Audit**: Centralized under policy registry
  * **Scheduler Hooks Resolve**: 100% verified callable
  * **Documentation Health**: 0 blocker errors
  * **Release Authorization**: Approved

* **SMRITI v2.1.0**:
  * **Status**: Deprecated (Superceded by v2.1.1)
