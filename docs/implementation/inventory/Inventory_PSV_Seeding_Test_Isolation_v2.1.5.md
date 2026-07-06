# Implementation Plan - Inventory PSV Seeding Test Isolation v2.1.5

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** In Progress
- **Version:** v2.1.5
- **Date:** 2026-07-06

---

## 1. Objective
Fix a test-isolation bug in the UAT seeding script `smriti_retail_os/tests/seed_psv_uat.py` where data from previous runs is not cleared, causing duplicate records to accumulate and break row-count assertions in Scenarios B and C of the compatibility matrix validation.

## 2. Business Motivation
Ensure that automated UAT verification runs are completely idempotent, reliable, and decoupled from historical database states. This prevents false validation failures in continuous integration/testing loops.

## 3. Scope
- Introduce a shared helper function `_clear_ledger_entries_by_company(company)` in `seed_psv_uat.py` to delete entries from `PSV Ledger Entry` and `SMRITI Party Stock Ledger Entry` tables.
- Call the shared helper in `validate_compatibility_matrix()` before Scenario A, Scenario B, and Scenario C seeding blocks.
- Update `cleanup_uat_data()` to utilize the new shared helper.
- Add explicit assertions in the seeding script to verify the exact number of legacy and new ledger entries generated for Scenarios A, B, and C.
- Document the resolved issue in `KNOWN_ISSUES.md`.
- Run the full suite of validations in the testing environment twice to guarantee test isolation.

## 4. Current State
Currently, `validate_compatibility_matrix()` only clears `PSV Ledger Entry` and `SMRITI Party Stock Ledger Entry` for Scenario A (`COMPAT-TEST-CO`). Scenario B (`COMPAT-NEW-CO`) and Scenario C (`COMPAT-MIXED-CO`) do not clear their respective tables. Because their existence checks use dynamic datetimes and sha256 hashes, subsequent runs generate new unique hashes and insert duplicate records, leading to incorrect aggregation balances and assertion failures.

## 5. Gap Analysis
- **Seeding script**: Lacks pre-seed deletion logic for Scenario B and Scenario C.
- **Cleanup duplication**: Deletion logic is repeated in `cleanup_uat_data()` and `validate_compatibility_matrix()`.
- **Assertions**: Lacks row count validation for ledger entry tables to verify that no duplicate/stale records are present.

## 6. Architecture Impact
None. The changes only affect the UAT validation and seeding script `seed_psv_uat.py`, ensuring cleaner database state during test execution. No business logic or APIs are modified.

## 7. Proposed Design
- Implement the helper:
  ```python
  def _clear_ledger_entries_by_company(company):
      """Removes all PSV Ledger and legacy Party Stock Ledger entries for a given company."""
      frappe.db.delete("PSV Ledger Entry", {"company": company})
      frappe.db.delete("SMRITI Party Stock Ledger Entry", {"company": company})
  ```
- Call the helper in `validate_compatibility_matrix()` before Scenarios A, B, and C.
- Refactor `cleanup_uat_data()` to call `_clear_ledger_entries_by_company(company)`.
- Assert legacy and new table row counts for all three scenarios:
  - Scenario A: legacy=2, new=0
  - Scenario B: legacy=0, new=2
  - Scenario C: legacy=1, new=1

## 8. Files Created
- None.

## 9. Files Modified
- [seed_psv_uat.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/seed_psv_uat.py)
- [README.md](file:///D:/Smriti_Retail_OS/docs/implementation/README.md) (Master Index)
- [KNOWN_ISSUES.md](file:///D:/Smriti_Retail_OS/KNOWN_ISSUES.md)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)

## 10. Dependencies
- No external code or logic dependencies are affected.

## 11. Risks
- None. The companies `COMPAT-TEST-CO`, `COMPAT-NEW-CO`, and `COMPAT-MIXED-CO` are isolated and used solely within this validation module.

## 12. Rollback Strategy
- Discard changes using `git checkout -- smriti_retail_os/tests/seed_psv_uat.py` or `git reset --hard HEAD` to revert to clean state.

## 13. Verification Plan
- Run the full seeding validation twice inside the Docker container to ensure idempotency.
- Verify that compatibility matrix validations pass successfully on both runs.

## 14. Test Plan
- Run command: `bench --site smriti_retail execute smriti_retail_os.tests.seed_psv_uat.run_all_validation`

## 15. Documentation Impact
- A new walkthrough file `Inventory_PSV_Seeding_Test_Isolation_v2.1.5.md` will be created under `docs/walkthrough/inventory/`.
- Walkthrough master index `docs/walkthrough/README.md` will be updated to register the new walkthrough.
- `CHANGELOG.md` and `KNOWLEDGE_BASE.md` will be updated with the details of the fix.
- `KNOWN_ISSUES.md` will be updated with a resolved issue entry.

## 16. Deployment Plan
- Write changes to `D:\Smriti_Retail_OS` (Dev environment).
- Commit and push changes.
- Pull into `F:\Smriti9\apps\smriti_retail_os` (Test environment) and run verification.

## 17. Status
In Progress.

## 18. Related ADRs
- None.

## 19. Related Walkthroughs
- [Inventory_PSV_Seeding_Test_Isolation_v2.1.5.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/inventory/Inventory_PSV_Seeding_Test_Isolation_v2.1.5.md) (To be created upon completion)
