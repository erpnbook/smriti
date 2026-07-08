# SMRITI UI Architecture

> **Status:** DRAFT — v1.0.0
> **Authority:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to:** All UI Developers, AI Agents, Product Contributors
> **Companion to:** `SMRITI_EXPERIENCE_CONSTITUTION.md`, `SMRITI_PLATFORM_VISION.md`, `ARCHITECTURE.md`
> **Supersedes:** Nothing — this is a new document filling the companion gap referenced in `SMRITI_EXPERIENCE_CONSTITUTION.md` §Purpose.

---

## Purpose

The Platform Vision defines *what* SMRITI is.
The Engineering Constitution (`ARCHITECTURE.md`) defines *how* it is built at the backend.
The Experience Constitution defines *how* it behaves and feels.
This document defines *how it is composed* — the component inventory, the file layout, and the ownership rules for every visible surface.

---

## 1. Precedence

This document is subordinate to:

```
SMRITI_PRODUCT_CONSTITUTION.md     (SPC — supreme law)
    ↓
ARCHITECTURE.md                    (15 locked rules + persistence boundary)
    ↓
SMRITI_PLATFORM_VISION.md          (Golden Rule, Five Categories)
    ↓
SMRITI_EXPERIENCE_CONSTITUTION.md  (behaviour and feel)
    ↓
SMRITI_UI_ARCHITECTURE.md          (this document — composition and layout)
```

In a conflict, the higher document wins.

---

## 2. Current File Layout (Canonical)

This is the actual, verified layout as of v1.0.0. Do not follow an idealised or proposed layout that does not match this structure.

### 2.1 Page Layer — `www/`

All user-facing HTML pages are served from the flat `www/` directory via Frappe's `www/` routing convention. Each page consists of a paired `.html` + `.py` file.

```
smriti_retail_os/www/
├── billing.html / billing.py              ← POS / Billing
├── smriti-purchase.html / smriti_purchase.py  ← Purchase Studio
├── smriti-grn.html / smriti_grn.py        ← GRN / Goods Receipt
├── smriti-po-create.html / smriti_po_create.py  ← Purchase Order Create
├── smriti-po-print.html / smriti_po_print.py    ← Purchase Order Print
├── inventory.html / inventory.py          ← Inventory
├── customers.html / customers.py          ← Customers
├── suppliers.html / suppliers.py          ← Suppliers
├── products.html / products.py            ← Items / Products (A2 reference implementation)
├── reports.html / reports.py             ← Reports
├── analytics.html / analytics.py         ← Analytics
├── security.html / security.py           ← Security Center
├── smriti-home.html / smriti_home.py     ← Home / Dashboard
├── barcode.html / barcode.py             ← Barcode
├── shift.html / shift.py                 ← Shift Management
├── payments.html / payments.py           ← Payments
├── smriti-coming-soon.html               ← Feature flag placeholder
└── ... (see www/ for complete list)
```

**Rule:** New pages must be added to `www/`. Do not create HTML files inside studio or module directories — Frappe does not serve them from there without custom route registration (which requires an ADR).

### 2.2 Business Logic Layer — Studio Packages

Each business domain is a Python package following the `*_studio` naming convention.

```
smriti_retail_os/
├── purchase_studio/
│   ├── api/
│   ├── service/
│   ├── repository/
│   └── adapter/
├── sales_studio/
│   ├── api/
│   ├── service/
│   ├── repository/
│   └── adapter/
├── customer_studio/
├── item_studio/
├── user_studio/
├── analytics_studio/
├── search_studio/
├── notification_studio/
├── label_studio/
└── ... (see smriti_retail_os/ for complete list)
```

**Rule:** Studio packages contain Python only — API controllers, service logic, repositories, adapters. They do NOT contain HTML/CSS/JS.

### 2.3 Shared API Layer — `api/`

Top-level API files (`smriti_retail_os/api/`) serve whitelisted Frappe endpoints for features that predate the studio refactor or span multiple domains.

### 2.4 Print Framework — `print_framework/`

All print templates and print engine logic lives in `smriti_retail_os/print_framework/`. Screen-level print pages (e.g., `smriti-po-print.html`) live in `www/` and delegate rendering to `print_framework/`.

### 2.5 Public Assets — `public/`

```
smriti_retail_os/public/
├── css/
│   └── smriti_tokens.css     ← Design tokens (single source of truth for colours, fonts)
└── js/
    └── smriti_*.js           ← Shared JS bundles
```

**Rule:** Never hardcode colours or font sizes in page-level CSS. Always use CSS variables from `smriti_tokens.css`.

---

## 3. Module UI Ownership

Every business module owns its user-facing experience. The following table maps each module to its primary `www/` pages and its studio package.

| Module | Primary www/ Pages | Studio Package | Status |
|---|---|---|---|
| Billing / POS | `billing.html` | `sales_studio/` | A1 → A2 in progress |
| Purchase | `smriti-purchase.html`, `smriti-po-create.html`, `smriti-po-print.html` | `purchase_studio/` | A1 → A2 in progress |
| GRN / Goods Receipt | `smriti-grn.html`, `purchase_receipt.html` | `purchase_studio/` | A1 |
| Inventory | `inventory.html`, `stock-audit.html` | *(services/)* | A1 |
| Customers | `customers.html` | `customer_studio/` | A1 |
| Suppliers | `suppliers.html` | *(services/)* | A1 |
| Items / Products | `products.html`, `item_master.html` | `item_studio/` | **A2** (reference) |
| Barcode / Labels | `barcode.html`, `label.html` | `label_studio/` | A1 |
| Payments | `payments.html` | *(billing_api)* | A1 |
| Shift | `shift.html` | *(shift_api)* | A1 |
| Reports | `reports.html` | *(reports_api)* | A1 |
| Analytics | `analytics.html` | `analytics_studio/` | A1 |
| PSV / Channel | `psv-dashboard.html`, `psa.html` | *(psv_*)* | A1 |
| Security | `security.html`, `smriti-security-log.html` | `user_studio/` | A1 |
| CGE | `smriti-cge.html` | `cge/` | A1 |
| Clienteling | `smriti-clienteling.html` | `clienteling/` | A1 |
| SFM / SFC | `smriti-sfm.html`, `smriti-sfc.html` | `sfm/` | A1 |

**A2 Reference Implementation:** `products.html` → `item_studio/api/` → `item_studio/service/` → `item_studio/repository/`

---

## 4. Component Inventory (SPC-C-012 — Candidate)

> **Governance status:** Candidate Article SPC-C-012 in `SMRITI_PRODUCT_CONSTITUTION.md`.
> These components do not yet exist as a shared library. They exist as inline patterns within individual `www/*.html` files.
> The interim baseline is those inline patterns. This inventory defines the *target* component library.

### 4.1 Current State

Components are implemented inline. Each `www/*.html` file contains its own:
- Sidebar HTML (`smriti-sidebar` pattern)
- Topbar HTML (`smriti-topbar` pattern)
- Token loader (`{% include "templates/includes/smriti_token_loader.html" %}`)
- Page-specific CSS and JS in `<style>` and `<script>` blocks

### 4.2 Target Component Library

When the component library is formally scoped (Phase 2+), these components must be extracted as reusable SMRITI-owned units:

| Component | Current State | Target |
|---|---|---|
| **SMRITI Page Shell** | Inline in every `.html` (topbar + sidebar + token loader) | Shared include / Web Component |
| **SMRITI Form** | Inline per page | Configurable form component |
| **SMRITI Data Grid** | Inline tables per page | Shared grid with sort/filter/paginate |
| **SMRITI Sidebar** | `smriti_sidebar.html` include | Shared include (exists) |
| **SMRITI Topbar** | `smriti_topbar.html` include | Shared include (exists) |
| **SMRITI Toolbar** | Inline per page | Extracted toolbar component |
| **SMRITI Ribbon** | Not yet implemented | New — Phase 2 |
| **SMRITI Dashboard Card** | Inline per dashboard page | Reusable card component |
| **SMRITI Dialog** | Inline modals per page | Shared modal/dialog component |
| **SMRITI Search** | Inline per page | Shared search component (debounced, scope-aware) |
| **SMRITI Notification Center** | `smriti-notifications.html` (standalone page) | Embedded panel + standalone page |
| **SMRITI Error Center** | Inline error states per page | Shared error boundary component |
| **SMRITI Print Studio** | `print_framework/` + `smriti-po-print.html` | Formal print registry + template engine |
| **SMRITI Mail Studio** | Not yet implemented | New — Phase 2 (email templates) |

**Rule:** No module may depend on default Platform Engine UI components (Frappe Desk widgets, ERPNext forms). Until the shared library exists, the inline pattern from `products.html` (A2 reference implementation) is the required baseline.

---

## 5. Document Format Matrix (SPC-C-013 — Candidate)

> **Governance status:** Candidate Article SPC-C-013 in `SMRITI_PRODUCT_CONSTITUTION.md`.
> See `SMRITI_EXPERIENCE_CONSTITUTION.md` §Document Experience Constitution (Rules DOC-E1 through DOC-E5) for the enforcement rules.

### 5.1 Format Definitions

| Format | Required By | Current State |
|---|---|---|
| Screen View | All documents, immediately | Exists for most documents |
| Print View | All documents, before GA | Partial — `smriti-po-print.html` exists; others are Platform Engine fallbacks |
| PDF | All documents, before GA | Not formalised — currently Platform Engine print |
| Email | Transactional documents (Invoice, PO), before GA | Not implemented |
| Mobile View | All documents, Phase 2 | Not implemented |

### 5.2 Per-Document Format Completion Tracker

| Document | Screen | Print | PDF | Email | Mobile |
|---|---|---|---|---|---|
| Purchase Order | ✅ | ✅ `smriti-po-print.html` | ⬜ | ⬜ | ⬜ |
| Purchase Invoice | ✅ `purchase_invoice.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Goods Receipt Note | ✅ `smriti-grn.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Supplier Return | ✅ `supplier_returns.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Sales Invoice | ✅ `billing.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Sales Order | ✅ `sales_orders.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Quotation | ✅ `smriti-quotation.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Sales Return | ✅ `sales_return.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Delivery Challan | ✅ `delivery_challan.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Stock Entry | ✅ `inventory.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Barcode Label | ✅ `label.html` | ✅ `label.html` (thermal) | ⬜ | N/A | ⬜ |
| Customer Ledger | ✅ `reports.html` | ⬜ | ⬜ | ⬜ | ⬜ |
| Supplier Ledger | ✅ `reports.html` | ⬜ | ⬜ | ⬜ | ⬜ |

*Legend: ✅ Implemented  ⬜ Not yet implemented  N/A Not applicable*

---

## 6. Design System Reference

The design system is defined in `ARCHITECTURE.md` §10. This section adds the UI-layer file references.

### 6.1 Token File

```
smriti_retail_os/public/css/smriti_tokens.css
```

All CSS variables (colours, font sizes, spacing, border radii) are defined here. Every page must load this file via:

```html
{% include "templates/includes/smriti_token_loader.html" %}
```

### 6.2 Page Shell Includes

Every SMRITI page must include these three templates:

```html
{% include "templates/includes/smriti_token_loader.html" %}
{% include "templates/includes/smriti_topbar.html" %}
{% include "templates/includes/smriti_sidebar.html" %}
```

### 6.3 Colour Reference

```css
--smriti-navy:    #1A2B5C;   /* Primary dark navy */
--smriti-blue:    #2563EB;   /* Action blue */
--smriti-surface: #16213e;
--smriti-surface2:#1a2744;
--smriti-border:  #2a3a5c;
--smriti-text:    #e2e8f0;
--smriti-muted:   #8892a4;
--smriti-success: #22c55e;
--smriti-warning: #f59e0b;
--smriti-danger:  #ef4444;
--smriti-info:    #3b82f6;
```

---

## 7. Platform Boundary (UI Perspective)

This section restates the platform boundary from the UI developer's point of view. For the full ownership table see `SMRITI_PLATFORM_VISION.md` §Decision Matrix.

### 7.1 SMRITI Owns (must be built in SMRITI)

- All HTML, CSS, JavaScript for business pages
- All forms, grids, dialogs, toolbars, sidebars, dashboards
- All navigation menus and routing
- All print and email templates for business documents
- All error messages shown to business users
- All report and analytics UIs
- Branding, themes, accessibility

### 7.2 Platform Engine Owns (never replicate in SMRITI UI)

- ORM, database, authentication
- Background jobs, scheduler
- Workflow engine
- Permission checks (SMRITI enforces through API, never bypasses)
- GST computation, E-Way Bill computation

### 7.3 What SMRITI UI Must Never Do

```
❌  Link to /app/*, /desk/*, or /background-jobs
❌  Call frappe.client.insert() or frappe.new_doc() from page JS
❌  Display Platform Engine error messages (stack traces, DocType names)
❌  Use Frappe Desk widget classes or form renderers
❌  Hardcode colours, fonts, or spacing (use CSS variables)
```

---

## 8. Future-State Layout (Phase 2+ — Not Current)

> **Important:** The layout below is a proposed future target. It is NOT the current standard. Do not create these directories now. The current standard is §2 above.

A future migration (requiring a formal ADR) may co-locate HTML assets with their studio packages:

```
purchase_studio/
├── api/
├── service/
├── repository/
├── adapter/
└── ui/               ← Future: HTML assets co-located (requires custom route registration)
    ├── purchase_page.html
    ├── purchase_form.html
    ├── purchase_print.html
    └── purchase.css
```

This would require:
1. Custom Frappe route registration per studio
2. An approved ADR documenting the migration plan
3. Backfill of all existing `www/*.html` pages
4. Architecture Guard updates

Until that ADR is approved, all HTML stays in `www/`.

---

## 9. Naming Conventions

| Artefact | Pattern | Example |
|---|---|---|
| www page (URL) | `/<noun>` or `/smriti-<feature>` | `/billing`, `/smriti-purchase` |
| www HTML file | `<noun>.html` or `smriti-<feature>.html` | `billing.html`, `smriti-purchase.html` |
| www Python file | `<noun>.py` or `smriti_<feature>.py` | `billing.py`, `smriti_purchase.py` |
| API module | `smriti_retail_os.api.<feature>_api` | `smriti_retail_os.api.billing_api` |
| Studio API | `smriti_retail_os.<studio>.api.<feature>_api` | `smriti_retail_os.purchase_studio.api.po_api` |
| Service | `smriti_retail_os.<studio>.service.<feature>_service` | `smriti_retail_os.purchase_studio.service.po_service` |
| Repository | `smriti_retail_os.<studio>.repository.<feature>_repo` | `smriti_retail_os.purchase_studio.repository.po_repo` |
| CSS class prefix | `smriti-` | `smriti-card`, `smriti-btn` |
| CSS variable prefix | `--smriti-` | `--smriti-navy` |

---

## Amendment Log

| Version | Date | Change | Author |
|---|---|---|---|
| v1.0.0 | 2026-07-08 | Initial document created. Fills companion document gap referenced in SMRITI_EXPERIENCE_CONSTITUTION.md §Purpose. Integrates Component Inventory (SPC-C-012) and Document Format Matrix (SPC-C-013) derived from Independent Product Architecture Constitution review. Layout verified against actual codebase. | AI Architecture Agent |

---

*SMRITI UI Architecture v1.0.0 — DRAFT*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Companion to: SMRITI_EXPERIENCE_CONSTITUTION.md, SMRITI_PLATFORM_VISION.md, ARCHITECTURE.md*
