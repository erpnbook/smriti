# Procurement: Matrix Optimization & Supplier Synchronization

## 1. Purpose
Optimize the SMRITI Purchase Order Matrix grid layout to prevent color/size clutter (by displaying only active variant colors and matched size groups), and automate the synchronization of ERPNext standard suppliers to `SMRITI Supplier`.

## 2. Scope
* **SMRITI Matrix Engine**: `smriti_retail_os/matrix_engine/service/matrix_service.py`
* **ERPNext Hooks & Sync Bridge**: `smriti_retail_os/hooks_logic.py`

## 3. Files Created
None.

## 4. Files Modified
* [matrix_service.py](file:///d:/Smriti_Retail_OS/smriti_retail_os/matrix_engine/service/matrix_service.py)
* [hooks_logic.py](file:///d:/Smriti_Retail_OS/smriti_retail_os/hooks_logic.py)

## 5. Architecture Decisions
* **Smart Size-Group Signature Matching**: Instead of showing all sizes globally registered in the database, the system analyzes the size values of active variants, matches them against configured size groups, and displays only the sizes belonging to that matched group.
* **Variant-Restricted Color Rows**: Limit rows to colors present in existing active variants to prevent grid row explosion.
* **Closed-Loop Supplier Synchronization**: Hook into standard `Supplier` `on_update` to dynamically provision and sync counterpart `SMRITI Supplier` records.

## 6. Design Rationale
* **Usability**: Mixed clothing sizes (`S`, `M`, `L`) and footwear sizes (`36` to `43`) in PO grids caused column overflow and confused retail operators. Restricting columns to the matched size group guarantees a clean grid.
* **Clutter Reduction**: Avoid showing 10+ empty color rows that are not produced or sold for a given article style.

## 7. Implementation Summary
* Restricted `all_colors` in `MatrixService.build_session` to the set of colors defined on active variants of the article.
* Computed size group overlap using intersection analysis on `get_size_groups()` lists and populated `all_sizes` accordingly.
* Added `sync_supplier_address_and_credit_days` hook logic to find or create `SMRITI Supplier` records matching updated ERPNext `Supplier` documents.

## 8. Tests Executed
```bash
bench --site smriti_retail run-tests --app smriti_retail_os --module smriti_retail_os.tests.test_purchase_matrix
```

## 9. Verification Results
* **Automated Unit Tests**: All 4 matrix tests passed (`OK`).
* **Live E2E Verification**: Confirmed in SMRITI Purchase Studio (`/smriti-purchase#orders-create`) that selecting `JAWA` renders only active colors (`RED` and `BLACK`) and only footwear sizes (`36` to `43`).

## 10. Known Limitations
If an article has zero variants in the database, the grid falls back to showing all sizes globally registered in the system until variants are defined.

## 11. Future Work
Provide a dropdown selector in the PO Style Matrix popup to let users manually override the auto-detected size group if needed.

## 12. Related ADRs
None.

## 13. Related RFCs
None.
