---
Document ID: "ADMIN-002"
Title: "Frequently Asked Questions — Backup & Restore"
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

# Frequently Asked Questions — Backup & Restore

### Q1: How do I restore an encrypted backup if one of the key custodians is unavailable?
**A**: SMRITI's dual-custodian security requires both key fragments to rebuild the 32-character symmetric password. If one custodian is unavailable, you cannot decrypt the backup. It is strongly recommended to register an alternative emergency contact during setup or print and secure physical copies of the key fragments in a secure corporate safe.

### Q2: What happens if I lose the GPG encryption key?
**A**: If the GPG key is lost and no physical or secondary digital copies of the fragments exist, the backup files are **unrecoverable**. SMRITI support cannot bypass GPG symmetric decryption, as the cryptographic design does not include backend backdoor keys.

### Q3: Where are the database backup files stored on the server?
**A**: Backups are saved inside the site's private directory:
```text
sites/smriti_retail/private/backups/
```
From the host environment, you can access these files or copy them to external cloud targets using automated cron tasks.

### Q4: Does enabling backup encryption slow down my server performance?
**A**: The database dump extraction (`mysqldump`) is the primary consumer of system resources. GPG encryption is processed quickly in memory post-dump. Running backups during off-peak night shifts will prevent CPU bottlenecks during business hours.

### Q5: Can I restore a backup from an older version of SMRITI onto a newer version?
**A**: Yes. Restores from older versions are supported. SMRITI retains key version histories. After restoring the database dump, you must execute `bench migrate` to update schema structures to the newer release.

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