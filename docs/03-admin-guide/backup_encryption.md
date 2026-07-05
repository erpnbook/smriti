---
Document ID: "ADMIN-003"
Title: "SMRITI OS Backup Encryption & Custodian Security"
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

# SMRITI OS Backup Encryption & Custodian Security

This document outlines the cryptographic structure and dual-custodian recovery mechanism for SMRITI's database backup encryption.

## 🔐 AES-256 Symmetric GPG Encryption

To ensure database dumps are protected against data theft, SMRITI implements GPG symmetric encryption using the AES-256 standard:
- **Passphrase Generation**: When enabled under Security Settings, SMRITI generates a cryptographically secure 32-character key.
- **Passphrase Injection**: Passphrases are piped to GPG via standard stdin input streams instead of command-line arguments to prevent credential exposure in process monitoring utilities (like `ps aux`).
- **File Output**: The resulting backup is postfixed with a versioned extension (e.g. `smriti_backup-v1.enc`).

---

## 👥 Dual-Custodian Key Split Protocol

To eliminate single points of failure and prevent unilateral database decryption by a single administrator, SMRITI implements a dual-custodian key split protocol:

```text
       ┌──────────────────────────────┐
       │   32-Char Encryption Key     │
       └──────────────┬───────────────┘
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
   ┌─────────────────┐ ┌─────────────────┐
   │ Key Fragment 01 │ │ Key Fragment 02 │
   │ (First 16 Char) │ │ (Second 16 Char)│
   └────────┬────────┘ └────────┬────────┘
            │                   │
            ▼                   ▼
      Custodian A's       Custodian B's
      Verified Email      Verified Email
```

- **Split Action**: The key is split at its midpoint (e.g., characters 1-16 and characters 17-32).
- **Custodian Emails**: Fragment 1 is emailed to Custodian A, and Fragment 2 is emailed to Custodian B. The full key is never saved in raw text on the server.
- **Verification Gate**: Both custodians must check their status in SMRITI Settings and confirm receipt to set the overall Security Banner to Green (Fully Secured).

---

## 🗑️ Secure Temporary File Deletion

During backup decryption and database restore:
- The system decrypts the `.enc` file to a temporary `.sql.gz` dump on disk.
- Once the restore process finishes (whether it succeeds or fails), the system calls the UNIX `shred` utility (overwriting with multiple random passes and zeroing the file bytes) to destroy the decrypted data.
- If `shred` is absent on the host environment, SMRITI falls back to custom python overwrites before deleting the file handle, leaving zero data signatures on disk.

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