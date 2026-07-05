---
Document ID: KB-031
Title: Troubleshooting SMRITI POS Profile Issues
Owner: Support Team
Audience: Administrator
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

# Troubleshooting SMRITI POS Profile Issues

This troubleshooting article addresses common setup blockers and operational error codes encountered while configuring POS Profiles in SMRITI Retail OS.

---

## 🚫 Issue 1: Shift Lock Validation Block

### Problem Description
Administrators or store managers receive a validation block when trying to save changes (Warehouse, Payments grid, Cashier assignments) or deactivate/delete a POS Profile.

### Symptoms
*   **UI Alert**: A warning banner is displayed at the top of the details drawer:
    `ⓘ Shift lock active: Shift SH-XXXXX is currently open. Warehouse, Payments, and Cashiers cannot be modified.`
*   **Backend Exception**: Saving via the SMRITI API throws:
    ```text
    ValidationError: Cannot modify Warehouse, Payments, or Cashiers while an active shift (SH-XXXXX) is open.
    ```

### Cause
SMRITI checks for an active, open `POS Opening Entry` (status `"Open"`, docstatus `1`) linked to the POS Profile. To prevent accounting reconciliation and stock ledger issues, modifications to transaction rules are blocked until the cashier closes out their drawer.

### Resolution Steps
1.  Identify the open shift name (`SH-XXXXX`) from the UI alert or error message.
2.  Navigate to the POS Terminal or Shift closing interface.
3.  Proceed with shift closing:
    *   Perform reconciliation of cash, credit card, and digital payment receipts.
    *   Create and submit the `POS Closing Entry` document.
4.  Once the shift status transitions to `"Closed"`, open the SMRITI POS Profiles page.
5.  Make the necessary adjustments (e.g. assign cashiers or change the warehouse) and click **Save Profile**.

### Verification
Open the POS Profile details drawer. Verify that the shift warning banner has disappeared and that the inputs are now enabled.

### Prevention
Plan profile configuration adjustments (such as cashier rotation or stock warehouse modifications) before store hours start or during shift handover times, ensuring all lanes are closed.

---

## 🚫 Issue 2: Mode of Payment Account Mappings Blocker

### Problem Description
Saving a POS Profile fails with a "Missing Account" validation error from the ERPNext backend.

### Symptoms
*   **Error Dialog**:
    ```text
    Missing Account: Please set default Cash or Bank account in Mode of Payments HDFC Card
    ```

### Cause
Every Mode of Payment mapped inside the **Payments** table of a POS Profile must be mapped to an active Chart of Accounts ledger corresponding to the selected profile's Company. If this mapping is missing, the financial transactions cannot resolve which account to debit/credit.

### Resolution Steps
1.  Identify the problematic Mode of Payment (e.g., `HDFC Card`) from the error message.
2.  Open the Mode of Payment record:
    *   If using SMRITI, navigate to the Payment Configurations section.
    *   Select the target Mode of Payment.
3.  Locate the company-wise ledger accounts table.
4.  Add a row for your Company, select the default clearing/asset account ledger, and click **Save**.
5.  Re-open `/smriti-pos-profiles`, edit the profile, and click **Save Profile**.

### Verification
Verify that the profile is saved successfully without raising the "Missing Account" error.

### Prevention
Ensure that when a new Company is provisioned or a new Mode of Payment is introduced, account mappings are populated in the Chart of Accounts before linking them to terminal profiles.

---

## Related Documents
*   [SMRITI OS POS Profile Setup Guide](../03-admin-guide/pos_profile_setup.md)
*   [SMRITI OS POS Profile User Guide](../02-user-guide/pos_profile_usage.md)
*   [Frequently Asked Questions — POS Operations](../02-user-guide/pos.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial troubleshooting guide release |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
