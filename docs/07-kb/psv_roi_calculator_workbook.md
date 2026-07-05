---
Document ID: "KB-015"
Title: "COMM-07 — PSV ROI Workbook"
Owner: "Support Team"
Audience: "Support Engineer"
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

# COMM-07 — PSV ROI Workbook
**Sprint**: PSV-COMM-001
**Audience**: CFO, Brand Owner, Operations Head — "Kitna paisa bachega?"
**Purpose**: Enable brand-specific ROI calculation using their own numbers
**Usage**: Fill with prospect's numbers during or after demo

---

## The ROI Equation

```
Annual Margin Recovery
= Prevented Stockouts × Avg Contribution Margin per Item

Where:
  Prevented Stockouts = Annual Dispatch × Stockout Rate %
```

---

## Section 1 — Brand Inputs (Fill With Prospect's Numbers)

| Input | Your Number | Baseline (for reference) |
|-------|------------|--------------------------|
| Annual items dispatched to distributor network | __________ | 50,000 |
| Estimated stockout rate (% of dispatched items) | _______% | 6% |
| Average MRP per item | ₹__________ | ₹1,200 |
| Brand contribution margin (% of MRP) | _______% | 40% |
| Number of distributors | __________ | 1 (pilot) |

---

## Section 2 — Stockout Recovery Calculation

| Step | Formula | Baseline | Your Number |
|------|---------|----------|------------|
| Annual dispatched | Input | 50,000 | __________ |
| Stockout rate | Input | 6% | _______% |
| Prevented stockouts | Dispatched × Rate | **3,000 items** | __________ |
| Avg margin/item | MRP × Margin % | ₹1,200 × 40% = **₹480** | ₹__________ |
| **Annual stockout recovery** | Items × Margin | **₹14,40,000** | ₹__________ |

---

## Section 3 — Dead Stock Recovery Calculation

| Input | Your Number | Baseline |
|-------|------------|----------|
| Estimated dead stock qty (items > 60 days) | __________ | 200 items |
| Average stock value per item | ₹__________ | ₹720 (60% of MRP) |
| Estimated dead stock value | __________ | ₹1,44,000 |
| Expected recovery % (transfer/return/markdown) | _______% | 50% |
| **Dead stock capital recovered** | Value × Recovery % | **₹72,000** | ₹__________ |

---

## Section 4 — Holding Cost Reduction

| Input | Your Number | Baseline |
|-------|------------|----------|
| Average excess stock held per distributor (items) | __________ | 500 items |
| Monthly holding cost per item | ₹__________ | ₹10/item/month |
| Months of excess holding reduced | __________ | 2 months |
| **Holding cost saved** | Items × Cost × Months | **₹10,000** | ₹__________ |

---

## Section 5 — Total Annual ROI Summary

| Category | Baseline | Your Number |
|----------|----------|------------|
| Stockout Recovery | ₹14,40,000 | ₹__________ |
| Dead Stock Recovery | ₹72,000 | ₹__________ |
| Holding Cost Saved | ₹10,000 | ₹__________ |
| **Total Annual Recovery** | **₹15,22,000** | **₹__________** |

---

## Section 6 — Sensitivity Table

Use this when a prospect challenges the baseline assumptions:

| Annual Dispatch | Stockout Rate | Margin/Item | Annual Recovery |
|----------------|--------------|-------------|----------------|
| 20,000 | 6% | ₹300 | ₹3,60,000 |
| 20,000 | 6% | ₹500 | ₹6,00,000 |
| 50,000 | 6% | ₹480 | ₹14,40,000 ← baseline |
| 50,000 | 6% | ₹800 | ₹24,00,000 |
| 1,00,000 | 6% | ₹500 | ₹30,00,000 |
| 1,00,000 | 10% | ₹500 | ₹50,00,000 |

> **Note to salesperson**: Use the prospect's own numbers — never anchor on baseline.
> Ask: "Aapke annual dispatch kitne items hain?" Then fill Section 1 together.

---

## Section 7 — Payback Period Framing

Once you have their annual recovery number, use this framing:

```
If Annual Recovery = ₹15,00,000

Monthly recovery = ₹15,00,000 / 12 = ₹1,25,000 / month

PSV pays for itself if monthly cost < ₹1,25,000

[Insert PSV pricing once COMM-12 pricing is approved]
```

> **Pricing gap**: PSV pricing is pending Founder approval (COMM-12).
> Do not quote pricing in this workbook. Show recovery first, then pricing separately.

---

## Section 8 — CFO-Level Summary (One Page)

**Question CFO asks**: "What is the financial case for PSV?"

**Answer** (fill with their numbers):

```
Annual inventory dispatched  : [N] items
Estimated stockouts prevented : [N] items ([X]% of dispatch)
Margin recovered per item    : ₹[X] ([X]% of MRP)
Annual stockout recovery     : ₹[X]

Dead stock surfaced          : ₹[X] (estimated at pilot)
Expected recovery            : ₹[X] ([X]% transfer/return)

Total annual financial impact: ₹[X]
PSV annual cost              : [PENDING — see COMM-12]
Estimated payback period     : [PENDING]
```

---

## Formula Governance

All formulas in this workbook are governed by Formula Registry:

| Formula | Registry ID | Expression |
|---------|------------|------------|
| Sell-Through % | SAL-001 | `sold_qty / dispatched_qty × 100` |
| Weeks of Cover | INV-002 | `current_stock / weekly_velocity` |
| Dead Stock Score | INV-003 | `inactive_days × stock_value` |

*Formula Registry*: `docs/kb/kgf/formula-registry.md`

---

*Governance: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*All ROI figures are estimates based on brand-specific inputs. Actual results depend on pilot data.*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |