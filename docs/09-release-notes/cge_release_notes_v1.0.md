---
Document ID: "REL-001"
Title: "SMRITI Customer Growth Engine (CGE) — Release Notes v1.0"
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

# SMRITI Customer Growth Engine (CGE) — Release Notes v1.0

This document contains the release notes for the SMRITI Customer Growth Engine (CGE) v1.0 subsystem, marking its freeze as a Release Candidate (v1.0-RC).

---

## 1. Version Profile

*   **Subsystem**: SMRITI Customer Growth Engine (CGE)
*   **Version**: 1.0-RC
*   **Release Date**: 2026-06-19
*   **Governance Status**: **FEATURE FREEZE ENABLED**
*   **Architecture Review**: PASS
*   **Security Review**: PASS
*   **Ledger Integrity Review**: PASS
*   **Disaster Recovery Review**: PASS
*   **Performance Review**: PASS

---

## 2. Feature Summary

CGE v1.0 is a complete operational subsystem for managing promotions, coupons, budgets, loyalty rules, and cashback ledgering.

### Loyalty Rules Engine
*   Implemented [CGERuleEvaluator](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L24) for item-level point calculation.
*   Supports matching on Brand, Group, Style, Season, Store, Customer Group, and Tier.
*   Enforces priority override logic, exclusion rule dominance, stacking multiplier resolution, and custom points accumulation caps.

### POS Checkout Rule Pipeline
*   Exposes checkout pipeline endpoint [validate_checkout_rules](../../apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py#L20).
*   Resolves loyalty points, coupon discounts, and wallet deductions in a single execution step.
*   Supports coupon validation policies (start/expiry date checks, maximum usages per customer, mobile number mapping, and daily usage limits).

### Campaign Budget Control
*   Prevents campaign budget overruns with [CGECampaignManager](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L215).
*   Reserves coupon campaign discount budgets in Redis/Frappe cache during POS sessions (30-minute expiration).
*   Commits budget consumption upon POS Invoice submission and cancels/reverts allocations upon invoice cancellation.

### Cashback Wallet Ledger
*   Created append-only [smriti_wallet_ledger.json](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_ledger/smriti_wallet_ledger.json) with database-level immutability.
*   Forces double-entry bookkeeping by creating matching Journal Entries inside ERPNext for cashback credits and debits.
*   Supports manual credit/debit adjustments and reversal operations.

### CGE Studio UI
*   Main standalone page route `/app/smriti-cge` styled using SMRITI Navy (`#1A2B5C`) + Blue (`#2563EB`) themes.
*   Provides Loyalty, Coupon, and Cashback Wallet tabs with real-time audit logs and remarks.
*   Dashboard widgets display outstanding point liabilities, cashback exposure, and coupon budget allocations with setting-driven Amber/Red warning indicators.

---

## 3. Stabilization & Hardening (Sprint 5A Updates)

*   **Configurable Warning Thresholds**: Amber and Red warning thresholds are managed within the Settings database.
*   **Audit Reason Tracking**: Manual adjustments and reversals require a remarks text and an audit classification type.
*   **Daily Wallet Reconciliation**: Computes net ledger transactions, compares them against customer wallet balances, and stores results in [SMRITI Wallet Reconciliation Snapshot](../../apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_wallet_reconciliation_snapshot).
*   **Scale-Curve Performance Benchmarks**: Benchmarked up to 5,000 active rules, verifying scaling latency performance under load.

---

## 4. Governance Freeze & Next Steps

CGE is locked as a **Release Candidate**. Only the following changes are permitted:
*   Critical bug fixes
*   Security patches
*   Performance optimizations
*   Documentation updates

Development is transitioning to the **SMRITI Sales Performance Management (SPM)** bounded context, situated under `smriti_retail_os/spm/`.


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