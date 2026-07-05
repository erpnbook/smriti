---
Document ID: "KB-024"
Title: "Support Runbook — GST Not Calculating at POS"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "Core"
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

# Support Runbook — GST Not Calculating at POS

This runbook guides support engineers in diagnosing and resolving tax calculation failures during POS register checkouts.

## 🚨 Symptom
Cashiers scan sellable items, but the tax amount (CGST / SGST / IGST) shows as zero (`Rs. 0.00`) or is not appended to the invoice grand total.

---

## 🔍 Diagnostics Step-by-Step

### Step 1: Verify POS Profile Tax Settings
1. Navigate to the POS Profile settings.
2. Locate the **Sales Taxes and Charges Template** field.
3. Verify if a valid tax template is selected (e.g. `GST 18%`).
4. Ensure the **Apply Tax Automatically** checkbox is enabled.

### Step 2: Validate Item HSN Mapping
Taxes depend on valid product classifications:
- Open the Item Master card.
- Confirm the **Default HSN Code** field contains a valid 6 or 8-digit code (e.g. `640399`).
- Check if the **Item-wise Tax** table has overrides that force rates to zero.

### Step 3: Check Customer Tax Category
For GST to resolve between CGST/SGST (intra-state) and IGST (inter-state):
- Open the active Customer profile card.
- Verify that the **Tax Category** is set to `In-State` or `Out-of-State` based on their shipping address.
- If the Tax Category is blank, the system will fallback to local calculations, which may fail if the customer state is different from the warehouse company state.

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