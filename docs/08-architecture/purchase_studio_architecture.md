---
Document ID: "ARCH-PS-001"
Title: "SMRITI Purchase Studio — Architecture Document v1.0"
Owner: "Architecture Team"
Audience: "Architect"
Module: "Purchase Studio"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "SAS, UIE, Inventory"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Studio — Architecture Document

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

---

## Architectural Classification

**Type:** SMRITI-First UI Module
**ERPNext Role:** Transaction Engine (PO, GRN, Invoice remain in ERPNext)
**SMRITI Role:** UI/UX, Workflow, Policy Enforcement, Approval Gate

---

## Service Layer Diagram

```
┌─────────────────────────────────────────┐
│   smriti-purchase.html (SMRITI UI)      │
│   Route: /smriti-purchase               │
└───────────────┬─────────────────────────┘
                │  frappe.call()
                ▼
┌─────────────────────────────────────────┐
│   purchase_api.py                        │
│   18 @frappe.whitelist endpoints         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   purchase_service.py                    │
│   - Policy enforcement (invoice, LC)     │
│   - Approval threshold gate              │
│   - Audit log writer                     │
│   - ERPNext document creator             │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   ERPNext Core Engines                   │
│   - Purchase Order                       │
│   - Purchase Receipt (GRN)               │
│   - Purchase Invoice                     │
│   - Debit Note                           │
│   - Stock Ledger Engine                  │
│   - Accounting Engine                    │
│   - GST Engine                           │
└─────────────────────────────────────────┘
```

---

## Module Directory Structure

```
smriti_retail_os/purchase_studio/
├── __init__.py
├── api/
│   └── purchase_api.py          ← Whitelisted API (18 endpoints)
├── service/
│   └── purchase_service.py      ← Business logic, policy, approval
├── doctype/
│   ├── smriti_purchase_settings/
│   │   ├── smriti_purchase_settings.json    ← DocType schema
│   │   └── smriti_purchase_settings.py      ← DocType class (Single)
│   └── smriti_purchase_audit_log/
│       ├── smriti_purchase_audit_log.json
│       └── smriti_purchase_audit_log.py
└── www/
    └── smriti-purchase.html     ← SMRITI UI (Rule 7 compliant)
```

---

## DocType Inventory

### SMRITI Purchase Settings (Single DocType)

One global record per SMRITI installation. Stores:
- `approval_required` (Check)
- `approval_threshold` (Currency)
- `invoice_policy` (Select: grn_only / standalone / flexible)
- `lc_rule` (Select: standard / actual)
- `default_warehouse` (Link: Warehouse)
- `tolerance_pct` (Float)

### SMRITI Purchase Audit Log

Append-only audit trail. One record per significant purchase action.
Fields: `action`, `document_type`, `document_name`, `user`, `timestamp`, `before_value`, `after_value`, `reason`.

---

## Approval Workflow Architecture

```
create_purchase_order()
        │
        ▼
Is grand_total > approval_threshold?
        │
   YES  │                NO
        ▼                 ▼
Set status =         po_doc.submit()
"Pending Approval"   → ERPNext submit
        │
        ▼
resolve_po_approval(action="approve")
        │
        ▼
po_doc.submit()
Write to SMRITI Purchase Audit Log
```

**Key constraint:** The approval gate in `purchase_service.py` is the only path to submission. The ERPNext PO `submit()` method is not directly callable from the SMRITI frontend.

---

## Invoice Policy Enforcement

Policy is read from `SMRITI Purchase Settings.invoice_policy` at invoice creation time:

| Policy | Behaviour |
|---|---|
| `grn_only` | `purchase_receipt` field mandatory; items array rejected |
| `standalone` | Items array mandatory; `purchase_receipt` rejected |
| `flexible` | Either accepted |

This policy is enforced **server-side** in `purchase_service.validate_invoice_policy()` — it cannot be bypassed by the frontend.

---

## ERPNext Integration Points

Purchase Studio does not modify ERPNext core. It creates documents using `frappe.new_doc()` in the service layer, then calls `.insert()` and `.submit()` via the Frappe Document API.

| SMRITI Action | ERPNext Document Created |
|---|---|
| create_purchase_order | Purchase Order |
| create_grn | Purchase Receipt |
| create_invoice | Purchase Invoice |
| create_purchase_return | Purchase Receipt (is_return=1) |
| resolve_po_approval | Purchase Order (submit existing) |
| get_supplier_ledger | Reads GL Entry (no write) |

---

## Audit Log Architecture

Every mutation in Purchase Studio writes to `SMRITI Purchase Audit Log` before returning to the API caller. Fields captured:

```python
frappe.get_doc({
    "doctype": "SMRITI Purchase Audit Log",
    "action": "approved",
    "document_type": "Purchase Order",
    "document_name": "PO-2026-00042",
    "user": frappe.session.user,
    "timestamp": frappe.utils.now(),
    "before_value": json.dumps({"status": "Pending Approval"}),
    "after_value": json.dumps({"status": "To Receive and Bill"}),
    "reason": ""
}).insert(ignore_permissions=True)
```

The audit log is immutable — no update or delete is permitted on existing entries.

---

## Governance Compliance

| Rule | Compliance |
|---|---|
| SMRITI Rule 7 (SMRITI-First UI) | `/smriti-purchase` route; no Frappe Desk exposed |
| SMRITI Architecture Rule 2 (Service-First) | All mutations via purchase_service.py |
| SMRITI Architecture Rule 3 (ERPNext-First) | Uses ERPNext PO, GRN, PI as transaction records |
| SMRITI Architecture Rule 13 (Auditability) | SMRITI Purchase Audit Log per action |
| GEMINI.md Rule 6 (Service-First Design) | No frappe.client.insert from HTML |

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
*"Always decision-ready."*
