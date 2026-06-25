# SMRITI Retail OS™

<div align="center">

  <img src="smriti_retail_os/public/images/logo.svg" alt="SMRITI Retail OS" width="120" />

  ### Retail Intelligence Platform — Experience Layer for ERPNext®

  [![Version](https://img.shields.io/badge/SMRITI-v1.2.10-1A2B5C?style=for-the-badge)](https://github.com/erpnbook/smriti)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![ERPNext: v16](https://img.shields.io/badge/ERPNext-v16-2563EB?style=for-the-badge)](https://github.com/frappe/erpnext)
  [![Frappe: v16](https://img.shields.io/badge/Frappe-v16-2563EB?style=for-the-badge)](https://github.com/frappe/frappe)
  [![India Compliance: v16](https://img.shields.io/badge/India_Compliance-v16-22c55e?style=for-the-badge)](https://github.com/resilient-tech/india-compliance)

  **Developed by AITDL – AI Technology & Development Lab**
  Powered by ERPNext® & Frappe® Framework

</div>

---

> **Author**: Jawahar R. Mallah — Founder & Chief Architect, AITDL
> **Experience**: 20+ years in Retail Technology, Distribution Systems, POS Solutions, ERP Implementations & Enterprise Application Design
> *"Always decision-ready."*

---

## Table of Contents

1. [Product Identity](#1-product-identity)
2. [Architecture Model](#2-architecture-model)
3. [Architecture Constitution](#3-architecture-constitution--golden-rules)
4. [SMRITI-First UI Policy](#4-smriti-first-ui-policy-rule-7)
5. [Modules & Pages](#5-modules--pages)
6. [Project Structure](#6-project-structure)
7. [Roles & Permissions](#7-roles--permissions)
8. [Design System](#8-design-system)
9. [API Reference](#9-api-reference)
10. [Formula Registry](#10-formula-registry)
11. [Installation](#11-installation)
12. [Docker Production Setup](#12-docker-production-setup)
13. [Testing](#13-testing)
14. [AI Agent Development Guide](#14-ai-agent-development-guide)
15. [Documentation](#15-documentation)
16. [Governance Links](#16-governance-links)
17. [Roadmap](#17-roadmap)
18. [License](#18-license)

---

## 1. Product Identity

| Field | Value |
|---|---|
| **Official Name** | SMRITI Retail OS™ |
| **Developer** | AITDL – AI Technology & Development Lab |
| **Author** | Jawahar R. Mallah, Founder & Chief Architect |
| **Current Version** | `v1.2.10` |
| **License** | MIT |
| **Copyright** | © 2026 AITDL NETWORK & ERPNbook.com. All Rights Reserved. |
| **Framework** | Frappe v16 + ERPNext v16 + India Compliance v16 |

### What SMRITI Is NOT

SMRITI is **not a new ERP**. It is a **Retail Experience & Intelligence Layer** — a Frappe application that sits on top of ERPNext and transforms it into a retail operating system optimised for store operations, channel management, and business analytics.

### Mandatory Attribution Notice

All primary public-facing interfaces and manuals must display:

> **SMRITI Retail OS™**
> Developed by AITDL
> Powered by ERPNext® & Frappe® Framework

---

## 2. Architecture Model

```
┌─────────────────────────────────────────────────────────────┐
│                   SMRITI Retail OS™                         │
│                                                             │
│  SMRITI UI Layer (standalone www/* pages, no /desk)        │
│  SMRITI API Layer (whitelisted controllers)                 │
│  SMRITI Service Layer (business logic)                      │
│  SMRITI Repository Layer (data access abstraction)          │
├─────────────────────────────────────────────────────────────┤
│                   Frappe Framework v16                      │
│  ORM  │  REST API  │  Auth  │  Boot Session  │  Hooks      │
├─────────────────────────────────────────────────────────────┤
│                     ERPNext v16                             │
│  POS Invoice  │  Stock Entry  │  Purchase Receipt           │
│  Item  │  Customer  │  Supplier  │  POS Profile             │
│  Payment Entry  │  Price List  │  Loyalty Points            │
├─────────────────────────────────────────────────────────────┤
│                  India Compliance v16                       │
│  GST  │  GSTIN Validation  │  e-Invoice  │  e-Waybill      │
│  GSTR Reports  │  HSN Codes  │  Tax Templates               │
├─────────────────────────────────────────────────────────────┤
│                      Database Layer                         │
│              MariaDB / MySQL (via Docker)                   │
└─────────────────────────────────────────────────────────────┘
```

### Domain Ownership Table

| Domain | Owner | ERPNext Role |
|---|---|---|
| Accounting / GL / GST | ERPNext | System of Record |
| Inventory Valuation | ERPNext | System of Record |
| Stock Ledger | ERPNext | System of Record |
| Customers / Suppliers / Users | ERPNext | System of Record |
| UI / UX | SMRITI | Owner |
| Retail Workflows | SMRITI | Owner |
| POS Experience | SMRITI | Owner |
| Reports / Analytics | SMRITI | Owner |
| Store Operations | SMRITI | Owner |
| POS Profile Configuration | SMRITI | Experience Layer |
| Party Stock Visibility (PSV/PSA) | SMRITI | Shadow Ledger (read-only ERPNext) |
| Formula Registry | SMRITI | Owner |
| Explain Engine | SMRITI | Owner |
| Channel Governance Engine (CGE) | SMRITI | Owner |
| Trial CRM / Platform Admin | SMRITI | Owner |

---

## 3. Architecture Constitution — Golden Rules

The following rules apply to **all developers, contributors, and AI agents** working on this codebase. They are LOCKED and cannot be overridden.

### Rule 1 — Do NOT Replace the Architecture
Agents may **extend**, **improve**, **refactor**, or **optimize**.
Agents may **NOT** replace, introduce competing frameworks, or ignore approved service layers.

### Rule 2 — Service-First Design (MANDATORY)

```
UI → API → Service Layer → Business Logic → Database
```

**Forbidden:**
```
UI → Database (direct)
UI → frappe.client.insert() from frontend
UI → frappe.new_doc() from frontend
```

### Rule 3 — ERPNext Is the System of Record
Never create:
- Duplicate accounting logic
- Duplicate GST calculation
- Duplicate inventory valuation
- Duplicate stock ledger

### Rule 4 — Tally-First Accounting Strategy
SMRITI does NOT replace TallyPrime. SMRITI owns inventory, purchase, sales, PSV, and AI. Tally owns books of accounts, trial balance, balance sheet, and P&L.

### Rule 5 — Single Source of Truth
Every business concept has exactly one owner. No duplicate ownership.

### Rule 6 — PSV Ownership Boundary
PSV reads ERPNext master data. PSV does NOT modify ERPNext Stock Ledger Entries or General Ledger Entries.

### Rule 7 — No Shadow Databases
Never create duplicate customer masters, supplier masters, or stock tables.

### Rule 8 — Pricing Is a Separate Domain
Inventory never maintains selling prices.

### Rule 9 — Approval Before Automation
Analytics may be automatic. Business actions (POs, Transfers, Discounts, Price Changes) require human approval.

### Rule 10 — Auditability Required
Every critical action must log: User, Timestamp, Before Value, After Value, Reason.

---

## 4. SMRITI-First UI Policy (Rule 7)

> **Every new page, module, form, report, or UI component MUST be built as a dedicated SMRITI standalone page.**

### What Is FORBIDDEN

| ❌ Wrong Pattern | ✅ Correct Pattern |
|---|---|
| Opens `/desk#Form/Sales Invoice/new` | Opens `/billing` (SMRITI custom page) |
| Opens `/app/sales-invoice` | Opens `/smriti-masters` (SMRITI custom page) |
| `frappe.new_doc("Sales Invoice")` | `smriti_api.create_invoice()` via `frappe.call()` |
| `frappe.set_route("Form", "Customer")` | SMRITI modal/form renders custom UI |

### Mandatory Checklist (ALL Must Be YES Before Proceeding)

- [ ] Does this have a dedicated SMRITI www page or custom page route?
- [ ] Does the user URL contain `/smriti`, `/billing`, `/inventory`, `/reports`, `/masters`, or another SMRITI-owned route?
- [ ] Is all backend communication going through a SMRITI service controller?
- [ ] Is the page styled with SMRITI design system (Navy `#1A2B5C` + Blue `#2563EB` + Arial)?
- [ ] Does the page show SMRITI logo and branding?
- [ ] Is `/desk` and `/app` completely hidden from this user flow?

### Naming Convention

| Category | Pattern |
|---|---|
| SMRITI Pages | `/smriti-<feature>` |
| SMRITI APIs | `smriti_retail_os.<module>.api.<feature>_api.<method>` |
| SMRITI Services | `smriti_retail_os.<module>.service.<feature>_service.<method>` |
| SMRITI CSS | `smriti_<feature>.css` |
| SMRITI JS | `smriti_<feature>.js` |

### Coming Soon Policy

Never expose Frappe Desk as a temporary workaround. Always use the SMRITI Coming Soon page:

```
/smriti-coming-soon?feature=Purchase+Orders&progress=60&eta=Q3+2026
```

### Routing Policy (Frappe v16+)

```javascript
// CORRECT — Frappe canonical route
frappe.set_route("stock-center");
window.location.href = "/app/stock-center";   // fallback

// FORBIDDEN
window.location.href = "/page/stock-center";
window.location.href = "/desk/page/stock-center";
```

---

## 5. Modules & Pages

### Core Retail Modules

| Route | Module | Status |
|---|---|---|
| `/smriti-home` | SMRITI Dashboard | ✅ Live |
| `/billing` | POS Billing Engine | ✅ Live |
| `/inventory` | Inventory Management | ✅ Live |
| `/purchase` | Purchase Management | ✅ Live |
| `/reports` | Reports Center | ✅ Live |
| `/shift` | Shift Open/Close | ✅ Live |
| `/barcode` | Barcode Printing | ✅ Live |

### Masters & Configuration

| Route | Module | Status |
|---|---|---|
| `/item-master` | Item Master | ✅ Live |
| `/customers` | Customer Master | ✅ Live |
| `/suppliers` | Supplier Master | ✅ Live |
| `/brand-master` | Brand Master | ✅ Live |
| `/category-master` | Category Master | ✅ Live |
| `/smriti-pos-profiles` | POS Profile Manager | ✅ Live |
| `/configure` | System Configuration | ✅ Live |

### Analytics & Intelligence

| Route | Module | Status |
|---|---|---|
| `/analytics` | Analytics Dashboard | ✅ Live |
| `/smriti-pdt` | Predictive Distribution Twin | ✅ Live |
| `/smriti-formula-registry` | Formula Registry | ✅ Live |
| `/smriti-pricing` | Pricing Intelligence | ✅ Live |

### PSV / Channel Operations

| Route | Module | Status |
|---|---|---|
| `/psv-dashboard` | Party Stock Visibility | ✅ Live |
| `/psa` | Party Stock Accounts | ✅ Live |
| `/psv-opening-balance` | PSV Opening Balance | ✅ Live |
| `/psv-reconciliation` | PSV Reconciliation | ✅ Live |
| `/psv-exception-analysis` | PSV Exception Analysis | ✅ Live |
| `/smriti-cge` | Channel Governance Engine | ✅ Live |
| `/smriti-sfm` | SFM Module | ✅ Live |
| `/smriti-sfc` | SFC Module | ✅ Live |

### Commercial Platform

| Route | Module | Status |
|---|---|---|
| `/smriti-trial` | Trial Activation | ✅ Live |
| `/smriti-trial-leads` | Trial CRM | ✅ Live |
| `/smriti-platform-admin` | Platform Administration | ✅ Live |
| `/smriti-roi-calculator` | ROI Calculator | ✅ Live |
| `/smriti-presentation` | SMRITI Presentation | ✅ Live |

### Sales & Operations

| Route | Module | Status |
|---|---|---|
| `/sales-invoices` | Sales Invoices | ✅ Live |
| `/sales-orders` | Sales Orders | ✅ Live |
| `/sales-return` | Sales Returns | ✅ Live |
| `/sales-upload` | Sales Upload | ✅ Live |
| `/sizewise-invoice` | Size-Wise Invoice | ✅ Live |
| `/sizewise-item` | Size-Wise Item | ✅ Live |
| `/scheme-creator` | Scheme Creator | ✅ Live |
| `/delivery-challan` | Delivery Challan | ✅ Live |
| `/payments` | Payments | ✅ Live |

### Support & Governance

| Route | Module | Status |
|---|---|---|
| `/smriti-help` | Help Center | ✅ Live |
| `/smriti-dictionary` | Business Dictionary | ✅ Live |
| `/smriti-coming-soon` | Coming Soon Page | ✅ Live |
| `/smriti-go-live` | Go Live Checklist | ✅ Live |
| `/smriti-license` | License Manager | ✅ Live |
| `/smriti-support` | Support Portal | ✅ Live |
| `/smriti-clienteling` | Clienteling | ✅ Live |
| `/security` | Security & Users | ✅ Live |
| `/smriti-security-log` | Security Audit Log | ✅ Live |
| `/smriti-safe` | SMRITI Safe | ✅ Live |
| `/verify-certificate` | Certificate Verification | ✅ Live |
| `/backup` | Backup Manager | ✅ Live |
| `/release-notes` | Release Notes | ✅ Live |
| `/smriti-login` | Custom Login Page | ✅ Live |

---

## 6. Project Structure

```
smriti_retail_os/
│
├── smriti_retail_os/
│   │
│   ├── api/                         # Whitelisted API endpoints
│   │   ├── pos_profile_api.py       # POS Profile Management API
│   │   ├── trial_activation_api.py  # Trial Activation API
│   │   ├── trial_operations_api.py  # Trial Operations API
│   │   ├── help_api.py              # Help Center API
│   │   └── coming_soon_api.py       # Coming Soon Registry API
│   │
│   ├── repositories/                # Data access layer
│   │   ├── __init__.py
│   │   └── pos_profile_repository.py
│   │
│   ├── services/                    # Business logic layer
│   │   ├── pos_profile_service.py   # POS Profile business rules
│   │   ├── formula_service.py       # Formula Registry engine
│   │   ├── knowledge_service.py     # Knowledge Center
│   │   └── trial_service.py         # Trial lifecycle service
│   │
│   ├── clienteling/                 # Clienteling sub-module
│   │   └── service/
│   │       └── clienteling_service.py
│   │
│   ├── sfm/                         # SFM sub-module
│   │   └── service/
│   │       └── attribution_service.py
│   │
│   ├── smriti_retail_os/            # DocTypes (Frappe metadata)
│   │   └── doctype/
│   │       ├── smriti_trial_activation/
│   │       ├── smriti_trial_lead/
│   │       ├── smriti_psv_transaction/
│   │       ├── smriti_certification_exam/
│   │       ├── smriti_psv_exam_attempt/
│   │       ├── smriti_provision_log/
│   │       └── smriti_trial_settings/
│   │
│   ├── public/
│   │   ├── css/                     # SMRITI CSS (per-page + global)
│   │   │   ├── smriti-inventory.css
│   │   │   ├── smriti-purchase.css
│   │   │   ├── smriti-reports.css
│   │   │   ├── smriti-sizewise-invoice.css
│   │   │   ├── smriti-sizewise-item.css
│   │   │   └── smriti-ui-hardening.css
│   │   │
│   │   ├── js/                      # SMRITI JS
│   │   │   ├── smriti_nav_config.js # Navigation menu registry
│   │   │   ├── smriti_ui_resolver.js
│   │   │   ├── smriti_theme_manager.js
│   │   │   ├── smriti_offline_store.js
│   │   │   └── smriti_pwa.js
│   │   │
│   │   └── images/
│   │       └── logo.svg
│   │
│   ├── templates/
│   │   └── includes/
│   │       ├── smriti_sidebar.html  # Reusable sidebar component
│   │       ├── smriti_topbar.html   # Reusable top nav component
│   │       └── smriti_token_loader.html  # Auth token / branding
│   │
│   ├── www/                         # SMRITI standalone pages
│   │   ├── smriti-home.html / .py
│   │   ├── billing.html / .py
│   │   ├── inventory.html / .py
│   │   ├── purchase.html / .py
│   │   ├── shift.html / .py
│   │   ├── barcode.html / .py
│   │   ├── reports.html / .py
│   │   ├── smriti-pos-profiles.html / .py
│   │   ├── smriti-trial.html / .py
│   │   ├── smriti-trial-leads.html / .py
│   │   ├── smriti-platform-admin.html / .py
│   │   ├── psv-dashboard.html / .py
│   │   ├── smriti-formula-registry.html / .py
│   │   ├── smriti-coming-soon.html / .py
│   │   └── ... (100+ additional pages)
│   │
│   ├── tests/
│   │   ├── test_pos_profile.py       # POS Profile tests
│   │   ├── test_branding_integrity.py
│   │   ├── test_formula_registry.py
│   │   ├── test_knowledge_center.py
│   │   └── test_psv.py
│   │
│   ├── hooks.py                      # App registration, CSS/JS, doc events
│   ├── boot.py                       # Role-based routing, Desk blocking
│   ├── psv_service.py                # PSV shadow ledger engine
│   └── setup.py                      # Post-install setup hooks
│
├── docs/                             # Documentation (211 entries, governed)
│   ├── DOCUMENTATION_INDEX.md
│   ├── 01-product/
│   ├── 02-user-guide/
│   ├── 03-admin-guide/
│   ├── 04-operations/
│   ├── 05-developer/
│   ├── 06-api/
│   ├── 07-kb/
│   ├── 08-governance/
│   └── reports/
│
├── compose.yaml                      # Docker production compose
├── .env                              # Environment variables
└── README.md
```

---

## 7. Roles & Permissions

```
SMRITI Cashier:
├── POS Invoice      → Create, Read, Write
├── Customer         → Create, Read, Write
├── Item             → Read only
├── /billing         → Full access
└── All other routes → Redirected to /billing

SMRITI Store Manager:
├── Item             → Create, Read, Write
├── Customer / Supplier → Create, Read, Write
├── Stock Entry      → Create, Read, Write
├── Purchase Receipt → Create, Read, Write
├── All SMRITI pages → Full access
└── /desk, /app      → Blocked (redirected to /smriti)

SMRITI Admin:
├── POS Profile API  → create/update/archive/clone
├── Trial Management → Full access
├── Platform Admin   → Full access
└── All SMRITI pages → Full access

System Manager:
├── All ERPNext DocTypes → Full access
└── NOTE: /desk is accessible to System Manager only
    (SMRITI theme and routing bypass for admin work)
```

### boot.py — Desk Blocking Policy

```python
# Blocked for ALL users including Administrator:
SMRITI_BLOCKED_DESK_PATHS = [
    "/desk/setup-wizard",  → redirect to /smriti
    "/desk/modules",       → redirect to /smriti
    "/desk#Form",          → redirect to /smriti
    "/desk#List",          → redirect to /smriti
    "/desk#query-report",  → redirect to /smriti
    "/desk#setup-wizard",  → redirect to /smriti
]
```

---

## 8. Design System

### Color Palette

```css
:root {
    /* Primary Brand */
    --smriti-navy:      #1A2B5C;   /* Dark navy — primary background */
    --smriti-blue:      #2563EB;   /* Action blue — buttons, accents */

    /* Surface Scale */
    --smriti-surface:   #16213e;   /* Card / sidebar surface */
    --smriti-surface2:  #1a2744;   /* Input / secondary surface */
    --smriti-border:    #2a3a5c;   /* Border color */

    /* Typography */
    --smriti-text:      #e2e8f0;   /* Primary text */
    --smriti-muted:     #8892a4;   /* Secondary / muted text */

    /* Status */
    --smriti-success:   #22c55e;
    --smriti-warning:   #f59e0b;
    --smriti-danger:    #ef4444;
    --smriti-info:      #3b82f6;
}
```

### Typography

```
Primary Font:  Arial (UI body text)
Heading Font:  Outfit (400, 600, 800) — Google Fonts
Body Font:     Inter (400, 500, 600, 700) — Google Fonts
Icon Set:      Material Symbols Outlined
```

### UI Components

- **Navigation**: Left sidebar (`smriti_sidebar.html`) + top bar (`smriti_topbar.html`)
- **Page Shell**: Standalone HTML templates (`www/<page>.html`), never inside `/desk`
- **Drawers**: Right-side sliding drawer panels for create/edit forms
- **Modals**: SMRITI branded modal overlays (not Frappe dialogs)
- **Explain (ⓘ)**: Every KPI/metric must have a `ⓘ Explain` button revealing formula documentation

---

## 9. API Reference

### API Architecture

All APIs follow this strict pattern:

```
smriti_retail_os.<module>.api.<feature>_api.<method>()
```

All endpoints are `@frappe.whitelist()` decorated and enforce role-based access via service layer.

### POS Profile API (`api/pos_profile_api.py`)

| Method | Endpoint | Role Required |
|---|---|---|
| `get_profiles` | GET | SMRITI Admin / System Manager |
| `get_profile_detail` | GET | SMRITI Admin / System Manager |
| `save_profile` | POST | SMRITI Admin / System Manager |
| `archive_profile` | POST | SMRITI Admin / System Manager |
| `clone_profile` | POST | SMRITI Admin / System Manager |
| `get_dropdown_data` | GET | SMRITI Admin / System Manager |
| `check_shift_lock` | GET | SMRITI Admin / System Manager |

### Shift APIs (`shift_api.py`)

| Method | Description |
|---|---|
| `open_shift(opening_cash, pos_profile)` | Opens a POS shift (creates POS Opening Entry) |
| `close_shift(declared_cash, declared_card, declared_upi, opening_entry)` | Closes shift |
| `get_shift_status()` | Returns current shift status and cashier |

### Billing APIs (`billing_api.py`)

| Method | Description |
|---|---|
| `add_item_by_barcode(barcode, price_list)` | Resolves item from barcode |
| `hold_bill(cashier, customer, items)` | Parks current bill |
| `recall_bill(cashier)` | Retrieves parked bill list |
| `submit_bill(cashier, customer, items, payments, ...)` | Submits POS Invoice |
| `validate_manager_override(manager_user, manager_password, action_type, invoice_name)` | Manager PIN auth |

### Inventory APIs (`inventory_api.py`)

| Method | Description |
|---|---|
| `create_grn(supplier, invoice_no, items)` | Creates Purchase Receipt |
| `create_stock_transfer(from_warehouse, to_warehouse, items)` | Stock Entry Material Transfer |
| `create_stock_adjustment(items, reason)` | Stock Entry Material Issue/Receipt |
| `create_stock_audit(items)` | Stock Reconciliation |
| `get_stock_summary(warehouse)` | Returns item-wise stock list |

### Barcode APIs (`barcode_api.py`)

| Method | Description |
|---|---|
| `get_items_for_printing(filters, source_doctype, source_name)` | Returns items list with print_qty |
| `generate_prn(items, label_size)` | Returns ZPL/PRN string for thermal printer |

---

## 10. Formula Registry

SMRITI maintains a **central Formula Registry** (`/smriti-formula-registry`) for all computed retail KPIs. No formula may be deployed to production without being registered.

### Core Registered Formulas

| Formula | Category | Explain (ⓘ) |
|---|---|---|
| Sales Velocity | Inventory Intelligence | ✅ |
| Weeks of Cover (WOC) | Inventory Intelligence | ✅ |
| Outlet Health Score | Store Analytics | ✅ |
| Dead Stock Score | Inventory Intelligence | ✅ |
| Transfer Benefit Score | Operations | ✅ |
| Forecast Confidence | AI / PDT | ✅ |
| Sell Through % | PSV / Channel | ✅ |
| Stock Accuracy % | Audit | ✅ |
| Inventory Turnover | Finance | ✅ |
| Variant Curve Health | Merchandising | ✅ |

### Rule: Explainability-First (Rule ID: DOC-01)

Every metric shown on a SMRITI UI **must** be accompanied by:
1. Business Meaning
2. Exact Formula
3. Worked Example
4. Data Sources
5. Interpretation Guide
6. Recommended Action

---

## 11. Installation

### Prerequisites

```bash
# ERPNext v16 + Frappe v16 bench required
# Docker recommended for production

bench --version  # must be 5.x+
python --version # must be 3.11+
```

### Install Steps

```bash
# Step 1 — Get India Compliance (if not installed)
bench get-app --branch version-16 \
  https://github.com/resilient-tech/india-compliance.git
bench --site yoursite install-app india_compliance

# Step 2 — Get SMRITI Retail OS
bench get-app https://github.com/erpnbook/smriti.git
bench --site yoursite install-app smriti_retail_os

# Step 3 — Migrate
bench --site yoursite migrate

# Step 4 — Build assets
bench build --app smriti_retail_os

# Step 5 — Clear cache & restart
bench --site yoursite clear-cache
bench restart
```

### Post-Install Configuration

```
1. POS Profile Setup:
   → /smriti-pos-profiles → New Profile
   → Set Company, Warehouse, Currency, Payment Modes, Cashiers

2. Walk-In Customer:
   → /customers → New
   → Name: Walk-In Customer, Type: Individual

3. India Compliance:
   → Settings → Company GSTIN, HSN Codes, Tax Templates

4. Assign User Roles:
   → /security → Users → [Select User]
   → Add Role: SMRITI Cashier / SMRITI Store Manager / SMRITI Admin
```

---

## 12. Docker Production Setup

SMRITI Retail OS ships with a `compose.yaml` for Docker-based production deployment.

```bash
# Start all containers
docker compose up -d

# Check running containers
docker compose ps

# Install SMRITI on site
docker compose exec smriti_retail-backend-1 \
  bench --site frontend install-app smriti_retail_os

# Build assets inside container
docker compose exec smriti_retail-backend-1 \
  bench build --app smriti_retail_os

# Run SMRITI tests inside container
docker compose exec smriti_retail-backend-1 \
  bench --site frontend run-tests \
  --app smriti_retail_os \
  --module smriti_retail_os.tests.test_pos_profile

# Commit working container state
docker commit smriti_retail-backend-1 smriti-retail-os:v1.2.10

# Export image (disaster recovery backup)
docker save smriti-retail-os:v1.2.10 -o smriti_retail_os_v1.2.10.tar

# Restore image
docker load -i smriti_retail_os_v1.2.10.tar
```

### Default Port Mapping

| Service | URL |
|---|---|
| SMRITI UI | `http://localhost:8765` |
| Frappe Backend | Internal container |
| MariaDB | Internal container |

---

## 13. Testing

```bash
# Run all SMRITI tests
docker compose exec smriti_retail-backend-1 \
  bench --site frontend run-tests --app smriti_retail_os

# Run a specific test module
docker compose exec smriti_retail-backend-1 \
  bench --site frontend run-tests \
  --app smriti_retail_os \
  --module smriti_retail_os.tests.test_pos_profile

# Current test suite results
# ─────────────────────────────────────────────────
# test_pos_profile.py           PASS (19.039s / 5 tests)
#   ├── test_admin_permission_required     ✅
#   ├── test_save_and_retrieve_profile     ✅
#   ├── test_clone_profile                 ✅
#   ├── test_shift_lock_validation         ✅
#   └── test_archive_profile               ✅
#
# test_branding_integrity.py    PASS
# test_formula_registry.py      PASS
# test_knowledge_center.py      PASS
# test_psv.py                   PASS
# ─────────────────────────────────────────────────
```

---

## 14. AI Agent Development Guide

> This section governs AI agents (Antigravity, Gemini, Claude, Cursor) working on the SMRITI codebase.

### Before Making Any Change

```
1. Read this README fully — understand architecture and rules.
2. Read hooks.py — understand what is registered.
3. Read boot.py — understand role routing and Desk blocking logic.
4. Search existing www/ pages — check if a route already exists.
5. Verify ERPNext DocType exists before creating a custom field.
```

### Adding a New Feature — Required Pattern

```
Step 1:  Identify existing ERPNext DocType to leverage
Step 2:  Create SMRITI www page: www/<feature>.html + .py
Step 3:  Create service: services/<feature>_service.py
Step 4:  Create repository (if needed): repositories/<feature>_repository.py
Step 5:  Create API: api/<feature>_api.py
Step 6:  Register route in smriti_nav_config.js
Step 7:  Write tests: tests/test_<feature>.py
Step 8:  Write governance documentation (6 documents minimum)
Step 9:  bench build + migrate + clear-cache + restart
```

### Common Mistakes to Avoid

```
❌ Opening /desk or /app routes in browser automation
   → Always navigate to /smriti-* routes

❌ frappe.client.insert() or frappe.new_doc() from UI JS
   → Route through SMRITI API → Service → Repository

❌ Creating new DocType for data that ERPNext already owns
   → Use POS Invoice, Purchase Receipt, Stock Entry, etc.

❌ Writing GST calculation logic
   → Use India Compliance Item Tax Templates

❌ Creating custom stock ledger / accounting tables
   → Use ERPNext Stock Entry / Purchase Receipt / Payment Entry

❌ Hardcoded CSS class names
   → Use CSS variables (see Design System)

❌ Redirecting System Manager to SMRITI pages
   → Always check roles in boot.py and bypass

❌ pos_invoice.docstatus = 1
   → Use pos_invoice.submit()

❌ get_decrypted_password() for PIN auth
   → Use frappe.auth.check_password()

❌ /page/* or /desk/page/* routes in sidebar/buttons
   → Use /app/<route> or frappe.set_route("<route>")
```

### File Edit Checklist

```
After editing Python files:
□ bench --site frontend migrate
□ bench --site frontend clear-cache
□ bench restart

After editing JS/CSS files:
□ bench build --app smriti_retail_os
□ bench --site frontend clear-cache
□ Hard refresh browser (Ctrl+Shift+R)

After editing hooks.py:
□ bench --site frontend migrate
□ bench --site frontend clear-cache
□ bench restart
□ Hard refresh browser

After adding new API:
□ Verify @frappe.whitelist() decorator present
□ Add role permission check in service layer
□ Write unit test covering permission enforcement
```

### Commit Message Convention

```
feat(<module>): <short description>
fix(<module>): <short description>
docs(<module>): <short description>
test(<module>): <short description>
chore(<module>): <short description>
refactor(<module>): <short description>

Examples:
  feat(pos-profile): add shift lock enforcement in clone API
  fix(psv): correct opening balance calculation
  docs(billing): update API reference for hold_bill endpoint
```

---

## 15. Documentation

SMRITI Retail OS maintains a governed documentation library with **211+ registered documents** across 9 categories.

### Documentation Categories

| Category | Folder | Documents |
|---|---|---|
| Product Overview | `docs/01-product/` | Product briefs, executive summaries |
| User Guides | `docs/02-user-guide/` | Step-by-step usage guides |
| Admin Guides | `docs/03-admin-guide/` | Setup and configuration |
| Operations | `docs/04-operations/` | Runbooks, SOPs |
| Developer Docs | `docs/05-developer/` | Architecture, implementation guides |
| API Reference | `docs/06-api/` | Whitelisted endpoint references |
| Knowledge Base | `docs/07-kb/` | Troubleshooting, FAQ |
| Governance | `docs/08-governance/` | Policies, constitution, BRDs |
| Reports | `docs/reports/` | Health audits, compliance reports |

### Documentation Governance

Every document must have YAML frontmatter:

```yaml
---
id: "<CATEGORY-NNN>"
title: "<Human Readable Title>"
category: "<Category>"
status: "Published"
version: "<X.Y.Z>"
created: "<YYYY-MM-DD>"
author: "Jawahar R. Mallah"
---
```

### Key Documents

- **[DOCUMENTATION_INDEX.md](./docs/DOCUMENTATION_INDEX.md)** — Master registry (211 entries)
- **[DOCUMENTATION_CONSTITUTION.md](./docs/DOCUMENTATION_CONSTITUTION.md)** — Governance rules
- **[DOCUMENTATION_STYLE_GUIDE.md](./docs/DOCUMENTATION_STYLE_GUIDE.md)** — Formatting standards

---

## 16. Governance Links

| Document | Description |
|---|---|
| [BRD-01 Branding & Attribution](./docs/08-governance/BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION.md) | Product names, attributions, domain names |
| [AI Content Policy (AI-GOV-01)](./docs/08-governance/AI_CONTENT_POLICY.md) | Directives for AI coding agents |
| [Architecture Constitution](./docs/08-governance/ARCHITECTURE_CONSTITUTION.md) | 15 inviolable architecture rules |
| [SMRITI-First UI Policy](./docs/08-governance/SMRITI_UI_POLICY.md) | Rule 7 — No Desk exposure |

---

## 17. Roadmap

```
✅ Sprint 1  — SMRITI Business Opportunity Report (ROI Calculator PDF)
✅ Sprint 2  — SMRITI Trial Leads CRM
✅ Sprint 2A — Security & Audit Validation
✅ Sprint 3A — Trial Activation DocTypes, Platform Admin, Commercial Sidebar
✅ Sprint 3B — Test Infrastructure (DocType schema sync)
✅ Sprint 3C — POS Profile Management (Repository → Service → API → UI)

⏳ Sprint 4  — Billing Experience Upgrade (SMRITI POS v2)
⏳ Sprint 5  — SMRITI Reports Center (Sales, Stock, GST, Outstanding)
⏳ Sprint 6  — Loyalty & Promotions Engine
⏳ Sprint 7  — PSV Advanced Analytics (Aging, Capital Locked, Recovery)
⏳ Sprint 8  — PDT (Predictive Distribution Twin) v2
⏳ Sprint 9  — Mobile PWA (Offline-first cashier experience)
⏳ Sprint 10 — Tally Integration Layer
```

---

## 18. License

```
MIT License
Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All Rights Reserved.

SMRITI Retail OS is released under the MIT License.
Free for commercial use. Attribution required.

All open-source licensing notices for ERPNext and Frappe
must be preserved in source code files.
```

---

## Built On

| Framework | Version | Role |
|---|---|---|
| [Frappe Framework](https://frappeframework.com) | v16 | Application server, ORM, auth |
| [ERPNext](https://erpnext.com) | v16 | System of Record (accounting, inventory, POS) |
| [India Compliance](https://github.com/resilient-tech/india-compliance) | v16 | GST, e-Invoice, e-Waybill |

---

<div align="center">

**SMRITI Retail OS™ — Always Decision-Ready.**

*Developed by AITDL – AI Technology & Development Lab*
*Powered by ERPNext® & Frappe® Framework*

**Jawahar R. Mallah** — Founder & Chief Architect, AITDL
*20+ years in Retail Technology, Distribution Systems & Enterprise Application Design*

</div>
