# SMRITI Retail OS — Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

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
