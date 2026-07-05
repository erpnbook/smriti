---
Document ID: "DEV-017"
Title: "COMM-08 — PSV Pilot Success Criteria"
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

# COMM-08 — PSV Pilot Success Criteria
**Sprint**: PSV-COMM-001 Wave 1
**Dependency**: Embedded in COMM-04 (Pilot Offer Structure) — shared in same conversation
**Purpose**: Define what "pilot success" means — agreed before Day 1, measured at Day 30
**Owner**: Founder approval required before presenting to any prospect

---

## Why This Document Exists

> "Pilot successful kab mana jayega?"

This question will be asked on Day 1 of every pilot conversation.
If you don't have an answer ready, the pilot has no credibility — even if the product works perfectly.

Success criteria must be:
- **Agreed before pilot starts** (not invented at review time)
- **Measurable from PSV data** (not subjective opinions)
- **Realistic for 30 days** (not 6-month outcomes)
- **Meaningful to the brand** (not just technical metrics)

---

## The Six Criteria

### Criterion 1 — Stockout Reduction

**What it measures**: Did PSV help prevent at least one stockout event during the pilot?

```
Definition: A "stockout event" = WOC drops below 2 weeks at any tracked SKU
             and a reorder or transfer action is taken before actual stockout occurs.

Target:     ≥ 1 stockout prevented during 30-day pilot

Measurement: Exception Log — count of WOC Critical alerts acted upon
```

**Why it matters to the retailer**: Every stockout = a consumer who went to a competitor.

---

### Criterion 2 — Excess Stock Identification

**What it measures**: Did PSV surface inventory that is sitting idle above optimal levels?

```
Definition: "Excess stock" = WOC > 12 weeks at any tracked SKU/location

Target:     ≥ 1 excess stock situation identified and flagged

Measurement: WOC report — count of SKUs with WOC > 12 weeks flagged to brand team
```

**Why it matters**: Capital locked in slow-moving distributor stock = working capital problem.

---

### Criterion 3 — Dead Stock Identification

**What it measures**: Did PSV surface inventory with zero movement for 60+ days?

```
Definition: "Dead stock" = no secondary sales recorded for 60+ consecutive days

Target:     Dead stock inventory identified as ₹X value (any positive amount)

Measurement: Stock Aging report — items with 60+ day inactivity and their stock value
```

**Why it matters**: Dead stock identified = capital recovery opportunity. Even ₹1L surfaced in a pilot is a win.

---

### Criterion 4 — Inventory Balancing Opportunities

**What it measures**: Did PSV identify at least one case where stock could be transferred
from an overstocked location to an understocked location?

```
Definition: One location WOC > 12 weeks + another location WOC < 4 weeks, same SKU

Target:     ≥ 1 transfer opportunity identified

Measurement: Network Transfer Simulator output / Exception Log
```

**Why it matters**: Shows PSV's network intelligence — not just per-distributor tracking.

---

### Criterion 5 — Weeks-of-Cover Visibility Adoption

**What it measures**: Is the brand team actually using WOC data to make decisions?

```
Definition: Brand team references WOC in at least 1 business decision during pilot
            (reorder, transfer, pricing action, or distributor communication)

Target:     ≥ 1 WOC-driven business decision documented

Measurement: Self-reported by brand team at Week 4 review
```

**Why it matters**: Product adoption = product value. A tool that runs but is ignored is a failed pilot.

---

### Criterion 6 — PSV Dashboard Engagement

**What it measures**: Is the brand team logging into PSV and reading the data?

```
Definition: At least 3 PSV dashboard sessions per week by brand team

Target:     ≥ 12 sessions total across 30-day pilot (3/week × 4 weeks)

Measurement: SMRITI activity log
```

**Why it matters**: Engagement signals that the product is useful — not just implemented.

---

## Pilot Pass / Partial / Fail Definition

| Outcome | Criteria Met | Recommended Next Step |
|---------|-------------|----------------------|
| **PASS** | ≥ 4 of 6 criteria met | Rollout conversation — add distributors |
| **PARTIAL** | 2-3 of 6 criteria met | Identify specific gap — targeted re-pilot |
| **FAIL** | ≤ 1 of 6 criteria met | Root cause review — product or process gap |

> [!NOTE]
> A "PARTIAL" is not a failure — it's a diagnostic.
> It tells you exactly which part of PSV's value proposition needs more work or configuration.

---

## Criteria Agreement Process

**Before pilot starts** (Week 1 onboarding session):

```
Step 1: Share this document with brand team
Step 2: Discuss each criterion — adjust targets to their context
Step 3: Confirm which criteria they prioritize most (rank 1-6)
Step 4: Document agreed targets in writing
Step 5: Both parties sign off (email confirmation acceptable)
```

---

## 30-Day Review Meeting Agenda

```
Week 4 Review — 45 minutes

00:00 – 10:00   Data walkthrough (PSV reports)
10:00 – 25:00   Criterion-by-criterion scorecard
25:00 – 35:00   Business impact discussion
35:00 – 45:00   Next steps (rollout / re-pilot / close)
```

---

## Customization by Brand Type

| Brand Type | Highest Priority Criterion |
|-----------|--------------------------|
| Footwear brand | Criterion 3 (Dead Stock) + Criterion 4 (Balancing) |
| FMCG | Criterion 1 (Stockout) + Criterion 5 (WOC Adoption) |
| Apparel | Criterion 2 (Excess) + Criterion 3 (Dead Stock) |
| Distributor-first brand | Criterion 4 (Balancing) + Criterion 6 (Engagement) |

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Criteria targets may be adjusted per pilot — core framework is fixed.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |