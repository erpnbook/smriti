---
Document ID: "REL-007"
Title: "SMRITI CGE Sprint C — Final Stabilization Implementation Plan"
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

# SMRITI CGE Sprint C — Final Stabilization Implementation Plan

This plan governs the implementation of the final stabilization phase (**AUD-14** to **AUD-17**) for the SMRITI Customer Growth Engine (CGE) v1.0.

---

## 1. Overview of Tasks

### AUD-14: Wallet Credit Expiry Scheduler
*   **Target File**: [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py), [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py)
*   **Goal**: Periodically check and expire cashback wallet credits that have passed their expiry date.
*   **Implementation**:
    - Add `expire_wallet_credits()` function in `cge_service.py` to run SQL:
      ```sql
      UPDATE `tabSMRITI Wallet Ledger`
      SET is_expired = 1
      WHERE transaction_type = 'Credit'
        AND expiry_date < %s
        AND is_expired = 0
      ```
    - Register `smriti_retail_os.cge.service.cge_service.expire_wallet_credits` in the daily scheduled tasks in `hooks.py`.

### AUD-15: Expiry Calculation Correctness & Timezones
*   **Target File**: [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py), [smriti_cge_settings.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_cge_settings/smriti_cge_settings.json)
*   **Goal**: Enforce correct, timezone-safe 90-day credit validity logic dynamically.
*   **Implementation**:
    - Add `wallet_validity_days` (Int, default 90) configuration field to `SMRITI CGE Settings` DocType.
    - Update `CGEWalletLedger.post_transaction()` to compute and set `expiry_date` for Credit entries:
      ```python
      if transaction_type == "Credit" and not expiry_date:
          validity_days = frappe.db.get_single_value("SMRITI CGE Settings", "wallet_validity_days")
          validity_days = int(validity_days) if validity_days is not None else 90
          expiry_date = add_to_date(getdate(nowdate()), days=validity_days)
      ```
    - Ensure date parsing uses standard `getdate(nowdate())` to remain timezone-resilient.

### AUD-16: Snapshot Duplication Prevention & Multi-Company Support
*   **Target File**: [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py), [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py), [smriti_liability_snapshot.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_liability_snapshot/smriti_liability_snapshot.json), [smriti_wallet_ledger.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.json)
*   **Goal**: Track liability snapshots per company and prevent duplicate records.
*   **Implementation**:
    - Add `company` field to `SMRITI Wallet Ledger` and `SMRITI Liability Snapshot` DocTypes.
    - Refactored `post_transaction` to persist `company` on `SMRITI Wallet Ledger`.
    - Update `generate_nightly_liability_snapshot(company)` to:
      1. Calculate loyalty and wallet liabilities filtered by the given company.
      2. Check for existing snapshot for `(company, snapshot_date)`.
      3. If found, delete the old document before inserting the new snapshot.
    - Implement a parent scheduled task `generate_all_liability_snapshots()` that loops through active companies and triggers the snapshot. Register it in `hooks.py` `daily` scheduler.

### AUD-17: Campaign Reserved Budget Release
*   **Target File**: [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py), [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py), [hooks_logic.py](../../apps/smriti_retail_os/smriti_retail_os/hooks_logic.py)
*   **Goal**: Release campaign budget reservations immediately when draft invoices are deleted or cancelled.
*   **Implementation**:
    - Add `release_reserved_budget_on_trash(doc, method=None)` in `hooks_logic.py`.
    - Retrieve active budget reservations for the invoice from Redis cache, decrement `budget_reserved` on the campaign, and clear the reservation key.
    - Wire `release_reserved_budget_on_trash` to `on_trash` doc_events for both `Sales Invoice` and `POS Invoice` in `hooks.py`.

---

## 2. Verification Plan

### Automated Tests
*   Run the complete test suite:
    `docker exec smriti_retail-backend-1 bench --site smriti_retail run-tests --app smriti_retail_os --module smriti_retail_os.tests.test_cge_rules`
*   Append unit tests in `test_cge_rules.py` checking:
    1.  **Wallet Expiry Job**: Post credits, set their expiry date to yesterday, run `expire_wallet_credits()`, verify `is_expired` becomes 1, and ensure `get_active_wallet_balance` excludes it.
    2.  **Date Validity Check**: Post credit without expiry, verify `expiry_date` is set to exactly 90 days in the future.
    3.  **Liability Snapshot Uniqueness**: Trigger snapshot for the same company twice on the same date and verify only one snapshot document exists.
    4.  **Budget Release on Delete**: Apply a coupon, verify budget is reserved in Redis/DB, delete the draft Sales Invoice, and verify campaign budget is fully released.


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