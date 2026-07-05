---
Document ID: "PROD-005"
Title: "Development Roadmap: SMRITI Retail OS"
Owner: "Product Team"
Audience: "Product / Executive"
Module: "CGE"
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

# Development Roadmap: SMRITI Retail OS

## 1. Top 20 Improvements Matrix
Ranked by business value and ROI.

| # | Improvement | Category | Impact | Effort | Risk | ROI |
|---|---|---|---|---|---|---|
| 1 | **Secure Secret Management** | Security | Critical | Low | Low | Infinite |
| 2 | **Standardize Schema to JSON** | Architecture | High | Med | Med | High |
| 3 | **Dedicated POS PIN Field** | Security | High | Low | Low | High |
| 4 | **Redis-Cached Stock Lookups** | Performance | High | Med | Low | High |
| 5 | **Replace JSON Blobs with Child Tables** | Architecture | Med | Low | Low | High |
| 6 | **Offline Resiliency (PWA/Service Workers)**| Reliability | High | High | Med | High |
| 7 | **Comprehensive API Unit Testing** | Stability | High | Med | Low | Med |
| 8 | **Async/Incremental Asset Sync** | Performance | Med | Med | Low | Med |
| 9 | **Remove Hardcoded Role Strings** | Architecture | Med | Low | Low | Med |
| 10 | **AI Inventory Predictor (ML Integration)** | Innovation | High | High | High | Med |
| 11 | **Smart Barcode Resolver (Fuzzy Search)** | UX | Med | Med | Low | Med |
| 12 | **JWT Authentication for Billing Terminal** | Security | High | High | Med | Med |
| 13 | **Automated Cloud Backups (S3/Azure)** | Reliability | Med | Med | Low | Med |
| 14 | **POS Audit Trail Expansion** | Governance | Med | Med | Low | Med |
| 15 | **Dark Mode / Dynamic Theming** | UX | Low | Low | Low | Low |
| 16 | **Biometric Manager Override** | Security | Med | High | Med | Low |
| 17 | **Developer CLI Tooling** | DX | Low | Low | Low | Med |
| 18 | **Multi-Currency Standardization** | Expansion | Low | Med | Low | Low |
| 19 | **Sales Invoice UI Event Logging** | Audit | Med | Low | Low | Med |
| 20 | **Frappe v16 Regression Testing** | Stability | Critical | Med | Low | N/A |

## 2. 12-Month Implementation Timeline

### Phase 1: SFM & SFC Stabilization (Months 1-2)
- **Month 1**: Deploy SFM Phase 1 & SFC Phase 1 to UAT. Enforce target split invariant validation (`sum = 100`).
- **Month 2**: 30-60 days UAT observation run. Validate attribution accuracy, split rules, commission payouts, and settlement workflow.

### Phase 2: Walk-In Intelligence (Months 3-4)
- **Month 3**: Implement `SMRITI Walk-In Event` and `SMRITI Walk-In Counter` DocTypes for visitor tracking.
- **Month 4**: Deploy `SMRITI Conversion Snapshot` and compile conversion KPIs: `Conversion % = Bills / Walk-Ins * 100`, Store Conversion, and Employee Conversion.

### Phase 3: Clienteling Engine (Months 5-6)
- **Month 5**: Implement the read-only `SMRITI Customer Profile` DocType mapping sales history, returns, CGE loyalty, and attribution records.
- **Month 6**: Extract and display derived metrics (Preferred Brand/Category/Size/Color, Favorite Executive, Visit Frequency, and Average Basket Value).

### Phase 4: PDT Integration (Months 7-8)
- **Month 7**: Connect PDT (Product Digital Twin) next-purchase predictions with SMRITI Customer Profile.
- **Month 8**: Integrate clienteling profiles directly into POS checkout lanes to display high-confidence purchase recommendations to cashiers.

### Phase 5: Relationship Performance (Months 9-10)
- **Month 9**: Deploy executive performance metrics: Relationship Revenue Index, Retention Influence Score, and Growth Contribution.
- **Month 10**: Rollout leaderboards and executive-specific KPIs to the SFM/SFC Studio.

### Phase 6: Long-Term Gamification & AI Copilot (Months 11-12)
- **Month 11**: Rollout gamification badges (Top Seller, Retention Champion) and incentive campaigns linked to CGE rewards.
- **Month 12**: Launch the AI Retail Copilot architecture seamlessly connecting PDT prediction, Clienteling profiles, POS recommendations, and CGE rewards.


## 3. Immediate "Quick Wins"
1. **Security Patch**: Move the DB password from `pwd.yml` to an `.env` file (Effort: < 1 hour).
2. **UX Fix**: Implement the 4-digit PIN override in `billing_api.py` (Effort: 1 day).
3. **Architecture Fix**: Run `bench export-fixtures` or manually create the JSON files for current custom DocTypes (Effort: 1 day).

## 4. Barcode Studio Quality Engineering Roadmap

To maintain strict alignment with the SMRITI Governance Framework and the AITDL constitution, the Barcode Studio roadmap is structured as a sequential quality engineering capability:

- **Phase 3A: Design Quality Intelligence (Completed)**: Configurable Quiet Zone expansions, Virtual HRT bounds validation, and Printability Score Engine (`SMRITI-PRN-SCORE-01`).
- **Phase 4: Operational Telemetry Intelligence (ACP-BARCODE-002A) (Completed)**: Standalone scan telemetry collection pipeline, Scan Reliability Score (`SMRITI-SCAN-REL-01`), governance event IDs (`SCAN-EVT-001/002/003`), and 90-day retention cleanup.
- **Phase 4.1: Barcode Studio Ergonomics & Warehouse Workflow Suite (Completed)**: Widescreen 3-panel UI, Article Range Loader, variant expansion, transaction expansion modal, live mapping preview, box/carton quantity rules, price fallback rules, and reprint queue.
- **Phase 5: Predictive Barcode Twin (ACP-BARCODE-002B)**: Downstream machine learning loops (PDT) correlating design-time layouts with real-world physical scan performance.

---
*Roadmap generated based on architectural audit of D:\Smriti_Retail_OS.*



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