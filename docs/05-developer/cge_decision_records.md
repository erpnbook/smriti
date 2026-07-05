---
Document ID: "DEV-006"
Title: "SMRITI Customer Growth Engine (CGE) — Architecture Decision Records (ADR)"
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

# SMRITI Customer Growth Engine (CGE) — Architecture Decision Records (ADR)

This document records the major architectural design decisions made during the development of the SMRITI Customer Growth Engine (CGE) v1.0, preserving the context and reasoning for future maintainers.

---

## ADR 001: Shadow Ledger Architecture for Wallet/Cashback

### Context
Customers earn and redeem cashback rewards during retail transactions. We need to store these cashback transactions securely without impacting core financial performance.

### Alternatives Considered
1.  **Direct ERPNext General Ledger (GL) Integration**: Posting every wallet credit/debit directly as standard GL entries in `tabGL Entry` under a customer account.
2.  **Separate Custom Database Schema (SMRITI Shadow Ledger)**: Maintaining credits/debits inside a custom append-only table [smriti_wallet_ledger.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.json) and posting aggregated/underlying double-entry Journal Vouchers asynchronously or via hook events.

### Decision
We selected **Alternative 2: SMRITI Shadow Ledger**.

### Rationale
*   **Performance**: Standard ERPNext GL posting involves heavy tax calculations, ledger checks, and database locks. A custom shadow ledger allows fast read/write checkout performance ($< 15\text{ ms}$).
*   **Audit Separation**: High-frequency promotional ledger operations do not pollute standard accounting general ledgers.
*   **Compliance & Accounting Alignment**: Under the hood, [CGEWalletLedger](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L305) automatically creates double-entry ERPNext Journal Entries (Debit Promotion Expense, Credit Cashback Liability) to ensure official accounting books match physical wallet balances.

---

## ADR 002: Dedicated Wallet Liability Snapshots

### Context
Cashback wallets and loyalty points represent a real financial liability for the retailer. We need a way to audit outstanding exposure over time.

### Alternatives Considered
1.  **Dynamic Querying**: Calculating outstanding points and cashback balances on-the-fly whenever requested.
2.  **Daily Scheduled Snapshots**: Capturing daily liability totals and storing them in a dedicated record.

### Decision
We selected **Alternative 2: Daily Scheduled Snapshots**.

### Rationale
*   **Performance**: Summing millions of active ledger entries dynamically degrades database performance.
*   **Historical Tracking**: Dynamic querying cannot provide historical balance states. Storing daily snapshots allows managers to review historical liabilities and identify trends.
*   **Disaster Recovery Verification**: Serves as a baseline checkpoint to verify that database backups and restorations match expected balance states.

---

## ADR 003: Asynchronous/Scheduled Reconciliation

### Context
We must ensure that the sum of all individual customer cashback balances matches the overall ledger total ($\text{Ledger Total} - \text{Wallet Total} = 0.0$).

### Alternatives Considered
1.  **Synchronous Verification**: Calculating and asserting balance matching on every POS transaction.
2.  **Asynchronous Scheduled Jobs**: Running verification daily via a background job.

### Decision
We selected **Alternative 2: Asynchronous Scheduled Jobs**.

### Rationale
*   **Checkout Throughput**: Running a full database sum query across all customers during checkout would introduce transactional delays.
*   **Error Logging**: Moving reconciliation to a scheduled task allows the system to log variance mismatch errors without interrupting active POS checkouts.

---

## ADR 004: Two-Phase Budget Reservation (Reserve-Then-Commit)

### Context
Promotional coupon campaigns operate under strict budget limits. Under high checkout concurrency, multiple cashiers could apply a coupon simultaneously, exceeding the budget limit.

### Alternatives Considered
1.  **Commit-On-Checkout**: Deducting the campaign budget directly when a coupon is validated at the POS terminal.
2.  **Two-Phase Reservation (Reserve-Then-Commit)**: Temporarily reserving the budget in Redis/Frappe Cache during checkout, and committing it to the database only when the invoice is submitted.

### Decision
We selected **Alternative 2: Two-Phase Reservation**.

### Rationale
*   **Handling Abandoned Carts**: Commit-On-Checkout would require complex reversal logic if a customer abandons their cart.
*   **Concurrency Guard**: Temporary reservations are written to Redis with a 30-minute expiration. If the invoice is submitted, [CGECampaignManager](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L215) commits the budget. If the session expires or is cancelled, the reserved budget is automatically released.

---

## ADR 005: Boundary Isolation between CGE and SPM

### Context
SMRITI has two reward modules: Customer Growth Engine (CGE) and Sales Performance Management (SPM).

### Alternatives Considered
1.  **Unified Reward Subsystem**: Creating a single module to handle both customer cashback and sales commission payouts.
2.  **Isolated Bounded Contexts**: Separating CGE (customer incentives) and SPM (employee performance commissions) into isolated packages.

### Decision
We selected **Alternative 2: Isolated Bounded Contexts**.

### Rationale
*   **Domain Separation**: CGE deals with customer incentives (marketing campaigns, loyalty rules, point entries). SPM deals with employee incentives (sales targets, leaderboards, commission rates).
*   **Security & Privacy**: Employee commission records contain sensitive payroll data. Separating SPM ensures that cashiers and auditors do not have access to internal payroll records.
*   **Independent Lifecycles**: Isolating CGE and SPM allows teams to update customer marketing policies without affecting employee payroll logic.


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