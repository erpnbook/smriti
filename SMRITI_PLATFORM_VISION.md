# SMRITI Platform Vision

> **Status:** LOCKED — v2.0.0
> **Authority:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to:** All Developers, Contributors, AI Agents, Automation Systems
> **Supersedes:** v1.0.0

---

## The Single Most Important Sentence

> **SMRITI is the product. The Platform Engine is an internal implementation detail.**

---

## The Golden Rule

> **If a feature exists only to operate the Platform Engine, keep it in the Platform Engine.**
> **If a feature is part of the business experience, SMRITI owns it.**

This rule answers every architecture question. It is adopted as supreme law in the SMRITI Product Constitution (SPC-000). In the event of any conflict, SMRITI_PRODUCT_CONSTITUTION.md prevails.

---

## Rule 0 -- Business Experience Boundary

```
Business User
      |
      v
   SMRITI
      |
      v
Platform Engine
```

A business user must never interact with the Platform Engine directly -- not through a URL,
a form, a list view, a workspace, a report, a print format, or any other surface.

If a feature is not yet available in SMRITI, the correct response is a SMRITI
Coming Soon page -- never a Frappe Desk fallback.

---

## Final Architecture Model

```
Business User
      |
      v
SMRITI Experience Layer
  Dashboard | Pages | Forms | Reports | Search | Navigation | AI
      |
      v
SMRITI Business Layer
  API | Service | Repository
      |
      v
Platform Engine (currently ERPNext + Frappe)
  Workflow | ORM | Permissions | Scheduler | Print
      |
      v
Database
```

Side channel (not in the main request-response flow):

```
Compliance Layer
  GST | E-Way Bill | Statutory (computed by Platform Engine / India Compliance)

Accounting Integration Layer
  Accounting Adapter -> TallyPrime / Busy / Zoho Books / QuickBooks / SAP
```

---

## The Five Categories

Every feature, page, and tool in the SMRITI ecosystem belongs to exactly one category.

---

### Category A -- Business Experience (SMRITI owns)

Definition: Any feature that a retailer, store manager, cashier, purchase manager,
or owner uses in their day-to-day business operations.

SMRITI owns:
- UI, UX, Navigation, Forms, Lists, Search, Reports (operational), Dashboard
- Store User Management and Role Assignment (business operation, not IT admin)
- All retail workflows: Billing, Purchase, Inventory, Customers, Suppliers, Items

Rule: Business users must never open a Platform Engine URL for Category A tasks.

Examples:
- Item / Product Catalog
- Customers
- Suppliers
- Billing (Sales Invoice)
- Purchase Order
- Purchase Receipt / GRN
- Stock Entry
- Inventory
- Payments
- Barcode / Label Printing
- Shift Management
- Store User Management
- Operational Reports (Sales by Item, Inventory Aging, etc.)

#### Migration States

Since most Category A pages already exist as SMRITI URLs but have not yet
completed the full data-layer migration, two sub-states are tracked:

| State | URL | Data Layer | Status |
|---|---|---|---|
| A1 | SMRITI-owned (/customers) | frappe.client.* direct | Work in progress |
| A2 | SMRITI-owned (/customers) | SMRITI API -> Service -> Repository | Complete |

A1 pages have the correct visual ownership. They have NOT completed the data-layer
migration. All A1 pages must move to A2.

A2 is the only acceptable final state for a Category A page.

Reference implementation: products.html (A2, Guard-compliant, Repository-backed).

---

### Category B -- Platform Administration (Platform Engine admin tools)

Definition: Any feature that exists only to operate, monitor, or maintain the
Platform Engine infrastructure. Business users have no reason to use these tools.

Platform Engine owns:
- Background Jobs
- Error Logs
- Installed Applications
- Scheduler
- System Console
- Site Config / Bench commands
- Database Console

Rule: SMRITI must NEVER build a UI wrapper for Category B tools.

#### Category B Protection Rule

If a developer proposes building a SMRITI page for a Category B tool, the
correct answer is always: NO.

If a business user reports needing information from a Category B context,
the correct response is to build a Category A page that surfaces the
specific business information they need -- not the raw admin tool.

Examples of forbidden Category A-B confusion:

  WRONG: Build a SMRITI Background Jobs page
  RIGHT: Build a "Failed Invoices" alert in the SMRITI Dashboard

  WRONG: Build a SMRITI Error Logs viewer
  RIGHT: Build a SMRITI Sync Status indicator for business-relevant operations

  WRONG: Build a SMRITI Scheduler UI
  RIGHT: Build a SMRITI Automation Status page showing business job outcomes

---

### Category C -- Platform Services (Never replace)

Definition: The internal engines and services that the Platform Engine provides.
These are the reason SMRITI can be built on top of ERPNext without reimplementing
core business logic.

Platform Engine owns and SMRITI never replaces:
- DocType engine
- Workflow engine
- ORM
- Permission engine
- Print engine
- Scheduler
- Hooks and events

Rule: SMRITI must NEVER rewrite Category C services.
SMRITI may EXTEND them via Custom Fields, Hooks, and Custom DocTypes.

---

### Category D -- SMRITI Innovation (Pure SMRITI IP)

Definition: Business intelligence, AI, and retail-specific capabilities that
do not exist in any Platform Engine. This is SMRITI's proprietary value.

SMRITI owns exclusively:
- PSV (Party Stock Visibility / Channel Stock)
- CGE (Customer/Channel Engagement)
- Formula Registry and Explainability Engine
- AI Recommendations and Forecasting
- Inventory Intelligence (Coverage Days, Dead Stock, Reorder Engine)
- Outlet Health Scores
- SMRITI Analytics Studio
- Clienteling
- SFM / SFC (Sales Force Management)

Rule: These modules are SMRITI's competitive differentiation.
They must remain pure SMRITI -- no Platform Engine equivalent exists.

---

### Category E -- Compliance and Accounting Integration

This category has two distinct sub-layers.

#### E1 -- Statutory and GST Compliance

Definition: Government-mandated computations (GST, E-Way Bill, GSTR filings)
that are computed by the Platform Engine or India Compliance app.
SMRITI wraps the VIEW and the trigger. SMRITI never owns the computation.

Rule:
- SMRITI builds the user-facing page (e.g., smriti-grn.html, eway_bill.html)
- The computation happens in the Platform Engine / India Compliance
- SMRITI routes through a SMRITI API -> Repository, not frappe.client directly
- SMRITI never rebuilds a GST computation engine or GSTR filing engine

Examples:
- E-Way Bill (trigger and view in SMRITI, computation in Platform Engine)
- GST Summary view (view in SMRITI, data from Platform Engine)
- Barcode compliance (label printing via SMRITI, computation in Platform Engine)

#### E2 -- Accounting Integration Layer

Definition: SMRITI is the source of validated operational transactions.
Accounting systems are consumers of those transactions.

Architecture:

```
SMRITI
  |
  v
Validated Business Transaction
  |
  v
Accounting Adapter
  |
  +-- TallyPrime
  +-- Busy ERP
  +-- Zoho Books
  +-- QuickBooks
  +-- SAP (future)
```

Rule:
- SMRITI is responsible for: Billing, Purchase, Inventory, Payments (operational)
- Accounting systems are responsible for: General Ledger, Trial Balance, Balance Sheet,
  P&L (statutory), GST Filing, Audit, CA workflows
- SMRITI may display operational financial summaries (Sales Summary, Purchase Summary,
  Inventory Value) for the owner's dashboard -- these are operational views
- SMRITI must NEVER recompute Trial Balance, Balance Sheet, or statutory P&L
- The Accounting Adapter is the only point of contact between SMRITI and accounting systems
- If the accounting system changes (Tally -> Busy -> Zoho), only the adapter changes.
  SMRITI remains identical.

CA and accountant workflows:
- CAs use TallyPrime (or the relevant accounting system)
- CAs do NOT need SMRITI access
- SMRITI sends validated transactions to the accounting system via the adapter
- The accounting system handles all statutory computations and filing

This design gives the retailer freedom: Tally users connect Tally, Busy users connect Busy.
SMRITI is accounting-system-agnostic.

---

## Decision Matrix

| Feature | Category | SMRITI Action |
|---|---|---|
| Business Form (Item, Customer, etc.) | A | Replace with SMRITI Studio (A2) |
| Business List | A | Replace with SMRITI Grid (A2) |
| Dashboard / KPI Cards | A | Replace with SMRITI Dashboard |
| Workspace | A | Replace with SMRITI Home |
| Search | A | Replace with SMRITI Search |
| Operational Reports (Sales, Inventory) | A | SMRITI Reports page |
| Store User Management | A | SMRITI Security Center |
| E-Way Bill, Barcode Compliance | E1 | SMRITI wrapper -- Platform Engine computes |
| GST Summary view | E1 | SMRITI wrapper -- Platform Engine computes |
| Financial Accounting, Ledger, P&L | E2 | Accounting Adapter -> TallyPrime etc. |
| Trial Balance, Balance Sheet | E2 | Accounting system -- SMRITI does not compute |
| DocType | C | Keep |
| Workflow | C | Keep |
| ORM | C | Keep |
| Scheduler | B | Keep |
| Background Jobs | B | Keep -- never wrap in SMRITI UI |
| Error Logs | B | Keep |
| System Console | B | Keep |
| Site Config / Bench | B | Keep |
| PSV, CGE, AI, Formula | D | Pure SMRITI -- no Platform Engine equivalent |

---

## URL Convention

Business page URLs use clean, retailer-friendly bare nouns.
No technical prefixes in URLs that business users see.

| Domain | SMRITI URL | Not |
|---|---|---|
| Items / Products | /products | /app/item |
| Customers | /customers | /app/customer |
| Suppliers | /suppliers | /app/supplier |
| Billing | /billing | /app/sales-invoice |
| Purchase | /purchase | /app/purchase-order |
| Inventory | /inventory | /app/stock-entry |
| Stock Audit | /stock-audit | /app/stock-reconciliation |
| Reports | /reports | /app/query-report |

Internal module naming (not user-facing): customer_studio, item_studio, purchase_studio
Public URL (user-facing): /customers, /items, /purchase

The URL the retailer types must be a word they already use in their business.
Brand is in the page, not in the URL.

---

## What SMRITI Is

SMRITI is a **Retail Operating Platform**.

SMRITI owns: Business Experience, Retail Workflows, Operational Intelligence, Industry Extensions.
Platform Engine owns: Persistence, ORM, Workflow, Scheduler, Permissions, Infrastructure.
Accounting Systems own: Ledger, Statutory Accounting, CA workflows.

SMRITI is NOT:
- An ERPNext customization
- A replacement for TallyPrime
- A General Ledger engine
- A statutory compliance engine

SMRITI IS:
- The complete retail operating system for the store floor, purchase desk, and owner's office
- The single system that runs the business; accounting follows from the transactions SMRITI validates

---

## Architecture Guards

| Guard | Status | What It Protects |
|---|---|---|
| Guard 1 — Persistence Boundary | **Active** (smriti_architecture_guard.py) | No frappe.* DB calls above Repository layer (Python) |
| Guard 2 — Navigation Boundary | Planned | No /app/* or /desk/* in any SMRITI page |
| Guard 3 — UI Vocabulary Boundary | Planned | No DocType/Workspace/Repository in user-facing text |
| Guard 4 — Brand Boundary | Planned | No Platform Engine branding in page titles or footers |
| Guard 5 — UX Boundary | Planned | Mandatory Search/Save/Cancel/Breadcrumb on every screen |
| Guard 6 — UI Persistence Boundary | **Active (Warning Mode)** | No frappe.* in www/ JS/HTML; no frappe.* outside core/platform/ in Python |

**Guard 6 progression plan:**
- Phase 1 (current): Warning only — 2,348 violations tracked as migration baseline
- Phase 2 (after 50% migration cleared): Fail new violations only
- Phase 3 (after 90% migration cleared): Fail all remaining violations

## SMRITI Core Framework — Canonical API

The SMRITI Core Framework (`smriti_retail_os/core/`) is the canonical platform abstraction.

**Business code always uses the Framework API:**
```python
from smriti_retail_os import smriti

smriti.documents.get("Customer", name)      # never: frappe.get_doc(...)
smriti.db.get("Customer", name, "field")    # never: frappe.db.get_value(...)
smriti.cache.get_or_set("key", builder)     # never: frappe.cache().get_value(...)
smriti.events.publish("smriti:event", data) # never: frappe.publish_realtime(...)
smriti.jobs.enqueue("module.function", ...)  # never: frappe.enqueue(...)
```

**`smriti.core.platform` is the adapter layer — internal only.** Business modules never import it directly.
Model registry: `core/platform/document_map.yaml` — add a YAML entry to map any new SMRITI model.
Implementation: `docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md`

---

## Terminology Standard

| Use This | Not This |
|---|---|
| Platform Engine | ERPNext (in architecture documents) |
| Platform Engine (currently ERPNext + Frappe) | ERPNext (in architecture documents) |
| Accounting Adapter | Tally integration (implies only one target) |
| Repository Layer | frappe.db calls (in architecture documents) |
| Item / Product | DocType (in user-facing text) |
| Bill | Sales Invoice (in user-facing text) |
| Customer | Party (in user-facing text) |

---

*SMRITI Platform Vision v2.0.0*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Status: LOCKED*
