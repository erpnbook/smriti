---
Document ID: "DEV-019"
Title: "COMM-12 — PSV Feature Packaging & Tier Definition"
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

# COMM-12 — PSV Feature Packaging & Tier Definition
**Sprint**: PSV-COMM-001
**Audience**: Founder (approval), Sales team (reference)
**Status**: Framework complete — pricing numbers require Founder approval before client presentation
**Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL

---

## What Is PSV v1.1?

PSV v1.1 is the **commercially available version** of SMRITI Party Stock Visibility.

```
Version       : 1.1 Final Freeze + Reorder Intelligence
Platform      : SMRITI Retail OS on Frappe v16
Architecture  : Approved
DocTypes      : 9 (8 PSV core + 1 Reorder Rule)
Pilot Status  : Phase 1.2 frozen — Pilot Ready
```

---

## What's Included in PSV v1.1

### Core Feature Set (All Tiers)

| Feature | Description |
|---------|-------------|
| **PSV Shadow Ledger** | Parallel stock tracking at distributor level — separate from ERPNext |
| **Primary Sales Upload** | Brand dispatch records ingested via Excel or ERPNext export |
| **Secondary Sales Upload** | Distributor sell-through data via Excel upload template |
| **Sell-Through Tracker** | Real-time Sell-Through % by SKU and distributor |
| **Weeks of Cover (WOC)** | Automatic WOC calculation with Critical / Warning / Optimal bands |
| **Stock Aging Report** | 4-band aging classification: Active / Slowing / Aging / Dead Stock |
| **Exception Alerts** | WOC Critical, WOC Warning, Dead Stock, Excess Stock, Variance flags |
| **Exception Log** | Full audit trail of all alerts with timestamps and response records |
| **Reconciliation Cycle** | Primary vs secondary reconciliation with variance flagging |
| **Network Stock View** | Multi-distributor view with transfer opportunity detection |
| **Opening Balance Management** | Distributor opening stock capture and correction workflow |

### V1.1 Addition (Reorder Intelligence)

| Feature | Description |
|---------|-------------|
| **Reorder Rules Engine** | Configurable reorder thresholds per SKU / distributor |
| **Reorder Recommendations** | System-suggested reorder quantity based on WOC and velocity |

> V1.1 Reorder Engine: Deploy after pilot stabilization (Phase 1.2 → Phase 1.3).

---

## What Is NOT Included in v1.1

| Not Included | Available In |
|-------------|-------------|
| AI Demand Forecasting | PSV Phase 2 (Future) |
| Automated Purchase Orders | Phase 1.4 (Automation Layer) |
| Recovery Suggestions Engine | Phase 1.3B |
| Distributor Mobile App | Future |
| ERP API Integration | Post-pilot (Phase 1.3+) |
| Multi-brand / Multi-company | Future |

---

## Pilot Tier

**Definition**: First engagement — validate value before pricing conversation.

> [!IMPORTANT]
> **Pricing Governance Decision — 2026-06-24**
> Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
>
> **Pilot pricing does NOT block the first pilot.**
> Objective at pilot stage: Validate Value → Not Maximize Revenue.
> Production pricing is locked post-pilot based on field evidence.
>
> Pilot Package = Founder Approved to proceed.
> Production Pricing = Post-pilot decision.

| Parameter | Value |
|-----------|-------|
| Distributors | 1 |
| Duration | 30 days |
| Data method | Excel upload |
| Features | Full PSV v1.1 core feature set |
| Price | **Founder-approved pilot terms (case-by-case)** |
| Commitment | None — exit after pilot with no penalty |
| Deliverables | 5 pilot reports (see COMM-04) |
| Success Criteria | COMM-08 (6 criteria, agreed Day 1) |
| Weekly Review | Brand Planner + AITDL — 30 min |

---

## Production Tiers (Post-Pilot — Pricing TBD After Field Evidence)

| Tier | Distributors | Target Brand | Pricing |
|------|-------------|-------------|---------|
| **Starter** | 1–5 | Small brand, regional distribution | [Post-pilot] |
| **Growth** | 6–20 | Mid-market brand, multi-state | [Post-pilot] |
| **Enterprise** | 20+ | Large brand, national network | [Post-pilot] |

### Pricing Principles (Approved)

1. **Value-anchored**: PSV baseline recovery = ₹15L/year → pricing is a fraction of value delivered
2. **Per-distributor model**: Scales naturally with network size
3. **Pilot = subsidized entry**: Pilot price is below production price — reduces switching cost
4. **Annual preferred**: Annual commitment preferred; monthly available at premium
5. **No per-seat pricing**: PSV is a network product, not a per-user product

> [!IMPORTANT]
> Pricing numbers require explicit Founder approval before any client or prospect conversation.
> Do not quote figures from this document without approval.

---

## Value Proposition by Tier

### Pilot (1 Distributor)

```
"Prove PSV works on your data before committing."
Key message: Zero risk. 30 days. Real data. Real results.
```

### Starter (1–5 Distributors)

```
"Visibility across your core distribution network."
Key message: Know what's moving. Stop guessing.
```

### Growth (6–20 Distributors)

```
"Network intelligence at scale."
Key message: Network balancing, WOC trends, regional exception management.
```

### Enterprise (20+ Distributors)

```
"Complete channel stock command."
Key message: Full network visibility, integration, custom reporting.
```

---

## Competitive Differentiation

| Dimension | PSV | Generic BI Tools | Manual Tracking |
|-----------|-----|-----------------|----------------|
| PSV-specific formulas (WOC, Sell-Through) | ✅ Built-in | ❌ Custom build required | ❌ None |
| Distributor-level shadow ledger | ✅ | ❌ | ❌ |
| Exception alerts | ✅ Automatic | ⚠️ Custom alerting | ❌ |
| Retail-specific intelligence | ✅ | ❌ | ❌ |
| No distributor system change | ✅ Excel upload | ⚠️ Often requires integration | ✅ |
| Implementation time | Days | Months | Immediate but fragile |

---

## Approval Gate

```
Pricing numbers approved for client presentation: ❌ PENDING

To approve pricing:
  1. Founder reviews this document
  2. Founder adds approved pricing to this section
  3. Commits to main branch
  4. Sales team may present from approved version only

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
```

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*This document is an internal commercial reference. Pricing section is not complete until Founder approval.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |