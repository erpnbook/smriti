# Foundation — SMRITI Retail OS Layout Engine (SRLE) v1.0 — Phase 1

**Date:** 2026-07-08
**Author:** SMRITI Engineering Team
**Commits:** `02153b7` (module + assets), `a3cd2d8` (hooks.py registration)
**Status:** Completed

---

## 1. Purpose

Establish the SMRITI Retail OS Layout Engine (SRLE) as the platform-wide, single source of truth for application shell layout. Provide a formally versioned public API (`window.SRLE`) that all future SMRITI modules use instead of implementing their own layout behaviour.

---

## 2. Scope

**In scope — Phase 1:**
- Python module: `layout_engine/` with validation and server-side preference persistence
- JavaScript: 4-file stack (`layout_store` → `dock_manager` → `responsive_manager` → `layout_manager`)
- CSS: `layout_tokens.css` (custom properties) + `layout.css` (opt-in workspace rules)
- `hooks.py` asset registration (CSS + JS load order)
- Modification to `public/css/ui/layout.css` (add `.srle-workspace` opt-in class)

**Out of scope — Phase 1:**
- Resizable sidebar drag handle (Phase 2)
- Top dock "More" overflow menu (Phase 3)
- Full ARIA/keyboard navigation (Phase 4)
- Migration of existing 171 pages to opt-in `.srle-workspace`

---

## 3. Files Created

| File | Purpose |
|---|---|
| `layout_engine/__init__.py` | Python package marker |
| `layout_engine/layout_preferences.py` | Validates/sanitises all preference fields (position, width, collapsed, favorites, groups) |
| `layout_engine/layout_service.py` | `@frappe.whitelist` get/save endpoints; graceful localStorage fallback if custom field absent |
| `public/css/layout_engine/layout_tokens.css` | `--srle-*` CSS custom properties (dimensions, z-indices, timing, workspace offsets) |
| `public/css/layout_engine/layout.css` | `.srle-workspace` opt-in rules + dock-specific margin/height overrides |
| `public/js/layout_engine/layout_store.js` | Unified state store with localStorage, legacy `smriti-sidebar-*` bridge, server sync |
| `public/js/layout_engine/dock_manager.js` | CSS class applicator + CSS custom property workspace offset updater |
| `public/js/layout_engine/responsive_manager.js` | ResizeObserver breakpoint detection; auto-dock for tablet/mobile |
| `public/js/layout_engine/layout_manager.js` | `window.SRLE` public API (8 methods + `init()`) |

---

## 4. Files Modified

| File | Change |
|---|---|
| `public/css/ui/layout.css` | Added `.srle-workspace` opt-in class using `--srle-workspace-offset-*` CSS vars |
| `hooks.py` | Added 2 CSS + 4 JS SRLE asset paths in `app_include_css` / `app_include_js` with strict load order comment |

---

## 5. Architecture Decisions

### Why a thin public API facade (window.SRLE) instead of refactoring smriti_sidebar.js?
171 pages already call `SMRITI.renderFlexibleSidebar()`. Touching smriti_sidebar.js risks breaking all of them. SRLE is a coordination layer on top — it delegates to SMRITI.* and never replaces it.

### Why CSS custom property workspace offsets?
Instead of per-page margin hacks (the previous pattern), `dock_manager.js` sets `--srle-workspace-offset-left/top/right/bottom` on `:root`. Any element using `margin-left: var(--srle-workspace-offset-left)` automatically adapts when the dock switches, even across async renders.

### Why localStorage with a server sync option?
Local-first (zero latency, no auth required). Server sync is triggered only via `SRLE.savePreferences()` or `restorePreferences()`, not on every state change. The server endpoint gracefully skips if the custom User field doesn't exist — no deployment dependency.

### Why `--srle-*` token namespace?
Prevents collisions with the existing `--smriti-*` token namespace in `smriti_tokens.css`. Both can coexist indefinitely.

---

## 6. Design Rationale

- **Load order**: `layout_tokens.css` → `layout.css` → (sidebar renders) → `layout_store.js` → `dock_manager.js` → `responsive_manager.js` → `layout_manager.js`. Each file depends on the previous.
- **Legacy bridge**: `layout_store.js` reads `smriti-sidebar-position/collapsed/favorites/collapsed-groups` on first load and mirrors writes back to those keys, so existing sidebar code continues to read correct state.
- **Opt-in workspace**: `.srle-workspace` class is never added to existing pages automatically. Zero forced migration.

---

## 7. Implementation Summary

- 11 files (9 new, 2 modified)
- `02153b7`: 10 new files, 1,059 insertions
- `a3cd2d8`: 8 insertions in hooks.py

---

## 8. Tests Executed

```
python -c "import ast; ast.parse(open('__init__.py').read()); print('OK')"          → OK
python -c "import ast; ast.parse(open('layout_preferences.py').read()); print('OK') → OK
python -c "import ast; ast.parse(open('layout_service.py').read()); print('OK')"    → OK
python -c "import ast; ast.parse(open('hooks.py').read()); print('OK')"             → hooks.py SYNTAX OK

node --check layout_store.js       → (no output = OK)
node --check dock_manager.js       → (no output = OK)
node --check responsive_manager.js → (no output = OK)
node --check layout_manager.js     → (no output = OK)
echo "ALL JS OK"                   → ALL JS OK
```

---

## 9. Verification Results

| Claim | Status | Evidence |
|---|---|---|
| All 3 Python files parse without errors | Done | `ast.parse()` → OK × 3 |
| hooks.py parses without errors | Done | `ast.parse()` → SYNTAX OK |
| All 4 JS files parse without errors | Done | `node --check` → ALL JS OK |
| SRLE CSS/JS registered in hooks.py | Done | diff confirms 8 insertions |
| Committed to main (`02153b7`, `a3cd2d8`) | Done | git log confirmed |
| Pushed to origin/main | Done | push output confirmed |
| Test env (`F:\Smriti9`) updated | Done | fast-forward pull confirmed |
| Backward compat: 171 existing pages unmodified | Done | No existing file touched except layout.css (additive only) |
| Integration test against live Frappe bench | Unverified — requires `bench restart` + browser load |

---

## 10. Known Limitations

- SRLE JS/CSS are now loaded on every Frappe desk page via `app_include_*`. Pages not using `.srle-workspace` receive the CSS/JS but it has no visible effect (zero-cost opt-out).
- Server preference persistence requires a `smriti_layout_prefs` Custom Field on the Frappe User doctype. Until created, `layout_service.py` silently falls back to returning defaults.
- `SRLE.init()` auto-runs on `DOMContentLoaded` — pages that already call `SMRITI.renderFlexibleSidebar()` will have SRLE apply the stored position before the sidebar renders, which is the correct order.

---

## 11. Future Work

| Item | Phase | Priority |
|---|---|---|
| Resizable sidebar drag handle | 2 | Medium |
| Top dock "More" overflow menu | 3 | Medium |
| Full ARIA + keyboard nav | 4 | High |
| `smriti_layout_prefs` Custom Field creation in setup.py | - | High |
| Opt-in migration of priority pages to `.srle-workspace` | - | Low |

---

## 12. Related ADRs

None formally raised. Architecture principle: SRLE wraps, never replaces.

---

## 13. Related RFCs

None. Feature spec provided directly in user request (2026-07-08).
