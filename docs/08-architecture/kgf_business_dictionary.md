---
Document ID: "ARCH-014"
Title: "SMRITI Business Dictionary (DOC-04)"
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

# SMRITI Business Dictionary (DOC-04)

The **Business Dictionary** is the central glossary of SMRITI Retail OS. It maps and documents all key retail operational terms (such as PSA, PSV, PDT, WOC, Dead Stock, Size Curves) and links them to the **Formula Registry** and related terms. This ensures that cashiers, store managers, and executives have a unified, searchable reference.

---

## 📋 Schema Definition (`SMRITI Business Term`)

The Business Dictionary is backed by the `SMRITI Business Term` DocType. Each record contains:

*   **Term ID**: Unique glossary key (e.g. `PSA`, `PDT`).
*   **Term Name**: Descriptive name (e.g. "Predictive Distribution Twin").
*   **Term Category**: Category Select (e.g. `Distribution`, `Inventory`, `Forecasting`, `Sales`, `Audit`, `Outlet`).
*   **Term Version**: Glossary versioning (e.g. `1.0.0`).
*   **Replaces Term**: Self-link to a deprecated version of the term.
*   **Status**: Draft, Under Review, Approved, Deprecated (Enforces that only Approved terms can be active).
*   **Definition**: Plain-English definition.
*   **Hinglish Definition**: A localized explanation blending English terminology with Hindi sentence structure to assist ground-level operators.
*   **Term Aliases**: JSON array of aliases for enhanced searchability (e.g. `["Replenishment Engine", "Stock Planner"]`).
*   **FAQ**: JSON list of questions and answers.
*   **Common Mistakes**: JSON list of common operational errors and mitigation advice.
*   **Related Formulas**: Child table (`SMRITI Related Formula`) linking to the Formula Registry.
*   **Related Terms**: Child table (`SMRITI Related Term`) linking to other business terms.
*   **Manual & Training References**: References to printed user guides and training workbook modules.

---

## ⚡ Seeding & Link Validation

*   **Two-Phase Seeding**: To prevent `LinkValidationError` exceptions caused by forward-referencing child tables (e.g. term A linking to term B before term B is created), the seeding patch `seed_default_terms.py` runs in two phases:
    1.  **Phase 1**: Seeds the parent `SMRITI Business Term` records with all text, category, and JSON data.
    2.  **Phase 2**: Resolves database hashes and updates `related_formulas` and `related_terms` child tables with correct document name links.

---

## ⚡ Caching & Auditing

*   **Redis Caching**: Term details are cached in Redis at key `smriti:dictionary:{term_id}:{version}` with a **TTL of 3600 seconds** (1 hour). 
*   **Access Auditing**: Every lookup (cache hit or miss) is recorded in `SMRITI PSV Activity Log` with:
    *   `action_type` = `"Dictionary Accessed"`
    *   `event_type` = `"DICTIONARY_ACCESSED"`
    *   `reference_name` = `{term_id}`

---

## 📖 Core Business Terms

The following core business terms are registered in the Business Dictionary for Clienteling and Outlet Intelligence:

### 1. Customer Health Score (`CUST-HEALTH`)
*   **Term Name**: Customer Health Score
*   **Category**: `Clienteling`
*   **Version**: `1.1.0`
*   **Definition**: A composite metric between 0.0 and 100.0 representing the customer's overall engagement, value, and loyalty profile. It is calculated by weighting their churn risk, VIP candidate score, and campaign affinity.
*   **Hinglish Definition**: Customer ki overall profile value aur checkout engagement ko assess karne wala score. Churn risk, VIP candidate score aur campaign affinity ko jodkar composite score banaya jata hai taaki target promotions clear ho sakein.
*   **Term Aliases**: `["Customer Profile Score", "Engagement Health Index", "Customer Health Score"]`
*   **FAQ**:
    *   *Question*: Score kis limit mein hota hai?
    *   *Answer*: Score hamesha 0 aur 100 ke beech clamp hota hai.
    *   *Question*: Health Score high hone ka kya matlab hai?
    *   *Answer*: High health score (e.g., > 80%) yeh darshata hai ki customer highly active hai aur churn risk bohot kam hai.
*   **Common Mistakes**:
    *   *Mistake*: Churn risk aur health score ko same samajhna.
    *   *Correction*: Churn risk high hone par health score kam hoga. Dono inversely related hain.

### 2. Outlet Conversion Index (`OUT-CONV`)
*   **Term Name**: Outlet Conversion Index
*   **Category**: `Outlet`
*   **Version**: `1.1.0`
*   **Definition**: A performance benchmark measuring the percentage ratio of walk-in customers who successfully complete a purchase transaction relative to the total number of walk-ins recorded for the outlet.
*   **Hinglish Definition**: Kisi showroom ya outlet par total walk-in customers mein se kitne customers bill purchase complete karte hain, uski conversion percentage.
*   **Term Aliases**: `["Walk-in Conversion Rate", "Store Conversion Index"]`
*   **FAQ**:
    *   *Question*: Conversion Index check karna kyun zaroori hai?
    *   *Answer*: Isse outlet ki footfall efficiency aur sales team ki effectiveness ka pata chalta hai.
*   **Common Mistakes**:
    *   *Mistake*: Total sales amount ko conversion rate samajhna.
    *   *Correction*: Conversion sirf bills divided by total walk-ins ka ratio hai, sales value nahi.

### 3. Executive Performance Index (`EXEC-PERF`)
*   **Term Name**: Executive Performance Index
*   **Category**: `Sales`
*   **Version**: `1.1.0`
*   **Definition**: A performance score measuring the sales conversion efficiency, customer interaction duration, and upsell rate of a specific store sales executive.
*   **Hinglish Definition**: Store floor sales executives ki performance aur customer conversation efficiency ko assess karne wala rating score.
*   **Term Aliases**: `["Salesperson Efficiency Index", "Executive Conversion Index"]`
*   **FAQ**:
    *   *Question*: Index high hone par incentive milega?
    *   *Answer*: Haan, SFC module is index ko target checks ke liye use kar sakta hai.
*   **Common Mistakes**:
    *   *Mistake*: Sirf customer ratings par executive ko rank karna.
    *   *Correction*: Performance Index sales velocity aur conversion ko bhi verify karta hai.

### 4. Store Retention Index (`STORE-RET`)
*   **Term Name**: Store Retention Index
*   **Category**: `Outlet`
*   **Version**: `1.1.0`
*   **Definition**: The ratio of repeat customers who return to purchase at the same outlet within a designated lookback window (typically 90 days).
*   **Hinglish Definition**: Kisi outlet par aane wale purane (repeat) customers ka percentage jo checkouts frequency aur customer loyalty ko reflect karta hai.
*   **Term Aliases**: `["Store Loyalty Index", "Customer Retention Rate"]`
*   **FAQ**:
    *   *Question*: Dynamic lookback change ho sakta hai?
    *   *Answer*: Haan, lookback periods configuration ke mutabik change hote hain (e.g. 90 ya 180 days).
*   **Common Mistakes**:
    *   *Mistake*: Naye walk-ins ko repeat customer samajh lena.
    *   *Correction*: Repeat customer wahi hai jiska phone/ID customer graph mein matched transaction dikhata hai.

### 5. Graph Freshness (`GRPH-FRSH`)
*   **Term Name**: Graph Freshness
*   **Category**: `Governance`
*   **Version**: `1.1.0`
*   **Definition**: An operational status indicator measuring the elapsed time since the Customer Intelligence Graph (CIG) compilation job was last executed.
*   **Hinglish Definition**: Customer Intelligence Graph (CIG) last time kab update hua tha usko check karne wala indicator (Freshness in milliseconds/minutes).
*   **Term Aliases**: `["CIG Freshness Indicator", "Graph Sync Status"]`
*   **FAQ**:
    *   *Question*: Graph normal intervals par kab update hota hai?
    *   *Answer*: Automatic schedule night batch ya administrator demand ke through run hota hai.
*   **Common Mistakes**:
    *   *Mistake*: Stale graph details par campaign run karna.
    *   *Correction*: Freshness field check karein; agar status Failed hai ya stale hai toh manual trigger click karein.

### 6. Graph Version (`GRPH-VER`)
*   **Term Name**: Graph Version
*   **Category**: `Governance`
*   **Version**: `1.1.0`
*   **Definition**: A semantic versioning indicator (e.g. "CIG-1.1") detailing the layout structure and prediction algorithms used during graph generation.
*   **Hinglish Definition**: Customer graph details generate karne ke algorithms aur schemas ka standard version code (e.g., CIG-1.1).
*   **Term Aliases**: `["CIG Schema Version", "Graph Layout Version"]`
*   **FAQ**:
    *   *Question*: Version updates automatically hote hain?
    *   *Answer*: Haan, system algorithms update hone par version code backend se propagate hota hai.

---

## Support & Helpdesk
For questions or support, please contact the SMRITI Helpdesk at **support@aitdl.com**.

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