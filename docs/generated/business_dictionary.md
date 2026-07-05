---
Document ID: "SMRITI-DOC-027"
Title: "SMRITI Business Dictionary"
Owner: "Product Team"
Audience: "Support Engineer"
Module: "Core"
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

# SMRITI Business Dictionary Glossary

* **Compiler Version:** 1.1
* **Snapshot Commit:** `f95b4fe91f273f7a6745f2f7d1de4733757db2dd`
* **Compiled At:** 2026-06-25T10:19:35Z

## Glossary Terms

### Party Stock Account (`PSA`)
* **Artifact ID:** `ART-TERM-00517`
* **Category:** `Distribution`
* **Definition:** Party Stock Account maintains the ledger balances and shadow accounting of stock held by channel partners.
* **Hinglish Definition:** *Distributors ya channel partners ke stock balances aur shadow ledger calculations ko track karne wala internal ledger master.*
* **Aliases:** PSA, Stock Account, Channel Account
* **Manual Reference:** `Volume 3 > Distribution Operations`

### Party Stock Visibility (`PSV`)
* **Artifact ID:** `ART-TERM-00518`
* **Category:** `Distribution`
* **Definition:** Party Stock Visibility provides real-time insights into distributor and dealer inventory levels.
* **Hinglish Definition:** *Distributors aur secondary retail outlets ke stock levels aur sell-through activity ko monitor karne ki central visual tracking facility.*
* **Aliases:** PSV, Channel Stock Visibility, Partner Stock
* **Manual Reference:** `Volume 3 > Inventory Analytics`

### Predictive Distribution Twin (`PDT`)
* **Artifact ID:** `ART-TERM-00519`
* **Category:** `Forecasting`
* **Definition:** Predictive Distribution Twin utilizes historical demand, lead time, and variance parameters to optimize replenishment across outlets.
* **Hinglish Definition:** *Sales history, lead time, aur safety stock factors ke analytics par chalne wala intelligent store replenishment algorithm.*
* **Aliases:** PDT, Replenishment Engine, Stock Planner
* **Manual Reference:** `Volume 4 > Replenishment Science`

### Weeks of Cover (`WOC`)
* **Artifact ID:** `ART-TERM-00520`
* **Category:** `Inventory`
* **Definition:** Weeks of Cover is the duration in weeks that current stock will last based on standard weekly sales velocity.
* **Hinglish Definition:** *Warehouse ya store mein pada hua stock, average weekly sales velocity ke hisaab se kitne weeks tak chalega.*
* **Aliases:** WOC, Weeks of Cover, Inventory Coverage, Stock Cover
* **Manual Reference:** `Volume 3 > Inventory Control`

### Sales Velocity (`Sales Velocity`)
* **Artifact ID:** `ART-TERM-00521`
* **Category:** `Sales`
* **Definition:** Weekly sales velocity calculated over a lookback window (standard 30 days).
* **Hinglish Definition:** *Kisi specific period (lookback window) ke sales data par calculate ki gayi average weekly product sales velocity.*
* **Aliases:** Sales Velocity, Velocity, Weekly Sales Rate
* **Manual Reference:** `Volume 3 > Sales Analytics`

### Forecast Confidence Score (`Forecast Confidence`)
* **Artifact ID:** `ART-TERM-00522`
* **Category:** `Forecasting`
* **Definition:** Calculated score indicating reliability of forecasted demand based on demand volatility (Coefficient of Variation).
* **Hinglish Definition:** *Demand volatility ke parameters (Coefficient of Variation) par system forecast confidence score check karta hai.*
* **Aliases:** Forecast Confidence, Confidence Score, Forecasting Reliability
* **Manual Reference:** `Volume 4 > Forecasting Science`

### Dead Stock Score (`Dead Stock`)
* **Artifact ID:** `ART-TERM-00523`
* **Category:** `Inventory`
* **Definition:** Evaluates stock aging and inactive sales duration to calculate stock liquidation priority score.
* **Hinglish Definition:** *Aise inventory items jo kaafi time se sell nahi hue hain, unki static duration par dead stock score nikaala jaata hai.*
* **Aliases:** Dead Stock, Liquidation Score, Slow Moving Stock
* **Manual Reference:** `Volume 3 > Inventory Valuation`

### Sell Through Percentage (`Sell Through`)
* **Artifact ID:** `ART-TERM-00524`
* **Category:** `Sales`
* **Definition:** Percentage of received inventory sold within a specified sales cycle.
* **Hinglish Definition:** *Ek specific stock batch mein se kitne percent mal customer ko sell ho chuka hai (total sales quantity divided by opening stock plus receipts).*
* **Aliases:** Sell Through, Sell Through %, ST%
* **Manual Reference:** `Volume 3 > Sales Performance`

### Stock Accuracy Score (`Stock Accuracy`)
* **Artifact ID:** `ART-TERM-00525`
* **Category:** `Audit`
* **Definition:** Measures variance between physical inventory count values and system ledger balances.
* **Hinglish Definition:** *Physical counting inventory aur system ledger balances ke differences ka variance percentage calculation.*
* **Aliases:** Stock Accuracy, Audit Score, Inventory Accuracy
* **Manual Reference:** `Volume 3 > Audit Compliance`

### Inventory Turnover Ratio (`Inventory Turnover`)
* **Artifact ID:** `ART-TERM-00526`
* **Category:** `Inventory`
* **Definition:** Ratio showing how many times a company's inventory is sold and replaced over a year.
* **Hinglish Definition:** *Ek saal mein inventory kitni baar total replace ya rotate hoti hai (Cost of Goods Sold divided by average inventory value).*
* **Aliases:** Inventory Turnover, Turnover Ratio, ITR
* **Manual Reference:** `Volume 3 > Financial Inventory Control`

### Outlet Health Score (`Outlet Health Score`)
* **Artifact ID:** `ART-TERM-00527`
* **Category:** `Outlet`
* **Definition:** Consolidated score combining sync delay performance and ledger stock count variance indicators.
* **Hinglish Definition:** *Kisi specific store outlet ki inventory sync speed aur ledger reconciliation variances ka unified indicator score.*
* **Aliases:** Outlet Health Score, OHS, Store Health
* **Manual Reference:** `Volume 5 > Store Administration`

### Transfer Benefit Score (`Transfer Benefit Score`)
* **Artifact ID:** `ART-TERM-00528`
* **Category:** `Distribution`
* **Definition:** Calculates financial retaining benefit value of transferring stock between outlets versus origin stockout risk and transit freight costs.
* **Hinglish Definition:** *Ek outlet se doosre outlet mal transfer karne par margin benefit aur freight cost ka comparison assessment score.*
* **Aliases:** Transfer Benefit Score, TBS, Transfer Optimization
* **Manual Reference:** `Volume 4 > Distribution Science`

### Physical Inventory Snapshot (`Physical Snapshot`)
* **Artifact ID:** `ART-TERM-00529`
* **Category:** `Audit`
* **Definition:** A frozen state of ledger balances captured for auditing against physical warehouse count sheets.
* **Hinglish Definition:** *Physical counting audit ke time, database ledger stocks ko freeze karke comparative sheet banana.*
* **Aliases:** Physical Snapshot, Audit Snapshot, Stock Freeze
* **Manual Reference:** `Volume 3 > Audit Compliance`

### Party Stock Ledger (`Party Stock Ledger`)
* **Artifact ID:** `ART-TERM-00530`
* **Category:** `Distribution`
* **Definition:** Records chronological transaction ledger logs of partner stock movement (Receipts, Sales, Returns).
* **Hinglish Definition:** *Channel partner ke stock transactions (mal milna, customer ko bechna, return aana) ka chronologically detailed ledger book.*
* **Aliases:** Party Stock Ledger, PSL, Channel Ledger
* **Manual Reference:** `Volume 3 > Partner Operations`

### Reorder Suggestion (`Reorder Suggestion`)
* **Artifact ID:** `ART-TERM-00531`
* **Category:** `Forecasting`
* **Definition:** Quantity recommendations generated by forecasting engines to replenish safety stocks.
* **Hinglish Definition:** *Safety stock ko maintain karne ke liye forecasting algorithms dwara suggest ki gayi purchase quantity recommendation.*
* **Aliases:** Reorder Suggestion, Reorder Recs, Replenishment Qty
* **Manual Reference:** `Volume 4 > Replenishment Science`

### Stockout Risk Index (`Stockout Risk`)
* **Artifact ID:** `ART-TERM-00532`
* **Category:** `Forecasting`
* **Definition:** Calculates probability of stocking out before the next replenishment delivery arrives based on lead time variance.
* **Hinglish Definition:** * replenishment order aane se pehle store ka mal khatam hone ke risk ka statistical index probability score.*
* **Aliases:** Stockout Risk, Out of Stock Risk, SOR
* **Manual Reference:** `Volume 4 > Forecasting Science`

### Variant Size Curve (`Variant Curve`)
* **Artifact ID:** `ART-TERM-00533`
* **Category:** `Inventory`
* **Definition:** Represents the demand and stock distribution ratio across sizes or variants of a style.
* **Hinglish Definition:** *Kisi product style ke different sizes aur variants ki demand and availability distribution ratio model.*
* **Aliases:** Variant Curve, Size Curve, Size Ratio
* **Manual Reference:** `Volume 3 > Variant Management`

### Exponential Moving Average (`EMA`)
* **Artifact ID:** `ART-TERM-00534`
* **Category:** `Forecasting`
* **Definition:** A moving average placing greater weight and significance on the most recent demand data points.
* **Hinglish Definition:** *Sales forecasting mein recent demand trends ko zyada priority dene wala weighted moving average calculations method.*
* **Aliases:** EMA, Exponential Average, Weighted Average
* **Manual Reference:** `Volume 4 > Demand Science`

### Seasonality Factor (`Seasonality Factor`)
* **Artifact ID:** `ART-TERM-00535`
* **Category:** `Forecasting`
* **Definition:** Multiplicative multiplier adjusting forecasts based on cyclical demand changes (e.g. festivals).
* **Hinglish Definition:** *Sales forecasts ko festival spikes aur seasonal changes ke hisaab se adjust karne wala demand multiplier index factor.*
* **Aliases:** Seasonality Factor, Seasonality Index, Seasonal Index
* **Manual Reference:** `Volume 4 > Demand Science`

### Supplier Lead Time (`Lead Time`)
* **Artifact ID:** `ART-TERM-00536`
* **Category:** `Distribution`
* **Definition:** The chronological duration between purchase order release and store shelf GRN completion.
* **Hinglish Definition:** *Purchase order release karne se lekar store/warehouse par mal physically receive hone tak ka total transit and delivery days time.*
* **Aliases:** Lead Time, Supplier Lead Time, PO to GRN Time
* **Manual Reference:** `Volume 3 > Supplier Operations`
