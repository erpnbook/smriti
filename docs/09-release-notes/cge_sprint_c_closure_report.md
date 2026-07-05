---
Document ID: "REL-006"
Title: "SMRITI CGE Sprint C — Closure & Verification Report"
Owner: "Release Team"
Audience: "Executive / Team"
Module: "CGE"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI CGE Sprint C — Closure & Verification Report
**Focus**: Stabilization & Lifecycle Closure (AUD-14 to AUD-18)  
**Status**: 🟢 Completed & Verified  
**Date**: 2026-06-19  

---

## Executive Summary

This report documents the closure of **Sprint C Stabilization & Lifecycle Closure** for the SMRITI Customer Growth Engine (CGE) v1.0. All 5 Technical Audit findings (AUD-14 to AUD-18) have been resolved, code reviewed, and validated against the unit test suite.

All related unit tests (C-14.1, C-15.1, C-16.1, C-17.1, and C-17.2) executed successfully with a **100% pass rate**.

---

## 🛠️ Remediation & Fix Details

### 1. AUD-14: Wallet Expiry Scheduler (`expire_wallet_credits`)
* **Issue**: Unconsumed credit entries remained active indefinitely, preventing liability expiration.
* **Resolution**: Implemented `expire_wallet_credits()` run daily by the scheduler. It scans for active `Credit` records where `expiry_date < today` and `balance_remaining > 0` and sets `is_expired = 1` and `balance_remaining = 0.0`.
* **Result**: Expired cashback credits are automatically deactivated without affecting consumed credits.

### 2. AUD-15: Configurable Expiry Calculation
* **Issue**: Lack of configurable expiry periods and dynamic date filters for balance queries.
* **Resolution**: Added `wallet_validity_days` to `SMRITI CGE Settings` (defaulting to 90). Created `calculate_wallet_expiry_date(posting_date)` helper utilizing `add_to_date`. Updated `get_active_wallet_balance()` to filter out expired ledger records.
* **Result**: Dynamic credit validities are fully timezone-safe and accurately calculated.

### 3. AUD-16: Snapshot Duplication Isolation
* **Issue**: Nightly liability snapshots generated duplicate entries for the same company/date on multiple runs.
* **Resolution**: Refactored `generate_nightly_liability_snapshot(company)` to use idempotent update-or-create logic. Enforced application-level validation in `SMRITI Liability Snapshot` validate hook, and wrote a migration patch to add a `UNIQUE INDEX` constraint on `(company, snapshot_date)` in the database.
* **Result**: Snapshot data remains strictly clean, preserving document histories, permissions, and audit trails.

### 4. AUD-17: Reserved Budget Release & Safety Sweeper
* **Issue**: Coupon budget reservations remained locked if draft checkout invoices were deleted or if Redis restarted.
* **Resolution**: Added `release_reserved_budget_on_trash` registered on `on_trash` doc events to immediately free reserved budget. Implemented a daily sweeper `cleanup_expired_budget_reservations()` to release reservations older than 24 hours without submitted invoices, and reconcile campaign reserved amounts with Redis to heal from restarts. Included robust string/bytes deserialization handling via `safe_parse_redis_val()`.
* **Result**: Budget lockups from abandoned checkouts and Redis crashes are resolved.

### 5. AUD-18: Redundant Metadata Checks Optimization
* **Issue**: Rules evaluator performed N+1 database column checks inside item loops.
* **Resolution**: Moved `frappe.db.has_column` checks for custom style and season fields to the constructor level in `CGERuleEvaluator`.
* **Result**: Reduced item loop query complexity and improved processing latency.

---

## 🧪 Test Execution & Results

The complete test suite for CGE was run via the bench runner on the development container.

### Test Commands
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail run-tests --module smriti_retail_os.tests.test_cge_rules
```

### Execution Log Summary
```text
Running 21 unspecified-category tests for smriti_retail_os

smriti_retail_os.tests.test_cge_rules.TestCGERulesAndDR
    ✔  test_abandoned_reservation_cleanup
    ✔  test_ar_linkage
    ✔  test_budget_lifecycle_on_trash
    ✔  test_concurrency_stress_test
    ✔  test_coupon_customer_and_mobile_usage_limits
    ✔  test_coupon_date_range_limits
    ✔  test_dr_backup_validation  (7.43s)
    ✔  test_expired_wallet_credits
    ✔  test_idempotency_validation
    ✔  test_liability_overstatement_remaining_points
    ✔  test_loyalty_stacking_exclusions_and_caps
    ✔  test_non_critical_hook_isolation
    ✔  test_offline_cache_redis_and_memory_limit  (3.32s)
    ✔  test_reconciliation_performance_scale
    ✔  test_rule_evaluator_nplus1_performance
    ✔  test_snapshot_idempotency
    ✔  test_snapshot_uniqueness_validation
    ✔  test_validity_setting
    ✔  test_wallet_balance_hook
    ✔  test_wallet_ledger_immutability_rules
    ✔  test_wallet_reconciliation_job

----------------------------------------------------------------------
Ran 21 tests in 21.468s

OK
```

All 21 tests passed successfully. Specifically:
* **`test_expired_wallet_credits` (C-14.1)**: Expired wallet credits scheduler correctly marked `is_expired = 1` and `balance_remaining = 0.0`.
* **`test_validity_setting` (C-15.1)**: Settings-driven expiry date addition was verified.
* **`test_snapshot_idempotency` & `test_snapshot_uniqueness_validation` (C-16.1)**: Snapshot idempotency and manual duplication prevention were confirmed.
* **`test_budget_lifecycle_on_trash` (C-17.1)**: Confirmed budget release on trash/delete of draft invoices.
* **`test_abandoned_reservation_cleanup` (C-17.2)**: Verified safety sweeper cleans up stale/abandoned checkouts.

---

## 🏁 Conclusion

Sprint C stabilization remediation is now officially **Complete**. The CGE module is fully stabilized and ready for GA freeze.


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL