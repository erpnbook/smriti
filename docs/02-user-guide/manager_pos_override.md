---
Document ID: "USER-005"
Title: "SMRITI OS Manager POS Override PIN Security"
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

# SMRITI OS Manager POS Override PIN Security

This guide outlines the security design, hashing protocols, and auditing procedures for SMRITI's manager-level POS override system.

## 🔒 Security Design and Hashing

When cashiers execute restricted actions (such as voiding checkout rows, deleting carts, or entering custom discounts), SMRITI locks the register screen and requests a **Manager PIN**:
- **Hashed Credentials**: The numeric PIN (`custom_smriti_pin`) is stored as a salted hash in the database authentication ledger (`__Auth` table) rather than raw text.
- **Verification Engine**: Submissions utilize a secure server-side method executing a constant-time comparison check, preventing timing side-channel attacks.
- **Redis Rate-Limiter**: To mitigate brute-force attempts, PIN verification is rate-limited to **5 failed attempts within 10 minutes** (stored in Redis cache). Once exceeded, the manager account is locked out from overrides.

---

## ⚙️ Setting and Resetting POS PINs

System Administrators and authorized managers configure credentials via the SMRITI interface:
1. Navigate to the Security & Workflow Center (`/security`).
2. Open the **Users** tab.
3. Locate the manager's profile row and click the `🔢 PIN` button.
4. Input a secure 4-6 digit numeric code and click **Set PIN**.
5. To revoke override privileges, click the `🔢 PIN` button and select **Clear PIN** in the modal footer.

---

## 📝 Activity Logs & Override Auditing

Every approved override creates a persistent trail for security tracking:
- **Audit Logs**: The system automatically posts a comment to the corresponding Draft POS Invoice detailing the override context (e.g. `"Row void authorized by Manager 'jawahar.mallah@gmail.com'"`).
- **Security Logs**: Unauthorized override attempts or multiple PIN failures are saved under **SMRITI Security Logs**, capturing the timestamp, username, IP address, and failed action details.

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