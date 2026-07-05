---
Document ID: "API-001"
Title: "SMRITI Customer Growth Engine (CGE) — API Reference Manual v1.0"
Owner: "Integration Team"
Audience: "API Integrator"
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

# SMRITI Customer Growth Engine (CGE) — API Reference Manual v1.0

This document describes all whitelisted API endpoints exposed by the SMRITI Customer Growth Engine (CGE) in [cge_api.py](../../apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py). These methods are whitelisted for execution from the POS terminal, CGE Studio, or external integrations.

---

## 1. POS Checkout Rules Engine

### `validate_checkout_rules`
Runs the checkout rule pipeline to calculate promotional discounts, loyalty points earned, and wallet cashback deductions.

*   **Function Signature**: `validate_checkout_rules(invoice_data)`
*   **Whitelisted**: Yes (`frappe.whitelist()`)
*   **Method Type**: POST / GET
*   **Input Parameter**:
    *   `invoice_data` (Object/String): A JSON object or serialized string containing:
        ```json
        {
          "customer": "CUST-00001",
          "company": "SMRITI Retail Ltd",
          "coupon_code": "HOLIDAY10",
          "use_wallet_balance": 150.00,
          "session_id": "pos_session_abc123",
          "items": [
            {
              "item_code": "ITEM-9988",
              "qty": 2,
              "rate": 500.00,
              "warehouse": "Stores - TDP"
            }
          ]
        }
        ```
*   **Response Format**:
    ```json
    {
      "loyalty_points_earned": 20.0,
      "loyalty_tier": "Platinum Tier",
      "coupon_discount": 100.0,
      "wallet_deduction": 150.0,
      "net_total": 750.0,
      "items": [
        {
          "item_code": "ITEM-9988",
          "multiplier": 2.0,
          "bonus_points": 0.0,
          "cap": 0.0,
          "excluded": false,
          "points_earned": 20.0
        }
      ]
    }
    ```
*   **Exceptions**: Throws `frappe.ValidationError` if:
    *   The coupon code is invalid, expired, or has reached usage/mobile/daily limits.
    *   The campaign budget limit is exceeded (with `stop_on_limit` enabled).
    *   The requested wallet deduction exceeds the customer's active cashback balance.

---

### `get_offline_cache`
Exposes the complete serialized cache of loyalty rules, tiers, and campaign coupons for local POS caching.

*   **Function Signature**: `get_offline_cache()`
*   **Response Format**:
    ```json
    {
      "checksum": "d41d8cd98f00b204e9800998ecf8427e",
      "data": {
        "tiers": [...],
        "rules": [...],
        "campaigns": [...],
        "coupons": [...]
      }
    }
    ```

---

## 2. Cashback Wallet Management

### `get_wallet_ledger`
Retrieves logs from the SMRITI Wallet Ledger. Access is restricted to auditors, managers, and admins.

*   **Function Signature**: `get_wallet_ledger(customer=None, transaction_type=None, limit=50)`
*   **Role Gate**: `System Manager`, `SMRITI Store Manager`, `SMRITI Auditor`
*   **Response Format**:
    ```json
    [
      {
        "name": "WL-2026-000104",
        "ledger_sequence": "WL-2026-000104",
        "customer": "CUST-00001",
        "wallet_type": "Promo Cashback",
        "transaction_type": "Debit",
        "amount": 150.00,
        "reference_invoice": "SINV-00284",
        "is_reversal": 0,
        "remarks": "Redemption during POS Checkout",
        "adjustment_reason_type": "POS Transaction",
        "creation": "2026-06-19 12:00:00"
      }
    ]
    ```

---

### `post_wallet_adjustment`
Creates a manual audit-logged ledger entry to adjust a customer's wallet balance.

*   **Function Signature**: `post_wallet_adjustment(customer, wallet_type, transaction_type, amount, remarks, adjustment_reason_type, company=None)`
*   **Role Gate**: `System Manager`, `SMRITI Store Manager`
*   **Input Parameters**:
    *   `customer` (String, Required)
    *   `wallet_type` (String, Required)
    *   `transaction_type` (String, Required): `Debit` or `Credit`
    *   `amount` (Float, Required): Must be positive.
    *   `remarks` (String, Required): Audit reason.
    *   `adjustment_reason_type` (String, Required): Selection from:
        *   `Manual Credit`
        *   `Manual Debit`
        *   `Customer Complaint`
        *   `Campaign Correction`
        *   `System`
*   **Response Format**:
    ```json
    {
      "success": true,
      "name": "WL-2026-000105",
      "ledger_sequence": "WL-2026-000105",
      "journal_entry": "JV-2026-00021"
    }
    ```

---

### `reverse_wallet_transaction`
Executes a wallet ledger reversal by posting a counter-balancing transaction.

*   **Function Signature**: `reverse_wallet_transaction(ledger_seq, reason)`
*   **Role Gate**: `System Manager`, `SMRITI Store Manager`
*   **Input Parameters**:
    *   `ledger_seq` (String, Required): Target ledger transaction ID.
    *   `reason` (String, Required): Reversal justification.
*   **Response Format**:
    ```json
    {
      "success": true,
      "name": "WL-2026-000106",
      "ledger_sequence": "WL-2026-000106",
      "journal_entry": "JV-2026-00022"
    }
    ```

---

## 3. CGE Studio Dashboard Metrics

### `get_cge_liability_metrics`
Calculates total promotional point liabilities, outstanding wallet balance reserves, active campaign exposures, and retrieves warning thresholds.

*   **Function Signature**: `get_cge_liability_metrics()`
*   **Role Gate**: `System Manager`, `SMRITI Store Manager`, `SMRITI Auditor`
*   **Response Format**:
    ```json
    {
      "loyalty_liability": 45000.0,
      "cashback_liability": 125300.00,
      "coupon_exposure": 85000.0,
      "total_liability": 255300.0,
      "amber_threshold": 100000.0,
      "red_threshold": 250000.0
    }
    ```

---

### `get_campaigns_with_utilization`
Returns active coupon campaigns with real-time budget utilization statistics.

*   **Function Signature**: `get_campaigns_with_utilization()`
*   **Response Format**:
    ```json
    [
      {
        "name": "CAMPAIGN-001",
        "campaign_name": "Summer Sale",
        "campaign_type": "Discount Coupon",
        "budget_limit": 50000.0,
        "budget_reserved": 12000.0,
        "budget_consumed": 28000.0,
        "status": "Active",
        "utilization": 80.0
      }
    ]
    ```

---

## 4. CGE Studio Document Operations

These endpoints process updates for rules, tiers, and campaigns from the Studio UI:
*   `save_coupon_campaign(campaign_data)`
*   `save_loyalty_rule(rule_data)`
*   `save_loyalty_tier(tier_data)`

*   **Role Gate**: `System Manager`, `SMRITI Store Manager`
*   **Method Type**: POST
*   **Response Format**: Returns the database primary key `name` of the saved document.


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