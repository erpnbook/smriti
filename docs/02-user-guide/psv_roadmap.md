---
Document ID: "USER-018"
Title: "SMRITI Retail OS — PSV Phase 1.3 Candidate Roadmap"
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

# SMRITI Retail OS — PSV Phase 1.3 Candidate Roadmap

Following UAT verification and pilot feedback, the PSV roadmap has been refined to enforce a strict boundary between the **Intelligence Layer** (Wave 1/2) and the **Automation Layer** (Wave 3). This prevents operational disruption and cash flow risks before the analytical models are fully trusted.

---

## 🗺️ Governance & Decision Gates

### 📋 Phase 1.3 Activation Criteria
Phase 1.3 development may begin only after all of the following are met:
* [ ] **PSV Pilot** completed
* [ ] **Pilot feedback** reviewed
* [ ] **Usage analytics** collected
* [ ] **Phase 1.2** stable in production
* [ ] **Governance approval** recorded

Until then:
* **STATUS** = `CANDIDATE`

---

* **Pilot Loop Requirement**: No candidate feature in Phase 1.3 or 1.4 shall be promoted to active development without at least one completed Pilot Distributor review cycle.
* **Vertical Isolation Principle**: Vertical-specific features (e.g. Footwear Vertical Module) must remain decoupled as optional modules.
  * **PSV Phase 1.3A-P1A Conditional Feature**: Activates only if `Footwear Vertical Mode` is explicitly enabled in SMRITI Company Settings or PSV System Settings. No-op on other configurations.

---

## 📈 Phase 1.3A — Intelligence Layer (Wave 1)
These extend existing PSV analytics without changing operational workflows or automating transactions.

### 1. Capital Locked Analysis
* **Goal**: Enable distributors to see where working capital is stagnating.
* **Valuation Rules**:
  * Avoid raw `Item.valuation_rate` directly.
  * Prefer `Last Purchase Cost`, `ERPNext valuation rate`, or `Landed Cost Voucher adjusted rate` (based on availability) to ensure accurate capital estimate.
* **Categorization Buckets** (for visual reconciliation):
  * **Healthy Stock**: Active items with optimal coverage.
  * **Slow Mover Capital**: Active items with low velocity.
  * **Dead Stock Capital**: Zero sales velocity in last 90+ days.
  * **Excess Inventory Capital**: Stock exceeding target coverage days.
* **Deliverables**:
  * Locked Capital Dashboard Widget
  * Allocation and working capital impact charts.
* **Priority**: Critical

### 2. Coverage Days Intelligence
* **Goal**: High-precision daily coverage forecasting.
* **Formula**:
  $$\text{Coverage Days} = \frac{\text{Current Stock Balance}}{\text{Daily Velocity}}$$
* **Velocity Edge Cases**:
  * If $\text{Daily Velocity} = 0$, return `∞ Coverage` or `No Sales History` (avoiding `ZeroDivisionError`).
* **Deliverables**:
  * Daily velocity calculation
  * Coverage-day forecasting
  * Stockout and overstock warning alerts (thresholds at <7 days and >45 days).
* **Priority**: Critical

### 3. Inventory Aging Intelligence
* **Goal**: Complete the inventory health picture using shadow ledger history.
* **Aging Buckets**:
  * `0-30 days`
  * `31-60 days`
  * `61-90 days`
  * `91-180 days`
  * `180+ days` (Older than 6 months is key for distributors)
* **Intelligence mapping**: Age vs. Margin (e.g. Old+Profitable, Old+Unprofitable).
* **Priority**: Critical

---

## 🔍 Phase 1.3B — Recovery Intelligence (Wave 2)
Generates non-automated recommendations to help users resolve inventory bottlenecks.

### Dead Stock Recovery Intelligence
* **Architecture Rules**:
  * Implemented in a dedicated `psv_recovery_service.py` to keep analysis separate from the recommendation engine.
  * **Recommendation Only**: Recommendation outputs only (`recommendation: true`), never auto-executed (`auto_execute: false`). Keep humans in control.
* **Deliverables**:
  * Redistribution suggestions (e.g., Transfer to Branch B)
  * Bundling recommendations (e.g., Bundle slow item with fast item)
  * Promotion suggestions (e.g., Run clearance offer)
  * Order reduction recommendations
* **Priority**: High

---

## 📊 Phase 1.3C — Pilot Intelligence (Wave 2)
Focuses on telemetry and feedback ingestion during the pilot phase to guide design choices.

### 1. Usage Analytics (Performance Guarded)
* **Goal**: Track user interactions to identify dashboard utility without performance degradation.
* **Performance Rule**: Use a "fire-and-forget" pattern via `frappe.enqueue(...)` for all telemetry logging; never block with synchronous database `insert`/`commit`/`wait`.
* **Deliverables**:
  * Widget interaction tracking (opens/collapses)
  * Modal view counts
  * Excel/CSV export usage metrics
* **Priority**: Medium

### 2. Pilot Feedback Tracking
* **Goal**: Centralize feedback to serve as the gateway for Phase 1.4.
* **Deliverables**:
  * Distributor feedback registry
  * Feature request logging
  * Adoption & satisfaction score tracking
* **Priority**: Medium

---

## ⚙️ Phase 1.4 — Automation Layer (Wave 3)
Operational automation features. Scheduled only after successful validation of Phase 1.3 pilots.

### 1. Reorder Engine
* **Rule**: Requires validated pilot data to avoid dangerous over-ordering.
* **Requirements**: Lead time, MOQ, supplier behavior, seasonality, safety stock.
* **Priority**: Later (Deferred)

### 2. Purchase Suggestions
* **Rule**: Requires approval workflows and audit trails due to direct cash flow impact.
* **Workflow**: Auto-create **Draft Purchase Orders** in ERPNext (never auto-submit).
* **Priority**: Later (Deferred)

---

## 🔮 Phase 2 — Forecasting Layer (Future)
Future enhancements scheduled after successful Phase 1.3/1.4 deployment.

### Demand Forecasting
* **Architecture Module**: `psv_forecasting_service.py`
* **Goal**: Combine Coverage Days, Daily Velocity, and Seasonality indices to generate high-fidelity demand forecasting.
* **Priority**: Future

---

## 🏷️ Final Governance & Priority Status

```text
PSV Core Engine          ✅ Frozen
PSV Analytics Engine     ✅ Active
PSV Pilot                🟡 Active

Phase 1.3A Intelligence  🔵 Candidate
Phase 1.3B Recovery      🔵 Candidate
Phase 1.3C Telemetry     🔵 Candidate

Phase 1.4 Automation     ⚪ Future
Phase 2 Forecasting      ⚪ Future
```

| Wave | Phase | Feature / Deliverable | Priority |
|---|---|---|---|
| **Wave 1** | Phase 1.3A | Capital Locked Analysis (with Healthy Stock) | Critical |
| **Wave 1** | Phase 1.3A | Coverage Days Intelligence (with Velocity Edge Cases) | Critical |
| **Wave 1** | Phase 1.3A | Inventory Aging Intelligence (up to 180+ days) | Critical |
| **Wave 2** | Phase 1.3B | Dead Stock Recovery (Recommendations via psv_recovery_service.py) | High |
| **Wave 2** | Phase 1.3C | Usage Analytics (Asynchronous via frappe.enqueue) | Medium |
| **Wave 2** | Phase 1.3C | Pilot Feedback Tracking (Gate to 1.4) | Medium |
| **Wave 3** | Phase 1.4 | Reorder Engine (MOQ, Safety Stock) | Later |
| **Wave 3** | Phase 1.4 | Purchase Suggestions (Draft POs in ERPNext) | Later |
| **Future** | Phase 2 | Demand Forecasting (psv_forecasting_service.py) | Future |


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL