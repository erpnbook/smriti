---
Document ID: "KB-006"
Title: "Coupon Campaigns & Cashback Wallet"
Owner: "Support Team"
Audience: "Support Engineer"
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

# Coupon Campaigns & Cashback Wallet

SMRITI CGE v1.0 implements strict financial controls for coupon budgets and customer cashback accounts, linking transaction ledgers directly with ERPNext double-entry accounting.

---

## 📅 Coupon Campaign Budget Controls

Coupons are grouped under a **SMRITI Coupon Campaign** to restrict marketing exposure:
- **`budget_limit`**: Maximum total discount allowed for the campaign.
- **`stop_on_limit`**: If checked, coupon validation will reject checkouts if the campaign budget is exhausted.
- **`budget_reserved`**: Tracked outstanding discount reservations for active checkout sessions.
- **`budget_consumed`**: Total discount committed from submitted invoices.

### Checkout Reservation Lifecycle
To prevent double-spend or exceeding budget limits when multiple carts checkout concurrently:
1. **Reserve Phase**: When a coupon code is applied in POS, SMRITI reserves the estimated discount amount. It increments `budget_reserved` and caches the reservation in Redis with a 30-minute expiry time.
2. **Commit Phase**: When the invoice is submitted, `budget_reserved` is decremented and `budget_consumed` is incremented with the final discount.
3. **Reversal / Expiry Phase**: If the cart is abandoned or the invoice is cancelled, the reservation expires or is deleted. A nightly background task releases any expired reservations, returning the budget to the pool.

---

## 💳 Immutable Cashback Wallet Ledger (Rule 13 Compliance)

The **SMRITI Wallet Ledger** tracks customer cashback credits (issue) and debits (redemptions).
- **Strict Immutability**: Wallet ledger entries are write-once. The system throws a `frappe.ValidationError` on any update or delete action at the database level.
- **Reversals Only**: Errors must be corrected by posting a counter-balancing counter-transaction (reversal) referencing the original ledger sequence number.
- **Sequence Numbering**: Sequenced as `WL-YYYY-XXXXXX` (e.g. `WL-2026-000001`).

---

## 📊 Double-Entry Liability Accounting

Cashback transactions post automatically into ERPNext general ledger accounts to ensure balance sheets remain compliant and auditable.

### 1. Cashback Issuance (Credit)
When promotional cashback is issued to a customer:
- **Debit**: `Promotion Expense`
- **Credit**: `Cashback Liability` (linked to Customer party)

### 2. Cashback Redemption (Debit)
When the customer redeems their cashback during checkout:
- **Debit**: `Cashback Liability` (linked to Customer party)
- **Credit**: `Sales Invoice Adjustment` (or `Cashback Expense / Revenue` depending on invoice configuration)

### 3. Expiry / Cancellation (Reversal)
When cashback expires or the transaction is reversed:
- **Debit**: `Cashback Liability`
- **Credit**: `Cashback Expiry Income` (or `Promotion Expense` reversal)

*Note: SMRITI resolves and creates these ledger accounts automatically for the matching company abbreviation (e.g., `Cashback Liability - TDP`).*

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