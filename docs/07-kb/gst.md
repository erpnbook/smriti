---
Document ID: "KB-008"
Title: "Frequently Asked Questions — GST Configuration"
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

# Frequently Asked Questions — GST Configuration

### Q1: Why is GST not appearing on my POS invoices?
**A**: This occurs if the checkout transaction does not trigger a tax template. Verify that:
- An active **Sales Taxes and Charges Template** is assigned in the POS Profile.
- The item has a valid **HSN Code** mapped in the Item Master.
- The customer profile is mapped to the correct Tax Category (e.g. `In-State` or `Out-of-State`).

### Q2: How do I change the GST rate for a specific item group?
**A**:
1. Open the Item Group card or navigate to **Taxes** settings.
2. In the Item-wise Tax table, update the rate (e.g. change GST 12% to GST 18%).
3. Save the changes. The POS checkout terminal will automatically pull the updated tax configuration on the next item scan.

### Q3: How does the system handle multi-tax invoices?
**A**: SMRITI supports multi-slab billing. If your cart contains items with different tax slabs (e.g., shoe taxed at 5% and boot taxed at 18%), the system computes SGST/CGST on each item row independently based on its respective HSN mapping, and rolls them up into the invoice grand total.

### Q4: Do B2B sales invoices require special tax configurations?
**A**: Yes. B2B transactions require the customer's verified GSTIN. Register the GSTIN on the Customer card. During billing, the checkout panel automatically maps the transaction as a tax-credit eligible sales invoice.

### Q5: What is the minimum HSN digit count required by the validation engine?
**A**: SMRITI's India Compliance module enforces standard validation checks: HSN codes must be exactly **6 or 8 digits** long. Standard 4-digit codes will be rejected by the validation engine during product save operations.

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