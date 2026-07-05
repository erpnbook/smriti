---
Document ID: "DEV-068"
Title: "Walkthrough: Enhanced Supplier Registry in SMRITI Retail OS"
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

# Walkthrough: Enhanced Supplier Registry in SMRITI Retail OS

We have successfully enhanced the Supplier Registry module in SMRITI Retail OS to fully support all standard and advanced supplier fields available in ERPNext/Frappe v16. The user interface now offers a clean, retail-centric quick creation flow while giving access to complete compliance, purchase controls, and defaults.

---

## 🛠️ Changes Implemented

### 1. Backend API Enhancements
- **Modified** [master_api.py](../../apps/smriti_retail_os/smriti_retail_os/master_api.py):
  - Updated `get_supplier_detail(name)` to fetch all standard operational and compliance fields (e.g. currency, price list, bank account, transporter/internal flags, freeze, hold type/release date, RFQ/PO warnings, website, details).
  - Updated `save_supplier_detail(**kwargs)` to accept and map all basic and advanced fields to the `Supplier` document.
  - Implemented dynamic status mapping (`Active`, `Disabled`, `On Hold`) to Frappe's `disabled` and `on_hold` field flags.
  - Resolved `DoesNotExistError` in contacts by filtering the `Dynamic Link` query specifically with `parenttype="Contact"` (since Address records also use `Dynamic Link` records to associate to the Supplier).
  - Created or updated linked `Contact` records automatically on save.

### 2. Frontend User Interface Upgrades
- **Modified** [suppliers.html](../../apps/smriti_retail_os/smriti_retail_os/www/suppliers.html):
  - Structured the creation modal into two core visual panels:
    - **General Profile** (Basic Details): Naming Series, Supplier Name, Supplier Type, Contact Person, Status, Mobile, Email, GSTIN, GST Category, PAN, Billing Address, and Shipping Address (with "Same as Billing" checkbox).
    - **Advanced Details** (Collapsible Toggle): Pricing & Defaults, Internal & Logistics Settings, Purchase Controls & Holds, Warnings & Prevent Rules, and Extra Metadata.
  - Bound dynamic backend options load for Supplier Group, Naming Series, Payment Terms, Default Currency, Default Price List, Bank Account, Company, and Language.
  - Fixed syntax errors inside the Javascript `<script>` block by cleaning up a duplicated HTML code injection.

---

## 📸 Interface Walkthrough

### 1. Supplier Registry Directory Table
The Supplier Registry displays a sleek dark-themed grid of all registered vendors with badges for credit terms and system identifiers:

![Supplier Registry Overview](./images/suppliers_registry_final.png)

### 2. General Profile Form Modal (Basic Details)
When adding or editing, the user is presented with a standard basic profile form by default:

![Quick Add Supplier - Basic Details](./images/suppliers_modal_open.png)

### 3. Advanced Details Panel (Logistics, Compliance, and Controls)
Toggling "Advanced Details" expands settings for price list matching, credit terms, internal/transporter flags, freeze statuses, and custom warning triggers:

![Quick Add Supplier - Advanced Details](./images/suppliers_modal_scrolled.png)

---

## ✅ Verification and Testing Results
- Verified that all dynamic list options (like Currency list, Price List, Bank accounts) fetch correctly.
- Created `Test Advanced Supplier` with the following parameters:
  - **Status**: On Hold (Hold Type = Invoices, Release Date = 2026-12-31)
  - **India GST**: GSTIN = `29AABCR1718E1ZL` (state resolved automatically to Karnataka)
  - **Advanced Settings**: Credit Days = `45`, Transporter = `Checked`, Website = `www.testsupplier.com`
  - **Billing & Shipping Address**: Successfully matched and synced.
- The record saved correctly and reloaded on the fly. Editing the record works perfectly and updates the listing dynamically.


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