---
Document ID: "USER-008"
Title: "Frequently Asked Questions — POS Operations"
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

# Frequently Asked Questions — POS Operations

> **Author:** Jawahar R Mallah (<jawahar.mallah@gmail.com>)  
> **Last Updated:** 2026-06-18  

### Q1: Why can't I see products in the POS search or category lists?
**A**: Ensure the following product attributes are configured in the Item Master:
- **Disabled** must be set to `No`.
- **Is Sales Item** must be set to `Yes`.
- **Maintain Stock** must be set to `Yes`.
- The item must have an active price in the Selling Price List linked to the cashier's active POS Profile.
- The item must be linked to the company and warehouse designated in the profile.

### Q2: How do I refund a sale or process a return?
**A**:
1. Open the POS cart panel and select **Sales Return**.
2. Input the original invoice ID.
3. Select the items being returned, specify the return quantity, and confirm.
4. The register automatically processes stock receipt back into the warehouse and creates a draft Credit Note for manager approval.

### Q3: Can I print duplicate receipts for a past checkout transaction?
**A**: Yes. Navigate to the POS shift history panel or search for the submitted POS Invoice. Click the target invoice, open the Print View, and click **Print** to generate a duplicate receipt. SMRITI prints this receipt formatted under your default whitelabel brand layout.

### Q4: How do I handle cashier shift variances during register closure?
**A**: If the physical cash counted in the drawer does not match the system's expected balance:
- The cashier logs the actual closing amounts.
- If the difference exceeds the validation threshold (e.g. Rs. 500), the terminal locks.
- A Store Manager must verify the discrepancy and enter their numeric POS PIN to authorize the shift closure override.

### Q5: Can I recall a held bill on a different POS terminal?
**A**: By default, held bills (`custom_is_held = 1`) are locked to the cashier's active user ID and POS Profile to maintain register segregation. However, a Store Manager can override the user lock via the management console to load the draft cart onto another checkout terminal.

### Q6: Can I process checkouts if the network is completely down?
**A**: Yes. SMRITI POS includes an integrated Progressive Web App (PWA) offline checkout module. If the network goes offline, the billing interface displays a `🔴 Offline` status badge. When you submit a transaction, the terminal prompts you to queue it offline. The invoice payload is securely serialized and stored locally inside your browser's IndexedDB (`SmritiRetailOS` -> `pending_invoices`), and your cart resets so you can continue billing other customers immediately.

### Q7: How do queued offline invoices synchronize back to the server?
**A**: SMRITI's Service Worker automatically listens for network state changes. Once the browser detects that connection is restored, the status badge updates to `🟢 Online` and background sync processes the queued transactions in chronological order. A browser notification confirms when the sync completes, and the records are automatically deleted from your local IndexedDB queue.

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