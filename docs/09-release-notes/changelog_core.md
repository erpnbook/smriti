---
Document ID: "REL-009"
Title: "Changelog — SMRITI Retail OS"
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

# Changelog — SMRITI Retail OS

All notable changes to **SMRITI Retail OS** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Redesign the core desktop client utilizing Frappe v17.
- Implement AI-driven stock-out prediction engines.
- Add multi-currency cashier ledger balancing.

## [2.4.2] — 2026-06-30

### Changed
- **Navigation: Dedicated Barcode Studio Group**: Consolidated all barcode-related sidebar items under a new `Barcode Studio` menu group positioned between `Inventory` and `Finance`.
  - `Barcode Center` (renamed to **Label Studio**, route `/barcode`) — moved from `Inventory`
  - `Print Templates` (route `/print-templates`) — moved from `Inventory`
  - `Sizewise Item CRUD` (route `/sizewise_item`) — moved from `Masters`
  - `Sizewise Invoice` (route `/sizewise_invoice`) — moved from `Sales`
- Both `smriti_nav_config.js` (client) and `navigation_service.py` (`CANONICAL_NAV`) updated in sync.
- Legacy route `/barcode-center` preserved in `hooks.py` `website_route_rules` for backward-compatible bookmark redirects.

---

## [2.4.1] — 2026-06-30

### Fixed
- **Style/Article No Fallback Resolution Chain**: Fixed style token printing on variant items by replacing single-step SKU hyphen split with 4-step priority resolution (`variant_of` $\rightarrow$ `custom_style_code` $\rightarrow$ `style_no` $\rightarrow$ SKU hyphen split fallback).
- **ZPL/TSPL Print Tokens**: Added explicit `{style_code}` (raw field value mapping) and `{variant_template}` (direct `variant_of` mapping) print tokens to print data payloads.
- **QZ Tray WebSocket Dict Payload Crash**: Resolved USB printing WebSocket crash `TypeError: data[i].data.search is not a function` by extracting raw PRN ZPL/TSPL string from the backend dictionary response (`prnContent.prn || prnContent`) in download, LAN, and USB print flows. Wired up warning toast notifications for fallback template prints.

---

## [2.4.0] — 2026-06-21

### Added
- **Barcode Studio V2.4a Layout & Operations Upgrade:** Implemented high-performance warehouse barcode printing features.
- **Article Range Loader**: Input From/To range fields (e.g. `BBM-0001` to `BBM-0100`) to sequentially generate style IDs and load items into the print worksheet.
- **Variant Expansion**: Automatic size/color variant expansion for fashion retail styles on submission/fetch.
- **Interactive Worksheet Grid**: Standardized the print canvas into a 9-column grid (`Select | Article | Item Name | Brand | Color | Size | Barcode | MRP | Qty | Labels`).
- **Dynamic Tag Mapping Preview**: Left sidebar panel resolving template tags (e.g. `{barcode}`, `{brand}`, `{mrp}`) to actual database values in real-time.
- **Transaction Expansion Modal**: Selection modal panel when fetching PR/PO/GRN logs with selection filters ("Select All", "Only Missing Labels", "Only New SKUs").
- **Box & Carton Mode**: Packing multipliers logic converting carton/box units to label counts automatically.
- **Rate/MRP Fallback Rules**: Priority resolution hierarchy: Variant Price $\rightarrow$ Price List $\rightarrow$ Parent Template.
- **Reprint Queue**: Local cache of recent print runs for instant re-execution.
- **Ergonomic Widescreen 3-Panel Layout**: Separated settings (left), worksheet grid (center), and ranges (right) with a bottom sticky action bar.
- **Barcode Scan Telemetry Collection Framework (ACP-BARCODE-002A):** Introduced a clean, audit-friendly event collection and aggregation framework.
  - **Immutable Raw Scan Logs**: Created `SMRITI Barcode Scan Event` DocType to record cashier scan events, protected by a fail-closed immutability rule blocking updates/deletions.
  - **Seeded Governance Event Registry**: Formally registered event definitions `SCAN-EVT-001` (Success on first try), `SCAN-EVT-002` (Success after retry), and `SCAN-EVT-003` (Failure/bypassed) under `SMRITI Telemetry Event Definition`.
  - **Daily Aggregation Scheduler**: Background aggregation task scheduled for 03:00 AM daily (store local time) to compute `SMRITI Barcode Telemetry Snapshot` records.
  - **Pruning Retention Policy**: Configured daily cleanup job `delete_expired_scan_events` to delete raw scan logs older than 90 days.
  - **Scan Reliability Score (SRS)**: Registered `SMRITI-SCAN-REL-01` in the Formula Registry to calculate real-world scan usability percentage.
  - **Security & Role Verification**: Secured the `log_barcode_scan_event` endpoint to authenticated sessions matching POS User, Cashier, or System Manager roles.

---

## [2.2.0] — 2026-06-19

### Added
- **Knowledge Governance Framework (KGF) (v2.2.0):** Implemented the Formula Registry (`SMRITI Formula Definition`), Universal Explain Modal (`/smriti-explain` API with Redis caching and access-auditing), and Business Dictionary (`SMRITI Business Term`) to enforce DOC-01/02/03/04 and Rule 12.
- **2-Phase Glossary Seeding:** Seeding script `seed_default_terms.py` to register 20 core retail terms with fully resolved relationship links.
- **Universal Explain Modal integration:** Allows users to view mathematical worked examples and recommended actions for all KPIs and navigate directly to the Business Dictionary drawer.
- **Author Attribution Credits:** Incorporated chief architect profile attribution for Jawahar R. Mallah across all manuals, workbook training guides, and system templates (Rule 12).

## [2.1.0] — 2026-06-18

### Added
- **PWA Service Worker Interception:** Serving `/sw.js` directly via boot hook intercepts with strict `application/javascript` content-type headers.
- **IndexedDB POS Checkout Queue:** Enabled cashiers to queue transaction records offline inside IndexedDB when the network is down.
- **Auto-Sync & Network Status Indicators:** Implemented `#network-status` visual badge and FIFO service worker background sync.

## [2.0.1] — 2026-06-16

### Added
- **CGE Generic CRUD Console:** A dynamic web console providing generic explorers for all 12 CGE modules.

## [2.0.0] — 2026-06-15

### Added
- **Customer Growth Engine V2:** Rolled out Campaign, Coupon Rules, Loyalty Rules, Membership Tiers, and Cashback Wallets with SQL constraints and soft-delete protections.

---

## [1.9.0-GA] — 2026-06-11

### Added
- **PSV Custom Shadow Ledger:** Added `PSV Channel Partner`, `PSV Channel Partner Brand`, `PSV Ledger Entry`, `PSV System Settings`, and `PSV Stock Aging Snapshot` DocTypes.
- **Landing Cost Lookup Cache:** Request-bound local memory caching (`frappe.local.landing_cost_cache`) reducing bulk query complexity from $O(N)$ to $O(V)$ variant lookups.
- **Incremental Aging Snapshotting:** Caching with Redis-backed distributed locks (`smriti:psv:snapshot_generation`) to prevent overlapping executions.
- **Geographic Redistribution:** Territory-aware suggestions for over-stocked and under-stocked partners.
- **Backward Compatibility Matrix:** Transparent fallback layers to query legacy data structures when new shadow tables are empty.
- **Dedicated PSV Dashboard:** Glassmorphism UI page at `/psv-dashboard` styled with corporate Navy/Blue colors.
- **UAT & Validation Suite:** Created `seed_psv_uat.py` validating migration, compatibility, footwear size-curve analytics, and database index checks.

### Changed
- **Test Suite Expansion:** Expanded the automated test suite to **187 passing unit tests**.
- **GA Release Promotion:** Formally promoted Phase 1.1 to **General Availability (GA)** status after pilot validation (Distributor + 5 Dealers, 4 Weeks) met all technical, operational, and business acceptance criteria with 91% satisfaction and 85.87% alert precision.

---

## [1.4.0] — 2026-06-07

### Added
- **POS Returns (M-15):** Added `@frappe.whitelist() def create_return_invoice` API to construct and submit POS Sales/POS Invoice returns.
- **Purchase Returns:** Added `@frappe.whitelist() def create_purchase_return` API with role validation (`check_store_manager_role`) to submit Debit Notes/Purchase Receipt returns.
- **UI/UX Streamlining:** Added `getCleanReportName()` to dynamically filter and remove redundant `"SMRITI "` prefixes and trailing `" Book"` suffixes in report names.
- **Dynamic Warehouse Filter:** Added company-based filtering for the Warehouse dropdown to prevent duplicate options in multi-company environments.

### Fixed
- **XSS Vulnerabilities (C-09/C-10/H-13):** Replaced `innerHTML` with `textContent` across `barcode.html` print worksheet, toast error messages, and printer configurations.
- **Inventory Submission (C-01):** Replaced `docstatus=1 + save()` with correct `insert() + submit()` lifecycle across `create_grn`, `create_stock_transfer`, `create_stock_adjustment`, and `create_stock_audit` to ensure Stock Ledger and GL entries are posted.
- **Database Safety (C-11/C-12/H-09/H-15):** Added confirmation tokens to `reset_db()`, removed premature database commits from variant resolution, removed event hook commits, and wrapped opening/closing shifts in rollback transaction blocks.
- **Report Database Errors:** Resolved `declared_amount` database column mismatch in Cash Reconciliation and SQL parameter Keynes error in Cash Z-Report.

### Changed
- **Test Suite Expansion:** Grown the automated test suite to **113 passing tests** (including return transactions and database integration assertions).

---

## [1.3.0] — 2026-06-07

### Added
- **SMRITI Reporting Engine:** Implemented `SMRITIReportEngine` in `reports_api.py` supporting metadata-driven SQL execution, caching, and role validation.
- **Retail Reports Seeding:** Seeds 20 standard reports covering Sales, Inventory, Cash, and 6 newly added Accounting reports (Day Book, Cash Book, Payment Register, Receipt Register, Customer Outstanding, Supplier Outstanding).
- **Reports Test Suite:** Added `test_reports.py` verifying template seeding and execution, expanding the test suite to **105 passing tests**.

---

## [1.2.10] — 2026-06-06

### Added
- **Style/Article Search & Autocomplete**: Added a debounced (300ms) fuzzy search suggestion dropdown on the Style / Article input field (`flt-style`) supporting keyboard navigation (`Arrow Up`, `Arrow Down`, `Enter`, `Escape`) and auto-loading to the print queue worksheet (activated via configuration).
- **Test Suite Expansion**: Added test coverage for barcode and variant autocomplete queries, growing the automated test suite to **94 passing tests**.

### Fixed
- **Test Database Pollution**: Resolved MariaDB test database cleanup issues and prevented child table pollution in subsequent unit test runs.

---

## [1.2.9] — 2026-06-05

### Added
- **SMRITI Label Studio v2.1 Release Candidate**: Integrated local printing WebSocket handlers for QZ Tray, custom signature validation settings, printer latency socket benchmarks, and visual print safety confirmation dialogs.
- **Label Studio Print Run Analytics**: Built a database dashboard counting printed labels, templates usage stats, and printer diagnostics.
- **LAN Printing raw sockets**: Added TCP socket connections to network label printers over port `9100`.

---

## [1.2.8] — 2026-06-05

### Changed
- **Domain Migration to erpnbook.com**: Migrated all system references, whitelabel headers, support links, email templates, and developer domains from `smriti.io` to `erpnbook.com`.

### Fixed
- **Duplicate Scripts Cleanup**: Cleaned up duplicate security audit scripts in the app package directory.

---

## [1.2.7] — 2026-06-05

### Added
- **Warehouse Type Bootstrapping**: Added defensive bootstrapping logic in `setup_wizard_api.py` to create standard ERPNext Warehouse Types (`Transit`, `Standard`, `Subcontracted`) before company inserts, preventing the `Could not find Warehouse Type: Transit` error.

### Fixed
- **Setup Wizard Guest Whitelist**: Whitelisted `get_setup_wizard_initial_data` and `run_setup_wizard` API endpoints to support guest onboarding flows.
- **Privilege Escalation during setup**: Escales guest session context to `Administrator` programmatically to bypass link validations during new company creations.

---

## [1.2.6] — 2026-06-05

### Changed
- **N+1 Query Optimizations**: Collapsed database loops inside `item_master_api.py` using lookup caches, reducing queries by 90% on bulk variant imports.
- **SQL Aggregations**: Refactored in-memory Python calculations in `reports_api.py` into SQL queries (`SUM`, `COUNT`, `GROUP BY`).

### Security
- **Dynamic Password Generation**: Replaced hardcoded default installer passwords with randomized secure hashes (`secrets.token_urlsafe(16)`) per user.

---

## [1.2.1] — 2026-06-04

### Added
- **Custom Warehouse Selectors**: Allowed passing optional `warehouse` parameter overrides to Purchase Order, Purchase Receipt, and GRN creation endpoints.
- **Automated Tests**: Added new test cases verifying warehouse overrides, expanding the test suite to **87 passing tests**.

### Fixed
- **Company Warehouse Mismatch**: Implemented the `_get_default_warehouse(company)` helper to query warehouses matching the target company context first, preventing database cross-company validation errors.

---

## [1.2.0] — 2026-06-04

### Added
- **Smart PWA Support**: Implemented Smart Multi-Strategy caching service workers, push notification bindings, and offline fallback interfaces.
- **Offline IndexedDB Store**: Created `SmritiOfflineStore` for local database saving of pending invoices, customer lookups, and offline barcode registers.

### Fixed
- **Supplier Lookup Filters**: Removed the restricted `supplier_type: "Company"` constraint from Purchase Orders, enabling cashiers to select Individual suppliers.

---

## [1.1.0] — 2026-06-03

### Added
- **Primary Barcode Architecture**: Added the `custom_is_primary` field to `Item Barcode` child table, enforcing exactly one primary barcode per item variant and enabling ZPL print fallbacks.
- **Sizewise Barcode Scanning**: Added HID keyboard-wedge scanner support on `/sizewise_invoice` with automatic column increments and green/red flash CSS feedback.

---

## [1.0.0] — 2026-06-02

### Added
- **Docker Orchestration**: Configured standard `pwd.yml` multi-container stack.
- **Asset Guard**: Created `sync_assets.py` to hard-copy compiled bundles to Nginx, resolving CSS/JS MIME-type blockages.
- **SMRITI Pure Retail Mode**: Simplified POS invoices view, filtering out complex ERP warehouse columns for standard cashiers.
- **Automated Test Suite**: Launched initial test suite with **81 passing automated tests**.

---

## Versioning & Release Strategy

SMRITI Retail OS release pipelines are separated into logical branches:

1. **`main`**: Represents the stable production release branch. All tags are generated from this branch.
2. **Maintenance Branches (`v1.2.x`)**: Used for hotfixes and patch integrations for existing installations.
3. **Development Branches (`dev`)**: Feature-specific staging environments where changes are validated before merging.

### Test Suite Growth
Quality control gates monitor automated test volumes over major milestones:
- **v1.0.0**: 81 Passing Tests (Initial release baseline)
- **v1.2.1**: 87 Passing Tests (Added custom warehouse tests)
- **v1.2.10**: 94 Passing Tests (Added search/autocomplete and clean setup assertions)
- **v1.3.0**: 105 Passing Tests (Added reports templates and execution tests)
- **v1.4.0**: 113 Passing Tests (Added POS returns and database integration assertions)

### Release Readiness Matrix
The current platform status is represented by the following readiness metrics:

| Module              | Status                      |
| ------------------- | --------------------------- |
| Setup Wizard        | ✅ Stable                    |
| Masters             | ✅ Stable                    |
| Billing Engine      | ✅ Stable                    |
| Purchase            | ✅ Stable                    |
| Inventory           | ✅ Stable                    |
| Sizewise Invoice    | ✅ Stable                    |
| Barcode Studio      | ✅ Stable                    |
| Label Studio        | ✅ Stable                    |
| Print Templates     | ✅ Stable                    |
| Analytics Dashboard | ⚠️ Requires Production Data |
| USB/QZ Printing     | ⚠️ Pilot Validation         |
| LAN Printing        | ⚠️ Pilot Validation         |
| SmartPOS Framework  | 🚧 Ongoing Expansion        |


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |
| 1.1.0 | 2026-06-30 | Jawahar R. Mallah | Added v2.4.2 entry for Barcode Studio menu consolidation; updated Release Readiness Matrix |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL