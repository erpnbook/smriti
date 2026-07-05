---
Document ID: "DEV-040"
Title: "PILOT-001 — Tattly Threads Pilot Execution Plan"
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

# PILOT-001 — Tattly Threads Pilot Execution Plan
**Document Type**: Pilot Governance + Field Operations
**Status**: READY — Awaiting Pilot Start Date
**Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Principle**: PSV_COMMERCIALIZATION_PHASE = PILOT_EXECUTION

---

## 1. Executive Summary

**Objective**: Validate that PSV delivers measurable business value on real distributor data
within a 30-day engagement — and that the Tattly Threads team will use it weekly.

**What this pilot must answer**:
> "Will a real distributor upload data and act on PSV alerts every week?"

**What this pilot is NOT**:
- Not a product demo
- Not a feature showcase
- Not a guarantee of commercial rollout

**What happens after**:

| Pilot Score | Outcome |
|------------|---------|
| 4–6 criteria ✅ | Commercial rollout discussion — additional distributors |
| 2–3 criteria ✅ | Targeted re-pilot — specific gap identified and fixed |
| 0–1 criteria ✅ | Root cause review — product or process gap |

---

## 2. Founder Dashboard

> Review this section every Monday during the pilot.

```
PILOT-001 — Tattly Threads
Brand: Tattly Threads (Footwear)
Pilot Start: [TBD — First Upload Date]
Pilot End:   [Start + 30 days]
Distributor: [Name, City]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Week 0 (Setup)         □ Not Started
Week 1 (Data)          □ Not Started
Week 2 (Exceptions)    □ Not Started
Week 3 (Decisions)     □ Not Started
Week 4 (Review)        □ Not Started

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PILOT SCORECARD (update weekly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ C1  Distributor uploaded data weekly
□ C2  WOC Critical/Warning alert generated
□ C3  Dead stock identified (any ₹ value)
□ C4  Transfer opportunity identified
□ C5  At least 1 PSV-driven business decision taken
□ C6  Weekly dashboard usage (≥3 sessions/week)

CURRENT SCORE:  □ / 6
PILOT STATUS:   □ On Track  □ At Risk  □ Intervention Needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GO / NO-GO (fill Week 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score 4–6: PASS  → Commercial rollout discussion
Score 2–3: PARTIAL → Re-pilot (specific gap: _________)
Score 0–1: FAIL  → Root cause review

DECISION: _______________________
DATE:     _______________________
SIGNED:   Jawahar R. Mallah, Founder
```

---

## 3. Pilot Success Criteria

Full criteria detail: [COMM-08 Pilot Success Criteria](./comm_08_pilot_success_criteria.md)

**Summary** — agree these with Tattly Threads on Day 1:

| # | Criterion | Target | Measurement |
|---|-----------|--------|-------------|
| C1 | Stockout Prevention | ≥1 WOC Critical alert acted upon | Exception Log |
| C2 | Excess Stock Identified | ≥1 SKU with WOC > 12 weeks flagged | WOC Report |
| C3 | Dead Stock Identified | Any ₹ value surfaced (60+ days inactive) | Aging Report |
| C4 | Network Balancing | ≥1 transfer opportunity detected | Network View |
| C5 | WOC-Driven Decision | ≥1 business action triggered by WOC data | Self-reported |
| C6 | Dashboard Engagement | ≥12 total sessions in 30 days | Activity Log |

### PILOT_METRIC_007 — Decision Adoption Rate

```
Formula:  PSV-driven decisions taken
          ─────────────────────────────
          PSV recommendations shown

Target:   > 25%

Why:      This metric is not a pilot pass/fail criterion.
          It is a PDT architecture input.

          If decision adoption > 25%: users trust PSV signals.
          Forecasting value in PDT is HIGH.

          If decision adoption < 10%: signal-to-action gap.
          PDT needs explainability layer before forecasting.

          Capture this number at Week 4 review.
          It will directly shape PDT-ARCH-001 design.
```

> **Step 0**: Present this table to Tattly Threads in Week 0 kickoff.
> Get written confirmation of agreed targets before Week 1 begins.
> No pilot should start without signed criteria.

---

## 4. Week-by-Week Operational Plan

### Week 0 — Setup (Days -7 to 0)

**Goal**: Everything in place before first data upload.

**AITDL Tasks**:
```
[ ] PSV instance provisioned for Tattly Threads
[ ] Upload template customized (brand name, SKUs pre-loaded)
[ ] Opening balance format confirmed with distributor
[ ] PSV dashboard access credentials created and tested
[ ] Alert thresholds configured (WOC: Critical=2wk, Warning=4wk; Dead=60 days)
[ ] Kickoff meeting scheduled (30 min — brand + distributor + AITDL)
```

**Tattly Threads Tasks**:
```
[ ] Identify pilot distributor (name, city, contact person)
[ ] Collect opening stock snapshot (by SKU, by size)
[ ] Share past 8 weeks of secondary sales (if available)
[ ] Confirm data coordinator (who will fill weekly template)
[ ] Sign pilot success criteria (COMM-08)
```

**Kickoff Meeting Agenda (30 min)**:
```
00:00 - 05:00  Pilot overview + objectives
05:00 - 15:00  Upload template walkthrough (live demo)
15:00 - 22:00  Success criteria agreement (COMM-08)
22:00 - 28:00  Week 1 schedule + data coordinator confirmed
28:00 - 30:00  Next check-in: [Day 7 time]
```

**Week 0 Exit Gate**:
```
□ Credentials active
□ Template shared and understood by distributor
□ Opening balance uploaded
□ Success criteria agreed in writing
□ Week 1 check-in scheduled
```

---

### Week 1 — First Data (Days 1–7)

**Goal**: First upload processed, first WOC calculations visible, system working on real data.

**AITDL Tasks**:
```
[ ] Monitor for first upload (expected: Day 3-5)
[ ] Validate upload format (no blank rows, correct SKUs)
[ ] Confirm WOC calculations are generating correctly
[ ] Check for any data errors and notify brand coordinator
[ ] Send "Week 1 Status" message to Tattly Threads team
```

**Tattly Threads / Distributor Tasks**:
```
[ ] Complete Week 1 secondary sales (template row per SKU/size)
[ ] Upload by Friday of Week 1
[ ] Flag any template confusion immediately
```

**Brand Planner Check (Wednesday)**:
```
[ ] Open PSV dashboard — confirm data visible
[ ] Review Sell-Through tracker — does data look realistic?
[ ] Review WOC — any unexpected Critical alerts?
[ ] Document first impression: "What surprised you?"
```

**Week 1 Exit Gate**:
```
□ At least 1 upload processed successfully
□ WOC data visible and plausible
□ No critical data errors
□ Distributor confirmed template process is workable
```

---

### Week 2 — Exception Validation (Days 8–14)

**Goal**: Real exceptions surface. Team sees PSV's alert engine working on their data.

**AITDL Tasks**:
```
[ ] Review Exception Log with Tattly Threads team (30 min call)
[ ] Walk through any WOC alerts generated
[ ] Walk through any Dead Stock flags generated
[ ] Check Network view — any transfer opportunity visible?
[ ] Document: which exceptions are real vs data quality issues?
```

**Tattly Threads Tasks**:
```
[ ] Week 2 upload (by Friday)
[ ] Review Exception Log after AITDL call
[ ] For each WOC Critical alert: verify physical stock count
[ ] For each Dead Stock flag: confirm item is genuinely slow
[ ] Log first decision triggered by PSV (if any)
```

**Key Question for Week 2 Review**:
> "Is PSV telling you something you didn't already know?"
> (Yes = value confirmed. No = dig into why — data gap or no actual problem?)

**Week 2 Exit Gate**:
```
□ ≥1 exception alert generated (C1, C2, or C3)
□ Alert validated as real (not data error)
□ Team reviewed exception log independently (without AITDL prompting)
□ Week 3 decision-tracking format agreed
```

---

### Week 3 — Decision Adoption (Days 15–21)

**Goal**: Prove PSV changes decisions — not just displays data.

**AITDL Tasks**:
```
[ ] Weekly upload check
[ ] Review C5 (WOC-driven decisions) — ask directly: "Any action taken because of PSV?"
[ ] If no decisions yet: guided review workshop (see Risk Register)
[ ] Document all decisions taken with PSV as input
[ ] Check C6 (dashboard engagement) — pull activity log
```

**Tattly Threads Tasks**:
```
[ ] Week 3 upload
[ ] Log every business action influenced by PSV data (reorder / transfer / call to distributor)
[ ] Report: "What did we do differently because of PSV this week?"
```

**Decision Log Format** (capture one per action):
```
Date    : _______________
Alert   : WOC Critical / Dead Stock / Transfer Opportunity / Other
Action  : Reorder / Transfer / Markdown / No Action (explain)
Result  : Pending / Stockout avoided / Capital recovered / Other
Notes   : _______________
```

**Week 3 Exit Gate**:
```
□ ≥1 PSV-driven decision logged (C5 progress)
□ Dashboard engagement ≥3 sessions this week (C6 progress)
□ No upload missed across Weeks 1–3
□ Pilot on track for ≥4 criteria by Week 4
```

---

### Week 4 — Business Review (Days 22–30)

**Goal**: Score the pilot. Make the Go/No-Go decision. Agree next steps.

**AITDL Tasks (Days 22–28)**:
```
[ ] Compile all 5 pilot reports:
    - Sell-Through Report (30-day, all SKUs)
    - WOC Accuracy Report (forecast vs actual)
    - Exception Log Summary (all alerts + actions)
    - Reconciliation Summary (primary vs secondary)
    - Pilot Assessment (Go/No-Go recommendation with data)
[ ] Score criteria C1–C6 with evidence
[ ] Prepare Week 4 Review deck (30 min)
[ ] Draft Go/No-Go recommendation
```

**Week 4 Review Meeting (45 min)**:
```
00:00 – 10:00  Data walkthrough (5 reports)
10:00 – 25:00  Criteria scorecard (C1–C6 with evidence)
25:00 – 35:00  Business impact discussion
               "What changed in 30 days because of PSV?"
35:00 – 42:00  Go/No-Go decision
42:00 – 45:00  Next steps (rollout / re-pilot / close)
```

---

## 5. Risk Register

> Review this every Monday with the pilot status.

| # | Risk | Owner | Trigger | Intervention |
|---|------|-------|---------|-------------|
| R1 | Distributor stops uploading | Distributor | No upload for 7 days | Direct call from brand manager — not email |
| R2 | Data quality too poor | Brand Planner | > 10% invalid rows in upload | 30-min training session with distributor coordinator |
| R3 | No PSV-driven decisions by Week 3 | Pilot Lead | C5 = 0 at Week 3 mid-point | Guided review workshop — AITDL reviews exceptions with brand planner and identifies 1 actionable item together |
| R4 | Dashboard not being used | Pilot Lead | < 3 sessions/week by Week 2 | AITDL sends weekly summary email — lower engagement barrier |
| R5 | Distributor refuses to participate | Brand Team | Week 0 kickoff fails | Identify alternate distributor — pilot can shift, cannot skip |
| R6 | Opening balance wrong | Brand Planner | WOC values implausible in Week 1 | Physical count requested — rebase opening balance |
| R7 | PSV technical issue | AITDL Engineering | Any error blocking upload or dashboard | Critical defect track — fix within 24 hours |
| R8 | Pilot lead changes | Brand Team | Any time | Handoff document + 30-min briefing from AITDL |

---

## 6. Escalation Matrix

| Situation | Escalate To | Timeline |
|-----------|------------|---------|
| R7 — Technical issue blocking pilot | AITDL Engineering + Founder | Immediately |
| R1 — Distributor not uploading (2 weeks) | Brand Owner + Founder | Day 14 |
| R3 — No decisions by Week 3 | Founder review | Day 21 |
| Pilot trending toward FAIL at Week 3 | Founder decision: continue / intervene / close | Day 21 |
| Distributor requests data deletion | Founder + Legal | Immediately |

**Founder Hotline**: Direct message or call — do not wait for weekly review for R7, R1 (2 weeks), or data requests.

---

## 7. Week-4 Review Agenda

**Duration**: 45 minutes
**Attendees**: Tattly Threads brand owner + brand planner, AITDL (Founder + pilot lead)
**Format**: Video call or in-person

```
00:00 – 10:00  30-Day Data Summary
               - Sell-Through % across SKUs
               - WOC trend (Week 1 → Week 4)
               - Exception alerts generated
               - Reconciliation variance

10:00 – 25:00  Criteria Scorecard (C1–C6)
               For each criterion: Evidence shown → Score confirmed

25:00 – 35:00  Business Impact
               "What did PSV change in 30 days?"
               "What would you have missed without it?"
               "What frustrated you?"

35:00 – 42:00  Go / No-Go Decision
               Founder presents recommendation
               Brand owner decides

42:00 – 45:00  Next Steps
               PASS → "Here's the rollout proposal"
               PARTIAL → "Here's what we fix and the re-pilot offer"
               FAIL → "Here's what we learned and why"
```

---

## 8. Go / No-Go Decision Framework

### Scoring

| Criteria Met | Score | Verdict | Next Action |
|-------------|-------|---------|------------|
| 5–6 of 6 | Strong PASS | Enthusiastic rollout | Offer Growth tier immediately |
| 4 of 6 | PASS | Rollout with notes | Offer Starter tier + address gaps |
| 2–3 of 6 | PARTIAL | Re-pilot | Identify weakest criterion → targeted fix |
| 0–1 of 6 | FAIL | Root cause | Product gap vs process gap vs wrong distributor |

### Questions for Fail / Partial Analysis

```
If C1 failed (no stockout prevented):
  → Was WOC data accurate? Or was upload too infrequent?

If C3 failed (no dead stock found):
  → Does Tattly Threads actually have aging inventory? Or is the product moving fast?
    (Fast-moving = PSV still valuable for WOC, not dead stock)

If C5 failed (no decisions changed):
  → Was the data reviewed? Or did it sit in the dashboard untouched?
    (Untouched = adoption problem. Reviewed but no action = no exceptions to act on)

If C6 failed (low engagement):
  → Who was the primary user? Did they have time?
    (Operational mismatch = change the user, not the product)
```

### Post-Pilot Actions

**If PASS**:
```
1. Draft COMM-10 Success Story (Tattly Threads)
2. Unlock production pricing conversation (COMM-12)
3. Offer Growth tier (6-20 distributors)
4. Start PDT-ARCH-001 architecture discovery
```

**If PARTIAL**:
```
1. Document specific gap
2. Fix gap (engineering if needed — unfreeze for critical path)
3. Offer 15-day re-pilot at no charge
4. Do NOT build new features — fix what failed
```

**If FAIL**:
```
1. Root cause documented
2. Share findings with Tattly Threads transparently
3. Decide: product gap (fix) vs wrong fit (move to next prospect)
4. Do NOT offer re-pilot until root cause is resolved
```

---

---

## PDT Architecture Block

```
PDT_ARCHITECTURE_BLOCKED_BY:  PILOT-001 Findings

Unlock Condition:             Week-4 Review Complete

Reason:
  Pilot will surface: upload frequency, data quality,
  distributor participation, WOC behavior, exception
  response rates, and Decision Adoption Rate (M-007).

  These inputs directly determine PDT forecasting
  architecture. Building PDT before pilot findings
  means rebuilding after them.

  DO NOT start PDT-ARCH-001 until PILOT-001 Week-4
  review is complete and findings are documented.

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
Date:      2026-06-24
```

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*This document runs Pilot Customer #1. It is not a product document — it is a business execution document.*
*Update weekly. Review with Founder every Monday.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |