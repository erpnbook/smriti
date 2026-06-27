# PDT — Product Digital Twin
## Architecture, Assumptions & Design Boundaries

> **Document ID**: DEV-072
> **Module**: PDT (Product Digital Twin)
> **Category**: Developer Architecture Reference
> **Status**: LOCKED — v1.8.5
> **Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Date**: 2026-06-25

---

## 1. What is PDT?

The **Product Digital Twin (PDT)** is SMRITI's per-SKU analytics engine. For each item at each Party Stock Account (PSA/distributor location), PDT calculates a live digital twin containing:

- Inventory position and health state
- Demand forecast (EMA-based weekly velocity)
- Weeks of Cover (WOC)
- Dead Stock probability score
- Network transfer recommendation (single-source optimization)
- Variant curve health (missing sizes)
- Data quality score

PDT twins are stored in `SMRITI SKU Twin` DocType and cached in Redis. They are rebuilt asynchronously via Frappe's `long` queue on inventory events.

---

## 2. Explicit Design Assumptions

Every forecasting engine has assumptions. These are PDT v1's documented assumptions.

| Assumption | Detail |
|---|---|
| **Sales history granularity** | Daily sales from `SMRITI Party Stock Ledger Entry` |
| **Forecasting model** | Exponential Moving Average (EMA) |
| **Missing days** | Zero-demand days included in the lookback window (not excluded) |
| **Transfer optimization** | Single-source greedy (see §5) |
| **SKU independence** | Each SKU forecasted independently — no correlation across variants or styles |
| **Seasonality model** | None in v1 (`seasonality_factor` field reserved, hardcoded to `1.0`) |
| **Promotion uplift** | Not modeled — promotional spikes are absorbed into EMA history |
| **Explainability** | Preferred over opaque ML — all formulas are registered, documented, and ⓘ-explained |
| **Inventory source** | PSV shadow ledger only (`SMRITI Party Stock Ledger Entry`) — not ERPNext Stock Ledger |

---

## 3. Configurable Parameters

All tunable parameters are read from **`SMRITI PSV Settings`**. Hardcoded defaults are used only as safe fallbacks.

| Parameter | Settings Field | Default | Valid Range | Effect |
|---|---|---|---|---|
| Lookback window | `reorder_avg_weeks` | 4 weeks | 1–26 | Longer = smoother, less reactive |
| EMA alpha | `ema_alpha` | 0.3 | 0.05–0.95 | Higher = more weight to recent sales |
| Safety stock | `default_safety_stock` | 0.0 | ≥ 0 | Buffer before excess stock calculation |
| Variant dimension | `variant_dimension` | `"Size"` | Any ERPNext attribute name | Drives variant curve label extraction |

### EMA Alpha Guide

```
alpha = 0.1–0.2  →  Slow-responding. Best for stable, predictable demand (staples, basics).
alpha = 0.3      →  Balanced. Recommended default for standard retail SKUs.
alpha = 0.5–0.7  →  Fast-responding. Better for seasonal or highly volatile SKUs.
alpha = 0.8–0.95 →  Very reactive. Only for extremely short-cycle or fashion SKUs.
```

---

## 4. Forecasting Engine — EMA

### Formula

```
EMA[t] = alpha × Sales[t] + (1 - alpha) × EMA[t-1]
Weekly Velocity = EMA[final_day] × 7
```

### Confidence Calculation

```
CV (Coefficient of Variation) = StdDev / Mean
Confidence = 100% × e^(-0.5 × CV)

CV ≈ 0.1 → Confidence ≈ 95%  (very stable demand)
CV ≈ 1.0 → Confidence ≈ 61%  (moderate volatility)
CV ≈ 2.0 → Confidence ≈ 37%  (high volatility)
```

When mean sales = 0 and all daily values are zero: Confidence = 100% (certain forecast of zero demand).

### Worked Example

```
Item: NIKE-AIR-UK8, PSA: Mumbai Distributor
Lookback: 28 days, alpha: 0.3

Week 1: [2, 0, 3, 0, 1, 2, 0] → avg 1.14/day
Week 2: [1, 3, 0, 2, 0, 1, 3] → avg 1.43/day
Week 3: [0, 2, 1, 0, 2, 0, 1] → avg 0.86/day
Week 4: [3, 1, 2, 1, 0, 2, 1] → avg 1.43/day

EMA final ≈ 1.27/day
Weekly Velocity = 1.27 × 7 = 8.9 units/week

Mean = 1.21, StdDev = 0.94, CV = 0.78
Confidence = 100 × e^(-0.5 × 0.78) = 67.8%
```

---

## 5. Transfer Optimization Engine — Single-Source Greedy

### Optimization Problem Solved (v1)

> **"Find the best individual source for a given transfer need."**

This is a **single-source optimization** — not a multi-source network optimization. The algorithm selects the single PSA with the highest economic benefit score among all candidates with excess stock.

This is an intentional v1 design boundary, not a defect.

### Algorithm

```python
for each candidate PSA with excess_qty > 0:
    transfer_qty = min(needed_qty, excess_qty)
    unit_benefit = item_rate - freight_cost - delay_penalty
    benefit_score = unit_benefit × transfer_qty
    track best_score, best_source

if best_score > 0:
    recommend transfer from best_source
else:
    recommend new procurement
```

### Zone Freight Costs

| Route | Freight (₹/unit) | Delay Penalty (₹/unit) |
|---|---|---|
| Same zone | ₹6.00 | ₹5.00 |
| Different zone | ₹18.00 | ₹20.00 |

### What v1 Does NOT Solve

- Combining stock from multiple sources (partial fills)
- Route optimization across 3+ hops
- Minimizing total network freight cost simultaneously
- Demand-matched replenishment timing

**PDT v2 Roadmap**: Multi-source network flow optimization using linear programming.

---

## 6. Dead Stock Score Formula

```
Dead Stock Score =
    (no_sale_days × 0.4)       # 40% weight — recency of last sale
  + (aging_days × 0.3)         # 30% weight — age of inventory
  + max(0, 30 - sales_qty_28d) # Turnover score
  + (weeks_of_cover × 2.0)     # Cover penalty

Score range: 0–100 (clamped)

Interpretation:
  > 75 → High dead stock probability
  45–75 → Medium
  < 45 → Low
```

---

## 7. Twin State Machine

```
Stock = 0             → Stockout
Dead Stock = High     → Dead Stock
WOC > 12 weeks        → Overstock
WOC < 2 weeks         → Critical
WOC < 4 weeks         → Replenish Soon
WOC < 6 weeks         → Monitor
Otherwise             → Healthy
```

---

## 8. Variant Curve Logic

A variant curve is **Broken** when:
1. The item is part of a template (has siblings variants)
2. Total style stock across all variants > 0 (style is alive)
3. One or more sibling variants have zero balance

The **variant dimension** used for label extraction is configured via `SMRITI PSV Settings > variant_dimension` (default: `"Size"`). This makes the algorithm reusable across categories:

```
Footwear / Garments → variant_dimension = "Size"
Furniture           → variant_dimension = "Dimension"
Electronics         → variant_dimension = "Storage"
Colour variants     → variant_dimension = "Colour"
```

---

## 9. Known Limitations & V2 Roadmap

| Limitation | Severity | V2 Plan |
|---|---|---|
| No seasonality model | Low — retail baseline adequate | Seasonal index multiplier on EMA |
| No promotion uplift | Low — absorbed into EMA history | Promotion-period exclusion flag |
| Single-source transfer | Medium — sufficient for v1 | Multi-source LP optimization |
| Independent SKU forecast | Medium | Variant-correlated demand model |
| Fixed zone freight costs | Low | Configurable freight matrix per zone pair |
| EMA only (no ARIMA/ML) | Low — explainability preferred | Optional ML adapter with explain wrapper |

---

## 10. Error Handling & Infrastructure Policy

| Code Path | Exception Policy | Rationale |
|---|---|---|
| Settings read failure | `frappe.log_error()` + use defaults | Settings failure is operational |
| Business logic failure (rebuild) | `frappe.log_error()` — full | Business failure must surface |
| Redis cache write failure | `frappe.log_error()` — logged | Cache miss degrades gracefully |
| Redis lock release (finally) | `logger.debug()` only | Cleanup path; lock expires via TTL |

---

## 11. Author

**Jawahar R. Mallah**
Founder & Chief Architect, AITDL – AI Technology & Development Lab

> *"Always decision-ready."*
