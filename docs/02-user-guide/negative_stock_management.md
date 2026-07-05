---
Document ID: "USER-035"
Title: "SMRITI Negative Stock Management — User Guide v1.0"
Owner: "Operations Team"
Audience: "End User"
Module: "SNSM"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "Inventory"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Negative Stock Management — User Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Date:** 2026-07-02

---

## What is Negative Stock?

Negative stock occurs when the system records more stock being sold or consumed than is currently available in a warehouse. For example:

- Warehouse has 5 units
- POS sale is posted for 8 units
- Result: Stock balance = -3 units

This creates an inaccurate inventory position and can distort stock valuation.

**Common causes:**
- Stock opening balance not entered before sales begin
- Items sold before GRN is received
- Multiple concurrent sales at the same counter
- Data entry errors in stock transfers

---

## SMRITI Negative Stock Management Engine (SNSM)

SNSM is SMRITI's built-in detection and recovery system. It:

1. **Detects** negative stock events as they occur
2. **Creates a Case** for each negative stock incident
3. **Enforces Policy** (block, warn, or allow) based on your configuration
4. **Guides Recovery** through an operator-approved correction workflow
5. **Audits** every action with before/after values and timestamps

---

## Negative Stock Policy Configuration

Administrators can configure the policy per item group, warehouse, or globally:

| Policy Mode | Behaviour |
|---|---|
| **Block** | Transaction is rejected if it would cause negative stock |
| **Warn** | Transaction proceeds but a warning alert is raised |
| **Allow** | Negative stock is permitted (not recommended for production) |

### Setting the Policy

1. Go to **SMRITI Settings → Negative Stock Policy**
2. Select **Policy Mode**
3. Optionally restrict by **Item Group** or **Warehouse**
4. Set **Alert Threshold** (e.g., warn if stock goes below -5 units)
5. Save

---

## Viewing Negative Stock Cases

When a negative stock event occurs:

1. A **Case** is automatically created
2. Go to **Inventory → Negative Stock Cases**
3. Each case shows:
   - Item and warehouse
   - Date and time of event
   - Quantity at time of event
   - Triggering transaction
   - Current status (Open / Recovery In Progress / Resolved)

---

## Recovery Workflow

Recovery means correcting the stock to bring it back to zero or positive.

### Step 1 — Understand the Root Cause

Open the case and review the **Reason** field:
- Missing GRN (goods received but not recorded)
- Opening balance gap
- Concurrent transaction conflict
- Manual adjustment error

### Step 2 — Choose Recovery Action

| Action | When to Use |
|---|---|
| Post Missing GRN | Goods were received but GRN not created |
| Stock Reconciliation | Opening balance needs adjustment |
| Reverse Transaction | The sale transaction was in error |
| Manual Adjustment | Direct stock entry after investigation |

### Step 3 — Submit for Approval

1. Fill in the **Recovery Action** and **Justification**
2. Click **Submit for Approval**
3. An approver (Store Manager or above) will review

### Step 4 — Approval

Approvers will see pending recovery requests in:
**Inventory → Negative Stock Cases → Pending Approval**

Once approved, SNSM executes the recovery action and marks the case **Resolved**.

---

## Audit Trail

Every case maintains a complete audit trail:

| Field | Value |
|---|---|
| Created By | System (automatic) |
| Recovery Submitted By | Operator |
| Approved By | Manager |
| Before Stock | -3 units |
| After Stock | 0 units |
| Resolution Date | Timestamp |

This audit trail is immutable — it cannot be edited after approval.

---

## Best Practices

1. **Always post GRN before opening POS** — stock must be in the system before sales begin.
2. **Use Block mode in production** — Allow mode should only be used during data migration.
3. **Resolve cases within 24 hours** — Unresolved negative stock compounds when further transactions occur.
4. **Monitor the alert count** — If negative stock cases exceed 5 per day, investigate your receiving workflow.

---

## Frequently Asked Questions

**Q: Can SNSM automatically fix negative stock without human approval?**
No. SNSM flags and guides, but never auto-corrects. Human approval is mandatory. This is by design (SMRITI Architecture Rule 10).

**Q: Will SNSM block POS sales?**
Only if Policy Mode is set to Block. If set to Warn, the sale proceeds and a case is raised in the background.

**Q: Does SNSM affect ERPNext's stock ledger?**
SNSM reads the ERPNext stock ledger but does not write to it directly. All corrections go through standard ERPNext stock transactions.

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
