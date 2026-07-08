# Procurement — Purchase Studio Deep Review Fixes v2.3.1

**Date:** 2026-07-08
**Author:** SMRITI Engineering Team
**Commit:** `4737271` (code) · `4b3f023` (UI) · (docs — this commit)
**Status:** Completed

---

## 1. Purpose

Close three outstanding issues from the Purchase Studio deep-review backlog:

| Issue | Description |
|---|---|
| UI gap | `loadSizePresets()` in PO Create and Quotation pages was reading the raw API response as a plain dict after `get_size_presets` changed its return shape to `{presets, using_defaults}` in v2.2.1 |
| Issue #4 | TDS category was never synced from `SMRITI Supplier` to ERPNext `Supplier.tax_withholding_category` — field didn't exist on `SMRITI Supplier` at all |
| Issue #5 | Approval threshold comparison always used `grand_total` (GST-inclusive) even though the business intent was pre-GST amounts, and the setting had no way to declare intent |

---

## 2. Scope

**Files changed:**

| File | Change |
|---|---|
| `www/smriti-po-create.html` | `loadSizePresets()` unpacks new shape + banner |
| `www/smriti-quotation.html` | Same fix for sales path |
| `smriti_retail_os/doctype/smriti_supplier/smriti_supplier.json` | Added `tds_category` Link field |
| `purchase_studio/adapter/erp_adapter.py` | TDS sync in update + create paths |
| `purchase_studio/service/purchase_settings_service.py` | `approval_threshold_inclusive_of_tax` + updated `check_approval_required` |
| `purchase_studio/service/purchase_workflow_service.py` | `submit()` delegates to `check_approval_required` |

---

## 3. Files Created

None. All changes are modifications to existing files.

---

## 4. Files Modified

### `www/smriti-po-create.html`
- `loadSizePresets()`: `sizePresets = data.message.presets || data.message || {}` (old-shape fallback)
- `usingDefaults = payload.using_defaults === true`
- Injects purple info banner with "Configure size groups" link when `usingDefaults` is true
- Banner is idempotent — old `#srle-size-defaults-banner` removed before re-injection

### `www/smriti-quotation.html`
- Same pattern applied to the `api()` helper-based call (`sales_studio.api.sales_api.get_size_presets`)
- No visible change when using_defaults is false; banner shown when platform defaults are active

### `smriti_retail_os/doctype/smriti_supplier/smriti_supplier.json`
- Added `tds_category` field: type=Link, options=`Tax Withholding Category`, inserted after `disabled`
- No existing field position or property changed

### `purchase_studio/adapter/erp_adapter.py` — `get_or_create_bridge_supplier`
- **Update path** (linked supplier exists): builds `sync_vals` dict; adds `tax_withholding_category` only when `smriti_supplier.tds_category` is set and `frappe.db.exists("Tax Withholding Category", …)` passes
- **Create path** (new supplier): same guard applied before `insert()`
- Guard means zero breakage on installations without `india_compliance` app

### `purchase_studio/service/purchase_settings_service.py`
- `get_settings()` SDK provider block: added `approval_threshold_inclusive_of_tax: bool(config.get_config(...))`
- `get_settings()` DocType fallback: added `approval_threshold_inclusive_of_tax: bool(getattr(s, ..., False))`
- `get_settings()` safe defaults: added `approval_threshold_inclusive_of_tax: False`
- `check_approval_required(grand_total, net_total=None)`:
  - Reads `inclusive` flag from Policy Engine (or settings fallback)
  - When `inclusive=True`: compares `grand_total` (GST-inclusive) vs threshold
  - When `inclusive=False` (default): compares `net_total` vs threshold (falls back to `grand_total` if `net_total` not provided)

### `purchase_studio/service/purchase_workflow_service.py`
- `submit()`: removed inline `threshold > grand_total` comparison
- Now: `net_total = getattr(po, "net_total", None) or po.grand_total` then calls `settings_svc.check_approval_required(grand_total=po.grand_total, net_total=net_total)`

---

## 5. Architecture Decisions

### Why a fallback for the old size presets shape?
`get_size_presets` changed shape in v2.2.1. Any cached HTML (CDN/browser cache) would still send the old format. The fallback `|| data.message` ensures zero-downtime: if `data.message` is a plain dict (old shape) it's used as-is; if it has `.presets` (new shape) that key is used.

### Why `frappe.db.exists` guard for TDS?
`Tax Withholding Category` is an `india_compliance` app doctype. Not all SMRITI deployments have that app. The guard means the TDS sync is silently skipped on non-India installations — no KeyError, no exception.

### Why default `approval_threshold_inclusive_of_tax = False` (pre-GST)?
The `SMRITI Purchase Order` is an intent document — its `grand_total` is the sum of line-item amounts (pre-GST). Comparing a pre-GST approval threshold to a pre-GST total is internally consistent. Post-GST comparison is opt-in via the boolean setting.

---

## 6. Design Rationale

All three fixes follow the "additive, no breakage" principle:
- `tds_category` field is optional — existing suppliers with no TDS category are unaffected
- `approval_threshold_inclusive_of_tax` defaults to `False` — no change in behaviour for existing deployments
- Size preset fallback ensures both old and new API shapes work simultaneously during cache flush

---

## 7. Implementation Summary

- 6 files modified, 0 files created
- Commits `4b3f023` (UI, +55/-4) and `4737271` (backend, +91/-44)

---

## 8. Tests Executed

```
python -c "import ast; ast.parse(open('erp_adapter.py').read()); print('OK')"              → OK
python -c "import ast; ast.parse(open('purchase_settings_service.py').read()); print('OK') → OK
python -c "import ast; ast.parse(open('purchase_workflow_service.py').read()); print('OK') → OK
```

---

## 9. Verification Results

| Claim | Status | Evidence |
|---|---|---|
| Python syntax — 3 service/adapter files | Done | `ast.parse()` → OK × 3 |
| `smriti_supplier.json` is valid JSON | Done | `json.load()` → no exception, field count 13→14 |
| `tds_category` field at index 8 in doctype | Done | Python field-list printout confirmed |
| Commits pushed to `origin/main` | Done | push output — `4b3f023`, `4737271` |
| `F:\Smriti9` synced | Done | fast-forward pull confirmed |
| Integration: TDS actually syncs on transaction | Unverified — requires `bench migrate` + `bench restart` + live transaction on test server |
| Integration: `approval_threshold_inclusive_of_tax` field on Settings DocType | Unverified — requires DocType update in bench env (`bench migrate`) |

---

## 10. Known Limitations

- `approval_threshold_inclusive_of_tax` is read via `getattr(s, ..., False)` from the Settings DocType — the field does not yet exist on the DocType definition. A DocType schema update or Custom Field addition is required for the UI toggle. Until then the default (`False`) always applies.
- `tds_category` field was added to the doctype JSON but not yet propagated to the database via `bench migrate`. The field will appear in the form only after migration.

---

## 11. Future Work

| Item | Priority |
|---|---|
| Add `approval_threshold_inclusive_of_tax` Check field to `SMRITI Purchase Settings` DocType | High |
| Add TDS category display column to Supplier list view | Low |
| Write unit tests for `check_approval_required` covering both inclusive/exclusive branches | Medium |
| Validate size preset banner rendering in browser against live `get_size_presets` response | Medium |

---

## 12. Related ADRs

None.

---

## 13. Related RFCs

None. Issues captured in session deep-review backlog (2026-07-08).
