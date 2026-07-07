# SMRITI Retail OS — Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.1.7] — 2026-07-07

### Added
- Created a dedicated `error_pages` module containing Jinja-resolved `404.html`, `403.html`, `500.html`, and `503.html` templates.
- Created reusable glassmorphic layout component files (`error_page.html`, `error_page.css`, `error_page.js`) mapping tonamespaced SMRITI design tokens.
- Created pre-rendered static assets under `public/error_pages/` for immediate Nginx serving when Frappe backend services are offline.
- Added route aliases and redirect logic for `/500` and `/503` under `website_route_rules` in `hooks.py`.

### Changed
- Replaced custom page content in `www/404.html`, `www/smriti-404.html`, `www/403.html`, and `www/smriti-403.html` with centralized error module Jinja inclusions.
- Updated expected SHA-256 validation hashes inside `tests/test_branding_integrity.py` to match the newly styled templates.

### Fixed
- Fixed an unhandled validation crash during product catalog import dry-runs where invalid HSN code lengths (e.g. 7 digits) crashed the validate_import_rows API endpoint; wrapped the HSN loader in a try-except block to return validation messages gracefully as row-level errors.

## [2.1.6] — 2026-07-06

### Added
- Integrated static checks (permission audit, architecture compliance) and integration test execution into `.github/workflows/smriti_ci.yml`.
- Created `LookupRepository` and `MatrixRepository` classes to isolate direct database access.

### Fixed
- Completed a comprehensive manual security audit of all 161 whitelisted permission bypass endpoints, replacing generic comments with unique descriptions.
- Resolved 5 architecture boundary violations across lookup, variant lifecycle, purchase order, notification, and matrix engine services by routing database persistence operations through repository-layer abstractions.
- Resolved database setup issues in Tally Integration test modules by dynamically initializing parent and child Cost Centers and Round Off Accounts.

## [2.1.5] — 2026-07-06

### Fixed
- Fixed a test-isolation bug in the UAT seeding script `seed_psv_uat.py` where data from previous runs leaked into subsequent runs.
- Introduced `_clear_ledger_entries_by_company(company)` shared helper function to clear both `PSV Ledger Entry` and legacy `SMRITI Party Stock Ledger Entry` tables.
- Refactored `validate_compatibility_matrix()` and `cleanup_uat_data()` to utilize the shared helper function.
- Added row-count assertions for Scenarios A, B, and C to verify exact seeded ledger entries.

## [2.1.3] — 2026-07-06

### Added
- Route-level forced theme override inside SMRITI UI resolver to automatically apply a premium "Royal Black and White" theme on `/smriti-help`.

### Fixed
- Fixed accessibility contrast bugs on the Help Center page by mapping headings and native Hinglish definitions to theme-aware variables.
- Mapped Business Dictionary and Formula Registry pages to responsive SMRITI tokens, resolving dark-mode text and drawer background contrast conflicts.

## [2.1.2] — 2026-07-06

### Changed
- Migrated primary project license from MIT License to GNU General Public License v3.0 (GPL-3.0-only).
- Created `COPYING` file with verbatim GPLv3 text and added standard `NOTICE` file.
- Created `THIRD_PARTY_LICENSES.md` to document upstream framework and dependency licenses.
- Added `SPDX-License-Identifier: GPL-3.0-only` headers to SMRITI source code files.

## [2.1.1] — 2026-07-04

### Fixed
- Resolved undefined `frappe.db` client console error on the `/products` page by adding the whitelisted backend API `get_catalog_metadata` to load filter options.
- Resolved `400 (BAD REQUEST)` empty CSRF token error on `/products` and `/smriti` by injecting the global `window.csrf_token` and `window.csrfToken` variables.
- Resolved `403 (FORBIDDEN)` permission error on notification badge hydration by whitelisting `get_unread_count` in the notification API.
- Fixed collapsed sidebar layout: SMRITI brand logo now remains visible and centered when collapsed, and brand text collapses vertically.
- Configured custom dropdown select styles with premium SVG chevron arrow indicator, fixing unstyled native select filters in `products-toolbar`.
- Set `smriti_logo.svg` globally as the default favicon and app shortcut icon across all SMRITI pages and templates.
- Resolved Negative Stock Recovery Safety Net (KI-003) daily scheduler ImportError by creating package `__init__.py` and wrapper `run_safety_net` function.
- Implemented static AST-based scheduler/doc_events hook validation regression test suite (`test_scheduler_hooks.py`) to prevent future import/signature regressions.
- Resolved documentation compliance blockers (13 missing metadata headers and relative file paths in broken links), achieving 100% pass on Documentation Health Audit.
- Resolved license conflict by replacing the Apache 2.0 LICENSE file in the app directory with the canonical MIT License.
- Deleted the redundant `license.txt` file to maintain a single canonical LICENSE.
- Updated `SECURITY.md` to define actual SMRITI versioning support limits and correct vulnerability reporting contacts.
- Corrected Architecture Guard metrics in `QUALITY_DASHBOARD.md` to report real static checking count (770 remaining violations, 7.9% reduction from baseline) and locked in baseline progress.
- Cleaned up outdated `v1.8.x` version badges from root and app `README.md` files.

## [2.1.0] — 2026-07-04

### Added
- Automated E2E UI Integration Regression Test Suite (`test_ui_sidebar_regression.py`)
  with 5 test cases covering sidebar structure, CSS classes, hashchange, permissions,
  and developer bypass configuration.
- Config-driven `window.SMRITI_DEVELOPER_MODE` flag injected from `frappe.conf.developer_mode`
  via `smriti_token_loader.html`.
- Centralized role constants: `Roles.ACCOUNTANT`, `Roles.SALES_MANAGER`, `Roles.SMRITI_TEAM`.
- `RELEASE_GATE_CRITERIA.md` — formal release quality gate definitions.
- `QUALITY_DASHBOARD.md` — per-release health tracking dashboard.
- Purchase Studio dynamic sidebar with Left/Right/Top/Bottom placement, collapse toggle,
  popout buttons, and hash-based active highlighting.
- Customer Studio backend (api, service, repository layers).

### Changed
- Developer bypass in `smriti_ui_resolver.js` now reads `window.SMRITI_DEVELOPER_MODE`
  instead of checking `window.location.hostname`.
- Migrated raw role strings in `security_api.py` page access registry to centralized
  `Roles` class constants.
- Purchase Studio layout extracted to dedicated `purchase_layout.html` template and
  `smriti_purchase.css` stylesheet.
- Retired legacy standalone `/purchase` manager; redirects to `/smriti-purchase`.

### Fixed
- Corrected module import paths for `security_api` in regression test files.
- Added cache-busting `?v=2.0.5` parameters to resolver/theme manager script tags.
- Extended `blank.html` base template in Purchase, PO, and GRN standalone pages.
- Renamed hyphenated www page controllers to underscores for Frappe router resolution.
- Corrected central Roles import path in `security_api.py`.

---

## [2.0.0] — 2026-07-02

### Added
- Purchase Studio — full purchase lifecycle UI + service layer.
- UIE (Universal Integration Engine) — TallyPrime connectivity framework.
- SNM (Navigation Manager) — database-driven nav with Redis caching.
- SNSM (Negative Stock Engine) — policy-based stock management.
- 23 new DocTypes.
- Architecture Guard (`smriti_architecture_guard.py`) with CI pre-commit integration.
- SMRITI Connect Core and Tally reference implementation.
- Platform Vision v2.0 and Experience Constitution v1.0.
- Centralized `check_page_access()` policy for 41 page controllers.
- SMRITI Settings DocType with `default_item_group` and `default_hsn_code`.
- Custom POS override PIN field on User DocType.
- Sidebar 4-way position toggle, notification bell, user profile link.
- SMRITI Product Studio reference implementation.

### Changed
- 84 commits, 325+ files changed, +26,159 lines.
- Persistence Leak Migration completed across 6 batches.
- Complete legacy desk pages retirement (21 directories removed).

### Security
- Eliminated hardcoded UPI credentials from sizewise invoice.
- License fail-open guard with `table_exists()` check.
- TRUNCATE allowlists in `item_master_api.py` and `inventory_api.py`.
- Random per-process HMAC dev key when `dev_defaults.json` absent.

---

## [1.8.6] — 2026-06-15

### Added
- PSV Phase 2 enhancements.
- Barcode printing async queue.
- CGE (Customer Growth Engine) v1.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
