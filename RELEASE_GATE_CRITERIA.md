# SMRITI Retail OS — Release Gate Criteria (v2.x)

This document defines the mandatory quality, performance, and security gates that must be satisfied before any release candidate is tagged and deployed.

---

## 1. Architecture Governance Gate
* **Standard**: Zero boundary violations against the centralized dependency graph rules.
* **Verification Command**:
  ```bash
  python smriti_architecture_guard.py
  ```
* **Blocker Threshold**: Any violation raises a build blocker and fails CI/CD.

---

## 2. Automated Tests & UI Regression Gate
* **Standard**: 100% pass rate across python unit tests and E2E DOM regression assertions.
* **Verification Command**:
  ```bash
  bench run-tests --app smriti_retail_os
  ```
* **Core UI Checks**:
  * **Theme Persistence**: Theme preference remains active on refresh.
  * **Sidebar Layouts**: Full Left/Right/Top/Bottom placement layout changes and collapse transitions.
  * **Popouts**: Popout menu link buttons function correctly.
  * **Hash Routing**: Navigation path highlighting matches current location hash.

---

## 3. Performance Gate
Performance metrics are measured against the reference development environment:

| Action / Load Type | Target Threshold | Metric Type |
|---|---|---|
| **Cold Start Page Load** | `< 2.5 seconds` | Page Load Time |
| **Warm Page Load** | `< 1.0 seconds` | Page Load Time |
| **Theme Switching Transition** | `< 100 milliseconds` | UI Latency |
| **Sidebar Toggle / Placement** | `< 100 milliseconds` | UI Latency |

* **Asset Compilation Check**:
  * esbuild packaging and minification must build without warning.
  * Assets linked correctly with versioned cache-busting keys (`?v=2.x`).

---

## 4. Quality & Errors Gate
* **Mandatory Blocker**:
  * **0 JavaScript runtime errors** on page load.
  * **0 unhandled promise rejections**.
* **Review Item**:
  * Console warnings reviewed and verified to not impact performance or security.

---

## 5. Security & Access Gate
Centralized policy validation (`check_page_access()`) enforced at HTTP/Python controller layer:

| User Session / Role | Page Access Restriction | Expectation |
|---|---|---|
| **Anonymous / Guest** | Denied | Redirects to login, returns `403` |
| **SMRITI Cashier** | Billing / Transactions | No access to Security Center |
| **SMRITI Store Manager** | Store Operations / Configuration | Operations management |
| **Administrator** | Security Architect | Full unhindered access |

---

## 6. Accessibility (a11y) Gate
* **Keyboard Navigation**: Interactive elements must follow logical tab-focus order.
* **Visible Focus**: Clear visible border/outline focus ring on active interactive inputs/buttons.
* **Branding**: Contrast ratios matching SMRITI tokens (Navy `#1A2B5C` + Blue `#2563EB` on Dark/Light baselines).

---

## 7. Release & Documentation Gate
* **Version Increment**: Version bumped systematically in `hooks.py` and `setup.py`.
* **Release Notes**: Centralized log detailing changes, database schema patches, and breaking changes.
* **Backlog Audit**: Outstanding backlog items verified and logged under future roadmap milestones.
