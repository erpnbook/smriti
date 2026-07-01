# SMRITI Retail OS — Release Notes
# Version 2.0.0
# Release Date: 2026-07-02
# Repository: erpnbook/smriti (Frappe App)
# Previous Release: v1.8.6
# Commits Since Last Release: 84
# Files Changed: 325 files (+26,159 / -8,410 lines)

---

## Release Theme

**"Platform Expansion"** — Four new operational modules, a full UI/theme overhaul,
and a production-grade analytics layer covering the complete purchase lifecycle.

---

## New Features

### F-01 · Purchase Studio (smriti_retail_os.purchase_studio)
Full purchase lifecycle management — PO → GRN → Invoice → Returns.

  - SMRITI Purchase Center UI at /smriti-purchase (smriti-purchase.html)
  - Purchase Order: create, approve/reject, track by status
  - GRN / Purchase Receipt: receive against PO with warehouse assignment
  - Purchase Invoice: create standalone or against GRN; policy enforcement
  - Purchase Returns / Debit Notes
  - Supplier Ledger view per supplier
  - 18 whitelisted API endpoints in purchase_api.py
  - SMRITI Purchase Settings DocType (approval threshold, LC rule, policy)
  - SMRITI Purchase Audit Log DocType
  - SMRITI Purchase Studio Design Language (SSDL) v1.0 documentation

### F-02 · Purchase Analytics Studio (SAS — Purchase Category)
6 purchase reports in the SMRITI Analytics Studio.

  - purchase_order_summary — PO lifecycle with COALESCE(advance_paid,0) balance guard
  - grn_register — GRN log with pr.status and is_return=0 enforced at SQL
  - purchase_invoice_register — Invoices with overdue_days CASE guard (non-negative)
  - supplier_purchase_summary — Supplier aggregation with drill-down to invoices
  - item_wise_purchase — Item analysis with weighted avg rate (SUM/NULLIF pattern)
  - purchase_return_register — Debit notes with CGST/SGST/IGST split
  - Navigation: "Purchase Reports" section added to sidebar after Sales Reports
  - SAS catalog: 5 → 6 categories, 19 → 25 total reports

### F-03 · SMRITI UIE — Universal Integration Engine (smriti_retail_os.uie)
TallyPrime bidirectional sync framework.

  - UIE Integration Center console at /smriti-uie.html
  - Standard Connectivity Framework (SCF): BaseAdapter, TallyAdapter, SyncCoordinator
  - Sales Invoice submit hooks → Tally sync on submit
  - Purchase, Debit/Credit Notes, Payment Entry sync workflows
  - Customer and ledger auto-creation on first sync
  - Idempotency key with DB index (UIE-001) for duplicate-safe dispatch
  - 5 new DocTypes: SMRITI UIE Integration, Credential, Endpoint, Sync Log, Sync Queue
  - Legacy /smriti-tally compatibility redirect wrapper
  - E2E integration test: enqueue → dispatch → assert

### F-04 · SMRITI Navigation Manager (SNM)
Database-driven navigation with Redis caching.

  - NavigationManager replaces static CANONICAL_NAV dict where overrides exist
  - Redis-cached nav responses with invalidation on save
  - 6 new DocTypes: Profile, Assignment, Override, Permission, Favorite, Order
  - Barcode Studio dedicated navigation group
  - CLI health validator: bench execute smriti_retail_os.navigation.*

### F-05 · SMRITI Negative Stock Management Engine (SNSM)
Policy-based negative stock detection and recovery.

  - Negative stock case detection and policy engine
  - 4 new DocTypes: Case, Policy, Reason, Recovery
  - Scheduler safety net (runs on schedule)
  - CSS theme integration
  - Note: scheduler hook path fixed (was NegativeStockRecoveryService path error — non-breaking)

### F-06 · SMRITI Analytics Studio (SAS) v1.0 — General Foundation
Launched in this cycle (previously staged).

  - SMRITIReportEngine SQL engine (REPORT_QUERIES, filter chain, group-by, order-by)
  - Custom report runner (_run_custom_report dispatch)
  - SAS_REPORT_DEFAULTS metadata (chart type, KPI fields, conditional format rules)
  - sas_report_catalog.json static fixture
  - SMRITI Report Template DocType with columns_json / filters_json

---

## Enhancements

### E-01 · UI/Theme System Overhaul
  - smriti_tokens.css: canonical CSS custom property registry
  - validate_tokens.py: governance linter for token compliance
  - sleek-compact set as the single canonical fallback (THEME-005)
  - Dark mode defensive fallbacks added to setup wizard
  - token_loader included in all remaining www pages (global coverage)
  - Sidebar background token aligned; body data-theme synced via theme_manager.js
  - All disconnected c1 tokens replaced with canonical tokens
  - 37KB inline CSS duplication eliminated from sidebar

### E-02 · Barcode Studio — Label Studio v2.x
  - QZ Tray USB routing with print safety confirmations
  - Live autocomplete with keyboard navigation, debounce, and auto-loading
  - 4-step style resolution priority: style_code → variant_template → item_code → fallback
  - prnContent dict extraction fixed in USB / LAN / download flows
  - Signature validation and socket latency benchmarks
  - Secondary barcode support with system-wide validation hardening
  - SMRITI Barcode Settings migrated to file-backed DocType (patches/v1_8_7)

### E-03 · SMRITI Print Modal
  - Universal print modal replacing direct Frappe print routes
  - payments.html PDF download wrapped in SmritiPrint modal
  - Debranding: Frappe/ERPNext print routes no longer exposed

### E-04 · Security Debranding (SPC-Rule6 remediation)
  - frappe.client.insert / frappe.new_doc removed from HTML frontend files
  - All operations route through SMRITI service controllers
  - 4 HTML pages remediated (purchase pages)

### E-05 · CSRF / Session Hardening
  - Defensive csrf_token resolution across all www page controllers
  - Stale CSRF token and session expiration handling in sw.js
  - HTTP response status validation in fetch API helper

### E-06 · SMRITI Print Template
  - Migrated from programmatic to file-backed DocType module
  - Unit tests added

### E-07 · SMRITI Telemetry Event Definition
  - Migrated from programmatic to file-backed DocType (patches/v1_8_7)

### E-08 · Barcode Asset Hardening
  - Hardcoded version strings removed from www assets
  - Favicon injected via token_loader (global)
  - str.format replaced with safe substitute to prevent KeyError

### E-09 · Navigation Reconciliation
  - boot.py navigation deep copy regression fixed
  - SMRITI breadcrumb + parent group links clickable across 65 pages
  - initUIEngine reliability fix: token_loader instead of window.frappe guard

### E-10 · PWA / Offline
  - Advanced PWA v2: IndexedDB, background sync, push notifications
  - PWA launcher icons added

---

## Bug Fixes

### BF-01 · fix(spc-rule6): frappe.client calls removed from legacy purchase pages
### BF-02 · fix(tests): whitelist check corrected for Frappe v16 (frappe.whitelisted set)
### BF-03 · fix(purchase-studio): DocTypes moved to canonical module path
### BF-04 · fix(nav): release-blocker 404 routes in Purchase sidebar resolved
### BF-05 · fix(SAS): dataset_engine schema — correct POS Invoice column mapping
### BF-06 · fix(barcode): prnContent dict extraction in USB/LAN/download flows
### BF-07 · fix(barcode): str.format → safe substitute; warning returned on fallback
### BF-08 · fix(barcode): DocType query fixed (Item Attribute → Item Variant Attribute)
### BF-09 · fix(backup): deprecated with_files param resolved; root Item Group seeded
### BF-10 · fix(branding): SMRITI bag icon replaces default Frappe logo on login/setup
### BF-11 · fix(theme): --smriti-primary mapped to brand token (not hardcoded hex)
### BF-12 · fix(theme): unicode comment corruption resolved; missing tokens defined
### BF-13 · fix(route): smriti-home.html /app/smriti-* route dependency eliminated
### BF-14 · fix(api): HTTP status validation in fetch helper across www templates
### BF-15 · fix(barcode): style resolution priority corrected (4-step chain)
### BF-16 · fix(theme,nav): initUIEngine reliable on all pages via token_loader

---

## Performance

### P-01 · UIE N+1 eliminated
  - Payload builder decoupled from full document requirements
  - Batch pre-fetch pattern used

### P-02 · (Carried forward from v1.4.0 sprint)
  - Batch item defaults, tax templates, GST in billing create_invoice
  - Batch item prices in search_items
  - Batch item flags in purchase create_purchase_receipt

---

## Database Changes

4 new database patches applied since v1.8.6:

| Patch | Description |
|---|---|
| patches.v1_8_7.migrate_barcode_settings_to_standard | Migrates SMRITI Barcode Settings from programmatic to file-backed DocType |
| patches.v1_8_7.migrate_telemetry_event_to_standard | Migrates SMRITI Telemetry Event Definition to file-backed DocType |
| patches.v1_8_7.add_idempotency_key_index | Adds DB index on SMRITI UIE Sync Queue idempotency_key (UIE-001) |
| patches.seed_purchase_report_templates | Seeds 6 SMRITI Report Template records (Purchase category) — idempotent |

23 new DocTypes added:
  Purchase Studio: SMRITI Purchase Audit Log, SMRITI Purchase Settings
  Navigation: SMRITI Navigation Assignment, Override, Permission, Profile, Profile Favorite, Profile Order
  Negative Stock: SMRITI Negative Stock Case, Policy, Reason, Recovery
  UIE: SMRITI Tally Settings, Tally Sync Log, UIE Credential, UIE Endpoint, UIE Integration, UIE Sync Log, UIE Sync Queue
  Barcode: SMRITI Barcode Settings (migrated)
  Telemetry: SMRITI Telemetry Event Definition (migrated)

---

## API Changes

### New Endpoints (whitelisted, additive — no breaking changes)

Purchase Studio (smriti_retail_os.purchase_studio.api.purchase_api):
  get_purchase_dashboard, get_purchase_orders, get_purchase_order_detail,
  create_purchase_order, resolve_po_approval, get_grns, get_grn_detail,
  create_grn, create_invoice, get_invoices, get_invoice_detail,
  get_returns, create_purchase_return, get_supplier_ledger,
  get_purchase_settings, save_purchase_settings,
  search_suppliers, search_items

SAS Reports (smriti_retail_os.reports_api):
  run_report (enhanced — now handles purchase_order_summary, grn_register,
  purchase_invoice_register, supplier_purchase_summary,
  item_wise_purchase, purchase_return_register)

UIE (smriti_retail_os.uie.*):
  sync endpoints, credential management, integration status

Navigation Manager (smriti_retail_os.navigation.*):
  get_navigation, get_navigation_profile, override management

### Removed Endpoints
  None. Zero breaking API changes.

---

## Breaking Changes

None confirmed by diff analysis (0 removed @frappe.whitelist decorators).

---

## Known Issues

See KNOWN_ISSUES.md for full detail.

KI-001 · test_add_item_by_barcode — pre-existing test failure (unrelated to this release)
KI-002 · test_calculation_order_and_dual_discounts — pre-existing test failure
KI-003 · V17FrappeDeprecationWarning: limit_page_length deprecated — use limit (non-breaking, Frappe v16 only)
KI-004 · SNSM scheduler path error logged at migrate (non-breaking, recovery job skipped)
KI-005 · smriti-docker: demo company seeding disabled in Docker env config

---

## Deployment Notes

See MIGRATION.md for the full migration procedure.

Quick summary:
  1. Pull new image or update app source
  2. bench --site smriti_retail migrate
     (runs 4 new patches automatically)
  3. bench --site smriti_retail execute smriti_retail_os.patches.seed_purchase_report_templates.execute
     (idempotent — safe to re-run)
  4. Restart workers: bench restart
  5. Verify: bench --site smriti_retail execute smriti_retail_os.analytics_studio.sas_service.get_srs_report_list_for_sas

---

## Rollback Plan

  1. git -C apps/smriti_retail_os checkout v1.8.6
  2. bench --site smriti_retail migrate
  3. bench restart
  Note: DocType additions are additive — no data loss on rollback.
  Note: UIE Sync Queue records created during v2.0.0 will remain as orphaned rows (no data corruption).

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
