---
Document ID: "ADMIN-007"
Title: "SMRITI OS Go-Live Readiness Checklist Guide"
Owner: "Administration Team"
Audience: "Administrator"
Module: "Core"
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

# SMRITI OS Go-Live Readiness Checklist Guide

This guide describes how to verify store setup parameters, interpret the Go-Live dashboard, and resolve critical deployment blockers.

## 📊 The Readiness Dashboard

The SMRITI Go-Live Readiness Checklist is a central validation page located under:
```text
http://localhost:8765/smriti-go-live
```
It runs 14 real-time checks grouped by operational area and calculates a **Readiness Score** representing the percentage of passed criteria.

---

## 🚦 Status Indicators

Each validation checklist row displays a status indicating its operational impact:

### 🟢 PASS (Passed)
- **Impact**: Criteria met successfully.
- **Example**: Active SMRITI License key detected, default company configured, at least 5 sellable products found.

### 🟡 WARN (Warning)
- **Impact**: System can go live, but functionality will be degraded.
- **Example**: GST/Tax templates are missing (tax won't calculate at registers), or fewer than 5 items are found in the catalog.

### 🔵 INFO (Information)
- **Impact**: Non-blocking recommendation.
- **Example**: Backup Encryption Settings not found. (Enterprise recommendation, but doesn't prevent register transactions).

### 🔴 FAIL (Failed Blocker)
- **Impact**: **BLOCKS GO-LIVE**. The overall site status is set to `NOT READY`, preventing release certification.
- **Example**: 0 sellable items in the Product Catalogue, 0 warehouses configured, or no active POS Profiles.

---

## 🛠️ Resolving the Catalogue Blocker

If the Product Catalogue check fails with `"No sellable items found"`:
1. Ensure you have created or imported at least **5 active items**.
2. Verify that **Disabled = No**, **Is Sales Item = Yes**, and **Maintain Stock = Yes**.
3. Create prices under the **Standard Selling** and **MRP** price lists for each item.
4. Click `Re-run Checks` in the Go-Live dashboard topbar to refresh the score.

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