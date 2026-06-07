# SMRITI Retail OS
### Keyboard-First Retail Experience Layer for ERPNext + India Compliance

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext: v16](https://img.shields.io/badge/ERPNext-v16-blue.svg)](https://github.com/frappe/erpnext)
[![Frappe: v16](https://img.shields.io/badge/Frappe-v16-blue.svg)](https://github.com/frappe/frappe)
[![India Compliance: v16](https://img.shields.io/badge/India_Compliance-v16-green.svg)](https://github.com/resilient-tech/india-compliance)

---

## 🧠 What is SMRITI?

SMRITI Retail OS is **not a new ERP**.

It is a **Retail Experience Layer** — a thin,
upgrade-safe Frappe application that sits on top
of ERPNext and transforms it into a
keyboard-first retail operating system.

ERPNext remains the engine for:
- Inventory management
- Accounting & ledgers
- POS infrastructure
- GST & taxation (via India Compliance)

SMRITI only provides:
- Simplified retail UI
- Role-based screen routing
- Barcode-first workflows
- Dark retail theme
- Retail-specific APIs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           SMRITI Retail OS              │
│                                         │
│  Custom Pages  │  Client Scripts        │
│  CSS Theme     │  Whitelisted APIs      │
│  Boot Hooks    │  Sidebar Component     │
├─────────────────────────────────────────┤
│              ERPNext v16                │
│                                         │
│  Item  │  Customer  │  Supplier         │
│  POS Invoice  │  Stock Entry            │
│  Purchase Receipt  │  Payment Entry     │
├─────────────────────────────────────────┤
│          India Compliance v16           │
│                                         │
│  GST  │  GSTIN Validation               │
│  e-Invoice  │  e-Waybill                │
│  GSTR Reports  │  HSN Codes             │
├─────────────────────────────────────────┤
│         Frappe Framework v16            │
│                                         │
│  ORM  │  REST API  │  Auth              │
│  Boot Session  │  Hooks  │  Jobs        │
└─────────────────────────────────────────┘
```

### Golden Rules (NEVER violate)

```
1. NEVER modify ERPNext core files
2. NEVER modify India Compliance files
3. NEVER create duplicate accounting logic
4. NEVER create duplicate GST logic
5. NEVER create duplicate inventory logic
6. ALWAYS use existing ERPNext DocTypes
7. ALWAYS extend via hooks, not patches
8. System Manager must always see
   standard ERPNext — unaffected
```

---

## 📁 Project Structure

```
smriti_retail_os/
│
├── smriti_retail_os/
│   │
│   ├── hooks.py                 # App registration,
│   │                            # CSS/JS includes,
│   │                            # boot_session,
│   │                            # doc_events,
│   │                            # brand_html
│   │
│   ├── boot.py                  # Role-based login redirect
│   │                            # ERPNext branding override
│   │                            # bootinfo patching
│   │
│   ├── hooks_logic.py           # Server-side doc event handlers
│   │                            # Item tax sync
│   │                            # Address auto-creation
│   │                            # Payment terms sync
│   │
│   ├── billing_api.py           # POS billing whitelisted APIs
│   │                            # add_item_by_barcode
│   │                            # hold_bill / recall_bill
│   │                            # submit_bill
│   │                            # validate_manager_override
│   │
│   ├── inventory_api.py         # Inventory whitelisted APIs
│   │                            # create_grn
│   │                            # create_stock_transfer
│   │                            # create_stock_adjustment
│   │                            # create_stock_audit
│   │
│   ├── barcode_api.py           # Barcode printing APIs
│   │                            # get_items_for_printing
│   │                            # generate_prn (ZPL)
│   │
│   ├── shift_api.py             # Day open/close APIs
│   │                            # open_shift
│   │                            # close_shift
│   │                            # get_shift_status
│   │
│   ├── master_api.py            # Master data APIs
│   │                            # search_item
│   │                            # search_customer
│   │
│   ├── setup.py                 # After install hook
│   │                            # Creates custom fields
│   │                            # Creates SMRITI roles
│   │                            # Creates workspace
│   │
│   ├── public/
│   │   ├── css/
│   │   │   ├── smriti_theme.css      # Dark theme CSS variables
│   │   │   ├── smriti_sidebar.css    # Custom sidebar styles
│   │   │   └── smriti_branding.css   # Branding overrides
│   │   │
│   │   └── js/
│   │       ├── smriti_sidebar.js     # Reusable sidebar component
│   │       │                         # SMRITI.renderSidebar(page)
│   │       ├── main.js               # Global desk JS
│   │       │                         # Sidebar lockdown
│   │       │                         # Role-based hiding
│   │       ├── item.js               # Item form simplification
│   │       ├── customer.js           # Customer form simplification
│   │       └── supplier.js           # Supplier form simplification
│   │
│   ├── page/
│   │   ├── smriti-billing/           # POS Billing screen
│   │   │   ├── smriti-billing.json   # Page registration
│   │   │   ├── smriti-billing.js     # Billing controller
│   │   │   └── smriti-billing.css    # Billing styles
│   │   │
│   │   ├── smriti-inventory/         # Inventory screen
│   │   │   ├── smriti-inventory.json
│   │   │   ├── smriti-inventory.js
│   │   │   └── smriti-inventory.css
│   │   │
│   │   ├── smriti-barcode/           # Barcode printing screen
│   │   │   ├── smriti-barcode.json
│   │   │   ├── smriti-barcode.js
│   │   │   └── smriti-barcode.css
│   │   │
│   │   ├── smriti-desk/              # Store Manager dashboard
│   │   │   ├── smriti-desk.json
│   │   │   ├── smriti-desk.js
│   │   │   └── smriti-desk.css
│   │   │
│   │   └── smriti-shift/             # Day open/close screen
│   │       ├── smriti-shift.json
│   │       ├── smriti-shift.js
│   │       └── smriti-shift.css
│   │
│   ├── www/
│   │   └── login.html                # Custom SMRITI login page
│   │
│   └── tests/
│       ├── test_billing_api.py
│       ├── test_inventory_api.py
│       └── test_hooks.py
│
├── hooks.py                     # (root level — app metadata)
├── setup.py
├── requirements.txt
└── README.md
```

---

## 🔧 Technical Implementation

### hooks.py — Key Registrations

```python
# Branding
brand_html = "<b style='color:#e94560'>SMRITI Retail OS</b>"

# CSS/JS — load order matters
app_include_css = [
    "/assets/smriti_retail_os/css/smriti_theme.css",
    "/assets/smriti_retail_os/css/smriti_sidebar.css",
    "/assets/smriti_retail_os/css/smriti_branding.css"
]
app_include_js = [
    "/assets/smriti_retail_os/js/smriti_sidebar.js",
    "/assets/smriti_retail_os/js/main.js"
]

# Boot — role based routing
boot_session = "smriti_retail_os.boot.boot_session"
extend_bootinfo = "smriti_retail_os.boot.extend_bootinfo"

# Form simplification
doctype_js = {
    "Item":     "public/js/item.js",
    "Customer": "public/js/customer.js",
    "Supplier": "public/js/supplier.js"
}

# Server-side automation
doc_events = {
    "Item": {
        "before_save": "smriti_retail_os.hooks_logic.sync_item_taxes_and_prices"
    },
    "Customer": {
        "on_update": "smriti_retail_os.hooks_logic.sync_customer_address"
    },
    "Supplier": {
        "on_update": "smriti_retail_os.hooks_logic.sync_supplier_address_and_credit_days"
    }
}

# Login page override
website_route_rules = [
    {"from_route": "/login", "to_route": "login"}
]
```

### boot.py — Role Based Routing

```python
def boot_session(bootinfo):
    extend_bootinfo(bootinfo)

def extend_bootinfo(bootinfo):
    # 1. Apply SMRITI branding to bootinfo
    _apply_branding(bootinfo)

    user = frappe.session.user
    if user == "Administrator":
        return

    roles = frappe.get_roles(user)

    # 2. System Manager — NO redirect, normal ERPNext
    if "System Manager" in roles:
        return

    # 3. Cashier → Billing screen
    if "SMRITI Cashier" in roles:
        if frappe.db.exists("Page", "smriti-billing"):
            bootinfo.default_route = "/app/smriti-billing"
        else:
            bootinfo.default_route = "/app/point-of-sale"

    # 4. Store Manager → Dashboard
    elif "SMRITI Store Manager" in roles:
        if frappe.db.exists("Page", "smriti-desk"):
            bootinfo.default_route = "/app/smriti-desk"
        else:
            bootinfo.default_route = "/app"
```

### Custom Fields Added to ERPNext DocTypes

```
Item DocType:
├── custom_is_retail_item    (Check, default=1)
├── custom_department        (Link → Item Group)
├── custom_gst_percentage    (Select: 0,5,12,18,28)
├── custom_mrp               (Currency)
├── custom_barcode_size      (Select: 50x25,50x30,75x50,100x50)
└── custom_current_stock_html (HTML — display only)

Customer DocType:
├── custom_address_text      (Small Text)
├── custom_birthday          (Date)
└── custom_anniversary       (Date)

Supplier DocType:
├── custom_address_text      (Small Text)
└── custom_credit_days       (Int)

POS Invoice DocType:
├── custom_is_held           (Check)
├── custom_held_by           (Data)
└── custom_hold_time         (Datetime)
```

### ERPNext DocType Mapping

```
SMRITI Concept          ERPNext DocType
──────────────────────────────────────────
Product Master       →  Item
Customer Master      →  Customer
Supplier Master      →  Supplier
Billing              →  POS Invoice
Hold Bill            →  POS Invoice (Draft, custom_is_held=1)
GRN                  →  Purchase Receipt
Stock Transfer       →  Stock Entry (Material Transfer)
Stock Adjustment     →  Stock Entry (Material Issue/Receipt)
Stock Audit          →  Stock Reconciliation
Day Open             →  POS Opening Entry
Day Close            →  POS Closing Entry
Loyalty              →  Loyalty Point Entry
Promotions           →  Pricing Rule
Address              →  Address (linked)
Payment Terms        →  Payment Terms Template
Manager Audit Log    →  Comment (on POS Invoice)
```

---

## 👥 Roles & Permissions

```
SMRITI Cashier:
├── POS Invoice      → Create, Read, Write
├── Customer         → Create, Read, Write
├── Item             → Read only
├── smriti-billing   → Full access
└── Everything else  → No access

SMRITI Store Manager:
├── Item             → Create, Read, Write
├── Customer         → Create, Read, Write
├── Supplier         → Create, Read, Write
├── Stock Entry      → Create, Read, Write
├── Purchase Receipt → Create, Read, Write
├── All SMRITI pages → Full access
└── ERPNext modules  → Hidden

System Manager:
└── Everything       → Full ERPNext access
                       SMRITI theme bypassed
                       Normal ERPNext desk
```

---

## 🎨 Theme System

SMRITI uses pure CSS variables — no JS DOM hacks.

```css
/* All theme colors defined as variables */
:root {
    --smriti-primary:   #e94560;  /* Red — action color */
    --smriti-bg:        #0b0f19;  /* Dark navy — background */
    --smriti-surface:   #16213e;  /* Surface — cards/sidebar */
    --smriti-surface2:  #1a2744;  /* Surface 2 — inputs */
    --smriti-border:    #2a3a5c;  /* Border color */
    --smriti-text:      #e2e8f0;  /* Primary text */
    --smriti-muted:     #8892a4;  /* Muted text */
}
```

Theme scoped to `body.smriti-user-layout` —
System Manager never sees dark theme.

---

## ⌨️ Keyboard Shortcuts

```
F2   → Item search (catalog modal)
F3   → Customer lookup
F4   → Hold bill
F5   → Recall held bill
F6   → Open payment drawer
F7   → Apply discount
F9   → Submit bill + print
F10  → Edit quantity
F12  → Reprint last bill
DEL  → Remove item (manager override)
ESC  → Cancel / close modal
```

---

## 📦 Installation

### Prerequisites

```bash
# ERPNext v16 bench setup required
# Docker recommended for production

bench --version  # should be 5.x
python --version # should be 3.11+
```

### Install Steps

```bash
# Step 1 — Get India Compliance (if not installed)
bench get-app --branch version-16 \
  https://github.com/resilient-tech/india-compliance.git
bench --site yoursite install-app india_compliance

# Step 2 — Get SMRITI
bench get-app \
  https://github.com/yourname/smriti_retail_os.git
bench --site yoursite install-app smriti_retail_os

# Step 3 — Migrate
bench --site yoursite migrate

# Step 4 — Build assets
bench build --app smriti_retail_os

# Step 5 — Clear cache
bench --site yoursite clear-cache

# Step 6 — Restart
bench restart
```

### Post Installation

```bash
# Verify installation
bench --site yoursite list-apps

# Expected output:
# frappe
# erpnext
# india_compliance
# smriti_retail_os

# Run tests
bench --site yoursite run-tests \
  --app smriti_retail_os
```

---

## ⚙️ Configuration After Install

### 1. Create POS Profile
```
ERPNext → Point of Sale → POS Profile → New
- Company: Your Company
- Warehouse: Your Store Warehouse
- Currency: INR
- Payments: Cash, UPI, Card
```

### 2. Create Walk-In Customer
```
ERPNext → CRM → Customer → New
- Customer Name: Walk-In Customer
- Customer Type: Individual
```

### 3. Setup India Compliance
```
India Compliance → Settings
- Company GSTIN
- HSN Codes
- Tax Templates
```

### 4. Assign Roles to Users
```
ERPNext → Users → [Select User]
- Add Role: SMRITI Cashier
  OR
- Add Role: SMRITI Store Manager
```

---

## 🔌 API Reference

### Billing APIs
```
POST /api/method/smriti_retail_os.billing_api.add_item_by_barcode
Args: barcode, price_list
Returns: item_code, item_name, rate, mrp, gst_percentage, available_qty

POST /api/method/smriti_retail_os.billing_api.hold_bill
Args: cashier, customer, items (JSON)
Returns: invoice_name, message

POST /api/method/smriti_retail_os.billing_api.recall_bill
Args: cashier
Returns: list of held invoices

POST /api/method/smriti_retail_os.billing_api.submit_bill
Args: cashier, customer, items, payments,
      loyalty_points, invoice_name
Returns: invoice, grand_total, print_url

POST /api/method/smriti_retail_os.billing_api.validate_manager_override
Args: manager_user, manager_password,
      action_type, invoice_name
Returns: authorized (bool), manager
```

### Inventory APIs
```
POST /api/method/smriti_retail_os.inventory_api.create_grn
Args: supplier, invoice_no, items
Returns: receipt_name

POST /api/method/smriti_retail_os.inventory_api.create_stock_transfer
Args: from_warehouse, to_warehouse, items
Returns: entry_name

POST /api/method/smriti_retail_os.inventory_api.create_stock_adjustment
Args: items, reason
Returns: entry_name

POST /api/method/smriti_retail_os.inventory_api.create_stock_audit
Args: items
Returns: reconciliation_name

GET /api/method/smriti_retail_os.inventory_api.get_stock_summary
Args: warehouse (optional)
Returns: item wise stock list
```

### Shift APIs
```
POST /api/method/smriti_retail_os.shift_api.open_shift
Args: opening_cash, pos_profile
Returns: opening_entry_name

POST /api/method/smriti_retail_os.shift_api.close_shift
Args: declared_cash, declared_card,
      declared_upi, opening_entry
Returns: closing_entry_name, difference

GET /api/method/smriti_retail_os.shift_api.get_shift_status
Returns: status (Open/Closed), cashier
```

### Barcode APIs
```
GET /api/method/smriti_retail_os.barcode_api.get_items_for_printing
Args: filters, source_doctype, source_name
Returns: items list with print_qty

POST /api/method/smriti_retail_os.barcode_api.generate_prn
Args: items (JSON), label_size
Returns: ZPL/PRN string for thermal printer
```

---

## 🧪 Testing

```bash
# Run all SMRITI tests
bench --site yoursite run-tests \
  --app smriti_retail_os

# Run specific test file
bench --site yoursite run-tests \
  --app smriti_retail_os \
  --module smriti_retail_os.tests.test_billing_api

# Expected: All tests pass
# test_add_item_by_barcode      ✔
# test_hold_and_recall_bill     ✔
# test_submit_bill              ✔
# test_manager_override         ✔
# test_search_customer          ✔
# test_create_grn               ✔
# test_stock_transfer           ✔
# test_stock_audit              ✔
# test_customer_address_sync    ✔
# test_supplier_credit_days     ✔
```

---

## 🐳 Docker Production Setup

```bash
# Build and start
docker compose -f pwd.yml up -d

# Apply SMRITI
docker compose -f pwd.yml exec backend \
  bench --site frontend install-app smriti_retail_os

# Build assets
docker compose -f pwd.yml exec backend \
  bench build --app smriti_retail_os

# Create permanent snapshot
docker commit smriti_retail_os-backend-1 \
  smriti-retail-os:v1.0

# Save image (permanent backup)
docker save smriti-retail-os:v1.0 \
  -o smriti_retail_os_v1.0.tar

# Restore anytime
docker load -i smriti_retail_os_v1.0.tar
```

---

## 🤖 AI Agent Development Guide

> This section is for AI agents (Claude Code, Cursor, Gemini)
> working on SMRITI codebase.

### Context

```
SMRITI = UI layer only
ERPNext = business logic engine
India Compliance = GST engine

NEVER duplicate what ERPNext already does.
ALWAYS check if ERPNext has an existing
DocType/API before building new.
```

### Before Making Any Change

```
1. Read hooks.py first — understand
   what is registered

2. Read boot.py — understand
   role routing logic

3. Check existing APIs in:
   billing_api.py
   inventory_api.py
   shift_api.py
   barcode_api.py

4. Verify ERPNext DocType exists
   before creating custom field
```

### Adding a New Feature

```
Step 1: Identify ERPNext DocType to use
Step 2: Add minimum custom fields only
Step 3: Write whitelisted API in relevant _api.py
Step 4: Add frontend in relevant page JS
Step 5: Add test in tests/
Step 6: Update hooks.py if needed
Step 7: bench build + migrate + clear-cache
```

### Common Mistakes to Avoid

```
❌ Creating new DocType for billing data
   → Use POS Invoice

❌ Writing GST calculation logic
   → Use India Compliance Item Tax Template

❌ Creating custom stock ledger
   → Use Stock Entry / Purchase Receipt

❌ JS innerText for branding
   → Use brand_html hook + CSS ::after

❌ Hardcoded CSS class selectors
   → Use CSS variables

❌ Redirecting System Manager
   → Always check and bypass

❌ pos_invoice.docstatus = 1
   → Use pos_invoice.submit()

❌ get_decrypted_password for PIN
   → Use frappe.auth.check_password()
```

### Debug Commands

```bash
# Check app installed
bench --site frontend list-apps

# Check custom fields exist
bench --site frontend execute "
import frappe
print(frappe.db.get_all(
    'Custom Field',
    filters={'dt': 'Item', 'fieldname': ['like', 'custom_%']},
    pluck='fieldname'
))
"

# Check pages registered
bench --site frontend execute "
import frappe
pages = ['smriti-billing','smriti-desk',
         'smriti-inventory','smriti-barcode',
         'smriti-shift']
for p in pages:
    print(p, '→', frappe.db.exists('Page', p))
"

# Check boot redirect working
bench --site frontend execute "
import frappe
frappe.set_user('cashier@test.com')
from smriti_retail_os.boot import extend_bootinfo
import types
b = types.SimpleNamespace()
extend_bootinfo(b)
print(b.default_route)
"

# Test billing API
bench --site frontend execute "
import frappe
frappe.set_user('Administrator')
from smriti_retail_os.billing_api \
    import add_item_by_barcode
print(add_item_by_barcode('TEST-BARCODE'))
"

# Rebuild assets
bench build --app smriti_retail_os --force
bench --site frontend clear-cache
bench restart
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
```

---

## 🗺️ Roadmap

```
✅ Phase 1 — Masters
   Product, Customer, Supplier

✅ Phase 2 — Billing Engine
   POS, Hold/Recall, Payments, Print

✅ Phase 3 — Inventory
   GRN, Transfer, Adjustment, Audit

✅ Phase 4 — Day Operations
   Open/Close shift, Reconciliation

✅ Phase 5 — Branding & Theme
   Dark theme, Login page, Sidebar

⏳ Phase 6 — Reports
   Sales, Stock, GST, Outstanding

⏳ Phase 7 — Loyalty & Promotions
   Points, Tiers, Discount schemes

⏳ Phase 8 — Mobile App
   PWA or React Native wrapper
```

---

## 🤝 Contributing

```bash
# Fork and clone
git clone https://github.com/yourname/smriti_retail_os

# Create branch
git checkout -b feature/your-feature

# Make changes following rules above

# Test
bench --site frontend run-tests \
  --app smriti_retail_os

# Commit
git add .
git commit -m "feat: your feature description"

# Push
git push origin feature/your-feature

# Create Pull Request
```

---

## 📄 License

MIT License — Free for commercial use.

---

## 🙏 Built On

- [Frappe Framework](https://frappeframework.com)
- [ERPNext](https://erpnext.com)
- [India Compliance](https://github.com/resilient-tech/india-compliance)

---

*SMRITI — Smart Retail Intelligence.*
*Built for Indian retail. Powered by ERPNbook.*
