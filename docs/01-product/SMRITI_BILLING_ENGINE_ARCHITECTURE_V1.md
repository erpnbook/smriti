---
Document ID: "SMRITI-ARCH-003"
Title: "SMRITI Billing Engine Architecture Specification"
Owner: "Billing Team"
Audience: "Support Engineer"
Module: "Billing"
Version: "1.0.0"
Status: "Frozen"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Billing Engine Architecture Specification (v1.0 - Frozen)

## 1. Governing Constitutional Rule
> **All monetary values shall originate from the Billing Summary Engine. Services may propose adjustments, but only the Billing Summary Engine may finalize monetary values for display, persistence, printing, taxation, tender allocation, and accounting.**
> 
> **The Billing Session Manager is the single source of truth during an active transaction. UI components, services, and plugins must never calculate totals independently or bypass the Billing Session state.**

---

## 2. Architectural Blueprint

The billing terminal follows a strictly decoupled, unidirectional state and processing model:

```text
                SMRITI Billing UI (Event Bus Driven)
                        │
                        ▼
             Billing Session Manager (Local State)
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
 Discount Service  Salesperson Service  Approval Service
  (Adjustments)         (Core)          (Generic Engine)
        │               │                │
        └───────────────┼────────────────┘
                        ▼
              Billing Summary Engine (Read-Only Summary)
                        ▼
                Invoice Mapper (Pure Mapping)
                        ▼
             ERPNext Transaction Layer (Accounting)
```

---

## 3. Transaction State Machine & Lifecycle

Every active billing transaction progresses through the following sequential states:

```text
  [NEW] ➔ [ACTIVE] ➔ [PAYMENT_PENDING] ➔ [VALIDATED] ➔ [SUBMITTED] ➔ [PRINTED] ➔ [SYNCED] ➔ [CLOSED]
```

### Transition Hooks & Extension Points

Developers can hook custom logic at the following extension points:

- **`before_item_added(item, session)`**: Runs before inserting an item into the cart.
- **`after_item_added(item, session)`**: Runs after inserting.
- **`before_discount_applied(discount, session)`**: Enforces approval limits or validates manager PINs.
- **`after_discount_applied(discount, session)`**: Triggers analytics or auditing logs.
- **`before_tax_calculation(session)`**: Modifies taxes dynamically.
- **`after_tax_calculation(summary, session)`**: Validates final values.
- **`before_payment(payments, session)`**: Checks payment limits.
- **`after_payment(payments, session)`**: Triggers drawer opening.
- **`before_invoice_submit(doc, session)`**: Runs final data checks.
- **`after_invoice_submit(doc, session)`**: Enqueues background sync and telemetry alerts.

---

## 4. Versioned Event Bus Contracts

UI components and service extensions communicate via a versioned Event Bus contract:

| Event Name | Version | Payload | Description |
|---|---|---|---|
| `billing:created` | v1 | `{ session_id, customer }` | Triggers UI reset |
| `billing:item-added` | v1 | `{ item_code, qty, rate }` | Adds row to cart |
| `billing:item-updated` | v1 | `{ item_code, qty, rate }` | Recalculates totals |
| `billing:item-removed` | v1 | `{ item_code }` | Removes row |
| `discount:applied` | v1 | `{ level: "item"\|"bill", val, type: "%"\|"₹" }` | Triggers summary recalculation |
| `discount:removed` | v1 | `{ level: "item"\|"bill" }` | Clears discount state |
| `salesperson:changed` | v1 | `{ level: "item"\|"bill", name }` | Attributes commission |
| `tax:recalculated` | v1 | `{ tax_details }` | Renders GST breakdown |
| `summary:updated` | v1 | `{ subtotal, discount, grand_total }` | Renders totals card |
| `payment:updated` | v1 | `{ payments, balance, change }` | Updates tender inputs |
| `payment:completed` | v1 | `{ invoice_name }` | Displays checkout success overlay |
| `invoice:submitted` | v1 | `{ invoice_name, print_url }` | Commits transaction |

---

## 5. Plugin Execution Pipeline

The **Billing Session Manager** passes the active cart state through a prioritized plugin pipeline before sending it to the **Billing Summary Engine**:

| Execution Order | Plugin Stage | Description |
|---|---|---|
| Priority 100 | **Item Override Plugins** | Handles manual price changes and cashier overrides |
| Priority 200 | **Discount Plugins** | Handles manual item-level and bill-level adjustments |
| Priority 300 | **Coupon & Promotion Plugins** | Evaluates CGE campaigns and coupon matchers |
| Priority 400 | **Membership & Loyalty Plugins** | Calculates tier-based prices and loyalty points |
| Priority 500 | **Wallet & Voucher Plugins** | Applies gift vouchers and cashbacks |

If any plugin crashes, SMRITI logs the error, disables the offending plugin, and continues billing execution without corrupting active session state.

---

## 6. Non-Functional Requirements & Performance Budget

To certify General Availability (GA), the billing engine must respect the following limits:

| Operation | Performance Budget | Target Platform |
|---|---|---|
| Scan / Add Barcode | **<50 ms** | Local Cache Lookup |
| Apply Discount | **<100 ms** | Local summary recalculation |
| Rebuild Totals Summary | **<50 ms** | Local calculation cycle |
| Update Tender Amount | **<50 ms** | Event bus render |
| Invoice Submit | **<500 ms** | Offline fallback draft save |

### Offline Policy
When internet connection is lost:
- Real-time manager validation is disabled.
- Cashiers are authorized to apply discounts up to the configured `max_offline_cashier_discount` (default: 5.0%) without manager validation.
- All submitted invoices are stored locally inside `SmritiOfflineStore` (IndexedDB) and enqueued for background synchronization.
