---
Document ID: "KB-017"
Title: "Frequently Asked Questions — Sales Force Management & Commission (SFM/SFC)"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "SFM"
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

# Frequently Asked Questions — Sales Force Management & Commission (SFM/SFC)

> **Author:** Jawahar R Mallah (<jawahar.mallah@gmail.com>)  
> **Last Updated:** 2026-06-22  

### Q1: How does the Customer Ownership History model prevent audit trail gaps?
**A**: SMRITI enforces a timeline model with `start_date`, `end_date`, and `is_active` fields in `SMRITI Customer Ownership`. Historical records are never modified. When customer ownership changes, the old record is set with `end_date = yesterday` and `is_active = 0`, and a new record is created with `start_date = today` and `is_active = 1`. This provides an audit-grade timeline of customer ownership.

### Q2: What is the difference between a Store and a Warehouse in Sales Target mappings?
**A**: In SMRITI, targets are mapped at the `SMRITI Store` abstraction layer rather than the physical ERPNext `Warehouse` layer. A single Store can map to multiple warehouses, but target tracking and commission splits are consolidated at the Store level.

### Q3: How are commission splits handled when multiple sales reps collaborate?
**A**: When a sales transaction involves multiple reps, the target split percentages are applied. SMRITI validates that the sum of target split percentages across reps is exactly 100% (`primary_split_pct + secondary_split_pct = 100`) to prevent payouts from exceeding or under-allocating the total transaction value.

### Q4: Does settlement approval overwrite or delete commission ledger entries?
**A**: No. Settlement approval never supersedes or deletes active commission ledger entries. The commission ledger is the immutable record of earned commission. The settlement represents the payout lifecycle (`Draft` → `Approved` → `Paid`). Ledger entries remain `Active` upon settlement approval.

### Q5: How does the system handle minimum revenue thresholds for commission payout eligibility?
**A**: The resolving engine checks if the sales rep's total attributed revenue for the month meets the `min_revenue_threshold` configured in the active `SMRITI Commission Rule` or global settings. If the threshold is not met, the gross commission compiles to `0.0`.

### Q6: Can manual adjustments be added to monthly settlements?
**A**: Yes. Adjustments are recorded in the `SMRITI Commission Adjustment Detail` child table inside the settlement document. Each adjustment requires a `reason`, `amount`, `remarks`, `approved_by` manager signature, and `approved_on` timestamp.

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