---
Document ID: "KB-013"
Title: "SMRITI Retail OS — Pilot Rollout Handbook"
Owner: "Support Team"
Audience: "Support Engineer"
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

# SMRITI Retail OS — Pilot Rollout Handbook

Welcome to the SMRITI Retail OS Pilot Program! This handbook provides retail store owners, managers, and system administrators with everything needed to execute a successful store pilot rollout.

---

## 1. Welcome to SMRITI OS

Welcome to SMRITI Retail OS.

Thank you for being part of the early rollout.

SMRITI Retail OS is a premium operational retail layer built on top of ERPNext. While ERPNext manages the transaction ledger, accounting, and tax computations in the background, SMRITI provides the frontend UI, register billing layouts, reorder intelligence dashboards, and POS cashier workflows.

---

## 2. System Hardware Requirements

To run SMRITI's register billing interface smoothly:
- **Terminal PC**: Core i3 Processor, 4 GB RAM, and Google Chrome version 100+ (or other Chromium browsers).
- **Barcode Scanner**: Standard plug-and-play USB barcode reader.
- **Receipt Printer**: 80mm thermal receipt printer (thermal printing templates default to standard browser print sizes).

---

## 3. Quick Setup & Configuration

Follow these steps to initialize your store:
1. **Log In**: Open `/` on your server and enter your credentials.
2. **Setup Warehouses**: Create your physical store warehouses under the store group.
3. **Configure POS Profiles**: Create a POS Profile, map payment methods, and assign cashier accounts.
4. **Import Products**: Download the spreadsheet template, enter your SKUs (Disabled = No, Maintain Stock = Yes, Sales Item = Yes), and import the file.
5. **Set Prices**: Map standard selling rates and MRPs under Item Price.
6. **Map GST**: Assign standard CGST/SGST templates in the POS Profile.

---

## 4. Cashier Training Checklists

### Start of Shift
- Open the POS register page.
- Input your opening cash drawer amounts.
- Click **Submit** to open the register.

### Processing Sales
- Scan product barcodes.
- Click **Checkout** and select the payment mode (Cash/Card/UPI/Credit).
- Input received amounts and click **Print Receipt**.

### End of Shift
- Click **Close Shift**.
- Perform a physical count of the drawer and enter the actual closing amounts.
- Submit the shift closing sheet (variance requires a manager override PIN).

---

## 5. Security & Backup Management

- **Backup Schedule**: Enable automated backup generation in Security Settings.
- **Encryption**: Enable GPG AES-256 encryption.
- **Key Custodians**: Ensure both key custodians check their email for their recovery key fragments. Store physical copies in a safe.

---

## 6. Support & Escalations

For support during the pilot phase:
- **IT Desk Email**: `support@erpnbook.com`
- **Response SLAs**:
  - *Critical Blocker (POS offline)*: 1 hour.
  - *Major Issue (Inventory/Reorder errors)*: 4 hours.
  - *General Question*: Next business day.

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