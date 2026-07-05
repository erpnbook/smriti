---
Document ID: "USER-026"
Title: "Volume 1 Daily Operations"
Owner: "Operations Team"
Audience: "End User"
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
---

## Purchase Workflow (v2.0.0)

> 📦 **New in v2.0.0:** The SMRITI Purchase Center replaces the legacy ERPNext purchase form workflow.
> Access it from: **Sidebar → Purchase → Purchase Center** or URL `/smriti-purchase`

### Daily Purchase Tasks

| Task | Where | Frequency |
|---|---|---|
| Check pending GRNs | Purchase Center → GRN | Daily (morning) |
| Approve pending POs | Purchase Center → PO → Pending Approval | As needed |
| Create purchase invoices for received goods | Purchase Center → Invoices | Daily |
| Review overdue supplier invoices | Reports → Purchase Invoice Register | Weekly |

### Quick Reference

- **Create PO:** Purchase Center → New PO → Select Supplier → Add Items → Save
- **Receive Goods:** Purchase Center → New GRN → Link PO → Verify Qty → Submit
- **Create Invoice:** Purchase Center → New Invoice → Link GRN → Enter Bill No → Submit
- **View full guide:** [Purchase Center User Guide](./purchase_center.md)
