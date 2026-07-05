---
Document ID: "ARCH-015"
Title: "SMRITI Formula Registry (DOC-02)"
Owner: "Architecture Team"
Audience: "Architect"
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

# SMRITI Formula Registry (DOC-02)

The **Formula Registry** is a central governance ledger in SMRITI Retail OS. It registers every mathematical, financial, and forecasting formula used across the platform (such as Weeks of Cover, Sales Velocity, or Transfer Benefit). This prevents "black-box" computations and ensures that formulas are audited, versioned, and documented.

---

## 📋 Schema Definition (`SMRITI Formula Definition`)

The Formula Registry is backed by the `SMRITI Formula Definition` DocType. Each record contains:

*   **Formula ID**: Unique code (e.g. `INV-002`).
*   **Formula Name**: Human-readable name (e.g. "Weeks of Cover").
*   **Formula Category**: Category tag (e.g. `Inventory`, `Forecasting`, `Sales`).
*   **Formula Expression**: String showing the raw mathematical expression (e.g. `current_stock / weekly_velocity`).
*   **Formula Language**: The documentation syntax (e.g., `documentation`).
*   **Business Meaning**: Clear business description for store managers.
*   **Worked Example**: Arithmetic step-by-step walkthrough using real numbers.
*   **Interpretation Guide**: Reference bands (Critical, Monitor, Healthy).
*   **Recommended Action**: Next steps for a store operator when the metric reaches certain bands.
*   **Implementation Reference**: Code file and function where the formula is executed (e.g. `services/forecasting_service.py::calculate_weeks_of_cover`).
*   **Business Owner**: The corporate owner accountable for the formula logic.

---

## ⚡ Caching & Auditing

*   **Redis Caching**: When a formula is loaded by the front-end or service layer, it is cached in Redis at key `smriti:explain:{formula_id}:{version}` with a **TTL of 3600 seconds** (1 hour). Subsequent requests load from cache to ensure sub-second response times.
*   **Access Auditing**: Every fetch of a formula (cache hit or miss) is audited. The system automatically creates a `SMRITI PSV Activity Log` entry with:
    *   `action_type` = `"Formula Explained"`
    *   `event_type` = `"FORMULA_EXPLAINED"`
    *   `reference_name` = `{formula_id}`
    *   `details` = `Version: {version}`

---

## 🧮 Core Registered Formulas

The registry seeds the following 10 core formulas by default:

| Formula ID | Name | Category | Expression | Code Reference |
| :--- | :--- | :--- | :--- | :--- |
| **INV-001** | Sales Velocity | Inventory | `total_sales_qty / lookback_weeks` | `dictionary_service.py` |
| **INV-002** | Weeks of Cover | Inventory | `current_stock / weekly_velocity` | `explain_service.py` |
| **INV-003** | Dead Stock Score | Inventory | `inactive_days * stock_value` | `dictionary_service.py` |
| **INV-004** | Inventory Turnover | Inventory | `cogs / average_inventory_value` | `dictionary_service.py` |
| **FRC-001** | Forecast Confidence | Forecasting | `1.0 - (std_dev / mean)` | `dictionary_service.py` |
| **TRF-001** | Transfer Benefit Score | Distribution | `margin_gain - freight_cost` | `dictionary_service.py` |
| **SAL-001** | Sell Through % | Sales | `sold_qty / dispatched_qty` | `dictionary_service.py` |
| **AUD-001** | Stock Accuracy % | Audit | `1.0 - (abs_variance / ledger_stock)` | `dictionary_service.py` |
| **OHS-001** | Outlet Health Score | Outlet | `0.6 * sync_score + 0.4 * audit_score` | `dictionary_service.py` |
| **VAR-001** | Size Curve Health | Inventory | `overlap_coefficient(stock, sales)` | `dictionary_service.py` |
| **TST-OCI** | Outlet Conversion Index | Outlet | `(billed_walkins / total_walkins) * 100` | `clienteling_service.py` |
| **TST-EPI** | Executive Performance Index | Sales | `(attributed_sales_qty / total_outlet_sales_qty) * 100` | `clienteling_service.py` |
| **TST-SRI** | Store Retention Index | Outlet | `(repeat_customers / total_customers) * 100` | `clienteling_service.py` |
| **TST-HEALTH** | Customer Health Score | Clienteling | `(100 - churn) * 0.4 + vip * 0.4 + affinity * 0.2` | `clienteling_service.py` |

---

### SAL-001 Variable Definitions

| Variable | PSV Definition |
|----------|---------------|
| `sold_qty` | Secondary sales quantity — units sold by distributor to retail outlets in the measurement period |
| `dispatched_qty` | Primary sales quantity — stock dispatched from brand/warehouse to distributor in the measurement period. **Not** opening stock balance (which may include carry-forward from prior periods) |

> **Why `dispatched_qty` not `opening_stock_qty`?**
> In PSV context, the denominator is always "what the brand sent to the distributor" for a specific period.
> `opening_stock_qty` is general inventory terminology and includes carry-forward stock from prior periods,
> which would understate the Sell-Through % for new deliveries.
> `dispatched_qty` = `opening_stock_qty` only when the distributor had zero carry-forward inventory.
>
> **Code reference**: `psv_sell_through.py` — `round((r.sold / r.dispatched) * 100, 2) if r.dispatched else 0`
> **Founder approved**: Jawahar R. Mallah, AITDL — 2026-06-24

---

## 🔬 Detailed Formula Specifications (DOC-01 / DOC-02)

Below are the audited mathematical, execution, and action details for the newly registered Clienteling and Outlet Intelligence formulas.

### 1. Outlet Conversion Index (`TST-OCI`)
*   **Business Meaning**: Measures the efficiency of turning store foot traffic (walk-ins) into purchasing customers.
*   **Formula Expression**:
    $$\text{Outlet Conversion Index} = \left(\frac{\text{billed\_walkins}}{\text{total\_walkins}}\right) \times 100$$
*   **Worked Example**:
    - Billed Walk-ins = 40 customers.
    - Total Walk-ins = 200 visitors.
    - $\text{Outlet Conversion Index} = \left(\frac{40}{200}\right) \times 100 = 20.0\%$.
*   **Data Sources**: `tabSMRITI Walk In Analytics`, `tabSales Invoice`.
*   **Interpretation Guide**:
    - `< 15.0%`: **Critical** (Inefficient sales pitch, sizing stockouts, or poor layout).
    - `15.0% - 25.0%`: **Monitor** (Average performance, needs refinement).
    - `> 25.0%`: **Healthy** (High floor efficiency, good customer interaction).
*   **Recommended Action**: For critical scores, verify if popular item variants/sizes are out-of-stock. If stock is healthy, schedule sales floor training.

### 2. Executive Performance Index (`TST-EPI`)
*   **Business Meaning**: Evaluates an executive's individual conversion contribution relative to the outlet's total sales volume.
*   **Formula Expression**:
    $$\text{Executive Performance Index} = \left(\frac{\text{attributed\_sales\_qty}}{\text{total\_outlet\_sales\_qty}}\right) \times 100$$
*   **Worked Example**:
    - Executive's Attributed Sales Qty = 30 items.
    - Outlet's Total Sales Qty = 150 items.
    - $\text{Executive Performance Index} = \left(\frac{30}{150}\right) \times 100 = 20.0\%$.
*   **Data Sources**: `tabSales Invoice Item`, `tabSMRITI Sales Partner Split`.
*   **Interpretation Guide**:
    - `< 10.0%`: **Critical** (Underperforming relative to floor average).
    - `10.0% - 20.0%`: **Monitor** (Standard contribution).
    - `> 20.0%`: **Healthy** (High sales driver, eligible for performance bonuses).
*   **Recommended Action**: Pair executives in the critical range with high-performing mentors. Review target payout adjustments.

### 3. Store Retention Index (`TST-SRI`)
*   **Business Meaning**: Measures customer loyalty and repeat checkout frequency at a specific outlet.
*   **Formula Expression**:
    $$\text{Store Retention Index} = \left(\frac{\text{repeat\_customers}}{\text{total\_customers}}\right) \times 100$$
*   **Worked Example**:
    - Repeat Customers (>= 2 visits in lookback) = 60.
    - Total Unique Customers = 200.
    - $\text{Store Retention Index} = \left(\frac{60}{200}\right) \times 100 = 30.0\%$.
*   **Data Sources**: `tabSMRITI Customer Intelligence Graph`, `tabSales Invoice`.
*   **Interpretation Guide**:
    - `< 15.0%`: **Critical** (High churn rate, customers are not returning).
    - `15.0% - 30.0%`: **Monitor** (Standard brand retention).
    - `> 30.0%`: **Healthy** (Excellent brand affinity and customer connection).
*   **Recommended Action**: Trigger SMS winback campaign to dormant customers or offer loyalty vouchers for next purchases.

### 4. Customer Health Score (`TST-HEALTH`)
*   **Business Meaning**: A composite score detailing the customer's overall engagement, value contribution, and retention probability.
*   **Formula Expression**:
    $$\text{Customer Health Score} = \max\left(0.0, \min\left(100.0, (100 - \text{churn\_risk\_score}) \times 0.4 + \text{vip\_candidate\_score} \times 0.4 + \text{campaign\_affinity\_score} \times 0.2\right)\right)$$
*   **Worked Example**:
    - Churn Risk Score = 20.
    - VIP Candidate Score = 70.
    - Campaign Affinity Score = 60.
    - $\text{Health} = (100 - 20) \times 0.4 + 70 \times 0.4 + 60 \times 0.2 = 80 \times 0.4 + 28 + 12 = 32 + 28 + 12 = 72.0\%$.
*   **Data Sources**: `tabSMRITI Customer Intelligence Graph`, `tabSMRITI Customer Profile`.
*   **Interpretation Guide**:
    - `< 40.0%`: **Critical** (High churn risk or extremely low engagement. Needs immediate winback touchpoint).
    - `40.0% - 75.0%`: **Monitor** (Standard customer engagement).
    - `> 75.0%`: **Healthy** (Highly active VIP, prioritize premium customer service).
*   **Recommended Action**: Used by counter salesmen in Clienteling Studio. Offer immediate special discounts to Healthy score customers. File winback tasks for Critical scores.

---

## Support & Helpdesk
For questions or support, please contact the SMRITI Helpdesk at **support@aitdl.com**.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |