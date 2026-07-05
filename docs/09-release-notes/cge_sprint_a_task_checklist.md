---
Document ID: "REL-004"
Title: "SMRITI CGE Sprint A — Task Checklist"
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

# SMRITI CGE Sprint A — Task Checklist
**Focus**: Critical Security & Accounting Fixes (AUD-01 to AUD-07)  
**Version**: 1.1.0  
**Target File**: `docs/cge/CGE_SPRINT_A_TASK_CHECKLIST.md`

---

## AUD-01: Wallet Redemption Accounting Correctness
- [ ] Modify `create_double_entry_journal` in `cge_service.py` to credit standard `Accounts Receivable` (Debtors).
- [ ] Incorporate standard receivable line fields: `party_type = "Customer"`, `party = customer`, `reference_type = "Sales Invoice"`, and `reference_name = reference_invoice`.
- [ ] Verify that customer receivable outstandings decrease correctly by the redeemed amount.
- [ ] Verify that promotion expense accounts are not credited on redemption.

## AUD-02: POS Invoice Bypass on Coupon Usage Limits
- [ ] Update customer usage count queries in `cge_service.py` to query both `Sales Invoice` and `POS Invoice` docstatus.
- [ ] Update mobile usage count queries in `cge_service.py` to check both `Sales Invoice` and `POS Invoice` tables.
- [ ] Update daily usage count queries in `cge_service.py` to sum both `Sales Invoice` and `POS Invoice` docstatus.

## AUD-03: Wallet Negative Balance Exploit
- [ ] Create shared service function `get_active_wallet_balance(customer)` in `cge_service.py`.
- [ ] Refactor calculations in `validate_checkout_rules`, manual adjustments, reconciliations, and dashboard APIs to use `get_active_wallet_balance`.
- [ ] Implement active balance calculation check in `CGEWalletLedger.post_transaction`.
- [ ] Raise `frappe.ValidationError` inside `post_transaction` if a debit exceeds the calculated active wallet balance.
- [ ] Add unit test verifying that a negative wallet balance exploit is blocked.

## AUD-04: Missing Server-Side Validation Hooks
- [ ] Add coupon rules validation inside `validate_and_reconcile_retail_invoice` in `hooks_logic.py`.
- [ ] Add wallet balance validation checks inside `validate_and_reconcile_retail_invoice` in `hooks_logic.py`.
- [ ] Raise `frappe.ValidationError` during invoice save/submit lifecycle if checks fail on the server.

## AUD-05: Swallowed Journal Entry Failures
- [ ] Remove `try-except` swallowing from `CGEWalletLedger.post_transaction` and propagate exceptions to trigger transaction rollback.
- [ ] Remove `try-except` swallowing from `CGEWalletLedger.reverse_transaction` and propagate exceptions.
- [ ] Verify that a failed ERPNext Journal Entry successfully rolls back the SMRITI shadow wallet transaction.

## AUD-06: Manual Commits in Hooks
- [ ] Remove manual `frappe.db.commit()` statements inside `process_invoice_submit`.
- [ ] Remove manual `frappe.db.commit()` statements inside `process_invoice_cancel`.
- [ ] Verify that a hook failure occurring after CGE processing successfully rolls back all CGE changes.

## AUD-07: Concurrency Race Condition in Sequence Generation
- [ ] Replace `frappe.db.count() + 1` with `make_autoname("WL-.YYYY.-.#####")` in `post_transaction`.
- [ ] Replace `frappe.db.count() + 1` with `make_autoname("WL-.YYYY.-.#####")` in `reverse_transaction`.
- [ ] Implement concurrency stress test case `A-07.2` simulating 50 simultaneous credits and 50 simultaneous debits.
- [ ] Verify sequence uniqueness and verify no gaps/collisions are generated.


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