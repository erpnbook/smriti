---
Document ID: "DEV-041"
Title: "SMRITI PSV — Agent Prompt: Phase 1"
Owner: "Development Team"
Audience: "Developer"
Module: "PSV"
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

# SMRITI PSV — Agent Prompt: Phase 1
# DocTypes + Custom Fields + Permissions
# Spec Version: v1.0.2 Final Freeze

---

## PRIME DIRECTIVE

You are implementing the **SMRITI Party Stock Visibility (PSV)** module inside the `smriti_retail` Frappe app.

### Non-Negotiable Rules
- ZERO modifications to ERPNext/Frappe core files
- ZERO modifications to Stock Ledger Entry, Bin, GL Entry
- ALL files under `smriti_retail/` app only
- hooks.py — ADD only, never replace existing entries
- Custom fields via `setup.py` using `create_custom_fields()` — never JSON
- Item code ALWAYS = Item Variant (e.g. `KORA-1383-BLACK-38`), never template

### App Path
```
/home/frappe/frappe-bench/apps/smriti_retail/smriti_retail/
```

---

## FOLDER STRUCTURE TO CREATE

```
smriti_retail/
└── party_stock_visibility/
    ├── __init__.py
    ├── doctype/
    │   ├── smriti_party_stock_account/
    │   ├── smriti_psv_settings/
    │   ├── smriti_party_stock_ledger_entry/
    │   ├── smriti_psv_activity_log/
    │   ├── smriti_psv_exception_record/
    │   ├── smriti_party_sales_upload/
    │   ├── smriti_party_sales_item/
    │   ├── smriti_party_physical_snapshot/
    │   └── smriti_party_physical_item/
    ├── service/
    │   └── __init__.py
    ├── engine/
    │   └── __init__.py
    └── utils/
        └── __init__.py
```

---

## TASK 1.1 — modules.txt

In `smriti_retail/modules.txt`, ADD:
```
Party Stock Visibility
```

---

## TASK 1.2 — DocType: SMRITI Party Stock Account

`doctype/smriti_party_stock_account/smriti_party_stock_account.json`

```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Stock Account",
  "module": "Party Stock Visibility",
  "autoname": "format:{customer}-{location_name}",
  "title_field": "location_name",
  "search_fields": "customer,location_name,zone",
  "fields": [
    {"fieldname": "company",        "fieldtype": "Link",   "options": "Company",  "label": "Company",        "reqd": 1, "in_list_view": 0},
    {"fieldname": "customer",       "fieldtype": "Link",   "options": "Customer", "label": "Customer",       "reqd": 1, "in_list_view": 1},
    {"fieldname": "location_name",  "fieldtype": "Data",                          "label": "Location Name",  "reqd": 1, "in_list_view": 1},
    {"fieldname": "zone",           "fieldtype": "Select", "options": "North\nSouth\nEast\nWest\nCentral", "label": "Zone", "in_list_view": 1},
    {"fieldname": "region",         "fieldtype": "Data",                          "label": "Region"},
    {"fieldname": "area_manager",   "fieldtype": "Link",   "options": "User",     "label": "Area Manager"},
    {"fieldname": "address",        "fieldtype": "Link",   "options": "Address",  "label": "Address"},
    {"fieldname": "contact_person", "fieldtype": "Data",                          "label": "Contact Person"},
    {"fieldname": "mobile",         "fieldtype": "Data",                          "label": "Mobile"},
    {"fieldname": "email",          "fieldtype": "Data",                          "label": "Email"},
    {"fieldname": "status",         "fieldtype": "Select", "options": "Active\nInactive\nSuspended", "label": "Status", "default": "Active", "in_list_view": 1},
    {"fieldname": "active",         "fieldtype": "Check",                         "label": "Active",         "default": 1}
  ],
  "permissions": [
    {"role": "System Manager",       "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "SMRITI Store Manager", "read": 1, "write": 1, "create": 1, "delete": 0},
    {"role": "Sales User",           "read": 1, "write": 0, "create": 0, "delete": 0},
    {"role": "Warehouse User",       "read": 1, "write": 0, "create": 0, "delete": 0}
  ]
}
```

`doctype/smriti_party_stock_account/smriti_party_stock_account.py`
```python
import frappe
from frappe.model.document import Document

class SMRITIPartyStockAccount(Document):
    def validate(self):
        if self.mobile and not self.mobile.isdigit():
            frappe.throw("Mobile number must be numeric.")
```

---

## TASK 1.3 — DocType: SMRITI PSV Settings (Single)

`doctype/smriti_psv_settings/smriti_psv_settings.json`

```json
{
  "doctype": "DocType",
  "name": "SMRITI PSV Settings",
  "module": "Party Stock Visibility",
  "issingle": 1,
  "fields": [
    {"fieldname": "upload_frequency",     "fieldtype": "Select",  "options": "Weekly\nBi-Weekly\nMonthly", "label": "Upload Frequency", "default": "Weekly"},
    {"fieldname": "velocity_weight",      "fieldtype": "Float",   "label": "Velocity Weight",    "default": 0.4},
    {"fieldname": "ageing_weight",        "fieldtype": "Float",   "label": "Ageing Weight",      "default": 0.3},
    {"fieldname": "accuracy_weight",      "fieldtype": "Float",   "label": "Accuracy Weight",    "default": 0.2},
    {"fieldname": "discipline_weight",    "fieldtype": "Float",   "label": "Discipline Weight",  "default": 0.1},
    {"fieldname": "variance_threshold",   "fieldtype": "Float",   "label": "Variance Threshold %", "default": 5.0},
    {"fieldname": "health_check_enabled", "fieldtype": "Check",   "label": "Enable Health Check", "default": 1}
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1}
  ]
}
```

`doctype/smriti_psv_settings/smriti_psv_settings.py`
```python
from frappe.model.document import Document
class SMRITIPSVSettings(Document):
    pass
```

---

## TASK 1.4 — DocType: SMRITI Party Stock Ledger Entry (Hidden/Immutable)

`doctype/smriti_party_stock_ledger_entry/smriti_party_stock_ledger_entry.json`

```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Stock Ledger Entry",
  "module": "Party Stock Visibility",
  "hidden": 1,
  "in_create": 0,
  "fields": [
    {"fieldname": "company",             "fieldtype": "Link",     "options": "Company",                    "label": "Company",           "reqd": 1},
    {"fieldname": "posting_datetime",    "fieldtype": "Datetime",                                          "label": "Posting Datetime",  "reqd": 1},
    {"fieldname": "party_stock_account", "fieldtype": "Link",     "options": "SMRITI Party Stock Account", "label": "Party Stock Account","reqd": 1},
    {"fieldname": "item_code",           "fieldtype": "Link",     "options": "Item",                       "label": "Item Variant",      "reqd": 1},
    {"fieldname": "qty",                 "fieldtype": "Float",                                             "label": "Qty (+/-)",         "reqd": 1},
    {"fieldname": "voucher_type",        "fieldtype": "Select",   "options": "Opening\nDispatch\nSales\nAdjustment\nReturn", "label": "Voucher Type", "reqd": 1},
    {"fieldname": "voucher_no",          "fieldtype": "Data",                                              "label": "Voucher No",        "reqd": 1},
    {"fieldname": "unique_hash",         "fieldtype": "Data",                                              "label": "Unique Hash",       "reqd": 1},
    {"fieldname": "is_reversal",         "fieldtype": "Check",                                             "label": "Is Reversal"},
    {"fieldname": "reversal_of",         "fieldtype": "Data",                                              "label": "Reversal Of (Hash)"},
    {"fieldname": "source_hash",         "fieldtype": "Data",                                              "label": "Source Hash"},
    {"fieldname": "adjustment_type",     "fieldtype": "Data",                                              "label": "Adjustment Type"},
    {"fieldname": "reason",              "fieldtype": "Small Text",                                        "label": "Reason"},
    {"fieldname": "approved_by",         "fieldtype": "Link",     "options": "User",                       "label": "Approved By"},
    {"fieldname": "approved_on",         "fieldtype": "Datetime",                                          "label": "Approved On"}
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 0, "create": 0, "delete": 0}
  ]
}
```

`doctype/smriti_party_stock_ledger_entry/smriti_party_stock_ledger_entry.py`
```python
import frappe
from frappe.model.document import Document

class SMRITIPartyStockLedgerEntry(Document):
    def before_insert(self):
        if not self.unique_hash:
            frappe.throw("unique_hash is required for ledger entry.")

    def on_update(self):
        frappe.throw("PSV Ledger entries are immutable. Editing is not allowed.")

    def on_trash(self):
        frappe.throw("PSV Ledger entries cannot be deleted.")
```

---

## TASK 1.5 — DocType: SMRITI PSV Activity Log (Hidden)

`doctype/smriti_psv_activity_log/smriti_psv_activity_log.json`

```json
{
  "doctype": "DocType",
  "name": "SMRITI PSV Activity Log",
  "module": "Party Stock Visibility",
  "hidden": 1,
  "fields": [
    {"fieldname": "timestamp",         "fieldtype": "Datetime", "label": "Timestamp",          "reqd": 1},
    {"fieldname": "user",              "fieldtype": "Link",     "options": "User", "label": "User"},
    {"fieldname": "action_type",       "fieldtype": "Data",     "label": "Action Type",        "reqd": 1},
    {"fieldname": "severity",          "fieldtype": "Select",   "options": "Info\nWarning\nHigh\nCritical", "label": "Severity", "reqd": 1},
    {"fieldname": "alert_key",         "fieldtype": "Data",     "label": "Alert Key"},
    {"fieldname": "reference_doctype", "fieldtype": "Data",     "label": "Reference DocType"},
    {"fieldname": "reference_name",    "fieldtype": "Data",     "label": "Reference Name"},
    {"fieldname": "details",           "fieldtype": "Long Text","label": "Details"}
  ],
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 0, "create": 0, "delete": 0}
  ]
}
```

`doctype/smriti_psv_activity_log/smriti_psv_activity_log.py`
```python
from frappe.model.document import Document
class SMRITIPSVActivityLog(Document):
    def on_update(self):
        import frappe
        frappe.throw("PSV Activity Logs are immutable.")
    def on_trash(self):
        import frappe
        frappe.throw("PSV Activity Logs cannot be deleted.")
```

---

## TASK 1.6 — DocType: SMRITI PSV Exception Record

`doctype/smriti_psv_exception_record/smriti_psv_exception_record.json`

```json
{
  "doctype": "DocType",
  "name": "SMRITI PSV Exception Record",
  "module": "Party Stock Visibility",
  "autoname": "PSV-EXC-.####",
  "fields": [
    {"fieldname": "party_stock_account", "fieldtype": "Link",      "options": "SMRITI Party Stock Account", "label": "Party Stock Account", "reqd": 1, "in_list_view": 1},
    {"fieldname": "exception_type",      "fieldtype": "Select",    "options": "Cancellation\nNegative Balance\nLate Upload\nAudit Overdue", "label": "Exception Type", "reqd": 1, "in_list_view": 1},
    {"fieldname": "severity",            "fieldtype": "Select",    "options": "Info\nWarning\nHigh\nCritical", "label": "Severity", "reqd": 1, "in_list_view": 1},
    {"fieldname": "status",              "fieldtype": "Select",    "options": "Open\nUnder Review\nResolved\nIgnored", "label": "Status", "default": "Open", "in_list_view": 1},
    {"fieldname": "item_code",           "fieldtype": "Link",      "options": "Item", "label": "Item Variant"},
    {"fieldname": "created_on",          "fieldtype": "Datetime",  "label": "Created On"},
    {"fieldname": "resolved_on",         "fieldtype": "Datetime",  "label": "Resolved On"},
    {"fieldname": "resolved_by",         "fieldtype": "Link",      "options": "User", "label": "Resolved By"},
    {"fieldname": "resolution_notes",    "fieldtype": "Text",      "label": "Resolution Notes"}
  ],
  "permissions": [
    {"role": "System Manager",       "read": 1, "write": 1, "create": 1, "delete": 0},
    {"role": "SMRITI Store Manager", "read": 1, "write": 1, "create": 0, "delete": 0},
    {"role": "Sales User",           "read": 1, "write": 0, "create": 0, "delete": 0},
    {"role": "Warehouse User",       "read": 1, "write": 0, "create": 0, "delete": 0}
  ]
}
```

`doctype/smriti_psv_exception_record/smriti_psv_exception_record.py`
```python
from frappe.model.document import Document
class SMRITIPSVExceptionRecord(Document):
    pass
```

---

## TASK 1.7 — DocType: SMRITI Party Sales Upload + Child

### Child: SMRITI Party Sales Item

`doctype/smriti_party_sales_item/smriti_party_sales_item.json`
```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Sales Item",
  "module": "Party Stock Visibility",
  "istable": 1,
  "fields": [
    {"fieldname": "sales_date", "fieldtype": "Date",  "label": "Sale Date", "in_list_view": 1},
    {"fieldname": "item_code",  "fieldtype": "Link",  "options": "Item", "label": "Item Variant (SKU)", "reqd": 1, "in_list_view": 1},
    {"fieldname": "qty_sold",   "fieldtype": "Float", "label": "Qty Sold", "reqd": 1, "in_list_view": 1}
  ]
}
```

`doctype/smriti_party_sales_item/smriti_party_sales_item.py`
```python
from frappe.model.document import Document
class SMRITIPartySalesItem(Document):
    pass
```

### Parent: SMRITI Party Sales Upload

`doctype/smriti_party_sales_upload/smriti_party_sales_upload.json`
```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Sales Upload",
  "module": "Party Stock Visibility",
  "autoname": "PSV-UPL-.####",
  "title_field": "party_stock_account",
  "fields": [
    {"fieldname": "company",             "fieldtype": "Link",   "options": "Company",                    "label": "Company",           "reqd": 1},
    {"fieldname": "party_stock_account", "fieldtype": "Link",   "options": "SMRITI Party Stock Account", "label": "Party Stock Account","reqd": 1, "in_list_view": 1},
    {"fieldname": "upload_date",         "fieldtype": "Date",                                            "label": "Upload Date",        "reqd": 1, "in_list_view": 1},
    {"fieldname": "period_start_date",   "fieldtype": "Date",                                            "label": "Period From"},
    {"fieldname": "period_end_date",     "fieldtype": "Date",                                            "label": "Period To",          "in_list_view": 1},
    {"fieldname": "excel_file",          "fieldtype": "Attach",                                          "label": "Upload Excel"},
    {"fieldname": "file_hash",           "fieldtype": "Data",                                            "label": "File Hash"},
    {"fieldname": "status",              "fieldtype": "Select", "options": "Draft\nValidated\nImported\nFailed", "label": "Status", "default": "Draft", "in_list_view": 1},
    {"fieldname": "items",               "fieldtype": "Table",  "options": "SMRITI Party Sales Item",    "label": "Sales Items"}
  ],
  "permissions": [
    {"role": "System Manager",       "read": 1, "write": 1, "create": 1, "delete": 1},
    {"role": "SMRITI Store Manager", "read": 1, "write": 1, "create": 1, "delete": 0},
    {"role": "Sales User",           "read": 1, "write": 1, "create": 1, "delete": 0}
  ]
}
```

`doctype/smriti_party_sales_upload/smriti_party_sales_upload.py`
```python
import frappe
from frappe.model.document import Document

class SMRITIPartySalesUpload(Document):
    def validate(self):
        if self.period_end_date and self.period_start_date:
            if self.period_end_date < self.period_start_date:
                frappe.throw("Period End Date cannot be before Period Start Date.")
        total = sum(row.qty_sold for row in self.items if row.qty_sold)
        if total == 0 and self.status not in ("Draft",):
            frappe.throw("Cannot validate upload with zero total qty.")
```

---

## TASK 1.8 — DocType: SMRITI Party Physical Snapshot + Child

### Child: SMRITI Party Physical Item

`doctype/smriti_party_physical_item/smriti_party_physical_item.json`
```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Physical Item",
  "module": "Party Stock Visibility",
  "istable": 1,
  "fields": [
    {"fieldname": "item_code",       "fieldtype": "Link",   "options": "Item", "label": "Item Variant", "reqd": 1, "in_list_view": 1},
    {"fieldname": "system_qty",      "fieldtype": "Float",  "label": "System Qty",   "read_only": 1, "in_list_view": 1},
    {"fieldname": "physical_qty",    "fieldtype": "Float",  "label": "Physical Qty", "reqd": 1,      "in_list_view": 1},
    {"fieldname": "variance",        "fieldtype": "Float",  "label": "Variance",     "read_only": 1, "in_list_view": 1},
    {"fieldname": "variance_reason", "fieldtype": "Select", "options": "\nDamage\nTheft\nData Error\nShortage\nExcess", "label": "Variance Reason"}
  ]
}
```

`doctype/smriti_party_physical_item/smriti_party_physical_item.py`
```python
from frappe.model.document import Document
class SMRITIPartyPhysicalItem(Document):
    pass
```

### Parent: SMRITI Party Physical Snapshot

`doctype/smriti_party_physical_snapshot/smriti_party_physical_snapshot.json`
```json
{
  "doctype": "DocType",
  "name": "SMRITI Party Physical Snapshot",
  "module": "Party Stock Visibility",
  "autoname": "PSV-PHY-.####",
  "fields": [
    {"fieldname": "company",             "fieldtype": "Link",   "options": "Company",                    "label": "Company",      "reqd": 1},
    {"fieldname": "party_stock_account", "fieldtype": "Link",   "options": "SMRITI Party Stock Account", "label": "Party Account","reqd": 1, "in_list_view": 1},
    {"fieldname": "audit_date",          "fieldtype": "Date",                                            "label": "Audit Date",   "reqd": 1, "in_list_view": 1},
    {"fieldname": "status",              "fieldtype": "Select", "options": "Draft\nPending Approval\nApproved\nRejected", "label": "Status", "default": "Draft", "in_list_view": 1},
    {"fieldname": "approved_by",         "fieldtype": "Link",   "options": "User",                       "label": "Approved By"},
    {"fieldname": "approved_on",         "fieldtype": "Datetime",                                        "label": "Approved On"},
    {"fieldname": "items",               "fieldtype": "Table",  "options": "SMRITI Party Physical Item", "label": "Physical Count"}
  ],
  "permissions": [
    {"role": "System Manager",       "read": 1, "write": 1, "create": 1, "delete": 0},
    {"role": "SMRITI Store Manager", "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1},
    {"role": "Warehouse User",       "read": 1, "write": 1, "create": 1, "delete": 0}
  ]
}
```

`doctype/smriti_party_physical_snapshot/smriti_party_physical_snapshot.py`
```python
import frappe
from frappe.model.document import Document

class SMRITIPartyPhysicalSnapshot(Document):
    def validate(self):
        for row in self.items:
            row.variance = (row.physical_qty or 0) - (row.system_qty or 0)

    def on_submit(self):
        self.status = "Pending Approval"
```

---

## TASK 1.9 — Custom Field on Sales Invoice (setup.py)

In `smriti_retail/setup.py`, ADD this function and call it from `after_install()`:

```python
def create_psv_custom_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields({
        "Sales Invoice": [
            {
                "fieldname": "custom_party_stock_account",
                "label": "Party Stock Account (PSV)",
                "fieldtype": "Link",
                "options": "SMRITI Party Stock Account",
                "insert_after": "customer",
                "description": "Link to PSV Party Stock Account for shadow inventory tracking.",
                "allow_on_submit": 0,
            }
        ]
    })
```

---

## TASK 1.10 — hooks.py (ADD ONLY)

In `smriti_retail/hooks.py`, ADD inside `doc_events`:

```python
doc_events = {
    # ... keep all existing entries unchanged ...
    "Sales Invoice": {
        "before_cancel": "smriti_retail.party_stock_visibility.service.psv_service.validate_sales_invoice_cancel",
        "on_submit":     "smriti_retail.party_stock_visibility.service.psv_service.process_sales_invoice_submit",
        "on_cancel":     "smriti_retail.party_stock_visibility.service.psv_service.process_sales_invoice_cancel",
    }
}
```

ADD scheduler:
```python
scheduler_events = {
    # ... keep all existing entries unchanged ...
    "daily": [
        "smriti_retail.party_stock_visibility.service.psv_service.run_psv_daily_health_check"
    ]
}
```

ADD stub service file (Phase 2 will implement):

`party_stock_visibility/service/psv_service.py`
```python
import frappe

def process_sales_invoice_submit(doc, method):
    """Phase 2: Creates PSV Dispatch ledger entries."""
    pass

def process_sales_invoice_cancel(doc, method):
    """Phase 2: Creates reversing ledger entries with is_reversal=1."""
    pass

def validate_sales_invoice_cancel(doc, method):
    """Phase 2: Creates exception records if cancellation produces negative balance."""
    pass

def run_psv_daily_health_check():
    """Phase 2: Negative balance + late upload + audit overdue checks."""
    pass
```

---

## VERIFICATION COMMANDS

```bash
cd /home/frappe/frappe-bench

# Migrate
bench --site smriti.localhost migrate

# Verify all DocTypes
bench --site smriti.localhost execute \
  "import frappe; dts = ['SMRITI Party Stock Account','SMRITI PSV Settings','SMRITI Party Stock Ledger Entry','SMRITI PSV Activity Log','SMRITI PSV Exception Record','SMRITI Party Sales Upload','SMRITI Party Physical Snapshot']; [print(dt, '✅') for dt in dts if frappe.db.exists('DocType', dt)]"

# Verify custom field
bench --site smriti.localhost execute \
  "import frappe; print(frappe.db.exists('Custom Field', 'Sales Invoice-custom_party_stock_account') and '✅ Custom field exists' or '❌ Missing')"

# Verify hooks
bench --site smriti.localhost execute \
  "import frappe; hooks = frappe.get_hooks('doc_events'); si = hooks.get('Sales Invoice',{}); print('on_submit:', si.get('on_submit')); print('before_cancel:', si.get('before_cancel'))"

# Verify module
bench --site smriti.localhost list-modules 2>&1 | grep -i "party stock"
```

---

## PHASE 1 ACCEPTANCE GATE

- [ ] All 7 DocTypes visible in ERPNext under Party Stock Visibility module
- [ ] SMRITI Party Stock Account — create/save works
- [ ] SMRITI PSV Settings — single form opens
- [ ] SMRITI Party Stock Ledger Entry — hidden, edit throws error, delete throws error
- [ ] SMRITI Party Sales Upload — child table populates
- [ ] SMRITI Party Physical Snapshot — variance auto-calculates on validate
- [ ] Sales Invoice has `custom_party_stock_account` field visible
- [ ] hooks.py — existing hooks intact, PSV hooks added
- [ ] bench migrate — 0 errors, 0 warnings
- [ ] Stub psv_service.py — no import errors

**DO NOT proceed to Phase 2 until all 10 gates pass.**


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