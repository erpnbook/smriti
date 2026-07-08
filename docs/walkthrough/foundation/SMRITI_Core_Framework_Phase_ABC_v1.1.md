# SMRITI Core Framework — Phase A+B+C Walkthrough

**Area:** Foundation
**Date:** 2026-07-08
**Author:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Status:** Completed
**Commit:** b695824 (Phase A+B+C) + follow-up (Experience Constitution + core/__init__.py)
**Prerequisite:** SMRITI Core Framework v1.0 (commit 9915cdb) — Platform Adapter Layer

---

## 1. Purpose

Three deliverables in one session:

| Phase | What | Why |
|---|---|---|
| A — Governance | 8 governance documents updated | Implementation must follow governance, not become it |
| B — Framework API | `smriti.py` public surface | Business code must never import `smriti.core.platform` directly |
| C — Form Engine | `core/forms/` — full engine + 4 retail presets | Detach UX from platform form widgets |

---

## 2. Phase A — Governance Alignment

### Documents Updated

| Document | Change |
|---|---|
| `ARCHITECTURE.md` | §15 expanded: full layer diagram, canonical Python+JS patterns, Core Framework module table, Guard 6 progression plan |
| `SMRITI_PLATFORM_VISION.md` | Guard 6 → Active (Warning Mode); SMRITI Core Framework canonical API section added |
| `SMRITI_PRODUCT_CONSTITUTION.md` | **SPC-012 Platform Adapter Boundary** — Critical severity, constitutional law |
| `SMRITI_EXPERIENCE_CONSTITUTION.md` | Compliance section: Guard 1+6 both listed Active; checklist updated to `smriti.api.*` patterns |
| `.agents/AGENTS.md` | **Mandatory Core Framework Rule** — Python and JavaScript, with code examples |
| `CONTRIBUTING.md` | Platform Adapter Rule section with correct/forbidden patterns + YAML model registry guide |
| `CODE_OF_CONDUCT.md` | Technical standards: no `frappe.*` outside `core/platform/` |
| `ARCHITECTURE_MIGRATION_BACKLOG.md` | Guard 6 progression plan + migration priority table with estimated file counts |

### SPC-012 — key text

```
No SMRITI service, studio, API file, or www/ page may call frappe.* platform APIs directly.
All platform access must route through the SMRITI Core Framework (smriti_retail_os/core/platform/).
Business modules use the SMRITI Framework API (from smriti_retail_os import smriti).
```

### Guard 6 progression plan (now in all relevant docs)

| Phase | Trigger | Mode |
|---|---|---|
| Phase 1 (current) | Baseline established | Warning only — 2,348 violations, no build failures |
| Phase 2 | 50% cleared | Fail new violations only |
| Phase 3 | 90% cleared | Full enforcement |

---

## 3. Phase B — SMRITI Framework API

### New file: `smriti_retail_os/smriti.py`

One clean import for all business code:

```python
from smriti_retail_os import smriti

# These are now the canonical patterns (SPC-012):
customer = smriti.documents.get("Customer", "CUST-001")
value    = smriti.db.get("Customer", "CUST-001", "credit_limit")
cached   = smriti.cache.get_or_set("key", lambda: build(), ttl=300)
smriti.events.publish("smriti:stock_update", {"item": "ITEM-001"})
smriti.jobs.enqueue("smriti_retail_os.services.sync.run", company="SM")
smriti.permissions.require("Purchase", "create")
smriti.errors.raise_validation("Required", "Please fill in the Supplier field.")

# Form Engine (Phase C):
from smriti_retail_os import smriti
schema = smriti.forms.SmritiForm
```

### Architecture impact

```
Business Studio / Service
        │
        ▼   from smriti_retail_os import smriti       ← Phase B: this file
            smriti.documents.get(...)
SMRITI Framework API  (smriti_retail_os/smriti.py)
        │
        ▼   delegates to →
SMRITI Core Platform Adapter  (core/platform/)        ← Phase 1 (v1.0)
        │
        ▼
Frappe ORM / ERPNext
```

`smriti.core.platform` is now explicitly marked **internal only** in `core/__init__.py`.

---

## 4. Phase C — SMRITI Form Engine

### Files created

| File | Lines | Purpose |
|---|---|---|
| `core/forms/__init__.py` | 20 | Replaces stub; exports all public classes |
| `core/forms/field.py` | 210 | 12 field types + SectionBreak |
| `core/forms/validator.py` | 210 | ValidationResult + FormValidator + ValidationRule factories |
| `core/forms/form_engine.py` | 185 | SmritiForm base class |
| `core/forms/lifecycle.py` | 165 | FormLifecycle hook protocol |
| `core/forms/retail_forms/__init__.py` | 10 | Retail forms package |
| `core/forms/retail_forms/purchase_form.py` | 200 | Reference implementation |
| `core/forms/retail_forms/customer_form.py` | 40 | Customer form |
| `core/forms/retail_forms/product_form.py` | 55 | Product/Item master form |
| `core/forms/retail_forms/grn_form.py` | 100 | Goods Receipt Note form |

### Field types

```python
TextField / TextAreaField
NumberField / CurrencyField
DateField / DateTimeField
SelectField / LookupField    ← resolves SMRITI model → DocType via registry
TableField                   ← child table with typed columns
CheckboxField
BarcodeField / ImageField
SectionBreak                 ← visual grouping (not a data field)
```

### Validation

```python
from smriti_retail_os.core.forms.validator import ValidationResult, ValidationRule

# Field-level (automatic — declared on SmritiField)
TextField("supplier", "Supplier", required=True, max_length=140)
NumberField("qty", "Qty", required=True, min_value=0.001, precision=3)

# Custom rules (added in SmritiForm._extra_rules())
ValidationRule.custom("schedule_date",
    lambda v, d: (v >= d["transaction_date"], "Required By must be after Order Date"))

ValidationRule.global_rule(
    lambda d: "Total must be > 0." if float(d.get("grand_total") or 0) <= 0 else None)

ValidationRule.regex("gstin", "GSTIN",
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
    "Invalid GSTIN format.")
```

### Lifecycle hooks

```python
class MyLifecycle(FormLifecycle):
    def on_load(self, name): ...          # enrich data when opening
    def on_change(self, field, val, data): ...  # dependent field updates
    def on_before_save(self, data): ...   # final validation gate
    def on_after_save(self, doc): ...     # cache clear, realtime events
    def on_before_submit(self, data): ... # submit guard
    def on_after_submit(self, doc): ...   # post-submit notifications
```

### SmritiForm usage

```python
from smriti_retail_os.core.forms.retail_forms.purchase_form import PurchaseForm

form = PurchaseForm()

# Get serializable schema (for JS renderer, Phase D)
schema = form.schema()
# → {"model": "Purchase", "title": "Purchase Order", "fields": [...16 fields...]}

# Validate without saving
result = form.validate(data)
if not result.ok:
    print(result.errors)       # {field_name: [error_messages]}
    print(result.global_errors)

# Load existing document with lifecycle enrichments
doc_data = form.load("PO-2026-00001")

# Save (validate → get/new → update → save → on_after_save)
saved = form.save(data)

# Submit (lifecycle gate → submit → on_after_submit)
submitted = form.submit({"name": "PO-2026-00001"})
```

### PurchaseForm — reference implementation

Demonstrates every Form Engine capability:
- 16 fields across 4 `SectionBreak` groups
- `LookupField` for Supplier (resolves to "Supplier" DocType via registry)
- `TableField` with 8 typed columns for order items
- `_PurchaseLifecycle`: supplier auto-fills payment terms; items + total validated
- Custom `ValidationRule` for date ordering and non-zero total
- `on_after_save`: cache invalidation + `smriti:purchase_saved` realtime event
- `on_before_submit`: status guard (Draft/Rejected cannot be submitted)
- `on_after_submit`: `smriti:purchase_posted` realtime event

---

## 5. Tests

```
PASS: TextField, to_dict()
PASS: ValidationResult field error
PASS: _is_empty helper
PASS: ValidationRule.required
PASS: FormValidator required + min_value checks
PASS: FormLifecycle default hooks
PASS: SmritiForm.schema()
PASS: PurchaseForm.schema() — 16 fields
PASS: PurchaseForm.validate() rejects empty items
PASS: PurchaseForm field-level validation with valid data, ok= True
=== ALL FORM ENGINE TESTS PASSED ===
```

No Frappe runtime required for these tests — field types, validation, and schema generation are pure Python.

---

## 6. What is now in place

```
smriti_retail_os/
├── smriti.py                          ← Phase B: THE public API
├── core/
│   ├── __init__.py                    ← Updated: preferred/internal/framework import guide
│   ├── platform/                      ← Phase 1: 8 Frappe adapters (internal only)
│   │   ├── documents.py
│   │   ├── db.py / cache.py / events.py / jobs.py
│   │   ├── permissions.py / errors.py
│   │   └── document_map.yaml          ← 39 SMRITI model registrations
│   ├── documents/                     ← SmritiDocument + mixins
│   ├── services/                      ← BaseService contract
│   └── forms/                         ← Phase C: Form Engine
│       ├── field.py                   ← 12 field types
│       ├── validator.py               ← ValidationResult + FormValidator
│       ├── form_engine.py             ← SmritiForm base class
│       ├── lifecycle.py               ← FormLifecycle hooks
│       └── retail_forms/
│           ├── purchase_form.py       ← Reference implementation (16 fields)
│           ├── customer_form.py
│           ├── product_form.py
│           └── grn_form.py
```

---

## 7. Known Limitations

- JS Form Renderer deferred to Phase D — `form.schema()` produces the dict, but rendering is still done by each `www/` page manually
- `SmritiDocument` does not yet wrap `.append()` for child table manipulation (workaround: access `.raw.append()`)
- Guard 6 is warning-only — 2,348 pre-existing violations in migration backlog

---

## 8. Next Steps (Phase D)

1. **JS Form Renderer** — `smriti.forms.render(schema, '#container')` — reads `form.schema()` output and builds the UI without platform widgets
2. **Migrate `services/`** — 21 files, ~450 violations; use `BaseService` + `smriti.*` patterns
3. **Core API endpoints** — `smriti_retail_os/core/api.py` — whitelisted `smriti.api.get/getList/save/delete` backend routes for the JS adapter
4. **Guard 6 Phase 2** — after 50% migration cleared, switch from warning to "fail new violations"

---

## 9. Related Documents

- `SPC-012` — `SMRITI_PRODUCT_CONSTITUTION.md`
- `ARCHITECTURE.md §15` — Canonical layer model + patterns
- `docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md` — Platform Adapter Layer walkthrough
- `ARCHITECTURE_MIGRATION_BACKLOG.md` — Guard 6 progression plan
