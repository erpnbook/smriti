---
Document ID: "DEV-014"
Title: "COMM-03 — PSV Exception Scenario Flows"
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

# COMM-03 — PSV Exception Scenario Flows
**Sprint**: PSV-COMM-001 Wave 2
**Purpose**: Three demo-ready stories that cover the most common retailer and distributor questions
**Format**: Narrative + slide reference + data + outcome
**Used in**: COMM-01 (slide 02:30), COMM-02 (slides 03:30, 06:00, 08:30)

---

## Why These Three Scenarios

Every PSV demo needs to answer an unspoken question:

> "Give me a real situation where this would have saved me something."

Generic features don't answer that. Specific stories do.
These three scenarios cover the three most common business pains
in distributor-brand inventory management.

---

## Scenario 1 — Stockout Prevention

### The Story

> **Ajay runs a footwear distribution hub in Pune.**
> He stocks 14 SKUs from a mid-market brand.
> Size 8 is his fastest mover — 40 pcs/week across his retail accounts.
>
> One Tuesday morning, PSV flags:
> *"Size 8 WOC = 1.8 weeks. Critical. Reorder recommended."*
>
> Ajay has 72 pcs of Size 8 in stock.
> He had no idea it was this low — his manual count was 10 days old.
>
> He calls the brand. Reorder placed — 200 pcs dispatched within 5 days.
> Stockout window avoided by 3 days.
>
> His retail accounts never ran out. No lost sales. No emergency calls.

---

### The Numbers

```
Current stock      : 72 pcs
Weekly velocity    : 40 pcs / week
WOC                : 72 / 40 = 1.8 weeks  ← Critical threshold: < 2 weeks
Alert triggered    : Tuesday
Reorder placed     : Wednesday
Stock received     : Monday (5 days)
Stockout would have occurred : Thursday (8 days from alert)
Buffer created     : 5 days
```

**Outcome**: 0 stockout events. 40 pcs × ₹500 margin × potential 3 days of lost sales = avoided.

---

### Demo Flow

**Slide**: Distributor Sell-Through Tracker
**Action**: Click "Log 50 Secondary Sales" to reduce WOC toward critical

**What to say**:
> "Dekho — jaise secondary sales log hoti hain, WOC real-time update hota hai.
> Jab WOC 2 weeks se neeche aata hai — PSV automatically alert karta hai.
> Ajay ko manually count nahi karna tha. System ne bataya."

**What not to say**: Do not promise specific lead times — those depend on brand logistics.

---

## Scenario 2 — Dead Stock Recovery

### The Story

> **Meera manages inventory for a branded apparel distributor in Nagpur.**
> She has been holding 820 pcs of a summer line — ordered in March.
> It is now mid-August. She assumed it was selling slowly.
> Her weekly reports never flagged it because the format only showed totals.
>
> PSV Stock Aging report runs automatically.
> It flags: *"Summer Slim Fit — 820 pcs. 97 days inactive. Dead Stock."*
> *"Estimated locked capital: ₹4,10,000"*
>
> She calls the brand: transfer request to a western India hub with better sell-through.
> 400 pcs transferred. 420 pcs returned at agreed terms.
>
> ₹4,10,000 in dead capital unlocked in 2 weeks.

---

### The Numbers

```
Item           : Summer Slim Fit (multiple sizes)
Stock          : 820 pcs
Days inactive  : 97 days
Dead stock threshold : 60 days (PSV default, configurable)
Stock value    : 820 × ₹500 avg = ₹4,10,000 locked
Action         : 400 pcs transferred + 420 pcs returned
Capital freed  : ₹4,10,000
Time to action : 14 days from alert to resolution
```

**Outcome**: ₹4.1L capital recovered. No write-off. No markdowns at retail.

---

### Demo Flow

**Slide**: Inventory Freshness & Aging (aging bands chart)
**Action**: Point to the Dead Stock (90+ days) band

**What to say**:
> "Yeh aging chart automatically har SKU ko classify karta hai.
> 0-30 din — active. 31-60 — slowing. 61-90 — aging. 90 plus — dead.
>
> Meera ka maal 97 din se pada tha. Excel report mein yeh kabhi surface nahi hua
> kyunki format sirf total stock dikhata tha.
> PSV ne automatically flag kiya — kitna capital locked hai, aur kahan transfer ho sakta hai."

---

## Scenario 3 — Network Balancing

### The Story

> **Rajan is a regional distribution manager for a footwear brand.**
> He handles 3 hubs — Mumbai, Pune, Nashik.
>
> PSV Network view shows:
> - Mumbai: Size 32 Denim — 120 pcs surplus. WOC = 18 weeks.
> - Pune: Size 32 Denim — 0 pcs. Stockout active.
>
> Both are his hubs. Same SKU. Same city cluster.
> Mumbai retailer accounts are slow on this size.
> Pune retailer accounts are asking for it every week.
>
> PSV flags the opportunity:
> *"Transfer 80 pcs from Mumbai to Pune. Estimated Margin Protection: ₹40,000"*
>
> Rajan raises a transfer note. 80 pcs moved in 2 days.
> Pune stockout resolved. Mumbai WOC normalized to 10 weeks.
> No fresh purchase required. No brand involvement needed.

---

### The Numbers

```
Mumbai stock   : 120 pcs Size 32 Denim
Mumbai WOC     : 120 / 6.7 pcs/week = 18 weeks  ← Excess
Pune stock     : 0 pcs Size 32 Denim             ← Stockout
Transfer qty   : 80 pcs
Transfer time  : 2 days (intra-city)

New Mumbai WOC : 40 / 6.7 = 6 weeks  (Optimal: 4-8 weeks)
New Pune stock : 80 pcs
Pune WOC       : 80 / 12 pcs/week = 6.7 weeks (Optimal)

Margin protected : 80 pcs × ₹500 = ₹40,000 (avoided stockout revenue loss)
Fresh PO avoided : Yes — no new brand order needed
```

**Math check**: 120 - 80 = 40 remaining Mumbai. 40/6.7 = 5.97 weeks ≈ 6 weeks ✅

**Outcome**: Zero fresh purchase. ₹40,000 margin protected. Network rebalanced in 48 hours.

---

### Demo Flow

**Slide**: Network Stock Transfer Simulator
**Action**: Click "Balance Network Stock" — watch Mumbai surplus move to Pune

**What to say**:
> "Mumbai mein 120 pcs excess hain — 18 weeks ka cover.
> Pune mein 0 pcs — stockout chal raha hai.
>
> PSV detect karta hai ki yeh same SKU hai, same region hai.
> Transfer recommendation deta hai. Rajan ne approve kiya.
> Fresh order nahi, brand involvement nahi, capital block nahi.
> 2 din mein problem solve."

---

## Scenario Usage Guide

| Scenario | Best for | Demo timing |
|----------|---------|------------|
| Stockout Prevention | Retailers worried about lost sales | COMM-01: 02:30 |
| Dead Stock Recovery | Distributors with old inventory | COMM-02: 03:30 |
| Network Balancing | Multi-location brands/distributors | COMM-02: 08:30 |

---

## Exception Alert Reference

| Alert Type | Trigger | Default Threshold |
|-----------|---------|-----------------|
| WOC Critical | WOC < 2 weeks | Configurable in PSV Settings |
| WOC Warning | WOC < 4 weeks | Configurable in PSV Settings |
| Dead Stock | No movement > 60 days | Configurable in PSV Settings |
| Excess Stock | WOC > 12 weeks | Configurable in PSV Settings |
| Variance Flag | Physical vs ledger > 5% | Configurable in PSV Settings |

> All thresholds are configurable per brand in SMRITI PSV Settings.
> Default values are based on mid-market footwear and apparel norms.

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Scenario numbers (stock quantities, margins) are illustrative. Use brand-specific data in live pilots.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |