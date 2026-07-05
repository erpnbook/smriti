---
Document ID: "ADMIN-009"
Title: "SMRITI OS POS Profile Setup Guide"
Owner: "Administration Team"
Audience: "Administrator"
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

# SMRITI OS POS Profile Setup Guide

This guide details configuring and maintaining SMRITI POS Profiles, mapping payment modes, assigning cashiers, and enforcing shift lock safety checks inside SMRITI Retail OS.

---

## 🖥️ SMRITI POS Profile Interface

In accordance with SMRITI UI Governance (Rule 7), managers and administrators must configure all POS settings inside the custom SMRITI interface located at `/smriti-pos-profiles`. Exposing the native Frappe Desk (`/desk`) or ERPNext standard lists is strictly prohibited.

---

## 🛠️ Configuring a POS Profile

To add or modify a profile, click on it in the SMRITI list to open the right-side configuration drawer. The setup is divided into four main sections:

### 1. General Tab
Configure default operational parameters:
*   **Profile Name**: Unique name (e.g. `Register-01`).
*   **Warehouse**: Stock source warehouse (e.g. `Store 01 - Main - TSC`).
*   **Selling Price List**: Catalog price list (e.g. `Standard Selling`).
*   **Currency**: Trading currency (e.g. `INR`).
*   **Walk-in Customer**: Default customer for checkout if none is selected (e.g. `Walk-in Customer`).
*   **Disabled**: Toggle to `1` (ON) to archive the profile.

### 2. Payments Tab
Map active modes of payment to default accounting ledger accounts:
*   **Mode of Payment**: The transaction type (e.g., `Cash`, `Credit Card`, `UPI`).
*   **Default Account**: The Chart of Accounts ledger name for clearing (e.g. `Cash - TSC`).
*   **Default**: Mark exactly one mode of payment as the default checkout method.

### 3. Cashiers Tab
Roster cashier users permitted to open the terminal:
*   Add user emails (e.g., `cashier01@smriti.local`) to the authorized users list.
*   A cashier can only be assigned to a terminal if they do not have active shifts open on another profile.

### 4. Advanced Tab
Contains audit information (created by, modified by, creation date) and the Profile Cloning utility.

---

## 🔒 Shift Lock Policy

To preserve financial audit integrity, SMRITI enforces a zero-exception **Shift Lock** policy.

### Active Shift Detection
SMRITI checks for any `POS Opening Entry` matching the profile name with `status = "Open"` and `docstatus = 1`. If an active shift is detected:
*   **Locked Actions**: Adding or removing payment modes, changing the default warehouse, updating cashier assignments, and disabling/deleting the profile are blocked.
*   **Programmatic Exceptions**: Any attempt to save these changes programmatically raises a `ValidationError`:
    ```text
    ValidationError: Cannot modify Warehouse, Payments, or Cashier assignments while an active shift (SH-2026-00124) is open.
    ```

---

## 📋 Worked Configuration Example

Below is a serialized configuration payload:

```json
{
  "doctype": "POS Profile",
  "name": "Store 01 - Express Lane 01",
  "company": "Test SMRITI Company",
  "warehouse": "Store 01 - Main - TSC",
  "selling_price_list": "Standard Selling",
  "currency": "INR",
  "write_off_account": "Temporary Write Off Account - TSC",
  "write_off_cost_center": "Main Cost Center - TSC",
  "payments": [
    {
      "mode_of_payment": "Cash",
      "default_account": "Cash - TSC",
      "default": 1
    }
  ],
  "applicable_for_users": [
    {
      "user": "cashier01@smriti.local"
    }
  ]
}
```

---

## Related Documents
*   [SMRITI OS POS Profile Overview](../01-product/pos_profile_overview.md)
*   [SMRITI OS POS Profile User Guide](../02-user-guide/pos_profile_usage.md)
*   [SMRITI POS Profile Developer Guide](../05-developer/pos_profile_developer.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized for SMRITI custom console interface |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL