# CHANGELOG — SMRITI Retail OS

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.2.15] — 2026-06-27

### UI & Modal Resiliency Improvements

#### Fixed
- **`www/billing.html` — Modal display fix**: Removed inline `style="display:none;"` from `item-options-modal`, `bill-discount-modal`, and `manager-override-modal`. Visibilities are now cleanly driven by the CSS `.open` class to prevent modals remaining hidden on click.
- **`www/billing.html` — API error formatting**: Improved `api()` fetch error handler to extract user-friendly error messages from double-encoded `_server_messages` or final exception traceback lines, preventing full Python tracebacks from leaking into the cashier override UI.

---

## [1.2.14] — 2026-06-27

### HARDEN-9.3 — Production Quality Hardening (Score 9.0 → 9.3)

> Authority: Jawahar R. Mallah / AITDL  
> Review result: 9.0 → 9.3 / 10 (four targeted fixes)

#### Added
- **`.github/workflows/smriti_ci.yml`**: GitHub Actions CI pipeline (Frappe-free gate).
  Runs on every push to `main` and every pull request:
  1. Python syntax check — `py_compile` all `*.py` files
  2. SDC compiler — `python sdc/discovery.py` must exit 0
  3. Architecture fitness tests — 4 file-scanning governance tests (no DB required)
  4. SDC-006 mutation tests — 6 pure-Python mutation tests
  - Integration tests explicitly scoped out with comment: `bench run-tests --app smriti_retail_os`

#### Fixed
- **`barcode_api.py` — `_process_print_job()` failure path**: Added `frappe.log_error()` before
  `log_print_job()`. Print job failures now appear in Frappe admin **Error Log** (`/app/error-log`)
  in addition to the local file log and Activity Log. Administrators no longer need file system
  access to diagnose background worker failures.
- **`item_master_api.py` — `get_style_details()` N+1 elimination**: Replaced 3 per-variant
  `frappe.db.get_value()` calls in a loop with 3 bulk `frappe.get_all()` queries total.
  For a 20-size footwear style: 60 queries → 3 queries. Also corrected `color_val` from
  taking arbitrary `variants[-1]` color to collecting unique colors across all variants via
  `dict.fromkeys()` — multi-color styles (combo packs) now correctly return `"Black, Brown"`
  instead of whichever variant happened to be last.
- **`services/field_explorer_service.py` — version alignment**: `@version 1.0.0` → `1.2.14`
  to align with the repo canonical version declared in `hooks.py`.

---

## [1.2.13] — 2026-06-26

### UFE-001 — SMRITI Universal Field Explorer

> Authority: Jawahar R. Mallah / AITDL  
> Approved rating: 9.8/10

#### Added
- **`services/field_explorer_service.py`**: Canonical metadata service for all SMRITI field
  discovery. Reads `frappe.get_meta()` live with 1-hour TTL cache. Contains `FIELD_ID_REGISTRY`
  — stable Field ID → path mapping used by Barcode Studio.
- **`api/field_explorer_api.py`**: 6 whitelisted endpoints:
  - `get_doctype_fields` — fields of any DocType grouped by section
  - `get_document_data` — real field values for any document
  - `search_fields` — cross-DocType field name search
  - `get_field_relationships` — linked DocType tree
  - `resolve_label_preview` — resolve Field IDs/paths to real values
  - `get_field_id_registry` — canonical Field ID registry (printable fields only or all)
- **`www/smriti-field-explorer.html`**: Full SMRITI page at `/smriti-field-explorer`. Six tabs:
  1. **Field Explorer** — browse fields grouped by section, `[C]` badge for custom fields, one-click path copy
  2. **Document Data** — inspect real document values, blank fields highlighted amber
  3. **Cross-Search** — search "gstin", "barcode" etc across all retail DocTypes
  4. **Label Preview** — paste Field IDs or paths + document name → resolve values before printing
  5. **Relationship Tree** — linked DocType hierarchy with expandable nodes
  6. **Barcode Mode** — Field ID registry (stable IDs only, not raw paths)
- **`www/smriti-field-explorer.py`**: Auth + context controller for the UFE page.
- **`public/js/smriti_field_explorer_widget.js`**: Embeddable modal widget. Any SMRITI page
  can call `smritiFieldExplorer.openModal({ doctype, mode, onSelect })` to open Field Explorer
  inline without navigating away. Callback receives `{ field_id, label, fieldname, path, doctype, fieldtype }`.

#### Changed
- **`hooks.py`**: Added `Custom Field` and `DocType` `on_update` cache invalidation hooks.
  New custom fields added in ERPNext appear in UFE within seconds — no bench restart needed.
  Added `/smriti-field-explorer` website route entry.

#### Architecture Decision (Barcode Studio — Field ID Pattern)
Barcode Studio stores stable **Field IDs** (`ITEM_BARCODE`, `ITEM_MRP`, `ITEM_SIZE`)
not raw paths (`Item.barcodes[].barcode`). If the underlying ERPNext path changes tomorrow,
only `FIELD_ID_REGISTRY` in `field_explorer_service.py` is updated — every label template
continues to work without modification. This is the approved architecture from the 9.8/10
design review by Jawahar R. Mallah.

---

## [1.2.12] — 2026-06-26

### SDC-006 — Knowledge Governance Production Hardening

> Authority: Jawahar R. Mallah / AITDL  
> Final score: 9.0/10 (up from 8.6 before this sprint)

#### Added
- **`sdc/knowledge_health_policy.json`** (SDC-POL-001): Single Source of Truth for all
  SDC governance policy. Centralises banned terms, scan extensions, ignore paths, and
  tolerances. Previously scattered across `discovery.py` and tests.
- **SDC-006 Fail-Fast Policy Loading**: `SDCPolicy.load()` validates schema immediately on
  startup — missing or malformed policy file raises `SystemExit(1)` with a clear diagnostic.
  Silent defaults eliminated.
- **`sdc/tests/test_sdc006_mutation.py`**: 6 mutation tests:
  - `test_banned_terminology_in_source_file_raises_violation` — confirms shadow ledger detection
  - `test_css_box_shadow_not_flagged_as_banned_term` — CSS `box-shadow` not a false positive
  - `test_formula_expression_change_without_explain_update` — drift detection
  - `test_formula_and_explain_both_updated_no_violation` — clean update passes
  - `test_coverage_history_appended_on_success` — trending works
  - `test_coverage_history_appends_multiple_runs` — multi-run history
- **Coverage Trend History**: `sdc/coverage_history.json` — each SDC run appends a timestamped
  snapshot of `coverage_pct`, `health_score`, and `total_formulas`. Enables longitudinal tracking.
- **`sdc/tests/test_knowledge_governance.py` — Architecture Fitness Tests** (lines 245–320):
  - `test_no_hardcoded_evidence_badge` — evidence badge must be dynamic, never hardcoded
  - `test_no_banned_terminology` — zero occurrences of `shadow ledger` in production code
  - `test_every_formula_has_explain_object` — every formula must have a matching explain object
  - `test_no_orphan_knowledge_objects` — no orphaned KPIs or explain objects

#### Fixed
- **P1A — Evidence badge dynamic**: `build_context_pack(return_metadata=True)` now returns
  actual edge count from `seen_edges` and derives `validation_status` (Draft/Certified/Verified)
  dynamically. Hardcoded `"12 Graph Links"` eliminated.
- **P1B — Transaction integrity** (`billing_api.py`, `transaction_kernel.py`):
  - Critical paths: `create_custom_sales_return`, `update_sales_return`, `delete_sales_return`,
    `_build_and_persist_doc` — all now `rollback + raise`
  - Auxiliary paths: `set_taxes`, address sync — `log_error` only, no raise (per architecture decision)
- **P2A — Banned terminology**: Zero occurrences of `shadow ledger` in production code.
  10 remaining occurrences are all legitimate: SDC `banned_terms` list definition (1),
  `test_sdc006_mutation.py` deliberate injection tests (6), `test_knowledge_governance.py`
  docstrings/assertions (3).
- **`smriti-presentation.html`**: Removed `shadow ledger` terminology from slide content.
  Remaining `shadow` hits are CSS (`box-shadow`, `shadow-lg`) — styling, not banned terminology.

---

## [Unreleased] — 2026-06-20

### Remediation Directive — 10/10 Audit Score (Phases 0–4)

> Authority: Jawahar R. Mallah / AITDL
> Applies to: smriti_retail_os app
> Status: ALL 6 PHASES COMPLETE ✅

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
