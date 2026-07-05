---
Document ID: "DEV-005"
Title: "CGE CUSTOM FIELDS SPECIFICATION (SPRINT 1)"
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

# CGE CUSTOM FIELDS SPECIFICATION (SPRINT 1)

This document details the schema extensions added to standard ERPNext masters to support the SMRITI Customer Growth Engine (CGE) v1.0.

## 1. Customer DocType Extensions
These fields support loyalty membership, tier evaluation, and growth scores.

| Fieldname | Label | Fieldtype | Options | Default | Insert After | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `custom_membership_plan` | Membership Plan | Link | `SMRITI Membership Plan` | | `custom_anniversary` | Reserved link field for Phase 5B membership plans. |
| `custom_membership_start` | Membership Start Date | Date | | | `custom_membership_plan` | Reserved membership validity. |
| `custom_membership_expiry`| Membership Expiry Date | Date | | | `custom_membership_start` | Reserved membership validity. |
| `custom_customer_growth_score`| Customer Growth Score | Float | | | `custom_membership_expiry`| Reserved scoring index for Phase 5C analytics. |
| `custom_growth_score_last_calculated`| Growth Score Last Calculated | Datetime | | | `custom_customer_growth_score`| Timestamp of the last analytics score updates. |

## 2. Coupon Code DocType Extensions
These fields support campaign containment, coupon targeting, and fraud protection limits.

| Fieldname | Label | Fieldtype | Options | Default | Insert After | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `custom_coupon_scope` | Coupon Scope | Select | `Invoice`, `Item`, `Brand`, `Customer`, `Customer Group`, `Store` | `Invoice` | `coupon_type` | Limits where the coupon code can be applied. |
| `custom_campaign` | Campaign | Link | `SMRITI Coupon Campaign` | | `custom_coupon_scope` | Groups coupons within a marketing budget campaign. |
| `custom_max_uses_per_customer`| Max Uses per Customer | Int | | | `custom_campaign` | Limits usage frequency for a single customer. |
| `custom_max_uses_per_mobile` | Max Uses per Mobile | Int | | | `custom_max_uses_per_customer`| Fraud control mapping usage frequency to mobile. |
| `custom_max_uses_per_day` | Max Uses per Day | Int | | | `custom_max_uses_per_mobile`| Restricts aggregate daily coupon burn rate. |
| `custom_max_discount_cap` | Max Discount Cap | Currency | | | `custom_max_uses_per_day` | Sets absolute cash value limit on percentage coupons. |


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