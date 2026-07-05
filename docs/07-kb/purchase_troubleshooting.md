---
Document ID: "KB-PS-001"
Title: "SMRITI Purchase Studio — Troubleshooting Guide v1.0"
Owner: "Support Team"
Audience: "End User"
Module: "Purchase Studio"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "USER-033"
Related Modules: "Inventory, Accounting"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Studio — Troubleshooting Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Date:** 2026-07-02

---

## Issue 43 — Purchase Order Shows "Pending Approval" Immediately After Save

**Symptom:** A PO is saved and immediately shows *Pending Approval* status without being submitted.

**Cause:** The PO Grand Total exceeds the **Approval Threshold** configured in SMRITI Purchase Settings.

**Resolution:**

Option A — Reduce PO value below threshold (split into multiple POs if needed).

Option B — Get approval from a Purchase Approver:
1. Ask your store manager or purchase approver to open the PO
2. They click **Approve** to submit

Option C — Raise the threshold (admin only):
1. Go to **Purchase Center → Settings**
2. Increase **Approval Threshold**
3. Save

---

## Issue 44 — "Invoice Policy requires a GRN link" Error

**Symptom:** When creating a Purchase Invoice, you see the error:
```
Invoice Policy requires a GRN link. Please select a Purchase Receipt.
```

**Cause:** Your company's SMRITI Purchase Settings has **Invoice Policy = GRN Only**.
A standalone invoice (without GRN) is not permitted.

**Resolution:**

Step 1 — Create a GRN first:
- Go to Purchase Center → GRN → New GRN
- Receive the goods from the supplier
- Submit the GRN

Step 2 — Create the invoice linked to the GRN:
- In the Invoice form, select the GRN in the **Purchase Receipt** field

Alternatively, if your business requires standalone invoices:
- Admin goes to Settings → Invoice Policy → change to **Flexible**

---

## Issue 45 — GRN Submitted But Stock Not Updated

**Symptom:** GRN is in *Completed* status but the item's stock quantity has not increased.

**Resolution — 4-step check:**

1. **Verify the warehouse:** Open the GRN, check the warehouse column on each item row. The warehouse must be a valid ERPNext warehouse for this company.

2. **Check item type:** Go to ERPNext Item Master for the item. Confirm **Is Stock Item = Yes**. If not checked, no stock entry is created.

3. **Check Stock Ledger:**
   ```
   ERPNext → Stock → Stock Ledger
   Filter by Item + Warehouse + Date
   ```
   If the entry is there, the stock is updated. The POS/Inventory view may be cached.

4. **Try a hard refresh:** Press Ctrl+Shift+R on the Inventory page.

If none of the above resolves the issue, check `bench error.log` for stock validation errors.

---

## Issue 46 — Purchase Return "Quantity Must Be Negative" Error

**Symptom:** When creating a Purchase Return, the system rejects with:
```
Return qty must be negative for return transactions.
```

**Cause:** The UI sent a positive quantity to `create_purchase_return`. The return form expects negative quantities.

**Resolution:**
- In the Return form, quantities should be entered as **negative numbers** (e.g., `-5` for returning 5 units)
- The UI return form automatically converts positive inputs to negative — if this is not happening, clear browser cache and reload

---

## Issue 47 — Supplier Not Found in PO Supplier Search

**Symptom:** Typing a supplier name in the PO form shows "No results" even though the supplier exists.

**Cause:** The supplier may be:
- Marked as **Disabled** in ERPNext
- Under a different company or restricted by User Permission

**Resolution:**

1. Go to ERPNext Supplier list (via your admin): verify the supplier is Active and not Disabled.
2. Check SMRITI User Permissions — if your user has company-level restrictions, the supplier must be linked to your company.
3. If supplier was just added, try waiting 60 seconds for cache to clear, then search again.

---

## Issue 48 — Purchase Invoice Overdue Days Showing Incorrect Value

**Symptom:** An invoice shows overdue days as a large negative number or incorrect value.

**Cause:** The invoice's **Due Date** was not set, so overdue days calculated against a null date.

**Resolution:**
1. Open the Invoice
2. Set the **Due Date** field
3. Save

> Note: SMRITI's GRN Register report applies a `GREATEST(0, overdue_days)` guard — overdue days will never display as negative in the report. If you see a negative value in the invoice form, the Due Date is not set.

---

## Issue 49 — Purchase Analytics Report Shows No Data

**Symptom:** A purchase report returns empty results with no error.

**Resolution — checklist:**

| Check | Action |
|---|---|
| Date range too narrow | Widen From/To date range; try All Time (leave dates blank) |
| Status filter too restrictive | Clear the Status filter |
| Supplier filter mismatch | Clear Supplier filter; verify supplier name spelling |
| No transactions in the selected period | Confirm purchases exist in that period |
| SAS templates not seeded | Run: `bench execute smriti_retail_os.patches.seed_purchase_report_templates.execute` |

---

## Issue 50 — Cannot Cancel GRN — "Invoice Already Exists"

**Symptom:** When trying to cancel a GRN, you get:
```
Cannot cancel: A Purchase Invoice is linked to this GRN.
```

**Resolution:**
1. Go to **Purchase Center → Invoices**
2. Find the invoice linked to this GRN
3. Cancel the invoice first
4. Then return to the GRN and cancel it

> ERPNext enforces document dependency order. GRN → Invoice → Payment. Cancel in reverse order.

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
