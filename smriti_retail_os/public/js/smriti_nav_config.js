/**
 * @file: smriti_retail_os/public/js/smriti_nav_config.js
 * @description: SMRITI Navigation Configuration — Single source of truth for all sidebar items.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-12
 * @version: 1.9.1
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
// ─────────────────────────────────────────
// SMRITI Navigation Configuration
// Single source of truth for all sidebar items
// ─────────────────────────────────────────

const SMRITI_NAV_META = {
  version: "1.9.1",
  updated_at: "2026-06-12",
  source: "SMRITI Sidebar Restructure v1.9.1"
};

// ─────────────────────────────────────────
// Route Resolver — SMRITI COMPLIANT
// ─────────────────────────────────────────
// POLICY (AITDL Rule 7 + GEMINI.md Rule 7):
//   ALL routes must point to SMRITI www pages (/smriti_retail_os/www/).
//   Raw ERPNext /app/ DocType routes FORBIDDEN for end users.
//   Unbuilt pages → /smriti-coming-soon?feature=...
// ─────────────────────────────────────────

const SMRITI_ROUTE_MAP = {
  // ── Built SMRITI www pages (files exist in www/) ────────────────────
  "customers":              "/customers",         // www/customers.html ✅
  "suppliers":              "/suppliers",         // www/suppliers.html ✅
  "sales_invoice":          "/sales_invoices",    // www/sales_invoices.html ✅
  "sales_return":           "/sales_return",      // www/sales_return.html ✅
  "credit_note":            "/sales_invoices",    // www/sales_invoices.html ✅
  "delivery_note":          "/delivery_challan",  // www/delivery_challan.html ✅
  "purchase_receipt":       "/purchase_receipt",  // www/purchase_receipt.html ✅
  "purchase_invoice":       "/purchase_invoice",  // www/purchase_invoice.html ✅
  "payment_entry_receipt":  "/payments",          // www/payments.html ✅
  "payment_entry_payment":  "/payments",          // www/payments.html ✅
  "advance":                "/payments",          // www/payments.html ✅
  "stock_entry":            "/inventory",         // www/inventory.html ✅
  "warehouse":              "/inventory",         // www/inventory.html ✅
  "supplier_returns":       "/supplier-returns",  // www/supplier_returns.html ✅
  "audit_reports":          "/reports?report=security_audit_log",

};

function resolveSmritiRoute(key) {
  if (SMRITI_ROUTE_MAP[key]) return SMRITI_ROUTE_MAP[key];
  // Safety net: unknown key → coming-soon, NEVER raw /app/ route
  console.warn("[SMRITI] No route for key:", key, "→ coming-soon");
  return "/smriti-coming-soon?feature=" + encodeURIComponent(key.replace(/_/g, " "));
}

// ─────────────────────────────────────────
// Navigation Config
// status: active | coming_soon | hidden | disabled
// ─────────────────────────────────────────

const SMRITI_NAV = {
  sections: [
    {
      id: "masters",
      label: "Masters",
      status: "active",
      items: [
        { id: "product_catalog",
          label: "Product Catalog",
          route: "/products",
          standalone_route: "/products",
          status: "active" },
        { id: "brand_master",
          label: "Brand Master",
          route: "/brand-master",
          standalone_route: "/brand-master",
          status: "active" },
        { id: "item_master",
          label: "Item Master",
          route: "/app/smriti-item-master",
          standalone_route: "/item_master",
          status: "active" },
        { id: "category_master",
          label: "Category Master",
          route: "/category-master",
          standalone_route: "/category-master",
          status: "active" },
        { id: "scheme_creator",
          label: "Scheme Creator",
          route: "/scheme-creator",
          standalone_route: "/scheme-creator",
          status: "active" },
        { id: "customers",
          label: "Customers",
          route: resolveSmritiRoute("customers"),
          standalone_route: "/customers",
          status: "active" },
        { id: "suppliers",
          label: "Suppliers",
          route: resolveSmritiRoute("suppliers"),
          standalone_route: "/suppliers",
          status: "active" }
      ]
    },
    {
      id: "psv",
      label: "PSV",
      status: "active",
      items: [
        { id: "distributor_accounts",
          label: "Distributor Accounts",
          route: "/psv-channel-partner",
          standalone_route: "/psv-channel-partner",
          status: "active" },
        { id: "sales_uploads",
          label: "Sales Uploads",
          route: "/sales-upload",
          standalone_route: "/sales-upload",
          status: "active" },
        { id: "stock_uploads",
          label: "Stock Uploads",
          route: "/stock-audit",
          standalone_route: "/stock-audit",
          status: "active" },
        { id: "reconciliation",
          label: "Reconciliation",
          status: "coming_soon",
          progress: 0,
          eta: "PSV Phase 1.3" },
        { id: "psv_dashboard",
          label: "Dashboard",
          route: "/psv-dashboard",
          standalone_route: "/psv-dashboard",
          status: "active" },
        { id: "stock_aging",
          label: "Stock Aging",
          route: "/psv-aging",
          standalone_route: "/psv-aging",
          status: "active" },
        { id: "exception_analysis",
          label: "Exception Analysis",
          status: "coming_soon",
          progress: 0,
          eta: "PSV Phase 1.3" }
      ]
    },
    {
      id: "sales",
      label: "Sales",
      status: "active",
      items: [
        { id: "pos_billing",
          label: "POS Billing",
          route: "/billing",
          standalone_route: "/billing",
          status: "active" },
        { id: "sales_orders",
          label: "Sales Orders",
          route: "/sales-orders",
          standalone_route: "/sales-orders",
          status: "active" },
        { id: "tax_invoice",
          label: "Tax Invoice",
          route: resolveSmritiRoute("sales_invoice"),
          standalone_route: "/sales-invoices",
          status: "active" },
        { id: "sales_return",
          label: "Sales Return",
          route: resolveSmritiRoute("sales_return"),
          standalone_route: "/sales-returns",
          status: "active" },
        { id: "delivery_challan",
          label: "Delivery Challan",
          route: resolveSmritiRoute("delivery_note"),
          standalone_route: "/delivery-challans",
          status: "active" },
        { id: "credit_notes",
          label: "Credit Notes",
          route: resolveSmritiRoute("credit_note"),
          standalone_route: "/credit-notes",
          status: "active" }
      ]
    },
    {
      id: "purchase",
      label: "Purchase",
      status: "active",
      items: [
        { id: "purchase_orders",
          label: "Purchase Orders",
          route: "/purchase?tab=new-po",
          standalone_route: "/purchase?tab=new-po",
          status: "active" },
        { id: "grn_receipts",
          label: "GRN / Receipts",
          route: resolveSmritiRoute("purchase_receipt"),
          standalone_route: "/grn-receipts",
          status: "active" },
        { id: "purchase_invoice",
          label: "Purchase Invoice",
          route: resolveSmritiRoute("purchase_invoice"),
          standalone_route: "/purchase-invoices",
          status: "active" },
        { id: "supplier_returns",
          label: "Supplier Returns",
          route: resolveSmritiRoute("supplier_returns"),
          standalone_route: "/supplier-returns",
          status: "active" }
      ]
    },
    {
      id: "inventory",
      label: "Inventory",
      status: "active",
      items: [
        { id: "warehouses",
          label: "Warehouses",
          route: resolveSmritiRoute("warehouse"),
          standalone_route: "/warehouses",
          status: "active" },
        { id: "opening_stock",
          label: "Opening Stock",
          route: "/opening-stock",
          standalone_route: "/opening-stock",
          status: "active" },
        { id: "stock_operations",
          label: "Stock Operations",
          route: "/inventory-ops",
          standalone_route: "/inventory-ops",
          status: "active" },
        { id: "stock_transfer",
          label: "Stock Transfer",
          route: "/inventory?tab=transfer",
          standalone_route: "/inventory?tab=transfer",
          status: "active" },
        { id: "stock_adjustments",
          label: "Stock Adjustments",
          route: resolveSmritiRoute("stock_entry"),
          standalone_route: "/stock-adjustments",
          status: "active" },
        { id: "stock_audit",
          label: "Stock Audit",
          route: "/stock-audit",
          standalone_route: "/stock-audit",
          status: "active" },
        { id: "barcode_center",
          label: "Barcode Center",
          route: "/barcode-center",
          standalone_route: "/barcode-center",
          status: "active" },
        { id: "print_templates",
          label: "Print Templates",
          route: "/print-templates",
          standalone_route: "/print-templates",
          status: "active" }
      ]
    },
    {
      id: "finance",
      label: "Finance",
      status: "active",
      items: [
        { id: "receipts",
          label: "Receipts",
          route: resolveSmritiRoute("payment_entry_receipt"),
          standalone_route: "/receipts",
          status: "active" },
        { id: "payments",
          label: "Payments",
          route: resolveSmritiRoute("payment_entry_payment"),
          standalone_route: "/payments",
          status: "active" },
        { id: "advances",
          label: "Advances",
          route: resolveSmritiRoute("advance"),
          standalone_route: "/advances",
          status: "active" }
      ]
    },
    {
      id: "reports",
      label: "Reports",
      status: "active",
      items: [
        { id: "sales_reports",
          label: "Sales Reports",
          route: "/reports/sales",
          standalone_route: "/reports/sales",
          status: "active" },
        { id: "inventory_reports",
          label: "Inventory Reports",
          route: "/reports/inventory",
          standalone_route: "/reports/inventory",
          status: "active" },
        { id: "finance_reports",
          label: "Finance Reports",
          route: "/reports/finance",
          standalone_route: "/reports/finance",
          status: "active" },
        { id: "gst_reports",
          label: "GST Reports",
          route: "/reports/gst",
          standalone_route: "/reports/gst",
          status: "active" },
        { id: "psv_reports",
          label: "PSV Reports",
          route: "/reports/psv",
          standalone_route: "/reports/psv",
          status: "active" },
        { id: "billing_metrics",
          label: "Billing Metrics",
          route: "/billing-metrics",
          standalone_route: "/billing-metrics",
          status: "active" },
        { id: "audit_reports",
          label: "Audit Reports",
          route: "/reports?report=security_audit_log",
          standalone_route: "/reports?report=security_audit_log",
          status: "active" }
      ]
    },
    {
      id: "administration",
      label: "Administration",
      status: "active",
      items: [
        { id: "day_open",
          label: "Day Open",
          route: "/shift",
          standalone_route: "/shift",
          status: "active" },
        { id: "day_close",
          label: "Day Close",
          route: "/shift",
          standalone_route: "/shift",
          status: "active" },
        { id: "shift_register",
          label: "Shift / Register",
          route: "/shift",
          standalone_route: "/shift",
          status: "active" },
        { id: "user_management",
          label: "User Management",
          route: "/security-workflows?tab=users",
          standalone_route: "/security-workflows?tab=users",
          status: "active" },
        { id: "roles_permissions",
          label: "Roles & Permissions",
          route: "/security-workflows?tab=roles",
          standalone_route: "/security-workflows?tab=roles",
          status: "active" },
        { id: "config_portal",
          label: "Config Portal",
          route: "/config-portal",
          standalone_route: "/config-portal",
          status: "active" },
        { id: "security_workflows",
          label: "Security & Workflows",
          route: "/security-workflows",
          standalone_route: "/security-workflows",
          status: "active" },
        { id: "audit_logs",
          label: "Audit Logs",
          route: "/smriti-security-log",
          standalone_route: "/smriti-security-log",
          status: "active" },
        { id: "backup_restore",
          label: "Backup & Restore",
          route: "/backup",
          standalone_route: "/backup",
          status: "active" }
      ]
    },
    {
      id: "help_desk",
      label: "Help Desk",
      status: "active",
      items: [
        { id: "user_manual",
          label: "User Manual",
          route: "/smriti-help",
          standalone_route: "/smriti-help",
          status: "active" },
        { id: "release_notes",
          label: "Release Notes",
          status: "coming_soon",
          progress: 0,
          eta: "Q3 2026" },
        { id: "support",
          label: "Support",
          status: "coming_soon",
          progress: 0,
          eta: "Q3 2026" }
      ]
    },
    {
      id: "ai_hub",
      label: "AI Hub",
      status: "hidden",
      items: [
        { id: "demand_forecasts",
          label: "Demand Forecasts",
          status: "hidden" },
        { id: "cashier_performance",
          label: "Cashier Performance",
          status: "hidden" }
      ]
    }
  ]
};
