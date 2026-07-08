# SMRITI Core Framework — Walkthrough v1.0

**Area:** Foundation
**Date:** 2026-07-08
**Author:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Status:** Completed
**Related Plan:** `docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md`

---

## 1. Purpose

Establish the SMRITI Core Framework — a formal Python `core/` package and JavaScript adapter layer that isolates all Frappe/ERPNext platform dependencies behind a single, replaceable abstraction. This is the foundational infrastructure that all future SMRITI studios will build on top of.

---

## 2. Scope

- 24 new files created (`core/` package + JS adapter)
- 6 files modified (4 repositories + hooks.py + architecture guard)
- Phase 0 audit: 266 production files / 3,380 lines of direct platform coupling measured and recorded as migration baseline

---

## 3. Files Created

| File | Description |
|---|---|
| `core/__init__.py` | SMRITI Core Framework root namespace |
| `core/platform/__init__.py` | Platform adapter public API |
| `core/platform/registry.py` | YAML-driven model → DocType resolver |
| `core/platform/document_map.yaml` | 35-entry SMRITI business model registry |
| `core/platform/documents.py` | Document CRUD adapter |
| `core/platform/db.py` | Database query adapter |
| `core/platform/cache.py` | Redis cache adapter with get_or_set pattern |
| `core/platform/events.py` | Realtime events adapter |
| `core/platform/jobs.py` | Background jobs adapter |
| `core/platform/permissions.py` | Permissions adapter with shortcut helpers |
| `core/platform/errors.py` | HREP-compliant error adapter |
| `core/documents/__init__.py` | Documents layer namespace |
| `core/documents/base_document.py` | SmritiDocument base class |
| `core/documents/mixins.py` | AuditMixin, WorkflowMixin, PermissionMixin |
| `core/services/__init__.py` | Services layer namespace |
| `core/services/base_service.py` | BaseService contract |
| `core/forms/__init__.py` | Reserved stub — Phase 3 |
| `core/reports/__init__.py` | Reserved stub — Phase 4 |
| `core/navigation/__init__.py` | Reserved stub — Phase 3 |
| `core/themes/__init__.py` | Reserved stub — Phase 3 |
| `core/print/__init__.py` | Reserved stub — Phase 4 |
| `core/email/__init__.py` | Reserved stub — Phase 4 |
| `core/components/__init__.py` | Reserved stub — Phase 3 |
| `public/js/smriti_core.js` | Full JS adapter (smriti.api / notify / dialog / navigation / events / context) |

---

## 4. Files Modified

| File | Change |
|---|---|
| `hooks.py` | `smriti_core.js` added as first `app_include_js` entry |
| `repositories/company_repository.py` | Migrated from `frappe.*` → `core.platform` |
| `repositories/lookup_repository.py` | Migrated from `frappe.*` → `core.platform` |
| `repositories/pos_profile_repository.py` | Migrated from `frappe.*` → `core.platform` |
| `repositories/security_repository.py` | Migrated from `frappe.*` → `core.platform` |
| `smriti_architecture_guard.py` | Guard 6 added (UI Persistence Boundary, warning mode) |

---

## 5. Architecture Decisions

### AD-1: YAML Registry (not Python dict)
Document model mapping lives in `core/platform/document_map.yaml`, not a Python dict. This means platform DocType names can be updated without touching Python code. The registry is hot-reloadable via `registry.reload()`.

### AD-2: Warning Mode for Guard 6
Guard 6 (UI Persistence Boundary) runs in warning mode — it reports violations but never fails the build. This is correct because 266 existing files have legacy `frappe.*` calls. The guard measures and reports; migration happens progressively.

### AD-3: Repositories Migrated First
Repositories are the lowest-risk layer (small files, already isolated by design). Migrating them first gives a working reference implementation before touching high-risk files like `billing_api.py` or `transaction_kernel.py`.

### AD-4: `resolve_or_passthrough` for LookupRepository
`LookupRepository` operates across many DocTypes by name. It uses `resolve_or_passthrough()` to handle both registered SMRITI model names and legacy raw DocType names during the migration window.

---

## 6. Design Rationale

The `purchase_studio/adapter/erp_adapter.py` (94 lines, pre-existing) already followed the correct pattern — all platform calls isolated in one file. This walkthrough generalises that pattern to the entire codebase via `core/platform/`.

The JavaScript adapter (`smriti_core.js`) follows the same principle: `smriti.api.call()` wraps `frappe.call()`, `smriti.notify.*` wraps `frappe.show_alert()`, `smriti.navigation.go()` replaces `frappe.set_route()` — and Guard 6 enforces the new convention on all new `www/` pages.

---

## 7. Implementation Summary

**Phase 0** — Ran real audit before writing any code:
- Python: 266 files, 3,380 direct platform-coupled lines (production only)
- JS/HTML: 46 files with `frappe.call`, 36 with `frappe.client`

**Phase 1** — Built `core/` Python package (11 active modules + 7 reserved stubs)

**Phase 2** — Built `public/js/smriti_core.js` (6 adapter namespaces), registered in `hooks.py`

**Phase 3** — Migrated 4 repository files (reference implementation)

**Phase 4** — Added Guard 6 to `smriti_architecture_guard.py`

**Phase 5** — Documentation (this walkthrough + implementation plan + index updates)

---

## 8. Tests Executed

```bash
# Verify files created
Get-ChildItem D:\Smriti_Retail_OS\smriti_retail_os\core -Recurse | Measure-Object

# Verify no frappe.* imports in migrated repositories
Select-String -Path "D:\Smriti_Retail_OS\smriti_retail_os\repositories\*.py" -Pattern "import frappe"

# Verify Guard 6 function exists
Select-String -Path "D:\Smriti_Retail_OS\smriti_architecture_guard.py" -Pattern "guard_6_ui_persistence"

# Verify smriti_core.js registered in hooks
Select-String -Path "D:\Smriti_Retail_OS\smriti_retail_os\hooks.py" -Pattern "smriti_core.js"
```

---

## 9. Verification Results

| Check | Result |
|---|---|
| `core/` package created with 24 files | Done |
| `document_map.yaml` has 35 registered models | Done |
| 4 repositories migrated — no `import frappe` remaining | Done |
| `smriti_core.js` registered first in `app_include_js` | Done |
| Guard 6 function `guard_6_ui_persistence()` exists | Done |
| Guard 6 runs in both `--report` and default ratchet mode | Done |

Full git diff evidence appended in verification run (see AGENTS.md Rule 1).

---

## 10. Known Limitations

- 266 Python files and 46 JS files still call `frappe.*` directly — tracked in `ARCHITECTURE_MIGRATION_BACKLOG.md`
- `core/forms/`, `core/reports/`, `core/navigation/`, `core/print/`, `core/email/`, `core/components/` are stubs only
- `SmritiDocument` does not yet wrap child table operations (`.append()`, child `.save()`)
- Guard 6 Python scan may be slow on large repos — consider caching in future

---

## 11. Future Work

| Phase | Scope | Priority |
|---|---|---|
| Phase 2 migration | `services/` (21 files) | High |
| Phase 3 migration | `*_studio/api/` (~30 files) | High |
| Phase 4 migration | `billing_api.py`, `item_master_api.py`, `reports_api.py` | Critical |
| Phase 5 migration | `transaction_kernel.py`, `setup.py` | Critical |
| `core/forms/` | SMRITI Form Engine | Phase 3 |
| `core/reports/` | SMRITI Report Studio | Phase 4 |
| Guard 6 → Error Mode | After all www/ pages migrated | Post Phase 3 |
| `smriti.api.get/getList/save/delete` backend routes | `core/api.py` whitelisted methods | Next sprint |

---

## 12. Related ADRs

- Architecture Constitution Rule 2 — Service-First Design (`ARCHITECTURE.md §5`)
- SMRITI Platform Vision v2.0.0 — Golden Rule (`SMRITI_PLATFORM_VISION.md`)
- Category A1 → A2 migration pattern (`SMRITI_PLATFORM_VISION.md §A`)

---

## 13. Related RFCs

- SMRITI Core Framework RFC — approved by Jawahar R. Mallah, 2026-07-08
- Implementation Plan: `docs/implementation/foundation/SMRITI_Core_Framework_v1.0.md`
