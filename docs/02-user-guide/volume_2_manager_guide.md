---
Document ID: "USER-032"
Title: "SMRITI Retail OS User Manual — Volume 2: Manager & Supervisor Guide"
Owner: "Support Team"
Audience: "Store Manager"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-28"
Last Reviewed: "2026-06-28"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Retail OS User Manual — Volume 2: Manager & Supervisor Guide


Welcome to the **SMRITI Retail OS Manager & Supervisor Guide**. This volume is written for Sales Managers, Distributor Supervisors, Audit Leads, and Store Owners. It covers auditing, stock rebalancing recommendations, and key administrative settings.

---

## Chapter 1: Audit & Variance Management (ÓñæÓñíÓñ┐Óñƒ ÓñöÓñ░ ÓñÁÓñ┐Óñ©ÓñéÓñùÓññÓñ┐ Óñ¬ÓÑìÓñ░Óñ¼ÓñéÓñºÓñ¿)

### 1. Purpose (ÓñëÓñªÓÑìÓñªÓÑçÓñÂÓÑìÓñ»)
The **Audit & Variance Management** module automatically reconciles physical counts (from [Physical Snapshots](dictionary:Physical Snapshot)) with the SMRITI shadow ledger. 
- **Business Problem Solved**: Identifying stock shrinkage (ÓñÜÓÑïÓñ░ÓÑÇ Óñ»Óñ¥ ÓñûÓÑïÓñ»Óñ¥ Óñ╣ÓÑüÓñå Óñ©ÓÑìÓñƒÓÑëÓñò) and posting ledger correction entries to align system balances.

### 2. Real-Life Example (ÓñÁÓñ¥Óñ©ÓÑìÓññÓñÁÓñ┐Óñò Óñ£ÓÑÇÓñÁÓñ¿ ÓñòÓñ¥ ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú)
At **Pune Plaza Footwear**, the SMRITI system records `Flyrunner-Blue-8` stock as **50 pairs**. 
During the monthly audit, the physical count is verified as **45 pairs**. SMRITI registers a **negative variance of 5 pairs** (Ôé╣12,495 retail value).

### 3. Step-by-Step Entry/Reconciliation Process (Óñ¬ÓÑìÓñ░ÓñòÓÑìÓñ░Óñ┐Óñ»Óñ¥)
1. **Menu Path**: SMRITI Home ÔåÆ Operations ÔåÆ Audit Console ÔåÆ **Reconciliation Sheet**
2. **Select Parameters**: Select the target [PSA](dictionary:PSA) and the audit date.
3. **Analyze Variance**: The screen will highlight rows with differences in red.
4. **Approve Adjustments**: The supervisor selects the reconciliation reason code (e.g. `THEFT`, `DAMAGE`, `DATA_ENTRY_ERROR`) and clicks **Approve & Adjust Ledger**.

[Screenshot: Audit Variance Console]

### 4. Field-by-Field Explanation (Óñ½ÓÑÇÓñ▓ÓÑìÓñí Óñ©ÓÑìÓñ¬ÓñÀÓÑìÓñƒÓÑÇÓñòÓñ░Óñú)

| Field Name | Type | Mandatory? | Simple Explanation | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **Audit Doc ID** | Link | **Yes** | Link to the submitted Physical Snapshot. | `AUD-2026-004` |
| **System Qty** | Float | Read-only | Expected stock quantity in the shadow ledger. | `50.0` |
| **Physical Qty** | Float | Read-only | Counted stock quantity. | `45.0` |
| **Variance Qty** | Float | Read-only | Difference (Physical Qty - System Qty). | `-5.0` |
| **Reconciliation Reason** | Select | **Yes** | Reason code for the difference. | `THEFT` |
| **Supervisor Notes** | Long Text | No | Remarks explaining the audit outcome. | `CCTV footage requested.` |

### 5. Example Transaction (ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú Óñ¬ÓÑìÓñ░ÓñÁÓñ┐ÓñÀÓÑìÓñƒÓñ┐)
- **Store**: `Pune Plaza Footwear`
- **Item**: `Flyrunner-Blue-8`
- **Variance**: `-5`
- **Approved Reason**: `DAMAGE`
- **Expected Output**: SMRITI adjusts the shadow ledger balance to 45.0 and logs a "SMRITI Liability Snapshot" record.

### 6. Reports & Analysis (Óñ░Óñ┐Óñ¬ÓÑïÓñ░ÓÑìÓñƒ ÓñöÓñ░ ÓñÁÓñ┐ÓñÂÓÑìÓñ▓ÓÑçÓñÀÓñú)
- **Report Name**: **Store Shrinkage & Variance Summary**
- **How to Read**: Displays total stock variance percentage for each store.
- **Action**: Any outlet showing variance greater than 3% requires a manager audit.

### 7. Common Mistakes (Óñ©Óñ¥Óñ«Óñ¥Óñ¿ÓÑìÓñ» ÓñùÓñ▓ÓññÓñ┐Óñ»Óñ¥Óñé)
- **Adjusting ledger without checking pending invoices**: Adjusting a negative variance of 10 units when a delivery truck containing 10 units is still unloading at the dock.
- *How to Fix*: Ensure all pending delivery notes and sales uploads are submitted before approving audits.

### 8. Business Interpretation (ÓñÁÓÑìÓñ»Óñ¥ÓñÁÓñ©Óñ¥Óñ»Óñ┐Óñò ÓñÁÓÑìÓñ»Óñ¥ÓñûÓÑìÓñ»Óñ¥)
- **Warning Sign**: Recurrent small positive variances followed by negative variances. This suggests store operators are logging fake audits to hide sales.

### 9. Frequently Asked Questions (FAQs)
1. **Can I undo a variance adjustment?**
   - No, once submitted. You must submit a fresh audit snapshot to correct it.
2. [Remaining FAQs in Volume 4]

### 10. Troubleshooting (Óñ©Óñ«Óñ©ÓÑìÓñ»Óñ¥ Óñ¿Óñ┐ÓñÁÓñ¥Óñ░Óñú)
- **Error**: `Cannot submit. Pending transactions exist for this PSA`.
- **Resolution**: Go to SMRITI Dashboard, check for unsubmitted Sales Uploads or Delivery Notes for this [PSA](dictionary:PSA), submit them, and retry the audit approval.

---

## Chapter 2: Transfer Recommendation (Óñ©ÓÑìÓñƒÓÑëÓñò ÓñƒÓÑìÓñ░Óñ¥ÓñéÓñ©Óñ½Óñ░ Óñ©ÓÑüÓñØÓñ¥ÓñÁ)

### 1. Purpose (ÓñëÓñªÓÑìÓñªÓÑçÓñÂÓÑìÓñ»)
The **Transfer Recommendation** module optimizes inventory distribution across outlets. It calculates when an overstocked store should transfer items to a stock-out store.
- **Business Problem Solved**: Prevents lost sales at one store while another store holds [dead stock](dictionary:Dead Stock). It computes the [Transfer Benefit Score](formula:TRF-001) to ensure freight and delay costs do not exceed the transfer benefit.

### 2. Real-Life Example (ÓñÁÓñ¥Óñ©ÓÑìÓññÓñÁÓñ┐Óñò Óñ£ÓÑÇÓñÁÓñ¿ ÓñòÓñ¥ ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú)
- **Mumbai Showroom** has **0 stock** of `Flyrunner-Blue-8` and sells 3 pairs a day. ([Stockout Risk](dictionary:Stockout Risk) = High).
- **Pune Showroom** has **50 pairs** of `Flyrunner-Blue-8` and sells only 0.2 pairs a day. (Overstock = High).
- SMRITI calculates the transfer economics and recommends shifting 20 pairs from Pune to Mumbai.

### 3. Step-by-Step Process (Óñ¬ÓÑìÓñ░ÓñòÓÑìÓñ░Óñ┐Óñ»Óñ¥)
1. **Menu Path**: SMRITI Home ÔåÆ Inventory ÔåÆ Transfer Recommendations
2. **Review Recommendations**: The system displays suggested transfers.
3. **Approve Transfer**: Click **Create Stock Transfer** (Óñ©ÓÑìÓñƒÓÑëÓñò ÓñƒÓÑìÓñ░Óñ¥ÓñéÓñ©Óñ½Óñ░ Óñ¼Óñ¿Óñ¥ÓñÅÓñé) to auto-generate the transfer request.

[Screenshot: Stock Transfer Recommendation list]

### 4. Calculation Explanation (ÓñùÓñúÓñ¿Óñ¥ Óñ©ÓÑìÓñ¬ÓñÀÓÑìÓñƒÓÑÇÓñòÓñ░Óñú)
The economic model checks:
$$\text{Transfer Benefit Score} = (\text{Item Retail Price} - \text{Freight Cost} - \text{Transit Delay Penalty}) \times \text{Transfer Qty}$$
- **Same Zone (e.g. West to West)**: Freight = Ôé╣6.0, Delay Penalty = Ôé╣5.0 per unit.
- **Different Zone (e.g. West to North)**: Freight = Ôé╣18.0, Delay Penalty = Ôé╣20.0 per unit.
- **Example calculation**:
  - Item Price = Ôé╣2,499. Transfer Qty = 20 pairs.
  - Same Zone: Benefit = $(2499 - 6.0 - 5.0) \times 20 = 2488 \times 20 = \text{Ôé╣49,760}$ (Highly recommended!).

### 5. Example Recommendation (ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú Óñ©ÓÑüÓñØÓñ¥ÓñÁ)
- **Source**: `Pune Plaza Footwear`
- **Target**: `Mumbai Grand Mall`
- **Item**: `SF-FLY-BLU-8`
- **Quantity**: `20`
- **Reason Code**: `EXCESS_WOC_AT_SOURCE,POSITIVE_TRANSFER_BENEFIT`

### 6. Reports & Analysis (Óñ░Óñ┐Óñ¬ÓÑïÓñ░ÓÑìÓñƒ ÓñöÓñ░ ÓñÁÓñ┐ÓñÂÓÑìÓñ▓ÓÑçÓñÀÓñú)
- **Report Name**: **Rebalancing Opportunity Log**
- **Action**: Check weekly recommendations and approve local transfers.

### 7. Common Mistakes (Óñ©Óñ¥Óñ«Óñ¥Óñ¿ÓÑìÓñ» ÓñùÓñ▓ÓññÓñ┐Óñ»Óñ¥Óñé)
- **Ignoring transit delays**: Transferring seasonal items across distant zones (e.g., Mumbai to Delhi) during monsoon delays. SMRITI adjusts the score down to penalize cross-zone transit times.

### 8. Business Interpretation (ÓñÁÓÑìÓñ»Óñ¥ÓñÁÓñ©Óñ¥Óñ»Óñ┐Óñò ÓñÁÓÑìÓñ»Óñ¥ÓñûÓÑìÓñ»Óñ¥)
- **Decision**: Approve transfer if the Benefit Score is positive. Reject if negative.

### 9. FAQs
1. **What is a Transit Delay Penalty?**
   - The cost of having inventory locked in transport, which makes it unavailable for sale during transit.

### 10. Troubleshooting (Óñ©Óñ«Óñ©ÓÑìÓñ»Óñ¥ Óñ¿Óñ┐ÓñÁÓñ¥Óñ░Óñú)
- **Error**: `No transfer recommended despite stockout`.
- **Resolution**: Check if neighboring stores have excess stock above their safety levels. If all stores are at or below safety stock, the system recommends a Purchase order instead.

---

## Chapter 3: Administration & Settings (Óñ¬ÓÑìÓñ░ÓñÂÓñ¥Óñ©Óñ¿Óñ┐Óñò Óñ©ÓÑçÓñƒÓñ┐ÓñéÓñùÓÑìÓñ©)

### 1. Purpose (ÓñëÓñªÓÑìÓñªÓÑçÓñÂÓÑìÓñ»)
This module allows administrators and supervisors to configure the global variables, reorder rules, and limits that govern SMRITI's predictive models.
- **Business Problem Solved**: Customizes SMRITI to fit your business lead times, safety margins, and forecasting parameters.

### 2. Real-Life Example (ÓñÁÓñ¥Óñ©ÓÑìÓññÓñÁÓñ┐Óñò Óñ£ÓÑÇÓñÁÓñ¿ ÓñòÓñ¥ ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú)
During festival season (e.g., Diwali), supplier delivery times increase from **7 days** to **14 days**. The administrator updates the global [Lead Time](dictionary:Lead Time) settings to 14 days to prevent stockouts.

### 3. Step-by-Step Configuration Process (Óñ¬ÓÑìÓñ░ÓñòÓÑìÓñ░Óñ┐Óñ»Óñ¥)
1. **Menu Path**: SMRITI Home ÔåÆ Administration ÔåÆ SMRITI PSV Settings
2. **Define Rules**: Create a `SMRITI PSV Reorder Rule` for specific item groups.
3. **Save**: Click Save. No server restarts are needed.

[Screenshot: SMRITI PSV Settings Page]

### 4. Field-by-Field Explanation (Óñ½ÓÑÇÓñ▓ÓÑìÓñí Óñ©ÓÑìÓñ¬ÓñÀÓÑìÓñƒÓÑÇÓñòÓñ░Óñú)

| Field Name | Type | Mandatory? | Explanation | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **Default Lead Time Days** | Int | **Yes** | Time taken by supplier to deliver stock (in days). | `7` |
| **Default Safety Stock** | Float | **Yes** | Minimum stock buffer to keep at stores. | `15.0` |
| **Reorder Avg Weeks** | Int | **Yes** | Lookback window for [Sales Velocity](formula:INV-001) math. | `4` |
| **Forecast Model** | Select | **Yes** | Model used (Defaults to Exponential Moving Average). | [EMA](dictionary:EMA) |

### 5. Example Settings Configuration (ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú Óñ¬ÓÑìÓñ░ÓñÁÓñ┐ÓñÀÓÑìÓñƒÓñ┐)
- **Rule Scope**: Item Group = `Sports Shoes`
- **Lead Time**: `10`
- **Safety Stock**: `20.0`
- **Result**: All sports shoes will maintain a minimum safety buffer of 20 pairs.

### 6. Reports & Analysis (Óñ░Óñ┐Óñ¬ÓÑïÓñ░ÓÑìÓñƒ ÓñöÓñ░ ÓñÁÓñ┐ÓñÂÓÑìÓñ▓ÓÑçÓñÀÓñú)
- **Report Name**: **Reorder Rule Registry**
- **Action**: Audit store reorder rules monthly to ensure safety stock levels align with updated sales trends and target [Inventory Turnover](formula:INV-004) ratios.

### 7. Common Mistakes (Óñ©Óñ¥Óñ«Óñ¥Óñ¿ÓÑìÓñ» ÓñùÓñ▓ÓññÓñ┐Óñ»Óñ¥Óñé)
- **Setting excessive safety stock**: Setting a safety stock of 1000 pairs for a store that sells only 5 pairs a week. This locks up valuable capital.
- *How to Fix*: Check the store's average weekly sales before updating safety stock limits.

### 8. Business Interpretation (ÓñÁÓÑìÓñ»Óñ¥ÓñÁÓñ©Óñ¥Óñ»Óñ┐Óñò ÓñÁÓÑìÓñ»Óñ¥ÓñûÓÑìÓñ»Óñ¥)
- **Decision**: Update target days cover to higher values for fast-moving items, and lower values for slow-moving fashion items.

### 9. FAQs
1. **Can store operators edit these settings?**
   - No. Only users with the "Administrator" or "System Manager" role have write access.

### 10. Troubleshooting (Óñ©Óñ«Óñ©ÓÑìÓñ»Óñ¥ Óñ¿Óñ┐ÓñÁÓñ¥Óñ░Óñú)
- **Error**: `Validation Error: Max Stock must be greater than Safety Stock`.
- **Resolution**: Set `max_stock` to a value higher than `safety_stock` in the reorder rule and click save.

---

## Chapter 4: Knowledge Governance Framework (KGF) (Óñ£ÓÑìÓñ×Óñ¥Óñ¿ Óñ¬ÓÑìÓñ░ÓñÂÓñ¥Óñ©Óñ¿ ÓñóÓñ¥ÓñéÓñÜÓñ¥)

### 1. Purpose (ÓñëÓñªÓÑìÓñªÓÑçÓñÂÓÑìÓñ»)
The **Knowledge Governance Framework (KGF)** is the transparency and compliance engine of SMRITI. It ensures that every mathematical formula, forecast model, performance metric, or business KPI displayed to managers or cashiers is fully explainable and registered, preventing any "black-box" decision-making.
- **Business Problem Solved**: Eliminates confusion and builds trust by letting ground-level operators immediately understand *how* a value was calculated, *what* the value means for their daily operations, and *what actions* they must take next.

### 2. Real-Life Example (ÓñÁÓñ¥Óñ©ÓÑìÓññÓñÁÓñ┐Óñò Óñ£ÓÑÇÓñÁÓñ¿ ÓñòÓñ¥ ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú)
A store manager at **Royal Pune Showroom** looks at their reorder report and sees a [Weeks of Cover (WOC)](formula:INV-002) metric of **1.5 weeks** for a popular running shoe variant. 
Instead of guessing how the 1.5 figure was arrived at, the manager clicks the **Ôôÿ Explain** icon next to the number. A clean modal pops up, showing:
- [WOC](dictionary:WOC) means the estimated weeks current stock will last.
- The mathematical formula: `current_stock / weekly_velocity`.
- A live worked example: `Current Stock = 30 pairs, Weekly Velocity = 20 pairs/week. WOC = 30 / 20 = 1.5`.
- A recommendation band showing that 1.5 is "Critical", advising the manager to immediately place a reorder.

### 3. Step-by-Step Process (Óñ¬ÓÑìÓñ░ÓñòÓÑìÓñ░Óñ┐Óñ»Óñ¥)
1. **Explain any KPI**: Click the **Ôôÿ Explain** button next to any calculated metric on any SMRITI dashboard or report.
2. **Read the Explanation**: The Universal Explain Modal displays the business meaning, mathematical expression, data sources, worked example, and recommended action steps.
3. **Lookup Glossaries**: Click the **­ƒôû Dictionary Entry** button inside the modal to navigate directly to the central **Business Dictionary** (/smriti-dictionary) to explore related terms (like [PDT](dictionary:PDT) or [PSA](dictionary:PSA)), Hinglish explanations, FAQs, and common mistakes.
4. **Manage Formulas (Admin/Managers)**: Go to **Help Desk ÔåÆ Formula Registry** (/smriti-formula-registry) to view, audit, or approve new mathematical formulas used across the platform.

### 4. Field-by-Field Explanation (SMRITI Formula Definition)

| Field Name | Type | Mandatory? | Simple Explanation | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **Formula ID** | Data | **Yes** | Unique identifier of the formula. | [INV-002](formula:INV-002) |
| **Formula Name** | Data | **Yes** | Human-readable name of the metric. | `Weeks of Cover` |
| **Formula Expression**| Data | **Yes** | Mathematical representation of the formula. | `current_stock / weekly_velocity` |
| **Business Meaning** | Long Text | **Yes** | What the metric measures in simple terms. | `How many weeks your stock will last.` |
| **Worked Example** | Long Text | **Yes** | Step-by-step arithmetic walk-through. | `30 / 20 = 1.5 weeks.` |
| **Interpretation Guide**| Long Text | **Yes** | Explanation of metric bands (Critical/Healthy).| `WOC < 2: Critical; WOC > 4: Overstock` |
| **Recommended Action**| Long Text | **Yes** | Concrete action for the operator. | `Place reorder immediately if Critical.` |

### 5. Example Registry Entry (ÓñëÓñªÓñ¥Óñ╣Óñ░Óñú Óñ¬ÓÑìÓñ░ÓñÁÓñ┐ÓñÀÓÑìÓñƒÓñ┐)
- **Formula ID**: [INV-003](formula:INV-003)
- **Name**: [Dead Stock Score](dictionary:Dead Stock)
- **Expression**: `inactive_days * stock_value`
- **Worked Example**: `Inactive Days = 90 days. Stock Value = Ôé╣10,000. Dead Stock Score = 90 * 10,000 = 900,000.`
- **Recommended Action**: If score > 500,000, mark for outlet rebalancing or discount clearance.

### 6. Reports & Analysis (Óñ░Óñ┐Óñ¬ÓÑïÓñ░ÓÑìÓñƒ ÓñöÓñ░ ÓñÁÓñ┐ÓñÂÓÑìÓñ▓ÓÑçÓñÀÓñú)
- **Log Name**: **SMRITI PSV Activity Log**
- **How to Read**: Tracks all user accesses to formulas and dictionary terms. 
- **Action**: Look at the most frequently clicked explanations to identify which metrics require additional team training.

### 7. Common Mistakes (Óñ©Óñ¥Óñ«Óñ¥Óñ¿ÓÑìÓñ» ÓñùÓñ▓ÓññÓñ┐Óñ»Óñ¥Óñé)
- **Deploying calculated metrics without registry entry**: Developers adding a new KPI to a custom report without creating a corresponding record in the central Formula Registry. The dashboard will block showing the metric or fail explainability audits.
- *How to Fix*: Always register the formula and obtain manager approval before enabling it on live dashboards.

### 8. Business Interpretation (ÓñÁÓÑìÓñ»Óñ¥ÓñÁÓñ©Óñ¥Óñ»Óñ┐Óñò ÓñÁÓÑìÓñ»Óñ¥ÓñûÓÑìÓñ»Óñ¥)
- **Standard**: Every number shown to a store partner must have a clear business translation. "Numbers without explanations cause confusion; clear definitions drive faster action."

### 9. FAQs
1. **How is the explain modal so fast?**
   - The system utilizes Redis caching (key `smriti:explain:{formula_id}:{version}`) with a **1-hour TTL** to serve definitions in sub-milliseconds.
2. **Who can update dictionary definitions or formulas?**
   - Only AITDL Core Team members and chief administrators can approve changes, ensuring that business definitions remain standardized.

### 10. Troubleshooting (Óñ©Óñ«Óñ©ÓÑìÓñ»Óñ¥ Óñ¿Óñ┐ÓñÁÓñ¥Óñ░Óñú)
- **Error**: `Formula definition not found or is in Draft status`.
- **Resolution**: Open the Formula Registry, find the Formula ID, ensure the status is changed from `Draft` to `Approved` and `Is Active` is checked.

---

## Chapter 5: SMRITI Navigation Manager (SNM) (स्मृति नेविगेशन प्रबंधक)

### 1. Purpose (उद्देश्य)
The **SMRITI Navigation Manager (SNM)** provides a fully dynamic, database-driven sidebar layout engine that replaces hard-coded menus. Store owners and administrators can configure distinct navigation profiles, customize labels, change icons, and reorder menus without redeploying code.
- **Business Problem Solved**: Bypasses the need for software code updates whenever a retail franchise wants to restrict cashier views, rename catalog menus, or change icon symbols.

### 2. Real-Life Example (वास्तविक जीवन का उदाहरण)
At **Pune Plaza Footwear**, the manager wants Cashiers to *only* see **Sales** (POS Billing) and **Help Desk** menus, hiding all purchasing, inventory, and backend configurations. The administrator creates a Navigation Profile named `Cashier Profile`, overrides the visibility of unauthorized menus, and assigns it to all users with the `SMRITI Cashier` role.

### 3. Step-by-Step Configuration Process (प्रक्रिया)
1. **Menu Path**: SMRITI Home ➔ Administration ➔ **Navigation Profiles**
2. **Create Profile**: Click **New SMRITI Navigation Profile**, enter the profile name (e.g. `Cashier Navigation`), and specify the home dashboard route.
3. **Add Overrides**: Click **New SMRITI Navigation Override**, select your target Profile, input the canonical `Menu ID` (e.g. `inventory`), and set the Override State to `Disabled` to hide it.
4. **Define Assignment**: Go to **Navigation Assignments**, create an assignment mapping the role `SMRITI Cashier` to your new Navigation Profile with a priority weight of `50`.
5. **Flush Cache**: If changes do not reflect instantly, clear the cache using the administrative action button.

### 4. Field-by-Field Explanation (SMRITI Navigation Override)

| Field Name | Type | Mandatory? | Simple Explanation | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| **Menu ID** | Data | **Yes** | The canonical identifier linking to the static config registry. | `inventory` |
| **Navigation Profile** | Link | **Yes** | The navigation profile this override applies to. | `Cashier Profile` |
| **Override State** | Select | **Yes** | Behaves as: Inherit (default), Override (custom settings), or Disabled (hidden). | `Override` |
| **Label Override** | Data | No | Customized title text for the menu node. | `Stockroom Management` |
| **Display Order** | Int | No | Reordering weight for layout sorting. | `15` |

---

## Support & Helpdesk
Thank you for using SMRITI Retail OS. For additional support, please contact the Helpdesk at **support@aitdl.com**.


---

## Purchase Performance Monitoring (v2.0.0)

### Purchase Reports for Managers

Access from: **Reports → Purchase Reports** or **Analytics Studio → Purchase**

| Report | What to Monitor | Frequency |
|---|---|---|
| Purchase Order Summary | Open POs, pending approvals, balance amounts | Daily |
| Purchase Invoice Register | Overdue invoices (highlighted red) | Daily |
| Supplier Purchase Summary | Supplier spend trends, top vendors | Weekly |
| Item-wise Purchase Analysis | Cost per item, weighted average rate | Monthly |
| Purchase Return Register | Return rates, GST reconciliation | Monthly |

### Approval Queue Management

If you are a Purchase Approver:
1. Go to **Purchase Center → Purchase Orders**
2. Filter by **Status = Pending Approval**
3. Review each PO — check items, quantities, rates
4. Click **Approve** or **Reject** with a reason
5. All decisions are logged in the SMRITI Purchase Audit Log

> **Policy:** POs above the approval threshold (configured in Purchase Settings) cannot be submitted without your approval.

### Negative Stock Alerts

The SMRITI Negative Stock Engine (SNSM) automatically flags negative stock events.

**Daily checklist:**
1. Go to **Inventory → Negative Stock Cases**
2. Open any cases with status **Open**
3. Review the root cause (missing GRN, data entry error, etc.)
4. Approve or reject the proposed recovery action

> **Target:** Zero open negative stock cases at end of day.

For full SNSM guide: [Negative Stock Management User Guide](./negative_stock_management.md)
