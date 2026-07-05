---
Document ID: "SMRITI-ARCH-002"
Title: "SMRITI Universal Document Numbering Engine (UDNE)"
Owner: "Core Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Draft"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Universal Document Numbering Engine (UDNE) — Implementation Plan

---

## 📋 Document Metadata
- **Document ID**             : SMRITI-ARCH-002
- **Document Family**         : Architecture & Platform Design
- **Document Classification** : Core Module Specification
- **Product**                 : SMRITI Retail OS
- **Release**                 : v1.0 GA
- **Document Version**        : 1.0
- **Release Status**          : DRAFT
- **Owner**                   : AITDL
- **Chief Architect**         : Jawahar R. Mallah

---

## Governing Principle
> **Every document generated in SMRITI shall obtain its identity from the Universal Document Numbering Engine (UDNE). Number generation must be configurable, auditable, offline-safe, financial-year aware, and independent of the underlying ERP transaction model.**

---

## 1. Architectural Blueprint
The numbering engine operates as an independent platform service layer that overrides standard document naming before insert operations:

```text
       SMRITI Terminals / UI           SMRITI Services (Billing, Stock, etc.)
                │                                         │
                ▼                                         ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Numbering Service (Central Coordinator)         │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
Series Resolver             FY Resolver                 Counter Manager
(Token Compiler)       (April-March/Jan-Dec)       (Store/Terminal Locks)
      │                           │                           │
      └───────────────────────────┼───────────────────────────┘
                                  ▼
                        Reservation Manager
                   (Offline Ranges: 1000 - 1999)
                                  │
                                  ▼
                         Duplicate Validator
                    (Conflict & Gap Detection)
                                  │
                                  ▼
                            Audit Logger
                   (SMRITI Numbering Audit Log)
                                  │
                                  ▼
                             ERP Mapper
                    (Assigns doc.name / series)
```

---

## 2. Component Breakdown

### Component A: Database Schema Extensions (`setup.py`)
To store rules, counters, offline ranges, and audit entries, we will define three lightweight DocTypes inside SMRITI:

1. **`SMRITI Numbering Rule`**:
   - `document_type`: Link (`DocType`)
   - `mode`: Select (`Auto`, `Manual`, `Hybrid`)
   - `prefix`: Data (e.g. `{branch}/FY{fy}/INV/`)
   - `suffix`: Data (e.g. `-{store}`)
   - `digits`: Int (e.g. `6` digits zero-padded)
   - `reset_rule`: Select (`Never`, `Yearly`, `Monthly`, `Daily`, `Financial Year`, `Store`, `Terminal`)
   - `is_active`: Check

2. **`SMRITI Numbering Counter`**:
   - `rule`: Link (`SMRITI Numbering Rule`)
   - `key`: Data (composed reset key, e.g., `MUMBAI-FY26-INV`)
   - `current_value`: Int (last generated count)

3. **`SMRITI Numbering Reserved Range`** (Offline Safe):
   - `document_type`: Link (`DocType`)
   - `terminal_id`: Data
   - `start_number`: Int
   - `end_number`: Int
   - `current_counter`: Int
   - `is_active`: Check

4. **`SMRITI Numbering Audit Log`**:
   - `document_type`: Link (`DocType`)
   - `document_name`: Data (the actual final primary key)
   - `generated_number`: Data
   - `prefix`: Data
   - `suffix`: Data
   - `counter_value`: Int
   - `terminal_id`: Data
   - `branch`: Link (`Warehouse`)
   - `user`: Link (`User`)
   - `timestamp`: Datetime

---

### Component B: Backend Core Services (`smriti_retail_os/services/udne/`)

1. **`series_resolver.py`**:
   - Compiles dynamic tokens:
     - `{store}` ➔ Resolves from Session / Company settings.
     - `{branch}` ➔ Resolves store location code.
     - `{state}` ➔ Resolves GST state code.
     - `{fy}` ➔ Resolves Financial Year string (e.g., `25-26`).
     - `{month}` ➔ Two-digit current month (`06`).
     - `{year}` ➔ Four-digit current year (`2026`).
     - `{terminal}` ➔ Cash register/POS device ID.
     - `{user}` ➔ Cashier initials or code.
     - `{company}` ➔ Company initials.
     - `{department}` ➔ Custom attribute fallback.

2. **`fy_resolver.py`**:
   - Calculates financial years based on dynamic dates. Supports standard Indian financial year (April 1 to March 31) and calendar year.

3. **`counter_manager.py`**:
   - Thread-safe transaction locks to increment counters without race conditions.

4. **`reservation_manager.py`**:
   - Allocates number blocks (ranges) to specific terminals for offline POS billing.
   - Example: Terminal `POS-01` requests a block of 1,000 numbers. Reservation Manager registers `start: 1000, end: 1999`. The POS terminal uses these locally and syncs back when online.

5. **`duplicate_validator.py`**:
   - Performs check: `frappe.db.exists(doctype, generated_name)` before commit.
   - If conflict detected, suggests next sequence number or throws exception.

6. **`audit_logger.py`**:
   - Appends read-only records to `SMRITI Numbering Audit Log`.

---

### Component C: ERP Interception (`hooks.py` Integration)
We will register `autoname` hook overrides for all supported DocTypes:
```python
doc_events = {
    "POS Invoice": {
        "autoname": "smriti_retail_os.services.udne.hooks.autoname_document"
    },
    "Sales Invoice": {
        "autoname": "smriti_retail_os.services.udne.hooks.autoname_document"
    },
    #quotation, orders, delivery note, stock entry, etc.
}
```

Inside the naming hook:
- If a SMRITI numbering rule exists for the DocType:
  - Resolve the series name.
  - Set `doc.name = resolved_name`.
  - Otherwise, fall back to Frappe standard naming.

---

### Component D: Frontend UI Settings Panel (`smriti-udne.html`)
A standalone SMRITI-themed administration page (`/app/smriti-udne` or `/smriti-udne` canonical route) that provides:
1. **Rule Selector**: Dropdown choosing the target document.
2. **Interactive Builder**: Grid to configure Prefixes, Suffixes, resets, and padding digits.
3. **Live Preview Panel**: Resolves variables mock-data dynamically as you type (e.g. `MUM/FY26/INV/000123`).
4. **Reservation Dashboard**: Displays blocks reserved by active POS terminals.

---

## 3. Risks & Mitigations

| Risk | Description | Mitigation | Status |
|---|---|---|---|
| Number Collisions | Offline terminals generating same receipt numbers | Terminals use pre-reserved range blocks mapped to terminal IDs | **Designed** |
| Concurrent Inserts | Double-clicks or simultaneous submits incrementing same count | Row locks on `SMRITI Numbering Counter` during fetch-and-update | **Designed** |
| Manual Conflict | User inserts a manual/hybrid ID that already exists in DB | Duplicate validator intercepts insert and forces unique constraint | **Designed** |

---

## Verification Plan

### Automated Tests
Add `test_udne.py` validating:
- **`test_auto_numbering`**: Generates sequences sequentially.
- **`test_token_resolution`**: Verifies `{fy}`, `{state}`, and `{branch}` resolve accurately.
- **`test_reset_rules`**: Tests daily/monthly/annual resets.
- **`test_offline_block_reservation`**: Simulates reservation and sync validation.
- **`test_duplicate_rejection`**: Verifies manual duplicate names are rejected.
