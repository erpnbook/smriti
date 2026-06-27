<div align="center">
  <img src="smriti_retail_os/public/images/logo.svg" alt="SMRITI Retail OS" width="100" /><br/><br/>

  # SMRITI Retail OS™
  **Enterprise Retail Operations Platform**<br/>
  Built on the ERPNext® application and the Frappe® Framework.

  ![Version](https://img.shields.io/badge/version-v1.8.5-1A2B5C)
  ![CI](https://img.shields.io/github/actions/workflow/status/erpnbook/smriti/smriti_ci.yml?label=CI&logo=github)
  ![Status](https://img.shields.io/badge/status-Production%20Candidate-22c55e)
  ![License](https://img.shields.io/badge/license-MIT-yellow)
  ![ERPNext](https://img.shields.io/badge/ERPNext-v16-2563EB)
  ![Frappe](https://img.shields.io/badge/Frappe-v16-2563EB)
  ![India Compliance](https://img.shields.io/badge/India%20Compliance-v16-22c55e)

</div>

---

| | |
|---|---|
| **Developer** | AITDL – AI Technology & Development Lab |
| **Version** | `v1.8.5` — Production Candidate |
| **Compatibility** | ERPNext v16 · Frappe v16 · India Compliance v16 |
| **License** | MIT — Free for commercial use |
| **Copyright** | © 2026 AITDL NETWORK & ERPNbook.com |

---

## 1. Product

SMRITI Retail OS is **not a new ERP**. It is a **Retail Experience and Intelligence Layer** built on top of ERPNext.

ERPNext handles the transaction engine — accounting, inventory, GST, compliance. SMRITI handles everything the retail user sees and does — store operations, POS workflows, analytics, channel management, and business intelligence.

> SMRITI Retail OS™ — Built on the ERPNext® application and the Frappe® Framework.
> Developed by AITDL – AI Technology & Development Lab.

---

## 2. Features

| Area | Capabilities |
|---|---|
| **POS & Billing** | Keyboard-first cashier terminal, hold/recall bills, manager override, loyalty |
| **Inventory** | GRN, stock transfer, stock audit, reorder alerts |
| **Purchase** | Purchase orders, supplier management, landed cost |
| **Analytics** | Sales velocity, weeks of cover, outlet health scores, dead stock |
| **Channel (PSV)** | Party Stock Visibility — distributor stock tracking via channel ledger |
| **Field Explorer (UFE)** | Universal Field Explorer at `/smriti-field-explorer` — browse, search, preview, and map fields across all DocTypes. Barcode Mode with stable Field IDs for label templates. |
| **Formula Registry** | Central registry for all computed KPIs with ⓘ Explain on every metric |
| **Knowledge Center** | Business Dictionary, Formula Registry, and Knowledge Search in one place |
| **POS Profile Manager** | Create, clone, archive POS profiles with shift-lock protection |
| **Trial CRM** | Lead capture, trial activation, platform administration |
| **Compliance** | India GST, e-Invoice, e-Waybill via India Compliance v16 |
| **PWA** | Offline-ready service worker, install prompt, IndexedDB cache |
| **CI / Quality Gate** | GitHub Actions pipeline — syntax, SDC compiler, architecture fitness, mutation tests |

---

## 3. Architecture

```
+----------------------------------------------------------+
|                  SMRITI Retail OS™                       |
|  Experience · Intelligence · Retail Workflows · PSV      |
|  UI Layer · API Layer · Service Layer · Repository Layer |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|              ERPNext v16  (System of Record)             |
|  Accounting · Inventory · POS · Customers · Compliance   |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|              Frappe Framework v16                        |
|  ORM · Auth · REST · Scheduler · Hooks · Boot Session   |
+----------------------------------------------------------+
                          │
                          ▼
+----------------------------------------------------------+
|  Database & Infrastructure (MariaDB · Redis · Docker)    |
+----------------------------------------------------------+
```

**Accounting model**: ERPNext is the operational System of Record for all transaction-level accounting (GL entries, GST, invoices). Financial reporting (Trial Balance, P&L, Balance Sheet) is the domain of TallyPrime in deployments where Tally integration is active; ERPNext data may be synchronized to Tally for statutory reporting.

→ Full architecture details: **[ARCHITECTURE.md](./ARCHITECTURE.md)**

---

## 4. Quick Start

### Docker (Recommended)

```bash
# 1. Clone and start
git clone https://github.com/erpnbook/smriti.git
docker compose up -d

# 2. Install app
docker compose exec smriti_retail-backend-1 \
  bench --site frontend install-app smriti_retail_os

# 3. Build assets
docker compose exec smriti_retail-backend-1 \
  bench build --app smriti_retail_os

# 4. Open in browser
http://localhost:8765
```

→ Full setup guide: **[INSTALL.md](../../INSTALL.md)** · **[DEPLOYMENT.md](../../DEPLOYMENT.md)**

### Post-Install Checklist

```
□ Configure POS Profile      → http://localhost:8765/smriti-pos-profiles
□ Assign user roles          → http://localhost:8765/security
□ Open first shift           → http://localhost:8765/shift
□ Run smoke tests            → see Testing section below
```

---

## 5. Project Structure

```
smriti_retail_os/
├── api/                  ← Whitelisted API endpoints (per feature)
├── repositories/         ← Data access layer
├── services/             ← Business logic layer
│   ├── field_explorer_service.py  ← UFE metadata + FIELD_ID_REGISTRY
│   └── formula_service.py         ← Formula Registry service
├── smriti_retail_os/
│   └── doctype/          ← Custom Frappe DocTypes
├── public/
│   ├── css/              ← Per-page SMRITI stylesheets
│   └── js/               ← Nav config, theme manager, PWA, offline store
│       └── smriti_field_explorer_widget.js  ← UFE embeddable modal
├── templates/includes/   ← Reusable sidebar, topbar, token loader
├── www/                  ← Standalone SMRITI pages (100+ routes)
│   ├── smriti-field-explorer.html  ← UFE full page (6 tabs)
│   └── smriti-formula-registry.html
├── sdc/                  ← SMRITI Documentation Compiler
│   ├── discovery.py              ← SDC compiler core
│   ├── knowledge_health_policy.json  ← Governance policy (single source of truth)
│   └── coverage_history.json     ← Coverage trend history
├── tests/                ← Unit + governance + mutation tests
├── .github/workflows/
│   └── smriti_ci.yml         ← GitHub Actions CI (Frappe-free gate)
├── hooks.py              ← App registration, doc events, boot session
└── boot.py               ← Role-based routing, Desk access blocking
```

---

## 6. Testing

```bash
# Run full integration test suite (requires live Frappe bench)
docker compose exec smriti_retail-backend-1 \
  bench --site frontend run-tests --app smriti_retail_os

# Run a specific module
docker compose exec smriti_retail-backend-1 \
  bench --site frontend run-tests \
  --app smriti_retail_os \
  --module smriti_retail_os.tests.test_pos_profile

# Run Frappe-free CI gate locally (no bench required)
python -m py_compile smriti_retail_os/**/*.py
python sdc/discovery.py
python -m pytest smriti_retail_os/tests/test_sdc006_mutation.py -v
python -m pytest smriti_retail_os/tests/test_knowledge_governance.py \
  -k "test_no_hardcoded or test_no_banned or test_every_formula or test_no_orphan" -v
```

> CI is automated: GitHub Actions runs the Frappe-free gate on every push to `main`.
> See `.github/workflows/smriti_ci.yml` for the full pipeline definition.

---

## 7. Documentation

Every module ships with a complete documentation set:

> Product Guide · User Guide · Admin Guide · Developer Guide · API Reference · Knowledge Base

→ **[Documentation Index](../../docs/DOCUMENTATION_INDEX.md)** — full registry (211 entries across 9 categories)

---

## 8. Governance

SMRITI Retail OS follows the **SMRITI Architecture Constitution** — a set of locked, inviolable rules covering UI policy, service-first design, system of record boundaries, auditability, and explainability requirements.

Key policies:
- **Rule 7 — SMRITI-First UI**: No Frappe Desk (`/desk`, `/app`) is ever exposed to end users
- **Rule 10 — Auditability**: Every critical action is logged with user, timestamp, before/after values
- **DOC-01 — Explainability**: Every metric has a `ⓘ Explain` modal with formula and worked example

→ **[ARCHITECTURE.md](./ARCHITECTURE.md)** — Architecture Constitution, Golden Rules, Design Principles

---

## 9. Contributing

```bash
# Branch naming
feature/<module>-<description>
fix/<module>-<issue>
docs/<module>-<document>

# Commit convention
feat(<module>): short description
fix(<module>): short description
docs(<module>): short description
test(<module>): short description

# Checklist before PR
□ SMRITI-First UI Policy followed (no /desk routes)
□ Service-First pattern: UI → API → Service → Repository
□ Unit tests written and passing
□ Governance docs created (6 document types per module)
□ Pre-commit HTML validator passes
```

→ **[CONTRIBUTING.md](../../CONTRIBUTING.md)** · **[CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md)**

---

## 10. License

```
MIT License
Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All Rights Reserved.

All open-source licensing notices for ERPNext and Frappe
must be preserved in source code files.
```

→ **[ABOUT_AUTHOR.md](./ABOUT_AUTHOR.md)** — About Jawahar R. Mallah, Founder & Chief Architect, AITDL

---

<div align="center">
  <em>SMRITI Retail OS™ — Always Decision-Ready.</em><br/>
  <em>Developed by AITDL – AI Technology &amp; Development Lab</em>
</div>
