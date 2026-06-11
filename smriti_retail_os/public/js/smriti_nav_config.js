/**
 * @file: smriti_retail_os/public/js/smriti_nav_config.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
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
// Route Resolver
// Update this map when native SMRITI pages
// replace ERPNext pages. Sidebar auto-updates.
// ─────────────────────────────────────────

const SMRITI_ROUTE_MAP = {
  "users":                    "/app/user",
  "roles":                    "/app/role",
  "audit_logs":               "/app/activity-log",
  "customers":                "/app/customer",
  "suppliers":                "/app/supplier",
  "sales_order":              "/app/sales-order",
  "sales_invoice":            "/app/sales-invoice",
  "sales_return":             "/app/sales-return",
  "delivery_note":            "/app/delivery-note",
  "credit_note":              "/app/sales-invoice",
  "purchase_order":           "/app/purchase-order",
  "purchase_receipt":         "/app/purchase-receipt",
  "purchase_invoice":         "/app/purchase-invoice",
  "warehouse":                "/app/warehouse",
  "stock_entry":              "/app/stock-entry",
  "payment_entry_receipt":    "/app/payment-entry",
  "payment_entry_payment":    "/app/payment-entry",
  "advance":                  "/app/payment-entry",
};

function resolveSmritiRoute(key) {
  return SMRITI_ROUTE_MAP[key] || "/app/" + key;
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
          route: "/product-catalog",
          status: "active" },
        { id: "brand_master",
          label: "Brand Master",
          status: "coming_soon",
          progress: 20,
          eta: "Q3 2026" },
        { id: "item_master",
          label: "Item Master",
          route: "/item-master",
          status: "active" },
        { id: "category_master",
          label: "Category Master",
          status: "coming_soon",
          progress: 10,
          eta: "Q3 2026" },
        { id: "scheme_creator",
          label: "Scheme Creator",
          route: "/scheme-creator",
          status: "active" },
        { id: "customers",
          label: "Customers",
          route: resolveSmritiRoute("customers"),
          status: "active" },
        { id: "suppliers",
          label: "Suppliers",
          route: resolveSmritiRoute("suppliers"),
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
          route: "/distributor-accounts",
          status: "active" },
        { id: "sales_uploads",
          label: "Sales Uploads",
          route: "/psv-sales-upload",
          status: "active" },
        { id: "stock_uploads",
          label: "Stock Uploads",
          route: "/psv-stock-upload",
          status: "active" },
        { id: "reconciliation",
          label: "Reconciliation",
          status: "coming_soon",
          progress: 0,
          eta: "PSV Phase 1.3" },
        { id: "psv_dashboard",
          label: "Dashboard",
          route: "/psv-dashboard",
          status: "active" },
        { id: "stock_aging",
          label: "Stock Aging",
          route: "/psv-aging",
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
          route: "/pos",
          status: "active" },
        { id: "sales_orders",
          label: "Sales Orders",
          route: resolveSmritiRoute("sales_order"),
          status: "active" },
        { id: "tax_invoice",
          label: "Tax Invoice",
          route: resolveSmritiRoute("sales_invoice"),
          status: "active" },
        { id: "sales_return",
          label: "Sales Return",
          route: resolveSmritiRoute("sales_return"),
          status: "active" },
        { id: "delivery_challan",
          label: "Delivery Challan",
          route: resolveSmritiRoute("delivery_note"),
          status: "active" },
        { id: "credit_notes",
          label: "Credit Notes",
          route: resolveSmritiRoute("credit_note"),
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
          route: resolveSmritiRoute("purchase_order"),
          status: "active" },
        { id: "grn_receipts",
          label: "GRN / Receipts",
          route: resolveSmritiRoute("purchase_receipt"),
          status: "active" },
        { id: "purchase_invoice",
          label: "Purchase Invoice",
          route: resolveSmritiRoute("purchase_invoice"),
          status: "active" },
        { id: "supplier_returns",
          label: "Supplier Returns",
          status: "coming_soon",
          progress: 0,
          eta: "Sprint P2" }
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
          status: "active" },
        { id: "opening_stock",
          label: "Opening Stock",
          route: "/opening-stock",
          status: "active" },
        { id: "stock_operations",
          label: "Stock Operations",
          route: "/stock-operations",
          status: "active" },
        { id: "stock_transfer",
          label: "Stock Transfer",
          status: "coming_soon",
          progress: 5,
          eta: "Sprint P1" },
        { id: "stock_adjustments",
          label: "Stock Adjustments",
          route: resolveSmritiRoute("stock_entry"),
          status: "active" },
        { id: "stock_audit",
          label: "Stock Audit",
          status: "coming_soon",
          progress: 0,
          eta: "Sprint P2" },
        { id: "barcode_center",
          label: "Barcode Center",
          route: "/barcode",
          status: "active" },
        { id: "print_templates",
          label: "Print Templates",
          route: "/print-templates",
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
          status: "active" },
        { id: "payments",
          label: "Payments",
          route: resolveSmritiRoute("payment_entry_payment"),
          status: "active" },
        { id: "advances",
          label: "Advances",
          route: resolveSmritiRoute("advance"),
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
          route: "/reports?category=sales",
          status: "active" },
        { id: "inventory_reports",
          label: "Inventory Reports",
          route: "/reports?category=inventory",
          status: "active" },
        { id: "finance_reports",
          label: "Finance Reports",
          route: "/reports?category=finance",
          status: "active" },
        { id: "gst_reports",
          label: "GST Reports",
          route: "/reports?category=gst",
          status: "active" },
        { id: "psv_reports",
          label: "PSV Reports",
          route: "/reports?category=psv",
          status: "active" },
        { id: "billing_metrics",
          label: "Billing Metrics",
          route: "/billing-metrics",
          status: "active" },
        { id: "audit_reports",
          label: "Audit Reports",
          status: "coming_soon",
          progress: 15,
          eta: "Sprint P2" }
      ]
    },
    {
      id: "administration",
      label: "Administration",
      status: "active",
      items: [
        { id: "day_open",
          label: "Day Open",
          route: "/day-open",
          status: "active" },
        { id: "day_close",
          label: "Day Close",
          route: "/day-close",
          status: "active" },
        { id: "shift_register",
          label: "Shift / Register",
          route: "/shift-register",
          status: "active" },
        { id: "user_management",
          label: "User Management",
          route: resolveSmritiRoute("users"),
          status: "active" },
        { id: "roles_permissions",
          label: "Roles & Permissions",
          route: resolveSmritiRoute("roles"),
          status: "active" },
        { id: "config_portal",
          label: "Config Portal",
          route: "/config-portal",
          status: "active" },
        { id: "security_workflows",
          label: "Security & Workflows",
          route: "/security-workflows",
          status: "active" },
        { id: "audit_logs",
          label: "Audit Logs",
          route: resolveSmritiRoute("audit_logs"),
          status: "active" },
        { id: "backup_restore",
          label: "Backup & Restore",
          route: "/backup",
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
