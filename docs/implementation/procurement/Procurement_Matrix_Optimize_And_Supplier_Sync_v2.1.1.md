# Implementation Plan - Procurement: Matrix Optimization & Supplier Synchronization v2.1.1

- **Author:** Historical Retrospective
- **Status:** Completed
- **Version:** v2.1.1
- **Date:** 2026-07-06

---

## 1. Objective
Optimize the SMRITI Purchase Order Matrix grid layout to prevent color/size clutter and automate the synchronization of ERPNext standard suppliers to `SMRITI Supplier`.

## 2. Business Motivation
- **Usability**: Restricting columns to the matched size group guarantees a clean grid.
- **Clutter Reduction**: Avoid showing empty color rows that are not produced or sold for a given article style.

## 3. Scope
- Optimize matrix grid representation in `matrix_service.py` to only display active colors/sizes.
- Sync ERPNext standard suppliers to `SMRITI Supplier` using hook logic in `hooks_logic.py`.

## 4. Current State
- PO matrix grids show all globally registered sizes and colors, leading to grid explosions.
- Suppliers in ERPNext and SMRITI are out of sync.

## 5. Gap Analysis
- Matrix engine lacks size-group matching and color rows restriction.
- No auto-provisioning bridge for standard suppliers.

## 6. Architecture Impact
Minor UI and integration hooks impact.

## 7. Proposed Design
- Implement Size-Group Signature Matching and Variant-Restricted Color Rows in `MatrixService.build_session`.
- Add `sync_supplier_address_and_credit_days` hook logic.

## 8. Files Created
None.

## 9. Files Modified
- [matrix_service.py](file:///d:/Smriti_Retail_OS/smriti_retail_os/matrix_engine/service/matrix_service.py)
- [hooks_logic.py](file:///d:/Smriti_Retail_OS/smriti_retail_os/hooks_logic.py)

## 10. Dependencies
None.

## 11. Risks
None.

## 12. Rollback Strategy
Git revert.

## 13. Verification Plan
- Verify via unit tests `smriti_retail_os.tests.test_purchase_matrix`.

## 14. Test Plan
- Run `bench --site smriti_retail run-tests --app smriti_retail_os --module smriti_retail_os.tests.test_purchase_matrix`.

## 15. Documentation Impact
Walkthrough and implementation index update.

## 16. Deployment Plan
Deployed in v2.1.1.

## 17. Status
Completed.

## 18. Related ADRs
None.

## 19. Related Walkthroughs
- [Procurement_Matrix_Optimize_And_Supplier_Sync_v2.1.1.md](file:///d:/Smriti_Retail_OS/docs/walkthrough/procurement/Procurement_Matrix_Optimize_And_Supplier_Sync_v2.1.1.md)
