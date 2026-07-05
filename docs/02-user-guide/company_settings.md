---
Document ID: "USER-002"
Title: "SMRITI Company Configurations"
Owner: "Operations Team"
Audience: "End User"
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

# SMRITI Company Configurations

SMRITI Retail OS supports multi-company operations, allowing a single Frappe instance to host multiple retail and wholesale operations. The **SMRITI Company Configurations** layer provides store managers with a centralized dashboard to customize store identities, operational defaults, brand colors, and loyalty behaviors per-company.

---

## Accessing Company Settings

Store managers can access the Company Settings portal through two paths:

1. **SMRITI Workspace**: Navigate to the SMRITI homepage workspace, look for the **Settings & Configuration** card, and click **Company Settings**.
2. **Direct URL**: Navigate directly to `/configure` on your SMRITI site (e.g. `http://localhost:8080/configure`).

> [!NOTE]
> Access to the configuration portal is restricted to users with the **SMRITI Store Manager** or **System Manager** roles.

---

## Dynamic Multi-Company Selector

At the top of the **Company Settings** tab, a company selection dropdown is available:

- **Dynamically loaded**: Changing the company automatically fetches the respective settings from the database via REST API.
- **Reference Filtering**: Upon selecting a company, reference links like **Default Warehouses**, **POS Profiles**, and **Sales Tax Templates** are automatically queried and filtered to only show records belonging to the selected company.

---

## Configuration Categories

The portal organizes per-company settings into three main groups:

### 1. Store Identity
- **Store Trade Name**: The business name displayed on printed and PDF receipts.
- **Store Logo URL**: Absolute path or URL to the store logo for printed headers.
- **Brand Color**: Hex color code representing the company's brand identity. Syncs dynamically with a color picker widget.
- **Invoice Series Prefix**: Custom prefix for sales invoices (e.g., `SMRITI-INV-` or `TATTLY-`).
- **Receipt Footer Text**: Custom message printed at the bottom of customer receipts.

### 2. Operational Defaults
- **Default Warehouse**: The source warehouse used automatically for POS and sales transactions.
- **Default POS Profile**: The POS profile containing terminal parameters (cashiers, payments, etc.).
- **Default Walk-in Customer**: Default customer record used for retail invoice billing when no registered customer is selected.
- **Default Intrastate Tax Template**: Taxes and charges template applied to customers within the same state (CGST + SGST).
- **Default Interstate Tax Template**: Taxes and charges template applied to out-of-state customer orders (IGST).

### 3. Loyalty Program
- **Enable Loyalty Program**: Toggle to activate or deactivate point accumulation.
- **Points per Rupee**: Conversion factor defining how many loyalty points are awarded per unit currency spent.

---

## Technical Details

### Database Schema
Settings are persisted in the **`SMRITI Company Settings`** DocType, which contains standard links to the `Company` DocType. 

Custom fields added to the standard **`Company`** DocType:
- `custom_smriti_store_type`: Select field (`Retail`, `B2B Distributor`, `Wholesale`).
- `custom_smriti_gstin_state`: Read-only code automatically resolved from the company's GSTIN.
- `custom_smriti_settings_configured`: Read-only flag set automatically once settings have been configured.

### Auto-Provisioning Hooks
When a new Company record is created in Frappe (via ERPNext interface or API), SMRITI Company Settings are automatically provisioned with default parameters via hooks on the `Company` doc_events:

```python
doc_events = {
    "Company": {
        "after_insert": "smriti_retail_os.company_api.ensure_company_settings",
        "on_update": "smriti_retail_os.company_api.ensure_company_settings"
    }
}
```

### Python API Usage
Developers can import and query configurations in custom API endpoints:

```python
from smriti_retail_os.company_api import get_setting, get_active_company

# Resolve active company
active_company = get_active_company()

# Read specific setting
brand_color = get_setting("brand_color", company=active_company, default="#1a73e8")
```

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