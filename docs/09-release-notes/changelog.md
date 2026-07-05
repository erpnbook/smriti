---
Document ID: "REL-008"
Title: "SMRITI Retail OS — Customer Changelog"
Owner: "Release Team"
Audience: "Executive / Team"
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

# SMRITI Retail OS — Customer Changelog

This document logs customer-facing updates, bug fixes, and feature releases for SMRITI Retail OS.

---

## [v1.1.0-beta] — 2026-06-18

### 🚀 Major Features
- **Customer Growth Engine (CGE) v1.0**: Dynamic priority-based stacking rules (Exclusion, Multipliers, Bonus Points, Caps), two-phase coupon campaign budget reservations, and immutable wallet ledgers with double-entry accounting.
- **CGE Documentation**: Centralized knowledge base modules, FAQs, and troubleshooting runbooks for customer loyalty operations.

---

## [v1.0.0-GA] — 2026-06-18

### 🚀 Major Features
- **Go-Live Readiness Checklist**: Interactive dashboard (`/smriti-go-live`) validating licensing, store warehouses, users, price lists, customer records, and outgoing emails before production launch.
- **SMRITI Help Center**: Task-based operational guides and FAQs integrated directly at `/smriti-help`.
- **Manager Override PIN Security**: 4-6 digit POS verification codes hashed and stored securely inside the database, complete with Redis rate-limiting (max 5 attempts per 10 minutes).
- **GPG Backup Encryption**: AES-256 GPG-symmetric encryption with dual-custodian key split, sending split fragments to authorized emails during database backup.
- **Post-Migrate Health Check**: Automated diagnostics validating database registry, custom fields, fixtures, and settings parameters.

### 🐛 Bug Fixes
- **Go-Live UI CSRF Fix**: Resolved `CSRFTokenError` on the Go-Live page by updating template contexts to retrieve standard session tokens via `frappe.sessions.get_csrf_token()`.
- **Catalogue Check Seeding**: Fixed checklist blocks on blank database setups by seeding 5 compliant items with HSN codes (`640399`) and mapping default GST templates.
- **Role Redirection**: Corrected setup wizard loops by redirecting administrative paths to `/app/smriti-dashboard` for all store cashiers.

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
---

## [v2.0.0] — 2026-07-02 — Platform Expansion

### 🆕 Added
- **Purchase Studio**: Full PO → GRN → Invoice → Returns lifecycle at `/smriti-purchase`.
  - 18 whitelisted API endpoints in `purchase_api.py`
  - SMRITI Purchase Settings DocType (approval threshold, LC rule, invoice policy)
  - SMRITI Purchase Audit Log DocType
- **Purchase Analytics Studio**: 6 purchase reports (purchase_order_summary, grn_register, purchase_invoice_register, supplier_purchase_summary, item_wise_purchase, purchase_return_register)
- **UIE Universal Integration Engine**: TallyPrime bidirectional sync at `/smriti-uie`
  - Standard Connectivity Framework (SCF): BaseAdapter, TallyAdapter, SyncCoordinator
  - 5 new DocTypes: SMRITI UIE Integration, Credential, Endpoint, Sync Log, Sync Queue
  - DB index on idempotency_key for duplicate-safe dispatch
- **SNM Navigation Manager**: Database-driven nav with Redis caching, 6 new DocTypes
- **SNSM Negative Stock Engine**: Policy-based detection and recovery, 4 new DocTypes
- **SMRITI Analytics Studio (SAS) v1.0**: SQL report engine, catalog, REPORT_QUERIES
- SMRITI Barcode Settings → migrated to file-backed DocType
- SMRITI Telemetry Event Definition → migrated to file-backed DocType
- SMRITI Print Template → migrated to file-backed DocType with unit tests
- Advanced PWA v2: IndexedDB, background sync, push notifications
- SMRITI Print Modal for universal debranded print routing

### 🔄 Changed
- Theme system: `smriti_tokens.css` as single canonical token registry
- `sleek-compact` as canonical theme fallback (THEME-005, all pages)
- Barcode Studio: 4-step style resolution priority
- `token_loader` included in all www pages (global favicon + theme coverage)
- Sidebar: 37KB inline CSS duplication eliminated; background token aligned

### 🐛 Fixed
- `frappe.client` calls removed from all HTML pages (SPC Rule 6 compliance)
- Frappe v16 whitelist test detection corrected
- prnContent dict extraction in USB/LAN/download barcode flows
- `initUIEngine` reliability via token_loader (65 pages)
- HTTP status validation in fetch API helper (all www templates)
- CSRF stale token handling in sw.js
- Barcode DocType query: Item Attribute → Item Variant Attribute
- `backup()` deprecated `with_files` param resolved; root Item Group seeded
- SMRITI bag icon replaces default Frappe logo on login/setup pages
- Purchase sidebar 404 routes resolved
- `smriti-home.html` `/app/smriti-*` route dependency eliminated

### ⚡ Performance
- UIE payload builder decoupled from full document requirements (N+1 eliminated)

---
