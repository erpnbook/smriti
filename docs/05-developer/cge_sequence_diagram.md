---
Document ID: "DEV-009"
Title: "SMRITI Customer Growth Engine (CGE) — Sequence Diagram Specification"
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

# SMRITI Customer Growth Engine (CGE) — Sequence Diagram Specification

This document details the transaction flow and execution sequences for POS checkout calculations, invoice submissions, cancellations, and nightly reconciliation jobs.

---

## 1. POS Checkout Rules Validation Sequence

When a cashier scans items and applies a coupon/wallet balance, the POS terminal invokes [validate_checkout_rules](../../apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py#L20).

```mermaid
sequenceDiagram
    autonumber
    participant POS as POS Terminal
    participant API as CGE API
    participant LE as Loyalty Evaluator
    participant CM as Campaign Manager
    participant WL as Wallet Ledger
    participant Cache as Redis/Frappe Cache

    POS->>API: validate_checkout_rules(invoice_data)
    
    rect rgb(240, 248, 255)
        Note over API, LE: Step 1: Loyalty Resolution
        API->>LE: evaluate(invoice_mockup)
        LE->>LE: Match Brand, Item Group, Style, Season, Store, Tier
        LE->>LE: Resolve stacking & override priority
        LE-->>API: return items points & tier
    end

    rect rgb(245, 245, 245)
        Note over API, CM: Step 2: Coupon Validation
        API->>CM: validate coupon_code
        CM->>CM: Check validity dates, max uses, limits
        CM->>CM: Check campaign budget
        API->>Cache: reserve_budget(coupon_code, discount, session_id)
        Cache-->>API: Budget reserved (30 min TTL)
    end

    rect rgb(255, 245, 238)
        Note over API, WL: Step 3: Wallet Deduction
        API->>WL: check customer wallet balance
        WL-->>API: return active balance
        Note over API: Deduct wallet up to Net Invoice Total
    end

    API-->>POS: return calculated totals, net_total, item_results
```

---

## 2. Invoice Submit & Cancel Event Hook Sequence

When the invoice is submitted or cancelled, standard event listeners registered in [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py) trigger background execution tasks.

### Invoice Submission

```mermaid
sequenceDiagram
    autonumber
    participant POS as POS Terminal
    participant Hooks as hooks.py (on_submit)
    participant SVC as cge_service.py (process_invoice_submit)
    participant CM as CGECampaignManager
    participant WL as CGEWalletLedger
    participant ERP as ERPNext Accounts

    POS->>Hooks: Submit Invoice
    Hooks->>SVC: process_invoice_submit(doc)

    rect rgb(240, 248, 255)
        Note over SVC, WL: Step 1: Wallet Posting
        SVC->>WL: post_transaction(Debit, wallet_deduction)
        WL->>WL: Uniqueness Idempotency Guard check
        WL->>ERP: create_double_entry_journal()
        ERP-->>WL: JV created & submitted
        WL->>WL: Insert immutable SMRITI Wallet Ledger record
    end

    rect rgb(245, 245, 245)
        Note over SVC, CM: Step 2: Campaign Commit
        SVC->>CM: commit_budget(coupon_code, discount)
        CM->>CM: Remove session cache reservation
        CM->>CM: Increment campaign.budget_consumed
    end

    rect rgb(255, 245, 238)
        Note over SVC: Step 3: Loyalty Point Entry
        SVC->>SVC: Insert Loyalty Point Entry record
    end

    SVC-->>Hooks: Complete
```

### Invoice Cancellation

```mermaid
sequenceDiagram
    autonumber
    participant POS as POS Terminal
    participant Hooks as hooks.py (on_cancel)
    participant SVC as cge_service.py (process_invoice_cancel)
    participant CM as CGECampaignManager
    participant WL as CGEWalletLedger
    participant ERP as ERPNext Accounts

    POS->>Hooks: Cancel Invoice
    Hooks->>SVC: process_invoice_cancel(doc)

    rect rgb(240, 248, 255)
        Note over SVC, WL: Step 1: Wallet Reversal
        SVC->>WL: reverse_transaction(ledger_seq)
        WL->>WL: Fetch original ledger details
        WL->>WL: Generate counter-balancing WL entry (Credit)
        WL->>ERP: create_double_entry_journal(Credit)
        ERP-->>WL: JV created & submitted
        WL->>WL: Insert reversal SMRITI Wallet Ledger record
    end

    rect rgb(245, 245, 245)
        Note over SVC, CM: Step 2: Campaign Reversion
        SVC->>CM: decrement campaign.budget_consumed
    end

    SVC-->>Hooks: Complete
```

---

## 3. Daily Scheduled Reconciliation Sequence

Every night, the scheduler triggers [reconcile_wallet_liability](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L401) to verify database balance consistency.

```mermaid
sequenceDiagram
    autonumber
    participant Cron as hooks.py (daily scheduler)
    participant SVC as cge_service.py (reconcile_wallet_liability)
    participant DB as MariaDB database

    Cron->>SVC: reconcile_wallet_liability()
    
    SVC->>DB: Sum Credits - Debits in tabSMRITI Wallet Ledger
    DB-->>SVC: return ledger_total
    
    SVC->>DB: Sum customer balances
    DB-->>SVC: return wallet_total
    
    SVC->>SVC: Compute variance (ledger_total - wallet_total)
    
    alt Variance detected (mismatch)
        SVC->>DB: Log critical error snapshot
        SVC->>DB: Write SMRITI Wallet Reconciliation Snapshot (Status: Mismatch)
    else No Variance (reconciled)
        SVC->>DB: Write SMRITI Wallet Reconciliation Snapshot (Status: Reconciled)
    end
    
    SVC-->>Cron: Done
```


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