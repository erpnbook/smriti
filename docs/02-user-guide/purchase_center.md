---
Document ID: "USER-033"
Title: "SMRITI Purchase Center — User Guide v1.0"
Owner: "Operations Team"
Audience: "End User"
Module: "Purchase Studio"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "SAS, Inventory"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Center — User Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02
**Audience:** Store Manager, Purchase Manager, Accounts Staff

---

## Overview

The SMRITI Purchase Center is your end-to-end procurement workspace. It covers the full purchase lifecycle:

```
Purchase Order → GRN (Receiving) → Purchase Invoice → Payment → Returns
```

Access it from the sidebar: **Purchase → Purchase Center**
URL: `/smriti-purchase`

> The Purchase Center connects directly to ERPNext's purchase ledger, stock ledger, and GST engine — no double entry required.

---

## Purchase Lifecycle at a Glance

| Stage | What Happens | Who Does It |
|---|---|---|
| Purchase Order | Raise order with supplier | Purchase Manager |
| Approval | High-value POs need approval | Senior Manager |
| GRN | Receive goods, update stock | Warehouse Staff |
| Invoice | Record supplier bill | Accounts Staff |
| Payment | Mark invoice as paid | Accounts Staff |
| Return | Return goods, raise debit note | Purchase Manager |

---

## 1. Purchase Orders

### 1.1 Creating a Purchase Order

1. Go to **Purchase Center → Purchase Orders → New PO**
2. Select **Supplier** from the dropdown (type 2+ characters to search)
3. Add **Items**:
   - Select item code
   - Enter quantity and rate
   - Assign warehouse
4. Set **Schedule Date** (expected delivery date)
5. Click **Save**

> **Approval threshold:** If the PO total exceeds your company's configured threshold, the PO will be saved as *Pending Approval* and cannot be submitted until approved.

### 1.2 PO Statuses

| Status | Meaning |
|---|---|
| Draft | Saved, not submitted |
| Pending Approval | Above threshold, awaiting senior approval |
| To Receive and Bill | Submitted, goods not yet received |
| To Bill | Goods received, invoice pending |
| Completed | All goods received and invoiced |
| Cancelled | PO voided |

### 1.3 Approving a PO

If you are a **Purchase Approver**:
1. Open the PO in *Pending Approval* status
2. Click **Approve** or **Reject**
3. If rejecting, enter a reason

---

## 2. GRN — Goods Receipt Note

### 2.1 Receiving Goods Against a PO

1. Go to **Purchase Center → GRN → New GRN**
2. Select the **Purchase Order** (optional but recommended)
3. Items from the PO are auto-populated
4. Adjust **received quantity** if partial delivery
5. Verify the **warehouse** (goods land here in stock)
6. Click **Save → Submit**

Stock is updated in real time once the GRN is submitted.

### 2.2 Receiving Without a PO

If no PO exists, create a GRN directly:
1. Select **Supplier**
2. Add items manually
3. Enter **Rate** (this becomes the valuation rate)

---

## 3. Purchase Invoices

### 3.1 Creating an Invoice

Two modes depending on your company's **Invoice Policy**:

**GRN-Only Mode** (most common for retail):
1. Go to **Purchase Center → Invoices → New Invoice**
2. Select the **GRN** to link
3. Bill details auto-populate from the GRN
4. Enter **Supplier Bill No** and **Bill Date**
5. Set **Due Date**
6. Submit

**Standalone Mode:**
1. Same as above, but no GRN link — enter items manually

### 3.2 Invoice Statuses

| Status | Meaning |
|---|---|
| Unpaid | Invoice submitted, payment pending |
| Partly Paid | Partial payment made |
| Paid | Fully settled |
| Overdue | Past due date, unpaid |

---

## 4. Purchase Returns

### 4.1 Raising a Return / Debit Note

Use this when goods need to be sent back to the supplier.

1. Go to **Purchase Center → Returns → New Return**
2. Select the original **GRN** (Purchase Receipt)
3. Select items and enter **return quantity** (system enters as negative)
4. Enter a **Return Reason** (mandatory)
5. Submit

The debit note automatically:
- Reverses stock in the warehouse
- Creates a debit note in the supplier's account
- Splits GST (CGST/SGST/IGST) for the return

---

## 5. Supplier Ledger

View a supplier's complete transaction history:

1. Go to **Purchase Center → Suppliers → [Supplier Name]**
2. Click **View Ledger**
3. Set **From Date** and **To Date**
4. See all invoices, payments, returns, and outstanding balance

---

## 6. Purchase Settings (Admin)

Configure purchase behavior for your company:

| Setting | Description |
|---|---|
| Approval Threshold | POs above this value require approval |
| Invoice Policy | `GRN Only`, `Standalone`, or `Flexible` |
| LC Rule | Landed Cost allocation rule |
| Default Warehouse | Pre-filled warehouse on new POs |
| Tolerance % | Allowed quantity variance between PO and GRN |

---

## 7. Purchase Analytics

Access purchase reports from the sidebar: **Reports → Purchase Reports**
Or from Analytics Studio → Purchase category.

See [Purchase Analytics Guide](./purchase_analytics.md) for full report descriptions.

---

## Frequently Asked Questions

**Q: The PO total is correct but it shows "Pending Approval" — why?**
Your company has an approval threshold configured. POs above that value require senior approval before submission. Contact your Purchase Approver.

**Q: Can I receive partial quantities against a PO?**
Yes. Edit the quantity in the GRN. The remaining quantity stays open on the PO.

**Q: The GRN is submitted but stock hasn't updated — what do I check?**
Verify that the correct warehouse is selected on the GRN item rows. Also confirm the item is configured as a stock item in ERPNext Item Master.

**Q: Can I cancel a submitted GRN?**
Yes, if no invoice has been created against it. Open the GRN → Cancel. If an invoice exists, cancel the invoice first, then the GRN.

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
*"Always decision-ready."*
