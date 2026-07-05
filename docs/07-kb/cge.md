---
Document ID: "KB-004"
Title: "Frequently Asked Questions — SMRITI CGE"
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

# Frequently Asked Questions — SMRITI CGE

Here are answers to the most common questions regarding the SMRITI Customer Growth Engine (CGE) v1.0.

---

## 🎖️ Loyalty & Points

### Q1: How is the customer's loyalty tier determined?
A customer's tier is automatically recalculated during checkout based on the sum of their active, non-expired loyalty points inside the ERPNext table `tabLoyalty Point Entry`. Tiers are checked against active **SMRITI Loyalty Tier** rules.

### Q2: Why are loyalty rules not stacking for certain items?
If any matching **SMRITI Loyalty Rule** has `allow_stack = 0 (False)`, stacking is disabled for that item. The engine will select only the highest priority rule. Check your loyalty rule definitions to ensure all stacked multipliers have `allow_stack` enabled.

### Q3: What happens if a customer matches an exclusion rule?
If an item matches a rule of type `Exclusion`, it earns zero loyalty points, regardless of other matching brand or category multipliers.

---

## 💳 Coupon Campaigns & Budgets

### Q4: Can a customer use a coupon code if the campaign's budget is full?
If the campaign has `stop_on_limit` checked, and the sum of `budget_reserved` and `budget_consumed` exceeds `budget_limit`, the coupon will be rejected at checkout.

### Q5: How long do coupon budget reservations last?
Reservations last for exactly **30 minutes** from the moment the coupon is applied in the cart. If the invoice is not submitted within 30 minutes, the reservation expires and the budget is released back to the campaign pool.

---

## 📈 Accounting & Cashback

### Q6: Can a cashier edit or delete a wallet transaction record?
No. The **SMRITI Wallet Ledger** is strictly immutable. If a mistake is made, a counter-acting reversal transaction must be posted. The system blocks all SQL/ORM edit or delete commands.

### Q7: Where do cashback transactions post in ERPNext?
All wallet credits and debits post directly as Journal Entries in ERPNext under standard chart accounts (e.g. `Promotion Expense - TDP` and `Cashback Liability - TDP`).

### Q8: How often is the liability snapshot generated?
SMRITI runs a background scheduler nightly at **01:00 AM** to sum all active loyalty points, cashback wallet balances, and outstanding coupon reservations, saving the result into `SMRITI Liability Snapshot` for audit reporting. Daily snapshots older than 90 days are deleted at **01:30 AM**, keeping only monthly snapshots for up to 5 years.

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