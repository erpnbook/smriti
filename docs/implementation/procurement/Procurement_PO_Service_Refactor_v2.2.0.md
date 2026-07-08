# Procurement — Purchase Order Service Refactor (Indian Market) v2.2.0

**Date:** 2026-07-08
**Status:** Completed
**Author:** SMRITI Engineering Team
**Commit:** `782917c`

---

## 1. Objective

Correct five defects in the Purchase Studio service layer identified during a deep Indian-market compliance audit: fake dashboard KPIs, wrong GL source for supplier ledger, pre-GST analytics data, N+1 variant attribute queries, and duplicated supplier search functions.

---

## 2. Business Motivation

Indian retail businesses must reconcile:
- Supplier ledger against GSTR-2B (Purchase Invoice GL, not PO amounts)
- Monthly spend reports against actual GST-inclusive invoiced amounts
- Dashboard payable figures against real ERPNext outstanding amounts

The existing code showed fabricated numbers (40% of PO spend as payable estimate, PO count as GRN count). These were architectural gaps, not intentional placeholders.

---

## 3. Scope

**In scope:**
- `purchase_service.py` — 4 function rewrites
- `purchase_order_service.py` — 1 function rewrite + import addition

**Out of scope:**
- API layer (no endpoint signature changes)
- UI/HTML pages
- DocType changes
- TDS support (separate phase)

---

## 4. Current State (Before)

| Function | Problem |
|---|---|
| `get_dashboard_data()` | `pending_grns = open_pos` (same number); `unpaid_invoices_amt = month_spend * 0.4` (fabricated); month_spend from SMRITI PO (pre-GST) |
| `get_supplier_ledger()` | Read SMRITI PO grand_total values, not GL entries; `overdue` hardcoded to `0.0` |
| `get_purchase_analytics()` | 3 SQL queries on `tabSMRITI Purchase Order` (pre-GST intent data) |
| `resolve_variant_item()` | N+1: one `frappe.db.get_all("Item Variant Attribute")` call per variant |
| `search_suppliers()` | Duplicate of `get_suppliers()` — both call `PurchaseOrderService.list_suppliers()` |

---

## 5. Gap Analysis

The `erp_adapter.py` already contained all correct implementations:
- `count_pending_grns()` — real unbilled GRN count
- `get_outstanding_payables_total()` — real PI outstanding
- `get_monthly_spend_total()` — real PI-based monthly spend
- `get_recent_activities()` — cross-doctype activity feed
- `get_supplier_gl_entries()` — real GL for supplier ledger
- `get_supplier_outstanding()` — real payable total
- `get_supplier_overdue_payable()` — real overdue amount
- `get_purchase_spend_analytics()` — PI-based spend analytics

The gap was exclusively in the service layer not calling these adapter functions.

---

## 6. Architecture Impact

No architectural changes. Existing `erp_adapter.py` isolation boundary maintained:
- Service layer calls adapter functions
- Adapter layer calls ERPNext DocTypes
- No direct DocType access added to service layer

---

## 7. Proposed Design

Wire service layer to existing adapter functions. Merge duplicate `search_suppliers` → thin alias of `get_suppliers`. Batch `Item Variant Attribute` query.

---

## 8. Files Created

None.

---

## 9. Files Modified

| File | Change |
|---|---|
| `purchase_studio/service/purchase_order_service.py` | Add `erp_adapter` import; rewrite `get_dashboard_data()` |
| `purchase_studio/service/purchase_service.py` | Rewrite `get_supplier_ledger()`, `get_purchase_analytics()`, `resolve_variant_item()`; merge `search_suppliers()` |

---

## 10. Dependencies

All adapter functions used were already implemented in `erp_adapter.py`. No new dependencies introduced.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| `get_purchase_analytics()` now returns PI-based keys (`by_supplier`, `by_month`, `by_item_group`, `po_trend`) — UI must handle `po_trend` being new | Key names match what adapter already returns; UI frontend reads these dynamically |
| Supplier ledger now empty if no ERPNext GL entries exist | Correct behaviour — empty ledger means no invoices posted, not a bug |
| `get_dashboard_data()` returns `0` for pending_grns if no GRNs exist in ERPNext | Correct — was returning `open_pos` (wrong) before |

---

## 12. Rollback Strategy

`git revert 782917c` reverts both files atomically. No DB migrations were involved.

---

## 13. Verification Plan

1. `ast.parse()` on both modified files — no syntax errors
2. AST function presence check — all 17 functions confirmed `FOUND`
3. `git diff` — all changes match intended design
4. Push to `main` + sync to `F:\Smriti9`

---

## 14. Test Plan

| Test | Type | Status |
|---|---|---|
| Syntax parse both files | Static | Done |
| All expected functions present | Static | Done |
| Dashboard returns real GRN count | Integration | Pending (requires live bench) |
| Supplier ledger returns GL entries | Integration | Pending (requires live bench) |
| Analytics returns PI-based spend | Integration | Pending (requires live bench) |
| Variant resolution returns correct item | Integration | Pending (requires live bench) |

---

## 15. Documentation Impact

| Document | Action |
|---|---|
| `docs/walkthrough/procurement/Procurement_PO_Service_Refactor_v2.2.0.md` | Created |
| `docs/walkthrough/README.md` | Updated |
| `docs/implementation/procurement/Procurement_PO_Service_Refactor_v2.2.0.md` | Created (this file) |
| `docs/implementation/README.md` | Updated |
| `CHANGELOG.md` | Updated |

---

## 16. Deployment Plan

1. Commit `782917c` pushed to `origin/main` ✓
2. `F:\Smriti9` pulled to `782917c` ✓
3. `bench restart` required on test instance to reload Python modules

---

## 17. Status

**Completed** — 2026-07-08

---

## 18. Related ADRs

None formally raised. Applies existing principle from `erp_adapter.py` header: "SMRITI reads GL, never writes it."

---

## 19. Related Walkthroughs

[Procurement_PO_Service_Refactor_v2.2.0.md](../walkthrough/procurement/Procurement_PO_Service_Refactor_v2.2.0.md)
