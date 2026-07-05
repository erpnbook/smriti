---
Document ID: "DEV-007"
Title: "CGE DOCTYPE INVENTORY (SPRINT 1)"
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

# CGE DOCTYPE INVENTORY (SPRINT 1)

This document catalogs the DocTypes introduced during Sprint 1 of the SMRITI Customer Growth Engine (CGE) v1.0.

## 1. SMRITI Loyalty Tier
Defines the parameters of the loyalty tier membership structure.
* **Autonaming**: `field:tier_name`
* **JSON File**: `smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_tier/smriti_loyalty_tier.json`
* **Properties**: Custom = 0, issingle = 0, track_changes = 1
* **Fields**:
  * `tier_name` (Data, Unique, Required, List View)
  * `min_points` (Float, Required, List View)
  * `tier_multiplier` (Float, Default: `1.0`, Required, List View)
  * `validity_months` (Int)
  * `active` (Check, Default: `1`, List View)
  * `tier_benefits` (Text)

## 2. SMRITI Loyalty Rule
Defines multipliers, bonus points, point caps, and exclusions based on dimensions.
* **Autonaming**: `hash`
* **JSON File**: `smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_rule/smriti_loyalty_rule.json`
* **Properties**: Custom = 0, issingle = 0, track_changes = 1
* **Fields**:
  * `rule_name` (Data, Required, List View)
  * `version` (Int, Default: `1`, Required, List View)
  * `status` (Select: `Draft`, `Active`, `Suspended`, `Archived`, Default: `Draft`, Required, List View)
  * `effective_from` (Date, Indexed)
  * `effective_to` (Date, Indexed)
  * `supersedes_rule` (Link -> SMRITI Loyalty Rule)
  * `rule_type` (Select: `Multiplier`, `Bonus Points`, `Cap`, `Exclusion`, Default: `Multiplier`, Required, List View)
  * `dimension` (Select: `Brand`, `Item Group`, `Style`, `Season`, `Store`, `Customer Group`, `Tier`, Default: `Brand`, Required, List View)
  * `dimension_doctype` (Select: `Brand`, `Item Group`, `Customer Group`, `Warehouse`, `Territory`, `Style`, `Season`, Required)
  * `dimension_value` (Dynamic Link -> `dimension_doctype`, Required, List View)
  * `rule_value` (Float, Required, List View)
  * `priority` (Int, Default: `0`)
  * `allow_stack` (Check, Default: `0`)
* **Database Indexes**:
  * Composite Index on `(status, dimension, dimension_value)`
  * Single Indexes on `(effective_from)` and `(effective_to)`

## 3. SMRITI CGE Settings
Unified Single DocType containing feature flags for CGE capabilities.
* **Autonaming**: Single DocType (`issingle: 1`)
* **JSON File**: `smriti_retail_os/smriti_retail_os/doctype/smriti_cge_settings/smriti_cge_settings.json`
* **Properties**: Custom = 0, issingle = 1, track_changes = 1
* **Fields**:
  * `enable_loyalty` (Check, Default: `0`)
  * `enable_cashback` (Check, Default: `0`)
  * `enable_coupon` (Check, Default: `0`)
  * `enable_campaign_budget` (Check, Default: `0`)
  * `enable_offline_cache` (Check, Default: `0`)
  * `enable_rule_trace` (Check, Default: `0`)


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