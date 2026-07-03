# SMRITI Platform Vision

> **Status:** LOCKED — v1.0.0
> **Authority:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to:** All Developers, Contributors, AI Agents, Automation Systems
> **Purpose:** This document defines what SMRITI is. Read it before writing any code, architecture, or recommendation for this project.

---

## The Single Most Important Sentence

> **SMRITI is the product. The Platform Engine is an internal implementation detail.**

---

## Rule 0 -- Business Experience Boundary

This is the foundation rule. Every other rule derives from it.

```
Business User
      |
      v
   SMRITI
      |
      v
Platform Engine
```

Never:

```
Business User
      |
      v
Platform Engine   <-- THIS MUST NEVER HAPPEN
```

A business user must never interact with the Platform Engine directly -- not through a URL, a form, a list view, a workspace, a report, a print format, or any other surface.

If a feature is not yet available in SMRITI, the correct response is a SMRITI "Coming Soon" page -- never a Frappe Desk fallback.

---

## What SMRITI Is

SMRITI is a **Retail Operating Platform** -- a complete business experience layer for retail, distribution, and wholesale operations.

SMRITI owns:

| Domain | What It Means |
|---|---|
| **UI** | Every screen, layout, and visual element a business user sees |
| **UX** | Every workflow, interaction pattern, and navigation path |
| **Pages** | Every URL the business user visits (/smriti, /billing, /stock-center, etc.) |
| **Forms** | Every create/edit/view form for any business entity |
| **Navigation** | Every sidebar, breadcrumb, tab, and menu |
| **Search** | Every search bar, filter panel, and autocomplete |
| **Reports** | Every business report, dashboard, and KPI view |
| **Dashboard** | Every summary card, chart, and alert |
| **Theme** | Every colour, font, spacing, and design token |
| **Brand** | Every logo, label, title, and product name shown to a user |
| **Business Experience** | The complete end-to-end operational journey of any retail role |
| **Retail Workflows** | POS, Purchase, Inventory, PSV, Clienteling, SFM, etc. |
| **Operational Intelligence** | Reorder recommendations, health scores, coverage days, etc. |

---

## What the Platform Engine Is

The Platform Engine is the **internal application engine** that SMRITI uses for persistence, document management, and infrastructure.

**Current Platform Engine:** ERPNext v16 + Frappe v16

The Platform Engine owns:

| Domain | What It Means |
|---|---|
| **Persistence** | Database reads and writes (via ORM only, through the Repository layer) |
| **ORM** | Document lifecycle (frappe.get_doc, frappe.new_doc, frappe.save) |
| **Workflow** | Document approval flows |
| **Scheduler** | Background jobs and cron hooks |
| **Permissions** | Role-based access control engine |
| **Hooks** | Event triggers (on_submit, on_cancel, etc.) |
| **Print Engine** | PDF generation for invoices and reports |
| **Infrastructure** | Redis, MariaDB, Celery, socket.io |

The Platform Engine does **not** own:
- Any URL a business user sees
- Any form a business user fills in
- Any report a business user reads
- Any navigation a business user follows

---

## Architecture Model

```
SMRITI Retail OS (Product)
         |
    +-----------+
    |           |
  Pages    Components
  (www/)   (public/)
    |           |
    +-----+-----+
          |
      API Layer
   (smriti_*_api.py)
          |
    Service Layer
   (smriti_*_service.py)
          |
  Repository / Adapter Layer
   (smriti_*_repository.py)
          |
  Platform Engine (ERPNext + Frappe)
          |
      Database
```

**The Repository/Adapter layer is the only point of contact with the Platform Engine.**

No layer above it may call frappe.get_doc, frappe.new_doc, frappe.db.sql, frappe.db.set_value, frappe.db.commit, frappe.db.delete, or frappe.delete_doc directly.

---

## Terminology Standard

| Use This | Not This | Reason |
|---|---|---|
| **Platform Engine** | ERPNext | SMRITI's identity must not depend on the engine name |
| **SMRITI Item Studio** | ERPNext Item Form | SMRITI owns the experience |
| **SMRITI Billing** | ERPNext Sales Invoice | SMRITI owns the experience |
| **Repository Layer** | frappe.db calls | Abstracts the engine |
| **Platform Engine (currently ERPNext/Frappe)** | "ERPNext" in architecture docs | Makes future engine changes non-breaking |

In all architecture documents and AI prompts, write:

```
Platform Engine (currently ERPNext + Frappe)
```

not:

```
ERPNext
```

---

## Studio Model

Every business domain in SMRITI is represented as a **Studio** -- a complete, self-contained business workspace.

A Studio provides:
- A dedicated SMRITI URL (e.g. /item-studio, /billing-center, /stock-center)
- A product list (Grid)
- A detail view (Drawer)
- A create/edit form (Form Engine)
- Search and filters (Toolbar)
- Actions and validation (via Service Layer)
- Persistence (via Repository Layer -> Platform Engine)

Studios do **not**:
- Expose any Platform Engine form
- Navigate to any /app/* or /desk/* URL
- Call frappe.new_doc or frappe.get_doc from the UI layer

---

## Architecture Guards

These automated checks enforce the platform boundary:

| Guard | Status | What It Protects |
|---|---|---|
| **Guard 1 -- Persistence Boundary** | Active (smriti_architecture_guard.py) | No DB calls above the Repository layer |
| **Guard 2 -- Navigation Boundary** | Planned | No /app/* or /desk/* in UI code |
| **Guard 3 -- UI Vocabulary Boundary** | Planned | No DocType/Workspace/Kernel exposed to users |
| **Guard 4 -- Brand Boundary** | Planned | No "ERPNext" in page titles, footers, or labels |
| **Guard 5 -- UX Boundary** | Planned | Mandatory Search/Save/Cancel/Breadcrumb on every screen |

All guards use the ratchet approach: they pass against today's codebase, fail only if someone makes things worse. The backlog can only shrink.

---

## What This Document Is For

This document exists to answer one question for any developer, architect, or AI agent working on SMRITI:

> "Who owns this?"

If the answer is "the business user experiences it" -- SMRITI owns it.
If the answer is "it stores or retrieves data" -- the Platform Engine owns it, accessed only through the Repository layer.

Any decision that blurs this line weakens SMRITI as a product and increases the cost of future Platform Engine changes.

---

## What This Document Is Not

This document is **not** an ERPNext customization guide.

SMRITI is **not** an ERPNext customization.

SMRITI is a product that uses ERPNext as its current Platform Engine.

Any future development -- features, studios, reports, workflows -- must reinforce this identity, not weaken it.

---

*SMRITI Platform Vision v1.0.0*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Status: LOCKED*
