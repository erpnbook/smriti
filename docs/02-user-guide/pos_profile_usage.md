---
Document ID: USER-030
Title: SMRITI OS POS Profile User Guide
Owner: Operations Team
Audience: End User
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

# SMRITI OS POS Profile User Guide

This user guide shows store managers, cashier supervisors, and operations staff how to use the custom **POS Profile Management Console** inside SMRITI Retail OS to manage cash register terminal configurations.

---

## 🖥️ The POS Profile Interface

To open the console:
1. Navigate to SMRITI Retail OS.
2. Under the **Administration** menu, select **POS Profiles**.
3. You will see a dashboard listing all current checkout profiles, their assigned warehouses, active cashiers, status (Active/Disabled), and the last updated timestamp.

### Searching and Filtering Profiles
*   **Search Bar**: Type the profile name (e.g. `Store 01 - Lane 1`) or warehouse code to quickly filter the list.
*   **Company Filter**: If managing multiple legal entities, select the Company from the dropdown to only see their registers.
*   **Warehouse Filter**: Filter profiles by specific inventory stock locations.

---

## 🛠️ Performing Key Tasks

### 1. View & Edit a Profile
1. Click on any profile row in the list.
2. A configuration panel slides out from the **right side** of the screen.
3. Review or edit settings across the four tabs:
   *   **General**: Set basic rules (Price List, Walk-in Customer).
   *   **Payments**: Add payment options (Cash, Cards, UPI) and default ledgers.
   *   **Cashiers**: Manage cashiers assigned to this terminal.
   *   **Advanced**: Check audit trails and trigger cloning.
4. Click the **Save Profile** button at the bottom of the drawer to submit changes.

### 2. Cloning an Existing Profile
When adding a new checkout lane, cloning an existing setup saves time:
1. Click on the profile you want to copy.
2. Navigate to the **Advanced** tab in the right-hand drawer.
3. In the **Clone Profile** section, enter the name of the new profile (e.g., `Store 01 - Lane 02`).
4. Click **Clone**.
5. The drawer will automatically load your new cloned profile. Update its default warehouse or cashier roster as needed and click **Save Profile**.

### 3. Disabling (Archiving) a Profile
To decommission a register terminal:
1. Click the profile row to open its details.
2. On the **General** tab, toggle the **Disabled** switch to `ON` (or click **Archive Profile** in the action footer).
3. Confirm the choice. The terminal will immediately be deactivated and removed from check-in lists.

---

## 🔒 Operational Safeguards (Shift Locks)

SMRITI protects current shifts from administrative errors. If a cashier has opened a shift (via `POS Opening Entry`) on a terminal:

1.  **UI Banner**: A warning alert will appear at the top of the details drawer:
    > ⓘ Shift lock active: Shift SH-2026-00124 is currently open. Warehouse, Payments, and Cashiers cannot be modified.
2.  **Field Locking**: Warehouse inputs, cashier list edit actions, and payment account selectors will be grayed out and disabled.
3.  **Archiving Blocked**: The profile cannot be archived while a shift is open.
4.  **How to edit**: To change these properties, the cashier must first close their shift (submit their `POS Closing Entry` cash reconciliation). Once closed, settings become editable again.

---

## Related Documents
*   [SMRITI OS POS Profile Overview](../01-product/pos_profile_overview.md)
*   [SMRITI OS POS Profile Setup Guide](../03-admin-guide/pos_profile_setup.md)
*   [Frequently Asked Questions — POS Operations](./pos.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial user guide release for POS Profile Management UI |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
