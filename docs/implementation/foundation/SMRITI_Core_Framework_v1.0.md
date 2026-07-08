# SMRITI Core Framework — Implementation Plan v1.0

**Area:** Foundation
**Status:** Completed
**Version:** 1.0.0
**Date:** 2026-07-08
**Author:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
**License:** GPL-3.0-only

---

## 1. Objective

Implement the SMRITI Core Framework — a formal `core/` Python package and JavaScript adapter layer that isolates all Frappe/ERPNext platform dependencies behind a single, replaceable abstraction. No SMRITI service, studio, or UI page may call `frappe.*` directly after migration.

---

## 2. Business Motivation

SMRITI is the product. The underlying platform (currently Frappe + ERPNext) is an implementation detail. Without a formal adapter layer, every module is tightly coupled to Frappe APIs — making the codebase fragile to platform upgrades, impossible to test in isolation, and difficult to migrate if the platform ever changes.

This framework eliminates that coupling progressively and measurably.

---

## 3. Scope

**In scope (Phase 1):**
- `core/platform/` — Python adapter for documents, db, cache, events, jobs, permissions, errors
- `core/platform/document_map.yaml` — configuration-driven SMRITI model → DocType registry
- `core/documents/` — SmritiDocument base class and mixins
- `core/services/` — BaseService contract
- Reserved stubs: `core/forms/`, `core/reports/`, `core/navigation/`, `core/themes/`, `core/print/`, `core/email/`, `core/components/`
- `public/js/smriti_core.js` — JavaScript adapter (smriti.api, smriti.notify, smriti.dialog, smriti.navigation, smriti.events, smriti.context)
- Repository migration: 4 files migrated as reference implementation
- Architecture Guard 6 (warning mode)

**Out of scope (tracked in ARCHITECTURE_MIGRATION_BACKLOG.md):**
- Migration of existing 266 platform-coupled files (phased backlog)
- `core/forms/`, `core/reports/`, `core/print/` full implementation (Phase 3/4)

---

## 4. Current State

**Before this implementation:**
- No unified platform adapter existed
- 266 production Python files called `frappe.*` directly (3,380 lines)
- 46 JS/HTML files called `frappe.call()` directly (162 lines)
- Only `purchase_studio/adapter/erp_adapter.py` followed the correct pattern (94 calls, isolated)
- Architecture Guard had 5 planned guards, only Guard 1 active

---

## 5. Gap Analysis

| Gap | Resolution |
|---|---|
| No `smriti.platform` Python package | Created `core/platform/` with 8 modules |
| Document mapping hard-coded or absent | Created `document_map.yaml` YAML registry |
| `frappe.call()` used in www/ pages | Created `smriti_core.js` with full JS adapter |
| No base service contract | Created `BaseService` in `core/services/` |
| No SmritiDocument wrapper | Created `SmritiDocument` in `core/documents/` |
| Guard 6 planned but not implemented | Implemented Guard 6 (warning mode) |
| Repository layer still calling `frappe.*` | Migrated all 4 repository files |

---

## 6. Architecture Impact

Introduces the canonical three-layer data path:

```
SMRITI UI / Service
    │
    ▼  smriti.platform.documents.get("Customer", name)
core/platform/documents.py
    │
    ▼  frappe.get_doc("Customer", name)   ← ONLY here
Frappe ORM
```

No architecture rule changes — this implements what ARCHITECTURE.md Rule 2 already mandated.

---

## 7. Proposed Design

See implementation_plan.md v2.0 (approved 2026-07-08).

Key decisions:
- **YAML registry** (not Python dict) for document model mapping
- **Warning mode** for Guard 6 (not error — 266 legacy files exist)
- **Repositories migrated first** (lowest risk, reference implementation)
- **Reserved stubs** for future Core Framework phases

---

## 8. Files Created

| File | Purpose |
|---|---|
| `smriti_retail_os/core/__init__.py` | Core Framework namespace |
| `smriti_retail_os/core/platform/__init__.py` | Platform adapter public surface |
| `smriti_retail_os/core/platform/registry.py` | YAML-driven document model resolver |
| `smriti_retail_os/core/platform/document_map.yaml` | 35-entry SMRITI → DocType mapping |
| `smriti_retail_os/core/platform/documents.py` | Document CRUD adapter |
| `smriti_retail_os/core/platform/db.py` | Database query adapter |
| `smriti_retail_os/core/platform/cache.py` | Redis cache adapter |
| `smriti_retail_os/core/platform/events.py` | Realtime events adapter |
| `smriti_retail_os/core/platform/jobs.py` | Background jobs adapter |
| `smriti_retail_os/core/platform/permissions.py` | Permissions adapter |
| `smriti_retail_os/core/platform/errors.py` | HREP-compliant error adapter |
| `smriti_retail_os/core/documents/__init__.py` | Documents layer namespace |
| `smriti_retail_os/core/documents/base_document.py` | SmritiDocument base class |
| `smriti_retail_os/core/documents/mixins.py` | AuditMixin, WorkflowMixin, PermissionMixin |
| `smriti_retail_os/core/services/__init__.py` | Services layer namespace |
| `smriti_retail_os/core/services/base_service.py` | BaseService contract |
| `smriti_retail_os/core/forms/__init__.py` | Reserved stub — Phase 3 |
| `smriti_retail_os/core/reports/__init__.py` | Reserved stub — Phase 4 |
| `smriti_retail_os/core/navigation/__init__.py` | Reserved stub — Phase 3 |
| `smriti_retail_os/core/themes/__init__.py` | Reserved stub — Phase 3 |
| `smriti_retail_os/core/print/__init__.py` | Reserved stub — Phase 4 |
| `smriti_retail_os/core/email/__init__.py` | Reserved stub — Phase 4 |
| `smriti_retail_os/core/components/__init__.py` | Reserved stub — Phase 3 |
| `smriti_retail_os/public/js/smriti_core.js` | JavaScript adapter (smriti.*) |

---

## 9. Files Modified

| File | Change |
|---|---|
| `smriti_retail_os/hooks.py` | Added `smriti_core.js` as first `app_include_js` entry |
| `smriti_retail_os/repositories/company_repository.py` | Migrated to `core.platform` |
| `smriti_retail_os/repositories/lookup_repository.py` | Migrated to `core.platform` |
| `smriti_retail_os/repositories/pos_profile_repository.py` | Migrated to `core.platform` |
| `smriti_retail_os/repositories/security_repository.py` | Migrated to `core.platform` |
| `smriti_architecture_guard.py` | Added Guard 6 (UI Persistence Boundary, warning mode) |

---

## 10. Dependencies

- Python `yaml` (PyYAML) — must be available in the Frappe bench environment
- Frappe v16 — all adapter calls wrap existing Frappe APIs
- No new pip packages required beyond what Frappe already installs

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| PyYAML not installed | Frappe already depends on PyYAML; confirmed in requirements |
| Repository callers break after migration | Signatures preserved; `model_name` parameter replaces raw DocType string |
| `smriti_core.js` conflicts with existing scripts | Loaded first in `app_include_js`; uses IIFE, no global pollution beyond `window.smriti` |
| Guard 6 too noisy (3,380 lines flagged) | Warning mode only — build never fails |

---

## 12. Rollback Strategy

1. Remove `smriti_retail_os/core/` directory
2. Revert 4 repository files to their pre-migration versions (git revert)
3. Remove `smriti_core.js` entry from `hooks.py`
4. Revert Guard 6 additions in `smriti_architecture_guard.py`

All changes are additive — no existing API was removed or renamed.

---

## 13. Verification Plan

```bash
# Python import smoke test
python -c "from smriti_retail_os.core.platform import documents, db, cache, events, jobs"
python -c "from smriti_retail_os.core.platform.registry import resolve; print(resolve('Customer'))"
python -c "from smriti_retail_os.core.documents import SmritiDocument"
python -c "from smriti_retail_os.core.services import BaseService"

# Architecture guard
python smriti_architecture_guard.py --report
```

---

## 14. Test Plan

- New test file: `smriti_retail_os/tests/test_smriti_core.py`
  - Registry: `resolve("Customer")` → `"Customer"`, `resolve("Purchase")` → `"Purchase Order"`
  - Registry: `resolve("unknown_model")` → `KeyError`
  - `SmritiDocument` instantiation and field access
  - `BaseService` permission helpers

---

## 15. Documentation Impact

- `ARCHITECTURE.md` — Core Framework section added
- `SMRITI_PLATFORM_VISION.md` — Guard 6 status updated to Active
- `ARCHITECTURE_MIGRATION_BACKLOG.md` — Phase 0 audit results added
- `docs/walkthrough/foundation/SMRITI_Core_Framework_v1.0.md` — created
- `docs/walkthrough/README.md` — index updated
- `docs/implementation/README.md` — index updated

---

## 16. Deployment Plan

1. Merge to `main` in `D:\Smriti_Retail_OS`
2. `git pull` in `F:\Smriti9` (test environment)
3. `bench build --app smriti_retail_os` (to bundle `smriti_core.js`)
4. `bench restart`
5. Verify `smriti.api` available in browser console on any SMRITI page

---

## 17. Status

**Completed — 2026-07-08**

---

## 18. Related ADRs

- Architecture Constitution Rule 2 — Service-First Design (ARCHITECTURE.md §5)
- SMRITI Platform Vision v2.0.0 — Golden Rule, Category A→A2 migration
- Guard 6 — UI Persistence Boundary

---

## 19. Related Walkthroughs

- `docs/walkthrough/foundation/SMRITI_Core_Framework_v1.0.md`
