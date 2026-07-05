---
Document ID: "API-004"
Title: "SMRITI Analytics Studio (SAS) — API Reference Manual v1.0"
Owner: "Integration Team"
Audience: "Developer"
Module: "SAS"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "DEV-SAS-001"
Related Modules: "Purchase Studio, Inventory, Sales"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Analytics Studio (SAS) — API Reference Manual v1.0

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

> Base module: `smriti_retail_os.reports_api` and `smriti_retail_os.analytics_studio.sas_service`

---

## Report Catalog

### `get_srs_report_list_for_sas`

Returns the full report catalog grouped by category.

**Method:** `smriti_retail_os.analytics_studio.sas_service.get_srs_report_list_for_sas`
**Parameters:** None

**Response:**
```json
{
  "Purchase": [
    {
      "report_key": "purchase_order_summary",
      "report_name": "SMRITI Purchase Order Summary",
      "dataset_key": null,
      "has_chart": true,
      "has_kpi": true,
      "explain_enabled": true
    }
  ],
  "Sales": [...],
  "Inventory Analytics": [...],
  "Cash": [...],
  "Accounting": [...],
  "Audit": [...]
}
```

---

## Run Report

### `run_report`

Executes a report by key and returns data, columns, chart config, and KPIs.

**Method:** `smriti_retail_os.reports_api.run_report`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `report_key` | string | Yes | Report identifier (see catalog above) |
| `from_date` | date | No | Filter: start date (YYYY-MM-DD) |
| `to_date` | date | No | Filter: end date |
| `supplier` | string | No | Filter: Supplier name |
| `warehouse` | string | No | Filter: Warehouse |
| `company` | string | No | Filter: Company |
| `status` | string | No | Filter: Document status |
| `item_group` | string | No | Filter: Item Group |
| `brand` | string | No | Filter: Brand |
| `project` | string | No | Filter: Project (Purchase Orders) |
| `limit` | int | No | Max rows (default: 500) |
| `page` | int | No | Page number (default: 1) |

**Response:**
```json
{
  "report_key": "purchase_order_summary",
  "report_name": "SMRITI Purchase Order Summary",
  "columns": [
    {"label": "PO Number", "fieldname": "po_name", "fieldtype": "Data"},
    {"label": "Supplier", "fieldname": "supplier_name", "fieldtype": "Data"},
    {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency"}
  ],
  "data": [...],
  "chart": {
    "type": "bar",
    "x_field": "supplier_name",
    "y_fields": ["grand_total"]
  },
  "kpis": [
    {"label": "Total Value", "value": 1250000.00, "fieldtype": "Currency"}
  ],
  "total_rows": 42,
  "page": 1
}
```

---

## Available Report Keys

### Purchase Category (v2.0.0)

| report_key | Description | Key Filters |
|---|---|---|
| `purchase_order_summary` | PO lifecycle — grouped by PO with balance | from_date, to_date, supplier, status, project, company |
| `grn_register` | Purchase Receipts (returns excluded) | from_date, to_date, supplier, warehouse, status, company |
| `purchase_invoice_register` | Purchase Invoices with overdue tracking | from_date, to_date, supplier, status, company |
| `supplier_purchase_summary` | Supplier aggregation with drill-down | from_date, to_date, company |
| `item_wise_purchase` | Item-level analysis, weighted avg rate | from_date, to_date, supplier, item_group, brand, warehouse, company |
| `purchase_return_register` | Debit notes with GST split | from_date, to_date |

### Sales Category

| report_key | Description |
|---|---|
| `item_wise_sales` | Item-wise POS sales analytics |
| `daily_sales_summary` | Daily aggregated sales |

### Inventory Analytics Category

| report_key | Description |
|---|---|
| `current_stock_position` | Live stock with status (In Stock / Low / Out) |
| `style_wise_stock` | Stock grouped by style |
| `size_wise_stock` | Stock by size, color, warehouse |
| `inventory_productivity` | SKU productivity scoring |
| `psv_reorder_report` | PSV channel reorder recommendations |

### Cash Category

| report_key | Description |
|---|---|
| `cash_reconciliation` | POS closing vs expected amounts |
| `cash_z_report` | Z-report by POS session |
| `payment_mode_summary` | Collections by payment mode |

### Accounting Category

| report_key | Description |
|---|---|
| `customer_outstanding` | Receivables ageing |
| `supplier_outstanding` | Payables ageing |
| `payment_register` | Payment entries (Pay type) |
| `receipt_register` | Payment entries (Receive type) |
| `cash_book` | Cash ledger |
| `day_book` | Daily transaction log |

### Audit Category

| report_key | Description |
|---|---|
| `security_audit_log` | User activity log |
| `address_change_log` | Address modification audit trail |

---

## Report Column Fieldtypes

| fieldtype | Display |
|---|---|
| `Data` | Plain text |
| `Currency` | Formatted with ₹ symbol |
| `Int` | Integer |
| `Float` | 2 decimal places |
| `Date` | DD-MM-YYYY |
| `Link` | Clickable if rendered in SAS UI |

---

## Conditional Formatting Rules

Some reports include conditional format metadata in `chart.conditional_rules`:

```json
{
  "conditional_rules": [
    {
      "field": "overdue_days",
      "condition": "gt",
      "value": 0,
      "style": "color: red; font-weight: bold;"
    }
  ]
}
```

Reports with conditional rules: `purchase_invoice_register`, `customer_outstanding`, `supplier_outstanding`.

---

## Explain (ⓘ Transparency)

When `explain_enabled: true` in the catalog, the SAS UI provides a transparency modal.
Developers can call the explain metadata endpoint:

**Method:** `smriti_retail_os.analytics_studio.sas_service.get_report_explain`

| Parameter | Type | Required |
|---|---|---|
| `report_key` | string | Yes |

**Response:** Business definition, formula, data sources, interpretation guide.

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
