---
Document ID: "USER-013"
Title: "PSV — Party Stock Visibility"
Owner: "Operations Team"
Audience: "End User"
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

# PSV — Party Stock Visibility
## Executive One-Pager

**Audit Execution**: AITDL
**Audit Owner**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Document Version**: 1.0 — 2026-06-24

---

## The Problem

Brands dispatching stock to distributors lose visibility the moment goods leave the warehouse.
No one knows how much stock is sitting at each distributor, which sizes are moving,
and which are turning into dead capital.

> **Result**: Stockouts at retail outlets coexist with excess stock at distributor depots —
> in the same territory, at the same time.

---

## The Solution

**SMRITI PSV (Party Stock Visibility)** gives brands real-time visibility into distributor inventory
without disrupting distributor workflows.

- **Sell-Through Tracking**: Know what percentage of dispatched stock has reached end consumers
- **Weeks of Cover (WOC)**: Know how many weeks of sales each distributor can sustain before stockout
- **Dead Stock Alerts**: Surface aging inventory before it becomes a write-off

PSV does not replace distributor systems. It creates a parallel shadow ledger — read-only from distributor uploads, actionable for the brand.

---

## Three Numbers That Drive Decisions

| Metric | Formula | What It Tells You |
|--------|---------|------------------|
| **Sell-Through %** | `sold_qty / dispatched_qty × 100` | How fast distributor is converting your stock into revenue |
| **Weeks of Cover** | `current_stock / weekly_velocity` | How many weeks before this distributor hits a stockout |
| **Dead Stock Value** | `inactive_days × stock_value` | Capital locked in slow-moving inventory |

---

## ROI Proof

| Step | Calculation | Result |
|------|------------|--------|
| Annual cohort size | Network dispatched | 50,000 items |
| Stockout rate | Industry typical | 6% |
| Stockouts prevented | 50,000 × 6% | **3,000 items** |
| Avg. contribution margin | MRP ₹1,200 × 40% brand margin | **₹500 / item** |
| Annual margin recovery | 3,000 × ₹500 | **₹15,00,000** |

> **Assumption visible**: ₹500/item contribution margin assumes avg. MRP of ₹1,200
> with 40% brand contribution margin — typical for mid-market footwear and apparel.
> Adjust the margin per item for your product category to get your specific recovery figure.

```
Lower margin product  (₹300/item): 3,000 × ₹300 = ₹9,00,000 / year
Mid-market footwear   (₹500/item): 3,000 × ₹500 = ₹15,00,000 / year  ← baseline
Premium product       (₹800/item): 3,000 × ₹800 = ₹24,00,000 / year
```

---

## Current Status

| Item | Status |
|------|--------|
| Architecture | ✅ Approved |
| DocTypes | ✅ 9 deployed (8 core + Reorder Intelligence) |
| Phase 1 & 2 | ✅ Complete |
| Phase 3 | ✅ Pilot-ready |
| Pilot Partner | 🟡 Tattly Threads — Phase 1.2 Frozen |
| V1.1 Reorder Engine | ⏸ Post-pilot stabilization |

**Platform**: SMRITI Retail OS on Frappe v16
**Version**: PSV v1.1 — Final Freeze + Reorder Intelligence

---

## Phase Readiness

```
Phase 1 — Data Foundation      ✅  COMPLETE
Phase 2 — Reconciliation       ✅  COMPLETE
Phase 3 — Analytics & Alerts   ✅  PILOT READY
Phase 4 — Reorder Intelligence ⏸  POST-PILOT
```

---

## Next Step

> **First Live Distributor Upload → First Reconciliation Cycle → Pilot Sign-off**

PSV is ready to onboard its first pilot distributor. The upload workflow, ledger engine,
reconciliation cycle, and exception alerts are all operational.

**To activate PSV for a new brand or distributor network:**
Contact: AITDL — Jawahar R. Mallah | jawahar.mallah@gmail.com

---

*"Always decision-ready."*
*— Jawahar R. Mallah, Founder & Chief Architect, AITDL*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |