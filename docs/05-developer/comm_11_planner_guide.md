---
Document ID: "DEV-018"
Title: "COMM-11 — PSV Brand Planner Guide"
Owner: "Development Team"
Audience: "Developer"
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

# COMM-11 — PSV Brand Planner Guide
**Sprint**: PSV-COMM-001
**Audience**: Brand Planner / Supply Chain Manager (internal — daily PSV user)
**Purpose**: Operating guide for the person running PSV day-to-day

---

## Your Role in PSV

The **Brand Planner** is the primary PSV user.
You are the bridge between distributor data and brand decisions.

Your job with PSV is not data entry — it is **decision-making**.
PSV surfaces the signals. You act on them.

---

## Weekly Operating Rhythm

### Monday — Exception Review (20 minutes)

```
Step 1: Open PSV Dashboard → Exception Log
Step 2: Filter by "New Since Last Week"
Step 3: For each WOC Critical alert:
          - Verify physical stock count with distributor
          - Initiate reorder OR transfer request
          - Log action taken in exception record
Step 4: For each Dead Stock flag:
          - Identify recovery path (transfer / markdown / return)
          - Raise action with distributor
Step 5: Note any unresolved alerts for Wednesday follow-up
```

---

### Wednesday — Sell-Through Review (15 minutes)

```
Step 1: Open PSV Dashboard → Sell-Through Tracker
Step 2: Sort by Sell-Through % ascending (lowest first)
Step 3: For any SKU < 50% Sell-Through:
          - Check: Is this a sizing issue? Location issue? Competition?
          - Flag for brand team discussion if pattern persists
Step 4: Check Network view — any new transfer opportunities?
Step 5: Follow up on Monday's unresolved alerts
```

---

### Friday — Data Completeness (10 minutes)

```
Step 1: Check which distributors have uploaded this week
Step 2: Chase any overdue uploads (> 7 days since last)
Step 3: Confirm reorders placed Monday are in process
Step 4: Prepare weekly summary for brand manager (if required)
```

---

## Monthly Operating Rhythm

### First Monday of Month

```
[ ] Download monthly Sell-Through Report (all distributors)
[ ] Download Stock Aging Report — identify new dead stock
[ ] Review WOC trends: is any distributor consistently low?
[ ] Prepare monthly distributor performance summary
[ ] Flag any distributor needing opening balance correction
```

### Last Friday of Month

```
[ ] Confirm all distributors have uploaded month-end data
[ ] Run reconciliation: primary sales vs secondary sales
[ ] Identify variance items (> 5% discrepancy)
[ ] Raise correction requests if needed
[ ] Archive month's exception log
```

---

## Decision Framework

### When WOC = Critical (< 2 weeks)

```
1. Is the alert accurate? → Verify with distributor (call/message)
2. How fast can stock reach distributor?
   - Same city warehouse: 1-2 days → Initiate transfer
   - Production/bulk order: 7-14 days → Initiate PO immediately
3. Is there surplus at another distributor? → Network transfer first
4. Log decision in Exception Record with timestamp
```

**Target response time**: Within 24 hours of alert.

---

### When Dead Stock Detected (60+ days)

```
1. Confirm stock is physically present (not already transferred)
2. Check sell-through at similar locations — is it a location issue?
3. Recovery options (in priority order):
   a. Transfer to faster-moving distributor
   b. Markdown / promotional push at current location
   c. Return to brand warehouse for reallocation
4. Raise action within 5 business days of detection
```

**Capital unlock target**: Resolve within 30 days of flag.

---

### When Variance Flag Triggered

```
1. Compare PSV ledger to distributor's own count
2. Common causes:
   - Upload error (wrong column, unit mismatch)
   - Sales recorded but upload missed
   - Returns not captured
3. Request corrected upload from distributor
4. If discrepancy > 10%: physical count required
```

---

## KPIs for Brand Planners

Track these monthly to measure your own PSV effectiveness:

| KPI | Target | How to Measure |
|-----|--------|---------------|
| Alert response time | < 24 hours for Critical | Exception Log timestamps |
| Upload compliance | ≥ 90% distributors uploading weekly | Dashboard — Upload Status |
| Dead stock resolution | < 30 days from detection | Aging Report delta |
| Reorder accuracy | Stockout rate < 3% | WOC Critical alert count |
| Network balance | < 5% distributors with WOC > 12 weeks | Network view |

---

## Escalation Guide

| Situation | Escalate To | When |
|-----------|------------|------|
| Distributor refuses to upload | Sales Manager | After 2 missed weeks |
| WOC Critical + no reorder stock available | Supply Chain Head | Immediately |
| Dead stock > ₹5L at one distributor | Brand Owner | Same day |
| Repeated variance flags (> 3 months) | Audit team | Month-end |
| PSV data does not match ERP dispatch | SMRITI Support | Within 24 hours |

**SMRITI Support**: support@aitdl.com

---

## Common Planner Mistakes

```
MISTAKE: Waiting for distributor to call instead of acting on WOC alert
FIX:     Monday exception review is mandatory — act before they call

MISTAKE: Accepting distributor's verbal stock count without upload
FIX:     All data must flow through PSV upload — no verbal updates

MISTAKE: Treating dead stock as a future problem
FIX:     Dead stock at 60 days → action within 5 days. At 90 days, recovery options narrow.

MISTAKE: Ignoring low Sell-Through without investigating cause
FIX:     < 50% Sell-Through = investigate. Is it size? Location? Visibility?

MISTAKE: Using PSV data for only one distributor, ignoring network view
FIX:     Monday review must include network view — imbalances are often invisible per-distributor
```

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*This guide assumes PSV v1.1 — Phase 1.2 frozen. Update as features are added in Phase 1.3+*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |