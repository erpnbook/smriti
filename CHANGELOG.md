# SMRITI Retail OS — Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Fixed

#### Architecture Compliance
- Refactored `style` attributes containing inline hex color codes in `label.html`, `smriti-po-create.html`, `smriti-po-print.html`, and `smriti-quotation.html` to CSS rules and SMRITI design tokens. Resolved 20 compliance linter warnings, allowing the static CI gate to pass successfully.

## [2.5.0] - 2026-07-08

### Added

#### Purchase Studio
- **`www/smriti-po-print.html`** (rebuild): Full replacement of the bare-bones PO print page with a SMRITI-styled view/print/PDF page modelled on `sizewise_invoice`. Includes SMRITI shell (sidebar, topbar, bg-grid, bg-glow, Inter/Outfit fonts, Material Symbols), 6 collapsible panels (PO Header, Transport/Remarks, Product Image, Sizewise Matrix Grid, Order Totals, Signatures), chrome-free `#print-layout` for `@media print`, PDF export via html2pdf.js (landscape A4), PO History drawer with search, and Load PO modal. Zero backend changes — uses existing `get_po_matrix_print_data` API.

#### Sidebar / Navigation
- **`smriti_sidebar_standalone.js`**: `coming_soon` status tier — items with `status: "coming_soon"` render with `.coming-soon` CSS class, amber `SOON` badge, tooltip with ETA date, `tabindex="-1"`, always navigate to `/smriti-coming-soon`. Pin-to-favorites and popout actions suppressed for coming-soon items.
- **`smriti_sidebar.js`**: Same `coming_soon` render logic ported (Frappe Desk variant parity). Also adds missing `badge` rendering that was absent. Coming-soon items excluded from Command Palette search results.
- **`smriti_sidebar_standalone.css` + `smriti_sidebar.css`**: `.smriti-nav-badge--soon` (amber variant), `.smriti-sidebar-item.coming-soon` (55% opacity, italic label, 50% icon opacity, default cursor, slight hover lift).

### Changed

#### Navigation — `CANONICAL_NAV` full refactor (`navigation_service.py`)
- **7 broken routes fixed** (pointed to non-existent pages → corrected or marked `coming_soon`): `/psv-channel-partner`, `/psv-aging`, `/opening-stock`, `/inventory-ops`, `/receipts`, `/advances`, `/config-portal`, `/security-workflows`
- **8 route mismatches fixed** (hyphen vs underscore — Frappe slug normalisation): `item_master`, `category_master`, `scheme_creator`, `brand_master`, `sales_orders`, `sales_return`, `delivery_challan`, `print_templates`, `release_notes`, `smriti_support`, `psv_reconciliation`, `psv_exception_analysis`
- **3 duplicates removed**: 3 shift entries → 1 "Day / Shift Register"; `credit_notes` (duplicate of `tax_invoice`); `user_manual` (duplicate of `knowledge_center`)
- **13 CGE sub-items** marked `coming_soon` (dedicated pages not yet built; routes now hash-anchor to `/smriti-cge`)

### Added to Sidebar (13 missing pages now have menu entries)
`sfm_master`, `sfc_catalog`, `quotation`, `grn_receipts` (standalone), `purchase_invoice_pg`, `purchase_receipt_pg`, `purchase_returns`, `tally`, `safe_cash`, `platform_admin`, `nav_health`, `field_explorer`, `go_live`, `setup_wizard`

---

## [Governance] — 2026-07-08

### Governance — Architecture Constitution Integration

- **`SMRITI_PRODUCT_CONSTITUTION.md` v1.1.0:** Added Candidate Articles `SPC-C-012` (SMRITI Component Library Standard) and `SPC-C-013` (SMRITI Document Format Standard). Amendment log updated.
- **`SMRITI_EXPERIENCE_CONSTITUTION.md`:** Added `Document Experience Constitution` section — Rules DOC-E1 through DOC-E5 covering the five-format document standard (Screen, Print, PDF, Email, Mobile), document branding, business language, chrome-free print views, and Print Studio registration.
- **`SMRITI_UI_ARCHITECTURE.md` (NEW — DRAFT):** Companion document filling the gap referenced in `SMRITI_EXPERIENCE_CONSTITUTION.md` §Purpose. Contains: Component Inventory, Document Format Matrix (completion tracker for 13 documents), current `www/` + `*_studio/` layout, module UI ownership table, naming conventions, and Future-State Layout (explicitly labelled not-current; requires ADR before implementation).

---

## [2.4.0] — 2026-07-08

### Added — Label Studio Phase A (Retail Chain Store complete)

#### Backend
- **`label_api.get_item_for_label(item_code)`**: Fetches `item_name`, `barcode` (from `Item Barcode` child table), `mrp` (from `Item Price` — Standard Selling), `hsn_code`, `brand` from ERPNext `Item`. Human-readable error when Item Code not found.
- **`label_api.get_printers_list()`**: Returns registered `SMRITI Printer` records; graceful fallback entry when doctype not configured.
- **`render_engine.ZPLRenderer`**: `QRCode` → `^BQN,2,3` command; `Line` → `^GB` graphic box; `visible=false` elements skipped; `font_size` used in text command (`^A0N`).
- **`render_engine.TSPLRenderer`**: `QRCode` → `QRCODE … H,3,M,0,M2`; `Line` → `BAR`; `visible=false` skipped.

#### JS
- **`label_core.js`**: Canvas starts **empty** (no placeholder elements). `LabelStudioState.nextId` counter for unique IDs. `LabelElementFactory.create(type, overrides)` — retail defaults per type (Text 60×8 mm, Barcode 80×18 mm, QRCode 20×20 mm, Line 90×1 mm). Event bus `off()` method added.
- **`label_designer.js`**: Full rewrite.
  - `element:add {type}` → creates via factory, pushes to canvas, selects.
  - `element:delete` → removes active element.
  - `canvas:resize {width_mm, height_mm}` → updates canvas dimensions, redraws.
  - `element:load_item` → if canvas empty scaffolds standard retail layout (name + brand + MRP texts + barcode); otherwise updates source-tagged elements. Emits `item:loaded`.
  - `QRCode` element renders as a QR-pattern grid placeholder on canvas.
  - `Line` element renders as horizontal rule.
  - `Text` element uses `el.font_size` for proportional text scaling.
  - Selection outline changed to purple dashed border (`#7c3aed`) — matches SMRITI accent.

#### UI (`label.html`) — full rebuild
- **Element palette toolbar**: `+ Text` / `+ Barcode` / `+ QR Code` / `+ Line` / `Delete` buttons.
- **Label size presets**: 100×50 mm (Standard), 58×40 mm, 40×30 mm, 75×50 mm, 100×30 mm (Strip), Custom (prompt).
- **SKU / Item Lookup card**: Item Code input (Enter or Load button) → `get_item_for_label` → shows Name / Barcode / MRP / HSN / Brand; auto-scaffolds or updates label on load.
- **Inspector**: content, x, y, width, height, rotation, font size, locked, visible.
- **Print panel** (right dock): printer selector (API-loaded), ZPL/TSPL format toggle, copies input, Print button, Export button (downloads JSON preview).
- **Element list panel**: live list of all elements; click-to-select.
- **Status bar** + **toast notifications** (success / error / info).
- **Keyboard shortcuts**: `Ctrl+Z` undo, `Ctrl+Y` redo, `Delete` / `Backspace` removes selected element.
- **Canvas info bar**: shows current dimensions + element count.

---

## [2.3.1] — 2026-07-08


### Fixed

#### Purchase Studio — Size Preset UI (Issues consumer of v2.2.1 API change)
- **`smriti-po-create.html`** `loadSizePresets()`: Unpacks `data.message.presets` from the v2.2.1 `{presets, using_defaults}` return shape. Old plain-dict fallback retained for zero-downtime compatibility. When `using_defaults=true` an inline info banner ("Using default size groups — Configure size groups") is injected above the preset selector.
- **`smriti-quotation.html`** `loadSizePresets()`: Same fix applied to the Quotation matrix-grid path (`sales_studio.api.sales_api.get_size_presets`).
- Both banners are idempotent — stale copies removed before re-injection.

#### Purchase Studio — TDS Category Sync (Issue #4)
- **`SMRITI Supplier` doctype** (`smriti_supplier.json`): Added `tds_category` Link field (→ `Tax Withholding Category`) inserted after `disabled`. No existing field changed.
- **`erp_adapter.get_or_create_bridge_supplier`**: Update path and create path both now sync `tds_category → tax_withholding_category` on the ERPNext Supplier. Guard: `frappe.db.exists("Tax Withholding Category", …)` prevents errors on installations without india_compliance.

#### Purchase Studio — Approval Threshold Basis (Issue #5)
- **`purchase_settings_service.py`**: Added `approval_threshold_inclusive_of_tax` boolean to all three settings return paths (SDK provider, DocType fallback, safe defaults). Default `False` = compare against pre-GST `net_total`.
- **`check_approval_required(grand_total, net_total=None)`**: New optional `net_total` parameter. When `approval_threshold_inclusive_of_tax=True` compares `grand_total` (GST-inclusive); when `False` compares `net_total` if supplied, else falls back to `grand_total`. SDK Policy Engine path also reads the new flag.
- **`purchase_workflow_service.submit()`**: Replaced inline `threshold > grand_total` comparison with delegating call to `check_approval_required(grand_total, net_total)` so the setting is always respected.

---

## [2.3.0] — 2026-07-08


### Added
- **SMRITI Retail OS Layout Engine (SRLE) v1.0 — all 4 phases** delivered in a single release.

#### Phase 1 — Core Module and Public API
- `layout_engine/` Python package with `layout_preferences.py` (validation) and `layout_service.py` (`@frappe.whitelist` get/save endpoints with graceful fallback).
- `window.SRLE` public API: `setLayout`, `getLayout`, `toggleSidebar`, `setCollapsed`, `savePreferences`, `restorePreferences`, `registerWorkspace`, `refreshLayout`, `init`, `getVersion`.
- `SRLE_Store` (`layout_store.js`): localStorage store with legacy `smriti-sidebar-*` bridge + Frappe server sync.
- `SRLE_DockManager` (`dock_manager.js`): dock CSS classes + `--srle-workspace-offset-*` custom property updates.
- `SRLE_Responsive` (`responsive_manager.js`): ResizeObserver breakpoints — bottom dock on mobile, left/bottom on tablet, user preference on desktop.
- CSS: `layout_tokens.css` (`--srle-*` namespace tokens) + `layout.css` (`.srle-workspace` opt-in, dock-specific workspace rules).

#### Phase 2 — Resizable Sidebar
- `smriti_sidebar.js`: `.srle-resize-handle` element injected after sidebar renders; mousedown/move/up drag logic sets `--srle-sidebar-width` + `--sidebar-width` CSS custom properties live; width persisted to `SRLE_Store` and `localStorage`; restores saved width on re-render; disabled in top/bottom dock modes.
- `smriti_sidebar.css`: resize handle positioning (right edge left-dock / left edge right-dock), hover accent highlight, hidden in top/bottom, `body.srle-resizing` prevents text selection during drag.

#### Phase 3 — Top Dock "More ▾" Overflow Menu
- `SRLE_NavRenderer` (`navigation_renderer.js`): ResizeObserver + MutationObserver watches sidebar content and dock class changes; nav items that overflow top-bar width collected into a "More ▾" dropdown (fixed-position, `@keyframes srle-dropdown-in` animation); keyboard: Escape closes and returns focus; fully ARIA-annotated (`aria-haspopup`, `aria-expanded`, `role="menu"`, `role="menuitem"`); no-op in non-top-dock modes.
- `layout.css`: `.srle-more-btn`, `.srle-more-dropdown` styles with open/close animation.

#### Phase 4 — ARIA and Keyboard Navigation
- `smriti_sidebar.js`: sidebar root gets `role="navigation"` + `aria-label` on every render; Arrow Up/Down moves focus between visible items and group headers; Home/End jump to first/last; Enter/Space activates group header toggle.
- `layout.css`: `aria-expanded` chevron rotation transition; `.srle-skip-link` hidden-until-focused helper; focus-visible outlines for all interactive sidebar elements; high-contrast mode overrides.

#### Custom Field and Migration
- `fixtures/custom_fields_layout_engine.json`: `smriti_layout_prefs` Small Text hidden field on Frappe User — enables cross-device SRLE preference persistence.
- `patches/install_srle_layout_prefs_field.py`: idempotent migration patch creates the field on `bench migrate`.
- `patches.txt`: patch registered for automatic execution.
- `hooks.py` fixtures list: Custom Field registered for `bench import-fixtures`.

### Changed
- **`hooks.py`** `app_include_css`: `layout_tokens.css`, `layout.css` added after `smriti_sidebar.css`.
- **`hooks.py`** `app_include_js`: `layout_store.js` → `dock_manager.js` → `responsive_manager.js` → `layout_manager.js` → `navigation_renderer.js` added after `smriti_sidebar.js`.
- **`public/css/ui/layout.css`**: Added `.srle-workspace` opt-in class (additive, no existing pages affected).
- **`smriti_sidebar.js`**: ARIA landmark attributes + Arrow key handler + resize handle injection (all additive — no existing behaviour removed).
- **`smriti_sidebar.css`**: Resize handle styles appended (additive).

---

## [2.2.1] — 2026-07-08


### Changed
- **Purchase Studio — Supplier Performance** (`get_supplier_performance`): Removed raw SQL on `tabSMRITI Purchase Order`. Now delegates to `erp_adapter.get_supplier_performance_data()` which reads ERPNext PO + PI KPIs with real overdue payable amounts per supplier.
- **Purchase Studio — Size Presets** (`get_size_presets`): Added `Generic (Single Size)` fallback preset so non-apparel stores can use matrix PO entry without configuring size groups. Return shape changed to `{"presets": {...}, "using_defaults": bool}` — UI reading this endpoint must read `result["presets"]`.

---

## [2.2.0] — 2026-07-08


### Added
- **Sales Studio Phase 1**: New `sales_studio` module with full service-repository-adapter layering for Quotation and Sales Order management (15 new files across adapter, API, repository, and service layers).
- **Quotation Manager UI**: New `www/smriti-quotation.html` page with dual-mode entry (manual line items + matrix grid), converting Quotations to Sales Orders in one click.
- **Sales Orders UI**: Rewired `www/sales_orders.html` to route all API calls through the new `sales_studio.api.sales_api` layer.
- **Security**: Registered `smriti_quotation` page in `security_api.py` with manager-role access policy.
- **Tests**: Added `tests/test_sales_studio.py` with 19 tests across 7 test classes.
- **Docs**: Added `docs/walkthrough/sales/Sales_Studio_Phase1_v2.0.0.md` and `docs/walkthrough/procurement/Procurement_PO_Service_Refactor_v2.2.0.md`.

### Changed
- **Purchase Studio — Supplier Ledger** (`get_supplier_ledger`): Now reads real ERPNext GL entries via `erp_adapter.get_supplier_gl_entries()` instead of SMRITI Purchase Order totals. Returns accurate `total_payable` (outstanding PI amount) and `overdue` (overdue PI amount) instead of PO values with hardcoded `0.0` overdue.
- **Purchase Studio — Dashboard KPIs** (`get_dashboard_data`): `pending_grns` now calls `erp_adapter.count_pending_grns()` (real unbilled GRN count); `unpaid_invoices_amt` now calls `erp_adapter.get_outstanding_payables_total()` (real outstanding); `month_spend` now calls `erp_adapter.get_monthly_spend_total()` (GST-inclusive PI-based); `recent_activity` now calls `erp_adapter.get_recent_activities()` (cross-doctype PO+GRN+PI feed). Removed fabricated `month_spend * 0.4` estimate.
- **Purchase Studio — Analytics** (`get_purchase_analytics`): Replaced 3 direct SQL queries on `tabSMRITI Purchase Order` with `erp_adapter.get_purchase_spend_analytics()` which reads from `tabPurchase Invoice` (GST-inclusive actual payments). Analytics now reflect real financials, not pre-GST order intents.
- **Purchase Studio — Variant Resolution** (`resolve_variant_item`): Replaced N+1 attribute query loop (one DB call per variant) with a single batch `frappe.db.get_all("Item Variant Attribute")` call for all variants, then grouped by parent in Python. Reduces DB queries from O(n) to O(1) for variant resolution.
- **Purchase Studio — Search** (`search_suppliers`): Merged as thin alias of `get_suppliers()`. Removed duplicate `PurchaseOrderService.list_suppliers()` call. SC-13 API endpoint unchanged.

### Infrastructure
- Merged `smriti-next` branch into `main` via fast-forward. `smriti-next` deleted locally and on remote.
- Both dev (`D:\Smriti_Retail_OS`) and test (`F:\Smriti9`) environments at commit `782917c`.

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
