---
Document ID: "DEV-051"
Title: "📊 Excel Setup Spreadsheet Automation"
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

# 📊 Excel Setup Spreadsheet Automation

SMRITI Retail OS includes a powerful **spreadsheet-driven company provisioner** designed to automate complex, standard statutory setups (Company nodes, Chart of Accounts, Address registries, GST parameters, and Bank accounts) directly from a local Excel file.

This completely bypasses the standard, error-prone manual ERPNext setup wizard and ensures that your Excel statutory files are the **single source of truth** for your storefront.

---

## 📂 The Setup File

Your central configuration workbook is located in the root repository folder:
👉 `D:\Smriti_Retail_OS\company\SMRITiRetailOS_Templates_TATTLY_THREADS.xlsx`

### **Workbook Roadmap (Sheets):**
1. **`1. Company Master`**: Holds primary legal entities. The parser reads Column A for the field key (case-insensitive) and Column C for the active configuration value.
   * *Parsed Fields*: Company Name, Abbr, Company PAN, Phone, Email, Address Line 1/2, City, Pin Code, State, Country.
2. **`2. GST Configuration`**: Configures statutory India GST parameters. The parser reads Column A for keys and Column C for values.
   * *Parsed Fields*: GSTIN / UIN, State Code.
3. **`3. Chart of Accounts`**: Documents prefilled retail ledger mapping (Sales, CGS, Cash in Hand, UPI, and Nginx duties/taxes).
4. **`4. Bank Account Ledger`**: Establishes primary storefront bank details. The parser reads Column A for keys and Column B for values.
   * *Parsed Fields*: Bank Name, Branch, Account Number, IFSC Code.
5. **`5. TDS Configuration`**: Tracks Income Tax withholding rates and Deductor TAN settings.
6. **`6. POS Profile`**: Pre-configures cashier permissions, store warehouse limits, and transaction payment methods.
7. **`7. User & Role Setup`**: Outlines unique storefront logins (Administrator, Cashiers, Managers) and security pins.
8. **`8. Master Checklist`**: A roadmap checklist to trace deployment milestones.

---

## ⚡ Automated First-Boot Provisioning

The dynamic parser is integrated directly into the Docker Compose boot process. When you run a fresh installation or reset:
* The system boots the Gunicorn `backend` container.
* The `create-site` utility automatically mounts the local `company` folder into the container.
* It executes **`setup_tattly_threads.py`** which performs automatic **self-healing relational checks**, and then imports all parameters from the Excel workbook under 5 seconds.

### **Self-Healing Relational Safeguards:**
* **Warehouse Type Pre-Population**: Creating a company triggers ERPNext to auto-generate default warehouse structures. If standard warehouse types (such as `All`, `Transit`, `Bonded`, `Consignment`, `Spares`, `Work In Progress`) do not exist on a fresh database, the setup will fail with a `LinkValidationError`. The script dynamically pre-populates these types before generating the company.
* **Bank Account Autonaming Resolution**: Since `Bank Account` documents are autonamed using the `bank_account_no` field, the script avoids hardcoded keys and instead dynamically queries:
  ```python
  frappe.db.get_value("Bank Account", {"bank_account_no": bank_account_no}, "name")
  ```
  to safely retrieve and update existing accounts without duplicating ledgers.

---

## 🔄 Dynamic Synchronization & Future Updates

If you need to change your company details in the future (e.g. updating a business phone number, registered email, bank account number, or IFSC branch code):

1. Open the Excel file at **`D:\Smriti_Retail_OS\company\SMRITiRetailOS_Templates_TATTLY_THREADS.xlsx`** and modify the desired values.
2. Save your changes.
3. Open your host terminal (PowerShell or Bash) and execute this single sync command:

```powershell
docker exec -it smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.setup_tattly_threads.run
```

### **How the Idempotent Script Processes Updates:**
* **Detects Existing Records**: Bypasses duplication checks or constraint violations.
* **Applies Overwrites**: Safely detects what changed in the Excel sheet and overwrites only those specific parameters in the SQL database.
* **Auto-Commits**: Performs direct database commits and outputs a clear execution log (e.g. `Bank Account successfully updated to match Excel changes!`).

---

## 🛡️ Database Verification
At any point, you can inspect the active database record by querying the MariaDB container:

```bash
docker exec smriti_retail-db-1 mariadb -u root -padmin -D _3b3360747feb1c46 -e "SELECT company_name, phone_no, email, pan, gstin FROM tabCompany;"
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