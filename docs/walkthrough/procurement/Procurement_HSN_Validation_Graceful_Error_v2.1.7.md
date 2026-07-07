# SMRITI Engineering Walkthrough — HSN Validation Graceful Error handling v2.1.7

- **Date:** 2026-07-07
- **Area:** Procurement
- **Version:** v2.1.7
- **Author:** Jawahar Ramkripal Mallah
- **Owner:** AITDL

---

## 1. Purpose
This walkthrough documents the fix for the unhandled validation crash during product catalog import dry-runs. When an invalid HSN length (such as 7 digits) was supplied, the backend HSN resolution helper raised an unhandled `ValidationError`, crashing the entire `validate_import_rows` API request (yielding `417 Expectation Failed`). This has been fixed by intercepting the validation error and reporting it cleanly as a row-specific validation error.

## 2. Scope
* Catch validation and value exceptions during HSN resolution inside `validate_import_rows` in `item_master_api.py`.
* Log validation messages inside the respective row-level `errors` collection.
* Add unit test `test_hsn_invalid_length_validation_catching` in `test_item_master_api.py`.
* Update FAQs in GST config and troubleshooting knowledge base documentation.

## 3. Files Created
* [Procurement_HSN_Validation_Graceful_Error_v2.1.7.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/procurement/Procurement_HSN_Validation_Graceful_Error_v2.1.7.md) (This file)

## 4. Files Modified
* [item_master_api.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/item_master_api.py)
* [tests/test_item_master_api.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/test_item_master_api.py)
* [docs/07-kb/gst.md](file:///D:/Smriti_Retail_OS/docs/07-kb/gst.md)
* [docs/07-kb/volume_4_troubleshooting_faq.md](file:///D:/Smriti_Retail_OS/docs/07-kb/volume_4_troubleshooting_faq.md)
* [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)

## 5. Architecture Decisions
1. **Row-Level Containment:** Dry-run validation APIs must never crash the entire transaction due to row-level content anomalies (like duplicate barcodes, invalid GST values, or wrong HSN lengths). Instead, row errors must be captured inside the per-row `errors` list.
2. **Standard Exception Interception:** Catching `Exception` inside the loop ensures that any validation-related throw (including `ValidationError` or `ValueError`) maps cleanly to the row diagnostics.

## 6. Design Rationale
* **HREP Compliance:** Invalid HSN length notifications are mapped directly to row-level validation arrays so they render as user-friendly inline messages instead of generic backend stack traces.

## 7. Implementation Summary
* Wrapped `_resolve_hsn_code_cached(hsn_raw)` in `validate_import_rows` with a `try...except Exception` block.
* Extracted validation arguments and appended them to `errors` array for that row.
* Registered unit test `test_hsn_invalid_length_validation_catching` in `TestBarcodeHardening` checking that the validation API completes successfully and reports the error cleanly.

## 8. Tests Executed
* Executed the item master unit tests inside the backend container:
  `bench run-tests --module smriti_retail_os.tests.test_item_master_api`

## 9. Verification Results
* **Test Suite execution:** 29/29 tests passed successfully (including the new HSN validation catching test case).

## 10. Known Limitations
* None.

## 11. Future Work
* Wrap other lookup checks (like Brand and Category creation dry-runs) in similar try-except blocks to catch any unexpected database or schema validation exceptions.

## 12. Related ADRs
* `ADR-0009` SMRITI Platform Primitives and Services Standard

## 13. Related RFCs
* None
