---
Document ID: "USER-029"
Title: "Volume 6 — PSV User Manual"
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

# Volume 6 — PSV User Manual
## SMRITI Party Stock Visibility

**Version**: 1.1
**Release Date**: 2026-06-24
**Platform**: SMRITI Retail OS on Frappe v16
**Intended Audience**: Brand Planners, Distributors, Operations Teams, Pilot Partners

---

### Author

**Author**: Jawahar R. Mallah
**Designation**: Founder & Chief Architect
**Organization**: AITDL — AI Technology & Development Lab
**Experience**: 20+ Years in Software Development, Retail Technology, Distribution Systems,
POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> *"Always decision-ready."*
> — Jawahar R. Mallah

---

## Chapter 1 — What Is PSV?

**PSV (Party Stock Visibility)** is SMRITI's channel inventory intelligence module.

It gives brands real-time visibility into how much stock their distributors hold,
how fast it is selling, and where the risks are — before those risks become losses.

### What PSV Is

- A **shadow ledger** that tracks stock at distributor locations in parallel to your own warehouse
- A **sell-through tracker** that measures how fast primary stock converts to consumer sales
- An **alert engine** that flags stockouts, dead stock, and excess inventory before damage is done
- A **network intelligence layer** that surfaces transfer opportunities between distributor locations

### What PSV Is Not

- **Not an ERP replacement** — PSV extends your ERP's visibility beyond your warehouse
- **Not a distributor management system** — distributors keep their own systems unchanged
- **Not surveillance** — distributors control what they share; PSV creates mutual benefit
- **Not a billing system** — PSV does not process transactions or financials
- **Not an API-integration requirement** — works with Excel uploads at pilot stage

---

## Chapter 2 — Business Problems Solved

### Problem 1: Invisible Distributor Inventory

After a brand dispatches stock to a distributor, visibility ends.
The brand has no real-time data on what remains, what is selling, or what has stalled.

**PSV Solution**: Shadow ledger tracks every dispatch, every secondary sale, every balance.

---

### Problem 2: Reactive Replenishment

Brands reorder when distributors call — often after stockouts have already occurred.
By then, consumers have purchased elsewhere.

**PSV Solution**: WOC (Weeks of Cover) alerts at 4-week and 2-week thresholds —
giving brands lead time to reorder before stockout.

---

### Problem 3: Capital Locked in Dead Stock

Stock that stops moving sits at distributor depots for months.
It is discovered only during physical audits — by which time significant capital is locked.

**PSV Solution**: Dead stock flagged automatically at 60 days of zero movement,
with estimated capital value surfaced for immediate action.

---

### Problem 4: No Network View

Brands with multiple distributors cannot see across their network.
One distributor may be overstocked while another is in stockout — same SKU, adjacent cities.

**PSV Solution**: Network stock view identifies imbalances and recommends transfers,
eliminating fresh purchases and unlocking existing inventory.

---

## Chapter 3 — Key Concepts

### Weeks of Cover (WOC)

```
Formula:    WOC = current_stock / weekly_velocity
Example:    140 pcs stock ÷ 35 pcs/week = 4.0 weeks
```

**What it means**: How many weeks of sales the distributor can sustain before running out.

| WOC Range | Status | Action |
|-----------|--------|--------|
| > 12 weeks | Excess Stock | Consider transfer or return |
| 4 – 12 weeks | Optimal | Monitor |
| 2 – 4 weeks | Warning | Plan reorder now |
| < 2 weeks | Critical | Immediate reorder / transfer |

---

### Sell-Through %

```
Formula:    Sell-Through % = sold_qty / dispatched_qty × 100
Example:    850 pcs sold ÷ 1,000 pcs dispatched × 100 = 85%
```

**What it means**: What percentage of dispatched stock has reached end consumers.

| Sell-Through % | Status | Interpretation |
|----------------|--------|---------------|
| ≥ 80% | Excellent | Fast-turning SKU — prioritize replenishment |
| 50–79% | Healthy | Normal velocity — monitor |
| < 50% | At Risk | Investigate: sizing issue, location, competition |

---

### Dead Stock

```
Threshold:  No secondary sales for 60+ consecutive days
Value:      Dead Stock Value = stock_quantity × avg_stock_value
```

**What it means**: Inventory that has stopped moving and is locking capital.
At 60 days — action recommended. At 90 days — urgent recovery required.

---

### Stockout Risk

```
Trigger:    WOC < 2 weeks (Critical alert)
Lead time:  Act within 5 days of alert for standard reorder cycles
```

**What it means**: The distributor will run out of stock before the next replenishment cycle.
PSV alerts 4 weeks before (Warning) and 2 weeks before (Critical) — providing two decision windows.

---

## Chapter 4 — Dashboard Walkthrough

### Distributor Sell-Through Tracker

**Location**: PSV Dashboard → Sell-Through tab

Shows for each distributor:
- Primary sales (dispatched by brand)
- Secondary sales (sold by distributor to retailers)
- Sell-Through % (auto-calculated)
- WOC (auto-calculated from secondary sales velocity)
- Alert status (Normal / Warning / Critical)

**How to read it**:
- Red row = WOC Critical (< 2 weeks) — act immediately
- Yellow row = WOC Warning (< 4 weeks) — plan reorder
- Green row = Optimal — monitor

---

### Stock Aging Report

**Location**: PSV Dashboard → Aging tab

Shows all SKUs at each distributor, classified into aging bands:
- **0-30 days**: Active — normal
- **31-60 days**: Slowing — watch
- **61-90 days**: Aging — plan action
- **90+ days**: Dead Stock — act now

**Filter**: Use "Show only Dead Stock" to surface critical capital lock.

---

### Network Stock View

**Location**: PSV Dashboard → Network tab

Shows all distributor locations on one screen with:
- Current stock per location
- WOC per location
- Transfer opportunities (highlighted when imbalance detected)

---

### Exception Log

**Location**: PSV Dashboard → Exceptions tab

All system-generated alerts in chronological order:
- Stockout Risk alerts
- Dead Stock flags
- Variance flags (physical vs ledger mismatch)
- Excess stock flags

Each alert shows: SKU, location, trigger value, recommended action.

---

## Chapter 5 — Daily Workflow

### Brand Planner (Weekly Cycle)

```
Monday:
  [ ] Check Exception Log — any new Critical alerts?
  [ ] Review WOC for all distributors — any < 4 weeks?
  [ ] Initiate reorders for WOC < 2 weeks

Wednesday:
  [ ] Review Sell-Through tracker — any SKU < 50%?
  [ ] Check Stock Aging — any new Dead Stock flags?
  [ ] Network view — any transfer opportunities?

Friday:
  [ ] Confirm reorder status for any Critical alerts from Monday
  [ ] Update distributor on transfer suggestions if raised
```

---

### Distributor (Weekly Upload Cycle)

```
Every Week (Friday recommended):
  [ ] Count secondary sales for the week (by SKU and size)
  [ ] Fill SMRITI Upload Template (Excel)
  [ ] Upload via PSV portal or email to brand coordinator
  [ ] Time required: 20 minutes

Monthly:
  [ ] Physical stock count
  [ ] Upload opening balance correction if needed
  [ ] Attend 30-minute brand review (if scheduled)
```

**Upload Template**: Available from SMRITI PSV Settings → Download Template

---

### Store Manager / Operations (Exception Response)

```
When WOC Critical alert received:
  1. Verify physical stock count
  2. Confirm weekly velocity is accurate
  3. Initiate reorder OR request network transfer
  4. Log action in Exception Log

When Dead Stock alert received:
  1. Verify item has not been recently moved
  2. Identify recovery option: transfer / markdown / return
  3. Raise transfer note or return request
  4. Update PSV with action taken

When Variance Flag received:
  1. Compare physical count to PSV ledger
  2. Identify discrepancy source (upload error / unrecorded sales)
  3. Correct upload or raise reconciliation request
```

---

## Chapter 6 — Alert Types

| Alert | Trigger | Urgency | Recommended Response |
|-------|---------|---------|---------------------|
| WOC Critical | WOC < 2 weeks | 🔴 Immediate | Reorder or transfer within 5 days |
| WOC Warning | WOC < 4 weeks | 🟡 Plan Now | Schedule reorder this week |
| Dead Stock | 60+ days no movement | 🟠 This Month | Transfer, markdown, or return |
| Excess Stock | WOC > 12 weeks | 🟢 Monitor | Consider transfer to understocked location |
| Variance Flag | Physical ≠ Ledger > 5% | 🟡 Verify | Physical count + upload correction |
| Upload Overdue | No upload for 10+ days | 🟠 Chase | Contact distributor for data |

> All thresholds are configurable per brand in SMRITI PSV Settings.

---

## Chapter 7 — Exception Handling (Real Scenarios)

### Scenario 1 — Stockout Prevention

> Ajay's Pune hub has 72 pcs of Size 8. Weekly velocity: 40 pcs.
> WOC = 1.8 weeks. PSV flags Critical.
> Reorder placed Wednesday. Stock received Monday.
> Stockout avoided by 3 days.

**Lesson**: WOC Critical alert gives 8–14 days of action window for standard reorder cycles.

---

### Scenario 2 — Dead Stock Recovery

> Meera's Nagpur hub has 820 pcs of Summer Slim Fit — 97 days inactive.
> Capital locked: ₹4,10,000. PSV flags Dead Stock.
> 400 pcs transferred west. 420 pcs returned.
> ₹4.1L recovered in 2 weeks.

**Lesson**: Dead stock surfaced at 60 days allows recovery. At 180 days, options narrow.

---

### Scenario 3 — Network Balancing

> Rajan's Mumbai hub has 120 pcs Size 32 Denim (WOC 18 weeks).
> Pune hub: 0 pcs, stockout active. Same SKU.
> PSV flags transfer opportunity. 80 pcs moved in 2 days.
> Fresh PO avoided. ₹40,000 margin protected.

**Lesson**: Network view prevents same-brand, cross-location waste.

---

## Chapter 8 — Pilot Success Criteria

During the 30-day pilot, success is measured against six criteria agreed on Day 1.

| # | Criterion | Target | How Measured |
|---|-----------|--------|-------------|
| 1 | Stockout Prevention | ≥ 1 event prevented | Exception log |
| 2 | Excess Stock ID | ≥ 1 SKU flagged | WOC report |
| 3 | Dead Stock ID | Any ₹ value surfaced | Aging report |
| 4 | Network Balancing | ≥ 1 transfer opportunity | Network view |
| 5 | WOC Adoption | ≥ 1 WOC-driven decision | Self-reported |
| 6 | Dashboard Engagement | ≥ 12 sessions / 30 days | Activity log |

**Pass**: ≥ 4 of 6 → Rollout conversation
**Partial**: 2–3 of 6 → Targeted re-pilot
**Fail**: ≤ 1 of 6 → Root cause review

Full criteria detail: [COMM-08 Pilot Success Criteria](../05-developer/comm_08_pilot_success_criteria.md)

---

## Chapter 9 — Frequently Asked Questions

**Q: Does PSV require the distributor to change their existing system?**
> No. Distributors use the SMRITI Excel upload template. No software installation required.

**Q: Does the brand see the distributor's pricing or customer details?**
> No. PSV shows Sell-Through %, stock levels, and aging data only. Pricing and customer data are never captured.

**Q: How often does the distributor need to upload data?**
> Weekly. The upload takes approximately 20 minutes per week.

**Q: What if the distributor misses an upload?**
> PSV flags an "Upload Overdue" alert after 10 days. The brand coordinator follows up.

**Q: Can PSV connect directly to our ERP?**
> At pilot stage: Excel upload. Post-pilot: API integration is available for brands on ERPNext.

**Q: Does PSV modify our stock ledger or accounting?**
> Never. PSV maintains a separate shadow ledger. It does not touch ERPNext Stock Ledger Entries or General Ledger.

**Q: What happens to our data after the pilot ends?**
> Data remains in your SMRITI instance. No data is shared with third parties.

**Q: Can we configure the alert thresholds?**
> Yes. WOC Critical/Warning thresholds, Dead Stock days, and Variance % are all configurable in SMRITI PSV Settings.

---

## Chapter 10 — Troubleshooting

| Issue | Likely Cause | Action |
|-------|-------------|--------|
| Sell-Through % shows 0% | No secondary sales uploaded yet | Request distributor upload |
| WOC shows very high number | Opening balance not set correctly | Correct opening balance upload |
| Dead stock flag on active item | Upload missed for 60+ days | Upload last 8 weeks of sales |
| Variance flag on correct stock | Upload format error (qty column) | Re-upload with correct template |
| Dashboard shows no data | First upload not processed yet | Allow 24 hours after first upload |
| Alert not visible in Exception Log | Threshold not configured | Check PSV Settings → Alert Thresholds |

**Support**: SMRITI Helpdesk — support@aitdl.com

---

## Revision History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-24 | Initial release — PSV v1.1 |

---

*Author: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*"Always decision-ready."*