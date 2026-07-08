# Procurement — Purchase Order Service Refactor (Indian Market Compliance) v2.2.0

**Date:** 2026-07-08
**Author:** SMRITI Engineering Team
**Branch:** main (merged from smriti-next)
**Commit:** `782917c`
**Status:** Completed

---

## 1. Purpose

Fix five correctness and performance defects in the Purchase Studio service layer identified during a deep audit against Indian retail compliance requirements:

1. Supplier Ledger read from SMRITI PO amounts instead of real GL entries
2. Dashboard KPIs used hardcoded stubs (pending GRNs = open POs, unpaid = 40% of PO spend)
3. Purchase analytics queried SMRITI PO tables (pre-GST intent data) instead of actual Purchase Invoices
4. Variant resolution issued N+1 SQL queries per variant (one `Item Variant Attribute` query per variant)
5. `search_suppliers` and `get_suppliers` were duplicate implementations of the same logic

---

## 2. Scope

| File | Layer | Change Type |
|---|---|---|
| `purchase_studio/service/purchase_service.py` | Business Logic | Refactor (4 fixes) |
| `purchase_studio/service/purchase_order_service.py` | Business Logic | Refactor (1 fix + import) |

No API layer, no adapter layer, no UI, no DocType, no fixtures changed.

---

## 3. Files Created

None.

---

## 4. Files Modified

### `purchase_studio/service/purchase_order_service.py`
- Added `from smriti_retail_os.purchase_studio.adapter import erp_adapter` import
- Rewrote `get_dashboard_data()`:
  - `pending_grns` → `erp_adapter.count_pending_grns(company)` (real unbilled GRNs)
  - `unpaid_invoices_amt` → `erp_adapter.get_outstanding_payables_total(company)` (real outstanding PI amount)
  - `month_spend` → `erp_adapter.get_monthly_spend_total(company, month_start)` (real PI-based spend)
  - `recent_activity` → `erp_adapter.get_recent_activities(company)` (cross-doctype PO/GRN/PI)
  - Removed raw SQL query on `tabSMRITI Purchase Order` for month spend

### `purchase_studio/service/purchase_service.py`
- **`get_supplier_ledger()`**: Now bridges SMRITI Supplier → ERPNext Supplier via `erpnext_supplier` field, then reads `tabGL Entry` via `erp_adapter.get_supplier_gl_entries()`. Returns real `total_payable` (outstanding) and `overdue` amounts from actual GL instead of PO totals. `overdue` was hardcoded `0.0` before.
- **`get_purchase_analytics()`**: Replaced 3 direct SQL queries on `tabSMRITI Purchase Order` and `tabSMRITI Purchase Order Item` with `erp_adapter.get_purchase_spend_analytics()` which reads from `tabPurchase Invoice` (GST-inclusive, actual payments).
- **`search_suppliers()`**: Merged into thin alias calling `get_suppliers()`. Removed duplicated `PurchaseOrderService.list_suppliers()` call. Added docstring noting SC-13 backward compatibility.
- **`resolve_variant_item()`**: Replaced N+1 attribute lookup loop (one `frappe.db.get_all("Item Variant Attribute")` call per variant) with a single batch query fetching all attributes for all variants at once, then grouped by parent in Python.

---

## 5. Architecture Decisions

### Why read GL instead of SMRITI PO totals for the supplier ledger?
Indian retail accountants reconcile the supplier ledger against GSTR-2B (supplier GST returns). The GSTR-2B view is driven by Purchase Invoice GL entries, not Purchase Order intents. A ledger showing PO values would always mismatch the accountant's view and the GST portal.

### Why use PI-based analytics instead of SMRITI PO analytics?
SMRITI POs are pre-GST intent records. They record the order value at the time of ordering. Purchase Invoices record the actual GST-inclusive amount paid. For spend analytics in an Indian context, PI values are the correct basis.

### Why batch-fetch variant attributes?
A matrix order of 10 articles × 8 colours × 6 sizes = 480 variants. The old code issued 480 individual DB queries per resolve call. A single batched query returns all 480 rows in one round-trip.

---

## 6. Design Rationale

All adapter functions called (`count_pending_grns`, `get_outstanding_payables_total`, `get_monthly_spend_total`, `get_recent_activities`, `get_supplier_gl_entries`, `get_supplier_outstanding`, `get_supplier_overdue_payable`, `get_purchase_spend_analytics`) already existed in `erp_adapter.py`. This was wiring, not new code. The adapter layer was already complete; the service layer was not using it.

---

## 7. Implementation Summary

- 2 files modified, 0 files created, 0 files deleted
- Net change: 140 lines removed, 81 lines added (−59 net lines)
- Commit: `782917c` on `main`

---

## 8. Tests Executed

```
python -c "import ast; ast.parse(open('purchase_service.py').read()); print('OK')"
# Output: OK

python -c "import ast; ast.parse(open('purchase_order_service.py').read()); print('OK')"
# Output: OK

# Function presence check — 17 functions verified FOUND, ALL OK
```

No automated integration tests were executed (test environment requires running Frappe/ERPNext instance). Syntax validation passed for both modified files.

---

## 9. Verification Results

| Claim | Status | Evidence |
|---|---|---|
| Both files parse without errors | Done | `ast.parse()` → `OK` on both |
| All 17 expected functions present | Done | AST walk — `ALL OK` |
| Git diff matches intended changes | Done | `git diff` output reviewed |
| Committed to `main` | Done | commit `782917c` |
| Pushed to origin | Done | `main -> main` push confirmed |
| Test env (`F:\Smriti9`) updated | Done | fast-forward pull to `782917c` |

---

## 10. Known Limitations

- `get_supplier_performance()` in `purchase_service.py` still queries `tabSMRITI Purchase Order` directly with raw SQL. This was not in scope for this refactor but is a candidate for the next pass (Issue #5 from the audit — use `erp_adapter.get_supplier_performance_data()`).
- TDS category support (Issue #4 from audit) not addressed — requires DocType change to `SMRITI Supplier`.
- Browser-level UI verification was not performed (test server hostname not resolvable from dev environment).

---

## 11. Future Work

| Item | Priority | Description |
|---|---|---|
| `get_supplier_performance()` adapter wiring | Medium | Same pattern as analytics — delegate to `erp_adapter.get_supplier_performance_data()` |
| TDS category field on SMRITI Supplier | High | Add `tds_category` field, sync to ERPNext Supplier bridge |
| Approval threshold: pre-GST vs post-GST | Medium | Clarify in settings and enforce consistently |
| `get_size_presets()` generic fallback | Low | Add a non-apparel default preset |

---

## 12. Related ADRs

None formally created for this refactor. Architecture principle applied: "SMRITI reads GL, never writes it" (see `erp_adapter.py` file header).

---

## 13. Related RFCs

None. Change was driven by Indian market compliance audit findings.
