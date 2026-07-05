---
Document ID: DEV-071
Title: SMRITI POS Profile Developer Guide
Owner: Development Team
Audience: Developer
Module: Core
Version: 1.0.0
Status: Active
Primary Document: Yes
Depends On: ""
Related Modules: ""
Last Updated: 2026-06-25
Last Reviewed: 2026-06-25
AI Generated: Yes
Reviewed By: Jawahar R. Mallah
---

# SMRITI POS Profile Developer Guide

This developer guide details the backend architecture, service layers, security guards, and cloning utilities for POS Profile Management in SMRITI Retail OS.

---

## 🏗️ Architecture Design

SMRITI POS Profile Management is built on a clean separation of concerns, separating controllers, validation logic, database persistence, and native ERPNext documents:

```text
               SMRITI Standalone UI (HTML/JS)
                             │
                             ▼
                      SMRITI API Layer
                 (api/pos_profile_api.py)
                    - Input serialization
                    - User role permission check
                             │
                             ▼
                    SMRITI Service Layer
               (services/pos_profile_service.py)
                  - Business logic & rules
                  - Shift lock guards & cloning
                             │
                             ▼
                 SMRITI Repository Layer
             (repositories/pos_profile_repository.py)
                  - Database CRUD operations
                             │
                             ▼
                    ERPNext POS Profile
```

---

## 📂 Code Files Layout

The implementation is located across the following files:

### 1. Repository Layer
*   **File**: `smriti_retail_os/repositories/pos_profile_repository.py`
*   **Purpose**: Encapsulates raw database queries and CRUD operations.
*   **Key Methods**:
    *   `get_profiles()`: Fetches the listing of active profiles.
    *   `get_profile_by_name(name)`: Retrieves a profile and its child tables (`payments`, `applicable_for_users`).
    *   `save_profile(data)`: Upserts the POS Profile document and child tables.
    *   `disable_profile(name)`: Performs soft delete by setting `disabled = 1`.

### 2. Service Layer
*   **File**: `smriti_retail_os/services/pos_profile_service.py`
*   **Purpose**: Implements business logic and shift lock safety validation.
*   **Key Methods**:
    *   `check_shift_lock(profile_name)`: Queries the database for open `POS Opening Entry` records. Throws `ValidationError` if an active shift is detected.
    *   `clone_profile(source_name, target_name)`: Copies the settings of a source profile to a new profile document.
    *   `get_dropdowns()`: Retrieves list mappings for Companies, Warehouses, Cashiers, and Payment Modes.

### 3. API Layer
*   **File**: `smriti_retail_os/api/pos_profile_api.py`
*   **Purpose**: Whitelists endpoints for the UI, performs role checks, and serializes requests.
*   **Permissions**: Restricts write operations to the `Administrator` and `System Manager` roles.

---

## 🔒 Technical Implementation: Shift Lock Guard

The shift lock protection prevents editing critical transaction configurations while a cashier has an open terminal drawer.

### Shift Check Routine
The service layer executes the following query to check for active shifts:
```python
def check_shift_lock(profile_name):
    active_shift = frappe.db.get_value(
        "POS Opening Entry",
        {"pos_profile": profile_name, "status": "Open", "docstatus": 1},
        ["name", "user"],
        as_dict=True
    )
    if active_shift:
        frappe.throw(
            f"Cannot modify POS Profile while an active shift ({active_shift.name}) is open for user {active_shift.user}.",
            frappe.ValidationError
        )
```

This verification is run in the service layer inside both `save_profile` (if warehouse, cashiers, or payments are modified) and `disable_profile` functions.

---

## 👥 Cloned Profile Setup

The `clone_profile` method deep-copies details from a source profile:
1.  Loads the source `POS Profile` document.
2.  Instantiates a new `POS Profile` document with a unique target name.
3.  Copies core properties (`company`, `warehouse`, `selling_price_list`, `currency`, `write_off_account`, `write_off_cost_center`).
4.  Appends copies of child tables:
    *   `payments` (linked payment mode default clearing accounts).
    *   `applicable_for_users` (assigned cashiers).
5.  Saves and commits the new document.

---

## 🧪 Unit Testing

Unit tests are implemented under `smriti_retail_os/tests/test_pos_profile.py`.

### Running Tests
To execute POS Profile unit tests inside the docker environment:
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail run-tests --app smriti_retail_os --module smriti_retail_os.tests.test_pos_profile
```

---

## Related Documents
*   [SMRITI OS POS Profile Overview](../01-product/pos_profile_overview.md)
*   [SMRITI OS POS Profile API Reference](../06-api/pos_profile_api.md)
*   [SMRITI OS POS Profile Setup Guide](../03-admin-guide/pos_profile_setup.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial developer documentation release for POS Profile Custom Management |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
