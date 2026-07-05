---
Document ID: "PROD-007"
Title: "SMRITI OS First Login Guide"
Owner: "Product Team"
Audience: "Product / Executive"
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

# SMRITI OS First Login Guide

This guide describes how to access SMRITI Retail OS for the first time, manage default user credentials, and configure system role permissions.

## 🔑 Accessing the System

Once SMRITI is installed and site services are active:
1. Open your browser and navigate to the root route:
   ```text
   http://localhost:8765/
   ```
2. Log in using default administrator credentials:
   - **Username**: `Administrator`
   - **Password**: `admin` (or the custom password configured during site initialization).

---

## 🛡️ Routing & Security Redirects

SMRITI enforces a strict **SMRITI-First UI Policy (Rule 7)**. Standard Frappe/ERPNext Desk panels (`/desk`, `/app`) are blocked at the HTTP middleware layer and redirected to SMRITI-owned templates:

| Requested Native Path | Redirect Destination | Scope |
| :--- | :--- | :--- |
| `/desk/setup-wizard` | `/app/smriti-dashboard` | Direct Intercept |
| `/desk/modules` | `/app/smriti-dashboard` | Direct Intercept |
| `/desk#Form` | `/app/smriti-dashboard` | Direct Intercept |
| `/#setup-wizard` | `/app/smriti-dashboard` | Direct Intercept |

This guarantees that store cashiers and managers only interact with custom SMRITI interfaces, maintaining clean branding and shielding complex backend forms.

---

## 👥 Managing Roles and Employee Accounts

Administrators configure user access boundaries by assigning specific system roles. Under the SMRITI configuration suite, three roles dictate dashboard accessibility:

### 1. SMRITI Cashier
- **Scope**: Active POS Billing register access (`/app/barcode#pos-dark`), draft invoice creation, hold/recall operations, shift open/close logs.
- **Restrictions**: Cannot adjust item prices, void transactions without approval, view store-wide sales margins, or execute stock audits.

### 2. SMRITI Store Manager
- **Scope**: Store management console, inventory reorders, pricing schemes setup, cashier shift audits, stock audits, supplier PO/GRN approvals.
- **Permissions**: Authorized to override cashier blockages via a 4-6 digit numeric PIN.

### 3. System Manager / Administrator
- **Scope**: Corporate controls, security settings, backup encryption keys management, license key registration, global whitelabel branding parameters.

---

## 🔒 Assigning Manager POS PINs

Store Managers must set up their POS PIN to authorize cashier exceptions (like line voiding or cart discounts):
1. Navigate to **Administration** → **Security & Workflow Center** → **Users** tab.
2. Locates the Store Manager's row.
3. Click the `🔢 Set PIN` button.
4. Input a secure 4-6 digit numeric PIN, verify, and click **Set PIN**.
5. The PIN is hashed and saved securely in the authentication ledger.

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