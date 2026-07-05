---
Document ID: "API-003"
Title: "SMRITI Purchase Studio — API Reference Manual v1.0"
Owner: "Integration Team"
Audience: "Developer"
Module: "Purchase Studio"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "DEV-PS-001"
Related Modules: "SAS, UIE"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Studio — API Reference Manual v1.0

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

> All endpoints are whitelisted Frappe methods. Call via `frappe.call()` or HTTP POST to `/api/method/<endpoint>`.
> Base module: `smriti_retail_os.purchase_studio.api.purchase_api`

---

## Authentication

All endpoints require an active Frappe session or API key/secret pair.
Unauthenticated requests return HTTP 403.

---

## Dashboard

### `get_purchase_dashboard`

Returns KPI summary for the Purchase Center landing page.

**Method:** `smriti_retail_os.purchase_studio.api.purchase_api.get_purchase_dashboard`
**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `company` | string | No | Filter by ERPNext Company name |
| `from_date` | date | No | Start of dashboard period (YYYY-MM-DD) |
| `to_date` | date | No | End of dashboard period (YYYY-MM-DD) |

**Response:**
```json
{
  "open_pos": 12,
  "pending_grns": 3,
  "overdue_invoices": 2,
  "total_payable": 142500.00,
  "recent_pos": [...],
  "recent_grns": [...]
}
```

---

## Purchase Orders

### `get_purchase_orders`

Returns paginated list of Purchase Orders.

**Method:** `...purchase_api.get_purchase_orders`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | No | Filter by Supplier name |
| `status` | string | No | Draft / To Receive and Bill / Completed / Cancelled |
| `from_date` | date | No | PO date from |
| `to_date` | date | No | PO date to |
| `page` | int | No | Page number (default: 1) |
| `page_size` | int | No | Records per page (default: 20, max: 100) |

**Response:**
```json
{
  "data": [
    {
      "name": "PO-2026-00001",
      "supplier": "ABC Traders",
      "posting_date": "2026-07-01",
      "grand_total": 45000.00,
      "status": "To Receive and Bill"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### `get_purchase_order_detail`

Returns full detail of a single Purchase Order.

**Method:** `...purchase_api.get_purchase_order_detail`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `po_name` | string | Yes | Purchase Order document name |

**Response:** Full PO document dict including items, taxes, terms.

---

### `create_purchase_order`

Creates a new Purchase Order.

**Method:** `...purchase_api.create_purchase_order`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | Yes | ERPNext Supplier name |
| `items` | array | Yes | Array of `{item_code, qty, rate, warehouse}` |
| `schedule_date` | date | No | Expected delivery date |
| `company` | string | No | Company (resolved from settings if omitted) |
| `taxes_and_charges` | string | No | Tax template name |

**Validation rules:**
- `items` must not be empty
- `supplier` must be an existing ERPNext Supplier
- If `grand_total` exceeds approval threshold in SMRITI Purchase Settings, status is set to `Pending Approval`

**Response:**
```json
{ "name": "PO-2026-00042", "status": "Draft", "grand_total": 18500.00 }
```

---

### `resolve_po_approval`

Approve or reject a Purchase Order awaiting approval.

**Method:** `...purchase_api.resolve_po_approval`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `po_name` | string | Yes | PO document name |
| `action` | string | Yes | `approve` or `reject` |
| `reason` | string | Required if `reject` | Rejection reason |

---

## GRN / Purchase Receipts

### `get_grns`

Returns paginated GRN list.

**Method:** `...purchase_api.get_grns`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | No | |
| `warehouse` | string | No | |
| `from_date` | date | No | |
| `to_date` | date | No | |
| `is_return` | bool | No | Default: false (excludes returns) |
| `page` | int | No | |

---

### `get_grn_detail`

**Method:** `...purchase_api.get_grn_detail`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `grn_name` | string | Yes | Purchase Receipt document name |

---

### `create_grn`

Creates a Purchase Receipt (GRN).

**Method:** `...purchase_api.create_grn`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | Yes | ERPNext Supplier name |
| `items` | array | Yes | `{item_code, qty, rate, warehouse, po_detail}` |
| `purchase_order` | string | No | Link to source PO (validates against PO items) |
| `posting_date` | date | No | Defaults to today |
| `company` | string | No | |

---

## Purchase Invoices

### `get_invoices`

**Method:** `...purchase_api.get_invoices`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | No | |
| `status` | string | No | Unpaid / Paid / Overdue / Cancelled |
| `from_date` | date | No | |
| `to_date` | date | No | |
| `page` | int | No | |

---

### `create_invoice`

Creates a Purchase Invoice.

**Method:** `...purchase_api.create_invoice`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | Yes | |
| `items` | array | Conditional | Required if `purchase_receipt` not provided |
| `purchase_receipt` | string | Conditional | GRN name — required if policy = `grn_only` |
| `bill_no` | string | No | Supplier's invoice number |
| `bill_date` | date | No | Supplier's invoice date |
| `due_date` | date | No | Payment due date |

**Invoice policy enforcement:**
- `grn_only`: `purchase_receipt` is mandatory; standalone items array rejected.
- `standalone`: `purchase_receipt` is rejected; items array is mandatory.
- `flexible`: Either is accepted.

---

## Purchase Returns

### `get_returns`

**Method:** `...purchase_api.get_returns`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | No | |
| `from_date` | date | No | |
| `to_date` | date | No | |
| `page` | int | No | |

---

### `create_purchase_return`

Creates a Purchase Return (Debit Note).

**Method:** `...purchase_api.create_purchase_return`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `purchase_receipt` | string | Yes | Original GRN name |
| `items` | array | Yes | `{item_code, qty}` — qty must be negative |
| `reason` | string | Yes | Return reason (non-empty) |

---

## Supplier Ledger

### `get_supplier_ledger`

Returns supplier payment and invoice history.

**Method:** `...purchase_api.get_supplier_ledger`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `supplier` | string | Yes | |
| `from_date` | date | Yes | |
| `to_date` | date | Yes | |

---

## Search

### `search_suppliers`

**Method:** `...purchase_api.search_suppliers`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | Min 2 characters |
| `limit` | int | No | Max results (default: 20) |

---

### `search_items`

**Method:** `...purchase_api.search_items`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | Yes | Min 2 characters |
| `limit` | int | No | Max results (default: 20) |

---

## Settings

### `get_purchase_settings`

Returns current SMRITI Purchase Settings.

**Method:** `...purchase_api.get_purchase_settings`

**Response:**
```json
{
  "approval_required": true,
  "approval_threshold": 50000.00,
  "invoice_policy": "grn_only",
  "lc_rule": "standard",
  "default_warehouse": "Stores - ABC"
}
```

---

### `save_purchase_settings`

Updates SMRITI Purchase Settings.

**Method:** `...purchase_api.save_purchase_settings`

| Parameter | Type | Validation |
|---|---|---|
| `approval_threshold` | float | Must be ≥ 0 |
| `invoice_policy` | string | `grn_only` / `standalone` / `flexible` |
| `lc_rule` | string | `standard` / `actual` |
| `default_warehouse` | string | Must exist in ERPNext |
| `tolerance_pct` | float | 0–100 |

---

## Error Responses

All errors follow Frappe standard format:

```json
{
  "exc_type": "ValidationError",
  "exception": "smriti_retail_os.purchase_studio...",
  "_server_messages": "[{\"message\": \"...\"}]"
}
```

Common error codes:

| Exception | Cause |
|---|---|
| `ValidationError` | Missing required field, policy conflict |
| `DoesNotExistError` | Document not found (PO, GRN, Supplier) |
| `PermissionError` | User lacks Purchase Manager role |

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
*"Always decision-ready."*
