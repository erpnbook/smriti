---
Document ID: "DEV-PS-001"
Title: "SMRITI Purchase Studio — Developer Guide v1.0"
Owner: "Development Team"
Audience: "Developer"
Module: "Purchase Studio"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "ARCH-PS-001"
Related Modules: "SAS, UIE"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Studio — Developer Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

---

## Module Structure

```
smriti_retail_os/
└── purchase_studio/
    ├── __init__.py
    ├── api/
    │   └── purchase_api.py          ← 18 whitelisted API endpoints
    ├── service/
    │   └── purchase_service.py      ← Business logic layer
    ├── doctype/
    │   ├── smriti_purchase_settings/
    │   │   ├── smriti_purchase_settings.json
    │   │   └── smriti_purchase_settings.py
    │   └── smriti_purchase_audit_log/
    │       ├── smriti_purchase_audit_log.json
    │       └── smriti_purchase_audit_log.py
    └── www/
        └── smriti-purchase.html     ← SMRITI Purchase Center UI
```

---

## Architecture Pattern

All frontend interactions must follow the service-first flow:

```
smriti-purchase.html (UI)
        ↓  frappe.call()
purchase_api.py (whitelisted endpoint)
        ↓
purchase_service.py (business logic)
        ↓
ERPNext DocTypes (Purchase Order, Purchase Receipt, Purchase Invoice)
        ↓
ERPNext Stock + Accounting Engines
```

**Never call Frappe DocType methods directly from HTML.** All operations must pass through `purchase_service.py`.

---

## DocTypes

### SMRITI Purchase Settings

Single DocType (one record per site). Configured via `/smriti-purchase` settings panel.

| Field | Type | Description |
|---|---|---|
| `approval_required` | Check | Enable/disable approval workflow |
| `approval_threshold` | Currency | PO value above which approval is required |
| `invoice_policy` | Select | `grn_only` / `standalone` / `flexible` |
| `lc_rule` | Select | `standard` / `actual` |
| `default_warehouse` | Link | Default warehouse for new POs |
| `tolerance_pct` | Float | Qty variance tolerance (0-100%) |

**Service method:**
```python
from smriti_retail_os.purchase_studio.service.purchase_service import get_settings
settings = get_settings()
```

### SMRITI Purchase Audit Log

Append-only record per significant purchase action.

| Field | Type | Description |
|---|---|---|
| `action` | Data | `created`, `approved`, `rejected`, `cancelled` |
| `document_type` | Data | `Purchase Order`, `Purchase Receipt`, etc. |
| `document_name` | Data | Document reference |
| `user` | Link | Frappe User |
| `timestamp` | Datetime | Action timestamp |
| `before_value` | JSON | State before action |
| `after_value` | JSON | State after action |
| `reason` | Text | Rejection or cancellation reason |

---

## Adding a New Purchase API Endpoint

1. Add the function to `purchase_api.py`:
```python
@frappe.whitelist()
def my_new_endpoint(param1, param2=None):
    from smriti_retail_os.purchase_studio.service.purchase_service import my_service_method
    return my_service_method(param1, param2)
```

2. Add the business logic to `purchase_service.py`:
```python
def my_service_method(param1, param2=None):
    # validate
    # query or mutate via frappe.get_doc / frappe.new_doc
    # log to SMRITI Purchase Audit Log
    return result
```

3. Never use `frappe.client.insert` or `frappe.new_doc` from HTML templates.

---

## Approval Workflow

The approval threshold is enforced in `purchase_service.py`:

```python
settings = get_settings()
if po_doc.grand_total > settings.approval_threshold:
    po_doc.custom_smriti_status = "Pending Approval"
    po_doc.save()
    # Do NOT submit — submit only after approval
else:
    po_doc.submit()
```

The `resolve_po_approval` endpoint handles the approval action and calls `po_doc.submit()` after approval.

---

## Invoice Policy Enforcement

```python
def validate_invoice_policy(items, purchase_receipt):
    settings = get_settings()
    if settings.invoice_policy == "grn_only" and not purchase_receipt:
        frappe.throw("Invoice Policy requires a GRN link. "
                     "Please select a Purchase Receipt.")
    if settings.invoice_policy == "standalone" and purchase_receipt:
        frappe.throw("Invoice Policy does not permit GRN-linked invoices.")
```

---

## Extending Purchase Studio

### Adding a New Settings Field

1. Add the field to `smriti_purchase_settings.json`
2. Run `bench --site smriti_retail migrate`
3. Add validation in `purchase_service.py → save_settings()`
4. Expose in `purchase_api.py → save_purchase_settings()`
5. Update [API-003](../06-api/purchase_api.md) documentation

### Adding a New Purchase Report (SAS)

See [SAS Developer Guide](./sas_developer.md) for the full pattern.
Short form:
1. Add SQL query to `REPORT_QUERIES` in `reports_api.py`
2. Add metadata to `SAS_REPORT_DEFAULTS` in `sas_service.py`
3. Add fixture entry to `smriti_report_template.json`
4. Write a test in `test_purchase_studio.py`
5. Run `bench --site smriti_retail execute smriti_retail_os.patches.seed_purchase_report_templates.execute`

## Matrix & Supplier Enhancements (v2.1.1)

### Matrix Session Filtering
When retrieving the style matrix session data, the system filters rows and columns dynamically in `matrix_service.py`:
1. **Color Filtering**: Returns only the color variants that have active, matching variant records created for that style, rather than displaying all global system colors.
2. **Size Group Filtering**: Resolves the style's variant sizes against active `SMRITI Size Group` definitions, dynamically picking the group with maximum overlap (e.g. Footwear vs Garments) and filtering out irrelevant sizes (like `S`, `M`, `L` when displaying shoes).

### Supplier Synchronization Bridge
Standard ERPNext `Supplier` updates trigger an `on_update` hook in `hooks_logic.py` (`sync_supplier_address_and_credit_days`) that automatically:
- Provisions a synchronized `SMRITI Supplier` counterpart matching the vendor's standard properties.
- Synchronizes contact, address mapping, and validation details to keep both registers aligned.

---

## Testing

Test class: `smriti_retail_os.tests.test_purchase_studio.TestPurchaseReportsSAS`

Run tests:
```bash
bench --site smriti_retail run-tests \
  --module smriti_retail_os.tests.test_purchase_studio
```

Expected: 4/4 tests pass (as of v2.0.0)

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| DocType not found after adding | Run `bench migrate` |
| Approval threshold not enforcing | Check `get_settings()` reads from DB, not cache |
| GRN-linked invoice failing | Verify `invoice_policy` field on Settings |
| Return qty not negative | `create_purchase_return` expects negative qty in payload |

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
