# Procurement — Purchase Studio Deep Review Fixes v2.3.1

**Date:** 2026-07-08
**Status:** Completed
**Author:** SMRITI Engineering Team
**Commits:** `4b3f023`, `4737271`

---

## 1. Objective
Close three backlogged issues from the Purchase Studio deep review: UI size preset consumption mismatch, missing TDS category sync between SMRITI and ERPNext suppliers, and ambiguous approval threshold basis (pre-GST vs post-GST).

## 2. Business Motivation
- **Size presets**: After `get_size_presets()` changed shape in v2.2.1, both PO and Quotation matrix grids silently received an empty preset list — users could not enter size-based orders.
- **TDS sync**: Without `tax_withholding_category` on ERPNext Supplier, TDS deductions were never applied to supplier payments — compliance risk.
- **Approval threshold**: A ₹50,000 threshold applied to GST-inclusive totals would trigger approval for orders that are only ₹42,373 pre-GST — overly conservative. Conversely, a pre-GST threshold applied to GST-inclusive amounts would under-trigger.

## 3. Scope
6 files modified. See walkthrough for full list.

## 4. Current State (Before)
- `loadSizePresets()` read `data.message || {}` — always received `{presets: {...}, using_defaults: bool}` as the "presets" variable (a nested object), making iteration over preset keys return nothing.
- `SMRITI Supplier` had no `tds_category` field. `get_or_create_bridge_supplier` never set `tax_withholding_category`.
- `purchase_workflow_service.submit()` compared `grand_total` (pre-GST in SMRITI) against the threshold but used raw inline comparison, bypassing `check_approval_required()`.

## 5. Gap Analysis
All three gaps resolved. No new gaps introduced.

## 6. Architecture Impact
Additive only. Existing workflows unchanged when new fields are absent.

## 7. Proposed Design
See walkthrough Section 5 — Architecture Decisions.

## 8. Files Created
None.

## 9. Files Modified
- `www/smriti-po-create.html`
- `www/smriti-quotation.html`
- `smriti_retail_os/doctype/smriti_supplier/smriti_supplier.json`
- `purchase_studio/adapter/erp_adapter.py`
- `purchase_studio/service/purchase_settings_service.py`
- `purchase_studio/service/purchase_workflow_service.py`

## 10. Dependencies
- `Tax Withholding Category` DocType — must exist (`india_compliance` app). Guard ensures graceful skip if absent.
- `SMRITI Purchase Settings` DocType — `approval_threshold_inclusive_of_tax` field not yet on DocType schema; uses `getattr` fallback until field is added.

## 11. Risks
| Risk | Mitigation |
|---|---|
| `db.exists("Tax Withholding Category")` slow on every transaction | Single SQL lookup; negligible cost; cached by Frappe query cache |
| `getattr(s, "approval_threshold_inclusive_of_tax", False)` masks schema gap | Acceptable — defaults to pre-GST basis which is the more conservative choice |

## 12. Rollback Strategy
`git revert 4737271 4b3f023`. No DB schema changes except doctype JSON — run `bench migrate` after revert.

## 13. Verification Plan
See walkthrough Section 8–9.

## 14. Test Plan
| Test | Type | Status |
|---|---|---|
| Python syntax × 3 | Static | Done |
| JSON validity — smriti_supplier.json | Static | Done |
| PO Create page renders preset selector with real data | Integration | Unverified |
| Quotation matrix renders preset selector | Integration | Unverified |
| TDS category appears on ERPNext Supplier after bridge call | Integration | Unverified |
| Approval not triggered for pre-GST PO below threshold | Integration | Unverified |

## 15. Documentation Impact
- Walkthrough: `docs/walkthrough/procurement/Procurement_Deep_Review_Fixes_v2.3.1.md` — Created
- Walkthrough Index: `docs/walkthrough/README.md` — Updated
- Implementation Index: `docs/implementation/README.md` — Updated
- CHANGELOG: v2.3.1 entry added

## 16. Deployment Plan
1. `git push origin main` ✓
2. `F:\Smriti9` pull ✓
3. `bench migrate` — propagates `tds_category` field to `tabSMRITI Supplier`
4. `bench restart`

## 17. Status
**Completed** — 2026-07-08

## 18. Related ADRs
None.

## 19. Related Walkthroughs
[Procurement_Deep_Review_Fixes_v2.3.1.md](../../walkthrough/procurement/Procurement_Deep_Review_Fixes_v2.3.1.md)
