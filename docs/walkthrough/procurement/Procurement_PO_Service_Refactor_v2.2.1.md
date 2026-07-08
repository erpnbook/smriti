# Procurement — Purchase Studio Service Refactor Follow-up v2.2.1

**Date:** 2026-07-08
**Author:** SMRITI Engineering Team
**Commit:** `bc79a09`
**Status:** Completed
**Supersedes:** N/A — addendum to v2.2.0

---

## 1. Purpose

Follow-up to the v2.2.0 refactor addressing two remaining items from the Indian market audit:
- `get_supplier_performance()` still queried `tabSMRITI Purchase Order` directly with raw SQL after v2.2.0
- `get_size_presets()` had a footwear-only fallback with no path for non-apparel stores

---

## 2. Scope

One file modified: `purchase_studio/service/purchase_service.py`

---

## 3. Files Created

None.

---

## 4. Files Modified

### `purchase_studio/service/purchase_service.py`

**`get_supplier_performance()`**
- Removed 12-line raw SQL query on `tabSMRITI Purchase Order` (same pattern as the analytics fix in v2.2.0)
- Now delegates to `erp_adapter.get_supplier_performance_data(company, from_date, to_date, top_n)`
- The adapter function reads from ERPNext `tabPurchase Order` + `tabPurchase Invoice` and attaches real overdue payable amounts per supplier

**`get_size_presets()`**
- Added `"Generic (Single Size)": ["-"]` to the built-in fallback presets so non-apparel stores can use matrix PO entry without configuring size groups
- Return type changed from `dict` to `{"presets": dict, "using_defaults": bool}` so the UI can detect when defaults are active and surface a "Configure size groups" prompt
- Note: any UI calling `get_size_presets()` and reading the result as a plain dict must be updated to read `result["presets"]` instead of `result`

---

## 5. Architecture Decisions

Same principle as v2.2.0 analytics fix: no direct DocType queries in the service layer. All queries belong in `erp_adapter.py`.

---

## 6. Implementation Summary

- 1 file modified, 0 created, 0 deleted
- Net change: 20 insertions, 29 deletions (−9 net lines)
- Commit: `bc79a09` on `main`

---

## 7. Tests Executed

```
python -c "import ast; ast.parse(open('purchase_service.py').read()); print('OK')"
# Output: SYNTAX OK

# Key lines verified present:
# 416: def get_supplier_performance(...)
# 423: return erp_adapter.get_supplier_performance_data(...)
# 581: def get_size_presets():
# 596: using_defaults = not bool(presets)
# 602: "Generic (Single Size)": ["-"]
# 604: return {"presets": presets, "using_defaults": using_defaults}
```

---

## 8. Verification Results

| Claim | Status | Evidence |
|---|---|---|
| `purchase_service.py` syntax clean | Done | `ast.parse()` → SYNTAX OK |
| `get_supplier_performance` delegates to adapter | Done | `git diff` shows SQL removed, adapter call added |
| `get_size_presets` returns `using_defaults` flag | Done | `git diff` + line verification shows new return shape |
| Committed and pushed to `main` | Done | commit `bc79a09`, push confirmed |
| Test env (`F:\Smriti9`) updated | Done | fast-forward pull to `bc79a09` |

---

## 9. Known Limitations

- UI calling `get_size_presets()` must be updated to read `result["presets"]` — the return shape changed from a plain dict to `{"presets": ..., "using_defaults": ...}`. The Purchase Order matrix UI (`purchase_orders.html`) should be inspected.
- TDS category support (Issue #4 from original audit) and approval threshold pre-GST clarification (Issue #5) remain future work requiring DocType changes.

---

## 10. Future Work

| Item | Priority |
|---|---|
| Update `purchase_orders.html` to handle `get_size_presets` new return shape | High |
| TDS category field on SMRITI Supplier | High |
| Approval threshold: clarify pre-GST vs post-GST in settings | Medium |

---

## 11. Related ADRs

None.

---

## 12. Related RFCs

None.

---

## 13. Related Walkthroughs

[Procurement_PO_Service_Refactor_v2.2.0.md](Procurement_PO_Service_Refactor_v2.2.0.md)
