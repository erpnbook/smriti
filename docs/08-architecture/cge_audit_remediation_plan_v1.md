---
Document ID: "ARCH-009"
Title: "SMRITI Customer Growth Engine (CGE) — Audit Remediation Plan v1.0"
Owner: "Architecture Team"
Audience: "Architect"
Module: "PSV"
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

# SMRITI Customer Growth Engine (CGE) — Audit Remediation Plan v1.0
**Author**: Jawahar R. Mallah (Founder & Chief Architect, AITDL)
**Maintainer**: AITDL
**Implementation Assistance**: Automated AI development tools
**Status**: Active  
**Date**: 2026-06-19  

This plan governs the remediation of technical findings identified during the June 2026 deep audit of the SMRITI Customer Growth Engine (CGE) v1.0.

---

## 1. CGE Release Readiness Dashboard

```text
Customer Growth Engine (CGE)

Documentation Status:
🟢 Frozen

Architecture Status:
🟢 Frozen

Code Status:
🟢 Production Frozen Baseline (Sprint C Closed)

Release Status:
🟢 Production Ready / Frozen

Production Freeze:
🟢 Closed (All Remediation Sealed)
```

### Overall SMRITI Release Stream Status

| Stream | Status | Detail |
|---|---|---|
| SMRITI Retail OS v1.0.0 | 🟢 Frozen | Core platform stable |
| Governance Package | 🟢 Complete | Compliance checks signed off |
| Documentation | 🟢 Complete | Technical documentation complete |
| CGE Documentation | 🟢 Complete | CGE manuals frozen |
| CGE Audit | 🟢 Complete | Deep audit report generated |
| CGE Remediation | 🟢 Closed | Sprint C Closed, All remediated |
| SPM Architecture | 🟢 Ready | Active / Unlocked |
| PSV Phase 1.3A | 🟢 Ready | Active / Unlocked |

---

## 2. Remediation Schedule

To ensure a structured and risk-isolated rollout, fixes are divided into three sequential Sprints. Each Sprint must pass full unit test suites and architectural compliance checks before proceeding.

### Sprint A: Release Blockers (AUD-01 to AUD-07)
*   **Focus**: Security exploits, double-entry accounting integrity, transaction safety, and concurrency crashes.
*   **Target Completion**: Sprint A is a hard blocker for declaring CGE production-ready.

### Sprint B: High Priority (AUD-08 to AUD-13)
*   **Focus**: System stability under load, query performance, and memory threshold optimization (OOM prevention).
*   **Target Completion**: Immediate post-GA or release candidate validation phase.

### Sprint C: Stabilization (AUD-14 to AUD-18)
*   **Focus**: Expiry scheduling, snapshot de-duplication, resource lockups, and code quality cleanup.

---

## 3. Remediation Registry & Status

| ID | Component | Title / Finding | Severity | Sprint | Status | Target File |
|---|---|---|---|---|---|---|
| **AUD-01** | General Ledger | Reversal of Promotion Expense / Unreconciled Customer Ledger | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-02** | Coupon Engine | POS Invoice Bypass on Coupon Usage Limits | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-03** | Wallet Engine | Wallet negative balance exploit | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-04** | Document Hooks | Missing server-side validation on invoice saving/submission | 🔴 Critical | Sprint A | Closed | [hooks_logic.py](../../apps/smriti_retail_os/smriti_retail_os/hooks_logic.py) |
| **AUD-05** | General Ledger | Journal Entry failure swallowed silently | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-06** | DB Transaction | Manual database commits inside hooks | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-07** | Concurrency | Race condition in sequence generation | 🔴 Critical | Sprint A | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-08** | Document Hooks | Lack of Hook Error Isolation | 🟠 High | Sprint B | Closed | [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py) |
| **AUD-09** | Liability Engine | Liability over-statement (sums loyalty points instead of remaining points) | 🟠 High | Sprint B | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-10** | Rule Evaluator | N+1 Database Queries inside Item Loop | 🟠 High | Sprint B | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-11** | Reconciler | N+1 Database Queries in Daily Wallet Reconciliation | 🟠 High | Sprint B | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-12** | Offline Cache | Offline cache memory exhaustion limit risk (OOM) | 🟠 High | Sprint B | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-13** | Offline Cache | Write-only Offline Cache Bypass | 🟠 High | Sprint B | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-14** | Expiry Scheduler | Missing Wallet/Cashback Expiry Logic | 🟡 Medium | Sprint C | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-15** | Wallet Engine | Cashback Balance Queries Lack Dynamic Expiry Date Filtering | 🟡 Medium | Sprint C | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-16** | Snapshot Job | Duplicate Daily Liability Snapshots | 🟡 Medium | Sprint C | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-17** | Campaign Mgr | Coupon Budget Lockup on Abandoned / Deleted Draft Invoices | 🟡 Medium | Sprint C | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |
| **AUD-18** | Code Quality | Redundant Database Schema Metadata Queries inside Item Loop | 🟢 Low | Sprint C | Closed | [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py) |

---

## 4. Technical Mitigation Specs

### Sprint A (Release Blockers)

#### AUD-01: Wallet Redemption Accounting Fix
*   **Target**: `cge_service.py` $\rightarrow$ `create_double_entry_journal` (Lines 495–508)
*   **Plan**: Credit the customer's specific standard `Accounts Receivable` (Debtors) ledger and link the invoice to reduce customer outstanding. Remove the credit targeting `Promotion Expense` on wallet debit entries.

#### AUD-02: POS Invoice Bypass Fix
*   **Target**: `cge_service.py` $\rightarrow$ `validate_checkout_rules` (Lines 724–743)
*   **Plan**: Count usage codes targeting both `Sales Invoice` and `POS Invoice` docstatus to block rapid parallel terminal checkout exploits:
    ```python
    cust_uses = (
        frappe.db.count("Sales Invoice", {"customer": customer, "coupon_code": coupon_code, "docstatus": ["!=", 2]}) +
        frappe.db.count("POS Invoice", {"customer": customer, "coupon_code": coupon_code, "docstatus": ["!=", 2]})
    )
    ```

#### AUD-03: Wallet Balance Exploit Fix
*   **Target**: `cge_service.py` $\rightarrow$ `CGEWalletLedger.post_transaction`
*   **Plan**: For all entries where `transaction_type == "Debit"`, execute a balance summation check. If the debit amount exceeds the customer's active balance, throw a `ValidationError` to reject the write.

#### AUD-04: Server-Side Validation Hooks Fix
*   **Target**: `hooks_logic.py` $\rightarrow$ `validate_and_reconcile_retail_invoice`
*   **Plan**: Hook SMRITI's coupon rules and wallet balance checks directly into the server-side document validation pipeline. If an invoice contains wallet deductions or coupon codes, perform a full re-validation of dates, campaign budgets, and wallet limits before allowing the document to be saved or submitted.

#### AUD-05: Silent Journal Entry Failure Fix
*   **Target**: `cge_service.py` $\rightarrow$ `post_transaction` and `reverse_transaction`
*   **Plan**: Remove try-except blocks swallowing double-entry errors. If `create_double_entry_journal` fails to submit in ERPNext, throw an exception to abort and roll back the shadow wallet database write.

#### AUD-06: Manual Commits in Hooks Fix
*   **Target**: `cge_service.py` $\rightarrow$ `process_invoice_submit` and `process_invoice_cancel`
*   **Plan**: Remove all instances of `frappe.db.commit()` inside hooks. Allow the standard Frappe framework transaction queue to commit atomically on completion.

#### AUD-07: Concurrency Race Condition Fix
*   **Target**: `cge_service.py` $\rightarrow$ sequence number generation
*   **Plan**: Replace `frappe.db.count() + 1` with Frappe's database-backed atomic naming generator:
    ```python
    from frappe.model.naming import make_autoname
    seq_id = make_autoname("WL-.YYYY.-.#####")
    ```

---

### Sprint B (High Priority)

#### AUD-08: Hook Error Isolation Fix
*   **Target**: `hooks.py` $\rightarrow$ `doc_events`
*   **Plan**: Separate non-critical transaction hooks or wrap CGE hooks in protected execution handlers to log errors without aborting the cashier's main checkout submission.

#### AUD-09: Liability Over-statement Fix
*   **Target**: `cge_service.py` $\rightarrow$ `generate_nightly_liability_snapshot`
*   **Plan**: Update SQL selection to sum `remaining_points` instead of `loyalty_points` in the `tabLoyalty Point Entry` table.

#### AUD-10: Rule Evaluator N+1 Fix
*   **Target**: `cge_service.py` $\rightarrow$ `CGERuleEvaluator.evaluate`
*   **Plan**: Pre-fetch item brands, groups, style codes, and seasons in a single batch query at the beginning of the evaluator:
    ```python
    items_info = {d.name: d for d in frappe.get_all("Item", filters={"name": ["in", item_codes]}, fields=["name", "brand", "item_group", "custom_style_code", "custom_season"])}
    ```

#### AUD-11: Reconciliation N+1 Fix
*   **Target**: `cge_service.py` $\rightarrow$ `reconcile_wallet_liability`
*   **Plan**: Remove customer loop. Execute a single SQL `GROUP BY` query to fetch credit/debit balances in one round-trip.

#### AUD-12: Offline Cache OOM Fix
*   **Target**: `cge_service.py` $\rightarrow$ `get_offline_cache`
*   **Plan**: Restrict coupon code syncing to non-personalized coupons or apply pagination limits based on modified timestamps to avoid huge in-memory JSON serialization blocks.

#### AUD-13: Write-Only Cache Fix
*   **Target**: `cge_service.py` $\rightarrow$ `get_offline_cache`
*   **Plan**: Query Redis for the latest cache entry before performing database operations:
    ```python
    cached = frappe.cache().hget("cge_offline_cache", "latest")
    if cached:
        return cached
    ```

---

### Sprint C (Stabilization)

#### AUD-14 & AUD-15: Wallet Expiries Fix
*   **Target**: `cge_service.py`
*   **Plan**: Register a daily scheduled cron task to update `is_expired = 1` for past-due cashback records. Update all wallet balance calculation methods to filter by `expiry_date >= nowdate()` dynamically.

#### AUD-15: Snapshot De-duplication Fix
*   **Target**: `cge_service.py` $\rightarrow$ `generate_nightly_liability_snapshot`
*   **Plan**: Delete existing snapshots for the current date before inserting the new nightly snapshot.

#### AUD-17: Budget Lockup Fix
*   **Target**: `cge_service.py` $\rightarrow$ `CGECampaignManager`
*   **Plan**: Hook document `on_trash` and `before_cancel` events for draft invoices to immediately release reserved campaign budgets.

#### AUD-18: Schema Queries Fix
*   **Target**: `cge_service.py` $\rightarrow$ `CGERuleEvaluator`
*   **Plan**: Extract `frappe.db.has_column` checks from the item loop, placing them as static variables at the evaluator constructor level.


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