---
Document ID: "REL-003"
Title: "SMRITI CGE Sprint A — Implementation Plan"
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

# SMRITI CGE Sprint A — Implementation Plan
**Focus**: Critical Security & Accounting Fixes (AUD-01 to AUD-07)  
**Version**: 1.1.0  
**Target File**: `docs/cge/CGE_SPRINT_A_IMPLEMENTATION_PLAN.md`

---

## AUD-01: Wallet Redemption Accounting Correctness

### Root Cause
When a customer redeems cashback (wallet Debit), the double-entry journal credits the `Promotion Expense` account rather than the customer's standard `Accounts Receivable` (Debtors) account. This causes an under-statement of promotion costs on redemptions and leaves the customer's Sales Invoice receivable balance open and unreconciled.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `create_double_entry_journal`

### Proposed Code Changes
In `create_double_entry_journal`, modify the `Debit` entry logic:
*   **Debit**: `Cashback Liability` account.
*   **Credit**: Standard customer `Accounts Receivable` account.
*   **Mandatory Linkage Fields**:
    *   `party_type` = "Customer"
    *   `party` = customer name
    *   `reference_type` = "Sales Invoice" (or `POS Invoice` if applicable)
    *   `reference_name` = Invoice name
*   This links the credit line directly to the invoice, reducing the outstanding receivable balance in ERPNext and allowing automatic invoice reconciliation.

### Migration Impact
No database schema changes required. Existing ledger balances must be reconciled manually via Journal Entries if needed.

### Rollback Strategy
Revert the modifications to `create_double_entry_journal` to credit `Promotion Expense`.

### Acceptance Criteria
1.  Wallet redemptions credit the standard `Accounts Receivable` account for the customer.
2.  Redemption line contains proper `party_type`, `party`, `reference_type`, and `reference_name` referencing the invoice.
3.  The customer's invoice outstanding balance is reduced correctly by the redeemed amount.
4.  The promotion expense account balance does not decrease upon redemption.

---

## AUD-02: POS Invoice Bypass on Coupon Usage Limits

### Root Cause
Coupon limits (customer, mobile, daily) only count submitted `"Sales Invoice"` records. POS terminals write to `"POS Invoice"` first (consolidated nightly), enabling customers to bypass limits by checking out at multiple terminals before nightly consolidation.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `validate_checkout_rules`

### Proposed Code Changes
Update all `frappe.db.count` counts for `"Sales Invoice"` to sum matching records from both `"Sales Invoice"` and `"POS Invoice"`, checking that `docstatus != 2` (excluding cancelled):
```python
# For customer limit:
cust_uses = (
    frappe.db.count("Sales Invoice", {"customer": customer, "coupon_code": coupon_code, "docstatus": ["!=", 2]}) +
    frappe.db.count("POS Invoice", {"customer": customer, "coupon_code": coupon_code, "docstatus": ["!=", 2]})
)
```

### Migration Impact
None.

### Rollback Strategy
Revert queries to count only `"Sales Invoice"`.

### Acceptance Criteria
1.  Submitting a POS Invoice with a single-use coupon prevents subsequent checkouts using the same coupon at other terminals (before nightly consolidation).

---

## AUD-03: Wallet Negative Balance Exploit

### Root Cause
`CGEWalletLedger.post_transaction` writes `Debit` transactions without checking if the customer has sufficient active cashback balance, allowing wallet balances to go negative.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `CGEWalletLedger.post_transaction` & new shared service helper.

### Proposed Code Changes
1.  Create a shared service function `get_active_wallet_balance(customer)` inside `cge_service.py`:
    ```python
    def get_active_wallet_balance(customer):
        """Calculates customer's active wallet balance using credits and debits."""
        credits = flt(frappe.db.sql("""
            select sum(amount)
            from `tabSMRITI Wallet Ledger`
            where customer = %s and transaction_type = 'Credit' 
              and is_expired = 0 and (expiry_date is null or expiry_date >= %s)
        """, (customer, nowdate()))[0][0])
        
        debits = flt(frappe.db.get_value("SMRITI Wallet Ledger", {"customer": customer, "transaction_type": "Debit"}, "sum(amount)"))
        return max(0.0, credits - debits)
    ```
2.  Refactor all wallet balance calculations in `validate_checkout_rules`, `get_cge_liability_metrics`, manual adjustment APIs, and reconciliation jobs to use this shared helper.
3.  In `post_transaction`, if `transaction_type == "Debit"`:
    *   Retrieve the customer's active balance using `get_active_wallet_balance(customer)`.
    *   If the requested debit `amount` exceeds the active balance, raise a `frappe.ValidationError` to block the database write.

### Migration Impact
None.

### Rollback Strategy
Remove the validation check from `post_transaction` and inline balance logic.

### Acceptance Criteria
1.  Debit transactions exceeding the customer's active balance are blocked and raise a ValidationError.
2.  Customer wallet balances can never drop below zero.
3.  Single source of truth is established via `get_active_wallet_balance()`.

---

## AUD-04: Missing Server-Side Validation Hooks

### Root Cause
Wallet deductions and coupon limits are only validated in the UI-facing `validate_checkout_rules` API. Directly submitted invoices (via APIs or bulk uploads) bypass all validation controls.

### Affected Files
*   [hooks_logic.py](../../apps/smriti_retail_os/smriti_retail_os/hooks_logic.py) $\rightarrow$ `validate_and_reconcile_retail_invoice`

### Proposed Code Changes
In `validate_and_reconcile_retail_invoice`:
*   Add a check for `custom_wallet_deduction` and `custom_coupon_code`.
*   Call CGE validation routines to verify coupon code expiration, maximum customer usage, daily limits, campaign budgets, and customer wallet balances.
*   Throw a `ValidationError` if any check fails during invoice saving or validation on the server.

### Migration Impact
None.

### Rollback Strategy
Remove coupon/wallet validations from `validate_and_reconcile_retail_invoice`.

### Acceptance Criteria
1.  Direct REST API or bulk imports of Sales Invoices with invalid/expired coupons or excessive wallet deductions are rejected with a Validation Error on the server.

---

## AUD-05: Swallowed Journal Entry Failures

### Root Cause
Exceptions during ERPNext `Journal Entry` submission inside wallet posting are caught, logged, and ignored. The SMRITI shadow wallet ledger transaction still commits, creating a permanent discrepancy between the two databases.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `CGEWalletLedger.post_transaction` and `CGEWalletLedger.reverse_transaction`

### Proposed Code Changes
Remove the try-except wrapper or re-raise the exception inside the `except` block. If the ERPNext `Journal Entry` fails, the exception must propagate up, aborting the CGE database insert and rolling back the transaction.

### Migration Impact
None.

### Rollback Strategy
Wrap the `create_double_entry_journal` call back in the try-except logging block.

### Acceptance Criteria
1.  Any failure to post a Journal Entry in ERPNext cancels and rolls back the SMRITI wallet ledger entry.
2.  Discrepancies between the shadow wallets and standard GL accounts are impossible.

---

## AUD-06: Manual Commits in Hooks

### Root Cause
The hooks `process_invoice_submit` and `process_invoice_cancel` execute manual `frappe.db.commit()` calls. This prevents the framework from rolling back CGE rewards/deductions if a subsequent hook or framework validation fails during invoice submission.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `process_invoice_submit` and `process_invoice_cancel`

### Proposed Code Changes
Remove all manual `frappe.db.commit()` statements inside hook handlers. Allow the framework to commit the database transaction atomically at the end of the HTTP/API request cycle.

### Migration Impact
None.

### Rollback Strategy
Restore `frappe.db.commit()` calls inside hooks.

### Acceptance Criteria
1.  Submitting an invoice that fails on a hook *after* CGE processing successfully rolls back both the invoice and the CGE points/wallet changes.

---

## AUD-07: Concurrency Race Condition in Sequence Generation

### Root Cause
Sequence IDs are generated using `frappe.db.count(...) + 1`. Under high concurrent checkout traffic, multiple terminals generate duplicate IDs, causing unique key crashes on insertion.

### Affected Files
*   [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) $\rightarrow$ `CGEWalletLedger.post_transaction` and `reverse_transaction`

### Proposed Code Changes
Replace manual counting with Frappe's database-backed atomic sequence generator:
```python
from frappe.model.naming import make_autoname
seq_id = make_autoname("WL-.YYYY.-.#####")
```

### Migration Impact
None. Naming conventions remain backward compatible.

### Rollback Strategy
Revert to using `frappe.db.count` for sequence ID generation.

### Acceptance Criteria
1.  Concurrent requests to post wallet ledger transactions generate unique sequence IDs without collisions or database crashes.


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