---
Document ID: "KB-005"
Title: "SMRITI OS GST Configuration Guide"
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

# SMRITI OS GST Configuration Guide

This guide details configuring India GST templates, mapping Item-wise HSN codes, and setting up POS profiles for automatic tax calculation.

## 📄 Creating GST Tax Templates

SMRITI utilizes standard **Sales Taxes and Charges Templates** to apply taxes during checkout. Set up the templates for standard tax slabs:

### Example: GST 18% Template
1. Create a new Sales Taxes and Charges Template named `GST 18%`.
2. Add the tax ledger rows:

| Type | Account Head | Rate (%) | Description |
| :--- | :--- | :---: | :--- |
| **On Net Total** | CGST Account | 9.0 | Central GST (9%) |
| **On Net Total** | SGST Account | 9.0 | State GST (9%) |

For interstate customers, configure a matching `IGST 18%` template mapping the full 18% rate to the Integrated GST ledger.

---

## 🏷️ HSN Code & Item-Wise Tax Mapping

SMRITI relies on the **India Compliance** application to validate and calculate taxes at the item row level. Configure tax mapping:
- **HSN Code validation**: Ensure every item variant is assigned a valid 6 or 8-digit HSN code (e.g. `640399` for leather footwear).
- **Item-wise Tax Override**: For products with dynamic tax slabs (e.g., items priced under Rs. 1,000 taxed at 5% and over Rs. 1,000 taxed at 12%), configure tax rules:
  1. Open the Item card and locate the **Tax** section.
  2. Map the GST category to the respective slab template.

---

## ⚙️ POS Profile Integration

To enable auto-calculation of GST during register checkout:
1. Open the target **POS Profile**.
2. Set the default **Sales Taxes and Charges Template** (e.g., `GST 18%`).
3. Check **Apply Tax Automatically** to ensure CGST/SGST calculation is executed immediately on product scans.

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