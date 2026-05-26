Bhai, SMRITI ke liye original GitHub README deta hoon:

---

```markdown
# SMRITI Retail OS

> Shoper9-style Retail Experience Layer for ERPNext

SMRITI is not a new ERP.
It is a simplified retail operating system
built on top of ERPNext + India Compliance.

---

## What is SMRITI?

Most retail store owners don't need a full ERP.
They need:
- Fast billing
- Simple inventory
- GST compliance
- Easy customer management

ERPNext is powerful but complex.
SMRITI makes it simple.

---

## Architecture

```
┌─────────────────────────────────┐
│         SMRITI Retail OS        │
│      (UI + Experience Layer)    │
├─────────────────────────────────┤
│            ERPNext              │
│  Inventory · Accounting · POS   │
├─────────────────────────────────┤
│       India Compliance          │
│  GST · e-Invoice · e-Waybill    │
└─────────────────────────────────┘
```

SMRITI never duplicates ERPNext logic.
It only simplifies the interface.

---

## Features

### Masters
- ✅ Product Master (simplified Item)
- ✅ Customer Master (mobile-first)
- ✅ Supplier Master (GSTIN validated)

### Billing
- ✅ Barcode-first POS billing
- ✅ Cash / UPI / Card / Split payment
- ✅ Hold & Recall bill
- ✅ Loyalty points redemption
- ✅ Manager override with PIN
- ✅ Thermal print (58mm / 80mm)

### Inventory
- ✅ GRN (Goods Receipt)
- ✅ Stock Transfer
- ✅ Stock Adjustment
- ✅ Stock Audit / Physical count
- ✅ Barcode label printing (ZPL/PRN)

### Day Operations
- ✅ Day Open (POS Opening Entry)
- ✅ Day Close (POS Closing Entry)
- ✅ Cash reconciliation
- ✅ Z-Report

### Experience
- ✅ Dark retail theme
- ✅ Custom SMRITI sidebar
- ✅ Role-based navigation
- ✅ Keyboard shortcuts (F2-F12)
- ✅ Mobile friendly

---

## Roles

| Role | Access |
|---|---|
| SMRITI Cashier | Billing only |
| SMRITI Store Manager | Full retail ops |
| System Manager | Full ERPNext |

---

## Requirements

- Frappe Framework 16.x
- ERPNext 16.x
- India Compliance 16.x
- Python 3.11+
- MariaDB 10.6+

---

## Installation

```bash
# Get the app
bench get-app https://github.com/yourname/smriti_retail_os

# Install on site
bench --site yoursite install-app smriti_retail_os

# Migrate
bench --site yoursite migrate

# Build assets
bench build --app smriti_retail_os

# Clear cache
bench --site yoursite clear-cache

# Restart
bench restart
```

---

## After Installation

1. Create roles:
   - SMRITI Cashier
   - SMRITI Store Manager

2. Configure POS Profile

3. Setup India Compliance (GST)

4. Create Walk-In Customer

5. Login as Store Manager
   → lands on SMRITI Dashboard

---

## Tech Stack

```
Backend   →  Python + Frappe Framework
Frontend  →  Vanilla JS + CSS Variables
Database  →  MariaDB (via ERPNext)
GST       →  India Compliance
Printing  →  ZPL / Raw PRN
```

---

## Design Principles

```
1. No new DocTypes
2. No ERPNext core modification
3. No duplicate business logic
4. UI layer only
5. Upgrade safe
6. India-first (GST, INR, Hindi)
```

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| F2 | Item search |
| F3 | Customer lookup |
| F4 | Hold bill |
| F5 | Recall bill |
| F6 | Payment |
| F9 | Submit & print |
| F12 | Reprint last bill |

---

## License

MIT License

---

## Built With ❤️ for Indian Retail

SMRITI is built for small and medium
Indian retail stores who want modern
billing without ERP complexity.

GST compliant. India ready.
```

---

**Aur ye `smriti_retail_os/README.md` mein bhi save karo:**

```bash
# GitHub pe push karo
cd apps/smriti_retail_os
git add README.md
git commit -m "docs: Add SMRITI Retail OS README"
git push origin main
```

---

Chahiye toh GitHub repo description, topics aur social preview image ke liye bhi content de sakta hoon.
