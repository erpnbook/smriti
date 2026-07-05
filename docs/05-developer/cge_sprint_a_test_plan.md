---
Document ID: "DEV-010"
Title: "SMRITI CGE Sprint A — Test Plan"
Owner: "Development Team"
Audience: "Developer"
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

# SMRITI CGE Sprint A — Test Plan
**Focus**: Critical Security & Accounting Fixes (AUD-01 to AUD-07)  
**Version**: 1.1.0  
**Target File**: `docs/cge/CGE_SPRINT_A_TEST_PLAN.md`

---

## 1. Accounting Integrity Tests

### Test Case A-01.1: Wallet Redemption Accounting Entries
*   **Objective**: Verify that cashback wallet debits credit the customer's Accounts Receivable (Debtors) ledger and not the Promotion Expense account.
*   **Procedure**:
    1.  Create a customer and issue Rs. 100 cashback (Credit transaction).
    2.  Submit a Sales Invoice for the customer for Rs. 500 with a custom wallet deduction of Rs. 100.
    3.  Assert the creation of a Journal Entry on invoice submission.
    4.  Verify that the Journal Entry:
        *   Debits the `Cashback Liability` account (Rs. 100).
        *   Credits the customer's standard `Accounts Receivable` account (Rs. 100).
        *   Contains `party_type` = "Customer", `party` = customer name, `reference_type` = "Sales Invoice", and `reference_name` = Invoice name.
    5.  Verify that `Promotion Expense` account balance has not changed.

### Test Case A-01.2: Customer Receivable Outstanding Reconciliation
*   **Objective**: Verify that standard customer outstanding registers decrease by the wallet redemption amount upon Sales Invoice submission.
*   **Procedure**:
    1.  Submit a Sales Invoice for Rs. 1000 with a wallet deduction of Rs. 200.
    2.  Check the `outstanding_amount` field on the submitted Sales Invoice.
    3.  Assert that `outstanding_amount` equals Rs. 800 (not Rs. 1000).

---

## 2. Security & Limit Bypass Tests

### Test Case A-02.1: POS Invoice Coupon Limit Enforcement
*   **Objective**: Verify that customers cannot bypass coupon usage limits by executing checkouts across multiple POS terminals before nightly consolidation.
*   **Procedure**:
    1.  Create a single-use coupon campaign with `custom_max_uses_per_customer = 1`.
    2.  Create a draft POS Invoice for Customer A using the coupon code and submit it.
    3.  Create a second draft POS Invoice for Customer A using the same coupon code.
    4.  Trigger server-side validation on the second POS Invoice.
    5.  Assert that validation throws a `ValidationError` blocking the checkout.

### Test Case A-03.1: Wallet Negative Balance Exploit Prevention
*   **Objective**: Verify that direct API calls cannot debit customer wallets below zero.
*   **Procedure**:
    1.  Create a customer with Rs. 50 wallet balance.
    2.  Submit a direct REST API call or draft invoice containing `custom_wallet_deduction: 150.0`.
    3.  Verify that the server rejects the transaction with a `ValidationError` indicating insufficient balance.
    4.  Verify that the customer's wallet balance remains Rs. 50.

### Test Case A-04.1: Direct API Submission Validation
*   **Objective**: Verify that direct REST API or bulk data uploads of invoices are subjected to full coupon and wallet validations on the server.
*   **Procedure**:
    1.  Bypass the UI and directly call `frappe.get_doc({"doctype": "Sales Invoice", ...}).insert()` with an expired coupon code.
    2.  Assert that insertion or submission throws a Validation Error.

---

## 3. Concurrency & Stress Tests

### Test Case A-07.1: Sequence Generation Uniqueness under Load
*   **Objective**: Verify that concurrent transactions do not cause unique constraint crashes.
*   **Procedure**:
    1.  Spawns 50 threads simulating concurrent wallet transactions.
    2.  Assert that all entries insert successfully with unique sequence IDs.
    3.  Verify that no `DuplicateEntryError` or database unique constraint key collision is thrown.

### Test Case A-07.2: Concurrent Posting Stress Test (AUD-07 Concurrency)
*   **Objective**: Verify that 50 simultaneous credit postings and 50 simultaneous debit postings executed concurrently generate correct sequential sequence IDs without collisions, duplicate errors, or skipped IDs.
*   **Procedure**:
    1.  Bootstrap a test customer with initial credit setup.
    2.  Spawn 50 concurrent worker threads posting Credit transactions of Rs. 10.0 each.
    3.  Spawn 50 concurrent worker threads posting Debit transactions of Rs. 5.0 each.
    4.  Verify that all 100 transactions are completed successfully.
    5.  Assert that `frappe.db.count("SMRITI Wallet Ledger")` has increased exactly by 100.
    6.  Verify that all 100 generated sequence IDs follow the format `WL-YYYY-XXXXX`, are completely unique, and contain no gaps or skipped numbers.

---

## 4. Transactional Rollback Tests

### Test Case A-05.1: Transaction rollback on Journal Entry Failure
*   **Objective**: Verify that CGE shadow wallets roll back if the ERPNext Journal Entry fails.
*   **Procedure**:
    1.  Post a manual wallet adjustment for a customer.
    2.  Mock or simulate a posting error (e.g., locking the posting date inside a closed period).
    3.  Assert that `CGEWalletLedger.post_transaction` raises an exception and no record is added to the `SMRITI Wallet Ledger` table.

### Test Case A-06.1: Rollback of CGE hooks on Invoice submit failure
*   **Objective**: Verify that CGE updates (wallet debit and loyalty points) roll back if a subsequent submit event handler fails.
*   **Procedure**:
    1.  Mock a subsequent submit hook handler for `Sales Invoice` to throw a `ValidationError` (simulating a validation crash).
    2.  Attempt to submit a Sales Invoice with Rs. 100 wallet deduction.
    3.  Verify that the Sales Invoice submission fails and rolls back.
    4.  Assert that no `Debit` transaction was committed to `SMRITI Wallet Ledger` and no points were written.


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