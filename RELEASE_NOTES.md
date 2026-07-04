# SMRITI Retail OS — Release Notes v2.1.1

**Release Date**: 2026-07-04
**Codename**: Engineering Governance
**Previous Version**: v2.1.0

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

- **Negative Stock Recovery Safety Sweep (KI-003)**: Added missing `__init__.py` module package initializer and module-level `run_safety_net` hook wrapper to resolve daily scheduler ImportError at migration.
- **Product Catalog Console Blocker**: Added whitelisted backend API `get_catalog_metadata` to load filter metadata dynamically on `/products`, resolving client-side `frappe.db` undefined error.
- **Missing CSRF Token Bad Requests**: Injected global `window.csrf_token` and `window.csrfToken` variables on `/products` and `/smriti` dashboard pages to prevent `400 Bad Request` errors on POST API calls.
- **Unread Notification Badge Forbidden**: Whitelisted the `get_unread_count` API endpoint in the notifications controller to resolve `403 Forbidden` error on standalone pages.
- **Collapsed Sidebar Brand Logo**: Fixed sidebar CSS layout to keep the brand logo visible and centered in collapsed mode, and verticalized the brand text.
- **Styled Toolbar Filter Dropdowns**: Configured custom premium SMRITI dropdown CSS styles with an embedded SVG chevron arrow indicator, replacing browser-default select arrows.
- **Unified Favicon Configuration**: Defined the SMRITI logo globally as the default page favicon and app tab shortcut icon.

---

## Known Issues

- Billing integration tests (`test_billing_api.py`) fail due to missing POS Profile fixture data in the test environment.
- CGE (Customer Growth Engine) tests have intermittent failures in concurrency stress tests due to database lock contention.

---

## Commits Since v2.1.0

12 commits, covering scheduler path hotfixes, client-side API error corrections, CSRF token handling, and CSS layout/styling polishes.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
