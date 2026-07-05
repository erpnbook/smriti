---
Document ID: API-002
Title: SMRITI POS Profile API Reference Manual
Owner: Integration Team
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

# SMRITI POS Profile API Reference Manual

This document details the whitelisted API endpoints exposed by SMRITI Retail OS for managing checkout lane POS Profiles.

---

## 🔒 Authentication & Role Security

All endpoints require active user session cookies. Write endpoints (`save_profile`, `clone_profile`, `archive_profile`) check permissions and throw a `PermissionError` (403/401 equivalent) if the user does not have the **Administrator** or **System Manager** roles.

---

## 📡 Endpoints Specification

### 1. List POS Profiles (`get_profiles`)
Retrieves a list of all POS Profiles.

*   **HTTP Method**: `GET`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.get_profiles`
*   **Parameters**: None
*   **Response JSON**:
    ```json
    {
      "message": [
        {
          "name": "Store 01 - Main Checkout",
          "company": "Test Company",
          "warehouse": "Main Store - TC",
          "disabled": 0,
          "modified": "2026-06-25 09:30:15"
        }
      ]
    }
    ```

---

### 2. Get Profile Details (`get_details`)
Retrieves detailed information of a specific profile, including payment modes and Cashier roster mapping.

*   **HTTP Method**: `GET`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.get_details`
*   **Parameters**:
    *   `name` (string, Required): The exact name/ID of the POS Profile.
*   **Response JSON**:
    ```json
    {
      "message": {
        "name": "Store 01 - Main Checkout",
        "company": "Test Company",
        "warehouse": "Main Store - TC",
        "selling_price_list": "Standard Selling",
        "currency": "INR",
        "disabled": 0,
        "payments": [
          {
            "mode_of_payment": "Cash",
            "default_account": "Cash Account - TC",
            "default": 1
          }
        ],
        "applicable_for_users": [
          {
            "user": "cashier@smriti.local"
          }
        ]
      }
    }
    ```

---

### 3. Save POS Profile (`save_profile`)
Creates or updates a POS Profile record. Evaluates active shift locks before saving.

*   **HTTP Method**: `POST`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.save_profile`
*   **Parameters**:
    *   `doc_data` (object/dict, Required): Profile parameters schema (nested payments and cashiers list).
*   **Response JSON**:
    ```json
    {
      "message": "Store 01 - Main Checkout"
    }
    ```
*   **Error Codes**:
    *   `400 ValidationError`: Raised if an active shift lock is detected, or if mandatory fields are missing.

---

### 4. Clone POS Profile (`clone_profile`)
Duplicates settings and child tables of a source profile under a new unique target profile name.

*   **HTTP Method**: `POST`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.clone_profile`
*   **Parameters**:
    *   `source_name` (string, Required): Name of the profile to clone from.
    *   `target_name` (string, Required): Name of the new profile to create.
*   **Response JSON**:
    ```json
    {
      "message": "Store 01 - Express Lane 02"
    }
    ```

---

### 5. Archive POS Profile (`archive_profile`)
Deactivates a profile. Soft-delete operation (`disabled = 1`). Fails if active shifts exist.

*   **HTTP Method**: `POST`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.archive_profile`
*   **Parameters**:
    *   `name` (string, Required): Profile name to deactivate.
*   **Response JSON**:
    ```json
    {
      "message": "Store 01 - Main Checkout"
    }
    ```

---

### 6. Get Dropdown Fields (`get_dropdowns`)
Retrieves list options for Companies, Warehouses, Cashiers, and Payment Modes.

*   **HTTP Method**: `GET`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.get_dropdowns`
*   **Parameters**: None
*   **Response JSON**:
    ```json
    {
      "message": {
        "companies": ["Test Company"],
        "warehouses": ["Main Store - TC"],
        "price_lists": ["Standard Selling"],
        "cashiers": ["cashier@smriti.local"],
        "payment_modes": ["Cash", "UPI", "Credit Card"]
      }
    }
    ```

---

### 7. Validate Shift Lock (`validate_profile`)
Checks if a profile has an active open cashier shift.

*   **HTTP Method**: `GET`
*   **Endpoint URL**: `/api/method/smriti_retail_os.api.pos_profile_api.validate_profile`
*   **Parameters**:
    *   `name` (string, Required): POS Profile name.
*   **Response JSON**:
    ```json
    {
      "message": {
        "is_locked": true,
        "active_shift": {
          "name": "SH-2026-00124",
          "user": "cashier@smriti.local"
        }
      }
    }
    ```

---

## Related Documents
*   [SMRITI POS Profile Developer Guide](../05-developer/pos_profile_developer.md)
*   [SMRITI OS POS Profile Overview](../01-product/pos_profile_overview.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial API Reference release |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
