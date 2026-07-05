---
Document ID: "PROD-006"
Title: "SMRITI Enterprise Readiness Report"
Owner: "Product Team"
Audience: "Product / Executive"
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

# SMRITI Enterprise Readiness Report

## 1. Executive Summary
SMRITI Retail OS demonstrates high readiness for medium-sized retail operations (1-20 stores) due to its specialized Experience and Governance layers. However, the transition to Enterprise (100+ stores) reveals critical single-points-of-failure in orchestration and recovery logic that must be addressed to prevent multi-store outages.

## 2. Scalability Architecture
### 2.1 Current State
- **Monolithic Site Strategy**: The system relies on a single Frappe site ("frontend") for all stores.
- **Bottleneck**: Background workers (`queue-long`, `queue-short`) will experience severe lag when processing simultaneous Day-Close summaries for 100+ stores.
- **Scaling Risk**: The `sync_assets.py` physical copy strategy, while reliable for stability, adds significant IO overhead to shared volumes during multi-container scaling.

## 3. Critical Redesign Requirements
### 3.1 P0: Decoupled Site Management
- **Issue**: Site-wide configuration (`smriti_backup_settings`) is stored in `frappe.db.get_default`.
- **Scalability Constraint**: Prevents store-specific backup schedules or recovery windows.
- **Fix**: Move all SMRITI settings to a per-site or per-store DocType immediately.

### 3.2 P1: Multi-Tenant Worker Separation
- **Issue**: All store material transfers and billing submissions share the same Redis queues.
- **Enterprise Risk**: A single store's large inventory sync can delay billing for the entire franchise.
- **Fix**: Redesign to utilize Frappe's multi-tenant worker capability.

## 4. Operational Breakdown Risks (Scale 100+)
| Component | Failure Trigger | Impact | Redesign Priority |
|---|---|---|---|
| **Asset Sync** | High-frequency container restarts | Nginx 502/404 for all stores | P2 |
| **Stock API** | Concurrent `tabBin` SUM queries | High DB CPU utilization | P1 |
| **Backup API** | Simultaneous multi-gigabyte uploads | Network saturated / Billing lag | P0 |

---
*Reference: SMRITI Platform Logic, `billing_api.py`, `sync_assets.py`*


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