# Walkthrough: Navigation Audit, Sidebar Refactor & PO Print v1.0

**Area:** Foundation / Navigation / Purchase Studio
**Version:** v2.5.0
**Date:** 2026-07-08
**Status:** Completed

---

## 1. Purpose

Deep audit of SMRITI sidebar `CANONICAL_NAV` against all `www/` pages, fix broken/stale/duplicate routes, add missing pages, implement `coming_soon` status rendering, and deliver a rebuilt PO print/view page modelled on `sizewise_invoice`.

---

## 2. Scope

| Component | Change Type |
|---|---|
| `navigation/navigation_service.py` | Full CANONICAL_NAV refactor |
| `public/js/smriti_sidebar_standalone.js` | New coming_soon item renderer |
| `public/css/smriti_sidebar_standalone.css` | New .coming-soon + amber badge CSS |
| `public/css/smriti_sidebar.css` | Same CSS (Frappe Desk variant) |
| `www/smriti-po-print.html` | Full rebuild in sizewise_invoice style |

---

## 3. Files Created

- `www/smriti-po-print.html` — rebuilt PO print/view page (1029 insertions)

---

## 4. Files Modified

| File | Change |
|---|---|
| `navigation/navigation_service.py` | 127 ins / 108 del - CANONICAL_NAV refactor |
| `public/js/smriti_sidebar_standalone.js` | 25 ins / 9 del - coming_soon render logic |
| `public/css/smriti_sidebar_standalone.css` | 24 ins - amber badge + coming-soon styles |
| `public/css/smriti_sidebar.css` | 24 ins - same (Frappe Desk parity) |

---

## 5. Architecture Decisions

- `coming_soon` is a first-class status tier: visible but muted (55% opacity, italic, amber SOON badge, tabindex=-1, routes to /smriti-coming-soon)
- Route normalisation: Frappe resolves filenames preserving underscores. All routes corrected (e.g. /item_master not /item-master)
- PO Print mirrors sizewise_invoice: same SMRITI shell, 6 panels, chrome-free print layout, PDF export, history drawer. Zero backend changes.

---

## 6. Audit Findings Summary

| Severity | Count | Resolution |
|---|---|---|
| Broken route (no page) | 7 | Redirected to coming-soon or fixed |
| Route mismatch (hyphen vs underscore) | 8 | Fixed to match actual Frappe slug |
| Duplicate route (2 IDs same URL) | 3 | Collapsed to 1 entry |
| Missing (page exists, no menu) | 13 | Added to CANONICAL_NAV |
| CGE sub-pages (not yet built) | 13 | Marked coming_soon |

---

## 7. New sidebar entries added

Masters: sfm_master, sfc_catalog
Sales: quotation
Purchase Studio: grn_receipts (standalone /smriti-grn), purchase_invoice_pg, purchase_receipt_pg, purchase_returns
Finance: tally, safe_cash
Administration: platform_admin, nav_health, field_explorer, go_live, setup_wizard

---

## 8. Tests Executed

- Python syntax check: `python -c "ast.parse(...)"` -> SYNTAX OK
- git diff --cached --stat for all 5 files confirmed
- git push to remote + fast-forward pull to F:\Smriti9 confirmed

---

## 9. Verification Results

| Commit | Hash | Status |
|---|---|---|
| PO print rebuild | 28b0b25 | Done |
| nav CANONICAL_NAV refactor | 077e5c5 | Done |
| sidebar coming_soon feature | a6c47d1 | Done |

---

## 10. Known Limitations

- CGE sub-page dedicated pages not yet built - routes are hash anchors on /smriti-cge
- smriti_sidebar.js (Frappe Desk version) does NOT have the coming_soon render logic yet
- Nav cache TTL=24h: run bench clear-cache after deploy

---

## 11. Future Work

- Build dedicated pages for coming_soon items (CGE, opening_stock, receipts, advances)
- Port coming_soon render logic to smriti_sidebar.js
- Automated nav health test: compare CANONICAL_NAV routes vs www filesystem

---

## 12. Related ADRs

- ADR-004: Sidebar Navigation as Single Source of Truth
- ADR-012: Route Normalisation — Underscore over Hyphen

---

## 13. Related RFCs

- RFC-008: Sidebar coming_soon Status Tier
- RFC-015: PO Print Page Architecture
