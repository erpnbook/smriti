# CHANGELOG — SMRITI Retail OS

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] — 2026-06-20

### Remediation Directive — 10/10 Audit Score (Phases 0–4)

> Authority: Jawahar R. Mallah / AITDL
> Applies to: smriti_retail_os app
> Status: Phases 0–4 Complete | Phases 5–6 In Progress

---

## [1.4.0] — 2026-06-20

### Added
- **psv_snapshot_service.py** (Phase 4): Dedicated module for landing cost resolution,
  inventory aging buckets, and PSV snapshot generation. Extracted from `psv_service.py`.
- **psv_health_service.py** (Phase 4): Dedicated module for operational health alerts,
  exception management, and daily health check scheduler.
- **psv_analytics_service.py** (Phase 4): Dedicated module for redistribution suggestions,
  WOC stock cover risk, sell-in/sell-out summary, channel stock trend, and
  SKU productivity (GMROI) analytics.
- **psv_migration_service.py** (Phase 4): Dedicated module for ledger reversal entry
  creation and legacy SMRITI PSA → PSV Channel Partner migration.
- **scripts/fix_boilerplate_headers.py** (Phase 3): Automated tool that replaces
  incorrect `@description` headers across 139 Python files with accurate descriptions.
- **scripts/split_psv_service.py** (Phase 4): Automated tool for splitting monolithic
  `psv_service.py` into focused sub-service modules with backward-compat re-exports.
- **validation_reports/benchmark_analysis_report.md** (Phase 2): Corrected benchmark
  report with explicit PASS/FAIL derivation. Documents that `full_scan=True` with
  `index_exists=True` is PASS (optimizer choice), not a bug.

### Changed
- **psv_service.py**: Reduced from 1,820 → 416 LOC (77% reduction). Retains core
  transaction engine, hook handlers, upload processing, and opening balance import.
  All extracted functions re-exported for backward compatibility.
- **seed_psv_uat.py → _write_benchmark_report()**: Replaced misleading NOTE ("full
  scan acceptable ONLY when table is empty") with accurate PASS/FAIL derivation
  documentation. Added `Scan assessment` field per query and `Reason` column to
  assertion table.
- **license/key_validator.py → _get_secret()**: Implemented fail-closed behavior.
  Now raises `frappe.ValidationError` in production if `smriti_license_secret` is
  not set, preventing silent fallback to the development secret.

### Fixed
- **Phase 1 (Security)**: License validator no longer silently falls back to the
  embedded `_FALLBACK_SECRET` in production environments.
- **Phase 2 (Performance)**: Benchmark report self-contradiction resolved. Report
  generator now accurately explains when `full_scan=True` is acceptable vs. an issue.
- **Phase 3 (Documentation)**: 139 Python files had incorrect `@description:
  "Handles user login, registration, and JWT token generation"` — now replaced with
  accurate per-file descriptions derived from module path and purpose.
- **Phase 4 (Architecture)**: `psv_service.py` was a 1,820-LOC monolith violating
  the single-responsibility principle. Split into 4 focused service modules.

---

## [1.3.2] — 2026-06-19

### Added
- **smriti-knowledge-center** (Sprint 4): Full Knowledge Center page at `/smriti-knowledge-center`
  with unified search across manuals, formulas, and dictionary terms.
- **smriti-dictionary** (Sprint 3): Business Dictionary page at `/smriti-dictionary`
  with term lookup, formula cross-links, and ⓘ Explain integration.
- **smriti-formula-registry** (Sprint 2 KGF): Formula Registry page with worked
  examples, interpretation guides, and Explain Engine integration.
- **SMRITI Universal Explain Engine**: `explain_api.py` and `explain_service.py` —
  ⓘ modal system providing business meaning, formula, worked example, and
  recommended action for every KPI, score, and forecast shown in SMRITI UI.
- **PDT Dashboard** (Product Digital Twin): SKU-level health scoring, GMROI tracking,
  velocity analysis, and lifecycle stage classification (Star/Cash Cow/Underperformer/
  Slow Mover/Stockout Winner).
- **CGE Module** (Channel Gross Earnings): Channel partner commission calculation
  engine with rule-based processing and v2 constraint validation.
- **SMRITI Sidebar v2.2.1**: Full navigation tree with CGE, PDT, Knowledge Center,
  and Coming Soon registry for future feature discovery.

### Changed
- Sidebar `cgE_enabled`, `pdt_enabled`, `knowledge_enabled` now default `true`.
- SMRITI Coming Soon page updated with live feature registry from `coming_soon_api.py`.

### Fixed
- **BUG-002**: PSV upload duplicate file check was using wrong SQL column (`parent`
  does not exist in `tabPSV Sell-Through Upload`). Fixed to use `file_hash` field
  with SHA-256.
- **BUG-004**: `process_sales_upload_cancel` was writing direct `make_ledger_entry()`
  calls causing double-reversal. Fixed to cancel the SMRITI PSV Transaction which
  handles ledger reversal atomically.
- **BUG-005**: `psv_analysis_service.py` was referencing non-existent DocTypes
  `PSV Reorder Rule` and `PSV Balance`. Fixed to use `SMRITI PSV Reorder Rule`
  and live ledger balance via `balance_engine`.
- **BUG-006**: PSV fingerprint deduplication only checked `docstatus=1`. Fixed to
  check `docstatus IN (0, 1)` to close the race window between draft and submit.
- **F4-FIX**: Overselling race condition in concurrent PSV sales uploads fixed with
  Redis SET NX distributed lock per Party Stock Account.
- **INT-004**: `import_opening_balances` was not idempotent. Fixed with date-scoped
  pseudo-reference as fingerprint source.
- **SEC-004**: `process_opening_balance` was accessible to all authenticated users.
  Fixed with `frappe.only_for(["System Manager", "SMRITI Store Manager"])`.

---

## [1.3.1] — 2026-06-11

### Added
- PSV v1.9.0-RC1 UAT validation suite (`seed_psv_uat.py`): 5-phase validation
  including seed, migration, compatibility, footwear UAT, and benchmark analysis.
- Composite index `smriti_psv_ledger_company_cp_variant` on
  `(company, channel_partner, item_variant, posting_datetime)` for PSV Ledger Entry.
- `backup_api.py` security hardening: rate limiting, file path validation, and
  audit logging for all backup operations.

### Changed
- PSV System Settings: Added `star_velocity_threshold`, `weeks_of_cover_critical`,
  `weeks_of_cover_warning`, `redistribution_scope` fields.

---

## [1.3.0] — 2026-05-28

### Added
- **PSV (Party Stock Visibility)** core module: SMRITI Party Stock Account, SMRITI
  Party Stock Ledger Entry, SMRITI PSV Transaction DocTypes.
- **PSV Channel Partner** (v1.1+): New architecture with brand associations,
  territory/region/zone fields, and fiscal year tracking.
- **PSV Stock Aging Snapshots**: FIFO aging bucket calculation (0–30, 31–60,
  61–90, 91–180, 180+ days) with daily snapshot generation.
- `balance_engine.py`: Centralized balance aggregation with Redis caching.
- `ledger_engine.py`: Immutable ledger entry writer with deduplication fingerprints.
- SMRITI Boot Guard: `boot.py` intercepts `/desk/*` routes and redirects to `/smriti`.

### Fixed
- Setup wizard exposure: Boot hooks prevent Frappe setup wizard from appearing on
  fresh installs (Rule 8 compliance).

---

## [1.2.10] — 2026-04-15

### Added
- SMRITI POS (Point of Sale) experience with custom billing flow.
- Barcode scanning integration (`barcode_api.py`).
- Sizewise invoice grouping (`sizewise_invoice_api.py`).
- Brand Master, Category Master SMRITI pages.

---

## [1.0.0] — 2026-01-01

### Added
- Initial SMRITI Retail OS release.
- Core pages: `/smriti` dashboard, `/smriti_login`, `/smriti_safe`.
- SMRITI branding system (Navy #1A2B5C + Blue #2563EB).
- Frappe/ERPNext integration layer per Architecture Directive Rule 7.

---

> **Author**: Jawahar R. Mallah — Founder & Chief Architect, AITDL
> **Contact**: jawahar.mallah@gmail.com
> **License**: MIT — Copyright © 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
