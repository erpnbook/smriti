---
Document ID: "SMRITI-REL-001"
Title: "SMRITI Master Release Notes"
Owner: "Release Engineering Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

﻿---

## 🚀 v2.0.0 — Platform Expansion (2026-07-02)

### 🏗️ 1. Purchase Studio — Full Purchase Lifecycle
- **Purchase Center** (`/smriti-purchase`): End-to-end procurement workflow for retail and distribution operations.
- **Purchase Orders**: Create, track, approve/reject with configurable threshold-based approval policy.
- **GRN Register**: Receive goods against PO with warehouse assignment, quantity variance tracking.
- **Purchase Invoice**: Create standalone or GRN-linked; policy enforcement (GRN-only or standalone modes).
- **Purchase Returns**: Debit notes with CGST/SGST/IGST split, linked back to original receipt.
- **Supplier Ledger**: Per-supplier transaction history with date range filters.
- **Purchase Settings**: Configure approval threshold, LC rule, invoice policy from SMRITI admin panel.

### 📊 2. Purchase Analytics Studio — 6 New Purchase Reports
Six new reports added to the SMRITI Analytics Studio (SAS) under the **Purchase** category:
- **SMRITI Purchase Order Summary** — PO lifecycle with balance tracking.
- **SMRITI GRN Register** — Receipts log (returns excluded by default).
- **SMRITI Purchase Invoice Register** — Invoices with overdue days, bill reference.
- **SMRITI Supplier Purchase Summary** — Supplier-level aggregation with drill-down.
- **SMRITI Item-wise Purchase Analysis** — Item procurement with weighted average rate.
- **SMRITI Purchase Return Register** — Debit notes with GST component split.

### 🔗 3. UIE — Universal Integration Engine (TallyPrime)
- **UIE Integration Center** (`/smriti-uie`): Bidirectional sync between SMRITI and TallyPrime.
- **Standard Connectivity Framework (SCF)**: BaseAdapter + TallyAdapter + SyncCoordinator pattern.
- **Voucher Sync**: Sales Invoice, Purchase Invoice, Debit/Credit Notes, Payment Entries.
- **Auto Ledger Creation**: Customer and mapped settings ledgers (Sales, Cash, Bank, Duties) created automatically on first sync.
- **Idempotency**: DB-indexed sync queue prevents duplicate voucher submission.

### 🗺️ 4. Navigation Manager (SNM)
- **Database-driven Navigation**: Nav profiles stored in DocTypes, Redis-cached for performance.
- **User Overrides**: Per-user navigation order, favorites, and permission-based visibility.
- **Barcode Studio Group**: Dedicated navigation group consolidating Label Studio, Print Templates, Sizewise CRUD.

### 📉 5. Negative Stock Management Engine (SNSM)
- **Policy-based Detection**: Configurable negative stock policy with reason codes.
- **Case Management**: Each negative stock event tracked as a case with audit trail.
- **Recovery Workflow**: Operator-approved recovery actions with full before/after logging.

### 🎨 6. UI/Theme System Overhaul
- **Token Registry** (`smriti_tokens.css`): Single canonical CSS custom property source.
- **Validator** (`validate_tokens.py`): Governance linter catches disconnected tokens.
- **sleek-compact** established as the single canonical theme fallback (THEME-005).
- **Dark Mode**: Defensive fallbacks added to setup wizard and all page controllers.
- **Global Coverage**: `token_loader` now included in all www pages.

### 🏷️ 7. Barcode Studio v2.x Enhancements
- 4-step style resolution priority: `variant_of → custom_style_code → style_no → SKU split`.
- prnContent dict extraction fixed in USB, LAN, and download print flows.
- Signature validation, socket latency benchmarks, native print analytics.
- str.format replaced with `safe_substitute` to prevent KeyError on missing tokens.

### 🔒 8. Security & Hardening
- `frappe.client.insert` / `frappe.new_doc` removed from all HTML frontend files (SPC Rule 6 full compliance).
- Defensive CSRF token resolution across all www page controllers.
- HTTP response status validation in fetch API helper.

---
---
Document ID: "REL-010"
Title: "ðŸš€ Release Notes â€” SMRITI Retail OS"
Owner: "Release Team"
Audience: "Executive / Team"
Module: "PSV"
Version: "1.1.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-30"
Last Reviewed: "2026-06-30"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# ðŸš€ Release Notes â€” SMRITI Retail OS

## ðŸ†• v2.4.1 â€” SMRITI Barcode Studio Token & Print Fixes (2026-06-30)

### ðŸ”– 1. Style/Article No Fallback Resolution Chain
- **4-Step Fallback Priority**: Resolved style token printing on variant items by replacing the single-step SKU hyphen split with a robust 4-step priority sequence (`variant_of` $\rightarrow$ `custom_style_code` $\rightarrow$ `style_no` $\rightarrow$ SKU hyphen split fallback). Variant items now correctly print their parent template code (e.g. `BBM-0001` instead of `BBM`).

### ðŸ§¬ 2. Extended Print Layout Tokens
- **New Dynamic Placeholders**: Added explicit `{style_code}` (direct alphanumeric code mapping) and `{variant_template}` (direct `variant_of` mapping) tokens to print data payloads, allowing templates to print specific style identifiers without resolution split fallbacks.

### ðŸ”Œ 3. QZ Tray Dict Payload & USB Print Crash Fix
- **WebSocket Payload Parsing**: Resolved the USB printing WebSocket error `TypeError: data[i].data.search is not a function` by extracting raw PRN ZPL/TSPL string from the backend dictionary response (`prnContent.prn || prnContent`) in download, LAN, and USB print flows.
- **Fallback Template Warnings**: Wired up warning toast notifications to alert the user if a fallback label size template was rendered due to custom template issues.

---

## ðŸ†• v2.4.2 â€” SMRITI Barcode Studio Navigation Consolidation (2026-06-30)

### ðŸ—‚ï¸ 1. Dedicated Barcode Studio Sidebar Group
- **New Menu Group**: Added a standalone `Barcode Studio` navigation group placed between `Inventory` and `Finance` in the SMRITI sidebar.
- **Consolidated Items**:
  - `Label Studio` (formerly **Barcode Center**) â€” moved from `Inventory`, route `/barcode`
  - `Print Templates` â€” moved from `Inventory`, route `/print-templates`
  - `Sizewise Item CRUD` â€” moved from `Masters`, route `/sizewise_item`
  - `Sizewise Invoice` â€” moved from `Sales`, route `/sizewise_invoice`

### ðŸ”„ 2. Backward-Compatible Routing
- **Legacy Redirect Preserved**: The old `/barcode-center` route continues to redirect to `/barcode` via `hooks.py` `website_route_rules`, ensuring saved bookmarks remain functional.

### ðŸ”§ 3. Dual-Config Sync
- Both `smriti_nav_config.js` (client-side) and `navigation_service.py` (`CANONICAL_NAV` server-side) updated in perfect sync to ensure consistent navigation across developer builds, Redis-cached sessions, and database-driven navigation profiles.

---

## ðŸ†• v2.4.0 â€” SMRITI Barcode Studio V2.4a Layout & Operations Upgrade (2026-06-21)

### ðŸ”– 1. Warehouse Article Range Loader
- **Sequential Range Inputs**: Added dynamic From/To Article fields (e.g. `BBM-0001` to `BBM-0100`) allowing operators to fetch and load lists of sequential styles directly into the worksheet grid in a single click.

### ðŸ§¬ 2. Automatic Variant Expansion
- **Fashion-Retail Variant Generator**: Input styles (e.g. `BBM-001`) automatically expand to their full set of size/color SKU variations (e.g. `BBM-001-NAVY-S`, `BBM-001-NAVY-M`, `BBM-001-NAVY-L`) by scanning existing item variants in the database.

### ðŸ“‹ 3. Interactive Worksheet Grid
- **Comprehensive 9-Column Workspace**: Standardized the empty barcode editor canvas into a rich grid featuring: `Select | Article | Item Name | Brand | Color | Size | Barcode | MRP | Qty | Labels` for print job management.
- **Zebra-Striping & Keyboard Accessibility**: Styled worksheet rows with subtle hover transitions and full input control.

### ðŸ‘ï¸ 4. Dynamic Mapping Preview
- **Tag Token Mappings**: Shows real-time mappings of layout tags (such as `{barcode}`, `{item_code}`, `{item_name}`, `{brand}`, and `{mrp}`) to actual database values in an interactive sidebar panel before sending print jobs.

### ðŸ“¦ 5. Transaction Expansion Modal
- **Bulk Receipt Imports**: Fetching transaction IDs (e.g. Purchase Receipts, Purchase Orders, Goods Receipt Notes) opens a grid showing the count of items found, with quick selection filters: "Select All", "Only Missing Labels", "Only New SKUs".

### âš–ï¸ 6. Box & Carton Packing Quantity Rules
- **Carton Mode Computations**: Quantities can be computed based on outer box/carton capacities (e.g. converting carton units to label counts).
- **Price Fallback Logic**: Added robust fallback hierarchy for missing Rate or MRP fields.

### ðŸ”„ 7. Reprint Queue
- **Recent Job History**: A persistent local queue displaying recent print operations, allowing warehouse operators to re-trigger print runs with a single click.

### ðŸŽ¨ 8. Ergonomic Redesign
- **Widescreen 3-Panel Layout**: Left sidebar for settings/preview, center worksheet grid, and right drawer for filters and templates.
- **Always-Visible Sticky Toolbar**: Houses printing actions at the bottom of the screen with dynamic disabled-state indicators based on row selection.

### ðŸ“Š 9. Barcode Scan Telemetry Collection Framework (ACP-BARCODE-002A)
- **Immutable Raw Scan Logs**: Created `SMRITI Barcode Scan Event` DocType to record cashier scan events, protected by a fail-closed immutability rule blocking updates/deletions.
- **Seeded Governance Event Registry**: Formally registered event definitions `SCAN-EVT-001` (Success on first try), `SCAN-EVT-002` (Success after retry), and `SCAN-EVT-003` (Failure/bypassed) under `SMRITI Telemetry Event Definition`.
- **Daily Aggregation Scheduler**: Background aggregation task scheduled for 03:00 AM daily (store local time) to compute `SMRITI Barcode Telemetry Snapshot` records.
- **Pruning Retention Policy**: Configured daily cleanup job `delete_expired_scan_events` to delete raw scan logs older than 90 days.
- **Scan Reliability Score (SRS)**: Registered `SMRITI-SCAN-REL-01` in the Formula Registry to calculate real-world scan usability percentage.
- **Security & Role Verification**: Secured the `log_barcode_scan_event` endpoint to authenticated sessions matching POS User, Cashier, or System Manager roles.

---

## ðŸ†• v1.9.0-GA â€” SMRITI Party Stock Visibility (PSV) Phase 1.1 (2026-06-11)

### ðŸ“ˆ 1. Custom Shadow Ledger & Snapshot Schema
- **Immutable PSV Ledger**: Created `PSV Ledger Entry` with sequential naming `PSV-.########` utilizing Frappe's native series engine. Built reversal-based correction engine.
- **Channel Partner Profile**: Implemented `PSV Channel Partner` supporting effective dates and a child table `brands` (table type `PSV Channel Partner Brand`) for multi-brand distributor profiles.
- **Stock Aging Snapshot**: Developed `PSV Stock Aging Snapshot` to store bucketized aging data and optimized with local memory caching.
- **System Settings Configuration**: Added singleton `PSV System Settings` for weeks-of-cover thresholds and geographic scopes.

### âš¡ 2. Performance & Memory Optimization
- **Landing Cost Cache**: Replaced $O(N)$ database roundtrips with $O(V)$ request-bound memory caching on landing cost lookups.
- **Concurrency Safeguards**: Added Redis-backed distributed locks (`smriti:psv:snapshot_generation`) to prevent overlapping snapshot generation runs.
- **Index Hardening**: Added database indexes for `company`, `posting_datetime`, `channel_partner`, and `item_variant` to optimize query planners under load.

### ðŸ”„ 3. Staged Pilot Program & General Availability (GA) Promotion
- **API Fallback Layer**: Implemented seamless backward compatibility layers in `balance_engine.py` and `psv_api.py` to transparently fallback to legacy `SMRITI Party Stock Account` and `SMRITI Party Stock Ledger Entry` tables if no new records exist.
- **UAT Validation Suite**: Wrote `seed_psv_uat.py` which seeds 3,000 flat items, 110 channel partners, and 2,160 ledger entries to run a 5-phase validation cycle (all passed).
- **Pilot distributor program**: Run a successful 4-week staged pilot program involving 1 distributor and 5 dealers to track alerts, weeks of cover, and dead stock reduction.
- **Project Status**: Formally promoted to **General Availability (v1.9.0-GA)** with an overall business acceptance score of 91% and alert precision of 85.87%.

---

## ðŸ†• v1.5.0 â€” SMRITI Party Stock Visibility (PSV) Hardening & Operations (2026-06-08)

### ðŸ“ˆ 1. Scalability & Performance Hardening
- **N+1 Query Elimination:** Optimized bulk balance checks in `get_bulk_party_balances` to aggregate all stock calculations in exactly **one DB query**, eliminating N+1 query regression patterns when scaling up to 100 locations, 500 SKUs, and 10,000+ ledger entries.
- **In-Memory SQL Tracing:** Implemented a transparent, Python-level monkey-patch for query counting in unit tests, avoiding deprecated/environment-dependent database trace tools.

### ðŸ›¡ï¸ 2. Concurrency & Integrity Constraints
- **Two-Layer Concurrency Protection:** Reinforced unique constraint safety at both the application level (`frappe.db.exists`) and database level (SHA-256 `UNIQUE(unique_hash)` index constraint) to prevent duplicate transactions.
- **Cross-Driver Error Resilience:** Configured the test framework to catch database-specific unique validation exceptions across MySQLdb and PyMySQL connections natively.

### ðŸ©º 3. Daily Scheduled Operational Health Checks
- **Priority-Ordered Evaluation:** Programmed `run_psv_daily_health_check` to run daily in a priority sequence: 1. Negative Balances, 2. Pending Reconciliations, 3. Late Uploads, 4. Never Audited, 5. Automatic Alert Resolution.
- **Enterprise Alert Key Suppression:** Introduced a hashed, uppercase alert key format (`{location}|{alert_type}|{item_code}`) to prevent duplicate exceptions and log spamming, auto-updating `last_seen` timestamps on open alerts instead.
- **Dynamic Location Status Resolution:** Automatically toggles location statuses between `"Active"` and `"Pending Reconciliation"` depending on outstanding stock exception records.

### ðŸ§ª 4. Schema Integrity & Test Suite
- **Single DocType Validation:** Configured the test suite to use `frappe.db.exists` to check schema existence for Single DocTypes (such as `SMRITI PSV Settings` stored in `tabSingles`) rather than trying to look up non-existent database tables.
- **9 Integration Tests:** Added a robust test suite covering opening imports, cancellation exception records, date overlaps, physical stock audits, concurrency limits, and scheduled health checks.

---

## ðŸ†• v1.4.0 â€” Security Hardening, POS Returns & UI/UX Streamlining (2026-06-07)

### ðŸ›¡ï¸ 1. P0/P1 Critical Bug Fixes
- **XSS Elimination:** Fixed 7 `innerHTML` injection sites in `barcode.html` (item names, barcodes, error messages, QZ printer OS names, session IPs) by adding an `esc(s)` HTML-escaping utility and using DOM node `textContent` construction.
- **`reset_db()` Hardening:** Restricted reset access exclusively to `Administrator`, added `"SMRITI_CONFIRM_RESET"` confirmation token, and logged errors with partial statuses.
- **Submit Lifecycle:** Corrected 4 inventory creation functions (`create_grn`, `create_stock_transfer`, `create_stock_adjustment`, `create_stock_audit`) to use `insert() + submit()` instead of `docstatus=1 + save()`, ensuring Stock Ledger and GL entries are correctly posted.
- **Shift & Session Security:** Wrapped Shift open/close submit in rollback blocks to prevent stuck draft open entries. Removed administrative session SID exposure endpoint.

### ðŸ”„ 2. POS Return Invoice & Purchase Return (M-15)
- **POS Returns:** Added `@frappe.whitelist() def create_return_invoice` using standard ERPNext return builders with rollback protection.
- **Purchase Returns:** Added `@frappe.whitelist() def create_purchase_return` with role protection and automatic stock reversal.
- **Unit Tests:** Added automated integration tests for both sales and purchase return flows.

### ðŸŽ¨ 3. UI/UX Deep Audit & Streamlining
- **Reports Load Fix:** Fixed the indefinite loading spinner hang on `/reports` page caused by UnboundLocalError scoping imports and missing Jinja context variables (`csrf_token`, `cashier`).
- **Sidebar Naming Cleanliness:** Stripped redundant `"SMRITI "` prefixes and trailing `" Book"` suffixes dynamically on the frontend via `getCleanReportName()`, simplifying the sidebar tree.
- **Warehouse Filter Scoping:** Added dynamic warehouse dropdown filtering based on the selected company, eliminating duplicate options in multi-company environments.
- **Query Fixes:** Fixed `declared_amount` column mismatch (renamed to `closing_amount` in DB) in Cash Reconciliation, and resolved SQL `%` formatting KeyError in Z-Report.

---

## ðŸ†• v1.3.0 â€” SMRITI Reporting Framework & Accounting Analytics (2026-06-07)

### ðŸ“Š 1. Reporting Engine & Seeding
- **Metadata Reporting Engine:** Added `SMRITIReportEngine` with caching, dynamic SQL builders, role-based access checking, and TTL expiry.
- **Reports Seeding:** Programmatically seeds 20 core report templates across Sales, Inventory, Cash, and Accounting categories.
- **Accounting Extensions:** Added 6 retail accounting reports: Day Book, Cash Book, Payment Register, Receipt Register, Customer Outstanding, and Supplier Outstanding.
- **Unit Tests:** Wrote `test_reports.py` verifying all 11 reports engine test paths.

---

## ðŸ†• v1.2.8 â€” Domain Migration to erpnbook.com (2026-06-05)

### ðŸŒ 1. Domain Migration
- Replaced all instances of `smriti.io` with `erpnbook.com` in code files, sidebar scripts, configuration files, and HTML/email templates.
- Updated developer email in `pyproject.toml` to `admin@erpnbook.com`.
- Changed support desk email to `support@erpnbook.com` and help links to `support.erpnbook.com` in `hooks.py`.
- Updated placeholder cashiers and developer scripts to use the `erpnbook.com` domain.

### ðŸ—‘ï¸ 2. Duplicate Script Cleanup
- Deleted duplicate `verify_security.py` from the root of `apps/smriti_retail_os`, keeping only the updated script at `/scripts/verify_security.py`.

---

## ðŸ†• v1.2.7 â€” Setup Wizard Whitelist, Warehouse Bootstrapping & Privilege Escalation (2026-06-05)

### ðŸ§™â€â™‚ï¸ 1. Setup Wizard Whitelist (`setup_wizard_api.py`)
- Added `allow_guest=True` whitelist flag to `get_setup_wizard_initial_data` and `run_setup_wizard` API endpoints to support first-time guest deployments without raising whitelisting errors.

### ðŸ›¡ï¸ 2. Privilege Escalation & Warehouse Bootstrapping (`setup_wizard_api.py`)
- Added code to programmatically escalate the session user to `"Administrator"` via `frappe.set_user("Administrator")` during setup wizard execution, bypassing `PermissionError` caused by third-party hooks (such as `india_compliance` company overrides) executing under the context of `Guest` user session.
- Implemented defensive bootstrapping logic to check for and create standard ERPNext Warehouse Types (`Transit`, `Standard`, `Subcontracted`) before company creation, resolving the fatal `Could not find Warehouse Type: Transit` validation crash.

### ðŸ§¹ 3. Audit Relocation & Code Review Fixes (`www/reports.py`, `cleanup_test_data.py`)
- Relocated developer audit scripts (`verify_deep_audit.py`, `verify_pos_features.py`, `verify_security.py`) to a new `/scripts/` folder outside the production app package.
- Wrapped the bare `frappe.throw()` at `www/reports.py:28` with standard `_()` translation macros.
- Fixed the misleading `@description` header inside `cleanup_test_data.py` to match its exact role.

---

## ðŸ†• v1.2.6 â€” Deep Review & Architecture Hardening (2026-06-05)

### ðŸ” 1. Security & Randomization (`security_api.py`)
- Replaced hardcoded default passwords with random, cryptographically secure password generation (`secrets.token_urlsafe(16)`) per user.

### ðŸ“ˆ 2. N+1 Performance Optimization (`item_master_api.py`)
- Implemented `_build_import_lookup_cache()` collapsing 600+ database queries down to 5 bulk queries per 100-row import.

### ðŸ“Š 3. Report Aggregation (`reports_api.py`)
- Refactored in-memory Python invoice loops into standard SQL aggregations (`SUM()`, `COUNT()`, `GROUP BY`) for massive database query efficiency.

### âš–ï¸ 4. Invariants and GST Jurisdiction Safeguards (`transaction_kernel.py`, `hooks_logic.py`)
- Removed the silent `"Karnataka"` fallback in `hooks_logic.py`, raising an warning log to prevent incorrect CGST/SGST splits.
- Eliminated generic ghost item creation (`_SMRITI_GENERIC_ITEM_`) in `transaction_kernel.py`, instead enforcing clean item master validation constraints.

### ðŸ› 5. Setup Wizard "Company Link" fixes (`setup_wizard_api.py`, `company_api.py`)
- Stripped payment accounts of non-existent companies before saving.
- Injected `flags.ignore_links = True` on setup wizard payments and company settings insert hooks to resolve `Could not find Row #N: Company: <name>` crashes.

---

## ðŸ†• v1.2.1 â€” Warehouse Hardening & Custom Warehouse Override (2026-06-04)

### ðŸ¢ 1. Company-matching Default Warehouse (`purchase_api.py`, `inventory_api.py`)
- Added `_get_default_warehouse(company)` helper to resolve warehouses with target company filters.
- Prevents database mismatch issues (e.g., `Warehouse Stores - TCL does not belong to company _Test Company`).
- Automatically queries first by name `"Stores"` (non-group) belonging to the target company, then falls back to any non-group warehouse for the company, and finally any warehouse for the company.

### ðŸŽ›ï¸ 2. Custom Warehouse Selection on Creation (`purchase_api.py`, `inventory_api.py`)
- Added optional `warehouse` parameter to whitelisted API endpoints: `create_purchase_order`, `create_purchase_receipt`, and `create_grn`.
- Allows custom warehouse overrides to be passed directly from the frontend or creation payload.

### ðŸ§ª 3. Expanded Test Suite
- Added new test cases verifying custom warehouse overrides in `test_purchase_api.py`.
- Verified all **87 tests** pass cleanly.

---

## ðŸ†• v1.2.0 â€” Advanced PWA & Supplier Hardening (2026-06-04)

### ðŸ“² 1. Advanced PWA â€” All 4 Phases (`sw.js`, `smriti_pwa.js`, `smriti_offline_store.js`)

**Phase 1 â€” Foundation**
- Updated `manifest.json`: Added app shortcuts (POS Billing, Item Master, B2B Invoice, Purchase Manager), PNG icon references, orientation `any`, categories
- Generated 192Ã—192 and 512Ã—512 PNG icons deployed to `public/images/`
- Service Worker exposed at root `/sw.js` via `www/sw.py` + `website_route_rules` â€” gives full `scope: '/'` control

**Phase 2 â€” Smart Multi-Strategy Caching** (`sw.js` v2.0)
- `Cache First` â†’ `/assets/`, `/files/`, `/favicon` (static resources, instant serve)
- `Network First` â†’ `/api/`, `/method/` (live data; falls back to cached JSON offline)
- `Stale While Revalidate` â†’ all 15 SMRITI pages (instant load + background refresh)
- Auto-purges stale cache versions on `activate`; new SW skips waiting immediately

**Phase 3 â€” Offline IndexedDB Store** (`smriti_offline_store.js`)
- `SmritiOfflineStore`: Full IndexedDB abstraction (`SmritiRetailOS` DB, v1 schema)
- `pending_invoices`: save/count/delete/incrementRetry â€” offline POS bill queue
- `items_cache`: bulk load + substring search (item_code + item_name) â€” offline barcode lookup
- `customers_cache`: bulk load + search (name + mobile_no)
- `sync_log`: timestamped audit trail of all sync events
- Background Sync auto-submits queued invoices via `sync-pending-invoices` tag when back online

**Phase 4 â€” Push Notifications** (`sw.js`)
- Handles `push` events: shows branded notifications with icon, badge, vibrate
- `notificationclick`: focuses existing window or opens deep-link URL

**PWA Controller** (`smriti_pwa.js`)
- Registers SW, detects updates â†’ shows animated **"New Version Available"** banner
- Captures `beforeinstallprompt` â†’ shows **"ðŸ“² Install SMRITI App"** button
- Online/offline detection â†’ shows toast (Frappe or vanilla fallback)
- Triggers `sync-pending-invoices` background sync immediately on reconnection
- Auto-injects `<link rel="manifest">` into `<head>` on all pages

**Offline Fallback Page** (`offline.html`, `offline.py`)
- Glassmorphic dark design with animated blobs
- Live IndexedDB stats: pending invoice count + cached item count
- Offline capabilities grid, retry button, auto-reload on `online` event

### ðŸ”— 2. Supplier Lookup Filter Fix (`purchase_order.js`)
- Removed `supplier_type: "Company"` filter from Purchase Order/Receipt supplier query
- All active suppliers (Individual + Company) now appear in PO/GRN supplier fields
- Individual suppliers created via SMRITI dashboard are now correctly visible

### âœ… 3. Supplier Vendor Code Validation (`item_master_api.py`, `setup.py`)
- Added `custom_vendor_code` unique field on Supplier DocType
- `_validate_vendor_code()` helper rejects unregistered vendor codes in all 3 import paths
- Supplier linkage now resolves exclusively via `custom_vendor_code` lookup

---

## ðŸ†• v1.1.0 â€” Barcode & B2B Invoice Hardening (2026-06-03)

### ðŸ”– 1. Barcode Hardening â€” Option B Architecture (`barcode_api.py`, `item_master_api.py`)
- Added `custom_is_primary` (Check) field to `Item Barcode` child table
- Enforced exactly **one primary barcode per item** across all import paths
- System-wide EAN-13 collision protection (checks `Item Barcode` table + `Item.item_code` namespace)
- Secondary barcodes preserved across style creation, variant updates, pivot & standard imports
- Barcode print fallback: `Primary â†’ First â†’ Item Code`
- Missing barcode detection report for active sellable variants (excludes templates)

### ðŸ“· 2. Sizewise Invoice â€” Barcode Scan Bar (`sizewise_invoice_api.py`, `sizewise_invoice.html`)
- Hardened `resolve_barcode()` API with user read permission checks (`frappe.has_permission`)
- Implemented parent template field fallbacks (inherits `custom_mrp`, `custom_gst_percentage`, `gst_hsn_code`, `custom_sub_category` from template if blank on variant)
- Dedicated scan bar UI with pulsing scanner icon, inline status label, USB/BT hint
- Finds or auto-creates Article+Color row in the pivot grid; increments size qty +1 per scan
- Auto-adds unknown size columns dynamically on scan
- Green/red CSS flash feedback on the input and size cell
- **Global HID keyboard-wedge listener** â€” works even when scanner fires without input focus

### ðŸ› ï¸ 3. Item Master Excel Import Fixes (`item_master_api.py`, `item_master.html`)
- **Bug 1** â€” Re-import false rejection: allowed re-import if barcode belongs to same variant
- **Bug 2** â€” Excel blank cell NaN guard: `"nan"/"none"/"null"` normalized to empty string
- **Bug 3** â€” `custom_is_primary` None-safety: `int(b.get(...) or 0)` coercion
- Fixes applied to **both** `validate_import_rows` and `import_item_master`
- Added `SIS` to Purchase Class dropdown

### ðŸ› ï¸ 4. Data Cleaning & HSN Fallback Hardening (`item_master_api.py`)
- Added a robust `_clean_str()` helper that sanitizes all pasted cells, automatically removing wrapping quotes, Excel stray quotes (`"`), and converting various Excel null representations (`nan`, `none`, `null`) into clean empty strings `""`
- Extracted digits only using regex to strip HSN format characters, dashes, dots, or placeholder text
- Added auto-formatting and padding (e.g. `6402` &rarr; `640200`) to comply with India Compliance's 6/8 digit validations
- Added smart fallback default HSN (`641590`) for blank or invalid HSN columns
- Automatically registers resolved HSN codes in the database, avoiding foreign key validation crashes on insertion

---

## ðŸ“¦ v1.0.0 â€” Production Release

### 1. ðŸ—ï¸ Robust Container Bootstrap (`pwd.yml`)
- Fixed missing volume mounts in `pwd.yml` for custom apps (`smriti_retail_os` and `india_compliance`).
- Backend processes (`configurator`, `queue-long`, `queue-short`, and `scheduler`) compile dependencies correctly.
- Completely prevents container startup crashes and ensures seamless site creation.

### 2. âš¡ Physical Asset Pipeline (No Symlinks)
- Implemented a custom physical asset hard-sync utility (`sync_assets.py`) that unlinks complex app symlinks inside the bench `/assets/` directory.
- Directly hard-copies compiled esbuild bundles (like `desk.bundle.css`, `erpnext.bundle.css`) straight to the shared Nginx assets volume.
- Resolves all browser console MIME-type stylesheet failures (`text/html` strictly checked blocking).

### 3. ðŸ—„ï¸ Automated Database Provisioning
- Automatically creates and binds all missing retail custom fields (MRP, stock HTML summaries, birthday, anniversary, credit terms) inside MariaDB via `setup.py`.
- Realigned reporting and shift APIs to target official ERPNext v16 tables (`Sales Invoice Payment` and `billing_address_gstin`).

### 4. ðŸŽ¨ SMRITI Pure Retail Mode (Sales Invoice Makeover)
- Simplifies complex invoice grids for store cashiers to show only `Item Code`, `Item Name`, `Qty`, `Rate`, and `Amount`.
- Dynamic glassmorphism dashboard overlay featuring backdrop-blur controls and elegant state slates (Draft, Submitted, Cancelled).
- Bypasses System Managers automatically to maintain standard ERPNext desk workflows for administrators.

### 5. ðŸ§ª Hardened 81-Test Suite (100% Passing)
- Hardened test setups to isolate company boundaries (`_Test Company`), active fiscal years, and clean DB child table structures.
- **81/81 tests completed with OK status**.

### 6. ðŸ›¡ï¸ System Audit & Hardening
- Removed critical security vulnerability in `get_admin_session_for_pdf` by removing guest access and enforcing a System Manager role check.
- Fixed malformed translation file `en.csv` that generated 352+ error log entries on every page load.
- Re-engineered `check.ps1` to automatically detect running container names from Docker Compose project name, ensuring accurate health reporting.

---

## ðŸ› ï¸ Update & Install Instructions

### 1. Updating your existing Docker Compose stack:
```bash
# Pull the latest stable release
cd apps/smriti_retail_os
git pull origin main
cd ../..

# Run migrations & rebuild bundles inside container
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
```

### 2. Fresh Installation:
```bash
git clone https://github.com/erpnbook/smriti-docker.git
cd smriti-docker
mkdir -p apps
git clone --branch v1.2.2 https://github.com/erpnbook/smriti.git apps/smriti_retail_os
git clone --branch version-16 https://github.com/resilient-tech/india-compliance.git apps/india_compliance
docker compose -f pwd.yml up -d
```
*(Wait 2 minutes for creation, then run setup hooks and asset sync).*

---

## ðŸ‘¥ Contributors & Base
- **Frameworks**: Frappe Framework v16 & ERPNext v16
- **Integrations**: India Compliance v16


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL â€“ AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> â€” Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
