# Foundation — SMRITI Retail OS Layout Engine (SRLE) v1.0 — Phase 1

**Date:** 2026-07-08
**Status:** Completed
**Author:** SMRITI Engineering Team
**Commits:** `02153b7`, `a3cd2d8`

---

## 1. Objective
Create the SMRITI Retail OS Layout Engine (SRLE) — a platform-wide, versioned layout API that becomes the single source of truth for navigation dock position, sidebar state, workspace scrolling, and responsive behaviour across all SMRITI modules.

## 2. Business Motivation
Each SMRITI module was independently managing layout concerns (sidebar margin, scroll, dock position). This caused inconsistencies: a dock switch in one page didn't persist correctly to another. SRLE centralises these concerns so future modules inherit layout behaviour automatically.

## 3. Scope
See walkthrough `Foundation_SRLE_Layout_Engine_v1.0.md` for full file list.

## 4. Current State (Before)
- `smriti_sidebar.js` had `setSidebarPosition()` supporting 4 docks, but no formal public API
- `smriti_sidebar.css` had top/bottom dock CSS but no workspace offset coordination
- localStorage keys (`smriti-sidebar-*`) were scattered — no central state store
- No server-side preference persistence
- No responsive manager
- No workspace registry

## 5. Gap Analysis
All gaps resolved in Phase 1. Phases 2–4 addressed separately.

## 6. Architecture Impact
SRLE is additive. `smriti_sidebar.js` and `smriti_sidebar.css` are unchanged. SRLE wraps and coordinates them via `window.SRLE`.

## 7. Proposed Design
See implementation_plan.md artifact for full design rationale.

## 8. Files Created
9 new files. See walkthrough.

## 9. Files Modified
`public/css/ui/layout.css`, `hooks.py`. See walkthrough.

## 10. Dependencies
- `smriti_sidebar.js` must be registered before SRLE JS (enforced by hooks.py load order)
- `smriti_tokens.css` must be registered before `layout_tokens.css` (enforced by hooks.py order)

## 11. Risks
| Risk | Mitigation |
|---|---|
| 171 existing pages break | SRLE is additive — no existing file logic changed |
| CSS `--srle-*` conflicts with `--smriti-*` | Different namespace, no overlap |
| Server endpoint breaks on missing field | `_field_exists()` guard in `layout_service.py` |

## 12. Rollback Strategy
`git revert a3cd2d8` (unhooks assets) + `git revert 02153b7` (removes module). No DB changes needed.

## 13. Verification Plan
See walkthrough Section 8–9.

## 14. Test Plan
| Test | Type | Status |
|---|---|---|
| Python syntax (3 files) | Static | Done |
| JS syntax (4 files) | Static | Done |
| hooks.py syntax | Static | Done |
| SRLE loads on bench page | Integration | Unverified |
| `SRLE.setLayout("top")` switches dock | Integration | Unverified |
| `SRLE.savePreferences()` persists to server | Integration | Unverified |

## 15. Documentation Impact
- Walkthrough: `docs/walkthrough/foundation/Foundation_SRLE_Layout_Engine_v1.0.md` — Created
- Walkthrough Index: `docs/walkthrough/README.md` — Updated
- Implementation Plan Index: `docs/implementation/README.md` — Updated
- CHANGELOG: Updated

## 16. Deployment Plan
1. `git push origin main` ✓
2. `F:\Smriti9` pull ✓
3. `bench build --app smriti_retail_os` — required to copy assets to `/assets/` path
4. `bench restart` — required to reload Python modules and hooks

## 17. Status
**Completed** — 2026-07-08

## 18. Related ADRs
None.

## 19. Related Walkthroughs
[Foundation_SRLE_Layout_Engine_v1.0.md](../../walkthrough/foundation/Foundation_SRLE_Layout_Engine_v1.0.md)
