---
Document ID: "SMRITI-CERT-001"
Title: "PSV Certified Planner Guide"
Owner: "Training Team"
Audience: "Support Engineer"
Module: "PSV"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI PSV Certified Planner Guide (Level 1)
## SMRITI Inventory Visibility Certified Planner Program

---

### Author Profile (Start)
- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL ÔÇô AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.
- **Author Note**: This guide is based on practical field experience gathered across retail operations, distribution management, inventory control, software architecture, business automation, and enterprise solution development. The objective is to make SMRITI Retail OS understandable and usable by both technical and non-technical users.
#### Document Metadata
- **Certification Version**: 1.0.0
- **Release Date**: 2026-06-23
- **Intended Audience**: Inventory Planners, Brand Managers, Store Managers, and Distributors.
- **Learning Objectives**:
  1. Understand the causes and costs of the Distribution Visibility Gap.
  2. Master Weeks of Cover (WOC) alert zones and calculations.
  3. Calculate Sell-Through % and use it to allocate styles.
  4. Design dynamic Reorder rules using Lead Time and Safety Stock parameters.
  5. Balance network stock via inter-store transfers.
  6. Solve data synchronization exceptions.
  7. Optimize working capital locked in dead stock.
- **Support Contact**: support@aitdl.example.com
- **Revision History**:
  - `v1.0.0` (2026-06-23) - Initial Release by Jawahar R. Mallah.

---

## Chapter 1: Understanding the Distribution Visibility Gap

### 1. The Lost Visibility Problem
Traditional supply chains operate on a blind channel model:
1. The brand dispatches stock to a distributor warehouse.
2. The brand registers this as a sale (Primary Sale) and assumes the inventory is moving.
3. The brand has no visibility into what happens next. The inventory could sit in the distributor's depot or be sold to retail shops.
4. The brand is blind to the actual consumer checkout rate (Secondary Sale).

This creates the **Distribution Visibility Gap**:
*   **The Stockout Trap**: High-velocity sizes (e.g. Size 8 footwear) sell out in the first week. The brand does not know, so no replenishment is scheduled. Sales are permanently lost.
*   **The Dead Stock Trap**: Low-velocity sizes (e.g. Size 11) sit stagnant. The distributor's capital is locked, and they demand returns or markdown discounts.
*   **guesswork Reorders**: Distributors place reorders based on gut feeling, compounding excess inventory of non-moving items.

### 2. SMRITI Inventory Visibility Layer Solution
SMRITI bridges this gap by establishing a real-time **Inventory Visibility Network**. It reads ERPNext primary transaction records but aggregates distributor inventories (Party Stock Accounts) using isolated secondary sales uploads.

This ensures:
*   Real-time visibility of stock at every node.
*   Complete separation of brand accounting from distributor logs.
*   Automated alerts for stockouts, aging, and discrepancies.

---

## Chapter 2: Understanding Weeks of Cover (WOC)

### 1. What is WOC?
**Weeks of Cover (WOC)** is the primary metric used by planners to measure inventory health. It indicates how many weeks the current channel inventory will last based on the recent sales velocity.

#### Formula (PSV-WOC-001):
$$\text{WOC} = \frac{\text{Current Stock (Channel Balance)}}{\text{Weekly Sales Velocity}}$$

Where:
$$\text{Weekly Sales Velocity} = \text{Average Daily Sales over lookback window} \times 7$$

### 2. Worked Example
If a distributor has **300 units** of a variant, and the daily sales average over the last 30 days is **5 units/day**:
$$\text{Weekly Sales Velocity} = 5 \times 7 = 35 \text{ units/week}$$
$$\text{WOC} = \frac{300}{35} = 8.57 \text{ Weeks of Cover}$$

### 3. Inventory Action Zones
Planners must manage inventory according to these defined safety thresholds:

| Zone | WOC Range | Meaning | Required Action |
| :--- | :---: | :--- | :--- |
| **Green Zone** | 7 ÔÇô 14 Weeks | **Healthy**: Stock level is optimized. | Maintain normal supply. No expedited action. |
| **Watch Zone** | 3 ÔÇô 7 Weeks | **Warning**: Stock is depletion-prone. | Queue next shipment; check transit times. |
| **Action Zone** | < 3 Weeks | **Critical**: High stockout threat. | Place immediate replenishment order or trigger transfer. |

*Note: In live production sites, these thresholds can be configured dynamically in SMRITI PSV Settings to match brand-specific buffers.*

---

## Chapter 3: Understanding Sell-Through %

### 1. Sell-Through Metrics
**Sell-Through %** measures the efficiency of inventory movement from the distributor to the consumer. It indicates what percentage of dispatched stock has actually been sold.

#### Formula (PSV-ST-001):
$$\text{Sell-Through \%} = \left( \frac{\text{Quantity Sold (Secondary)}}{\text{Quantity Dispatched (Primary)}} \right) \times 100$$

### 2. Worked Example
A brand ships 1,500 units of standard denim to a partner. The partner reports sales uploads totaling 900 units:
$$\text{Sell-Through \%} = \left( \frac{900}{1,500} \right) \times 100 = 60.0\%$$

### 3. Allocation Strategy
Planners evaluate Sell-Through rates to redirect inventory:
*   **ST > 70%**: High velocity. Allocate additional manufacturing budgets.
*   **ST 40% - 70%**: Stable. Maintain current replenishment curves.
*   **ST < 30%**: Low velocity. Freeze further dispatches; initiate promotional schemes or transfers.

---

## Chapter 4: Reorder Planning

### 1. Reorder Mechanics
Planners compute the **Reorder Point (ROP)** to automate replenishment suggestions without causing stockouts.

#### Key Variables:
1.  **Lead Time**: Days from placing an order to stock receipt.
2.  **Safety Stock**: Minimum buffer units kept to safeguard against sales spikes or transport delays.
3.  **Average Daily Sales (ADS)**: Weekly velocity divided by 7.

#### Formula:
$$\text{Reorder Point (ROP)} = (\text{ADS} \times \text{Lead Time}) + \text{Safety Stock}$$

### 2. Worked Scenario
*   Lead Time = 8 days
*   Average Daily Sales = 15 units
*   Safety Stock = 80 units
$$\text{ROP} = (15 \times 8) + 80 = 120 + 80 = 200 \text{ units}$$
When the distributor's stock drops below 200 units, the SMRITI PSV engine flags a replenishment suggestion.

---

## Chapter 5: Stock Transfer Decisions

### 1. Inter-Store Inventory Balancing
Shipping new inventory from the central factory is slow and expensive. SMRITI recommends moving stock from overstocked locations to short-supply depots.

### 2. Worked Scenario
*   ** Óñ«ÓÑüÓñéÓñ¼Óñê Depot**: Holds 250 excess units of sneaker Style-A (WOC = 30 weeks).
*   **Óñ¬ÓÑüÓñúÓÑç Depot**: Reports 0 units in stock (WOC = 0 weeks) with a customer demand of 20 units/week.
*   **Requisition**: SMRITI suggests a Network Stock Transfer (NST) of 120 units from Mumbai to Pune.
*   **Outcome**: Pune receives stock within 2 days (avoiding stockouts), Mumbai clears excess capital lockup, and overall margin is protected.

---

## Chapter 6: Exception Handling

Certified planners must monitor and resolve data exceptions in the SMRITI Exception Center:

1.  **Negative Inventory**: Caused by uploading secondary sales records before the brand's primary dispatch invoices are imported.
    *   *Fix*: Upload missing dispatch invoices.
2.  **Return Serial Mismatch**: Caused by manual scan errors during distributor returns.
    *   *Fix*: Cross-reference returns against original dispatch packing lists.
3.  **Late Upload Latency**: Mapped via the Outlet Health Score. If latency exceeds 3 days, velocity forecasts become inaccurate.
    *   *Fix*: Enforce daily sales uploads from the partner portal.

---

## Chapter 7: Capital Efficiency

Stagnant stock ties up working capital. Planners must calculate the cost of dead inventory.

#### Formula:
$$\text{Capital Locked} = \text{Dead Stock Qty (90+ Days)} \times \text{Landed Cost}$$

#### Worked Example:
A distributor holds Ôé╣40,00,000 in stock.
*   Active inventory: Ôé╣28,00,000
*   Dead stock (aging over 90 days): Ôé╣12,00,000
$$\text{Capital Locked \%} = \left(\frac{12,00,000}{40,00,000}\right) \times 100 = 30.0\%$$
Planners must target a Capital Locked rate of under 20% by using stock transfers and targeted promotions.

---

## Chapter 8: Final Assessment (Certification Exam)

To obtain the **SMRITI PSV Certified Planner (Level 1)** credential, candidates must answer the following 20 questions.

### Questions:

1.  **What does the Distribution Visibility Gap refer to?**
    *   A. Delay in supplier payments.
    *   B. Lack of real-time visibility into distributor stock status after dispatch.
    *   C. Mismatch in general ledger tax postings.
2.  **Does the SMRITI PSV ledger modify ERPNext's primary stock ledger?**
    *   A. Yes, automatically.
    *   B. No, it is an independent Inventory Visibility Layer.
    *   C. Only during physical snapshot reconciliations.
3.  **What is the formula for Weeks of Cover (WOC)?**
    *   A. `Current Stock / Daily Sales`
    *   B. `Current Stock / Weekly Demand`
    *   C. `Dispatched Stock / Monthly Sales`
4.  **If Current Stock = 140 units and Weekly Sales Velocity = 28 units, what is the WOC?**
    *   A. 5.0 Weeks
    *   B. 4.0 Weeks
    *   C. 6.0 Weeks
5.  **Which WOC range indicates a critical stockout risk (Action Zone)?**
    *   A. 7 - 14 Weeks
    *   B. 3 - 7 Weeks
    *   C. < 3 Weeks
6.  **How is Sell-Through % calculated?**
    *   A. `(Units Sold / Units Shipped) * 100`
    *   B. `(Units Shipped / Units Sold) * 100`
    *   C. `(Units Sold / Total Capacity) * 100`
7.  **What should a planner do if a variant line has a Sell-Through rate of 18% and high stock levels?**
    *   A. Order more stock immediately.
    *   B. Freeze dispatches and run promotions or transfer stock.
    *   C. Increase the standard retail price.
8.  **What does ROP stand for in replenishment planning?**
    *   A. Retail Opportunity Point
    *   B. Reorder Point
    *   C. Reclaimed Outstanding Profit
9.  **If Safety Stock = 50, ADS = 10, and Lead Time = 6 days, what is the ROP?**
    *   A. 110 units
    *   B. 60 units
    *   C. 80 units
10. **Why are Network Stock Transfers preferred over shipping new stock from the factory?**
    *   A. They increase total tax liabilities.
    *   B. They clear regional surpluses and reduce stockout delays at lower costs.
    *   C. They modify core ERPNext General Ledgers.
11. **What is the root cause of a Negative Shadow Balance exception?**
    *   A. Too much safety stock.
    *   B. Sales uploads processed before dispatch invoices are imported.
    *   C. High distributor profit margins.
12. **How often should physical inventory snapshots be taken?**
    *   A. Every 6 months.
    *   B. Every 14 days.
    *   C. Daily at shift close.
13. **How does SMRITI calculate Capital Locked?**
    *   A. `Stagnant Stock Qty * Landed Cost`
    *   B. `Total Shipped Qty * MRP`
    *   C. `Sales Velocity * Standard Rate`
14. **What is the standard target for Inventory Freshness in the distributor network?**
    *   A. At least 50% under 30 days.
    *   B. At least 80% in Fresh or Active aging bands.
    *   C. 100% dead stock clearance.
15. **What does the Outlet Health Score measure?**
    *   A. Cashier attendance.
    *   B. Partner compliance with daily sales uploads and physical counts.
    *   C. Store square-footage productivity.
16. **How does the system prevent duplicate sales file uploads?**
    *   A. By locking the distributor's user profile.
    *   B. By generating and verifying an MD5 file checksum fingerprint.
    *   C. By checking the cashier's IP address.
17. **Which aging band represents the highest risk of capital lockup?**
    *   A. 0 - 30 Days
    *   B. 31 - 60 Days
    *   C. 90+ Days
18. **What does Primary Sales represent?**
    *   A. Stock sold by the distributor to retailers.
    *   B. Stock sold by the brand to the distributor.
    *   C. Direct sales at corporate outlets.
19. **If Lead Time increases, what happens to the Reorder Point (ROP)?**
    *   A. It decreases.
    *   B. It increases.
    *   C. It remains unchanged.
20. **Under Rule 10, can SMRITI automatically place purchase orders?**
    *   A. Yes, to save time.
    *   B. No, all reorders must suggest recommendations that require human approval.
    *   C. Only for franchise store channels.

---

### Answer Key:
1-B, 2-B, 3-B, 4-A, 5-C, 6-A, 7-B, 8-B, 9-A, 10-B, 11-B, 12-B, 13-A, 14-B, 15-B, 16-B, 17-C, 18-B, 19-B, 20-B.

---

### Author Profile (End)
- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL ÔÇô AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.
---
*SMRITI Certified Planner Program ÔÇö Level 1 Credential | AITDL Network*
