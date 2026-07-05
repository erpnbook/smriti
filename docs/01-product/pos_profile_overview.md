---
Document ID: PROD-012
Title: SMRITI OS POS Profile Overview
Owner: Product Team
Audience: Product / Executive
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

# SMRITI OS POS Profile Overview

SMRITI Retail OS introduces a dedicated, standalone **POS Profile Management Console**. In line with SMRITI's core UI directive (Rule 7), this feature eliminates all direct user exposure to Frappe Desk and native ERPNext setup screens, replacing them with a fast, modern, and highly secure checkout configuration portal.

## Business Value

The checkout lane is the most critical touchpoint in a retail environment. Downtime, configuration errors, unauthorized cashier assignments, or warehouse mapping mix-ups directly impact store revenue and inventory accuracy. SMRITI POS Profile Management offers retail executives and store managers:

*   **Zero-Exposure Administration**: Managers configure checkout rules without exposing complex and confusing database-level Desk interfaces to store staff.
*   **Operational Continuity Protection (Shift Lock)**: Core properties such as stock warehouses, currency settings, payment accounts, and cashier rosters are locked from editing while a terminal is actively conducting business, preventing mid-shift transactional discrepancies.
*   **Rapid Store Expansion (Cloning)**: Deploying a new checkout counter takes seconds. Managers can clone an existing verified profile, preserving payment mappings and user credentials, and simply change the name or warehouse.
*   **Store-Level Isolation**: POS warehouse and payment ledger configurations are isolated at the cashier level to prevent cross-region or cross-lane data contamination.

---

## Key Capabilities

### 1. Unified Setup Drawer
Configuring a POS Profile is managed through a clean, right-side sliding pane containing four tabbed sections:
*   **General Settings**: Set Company, Warehouse, Selling Price List, and Currency defaults.
*   **Payments Grid**: Configure split-payment modes (Cash, Cards, UPI, Wallets) and associate default ledger clearing accounts.
*   **Cashier Roster**: Map store staff and cashier user accounts authorized to log into the terminal.
*   **Advanced Panel**: Actionable options to clone profiles, view creation timestamps, and access audit records.

### 2. Intelligent Shift Lock Guard
SMRITI checks for active shifts (using ERPNext `POS Opening Entry` status `"Open"`) linked to the profile. If an active shift is detected:
*   The UI renders a persistent banner: `ⓘ Shift lock active: Shift SH-XXX is currently open. Warehouse, Payments, and Cashiers cannot be modified.`
*   Inputs for Warehouse, Mode of Payments, and cashier assignments are disabled.
*   Backend service validation prevents any programmatic updates or deletion, raising a clear explainable validation error.

### 3. Soft-Deletion (Archiving)
To maintain referential integrity and audit histories, profiles are never physically deleted from the database. Deleting a profile from the SMRITI interface flags it as `disabled = 1` (archived), immediately removing it from active selection lists while preserving transaction histories.

---

## Related Documents
*   [DOCUMENTATION_MANIFEST](../DOCUMENTATION_MANIFEST.md)
*   [SMRITI OS POS Profile Setup Guide](../03-admin-guide/pos_profile_setup.md)
*   [SMRITI OS POS Profile User Guide](../02-user-guide/pos_profile_usage.md)

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial product overview guide release for POS Profile Console |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
