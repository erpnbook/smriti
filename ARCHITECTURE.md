# SMRITI Retail OS™ — Architecture & Technical Reference

> **Status**: LOCKED — v1.2.10
> **Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to**: All Developers, Contributors, AI Agents, Automation Systems

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Architecture Model](#2-architecture-model)
3. [Domain Ownership](#3-domain-ownership)
4. [Accounting Model Clarification](#4-accounting-model-clarification)
5. [Architecture Constitution — 15 Locked Rules](#5-architecture-constitution--15-locked-rules)
6. [SMRITI-First UI Policy (Rule 7)](#6-smriti-first-ui-policy-rule-7)
7. [Desk Blocking Policy (Rule 8)](#7-desk-blocking-policy-rule-8)
8. [Routing Standard](#8-routing-standard)
9. [Service-First Design Pattern](#9-service-first-design-pattern)
10. [Design System](#10-design-system)
11. [Docker Infrastructure](#11-docker-infrastructure)
12. [PSV Architecture](#12-psv-architecture)
13. [Formula Registry & Explainability](#13-formula-registry--explainability)
14. [AI Agent Rules](#14-ai-agent-rules)

---

## 1. Platform Overview

SMRITI Retail OS is architected as a **Retail Experience and Intelligence Layer** — a Frappe v16 application built on top of ERPNext v16 that transforms the ERP into a retail operating platform.

It does not replace ERPNext. It extends it through:

- A fully standalone UI layer (no Frappe Desk exposure to end users)
- A service-first API architecture decoupling UI from backend schema
- Business intelligence engines (PDT, CGE, PSV, Formula Registry)
- Industry-specific retail workflows (POS, GRN, Shift, Barcode, PSV)

---

## 2. Architecture Model

```
+----------------------------------------------------------+
|                  SMRITI Retail OS™                       |
|                                                          |
|  www/ pages (standalone HTML, never /desk)               |
|  api/       (whitelisted service controllers)            |
|  services/  (business logic layer)                       |
|  repositories/ (data access abstraction)                 |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|              ERPNext v16  —  System of Record            |
|                                                          |
|  POS Invoice · Purchase Receipt · Stock Entry            |
|  Item · Customer · Supplier · POS Profile                |
|  Payment Entry · Price List · Loyalty · Accounting       |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|              Frappe Framework v16                        |
|                                                          |
|  ORM · REST API · Auth · Boot Session                    |
|  Hooks · Scheduler · Background Jobs · DocType           |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|     India Compliance v16                                 |
|     GST · GSTIN Validation · e-Invoice · e-Waybill       |
|     GSTR Reports · HSN Codes · Tax Templates             |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|  Database & Infrastructure                               |
|  MariaDB · Redis Cache · Redis Queue · Docker Compose    |
+----------------------------------------------------------+
```

---

## 3. Domain Ownership

The following table is the canonical record of which system owns each business domain. When in doubt, consult this table before building.

| Domain | Owner | Rationale |
|---|---|---|
| Transaction Accounting (GL entries for invoices) | **ERPNext** | System of Record |
| GST / Tax Calculation | **ERPNext + India Compliance** | System of Record |
| Stock Ledger / Inventory Valuation | **ERPNext** | System of Record |
| Customers / Suppliers / Users / Roles | **ERPNext** | System of Record |
| Warehouses / Companies | **ERPNext** | System of Record |
| Statutory Financial Reporting (P&L, Balance Sheet, Trial Balance) | **TallyPrime** | Accounting SOR (see §4) |
| UI / UX | **SMRITI** | Owner |
| POS Experience | **SMRITI** | Owner |
| Retail Workflows | **SMRITI** | Owner |
| Reports & Analytics | **SMRITI** | Owner |
| Store Operations | **SMRITI** | Owner |
| POS Profile Configuration Experience | **SMRITI** | Experience Layer |
| Party Stock Visibility (PSV/PSA) | **SMRITI** | Shadow Ledger (read-only ERPNext) |
| Formula Registry | **SMRITI** | Owner |
| Explain Engine | **SMRITI** | Owner |
| Channel Governance Engine (CGE) | **SMRITI** | Owner |
| Pricing Intelligence | **SMRITI** | Owner (Pricing ≠ Inventory) |
| Trial CRM / Platform Admin | **SMRITI** | Owner |

---

## 4. Accounting Model Clarification

This clarifies an important architectural distinction that must be stated explicitly.

### Operational Accounting — ERPNext

ERPNext is the **operational System of Record** for all transaction-level accounting:

- Every POS Invoice creates GL entries in ERPNext
- Every Purchase Receipt creates GL entries and stock valuation entries in ERPNext
- GST is calculated and recorded in ERPNext via India Compliance
- Payment Entries are created in ERPNext

This is non-negotiable. SMRITI never bypasses ERPNext accounting.

### Statutory Financial Reporting — TallyPrime (where applicable)

In deployments where **TallyPrime integration is active** (typically FMCG, Distributor, and Enterprise Retail clients):

- TallyPrime is the **statutory System of Record** for books of accounts
- Trial Balance, P&L, and Balance Sheet are produced from TallyPrime
- ERPNext transaction data may be synchronized to Tally via the SMRITI Tally Integration layer

In deployments **without Tally integration**, ERPNext serves as the complete accounting system.

### Summary

```
ERPNext always:   Transaction accounting (GL, GST, Stock Valuation)
Tally (optional): Statutory reporting (P&L, Balance Sheet, Trial Balance)
SMRITI never:     Creates duplicate GL, stock valuation, or tax engines
```

---

## 5. Architecture Constitution — 15 Locked Rules

These rules apply to all developers, contributors, and AI agents. They are LOCKED.

### Rule 1 — Do NOT Replace the Architecture
Agents and developers may **extend**, **improve**, **refactor**, or **optimize**.
They may **NOT** replace the architecture, introduce competing frameworks, or ignore approved service layers.

### Rule 2 — Service-First Design (MANDATORY)

```
REQUIRED:   UI → API → Service Layer → Business Logic → Database
FORBIDDEN:  UI → Database
FORBIDDEN:  frappe.client.insert() or frappe.new_doc() called from UI JS
```

### Rule 3 — Inventory-First Operations
All stock calculations must originate from Purchase, GRN, Landed Cost, and Stock Ledger.
Never create a separate stock valuation system.

### Rule 4 — Accounting Model Boundary
See §4 above. ERPNext handles operational accounting. SMRITI never duplicates GL, stock valuation, or tax engines.

### Rule 5 — Single Source of Truth
Every business concept has exactly one owner. No duplicate ownership.

### Rule 6 — PSV Ownership Boundary
PSV reads ERPNext master data. PSV does NOT modify ERPNext Stock Ledger Entries or General Ledger Entries. PSV maintains its own shadow ledger.

### Rule 7 — No Shadow Databases
Never create duplicate customer masters, supplier masters, or stock tables. Extend existing masters; do not replace them.

### Rule 8 — Pricing Is a Separate Domain
Pricing owns Price Lists, Customer Pricing, Promotions, Schemes, and Price Revisions. Inventory never maintains selling prices.

### Rule 9 — Approval Before Automation
Analytics and recommendations may be automatic. Business actions require human approval:

```
Allowed without approval:    Recommendations · Alerts · Suggestions
Requires human approval:     Auto POs · Auto Transfers · Auto Discounts · Auto Price Changes
```

### Rule 10 — Auditability Required
Every critical action must record:

```
User · Timestamp · Before Value · After Value · Reason
```

Examples: Price Revision, Stock Adjustment, Recovery Action, Configuration Change.

### Rule 11 — Feature Flags Required
Unfinished features must be hidden until activated. Use the Coming Soon page:

```
/smriti-coming-soon?feature=Feature+Name&progress=60&eta=Q3+2026
```

### Rule 12 — Backward Compatibility
Existing APIs, DocTypes, and Workflows must be preserved. Breaking changes require explicit approval.

### Rule 13 — Governance Gate (Mandatory)
```
Architecture Review → Gap Analysis → Approval → Implementation → Verification → Evidence → Closure
```
Never skip governance stages.

### Rule 14 — No Unrelated Projects
Agents must prioritize existing approved modules and roadmap items. New unrelated projects require explicit governance approval.

### Rule 15 — Explainability-First (DOC-01)
Every metric, KPI, score, recommendation, or prediction displayed to users must have a `ⓘ Explain` modal providing:

```
1. Business Meaning
2. Exact Formula
3. Worked Example (real retail numbers)
4. Data Sources
5. Interpretation Guide (score bands)
6. Recommended Action
```

---

## 6. SMRITI-First UI Policy (Rule 7 — LOCKED)

> **Every new page, module, form, report, or UI component MUST be a dedicated SMRITI standalone page. Frappe Desk (/desk, /app) must NEVER be exposed to end users.**

### Forbidden Patterns

```
❌  User clicks → /desk#Form/Sales Invoice/new
❌  User clicks → /app/sales-invoice
❌  frappe.new_doc("Sales Invoice") from UI JS
❌  frappe.set_route("Form", "Customer") from UI JS
```

### Required Patterns

```
✅  User clicks → /billing (SMRITI custom page)
✅  User clicks → /smriti-masters (SMRITI custom page)
✅  frappe.call("smriti_retail_os.api.billing_api.create_invoice")
✅  SMRITI modal/form renders custom UI
```

### Mandatory Checklist (ALL must be YES before proceeding)

```
□  Dedicated SMRITI www page exists for this feature?
□  URL uses /smriti-*, /billing, /inventory, /reports, /masters or another SMRITI route?
□  All backend calls go through a SMRITI service controller?
□  Page uses SMRITI design system (Navy #1A2B5C + Blue #2563EB)?
□  Page shows SMRITI logo and branding?
□  /desk and /app are completely hidden from this user flow?
```

If **any** answer is NO — stop. Build the SMRITI wrapper first.

### Naming Convention

| Category | Pattern |
|---|---|
| Pages | `/smriti-<feature>` |
| APIs | `smriti_retail_os.<module>.api.<feature>_api.<method>` |
| Services | `smriti_retail_os.<module>.service.<feature>_service.<method>` |
| CSS | `smriti_<feature>.css` |
| JS | `smriti_<feature>.js` |

### Minimum Required Files Per New Page

```
smriti_retail_os/www/<page-name>.html   ← UI template
smriti_retail_os/www/<page-name>.py     ← Auth + context
smriti_retail_os/api/<feature>_api.py   ← Whitelisted backend API
```

---

## 7. Desk Blocking Policy (Rule 8 — LOCKED)

The following paths are blocked for **all users** (including Administrator) via `boot.py`:

```python
SMRITI_BLOCKED_DESK_PATHS = [
    "/desk/setup-wizard",   # → redirect /smriti
    "/desk/modules",        # → redirect /smriti
    "/desk#Form",           # → redirect /smriti
    "/desk#List",           # → redirect /smriti
    "/desk#query-report",   # → redirect /smriti
    "/desk#setup-wizard",   # → redirect /smriti
]
```

**Exception**: System Manager role bypasses SMRITI routing for legitimate ERP administration. This exception is intentional and must not be removed.

---

## 8. Routing Standard

SMRITI uses Frappe v16 canonical routes exclusively.

```javascript
// CORRECT
frappe.set_route("stock-center");
window.location.href = "/app/stock-center";

// FORBIDDEN
window.location.href = "/page/stock-center";
window.location.href = "/desk/page/stock-center";
```

Sidebar config must use:

```javascript
{ label: "Stock Center", route: "stock-center" }
// NOT: { label: "Stock Center", route: "/page/stock-center" }
```

---

## 9. Service-First Design Pattern

Every new feature must follow this four-layer structure:

```
smriti_retail_os/
├── www/<feature>.html             # UI — calls API via frappe.call()
├── api/<feature>_api.py           # API — @frappe.whitelist(), role checks
├── services/<feature>_service.py  # Service — business logic, validation
└── repositories/<feature>_repo.py # Repository — data access, ERPNext DocType ops
```

### Example: POS Profile Module

```
www/smriti-pos-profiles.html       ← Standalone SMRITI page
api/pos_profile_api.py             ← 7 whitelisted endpoints
services/pos_profile_service.py    ← Shift-lock guard, clone logic
repositories/pos_profile_repository.py ← CRUD, soft-delete
```

### Forbidden Anti-Patterns

```python
# FORBIDDEN — UI directly manipulating DocType
frappe.client.insert({"doctype": "Sales Invoice", ...})

# FORBIDDEN — No service layer
@frappe.whitelist()
def save_profile():
    frappe.db.set_value(...)  # Direct DB write from API, no service

# REQUIRED — Full stack
@frappe.whitelist()
def save_profile(data):
    return pos_profile_service.save(frappe.parse_json(data))
```

---

## 10. Design System

### Color Palette

```css
:root {
    --smriti-navy:    #1A2B5C;   /* Primary dark navy — backgrounds */
    --smriti-blue:    #2563EB;   /* Action blue — buttons, accents */
    --smriti-surface: #16213e;   /* Card / sidebar surface */
    --smriti-surface2:#1a2744;   /* Input / secondary surface */
    --smriti-border:  #2a3a5c;   /* Border color */
    --smriti-text:    #e2e8f0;   /* Primary text */
    --smriti-muted:   #8892a4;   /* Secondary / muted text */
    --smriti-success: #22c55e;
    --smriti-warning: #f59e0b;
    --smriti-danger:  #ef4444;
    --smriti-info:    #3b82f6;
}
```

### Typography

| Use | Font | Weights |
|---|---|---|
| Body / UI | Arial | System default |
| Headings | Outfit (Google Fonts) | 300, 400, 600, 800 |
| Body text | Inter (Google Fonts) | 400, 500, 600, 700 |
| Icons | Material Symbols Outlined | Variable |

### Page Shell

Every SMRITI page uses three shared includes:

```html
{% include "templates/includes/smriti_token_loader.html" %}
{% include "templates/includes/smriti_topbar.html" %}
{% include "templates/includes/smriti_sidebar.html" %}
```

---

## 11. Docker Infrastructure

```yaml
# Container roles
frontend          Nginx — proxy, static assets (port 8765)
backend           Gunicorn — Frappe WSGI app server
websocket         Socket.IO — real-time relays
db                MariaDB — relational database
redis-cache       Redis — session and page cache
redis-queue       Redis — RQ job broker
queue-short       RQ worker — transactional jobs
queue-long        RQ worker — bulk imports / reports
scheduler         Background job daemon
```

### Asset Pipeline Note

SMRITI uses `sync_assets.py` during container bootstrap to copy compiled bundles directly into Nginx volumes (bypassing symlink limitations in Docker environments). This is intentional and must not be replaced with standard Frappe symlink-based asset serving.

---

## 12. PSV Architecture

Party Stock Visibility (PSV) is a **Business-Type Activated Core Extension** — active for businesses selling through external channels (Footwear Brands, FMCG, Distributor Networks), hidden for standard retail.

```
PSV Owns:
  Distributor Stock · Channel Stock · Sell-Through
  Coverage Days · Inventory Aging · Capital Locked
  Recovery Suggestions

PSV Does NOT Own:
  Warehouse Inventory · Purchase Processing · Accounting

Technical Constraints:
  ✅  Reads ERPNext master data
  ❌  Does NOT modify ERPNext Stock Ledger Entries
  ❌  Does NOT modify ERPNext General Ledger Entries
  ✅  Maintains its own shadow ledger (SmritiPSVTransaction DocType)
```

---

## 13. Formula Registry & Explainability

All computed KPIs must be registered in the **SMRITI Formula Registry** (`/smriti-formula-registry`) before production deployment.

### Core Registered Formulas

| Formula | Category |
|---|---|
| Sales Velocity | Inventory Intelligence |
| Weeks of Cover (WOC) | Inventory Intelligence |
| Outlet Health Score | Store Analytics |
| Dead Stock Score | Inventory Intelligence |
| Transfer Benefit Score | Operations |
| Forecast Confidence | AI / PDT |
| Sell Through % | PSV / Channel |
| Stock Accuracy % | Audit |
| Inventory Turnover | Finance |
| Variant Curve Health | Merchandising |

### Explainability Requirement (DOC-01)

Every formula registration must document:

```
A. Business Meaning
B. Formula (exact mathematical expression)
C. Worked Example (real retail numbers)
D. Data Sources (source tables / parameters)
E. Interpretation Guide (score bands: Critical / Monitor / Healthy)
F. Recommended Action (what the user should do next)
```

The UI must render this via a `ⓘ Explain` button on every metric card.

---

## 14. AI Agent Rules

For any AI assistant or automated development tool working on SMRITI:

### Before Any Change

```
1. Read this file in full.
2. Read hooks.py — understand what is registered.
3. Read boot.py — understand role routing and Desk blocking.
4. Search existing www/ pages — does the route already exist?
5. Verify the ERPNext DocType to use before creating custom ones.
```

### Adding a New Feature

```
Step 1:  Identify existing ERPNext DocType to leverage
Step 2:  Create www/<feature>.html + .py
Step 3:  Create api/<feature>_api.py  (role-checked, @whitelisted)
Step 4:  Create services/<feature>_service.py
Step 5:  Create repositories/<feature>_repository.py (if needed)
Step 6:  Register in smriti_nav_config.js
Step 7:  Write tests/test_<feature>.py (min 5 tests)
Step 8:  Create 6 governance docs (PROD, USER, ADMIN, DEV, API, KB)
Step 9:  bench build → migrate → clear-cache → restart
Step 10: Verify in browser at /smriti-<feature> (never via /desk)
```

### Common Forbidden Patterns

```
❌  Navigating to /desk or /app in browser automation
❌  frappe.client.insert() or frappe.new_doc() from UI
❌  Direct DB writes from API (bypassing service layer)
❌  Creating new DocType when ERPNext one exists
❌  /page/* or /desk/page/* in sidebar/buttons
❌  Hardcoded colors instead of CSS variables
❌  Redirecting System Manager to SMRITI pages
```

### File Edit Checklist

```
Python file edits:     bench migrate → clear-cache → restart
JS/CSS file edits:     bench build → clear-cache → hard refresh
hooks.py edits:        bench migrate → clear-cache → restart → hard refresh
New API added:         verify @frappe.whitelist() + role check + unit test
```

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.2.10 — LOCKED*

---

## 15. Persistence Boundary Guard

**Rule:** The Repository/Adapter layer is the **only** layer permitted to call Platform Engine persistence APIs.

```
UI -> api -> service -> repository -> Platform Engine
                             ^
                    ONLY HERE may these calls appear:
                      frappe.get_doc(
                      frappe.new_doc(
                      frappe.db.sql(
                      frappe.db.set_value(
                      frappe.db.commit(
                      frappe.db.delete(
                      frappe.delete_doc(
```

**Allowed in service layers** (framework utilities, not persistence):
`frappe.throw`, `frappe.db.exists`, `frappe.get_cached_doc`, `frappe.permissions`, `frappe.utils`, `frappe._`

**Enforcement:** `smriti_architecture_guard.py` at the repo root enforces this rule in CI and pre-commit.

- **Ratchet mode** (default): passes against the current baseline, fails only on new violations or regressions.
- **Report mode** (`--report`): prints sprint-by-sprint progress, always exits 0.
- **Strict mode** (`--strict`): fails on any violation; switch to this once the backlog is cleared.

Baseline snapshot: `architecture_baseline.json` (versioned, ROOT-relative paths).

Migration backlog: `ARCHITECTURE_MIGRATION_BACKLOG.md` — 88 files, 858 calls, sequenced P0 to P3.

Reference implementation: `api/pos_profile_api.py` -> `services/pos_profile_service.py` -> `repositories/pos_profile_repository.py`

---

## 16. Platform Vision

See `SMRITI_PLATFORM_VISION.md` at the repo root for the full statement of:

- **Rule 0 — Business Experience Boundary** (Business User -> SMRITI -> Platform Engine, never directly to Platform Engine)
- **Domain ownership** (what SMRITI owns vs. what the Platform Engine owns)
- **Terminology standard** ("Platform Engine (currently ERPNext + Frappe)" not "ERPNext")
- **Studio model**
- **Architecture Guards roadmap** (Guards 1–5)

Every AI agent, developer, and contributor working on SMRITI must read `SMRITI_PLATFORM_VISION.md` before making architecture decisions.

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.3.0 — LOCKED*

---

## 17. Feature Category Framework

Every feature, page, and tool belongs to exactly one category.
Apply the Golden Rule first:

> If a feature exists only to operate the Platform Engine, keep it in the Platform Engine.
> If a feature is part of the business experience, SMRITI owns it.

| Category | Owner | Rule |
|---|---|---|
| A -- Business Experience | SMRITI | Replace all Platform Engine UI with SMRITI Studio pages |
| B -- Platform Administration | Platform Engine | Keep. Never wrap in SMRITI UI. |
| C -- Platform Services | Platform Engine | Never replace (ORM, Workflow, Scheduler, Print) |
| D -- SMRITI Innovation | SMRITI | Exclusive SMRITI IP (PSV, CGE, AI, Formula) |
| E1 -- Statutory Compliance | Platform Engine computes, SMRITI wraps view | Never recompute GST/E-Way |
| E2 -- Accounting Integration | Accounting Adapter | SMRITI -> Adapter -> TallyPrime / Busy / Zoho |

Category A migration states:
- A1: SMRITI-owned URL, frappe.client.* direct (transitional, unacceptable final state)
- A2: SMRITI-owned URL, data routed through API -> Service -> Repository (required final state)

Category B Protection Rule: Never build a SMRITI UI page for a Category B tool.
If a business user needs information from a Category B context, build a Category A
page that surfaces the specific business information -- not the raw admin tool.

Full specification: SMRITI_PLATFORM_VISION.md (v2.0.0, LOCKED)

---

## 18. Experience Constitution

The SMRITI_EXPERIENCE_CONSTITUTION.md defines how SMRITI behaves and feels.
It governs:

- User Personas (5 personas: Owner, Manager, Cashier, Purchase Manager, CA)
- Navigation (Sidebar, Breadcrumb, Back, No Platform Engine Navigation)
- Page Structure (Title, Search, Primary Action, Empty/Loading/Error states)
- Forms (Save/Cancel, Ctrl+S, validation before save, human-language errors)
- Buttons (One primary action, verb labels, destructive confirmation, loading states)
- Vocabulary (forbidden words: DocType, Frappe, Workspace, Desk, Master, Party, Submit, Amend)
- Keyboard Shortcuts (Ctrl+S, Ctrl+N, Ctrl+F, Escape, F2, F12)
- Search (instant, debounced, retailer-aware fields)
- Dashboard (Owner persona, KPI Explain buttons, no frappe.client direct calls)
- AI Behavior (recommends only, explainable, retail language, feature-flagged)
- Constitution Checklist (mandatory checklist before any page is declared A2 complete)

Every new page and every A1->A2 migration must pass the Constitution Checklist.

Full specification: SMRITI_EXPERIENCE_CONSTITUTION.md (v1.0.0, LOCKED)

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.4.0 — LOCKED*

---

## 19. SMRITI Connect™ — Integration Platform

SMRITI Connect is the enterprise-grade integration framework for SMRITI Retail OS. It decouples business modules from external APIs via an event-driven outbox queue and dynamic adapter registry.

### 19.1 Event Flow

```
Billing -> Business Event -> Policy Engine -> Event Bus -> Outbox Queue -> Engine Worker -> Registry -> Adapter -> Transport -> External API
```

### 19.2 Platform Specifications

1. **SMRITI Integration Provider (Registry):** DocType managing active adapters. Fields include: `provider_id`, `provider_type`, `version`, `min_platform_version`, `status`, `enabled`, `adapter_class`, `health_status`, `last_check`.
2. **SMRITI Event Definition (Schema Registry):** DocType managing schemas. Fields include: `event_name`, `version`, `producer`, `consumers` (dependency graph), `required_fields` (JSON validation).
3. **SMRITI Integration Policy (Policy Engine):** Rules engine deciding whether an event should route to specific adapters per company/location settings.
4. **Outbox Pattern:** Events are inserted into the database queue (`SMRITI Integration Queue`) inside the source document's active SQL transaction. If the transaction rolls back, the event rolls back.
5. **Adapter Lifecycle Hooks:** Every adapter must inherit from `BaseIntegrationAdapter` and implement: `connect()`, `disconnect()`, `health_check()`, and `handle_event()`.
6. **Queue Partitioning:** Supports `Critical`, `Normal`, and `Low` priorities, executed progressively by the engine worker.
7. **SMRITI Connect Admin Console:** Replaces individual plugin pages with a unified interface at `/connect` showing a health dashboard, latency metrics, provider configuration toggles, queue monitors, and audit logs.

Full specification: SMRITI_CONNECT_ARCHITECTURE.md (v1.0.0, LOCKED)

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.5.0 — LOCKED*

---

## 20. Platform Roadmap

The roadmap establishes the execution phases of SMRITI components:

- **Phase 1: Repository Migration (P0)** (Security, License, Trial, Billing, Payment data layer re-routing)
- **Phase 2: Complete SMRITI Experience** (URL cleanups and Category E1 statutory wrappers)
- **Phase 3: Operational Hardening** (Deduplication, metrics, HTTPS transport encryption)
- **Phase 4: GA Readiness** (Load tests, security penetration audits, UAT validation)

Full specification: SMRITI_ROADMAP.md (v1.0.0, LOCKED)

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.6.0 — LOCKED*

---

## 21. SMRITI Rule 21 — Verify Before Create

Before creating any new file, document, DocType, page, API, service, repository, integration, report, or configuration, the repository must first be searched to determine whether an equivalent implementation or section already exists.

### Priority Order:

1. **REUSE** existing implementation or document.
2. **EXTEND** existing implementation or document.
3. **CREATE** a new implementation only if no suitable equivalent can be found.

**Every creation request must include repository evidence for why a new artifact is necessary.**

---

*SMRITI Retail OS™ — Architecture & Technical Reference*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Version: 1.7.0 — LOCKED*
