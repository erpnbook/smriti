---
Document ID: "KB-009"
Title: "Frequently Asked Questions — Inventory Management"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "PSV"
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

# Frequently Asked Questions — Inventory Management

### Q1: Why is stock showing negative balances in my store warehouse?
**A**: SMRITI blocks negative stock checkout in POS by default. However, if back-office sales or manual Stock Entries are submitted with stock updates enabled when physical quantities have not yet been received in the system (e.g. GRN pending), the database ledger will register a negative balance. Ensure all Purchase Receipts are submitted before physical sales checkouts.

### Q2: How do I transfer stock between warehouses?
**A**:
1. Open the inventory management screen and select **Stock Entry**.
2. Set the purpose to **Material Transfer**.
3. Define the **Source Warehouse** and **Target Warehouse**.
4. Add the items and quantities.
5. Click **Submit** (requires SMRITI Store Manager or System Manager roles).

### Q3: How often are the stock aging snapshots recalculated?
**A**: Stock aging snapshots are generated incrementally using background tasks. Recalculation runs during off-peak hours as defined in PSV System Settings to prevent database locking during high-traffic store hours.

### Q4: What happens to negative entries in the FIFO aging calculation?
**A**: Negative ledger entries (representing sales and stock outflows) consume stock using FIFO logic. The aging engine only scans positive ledger entries (like Purchase Receipts or Stock Receipts) to trace the origin date of the remaining balance.

### Q5: Can I exclude a showroom warehouse from stock redistribution?
**A**: Yes. Open the Warehouse settings card or navigate to SMRITI PSV settings. Add the target warehouse to the **Redistribution Exclusions** list. The engine will skip this warehouse, preventing suggested transfers from targeting its display stock.

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