---
Document ID: "ADMIN-006"
Title: "SMRITI Customer Growth Engine (CGE) — Security & Permission Matrix v1.0"
Owner: "Administration Team"
Audience: "Administrator"
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

# SMRITI Customer Growth Engine (CGE) — Security & Permission Matrix v1.0

This document defines the Role-Based Access Control (RBAC) rules, API authorization gates, and database-level security policies implemented for the SMRITI Customer Growth Engine (CGE) v1.0.

---

## 1. System Roles in CGE

Security in CGE is enforced using standard SMRITI and system roles:
*   **System Manager / Administrator**: Full configuration access, rule definitions, and manual ledger adjustments.
*   **SMRITI Store Manager**: Operational authority. Can perform manual wallet adjustments, execute reversals, and adjust CGE configurations.
*   **SMRITI Auditor**: Read-only access to ledger records, reconciliation logs, and liability exposures for financial verification.
*   **SMRITI Marketing Manager**: Can edit loyalty tiers, loyalty rules, and coupon campaigns. Cannot perform wallet adjustments.
*   **Cashier**: Executes checkout calculations, applies coupons, and triggers wallet deductions during standard POS sessions.

---

## 2. API Endpoint Access Matrix

API access is restricted inside [cge_api.py](../../apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py) using the active user's roles.

| Whitelisted API Endpoint | Restricted Roles | Audit Level |
| :--- | :--- | :--- |
| `validate_checkout_rules` | Cashier, SMRITI Store Manager, System Manager | None (Read-only calculation) |
| `get_offline_cache` | Cashier, SMRITI Store Manager, System Manager | None (Cache lookup) |
| `get_wallet_ledger` | SMRITI Auditor, SMRITI Store Manager, System Manager | None (Read-only logs) |
| `post_wallet_adjustment` | SMRITI Store Manager, System Manager | **High** (Logs user, amount, remarks, categories) |
| `reverse_wallet_transaction`| SMRITI Store Manager, System Manager | **High** (Logs user, original transaction, remarks) |
| `get_cge_liability_metrics` | SMRITI Auditor, SMRITI Store Manager, System Manager | None (Read-only summary) |
| `get_campaigns_with_utilization`| SMRITI Marketing Manager, SMRITI Store Manager, System Manager | None (Read-only summary) |
| `save_coupon_campaign` | SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Medium (Tracked changes) |
| `save_loyalty_rule` | SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Medium (Tracked changes) |
| `save_loyalty_tier` | SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Medium (Tracked changes) |

---

## 3. Database DocType Permissions (RBAC)

Below is the database level permission mapping configured in CGE fixtures:

| DocType Name | Allowed Roles | Read | Write | Create | Delete |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **SMRITI CGE Settings** | SMRITI Store Manager, System Manager | Yes | Yes | Yes | No |
| | SMRITI Auditor, Cashier | Yes | No | No | No |
| **SMRITI Wallet Ledger** | SMRITI Store Manager, System Manager, SMRITI Auditor | Yes | No | Yes | No |
| | Cashier | No | No | No | No |
| **SMRITI Loyalty Tier** | SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Yes | Yes | Yes | Yes |
| | SMRITI Auditor, Cashier | Yes | No | No | No |
| **SMRITI Loyalty Rule** | SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Yes | Yes | Yes | Yes |
| | SMRITI Auditor, Cashier | Yes | No | No | No |
| **SMRITI Coupon Campaign**| SMRITI Marketing Manager, SMRITI Store Manager, System Manager | Yes | Yes | Yes | Yes |
| | SMRITI Auditor, Cashier | Yes | No | No | No |
| **SMRITI Wallet Reconciliation Snapshot** | SMRITI Store Manager, System Manager, SMRITI Auditor | Yes | No | No | No |
| **SMRITI Rule Evaluation Log** | SMRITI Store Manager, System Manager, SMRITI Auditor | Yes | No | No | No |

---

## 4. Ledger Immutability Protection

Regardless of RBAC write permissions, database-level changes to [smriti_wallet_ledger.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.json) records are blocked:
*   **Update Restriction**: The `before_save` hook blocks updates. Any edit throws a validation error.
*   **Trash Restriction**: The `on_trash` hook blocks deletions. Any deletion attempt is blocked.
*   **Ledger Corrections**: Adjustments must be performed using counter-entries (reversals), ensuring a permanent audit trail.

---

## 5. Audit Logging Architecture

Manual adjustments and reversals are logged in the system Activity Log:
1.  **Manual Adjustment Auditing**:
    *   Saves the previous customer wallet balance.
    *   Requires a `remarks` string and a classification code in `adjustment_reason_type`.
    *   Logs the user identity, transaction type, amount, remarks, reason, and balance changes.
2.  **Manual Reversal Auditing**:
    *   Logs the original ledger ID.
    *   Requires a reversal reason.
    *   Records a log entry capturing the user identity, original transaction details, and reversal justification.


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