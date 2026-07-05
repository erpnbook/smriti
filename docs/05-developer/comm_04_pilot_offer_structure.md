---
Document ID: "DEV-015"
Title: "COMM-04 — PSV Pilot Offer Structure"
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

# COMM-04 — PSV Pilot Offer Structure
**Sprint**: PSV-COMM-001 Wave 1
**Audience**: Retailer / Brand Owner (closing conversation, post-demo)
**Purpose**: Structured pilot offer that can be presented after COMM-01 demo
**Status**: Draft — Founder approval required before presenting to any prospect

---

## Pilot Definition

### What Is the PSV Pilot?

A **30-day, single-distributor, zero-disruption** engagement that demonstrates
PSV's core value on the brand's real data before a full rollout commitment.

---

## Pilot Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Duration | 30 days | Extendable to 60 days by mutual agreement |
| Distributor count | 1 | Start small — prove the model |
| Brand | 1 | One brand, one distributor network |
| Data entry method | Excel upload | No technical integration required at start |
| Hosting | SMRITI cloud (AITDL) | Brand data stays within the instance |
| Technical disruption | Zero | Does not touch distributor's existing systems |

---

## What the Brand Gets

```
Week 1: Onboarding + opening balance upload
Week 2: First sell-through tracking cycle
Week 3: First exception alerts (WOC warnings, dead stock flags)
Week 4: First reconciliation report + pilot review
```

### Deliverables at Pilot End

| Deliverable | Description |
|-------------|-------------|
| Sell-Through Report | Full 30-day sell-through % by SKU and distributor location |
| WOC Accuracy Report | Forecast vs actual weeks of cover for the distributor |
| Exception Log | All alerts triggered: stockouts, dead stock, variance flags |
| Reconciliation Summary | Primary dispatched vs secondary sold reconciliation |
| Pilot Assessment | Go/No-Go recommendation with data evidence |

---

## What the Brand Provides

| Item | Effort |
|------|--------|
| Opening balance data (stock at distributor) | One-time Excel upload |
| Primary sales data (monthly dispatch records) | Monthly Excel / ERPNext export |
| Distributor contact for data coordination | 1 point of contact |
| 30 minutes for onboarding session | Week 1 |
| 30 minutes for pilot review | Week 4 |

> **Distributor's effort**: Excel template to fill — sales tally per SKU per week.
> No software installation. No API integration. No change to their workflow.

---

## Pilot Success Criteria

Success is defined jointly before pilot starts. Suggested defaults:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data completeness | ≥ 80% SKUs tracked | Ledger coverage |
| WOC accuracy | ± 1 week of actual | End-of-pilot reconciliation |
| Sell-Through visibility | Weekly updates available | Upload compliance |
| Exception alert response | At least 1 actionable alert generated | Exception log |
| Brand team satisfaction | "Would recommend" rating ≥ 4/5 | Post-pilot survey |

---

## What Happens After Pilot

```
Pilot PASS → Rollout offer (additional distributors, pricing conversation)
Pilot FAIL → Root cause review → Option to re-pilot with changes
Pilot PARTIAL → Specific gap identified → Targeted improvement → Re-evaluate
```

---

## Pricing Framework

> [!IMPORTANT]
> **Pricing numbers require Founder approval before presenting to any prospect.**
> The structure below is the framework. Hard numbers are TBD.

### Pricing Principles

1. **Pilot pricing**: Subsidized / goodwill — brand takes the risk of testing
2. **Production pricing**: Per-distributor, per-month subscription
3. **Value anchor**: ₹15L annual margin recovery baseline → pricing is a fraction of value delivered
4. **Entry point**: Low enough that a single prevented stockout event pays for a month

### Indicative Pricing Tiers (Framework Only — Numbers Pending Founder Approval)

| Tier | Distributors | Model |
|------|-------------|-------|
| Pilot | 1 | [PRICE TBD — subsidized] |
| Starter | 1-5 | [PRICE TBD — per distributor/month] |
| Growth | 6-20 | [PRICE TBD — volume discount] |
| Enterprise | 20+ | [PRICE TBD — annual contract] |

---

## Objection: "We Already Track This in Excel"

> "Excel mein WOC automatically recalculate hota hai jab secondary sales data
> aata hai across 8 sizes, 3 locations, 50 SKUs?"
>
> PSV does not replace Excel. For the first 30 days, **it runs on Excel data**.
> The difference: SMRITI consolidates it, calculates it, and alerts you —
> instead of your team spending 4 hours every week rebuilding the sheet."

---

## Pilot Agreement Checklist

Before pilot starts, confirm:

```
[ ] Brand name and product category confirmed
[ ] Pilot distributor identified (name, city, contact)
[ ] Opening balance format agreed (SMRITI template shared)
[ ] Success criteria agreed and documented
[ ] Week 1 onboarding session scheduled
[ ] Week 4 review session scheduled
[ ] Data sharing method confirmed (email / shared drive / direct upload)
[ ] Pricing discussion scheduled (post-pilot or pre-pilot based on brand preference)
```

---

## Positioning Statement for Closing

> "Yeh pilot aapko ek cheez prove karta hai:
> **Kya PSV aapke actual distributor data pe kaam karta hai?**
>
> Agar haan — phir scaling ka conversation karte hain.
> Agar nahi — aapko kuch invest nahi karna pada.
>
> 30 din. Ek distributor. Real data. Real visibility."

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Pricing numbers require Founder approval before client presentation.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |