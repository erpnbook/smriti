# SMRITI Retail OS — Task Checklist

## ✅ Phase 1 — Masters
- [x] Item form simplification (item.js)
- [x] Customer form simplification (customer.js)
- [x] Supplier form simplification (supplier.js)
- [x] Custom fields on Item, Customer, Supplier, POS Invoice

## ✅ Phase 2 — Billing Engine
- [x] smriti-billing page (JS, CSS, JSON)
- [x] billing_api.py — add_item_by_barcode, hold_bill, recall_bill, submit_bill
- [x] validate_manager_override API
- [x] Keyboard shortcuts (F2–F12)

## ✅ Phase 3 — Inventory
- [x] smriti-inventory page
- [x] inventory_api.py — GRN, transfer, adjustment, audit
- [x] smriti-purchase page
- [x] purchase_api.py

## ✅ Phase 4 — Day Operations
- [x] smriti-shift page
- [x] shift_api.py — open_shift, close_shift, get_shift_status
- [x] Shift badge in sidebar footer (clickable)

## ✅ Phase 5 — Branding & Theme
- [x] smriti_theme.css — dark glassmorphic theme
- [x] smriti_branding.css — ERPNext UI override
- [x] smriti_sidebar.css + smriti_sidebar.js
- [x] login.html — custom branded login page
- [x] hooks.py — brand_html, CSS/JS includes, route rules
- [x] boot.py — role-based redirect, System Manager bypass
- [x] main.js — safety net, branding scrubber
- [x] Docker snapshot v1.0

## ✅ Phase 6 — Reports
- [x] reports_api.py — Sales, Stock, GST, Outstanding, Quick Stats
- [x] smriti-reports page (JSON, JS, Python)
- [x] smriti_reports.js — 4-tab UI with charts, filters, CSV export
- [x] smriti-reports.css — dark theme matching SMRITI
- [x] Sidebar updated — Reports → /app/smriti-reports (Store Manager only)
- [x] main.js route map updated — smriti-reports → "reports"
- [x] hooks.py — reports CSS/JS registered
- [x] bench build + migrate + clear-cache + restart ✅
- [x] Git push → github.com/erpnbook/smriti ✅

## ✅ Phase 6.5 — Sales & Purchase DocType Integration
- [x] Simplified Sales Invoice client script (`sales_invoice.js`)
- [x] Simplified Purchase Order client script (`purchase_order.js`)
- [x] Simplified Purchase Receipt client script (`purchase_receipt.js`)
- [x] Standard DocType views integrated into SMRITI Sidebar (Sales Invoices, Purchase Orders, Purchase Receipts)
- [x] Route mapping and auto-active navigation logic in `main.js`
- [x] DocType JS controllers registered in `hooks.py`
- [x] Bench built, container caches cleared, and changes pushed to GitHub ✅

## ✅ Phase 7 — Loyalty & Promotions
- [x] loyalty_api.py — get_points, get_schemes, save_scheme, enroll_customer
- [x] SMRITI Loyalty schemes custom configuration page (`smriti-loyalty`)
- [x] Dynamic loyalty points balance & INR discount equivalent display in customer card on `smriti-billing`
- [x] Checkout points redemption validation & reactive due balance adjustments
- [x] Auto-provisioning of default "SMRITI Standard Loyalty" program on migration
- [x] Workspace & SMRITI Sidebar integrated links (🎁) for Managers
- [x] Successful compile, cache flush, and git push to GitHub ✅

## ✅ Phase 8 — Mobile & PWA Optimization
- [x] PWA configuration — created `manifest.json` enabling app install directly to device homescreens
- [x] Service Worker caching — created `sw.js` to pre-cache critical dark glassmorphic CSS, JS, and brand logos
- [x] Registration script — embedded SW registration inside custom `www/login.html` head
- [x] Responsive tablet & mobile CSS — added Media Queries to `smriti-billing.css` for grid stacking, scrollable carts, and split pane scaling
- [x] Touch-optimized Live Camera Barcode Scanner — added camera scanning button and EAN/Code-128 native decoding stream modal on `smriti-billing`
- [x] Production build compiled, docker caches flushed, and committed to GitHub ✅
