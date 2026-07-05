---
Document ID: "KB-012"
Title: "Loyalty Engine — Configuration & Stacking Rules"
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

# Loyalty Engine — Configuration & Stacking Rules

The **SMRITI Loyalty Engine** dynamically computes points multipliers during sales invoicing based on the customer's historical loyalty tier and the items in their cart. 

---

## 🎖️ Loyalty Tiers

Loyalty tiers are configured via **SMRITI Loyalty Tier** records:
- **`min_points`**: The points balance threshold needed to qualify for the tier.
- **`tier_multiplier`**: A base point multiplier applied to all transactions for customers in this tier.
- **`active`**: Enable or disable the tier.

Customers are automatically mapped to the highest matching active tier based on the sum of their active loyalty points (`tabLoyalty Point Entry.loyalty_points`).

---

## 🎯 Loyalty Rules

Loyalty rules are configured via **SMRITI Loyalty Rule** records. They let you target specific subsets of products, stores, or customers.

### Dimensions
A rule can target product or customer attributes:
- **`Brand`**: E.g., apply a multiplier on items from *Raymond*.
- **`Item Group`**: E.g., apply a rule on *Footwear*.
- **`Style`**: E.g., apply a rule on a specific article/style code.
- **`Season`**: Target seasonal merchandise.
- **`Store`**: Limit the rule to specific warehouses.
- **`Customer Group`**: E.g., apply a rule to *Wholesale* or *Individual* customers.
- **`Tier`**: E.g., limit a rule to *Gold Tier* members.

### Rule Types
- **`Multiplier`**: Multiplies the base points earned.
- **`Bonus Points`**: Adds a flat point value to the transaction.
- **`Cap`**: Restricts the maximum points that can be earned.
- **`Exclusion`**: Excludes items matching this dimension from earning points.

---

## 🔀 Priority Resolution & Stacking Logic

When multiple loyalty rules match the items in a cart, CGE resolves them using the following rules:

### 1. Exclusion Rule Wins
If any matching rule is of type `Exclusion`, the item's effective points multiplier is immediately set to `0.0`. No points are earned for this line item.

### 2. Multiplier Stacking vs Override
- **`allow_stack = 1 (True)`**: If all matching rules allow stacking, the rules stack multiplicatively.
  $$\text{Effective Multiplier} = \text{Rule}_1 \times \text{Rule}_2 \times \dots \times \text{Base Tier Multiplier}$$
- **`allow_stack = 0 (False)`**: If any matched rule does not allow stacking, the rule with the highest **Priority** value wins. If priorities are equal, the rule with the highest **Rule Value** is selected.

#### Example Calculation:
- Base Gold Tier Multiplier: `1.5X`
- Brand Multiplier (Raymond, Priority 1, Stacking Allowed): `2.0X`
- **Effective Multiplier**: `2.0X (Brand) * 1.5X (Tier) = 3.0X`

### 3. Bonus Points Stacking
- Similar to multipliers, bonus point rules add together if stacking is allowed, or select the highest priority bonus points value if stacking is disallowed.

### 4. Cap Enforcement
- If multiple points caps are matched, the lowest cap (most restrictive) is enforced on the line item.

---

## 📝 Rule Evaluation Log (Rule 13 Compliance)

For auditability, every rule evaluation is logged in the database under **SMRITI Rule Evaluation Log** (when `enable_rule_trace` is active in **SMRITI CGE Settings**):
- Stores the exact rule matched, status (`Applied` or `Ignored`), final multiplier, and reason text.
- Helps support teams diagnose customer points calculations instantly.
- Entries are immutable once created.

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