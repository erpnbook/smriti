# SMRITI Retail OS — Release Notes v2.1.0

**Release Date**: 2026-07-04
**Codename**: Engineering Governance
**Previous Version**: v2.0.0

---

## Highlights

This release transitions SMRITI Retail OS from feature development into a quality-assured,
governance-driven release process. It introduces automated verification infrastructure,
centralized security constants, and formal release gate criteria.

---

## New Capabilities

### 1. Automated UI Integration Regression Test Suite
- 5 automated Python tests covering sidebar DOM structure, CSS classes,
  hashchange navigation, page access policy enforcement, and developer bypass configuration.
- Tests execute headlessly in the Docker test environment via `bench run-tests`.

### 2. Config-Driven Developer Bypass
- Replaced hostname-based loopback check (`localhost/127.0.0.1`) with server-controlled
  `window.SMRITI_DEVELOPER_MODE` flag injected from `frappe.conf.developer_mode`.
- Backend security controls remain authoritative in production.

### 3. Centralized Roles Constants Registry
- Added `Roles.ACCOUNTANT`, `Roles.SALES_MANAGER`, `Roles.SMRITI_TEAM` to the
  centralized `roles.py` class.
- Migrated all remaining raw string role references in the page access policy registry.

### 4. Release Governance Documents
- **RELEASE_GATE_CRITERIA.md**: Defines mandatory pass/fail thresholds for architecture,
  tests, performance, security, accessibility, and documentation.
- **QUALITY_DASHBOARD.md**: Tracks per-release health status across all quality gates.

### 5. Purchase Studio Sidebar Integration
- Dynamic sidebar with Left/Right/Top/Bottom placement controls.
- Collapse/expand toggle with smooth CSS transitions.
- Popout buttons on all menu items for multi-window workflows.
- Hash-based navigation highlighting matching the Space Midnight dark theme.

---

## Architecture & Governance

- Architecture Guard: `[OK] No new architecture boundary violations.`
- Legacy desk page retirement complete (21 directories removed in v2.0.0).
- Boot.py desk redirection enforced for all `/desk/*` routes.

---

## Fixes

- Corrected module import paths for `security_api` in regression tests.
- Added cache-busting version parameters to SMRITI resolver and theme manager scripts.
- Extended `blank.html` base template in Purchase, PO, and GRN pages to load Frappe JS.
- Renamed hyphenated www page controllers to underscores for Frappe router resolution.

---

## Known Issues

- Billing integration tests (`test_billing_api.py`) fail due to missing POS Profile
  fixture data in the test environment. These tests require a fully configured POS
  Profile with warehouse, price list, and payment modes. This is a pre-existing
  test data issue and does not affect production billing functionality.
- CGE (Customer Growth Engine) tests have intermittent failures in concurrency stress
  tests due to database lock contention under parallel execution.

---

## Commits Since v2.0.0

75 commits, spanning architecture governance, UI refactoring, automated testing,
security hardening, and documentation improvements.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
