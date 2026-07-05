---
Document ID: "ADMIN-004"
Title: "SMRITI OS Backup & Restore Guide"
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

# SMRITI OS Backup & Restore Guide

This guide describes backing up your store database, setting up GPG AES-256 backup encryption, and recovering from system incidents.

## 💾 CLI Backup Protocol

Run backups from the host environment or inside the docker container:
- **Direct CLI**:
  ```bash
  bench --site smriti_retail backup --with-files
  ```
- **Docker CLI**:
  ```bash
  docker exec -it smriti_retail-backend-1 bench --site smriti_retail backup --with-files
  ```
Backups are saved to the site's private files folder: `private/backups/`.

---

## 🔒 GPG AES-256 Backup Encryption Setup

SMRITI provides enterprise-grade **Security Settings** to encrypt backups at rest:
1. Navigate to **Administration** → **Security & Workflow Center** → **Backup Encryption Settings**.
2. Click **Enable Encryption**.
3. SMRITI generates a strong 32-character symmetric password. Passphrases are piped to GPG via secure streams (preventing command-line process sniffing).

### 👥 Dual-Custodian Key Recovery Flow
To prevent unauthorized restoration or loss of recovery keys:
- The generated encryption key is split at its midpoint:
  - **Key Fragment 01**: Dispatched via SMTP to Custodian A's verified email.
  - **Key Fragment 02**: Dispatched via SMTP to Custodian B's verified email.
- Decrypting a backup file requires both fragments to be merged back into the full passphrase.

---

## 🚀 Restore Recovery Protocol

To restore an encrypted database backup (e.g. `smriti_backup-v1.enc`):
1. **Combine Key**: Retrieve the fragments from both Custodians and concatenate them.
2. **Execute Decryption & Restore via CLI**:
   - Decrypt the file using GPG:
     ```bash
     gpg --decrypt --passphrase "merged_key" --output decrypted_backup.sql.gz smriti_backup-v1.enc
     ```
   - Restore the database:
     ```bash
     bench --site smriti_retail restore decrypted_backup.sql.gz --with-public-files public.tar --with-private-files private.tar --force --db-root-username root --db-root-password admin
     ```
3. **Audit**: Restores are logged automatically, and decrypter files are overwritten using the UNIX `shred` utility (with zero-overwrite fallback) to prevent trace leaks on disk.

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