---
Document ID: "DEV-070"
Title: "Vendor Mapping — ItemMaster ↔ Supplier Linkage"
Owner: "Development Team"
Audience: "Developer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Vendor Mapping — ItemMaster ↔ Supplier Linkage

> **Date:** 2026-06-04  
> **Session:** Vendor Mapping in Item Master with Supplier (Architecture Review & Feature Documentation)  
> **Status:** ✅ Implemented & Locked

---

## Overview

This walkthrough documents the **Vendor Code → Supplier linkage** architecture in the SMRITI Item Master import pipeline. When an item is imported with a `VENDOR CODE`, the system:

1. **Validates** the vendor code against the `custom_vendor_code` field on the ERPNext `Supplier` DocType.
2. **Hard-blocks** import if the vendor code doesn't exist in Supplier Master.
3. **Auto-links** the matched supplier into the `Item Supplier` child table (`supplier_items`) on the parent template item.

---

## Architecture

### 1. `custom_vendor_code` Field on Supplier

Created via `setup.py` during app install:

- **DocType:** `Supplier`
- **Field name:** `custom_vendor_code`
- **Type:** Data (unique)
- **Purpose:** Maps external ERP/wholesale codes (e.g., `SUP001`, `BATA`, `ACH-BAN`) to the corresponding ERPNext Supplier record.

Suppliers are managed at `/suppliers` ([suppliers.html](../../apps/smriti_retail_os/smriti_retail_os/www/suppliers.html)).

---

### 2. Validation Flow (`validate_import_rows`)

Called during dry-run validation **before** any item is created.

```python
# item_master_api.py — validate_import_rows()
vendor = _clean_str(row.get("VENDOR CODE", ""))
if vendor and str(vendor).strip() not in ("", "nan", "None", "N/A"):
    vendor_clean = str(vendor).strip()
    supplier_exists = frappe.db.exists(
        "Supplier",
        {"custom_vendor_code": vendor_clean}
    )
    if not supplier_exists:
        errors.append(
            f"Vendor Code '{vendor_clean}' not found in Supplier Master. "
            f"Please create a Supplier with Vendor Code '{vendor_clean}' before importing items."
        )
```

**Result:** Row is marked `status = "error"` — **hard-blocked**, cannot be imported until the supplier is created.

---

### 3. Runtime Validation (`_validate_vendor_code`)

Called inside `import_item_master()` and `create_style_with_variants()` as a **second safety guard** at write time:

```python
def _validate_vendor_code(vendor_code):
    if not vendor_code or str(vendor_code).strip() in ("", "nan", "None", "N/A"):
        return  # vendor code is optional — skip
    vendor_code = str(vendor_code).strip()
    exists = frappe.db.exists("Supplier", {"custom_vendor_code": vendor_code})
    if not exists:
        frappe.throw(
            f"Vendor Code '{vendor_code}' not found in Supplier Master. ...",
            title="Vendor Code Not Found"
        )
```

**Vendor code is optional.** If absent, no error is raised. If present, it must resolve to a known Supplier.

---

### 4. Supplier Linkage (`_get_or_create_template`)

After the template Item is created (or fetched), the matched Supplier is appended to `supplier_items`:

```python
# _get_or_create_template() — always run after insert/fetch
if vendor_code:
    supplier_name = frappe.db.get_value(
        "Supplier",
        {"custom_vendor_code": str(vendor_code).strip()},
        "name"
    )
    if supplier_name:
        if not any(d.supplier == supplier_name for d in item.supplier_items):
            item.append("supplier_items", {
                "supplier": supplier_name,
                "supplier_part_no": vendor_code
            })
            item.save(ignore_permissions=True)
```

**Key behaviours:**
- Idempotent — will not add duplicate supplier rows on re-import.
- `supplier_part_no` is set to the raw vendor code string (e.g., `SUP001`) for purchase order reference.
- The linkage applies to the **template item** (style/article), not individual size variants.

---

### 5. Column Mapping in the Import Grid

The UI (`smriti_item_master.js`) exposes `VENDOR CODE` as the 12th column:

| Column Key     | Label             | Aliases (fuzzy match)         |
|----------------|-------------------|-------------------------------|
| `VENDOR CODE`  | Vendor/Supplier   | `vendor`, `vendor code`, `supplier` |

From Excel, the column header can be `VENDOR CODE`, `Vendor Code`, `vendor`, or `supplier` — all auto-detected via `HEADER_ALIASES`.

---

## Import Workflow (User-Facing)

```
Excel paste/upload
      │
      ▼
[Validate Rows button]
      │
      ├─ VENDOR CODE present?
      │       ├─ YES → lookup custom_vendor_code in Supplier → ❌ ERROR if not found
      │       └─ NO  → skip (optional field)
      │
      ▼
[Import Valid Rows button]
      │
      ├─ _validate_vendor_code() guard
      ├─ _get_or_create_template() → insert/fetch template item
      ├─ Supplier linkage → append to supplier_items
      └─ Continue with variant + barcode creation
```

---

## Data Flow Summary

```
Item Master Import Grid
    VENDOR CODE = "SUP001"
         │
         ▼
frappe.db.exists("Supplier", {"custom_vendor_code": "SUP001"})
         │
         ├─ NOT FOUND → Hard error (red row, blocked from import)
         │
         └─ FOUND (e.g., Supplier = "Bata India Ltd")
                  │
                  ▼
         item.supplier_items.append({
             "supplier": "Bata India Ltd",
             "supplier_part_no": "SUP001"
         })
```

---

## Files Modified

| File | Change |
|---|---|
| [item_master_api.py](../../apps/smriti_retail_os/smriti_retail_os/item_master_api.py) | `_validate_vendor_code()`, `validate_import_rows()`, `_get_or_create_template()` |
| [setup.py](../../apps/smriti_retail_os/smriti_retail_os/setup.py) | `custom_vendor_code` field on Supplier DocType |
| [smriti_item_master.js](../../apps/smriti_retail_os/smriti_retail_os/public/js/item.js) | `VENDOR CODE` column + `EXTRA_ALIASES` for fuzzy matching |

---

## Related Features

- [Supplier Registry](./walkthrough_supplier_registry.md) — Create/manage suppliers with GST address sync
- [Supplier Lookup Fix Report](../../SUPPLIER_LOOKUP_FIX_REPORT.md) — Filter fix for Individual vs Company supplier types
- [completedlist.md #10](../../completedlist.md) — Locked feature entry for this work


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL