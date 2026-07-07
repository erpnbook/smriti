---
Document ID: "KB-028"
Title: "Volume 4 Troubleshooting Faq"
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

## Purchase Studio FAQs (v2.0.0)

**Q: Where is the new Purchase Center?**
Go to Sidebar → Purchase → Purchase Center, or navigate to `/smriti-purchase`.

**Q: My PO went to "Pending Approval" — who approves it?**
Your Store Manager or designated Purchase Approver. They will see the PO in Purchase Center → Purchase Orders → Pending Approval. They click Approve or Reject.

**Q: Can I skip GRN and create an invoice directly?**
Depends on your Invoice Policy setting. If policy = GRN Only, a GRN is mandatory. If Flexible, standalone invoices are allowed. Ask your administrator to check Purchase Settings.

**Q: The supplier is not appearing in the PO supplier search.**
The supplier may be disabled in ERPNext, or restricted by User Permissions. Contact your system administrator.

**Q: How do I reconcile purchase returns with GST?**
Use the Purchase Return Register report (Reports → Purchase Reports → Purchase Return Register). It shows CGST, SGST, and IGST amounts for each return separately.

**Q: Where do I see which POs have not been fully received yet?**
In the Purchase Order Summary report, check the Status column for "To Receive and Bill" entries. These have goods outstanding.

---

## UIE / TallyPrime FAQs (v2.0.0)

**Q: How do I connect SMRITI to TallyPrime?**
See the [UIE TallyPrime Setup Guide](./uie_tally_setup.md) for step-by-step instructions.

**Q: Does SMRITI replace TallyPrime?**
No. SMRITI owns Inventory, Purchase, Sales, and POS. TallyPrime owns the books of accounts (Trial Balance, P&L, Balance Sheet). UIE bridges the two.

**Q: What happens if TallyPrime is offline when an invoice is submitted?**
The sync entry goes into the Sync Queue with status "Queued". When TallyPrime comes back online, the queue processes automatically.

**Q: How do I check if a voucher was posted to Tally?**
Go to UIE Integration Center → Sync Queue. Filter by the invoice name. Status = "Completed" means it was posted successfully.

---

## SMRITI v2.1.1 FAQs

**Q: Why was the Product Catalog page showing a "TypeError: Cannot read properties of undefined (reading 'get_list')" error?**
In version 2.1.0, the `/products` page attempted to call a client-side database query. This has been resolved in v2.1.1 by routing the request through the secure whitelisted backend API `get_catalog_metadata`.

**Q: Why was the notification badge showing a "403 Forbidden" error?**
The sidebar and topbar notification badges query unread counts. In version 2.1.1, the `get_unread_count` endpoint was whitelisted to grant proper access to store managers and cashiers without raising a permission exception.

**Q: Why were POST requests returning a "400 Bad Request" error on the dashboard?**
The client was not passing the global CSRF token to the backend API. In v2.1.1, the global `window.csrf_token` and `window.csrfToken` parameters are injected directly into the templates, resolving this issue.

**Q: How does the new collapsed sidebar brand logo work?**
In collapsed mode, the SMRITI brand logo now remains visible and centered on the 68px width header, while the text label is hidden.

**Q: Why did the daily Negative Stock Safety Sweep scheduler fail with an ImportError during migrate?**
The scheduler job was pointing to a classmethod rather than a module-level function, and the service package was missing `__init__.py`. In v2.1.1, this is fully resolved with a plain wrapper function and the correct package initialization.

---

## SMRITI v2.1.7 FAQs

**Q: Why did the catalog validation API return a "417 (EXPECTATION FAILED)" error when entering an invalid HSN code length?**
In earlier versions, if an invalid HSN length (such as 7 digits) was supplied in a row during import validation dry-run, the backend validation helper raised an unhandled `ValidationError`, crashing the entire validate_import_rows API process. This has been resolved in v2.1.7 by wrapping the HSN validation in a try-except block, returning the validation message gracefully as a row-specific error to the user interface.
