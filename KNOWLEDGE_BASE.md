# 📚 SMRITI Retail OS — Knowledge Base

> **Single-source overview.** This document is the entry point to all project documentation, completed features, open risks, architecture decisions, and operational runbooks.  
> **Author:** Jawahar R Mallah (<jawahar.mallah@gmail.com>)  
> **Last Updated:** 2026-07-06 · **Version:** v2.1.4

> [!TIP]
> Keep this document updated after any development session to keep the knowledge base current.

---

## 🗺️ Table of Contents

1. [What is SMRITI Retail OS?](#1-what-is-smriti-retail-os)
2. [Stack & Architecture](#2-stack--architecture)
3. [Repository Structure](#3-repository-structure)
4. [Documentation Index](#4-documentation-index)
5. [Completed & Locked Features](#5-completed--locked-features)
6. [Open Risk Register](#6-open-risk-register)
7. [Development Roadmap Summary](#7-development-roadmap-summary)
8. [Operational Runbooks](#8-operational-runbooks)
9. [Key API Reference](#9-key-api-reference)
10. [Testing & QA](#10-testing--qa)
11. [Deployment & Infrastructure](#11-deployment--infrastructure)
12. [PSV Phase 1.1 — Channel Intelligence](#12-psv-phase-11--channel-intelligence)
13. [Label Studio V2.1 — Async Print Queue](#13-label-studio-v21--async-print-queue)
14. [Backup Encryption & Dual Custody (v1.8.3)](#14-backup-encryption--dual-custody-v183)
15. [Sidebar v1.9.1 — Data-Driven Nav & Routing Governance](#15-sidebar-v191--data-driven-nav--routing-governance)
16. [Audit Reports Module — Security and Audit Logs (v1.9.2)](#16-audit-reports-module--security-and-audit-logs-v192)
17. [Drag-and-Drop reporting and dashboard customization suite (v1.9.3)](#17-drag-and-drop-reporting-and-dashboard-customization-suite-v193)
18. [Customer Growth Engine V2 — Architecture & Pilot (v2.0.0)](#18-customer-growth-engine-v2--architecture--pilot-v200)
19. [SMRITI CGE Explorer & Generic CRUD Console (v2.0.1)](#19-smriti-cge-explorer--generic-crud-console-v201)
20. [SMRITI PWA Activation & Offline-First POS Integration (v2.1.0)](#20-smriti-pwa-activation--offline-first-pos-integration-v210)
21. [SMRITI Knowledge Governance Framework (KGF) & registries (v2.2.0)](#21-smriti-knowledge-governance-framework-kgf--registries-v220)
22. [SMRITI Predictive Hub & CGE Sidebar Integration (v2.2.1)](#22-smriti-predictive-hub--cge-sidebar-integration-v221)
23. [SMRITI Barcode Studio V2.4a Layout & Operations Upgrade (v2.4.0)](#23-smriti-barcode-studio-v24a-layout--operations-upgrade-v240)
24. [SMRITI Barcode Scan Telemetry Collection Framework (v2.4.0)](#24-smriti-barcode-scan-telemetry-collection-framework-v240)
25. [SMRITI Landed Cost Allocation Module (v2.5.0)](#25-smriti-landed-cost-allocation-module-v250)
26. [SMRITI Reporting Governance & Security Auditing Framework (v2.5.0)](#26-smriti-reporting-governance--security-auditing-framework-v250)
27. [SMRITI Sales Force Management & Commission Module (v2.6.0)](#27-smriti-sales-force-management--commission-module-v260)
28. [SMRITI Customer Intelligence Graph (CIG) (v2.7.0)](#28-smriti-customer-intelligence-graph-cig-v270)
29. [SMRITI Billing Terminal & Theme Hardening (v2.8.0)](#29-smriti-billing-terminal--theme-hardening-v280)
30. [SMRITI Royal Black and White Theme & Contrast Hardening (v2.8.1)](#30-smriti-royal-black-and-white-theme--contrast-hardening-v281)

---


## 1. What is SMRITI Retail OS?

**SMRITI Retail OS** is a premium retail experience layer built on top of **Frappe v16** and **ERPNext v16**. It acts as a _Sophisticated Experience Layer_ (SEL) — transforming the complex ERPNext UI into a cashier-friendly, India GST-compliant POS and merchandising platform tailored for multi-industry businesses (Footwear, FMCG, Garments, etc.).

### Core Value Proposition

| Layer | Description |
|---|---|
| **POS Billing Terminal** | High-performance, role-locked cashier interface with barcode scanning, hold/recall, manager overrides |
| **Sizewise Item Master** | Pivot-grid Excel import for style × size × color variant management |
| **SMRITI Pure Retail Mode** | Hides ERPNext desk complexity from cashiers while preserving full ERPNext for admins |
| **India GST Compliance** | Integrated with `india_compliance` for HSN auto-detection, GSTIN validation, and tax templates |
| **Supplier Registry** | Complete vendor management with GST address syncing and Vendor Code validation |
| **B2B Invoice (Sizewise)** | Pivot-grid B2B invoice creation with HID barcode scanner support |
| **PSV-Prime Engine** | **Flagship Module**: Business-Type Activated Core Extension for Party Stock Visibility (PSV). Reclassified from add-on to core industry extension. | [PSV_PRIME_MANUAL.md](C:/Users/netma/.gemini/tmp/smriti-retail-os/memory/PSV_PRIME_MANUAL.md) |

---

## 2. Stack & Architecture

```
┌───────────────────────────────────────────────────────────────┐
│  SMRITI Retail OS  (Custom Frappe App — smriti_retail_os)     │
│  ┌────────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │ billing_api│  │item_master_api│  │ psv_ledger_service   │  │
│  │ shift_api  │  │barcode_api    │  │ psv_upload_service   │  │
│  │ security_api│  │ company_api  │  │ psv_analysis_service │  │
│  └────────────┘  └───────────────┘  └──────────────────────┘  │
├───────────────────────────────────────────────────────────────┤
│  ERPNext v16 + Frappe v16 + India Compliance v16              │
├───────────────────────────────────────────────────────────────┤
│  MariaDB  │  Redis (Queues + Cache)  │  Nginx (Asset Guard)   │
├───────────────────────────────────────────────────────────────┤
│  Docker Compose (pwd.yml)  ·  9 Containers                    │
└───────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Rationale | Reference |
|---|---|---|
| **Architecture Directive** | Locked `GEMINI.md` mandating ERPNext as the System of Record and SMRITI as the Experience Layer. Enforces Service-First design and forbids raw DB writes from UI. | [GEMINI.md](file:///d:/Smriti_Retail_OS/GEMINI.md) |
| **Industry Configuration Layer** | Multi-industry support via `custom_business_type` setting. Dynamically toggles features (e.g., hides PSV for Footwear, enables for FMCG) to maintain a single core codebase. | [company_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/company_api.py), [smriti_sidebar_standalone.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/public/js/smriti_sidebar_standalone.js) |
| **PSV 3-Layer Sub-Ledger** | Robust 3-layer architecture: Layer 1 (Customer custom fields), Layer 2 (PSV Transaction Engine), Layer 3 (High-speed PSV Balance Table). | [psv_ledger_service.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/psv_ledger_service.py) |
| **HSN-First GST Architecture** | `gst_hsn_code` is the primary source of truth for GST %. `custom_gst_percentage` is auto-derived via the lookup chain. | [hooks_logic.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/hooks_logic.py) — `get_gst_rate_from_hsn()` |
| **Dynamic State Fallback** | Address state resolution reads `Company.state` instead of hardcoded strings — ensures correct CGST/SGST splits. | [hooks_logic.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/hooks_logic.py) — `_get_company_state_fallback()` |
| **Physical Asset Sync** | Unlinks symlinks and hard-copies compiled bundles to Nginx shared volume. | [sync_assets.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/sync_assets.py) |
| **ERPNext-First Data** | Company/Address/Supplier data lives in standard ERPNext DocTypes; SMRITI reads/writes through standard APIs. | [company_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/company_api.py) |
| **Role-Based Routing** | Cashiers hit `/billing`; System Managers see unaltered ERPNext desk. | [hooks.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/hooks.py) |
| **Metadata-Driven Reporting Engine** | `SMRITIReportEngine` uses `SMRITI Report Template` DocType + dynamic SQL builder with MD5 caching + Redis TTL. | [reports_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/reports_api.py) |
| **Hashed POS Manager PIN Override** | Store manager override PINs are stored securely in `custom_smriti_pin` using `update_password` hashing, rather than raw text or primary passwords, avoiding shoulder-surfing risks. | [test_billing_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/tests/test_billing_api.py) |
| **Stock Reconciliation Fields** | ERPNext maps the difference account to `expense_account` (labeled "Difference Account" in UI). Specifying `difference_account` is ignored, falling back to P&L defaults and causing opening entry balance sheet errors. | [inventory_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/inventory_api.py) |
| **Negative Balance Exception Logs** | Invoices/dispatches cancellation reversing shadow ledger entries must log a `SMRITI PSV Exception Record` and update status if it results in negative stock balances. | [smriti_psv_transaction.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_psv_transaction/smriti_psv_transaction.py) |
| **Backup Storage Security** | Backup files (`.gz`/`.tar`) are stored in `private/backups` where Nginx blocks direct public HTTP access. Downloads require a valid System Manager/Administrator session. Cloud sync utilizes encrypted TLS tunnels and S3 KMS-based encryption-at-rest. | [backup_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/backup_api.py) |
| **v1.8.2a Protected Config Denylist** | `PROTECTED_CONFIG_PATTERNS` in `security_constants.py` defines glob patterns (e.g. `*site_config*.json`, `*.key`, `*.pem`, `*.p12`) that are filtered out of all backup history listings and intercepted at the `before_request` level in `boot.py`. Any direct `/backups/<protected_file>` download is rejected with `403 PermissionError` and logged to the Activity Log. | [security_constants.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/security_constants.py), [boot.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/boot.py) |
| **v1.8.2a In-Memory Config Export** | `export_site_config()` in `backup_api.py` reads site config, redacts all fields in `SENSITIVE_EXPORT_FIELDS` (replacing values with `"*** REDACTED ***"`), and streams the result as a direct download. No file is ever written to disk. Requires System Manager role + password re-authentication. Guests are rejected before password check. | [backup_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/backup_api.py) |
| **v1.8.2a Fail-Closed Design** | This module follows fail-closed design. Any condition that cannot guarantee security integrity aborts the operation rather than silently degrading. This applies to: Guest session detection, role enforcement, password re-authentication, denylist matching, and audit log writes. | [backup_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/backup_api.py) |
| **Key Recovery (v1.8.3 scope)** | Dual-custodian key recovery is **UNBLOCKED for v1.8.3**. Architecture (post-review 2026-06-10): All Key Recovery UI lives inside the existing `/backup` page under a new **"Backup Security"** section — same Navy sidebar, SMRITI cards, SMRITI modals. **No separate page. No Frappe Form. No List View.** `SMRITI Key Custodian` DocType stores metadata only (email, verified, dates, status, hashed OTP, and 15-minute OTP expiry) — no key fragments. Key fragments (simple midpoint split) are generated in-memory by `key_recovery_service.py` and sent via email (after verifying SMTP configuration). Key rotation uses versioning in `frappe.conf` and filenames (e.g. `*-v[version].smriti.enc`) instead of re-encryption. `verify_custodian_emails()` and `send_recovery_key()` stubs in `backup_api.py` will delegate to `key_recovery_service.py`. Feature flag `enable_backup_encryption` controls rollout. | [implementation_plan.md](file:///C:/Users/netma/.gemini/antigravity-ide/brain/26cd6eeb-7016-4a5b-8bfc-ebd3e0c01e3d/implementation_plan.md) |
| **v1.8.2a Audit Closure Artifacts** | Three governance-quality artifacts captured on 2026-06-10: (1) Exported JSON showing `db_password → *** REDACTED ***`; (2) `ls private/backups/ \| grep site_config` → exit 1, zero results, confirming no file is written to disk during export; (3) `setup_activity_log_options()` idempotency verified — calling twice produces exactly one entry each for `"Blocked Download Attempt"` and `"Config Exported"`. | [walkthrough.md](file:///C:/Users/netma/.gemini/antigravity-ide/brain/26cd6eeb-7016-4a5b-8bfc-ebd3e0c01e3d/walkthrough.md) |
| **Label Studio Realtime Updates (V2.2)** | Switched printer queue dashboard updates from polling to namespaced Socket.io events (`smriti.barcode.print_status`). Restricts event delivery to `user=doc.requested_by` to prevent cross-user leakage in multi-cashier environments. Captures operator IP and user agent in `SMRITI Print Job` for auditing. | [barcode_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/barcode_api.py), [barcode.html](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/www/barcode.html) |
| **Print Template Versioning & Lock (V2.3)** | Created separate parent DocType `SMRITI Print Template Version` to store history snapshots. Computes SHA-256 checksums on template contents + mappings + layouts on save, and enforces optimistic locking (`expected_checksum`) during version restore to prevent concurrent overwrite conflicts. | [smriti_print_template.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_print_template/smriti_print_template.py), [barcode_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/barcode_api.py) |
| **Visual Designer & DPI Portability (V2.4a/b)** | Added tab-navigation layout editor. Stores elements as JSON coordinates (mm-based, 1mm = 8px on screen). Converts mm coordinates to ZPL/TSPL dots at compile time (`dots = mm * dpi / 25.4`). Handles versioned metadata wrappers (`layout_version: 1`, `compiler_version: 1`) with backward compatibility for unwrapped layouts. Blocks canvas editing for legacy/raw templates. Supports client-side undo/redo (20 states). | [barcode.html](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/www/barcode.html) |
| **Pre-Print Validation Engine & SVG Preview (V2.5)** | Replaced div preview with high-fidelity vector SVG preview. Simulates DPI grid and renders mock barcodes/QR codes/images. Added diagnostics validation (blocking errors for absolute boundary breaches, print-safe margin incursions on barcodes/QRs, and non-decorative element collisions; warnings for text overflow and text/image margin incursions). | [barcode_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/barcode_api.py), [barcode.html](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/www/barcode.html) |
| **PSV Hook Resolution (F1)** | Migrated `psv_integration.py` to the top-level app package to resolve `hooks.py` imports, implemented full Delivery Note and Stock Entry event hooks, and deprecated the legacy nested stub module with warnings and dynamic re-exports. | [psv_integration.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/psv_integration.py) |
| **SMTP Credential Security (F3)** | Replaced plain-text SMTP password storage in the JSON default settings blob with Frappe's secure AES-encrypted store (`tabPassword` via `frappe.utils.password`). Integrated an idempotent migration helper. | [backup_api.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/backup_api.py) |
| **PSV Distributed Lock (F4)** | Closed concurrent sales upload balance-check race windows using a per-PSA Redis context manager lock (`frappe.cache().set` with `SET NX EX`). | [psv_service.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/psv_service.py) |
| **Transaction Kernel Invariant (F5)** | Documented the `ignore_permissions=True` kernel persistence bypass, adding a `SECURITY INVARIANT` comment enforcing that user permission gates must precede payload enrichment and saving. | [transaction_kernel.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/transaction_kernel.py) |

### v1.8.3 Security Audit Event Matrix

| Event | Operation | Details |
|---|---|---|
| **Encryption Enabled** | `"Backup Encryption Enabled"` | User who enabled + active key fingerprint |
| **Encryption Disabled** | `"Backup Encryption Disabled"` | User who disabled |
| **Key Rotated** | `"Backup Key Rotated"` | User + old fingerprint + new fingerprint |
| **Custodian Verified** | `"Custodian Verified"` | Custodian email + verification timestamp |
| **Recovery Fragments Sent** | `"Recovery Fragments Sent"` | Masked recipient emails |
| **GPG Missing** | `"GPG Executable Missing"` | Site name + timestamp (Fail Closed trigger) |
| **Encrypted Restore** | `"Encrypted Backup Restored"` | Plaintext filename + user + key version |

Full architecture detail: [ARCHITECTURE_REPORT.md](file:///d:/Smriti_Retail_OS/ARCHITECTURE_REPORT.md)

---

## 3. Repository Structure

```
smriti_retail_os/
├── apps/
│   ├── smriti_retail_os/        ← Main custom app
│   │   └── smriti_retail_os/
│   │       ├── billing_api.py
│   │       ├── item_master_api.py
│   │       ├── psv_service.py          ← Universal Transaction Engine
│   │       ├── reports_api.py          ← SMRITIReportEngine + 20 reports
│   │       ├── hooks.py
│   │       ├── setup.py                ← Seeds DocTypes, custom fields
│   │       ├── www/                    ← Frontend pages (HTML/JS/CSS)
│   │       ├── public/js/              ← Desk overrides & Standalone UI logic
│   │       └── tests/                  ← Test suites
│   └── india_compliance/               ← GST compliance app
├── docs/                               ← VitePress documentation site
├── compose.yaml / pwd.yml              ← Docker Compose orchestration
├── install.ps1 / install.sh            ← Installers
├── GEMINI.md                           ← Locked Architecture Directive
└── KNOWLEDGE_BASE.md                   ← THIS FILE
```

---

## 4. Documentation Index

### Installation & Operations
* [README.md](file:///d:/Smriti_Retail_OS/README.md) - Quick install guide
* [INSTALL.md](file:///d:/Smriti_Retail_OS/INSTALL.md) - Full walkthrough
* [TROUBLESHOOTING.md](file:///d:/Smriti_Retail_OS/TROUBLESHOOTING.md) - Fix guide

### Architecture & Audit
* [GEMINI.md](file:///d:/Smriti_Retail_OS/GEMINI.md) - Locked Architecture Directives
* [SYSTEM_INVENTORY.md](file:///d:/Smriti_Retail_OS/SYSTEM_INVENTORY.md) - Complete system asset map
* [ARCHITECTURE_COMPLIANCE_REPORT.md](file:///d:/Smriti_Retail_OS/ARCHITECTURE_COMPLIANCE_REPORT.md) - Verification of ERPNext boundaries
* [INTEGRATION_AUDIT.md](file:///d:/Smriti_Retail_OS/INTEGRATION_AUDIT.md) - Cross-module pipeline verification
* [PRODUCTION_READINESS.md](file:///d:/Smriti_Retail_OS/PRODUCTION_READINESS.md) - Enterprise safety standards assessment
* [PERFORMANCE_REPORT.md](file:///d:/Smriti_Retail_OS/PERFORMANCE_REPORT.md) - Query/N+1 optimization audit
* [CLEANUP_REPORT.md](file:///d:/Smriti_Retail_OS/CLEANUP_REPORT.md) - Dead code and refactoring log

---

## 5. Completed & Locked Features

| # | Feature | Date | Key Files |
|---|---|---|---|
| 25 | **SMRITI Reporting Framework** | 2026-06-07 | `reports_api.py`, `reports.html` |
| 26 | **Accounting Analytics Extension** | 2026-06-07 | `reports_api.py`, `setup.py` |
| 27 | **P0/P1 Critical Bug Fix Session** | 2026-06-07 | Various APIs |
| 28 | **POS Return Invoice & Purchase Return** | 2026-06-07 | `billing_api.py`, `purchase_api.py` |
| 29 | **UI/UX Deep Audit & Streamlining** | 2026-06-07 | `reports.html`, `AUDIT_CRITIQUE.md` |
| 30 | **SMRITI Party Stock Visibility (PSV) Hardening** | 2026-06-08 | `psv_service.py`, `test_psv.py` |
| 31 | **PSV Production Hardening v1.2** | 2026-06-09 | `psv_service.py`, `psv_reorder_report.py` |
| 32 | **PSV Phase 3: Reporting & Wizard (v1.4)** | 2026-06-09 | `opening_balance.py`, `psv_party_stock_balance.py` |
| 33 | **PSV 3-Layer Sub-Ledger Engine** | 2026-06-09 | `smriti_psv_transaction.py`, `psv_service.py` |
| 34 | **Industry Config Layer (Multi-Business Type)** | 2026-06-09 | `company_api.py`, `smriti_sidebar_standalone.js` |
| 35 | **Architecture & Production Audit (5-Phase)** | 2026-06-09 | `ARCHITECTURE_COMPLIANCE_REPORT.md` |
| 36 | **Test Suite Hardening & Core Alignments (v1.6.1)** | 2026-06-09 | test_billing_api.py, inventory_api.py, smriti_psv_transaction.py |
| 37 | **Setup Wizard Improvements & Compliant Routing (v1.7.0)** | 2026-06-10 | `setup_wizard_api.py`, `setup_wizard.html` |
| 38 | **Global Branding Locks & Branded Error Overrides (v1.8.0)** | 2026-06-10 | `test_branding_integrity.py`, `hooks.py`, `404.html`, `403.html` |
| 39 | **Secure Backup Download Routing Fix (v1.8.1)** | 2026-06-10 | `backup.html`, `platform_center.html`, `smriti_backup.js` |
| 40 | **Backup Security Design documentation (v1.8.2)** | 2026-06-10 | `KNOWLEDGE_BASE.md` |
| 41 | **P0 Security Hotfix — Protected Config Denylist, Export Redaction, Boot Guards (v1.8.2a)** | 2026-06-10 | `security_constants.py`, `backup_api.py`, `platform_api.py`, `boot.py`, `test_backup_security_hotfix.py` |
| 42 | **v1.8.2a Governance Closure — Audit Artifacts Archived** | 2026-06-10 | `walkthrough.md` — exported JSON redaction sample, `private/backups` listing (zero `site_config` results), Activity Log migration idempotency PASS |
| 43 | **v1.8.3 Backup Encryption — Implementation Plan Created** | 2026-06-10 | `implementation_plan.md` — AES-256-GCM encryption service, dual-custodian key recovery, SMTP verification, `/smriti-key-recovery` SMRITI page, tests 9–12 |
| 44 | **SMRITI Label Studio V2.2/V2.3/V2.4a/b (Sockets, Version History, Designer & Metadata Wrappers)** | 2026-06-10 | `barcode_api.py`, `smriti_print_template.py`, `barcode.html`, `test_barcode_api.py` |
| 45 | **SMRITI Label Studio V2.5 (Preview & Pre-Print Validation Engine)** | 2026-06-11 | `barcode_api.py`, `test_barcode_api.py`, `barcode.html` |
| 46 | **SMRITI Retail OS Audit Remediation (PSV Hooks, SMTP Encryption, Redis Locking, Permission Gate)** | 2026-06-11 | `psv_integration.py`, `backup_api.py`, `psv_service.py`, `transaction_kernel.py`, `test_audit_remediation.py` |
| 47 | **SMRITI PSV Custom Shadow Ledger, Caching, and Core APIs (v1.9.0-GA)** | 2026-06-11 | `psv_service.py`, `balance_engine.py`, `psv_api.py`, `psv-dashboard.html`, `smriti_sidebar_standalone.js` |
| 48 | **PSV Phase 1.1 Validation & Staged Pilot Distributor Program** | 2026-06-11 | `seed_psv_uat.py`, `pilot_execution_plan.md`, `pilot_executive_summary.md` |
| 49 | **SMRITI Audit Reports Module (v1.9.2)** | 2026-06-16 | `reports_api.py`, `setup.py`, `reports.html`, `smriti_nav_config.js`, `coming_soon_api.py` |
| 50 | **Drag-and-Drop reporting and dashboard customization suite (v1.9.3)** | 2026-06-17 | `reports.html`, `psv-dashboard.html`, `smriti-home.html`, `test_reports.py` |
| 51 | **SMRITI Customer Growth Engine (CGE) v2 (v2.0.0)** | 2026-06-19 | `migrate_cge_to_v2.py`, `cge_v2_constraints.sql`, `test_cge_v2_constraints.py`, `cge_v2_activation_runbook.md`, `cge_v2_pilot_execution_report.md` |
| 52 | **SMRITI PWA Activation & Offline-First POS Integration (v2.1.0)** | 2026-06-19 | `sw.js`, `manifest.json`, `offline-pos.html` |
| 53 | **SMRITI Knowledge Governance Framework (KGF) & registries (v2.2.0)** | 2026-06-19 | `smriti-help.html`, `smriti-dictionary.html`, `smriti-formula-registry.html` |
| 54 | **SMRITI Predictive Hub & CGE Sidebar Integration (v2.2.1)** | 2026-06-19 | `pdt_dashboard.py`, `smriti_nav_config.js` |
| 55 | **Production Hardening, Python 3.14 Compatibility & Branding (v2.2.2)** | 2026-06-20 | `test_license.py`, `smriti-formula-registry.html`, `smriti-dictionary.html` |
| 56 | **SMRITI Barcode Studio V2.4a Layout & Operations Upgrade (v2.4.0)** | 2026-06-21 | `barcode.html`, `barcode_api.py`, `test_barcode_api.py` |
| 57 | **SMRITI Barcode Scan Telemetry Collection Framework (v2.4.0)** | 2026-06-21 | `barcode_api.py`, `test_telemetry.py`, `seed_telemetry_meta.py` |
| 58 | **SMRITI Landed Cost Allocation Module (v2.5.0)** | 2026-06-25 | `landed_cost.py` |
| 59 | **SMRITI Purchase Matrix Optimizations & Supplier Auto-Sync Bridge (v2.1.1)** | 2026-07-06 | `matrix_service.py`, `hooks_logic.py`, `test_purchase_matrix.py` |
| 60 | **SMRITI Licensing Migration to GPL-3.0-only (v2.1.2)** | 2026-07-06 | `LICENSE`, `COPYING`, `NOTICE`, `THIRD_PARTY_LICENSES.md` |
| 61 | **SMRITI Security Permission Audit & Custom Field Setup (v2.1.4)** | 2026-07-06 | `setup.py`, `test_billing_api.py`, `check_ignore_permissions.py` |

---

## 6. Open Risk Register

| Risk ID | Severity | Title | Status | File |
|---|---|---|---|---|
| **P0-01** | 🔴 Critical | Privilege escalation via Store Manager password reset | ✅ **FIXED** | `security_api.py` |
| **P0-02** | 🔴 Critical | Backup files unencrypted at rest — `site_config` exposure risk | ✅ **FIXED** | `gpg_service.py` (new) |
| **P1-01** | 🟠 High | Manager overrides use primary login password (shoulder-surfing risk) | ✅ **FIXED** | `billing_api.py`, `shift_api.py` |
| **P1-03** | 🟠 High | Email backup fails silently when DB backup exceeds 25MB SMTP limit | **OPEN** | `backup_api.py` |
| **P2-01** | 🟡 Medium | `sync_assets.py` uses `shutil.rmtree` — not atomic | ✅ **FIXED** | `sync_assets.py` |

---

## 7. Development Roadmap Summary

### Phase 1 — Footwear Pilot & PSV Phase 1.1 GA (CLOSED)
- ✅ Deploy to Client #1 (Footwear Retailer)
- ✅ Modules Active: Billing, Inventory, Masters, Loyalty, Reports, Day End, PSA, PSV, Sales Uploads, Physical Audits, Reorder Engine
- ✅ **v1.9.0-GA General Availability Released (2026-06-11)** — Successfully completed UAT validation and Pilot Distributor Program (1 Distributor, 5 Dealers, 4 Weeks) with 91% user acceptance score and 85.87% alert precision.

### Governance Status

```text
v1.8.2a       CLOSED ✅  8 tests
v1.8.3        CLOSED ✅  18 tests
Barcode V2.1  TAGGED ✅  25 tests
PSV 1.1       FROZEN ✅  187 tests
PSV 1.2       FROZEN ✅  6 tests
PSV Pilot     ACTIVE 🟡
PSV 1.3       CANDIDATE 🔵
CGE v2 (2.0)  PILOT ACTIVE 🟡  228 tests
```

### Phase 2 — Customer Intelligence Layer & Clienteling (ACTIVE)
- 🔲 **Walk-In Intelligence**: Visitor event tracking and conversion percentage KPIs.
- 🔲 **Clienteling Engine**: Derived customer brand, category, size, and executive preferences at POS.
- 🔲 **PDT POS Integration**: Realtime high-confidence purchase recommendations for cashiers.

### Phase 3 — AI Retail Copilot & Gamification
- 🔲 **Performance Index**: Relationship Revenue Index, Retention Influence Score, and Growth Contribution.
- 🔲 **Gamification**: Leaderboard badges, custom incentive campaigns integrated with CGE.
- 🔲 **AI Copilot**: Full end-to-end retail assistant loop connecting PDT, Clienteling, POS checkout, and CGE.


---

## 8. Operational Runbooks

### Install / Re-Install
**Windows (PowerShell):**
```powershell
git clone https://github.com/erpnbook/smriti-docker.git Smriti9
cd Smriti9
PowerShell -ExecutionPolicy Bypass -File .\install.ps1
```

### Health Check
```powershell
.\check.ps1
```

### Update Application
```bash
cd apps/smriti_retail_os && git pull origin main && cd ../..
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
```

---

## 9. Key API Reference

### Backend Whitelisted Endpoints (Service Layer)

| Endpoint | File | Purpose |
|---|---|---|
| `smriti_retail_os.company_api.get_business_type` | `company_api.py` | Resolves current Industry Type (e.g. Footwear vs FMCG) |
| `smriti_retail_os.psv_service.create_psv_transaction` | `psv_service.py` | Universal Engine for all PSV stock movements |
| `smriti_retail_os.billing_api.submit_bill` | `billing_api.py` | Submit POS Sales Invoice |
| `smriti_retail_os.item_master_api.import_pivot_item_master` | `item_master_api.py` | Pivot-matrix style × color × size import |
| `smriti_retail_os.barcode_api.validate_barcode` | `barcode_api.py` | Validate barcode format and uniqueness |
| `smriti_retail_os.inventory_api.reset_db` | `inventory_api.py` | **Admin Only** - Hard wipe of transactions |
| `smriti_retail_os.backup_api.get_backup_history` | `backup_api.py` | Returns backup archive list — protected files filtered via `PROTECTED_CONFIG_PATTERNS` |
| `smriti_retail_os.backup_api.export_site_config` | `backup_api.py` | System Manager + password re-auth required. Streams redacted config JSON in-memory. No disk write. |
| `smriti_retail_os.backup_api.log_audit_event` | `backup_api.py` | Internal helper — writes to Frappe Activity Log. Never raises on failure. |
| `smriti_retail_os.backup_api.get_encryption_status` *(v1.8.3)* | `backup_api.py` | Returns `{key_present, gpg_available, custodians_set, encryption_enabled}` for recovery dashboard |
| `smriti_retail_os.barcode_api.get_print_template_versions` | `barcode_api.py` | Returns linked version history snapshots for a template |
| `smriti_retail_os.barcode_api.restore_print_template_version` | `barcode_api.py` | Restores template version after validating expected_checksum optimistic lock |
| `smriti_retail_os.barcode_api.enqueue_print_job` | `barcode_api.py` | Enqueues raw printer job, captures user audit details, and publishes Socket.io status updates |
| `smriti_retail_os.barcode_api.validate_layout_diagnostics` | `barcode_api.py` | Validates print template layout and returns diagnostics for margin incursion, collision detection, and text overflow |

*(Note: API calls must comply with Service-First architecture defined in GEMINI.md)*

---

## 10. Testing & QA

### Automated Test Suite
- **Run Command**:
  ```bash
  docker exec smriti_retail-backend-1 bench --site smriti_retail run-tests --app smriti_retail_os
  ```
- **Test Coverage**: 208 passing tests covering core workflows, report engines, PSV Shadow Ledger dispatches and return flows, manager PIN security, e-way bill auditing, SMTP encryption, Redis distributed locking, and printing security controls.
- **Audit Remediation Test Module**: `smriti_retail_os.tests.test_audit_remediation` — 34 tests covering hook paths, encryption roundtrips, Redis locking concurrency, permission gates, and PSV business logic (partial dispatches, amendments, returns, cancel-amend idempotency).
- **Barcode & Studio Test Suite**: `smriti_retail_os.tests.test_barcode_api` — 25 tests covering async print job enqueuing/processing, Socket.io user-scoped targeting, version snapshotting, DPI portable coordinate translation, legacy guards, margin checking, text overflow, element collisions, and wrapped/unwrapped layout compatibility.
- **Security Test Module**: `smriti_retail_os.tests.test_backup_security_hotfix` — 15 tests for config denylist, 403 enforcement, Activity Log, export redaction, restore cleanup, GPG encryption/decryption, OTP expiration, key splitting, GPG fail-closed behavior, and sidecar verification.

### Cryptographic Brand Enforcement
To prevent unauthorized modification or accidental deletion of corporate branding elements and routing compliance rules, a cryptographic validation suite is integrated into the automated tests (`test_branding_integrity.py`). This suite checks line-ending-normalized SHA-256 hashes of critical files:
- **Global SVG Logos**: `public/images/smriti_logo.svg`, `public/images/logo.svg`, `public/logo.svg`
- **Login Background Wallpaper**: `public/images/login_wallpaper.svg`
- **Login and Error Pages**: `www/smriti-login.html`, `www/404.html`, `www/403.html`, `www/smriti-404.html`, `www/smriti-403.html`
- **Route Integrity**: Verifies that custom routing rules for `/login` -> `smriti-login`, `/404` -> `smriti-404`, and `/403` -> `smriti-403` are registered in `hooks.py`.

---

## 11. Deployment & Infrastructure

### Container Architecture
```
smriti_retail-backend-1     → Frappe/ERPNext app server
smriti_retail-frontend-1    → Nginx (Asset routing)
smriti_retail-websocket-1   → Socket.io for real-time POS
smriti_retail-queue-*       → Background job processing
smriti_retail-db-1          → MariaDB
smriti_retail-redis-*       → Caching & Queues
```

### Versions
| Component | Version |
|---|---|
| SMRITI Retail OS | **v1.8.2a** (closed ✅) → **v1.8.3** (closed ✅) |
| Frappe Framework | **v16** |
| ERPNext | **v16** |
| India Compliance | **v16** |

### v1.8.3 New Files (Planned)
| File | Type | Purpose |
|---|---|---|
| `gpg_service.py` | New service | GPG symmetric encrypt/decrypt using stdin. Key versioning. No Frappe dependency — fully unit-testable. |
| `key_recovery_service.py` | New service | OTP generation (15-min expiry), custodian verification, key fragment dispatch (simple midpoint split) via `frappe.sendmail()`. |
| `SMRITI Key Custodian` DocType | New DocType | Metadata only: email, verified, dates, status, otp_hash, otp_expiry. No key fragments stored. No Frappe UI exposed. |

**UI lives in existing SMRITI pages (no new routes):**
| Page | Change | Description |
|---|---|---|
| `/backup` | Extended | New "Backup Security" section with Encryption Status card + Key Custodians card + SMRITI modals |
| `/platform-center` | Extended | Encryption status widget + custodian count badge |

> [!IMPORTANT]
> `/app/smriti-key-custodian`, Frappe List View, Frappe Form View, and Frappe Workspace are **never exposed**. All custodian management happens through SMRITI cards and modals inside `/backup`.

### Key Version Retention Policy

> [!IMPORTANT]
> **Key Version Retention Policy**: Encryption key versions must not be removed until all backups encrypted using that version have expired according to the configured backup retention policy.
>
> **Example**:
> - Retention Period = 90 days
> - v1 key may only be retired after all v1 backups have been deleted and verified absent.

---

## 12. PSV Phase 1.1 — Channel Intelligence

### Core Architecture & New Tables
- **`PSV Channel Partner`**: Represents retail/distributor locations. Autonaming format `{customer}-{location_name}`. Features a child table `PSV Channel Partner Brand` supporting multi-brand distributor profiles.
- **`PSV Ledger Entry`**: The primary transaction record. Autonaming pattern `PSV-.########` (8-digit sequential numbering).
- **`PSV System Settings`**: A single configuration DocType specifying Weeks of Cover thresholds, snapshot batch size, and redistribution scope.
- **`PSV Stock Aging Snapshot`**: Optimizes dashboard queries to O(1) read performance by caching pre-bucketed aging metrics (`qty_0_30`, `qty_31_60`, etc.).

### Business Rules & Safeguards

> [!IMPORTANT]
> **PSV Ledger Immutability Rule**:
> 1. INSERT operations are allowed.
> 2. UPDATE operations are prohibited.
> 3. DELETE/TRASH operations are prohibited.
> 4. Corrections must be recorded via new reversal entries which invert quantity and reference the original ledger entry name.

- **Landing Cost Lookup Hierarchy**:
  1. Variant Item: `valuation_rate`
  2. Variant Item: `standard_rate`
  3. Variant Item: Standard Buying Price from `Item Price` table
  4. Parent Template Item: `valuation_rate` (if variant_of is set)
  5. Parent Template Item: `standard_rate`
  6. Parent Template Item: Standard Buying Price from `Item Price` table
  7. `0.0` (fallback default)

- **Distributed Locking for Snapshots**:
  `generate_snapshots()` runs incrementally in batches. It enforces a Redis-backed distributed lock with key `smriti:psv:snapshot_generation`. If the lock is present, execution is skipped and a warning is logged.

- **Territory-Aware Redistribution**:
  `get_redistribution_suggestions()` identifies over-stocked (WOC > healthy) and under-stocked (WOC < critical) locations, matching surplus to shortage within the configured geographical scope (Same Territory, Same Region, or All).

- **Backward Compatibility Fallback**:
  All read APIs automatically fall back to legacy `SMRITI Party Stock Account` / `SMRITI Party Stock Ledger Entry` data if the new tables are not yet populated, preventing service disruption during v1.9.x transitions.

### Dashboard Statistics Tuple Fix (v1.9.0-GA-hotfix)
- **Problem**: In `psv_service.py:get_channel_stock_trend()`, the `dates` result returned by `frappe.db.sql` is a tuple. Calling `.reverse()` directly on it caused a runtime `AttributeError: 'tuple' object has no attribute 'reverse'`, blocking the PSV dashboard stats from loading.
- **Resolution**: Cast `dates` to a `list` first (`dates = list(dates)`) before reversing. Verified clean with all 50 test suite runs.

---

## 13. Label Studio V2.1 — Async Print Queue

- **Problem solved**: Gunicorn worker block. Heavy or concurrent printing blocked Gunicorn web workers, causing interface lag. Async queue isolates printing workload.
- **Payload as .prn file — not in DB**: The raw printer payload (ZPL/TSPL) is saved directly to `sites/smriti_retail/private/print_jobs/<job_id>.prn` with restricted `0o600` permissions. No large payload in DB.
- **Job lifecycle**: `Queued` → `Sending` → `Success` / `Failed`.
- **Dedicated barcode queue**: Background workers run on isolated `barcode` queue workload (`barcode: bench worker --queue barcode`).
- **Retention**: Daily cleanup deletes `Success` jobs older than 30 days and `Failed` jobs + payloads older than 90 days.
- **Printer profiles via Company Settings**: Default printer settings (IP, Port, Language, Size) managed centrally per-company in SMRITI Company Settings.
- **Future**: Replace polling with `frappe.publish_realtime()` in V2.2.

---

## 14. Backup Encryption & Dual Custody (v1.8.3)

SMRITI Retail OS v1.8.3 implements a highly secure, fail-closed backup encryption and dual-custodian recovery system.

### Key Capabilities

* **AES-256 Symmetric Encryption**: Database backups are encrypted with GPG using a secure, dynamically generated symmetric key. Passphrases are piped to GPG via stdin to prevent process sniffing.
* **Key Versioning & Rotation**: Old keys are preserved in `site_config.json` inside a dictionary (`backup_encryption_keys`). The active key version (e.g. `v1`, `v2`) is saved as `active_backup_encryption_key_version`. Filenames are postfixed with version (e.g., `-v1.smriti.enc`) and can be decrypted using historical keys, permitting safe key rotation.
* **Fail-Closed GPG Enforcement**: If GPG is missing from the system path, enabling encryption raises a hard error (`RuntimeError`) and aborts configuration changes or backup generation immediately.
* **3-State Security Status Banner**:
  1. **UNENCRYPTED (RED)**: Encryption is disabled. UI displays a warning banner in red.
  2. **ENCRYPTED (AMBER)**: Encryption is enabled, but fewer than two verified custodians are onboarded. UI displays an amber warning.
  3. **ENCRYPTED & SECURED (GREEN)**: Encryption is enabled, and exactly two verified custodians are onboarded.
* **Dual-Custodian Split Key**: Operational control is divided between two custodians. The active encryption key is split at the midpoint (`mid = len(key) // 2`) and fragments are dispatched via email to the verified custodians. This provides strict operational control (not Shamir Secret Sharing).
* **Realtime Restore Progress**: Restore operations broadcast namespaced realtime Socket.io events (`smriti.backup.progress`), updating the cashiers in real-time (`Decrypting backup...`, `Verifying decrypted file...`, `Restoring database...`, `Cleaning temporary files...`, `Restore complete.`).
* **Secure Shred Cleanup**: Temporary files containing decrypted database SQL dumps are securely wiped using `shutil.which("shred")` with parameters `-u -z -n 1`. If `shred` is missing on the system, a zero-overwrite fallback writes null bytes (`b"\x00" * size`) to the file before deletion.

### API & Service Architecture

* **GPG Service**: `gpg_service.py` provides independent symmetric file encryption, decryption, versioned key retrieval, and key fingerprint generation.
* **Key Recovery Service**: `key_recovery_service.py` handles custodian email onboarding, 6-digit OTP verification (15-min expiry), email masking, key splitting, key rotation, and encryption status retrieval.
* **Backup API**: `backup_api.py` orchestrates settings lifecycle, manual backup triggering, cloud sync, SMTP credentials encryption, and secure restoration with outer try-finally shredding.

### Test Numbering and Validation
> [!NOTE]
> **Test numbering**: test_15 not present. Tests jump from test_14 to test_16. test_15 was superseded during development. Not a gap in coverage — all scenarios tested.


---

## 15. Sidebar v1.9.1 — Data-Driven Nav & Routing Governance

SMRITI Retail OS v1.9.1 implements a configuration-driven navigation model and locks down strict routing governance policies to align with enterprise-grade standards.

### Key Capabilities

* **Single Source of Truth (`smriti_nav_config.js`)**: Sidebar navigation has been migrated from hardcoded UI structures to a dynamically resolved JavaScript configuration mapping canonical routes, feature flags, progress values, and ETAs.
* **4-State Navigation Status**: Sidebar items support active resolution, coming soon badges (routing to a parameters-driven Coming Soon page), hidden (fully omitted), and disabled (rendered at 40% opacity with `not-allowed` cursor).
* **Category Auto-Hide Logic**: Section headers automatically hide if all of their children are hidden due to role access checks or feature flags.
* **Dual-Route Resolving**: Sidebar items resolve to canonical `/app/<page-name>` Desk Page routes for Desk users (System Managers/Store Managers) and fall back to standalone website routes (`standalone_route`) for cashiers on standalone terminal interfaces.
* **Routing Governance & Route Consolidation**:
  - Exposing legacy `/page/*` or `/desk/page/*` routes is strictly forbidden.
  - All duplicate/legacy route aliases mapping multiple paths to identical targets have been removed from `hooks.py` to enforce a clean single-canonical route policy.
  - Master AI architecture constitution (`AITDL.md`) and bootstrap instructions (`CLAUDE.md`) are placed at the repository root.

---

## 16. Audit Reports Module — Security and Audit Logs (v1.9.2)

SMRITI Retail OS v1.9.2 introduces the Audit Reports module under a dedicated "SMRITI Audit Reports" category. This module provides a SMRITI-First reporting interface for critical system operations and security logs without exposing raw Frappe desk views.

### Key Capabilities

* **Security Audit Log**: Tracks security-critical events (e.g. login, visual template changes, print queue cleanup) by querying the `tabActivity Log` table.
* **Address Change Log**: Audit trail for updates to company/party address configurations by querying the custom `tabSMRITI Address Audit Log` table.
* **Custom Engine Integration**: Patched the backend SMRITI Reporting Engine (`reports_api.py`) to support:
  - Custom date-range columns mapping: resolves `creation` for `tabActivity Log` and `changed_at` for `tabSMRITI Address Audit Log` instead of `posting_date` default.
  - Custom user-filtering fields (`user` for Activity Log, `changed_by` for Address Change Log).
* **Robust UI Formatting (`reports.html`)**:
  - Resolved dynamic formatting issues where text fields containing `"value"` (like `old_value` and `new_value`) were incorrectly styled as currency (`₹NaN`), aligned right, and counted in totals sum metrics.
  - Implemented field-specific exclusions for both formatting and summary bar calculations to preserve left-aligned clean text presentation.
* **Role-Based Security**: Access restricted to `System Manager` and `SMRITI Store Manager` roles.

---

## 17. Drag-and-Drop reporting and dashboard customization suite (v1.9.3)

SMRITI Retail OS v1.9.3 introduces the Drag-and-Drop suite to provide interactive reporting and custom layout personalizations on dashboards.

### Key Capabilities

*   **Column Reordering & Saved Views Integration**:
    *   Adds standard HTML5 drag-and-drop support to report columns. Users can drag headers to swap or reorder report columns on the fly.
    *   Column reordering is fully integrated with **SMRITI Saved Views**; custom column sequences are saved under the `visible_columns_json` field in the database.
*   **SMRITI Pivot Matrix Builder**:
    *   Enables dynamic pivot views next to the report filter bar.
    *   Users drag available report fields into Rows, Columns, and Values target dropzones.
    *   Features a client-side aggregation engine that computes Sum, Count, and Avg metrics.
    *   Renders complex pivot grids dynamically with merged row/column headers and Grand Totals.
*   **Dashboard Widget Customization**:
    *   Added a "Customize Layout" button to both `smriti-home.html` and `psv-dashboard.html`.
    *   Edit mode reveals Grab handles (`⠿`) and dashed blue borders around adjustable widget cards.
    *   Cards can be dragged and dropped to reorder them in the dashboard grid.
    *   Reordered dashboard layout sequences are serialized and persisted in browser `localStorage` to preserve customization across session reloads.

---

## 18. Customer Growth Engine V2 — Architecture & Pilot (v2.0.0)

SMRITI CGE v2 (Customer Growth Engine) introduces a decoupled, transaction-isolated, and high-performance loyalty/promotions ledger architecture, fully aligning SMRITI with its role as the experience and operational logic layer above the ERPNext transaction engine.

### Key Architecture & New DocTypes
*   **`SMRITI Benefit Instrument Type`**: Classifies instruments (`LOYALTY`, `CASHBACK`, `STORE_CREDIT`, `VOUCHER`, `MEMBERSHIP`).
*   **`SMRITI Benefit Instrument`**: The defined benefit instrument (e.g. `Promo Cashback` or `Loyalty Points`) specifying validity days, reversal strategies, and negative balance validation limits.
*   **`SMRITI Benefit Wallet`**: Holds the cached current-state outstanding balance per customer, company, and instrument. Employs a composite unique database index (`uq_wallet_cust_comp_inst`) to prevent double-allocation/duplicate wallet records.
*   **`SMRITI Benefit Ledger`**: Immutable sub-ledger tracking all transaction events (`EARN`, `REDEEM`, `REVERSE`). Optimized with query indexes (`idx_ledger_cust_inst_date` and `idx_ledger_ref`).
*   **`SMRITI Campaign`**: Replaces legacy coupon campaigns with budget caps, reserved funds, and stop-on-limit thresholds.

### Decoupled Two-Step Pilot Activation (Phase 5C)
The pilot rollout sequence for CGE v2 is decoupled into two separate operational phases to prevent runtime risks:
1.  **Step 1 (Infrastructure & Migration)**: Logical database backup, schema migration (`bench migrate`), database DDL index additions, live data migration patch (with parameterized CLI kwargs `dry_run=False`), validation queries verification, and cache clearing.
2.  **Step 2 (Business Activation)**: Verifying all constraint tests `PASS`, executing 8 core checkout UAT scenarios (Customer Registration, Loyalty Earn, Loyalty Redeem, Promotion Apply, Coupon Apply, Sales Return Reversal, Wallet Inquiry, Daily Closing), obtaining unanimous Go/No-Go committee approval, and updating the site config flag:
    ```bash
    bench --site smriti_retail set-config smriti_site_config '{"cge_enabled": true}'
    ```

### Performance & Scaling Benchmarks
*   **Test Dataset**: 500 legacy ledger records and 10 campaigns.
*   **Execution Duration**: **`0.0730 seconds`** (throughput of ~6,800 records/sec).
*   **Projected Production Speed**: `~14.60 seconds` for 100,000 records.

---

## 19. SMRITI CGE Explorer & Generic CRUD Console (v2.0.1)

To support the 12 CGE (Customer Growth Engine) modules without creating 12 duplicate boilerplate HTML templates, JS scripts, and backend APIs, SMRITI Retail OS v2.0.1 implements the **Generic Explorer & Config-Driven Console** pattern.

### Key Capabilities

*   **Generic Explorer Pattern**: A single unified UI template ([cge_generic.html](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/www/cge_generic.html)) and route controller ([cge_generic.py](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/www/cge_generic.py)) dynamically map 12 distinct URL paths to their corresponding backend DocTypes.
*   **Whitelisted Schema Security**: To prevent unauthorized database access or custom API exploitation, the backend controller (`cge_api.py`) strictly enforces a whitelist of CGE DocTypes:
    *   `SMRITI Benefit Instrument`
    *   `SMRITI Membership Tier`
    *   `SMRITI Loyalty Program`
    *   `SMRITI Campaign`
    *   `SMRITI Promotion Rule`
    *   `SMRITI Coupon Rule`
    *   `SMRITI Loyalty Rule`
    *   `SMRITI Benefit Wallet`
    *   `SMRITI Customer Benefit Profile`
    *   `SMRITI Benefit Resolution Policy`
    *   `SMRITI Benefit Liability Snapshot`
    *   `SMRITI Benefit Audit Log`
    *   `SMRITI Benefit Resolution Sequence Detail` (Child table metadata support)
    Any request containing a DocType outside this list throws a hard `frappe.PermissionError`.
*   **Decoupled Service-First Layer**: Business operations route through whitelisted backend endpoints in `cge_api.py` (`get_cge_generic_fields`, `get_cge_generic_list`, `get_cge_generic_doc`, `save_cge_generic_doc`, and `delete_cge_generic_doc`) which delegate database operations to the backend service module (`cge_service.py`). Direct database insertions from the UI are strictly prohibited.
*   **Config-Driven Form Rendering**: Field metadata is resolved dynamically by fetching the active fields list and building the layout on the fly, supporting standard datatypes (`Link`, `Select`, `Int`, `Float`, `Check`, `Text`, `Date`, `Datetime`) with corresponding UI controls.
*   **Child Table Support**: Forms dynamically scan parent metadata for `Table` type fields, rendering interactive editable child tables. Rows can be appended, modified, and removed dynamically, and are correctly serialized and persisted during saves.
*   **Role Enforcement**: Router-level validation ensures only `SMRITI Store Manager`, `System Manager`, and `Administrator` roles can view, create, or modify records. Cashiers are blocked at request intercept.
*   **Delete Protection & Audit Logs**: High-impact deletions and additions are recorded using the system's `log_audit_event` mechanism. Soft-delete and validation logic prevent breaking referential integrity.
*   **Automated Testing**: Complete test coverage is established in `test_cge_generic.py`, validating user role access, validation rules, child table nesting, whitelist restrictions, and audit logs.

---

## 20. SMRITI PWA Activation & Offline-First POS Integration (v2.1.0)

SMRITI Retail OS v2.1.0 activates Progressive Web App (PWA) capabilities and implements an offline-first transaction queue for the POS Billing Terminal.

### Key Capabilities

*   **Service Worker Interception & MIME-type Fix**: Intercepts requests for `/sw.js` directly within the Frappe `before_request` hook (`boot.py`) and returns the service worker file using a custom Werkzeug `HTTPException`. This ensures the script is served with the correct header `Content-Type: application/javascript; charset=utf-8` and allowed at root scope (`Service-Worker-Allowed: /`).
*   **PWA Auto-Registration**: Inline and external registration scripts map `/sw.js` with `{ scope: '/' }` on the login page and globally on all standalone SMRITI pages via base template script injection (`templates/blank.html`).
*   **Stale-While-Revalidate Caching**: Caches core standalone CSS and JS assets required for offline boot (e.g. `smriti_tokens.css`, `smriti_sidebar_standalone.js`, `smriti_session_lock.js`) and stores dynamic pages matching canonical hyphenated routes.
*   **IndexedDB POS Invoice Queue**: If the network is down or the checkout REST API throws a network exception:
    1. Cashiers are prompted to queue the sale offline.
    2. Invoices are serialized and saved inside IndexedDB (`SmritiRetailOS` -> `pending_invoices`).
    3. The POS terminal clears the cart and resets normally, allowing continuous cashier checkouts.
*   **Background Sync & Network Indicators**: A live network status indicator `#network-status` displays `🟢 Online` or `🔴 Offline` based on connection state. When the connection is restored, pending transactions are automatically synced to the server in the background and deleted from IndexedDB.

---

## 21. SMRITI Knowledge Governance Framework (KGF) & registries (v2.2.0)

SMRITI Retail OS v2.2.0 introduces the **Knowledge Governance Framework (KGF)** consisting of the Formula Registry, Universal Explain Modal, and Business Dictionary. This enforces explainability, transparency, and traceability of computed KPIs and recommendations without exposing Frappe Desk views.

### Key Capabilities

*   **Central Formula Registry (DOC-02)**: Config-driven `SMRITI Formula Definition` DocType to centrally manage mathematical and forecasting formulas (e.g. Weeks of Cover, Sales Velocity, Outlet Health Score) with variable maps and owner traceability.
*   **Universal Explain Modal (DOC-01/03)**: Access-controlled `/smriti-explain` API endpoint integrated with Redis caching (key `smriti:explain:{formula_id}:{version}`, TTL 3600s). Serves dynamically resolved worked examples and explanations to the UI **without using dangerous `eval()` runtime execution**.
*   **SMRITI Business Dictionary (DOC-04)**: Dynamic lookup resource mapping 20 default retail operational terms (such as PSA, PSV, PDT, WOC, Dead Stock, Size Curves). Features custom child Doctypes (`SMRITI Related Formula` and `SMRITI Related Term`) for full relational lineage and audit logging (`DICTIONARY_ACCESSED` Activity Log entry).
*   **Direct Integration**: The Explain Modal has a "📖 Dictionary Entry" button linking directly to the live Business Dictionary (`/smriti-dictionary?term=ID`), which automatically loads that term's details and related items.
*   **Author Profile & Credibility (Rule 12)**: Author section detailing Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab) and AITDL core team.

---

## 22. SMRITI Predictive Hub & CGE Sidebar Integration (v2.2.1)

SMRITI Retail OS v2.2.1 exposes the Product Digital Twin (PDT) and Customer Growth Engine (CGE) subsystems directly in the user-facing navigation sidebar. It also adds their documentation, help registry entries, and coming-soon roadmap visibility.

### Key Capabilities

*   **Active Sidebar Integration**:
    *   Set the **AI Hub** section status to active and registered **PDT Dashboard** (Product Digital Twin) and **Simulation Sandbox** as coming-soon roadmap items.
    *   Reserved the **Knowledge Center** menu route (`/knowledge-center`) at the top of the **Help Desk** sidebar section as a coming-soon portal option.
    *   Enabled CGE and AI Hub feature flags (`cge_enabled`, `ai_hub_enabled`, `intelligence_enabled`) by default across `boot.py`, `smriti_sidebar.js`, and `smriti_sidebar_standalone.js`.
*   **Coming Soon Registry Integration**: Added `pdt_dashboard`, `simulation_sandbox`, and `knowledge_center` entries to `coming_soon_api.py` detailing completion progress and ETA (Q3 2026).
*   **Unified Help Center Articles**:
    *   Registered dynamic help articles for `pdt_dashboard`, `simulation_sandbox`, `cge_engine`, and `knowledge_center` inside `help_api.py`.
    *   Detailed the predictive PDT state machine (Stockout, Dead Stock, Overstock, Critical, Replenish Soon, Monitor, Healthy) and sandbox/CGE audit mechanisms for cashier and store manager training.

---
---

## 23. SMRITI Barcode Studio V2.4a Layout & Operations Upgrade (v2.4.0)

SMRITI Retail OS v2.4.0 delivers the **Barcode Studio V2.4a** layout and operations upgrade, designed to streamline high-volume warehouse scanning and print queue operations.

### Key Capabilities

*   **Article Range Loader**: Allows warehouse operators to retrieve and load a sequential list of items by defining prefix boundaries (e.g. `BBM-0001` to `BBM-0100`).
*   **Fashion-Retail Variant Expansion**: Styles automatically expand into all active color-size variant SKU rows (e.g., style `BBM-001` expands to size-wise rows) in a single database lookup.
*   **Interactive Worksheet Grid**: A comprehensive 9-column grid replacing the blank print canvas, showing `Select | Article | Item Name | Brand | Color | Size | Barcode | MRP | Qty | Labels` for direct batch print settings.
*   **Dynamic Mapping Preview**: Sidebar preview rendering live tag values (e.g. `{barcode}`, `{brand}`, `{mrp}`) resolved from the database prior to ZPL compilation.
*   **Transaction Expansion Modal**: A modal panel showing the count of items in imported PR/PO/GRN logs with selection filters ("Select All", "Only Missing Labels", "Only New SKUs").
*   **Box & Carton Packing Rules**: Quantity conversions based on outer box/carton capacities (labels count = carton units * multiplier).
*   **Price Fallback Chain**: Robust resolution of missing Rates and MRPs using a 3-layer priority: Variant Price $\rightarrow$ Price List $\rightarrow$ Parent Template.
*   **Persistent Reprint Queue**: Browser local storage queue caching recent print runs for instant one-click re-firing.
*   **Widescreen 3-Panel UX Ergonomics**: Layout grouping settings/previews in the left sidebar, the center worksheet grid, and ranges/filters in the right drawer with an always-visible bottom sticky action bar.
*   **Author Profile & Credibility (Rule 12)**: Author section detailing Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab) and AITDL core team.

---

## 24. SMRITI Barcode Scan Telemetry Collection Framework (v2.4.0)

SMRITI Retail OS v2.4.0 implements the **Barcode Scan Telemetry Collection Framework** (ACP-BARCODE-002A) to monitor physical scan performance and print usability across retail environments.

### Key Capabilities

*   **Immutable Raw Scan Log (`SMRITI Barcode Scan Event`)**: Logs cashier-level scan events with fields for attempts, success status, first pass flag, template ID, and unique UUID (ensuring idempotency). Update and delete operations are strictly blocked by the controller (`before_save`) to maintain audit integrity.
*   **Seeded Governance Event Registry**: Formally registers event definitions `SCAN-EVT-001` (Success on 1st attempt), `SCAN-EVT-002` (Success after retry), and `SCAN-EVT-003` (Failure or keyboard override) to avoid magic constants in the database.
*   **Daily Aggregation Scheduler**: Processes raw scans at 03:00 AM daily (store local time) and records metrics in `SMRITI Barcode Telemetry Snapshot` to avoid table locks during store hours.
*   **Pruning Retention Policy**: Raw events are kept in the transactional database for 90 days (pruned via the daily system job `delete_expired_scan_events`). Aggregated snapshot data is stored permanently for predictive model training.
*   **Scan Reliability Score (SMRITI-SCAN-REL-01)**: Formally registered under the KGF Formula Registry. Computes physical scanning efficiency:
    $$SRS = \left( \frac{FirstPassSuccesses + 0.5 \times RetrySuccesses}{TotalScans} \right) \times 100$$
*   **Security & Role Enforcement**: Telemetry submit API (`log_barcode_scan_event`) enforces authentication and restricts submission to `System Manager`, `SMRITI POS User`, `POS User`, `SMRITI Store Manager`, and `SMRITI Cashier` roles.
*   **Author Profile & Credibility (Rule 12)**: Designed by Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab) and AITDL core team.

---

## 25. SMRITI Landed Cost Allocation Module (v2.5.0)

SMRITI Retail OS v2.5.0 introduces the **Landed Cost Allocation** module (ACP-LANDEDCOST-01). It is designed as an analytical shadow-ledger costing layer that computes landed costs on top of ERPNext transaction records without mutating the core stock ledger valuation (`valuation_rate`) or general ledger, preserving SMRITI's SEL (Sophisticated Experience Layer) boundaries.

### Key Capabilities

*   **Shadow Ledger Costing**: Operates purely as an analytical layer. It reads standard ERPNext documents (Purchase Receipts, Purchase Invoices) and builds a secure, independent costing profile without database write side-effects on standard accounting balances.
*   **Manual Cost Persistence (G1 Table)**: Integrates the `SMRITI Landed Cost Manual Allocation` child DocType (`manual_allocations` table) to persist row-level custom allocations. Map rows using stable Frappe child-row names (`cost_line_ref` and `purchase_receipt_row`), preventing positional index shift errors between saves.
*   **Unit Landed Cost Update (G2 Rule)**: Updates the custom `estimated_landed_cost_last` field on the `Item` master. Runs a 2-tier chronological tiebreaker query on submit (`posting_date` as primary comparison, `creation` as tiebreaker) to guarantee that only the newest submitted allocation updates the master SKU cost.
*   **Safe Reversion on Cancellation (G3 Rule)**: On cancellation, the engine scans the `SMRITI Allocation Audit Snapshot` table to find the chronologically newest remaining submitted allocation for each affected SKU. Reverts the item's `estimated_landed_cost_last` to that value, or resets it to the standard `valuation_rate` if no allocations remain.
*   **Performance Optimization (G4 Rule)**: Prevents N+1 database queries during submission by caching receipts and pre-calculating total quantities in local variables prior to allocation loops.
*   **Stock Item Scope (G5 Rule)**: Excludes service and non-stock lines (`is_stock_item = 0`) from all base purchase value, total quantity, and allocation loop calculations, ensuring landed costs only accrue to physical assets.
*   **Penny Rounding Adjustment (G6 Rule)**: Detects decimal discrepancies (rounding difference between the Cost Line amount and sum of allocated amounts) and automatically applies the discrepancy to the last active stock item row per cost line.
*   **Strict Currency Match (G7 Rule)**: Enforces that referenced invoices must exactly match receipt currencies (`inv.currency == doc.currency`) to prevent foreign exchange rate conversion risks in Phase 1.
*   **Client Script Defaults (G8 Rule)**: Auto-populates `allocation_basis` with the parent document's `allocation_method` value upon row insertion for improved user experience.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---

## 26. SMRITI Reporting Governance & Security Auditing Framework (v2.5.0)

SMRITI Retail OS v2.5.0 implements the **Reporting Governance & Security Auditing Framework** (ACP-REPORTS-001) to control report execution, prevent cross-tenant cache leakage, and secure exported data.

### Key Capabilities

*   **Tenant Cache Partitioning (FRZ-REP-003)**: Isolates Redis caching per active tenant namespace. Ensures report caches remain secure and prevents unauthorized access to cached datasets in multi-tenant environments.
*   **Export Logging & Auditing (FRZ-REP-004)**: Registers and logs all data export requests in the Activity Logs. User role permissions take precedence over report definitions during export operations.
*   **Optimistic Concurrency Control (FRZ-REP-005)**: Prevents race conditions and template overwrites during concurrent report modifications by enforcing template checksum validation before saving.
*   **Explainability & Dictionary Integration**: Report execution parses and verifies business terms against `SMRITI Business Dictionary` (`KAR-01`/`KGF-01`), rendering metrics transparency and live worked examples in the UI.
*   **Report Projection Recovery**: Resolves SELECT projection aliases deterministically when business dictionary terms are missing, while blocking subqueries, guarding reserved keywords, and logging explainability audit events.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---

## 27. SMRITI Sales Force Management & Commission Module (v2.6.0)

SMRITI Retail OS v2.6.0 introduces the **Sales Force Commission (SFC) & Management (SFM)** module (ACP-SFC-001). This module implements a robust, audit-grade **ledger-first** design for customer ownership timelines, target allocation splits, and commission payouts sit on top of SMRITI Customer Growth Engine (CGE) structures.

### Key Capabilities

*   **Audit-Grade Ownership Timelines**: Governed by `SMRITI Customer Ownership`. Historical ownership records are immutable. When ownership changes, SMRITI automatically sets `end_date = yesterday` and `is_active = 0` on the old record, and inserts a new active record with `start_date = today` and `is_active = 1`.
*   **Store Abstraction Target Mapping**: Maps sales targets at the `SMRITI Store` level rather than physical ERPNext warehouses, ensuring consolidated target boundaries.
*   **Target Split Invariant**: Enforces that split percentages across reps for shared sales attribution must exactly sum to 100% (`primary_split_pct + secondary_split_pct = 100`) on save.
*   **Ledger-First Commission Lifecycle**: Earned commission immediately books a `Commission Event` and `Commission Ledger` entry. Monthly payouts are compiled and managed through `SMRITI Commission Settlement` drafts (`Draft` → `Approved` → `Paid`).
*   **Precedence Resolution Rule**: Evaluates active commission rates through four strict priority layers:
    1. Employee-level override rule with active priority.
    2. Employee-level active rule.
    3. Company-wide active rule.
    4. SMRITI Commission Settings defaults.
*   **Immutability on Approval**: Locking a settlement draft as `Approved` or `Paid` sets a database edit lock, making the document and its manual adjustment child tables strictly immutable.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---

## 28. SMRITI Customer Intelligence Graph (CIG) (v2.7.0)

SMRITI Retail OS v2.7.0 introduces the **SMRITI Customer Intelligence Graph (CIG)** framework (ACP-CIG-001) for advanced customer clienteling, predictive analytics, and explainable scoring models.

### Key Capabilities

*   **Purpose**: The CIG represents a first-class experience layer module mapping customer demographics, checkout timelines, purchase categories, and sizes with dynamic predictive modeling.
*   **Architecture & Flow**: Adhering to Service-First architecture (Rule 2), all calculations flow through the service controllers:
    Customer Checkout Event → SMRITI Customer Graph → CIG Calculation → SMRITI Customer Profile Update.
*   **Formula Registry Integration**: CIG resolves mathematical expressions dynamically from the Formula Registry (using approved and active formulas `TST-CHURN`, `TST-VIP`, and `TST-AFFINITY`) instead of hardcoding formula logic in python controllers, ensuring full transparency.
*   **Clienteling Settings**: Central settings parameters (`vip_threshold`, `dormancy_days`, `enable_predictions`) are managed in a single custom settings record to allow configuration tuning without code changes.
*   **VIP Threshold**: Customers whose VIP Candidate Score exceeds the configured `vip_threshold` setting are automatically flagged as VIPs (`is_vip = 1`) on their Customer Profiles.
*   **Dormancy Detection**: Tracks and flags inactive customer profiles (`is_dormant = 1`) when `days_since_last_visit` exceeds the configured `dormancy_days` threshold.
*   **Prediction Confidence**: Models customer checkout recurrence and next-purchase likelihood, scaling confidence scores between 0% and 100% relative to historical purchase consistency and demand volatility.
*   **Explainability (ⓘ Explain)**: Renders a worked example and explanation modal for each intelligence metric dynamically based on registry expressions, showing cashiers the exact variables, data sources, and calculations that contributed to the score.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---

## 29. SMRITI Billing Terminal & Theme Hardening (v2.8.0)

SMRITI Retail OS v2.8.0 consolidates front-end assets, locks down canonical routes, and hardens the visual style resolver on the Billing Terminal page.

### Key Capabilities

*   **Canonical Route & Interception Wrappers**: Excluded all legacy `/desk/*` path exposures. Legacy routes like `/app/smriti-barcode` or `/app/smriti-shift` are intercepted at `boot.py` and redirected to their canonical standalone paths (`/barcode`, `/shift`, `/smriti`). Main POS billing routes through thin wrapper modules loader dynamically initializing `SmritiBillingController` via `frappe.require()` assets.
*   **Enterprise License Activation**: Integrates signature validation mapping to allow CGE and Midnight Dark theme features to load dynamically, bypassing default fallback light configurations.
*   **Switcher Grid Layout Alignment**: Migrated theme switcher pills inside `.smriti-standalone-theme-bar` from flex wrap to a structured 2x2 CSS Grid (`grid-template-columns: repeat(2, 1fr)`). This gives each pill button sufficient width and prevents label truncation (resolving "Hybric" and "Minima" to "Hybrid" and "Minimal").
*   **Clean Database Test Isolation**: Clears stale locks and prevents transactional deadlocks during execution of the `test_billing_api.py` test suite. All 24 automated tests pass cleanly with 100% success.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---

## 30. SMRITI Royal Black and White Theme & Contrast Hardening (v2.8.1)

SMRITI Retail OS v2.8.1 introduces the **Royal Black and White** theme override and contrast accessibility fixes across user-facing pages, resolving low-contrast text readability bugs in dark mode.

### Key Capabilities

*   **Route-Level Theme Forced Overrides**: Intercepts `/smriti-help` routes inside Level 2 of the SMRITI UI resolver to automatically serve a high-contrast monochrome token set. Derives dark mode automatically via background luminance checks (`bg_luminance < 80`).
*   **Contrast Accessibility Mapping**: Replaces legacy, low-contrast text color elements (such as Hinglish definitions, glossary term titles, and FAQ items) with responsive, theme-aware variables (`var(--text-dark)`).
*   **Theme-Responsive Dictionary & Formula Registry Pages**: Updates static variables in `smriti-dictionary.html` and `smriti-formula-registry.html` to bind with responsive SMRITI tokens, ensuring standard pages automatically match light/dark theme modes.
*   **Author Profile & Credibility (Rule 12)**: Designed by Founder & Chief Architect **Jawahar R. Mallah** (AITDL - AI Technology & Development Lab).

---
*This knowledge base is maintained by **Jawahar R Mallah** and the SMRITI project team. For issues, open a GitHub issue at [erpnbook/smriti-docker](https://github.com/erpnbook/smriti-docker).*
