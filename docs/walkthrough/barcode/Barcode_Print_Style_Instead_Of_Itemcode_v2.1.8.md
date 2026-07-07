# SMRITI Engineering Walkthrough — Barcode Style/Article Code Priority v2.1.8

- **Date:** 2026-07-07
- **Area:** Barcode
- **Version:** v2.1.8
- **Author:** Antigravity AI
- **Owner:** AITDL

---

## 1. Purpose
This walkthrough documents the changes made to prioritize printing the business `Style/Article` code on barcode labels (main label, shoe tag, and box tag) instead of raw system `Item Code` identifiers.

## 2. Scope
* Reordered Style resolution priority logic in `smriti_retail_os/barcode/item_service.py` and `smriti_retail_os/barcode/token_registry.py`.
* Replaced `{item_code}` placeholders with `{style}` in the raw ZPL printer seed template inside `smriti_retail_os/setup.py`.

## 3. Files Created
* None

## 4. Files Modified
* [item_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/barcode/item_service.py)
* [token_registry.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/barcode/token_registry.py)
* [setup.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/setup.py)

## 5. Architecture Decisions
1. **Business-Identified Printing:** Prioritized printing `custom_style_code` over the internal templates (`variant_of`) and raw database keys (`item_code`) to ensure physical retail labels display the Article/Style values expected by store operators.
2. **Eliminated Split Truncation:** Changed fallback logic to output the full item code instead of a hyphen-split prefix, preventing partial data loss during rendering when no custom style code exists.

## 6. Design Rationale
* The database-seeded ZPL templates for the Honeywell IH-2 printer used raw `{item_code}` fields, resulting in labels showing long strings like `CH-01-A-CREAM-37`. By mapping `{style}` in all segments (main, shoe tag, box tag) and setting priority to `custom_style_code`, the printed labels display the Article (`CH-01-A`) as defined in import logs.

## 7. Implementation Summary
* Reordered precedence in `get_item_print_details` to check `custom_style_code` first.
* Removed splitting logic on the item code fallback in `item_service.py` and `token_registry.py`.
* Replaced `{item_code}` with `{style}` in three locations within the Honeywell ZPL seed template inside `setup.py`.

## 8. Tests Executed
* Executed the barcode API unit tests in isolation via Docker:
  `docker exec smriti9-backend-1 bench --site smriti_retail run-tests --app smriti_retail_os --module smriti_retail_os.tests.test_barcode_api`

## 9. Verification Results
* **Unit Tests:** Passed (37/37 tests OK).
* **Architecture Guard:** Passed (`python smriti_architecture_guard.py` completed with no violations).

## 10. Known Limitations
* Database templates already loaded into "SMRITI Print Template" require `bench migrate` or manual raw template string updates to apply the new `{style}` placeholder.

## 11. Future Work
* None

## 12. Related ADRs
* None

## 13. Related RFCs
* None
