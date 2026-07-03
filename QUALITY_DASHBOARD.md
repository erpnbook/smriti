# SMRITI Retail OS — Quality & Release Dashboard

This dashboard tracks the status, metrics, and health indices of SMRITI Retail OS before tagging a release candidate.

---

## 1. Quality Gates Overview

| Verification Gate | Required Threshold | Current Value / Status | Result |
|---|---|---|---|
| **Architecture Guard** | 0 boundary violations | 0 violations (statically checked) | **PASS** |
| **Backend Unit Tests** | 100% pass rate | All core tests pass | **PASS** |
| **UI Integration Tests** | 100% pass rate | 5/5 tests pass (`test_ui_sidebar_regression.py`) | **PASS** |
| **Security Gates** | Authorized role access policies | Centralized check verified on whitelisted APIs | **PASS** |
| **Performance Gates** | Cold <2.5s, Warm <1.0s, UI <100ms | Verified in reference dev environment | **PASS** |
| **Quality & Console** | 0 JS errors, 0 unhandled promise rejections | Checked and verified error-free | **PASS** |
| **Documentation Gates** | Release criteria & notes updated | RELEASE_GATE_CRITERIA.md active | **PASS** |

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

---

## 3. Reference Test Environment Specifications
* **Operating System**: Windows 11 / WSL2
* **Container Environment**: Docker (Frappe/ERPNext Backend v16)
* **Target Web Browser**: Chrome v138+
* **Database Engine**: MariaDB 10.6

---

## 4. Release History & Quality Ledger
* **SMRITI v2.1.0** (Current Build):
  * **Status**: Stable
  * **Automated Guard Run**: Successful
  * **Roles Audit**: Centralized under policy registry
  * **Release Authorization**: Approved
