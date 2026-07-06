# Walkthrough - Inventory PSV Seeding Test Isolation v2.1.5

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** Completed
- **Version:** v2.1.5
- **Date:** 2026-07-06

---

## 1. Purpose
This walkthrough documents the design and execution of the test-isolation fix implemented in the automated UAT seeding script `seed_psv_uat.py`. The fix prevents ledger data from leaking across consecutive validation runs, thereby restoring matrix validation accuracy.

## 2. Scope
- Introduce a centralized helper `_clear_ledger_entries_by_company(company)` in the seeding script to handle ledger state teardown.
- Update `validate_compatibility_matrix()` and `cleanup_uat_data()` to utilize this helper.
- Verify row-count assertions across Scenarios A, B, and C.
- Document and resolve `KI-008` in `KNOWN_ISSUES.md`.

## 3. Files Created
- None.

## 4. Files Modified
- [seed_psv_uat.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/seed_psv_uat.py)
- [KNOWN_ISSUES.md](file:///D:/Smriti_Retail_OS/KNOWN_ISSUES.md)
- [README.md](file:///D:/Smriti_Retail_OS/docs/implementation/README.md) (Implementation Plan Index)

## 5. Architecture Decisions
- **Centralized Teardown Helper**: Extracted the deletion logic into a reusable function `_clear_ledger_entries_by_company(company)` to comply with the DRY principle and ensure that additions of future ledger models only require updates in a single, well-defined location.

## 6. Design Rationale
- Scenario A has a pre-existing idempotency check, but Scenario B and Scenario C use dynamic hashes containing timestamps, which circumvented that check. Clearing the ledger tables by company before seeding ensures complete test isolation without altering the core unique hash algorithm.

## 7. Implementation Summary
- Added `_clear_ledger_entries_by_company(company)`:
  ```python
  def _clear_ledger_entries_by_company(company):
      """Removes all PSV Ledger and legacy Party Stock Ledger entries for a given company."""
      frappe.db.delete("PSV Ledger Entry", {"company": company})
      frappe.db.delete("SMRITI Party Stock Ledger Entry", {"company": company})
  ```
- Called this helper in `validate_compatibility_matrix()` for:
  - `COMPAT-TEST-CO` (Scenario A)
  - `COMPAT-NEW-CO` (Scenario B)
  - `COMPAT-MIXED-CO` (Scenario C)
- Refactored `cleanup_uat_data()` to clean up companies using the new helper.
- Added row count assertions to the three compatibility scenarios.
- Updated `KNOWN_ISSUES.md` under `## Resolved in v2.1.5`.

## 8. Tests Executed
- Executed the main validation runner inside the Docker test environment:
  - Command: `bench --site smriti_retail execute smriti_retail_os.tests.seed_psv_uat.run_all_validation`
- Executed the cleanup function inside the Docker test environment:
  - Command: `bench --site smriti_retail execute smriti_retail_os.tests.seed_psv_uat.cleanup_uat_data`

## 9. Verification Results
- First Run: Completed successfully with `✅ VALIDATION PHASE COMPLETE` and `compatibility: PASS`.
- Second Run (without cleanup): Completed successfully, confirming perfect isolation between runs.
- Cleanup Run: Completed without errors.
- Third Run (after cleanup): Completed successfully, verifying the entire cleanup-to-reseed lifecycle.

## 10. Known Limitations
- None.

## 11. Future Work
- None.

## 12. Related ADRs
- None.

## 13. Related RFCs
- None.
