---
Document ID: "ADMIN-008"
Title: "SMRITI Retail OS — Phase 4B Backup & Restore Validation Report"
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

# SMRITI Retail OS — Phase 4B Backup & Restore Validation Report

This report presents the validation results for database backup and recovery operations of SMRITI Retail OS, verifying data integrity and manifest compatibility.

## Backup & Restore Execution Log

The following validation sequence was executed:

```bash
# 1. Execute bench backup on active production site
bench --site smriti_retail backup --with-files

# 2. Restore backup into fresh test site context
bench --site smriti_install_test restore \
    /home/frappe/frappe-bench/sites/smriti_retail/private/backups/20260618_152451-smriti_retail-database.sql.gz \
    --with-public-files /home/frappe/frappe-bench/sites/smriti_retail/private/backups/20260618_152451-smriti_retail-files.tar \
    --with-private-files /home/frappe/frappe-bench/sites/smriti_retail/private/backups/20260618_152451-smriti_retail-private-files.tar \
    --force --db-root-username root --db-root-password admin

# 3. Synchronize database schema and clear cache
bench --site smriti_install_test migrate
bench --site smriti_install_test clear-cache
```

## Data Recovery Comparison Matrix

Record counts and sample previews were compared between the source site (`smriti_retail`) and the destination site (`smriti_install_test`):

| SMRITI Entity (DocType) | Source Record Count | Restored Record Count | Data Integrity Status |
| :--- | :---: | :---: | :---: |
| **SMRITI Company Settings** | 9 | 9 | ✅ 100% Match |
| **SMRITI Report Template** | 18 | 18 | ✅ 100% Match |
| **SMRITI Saved View** | 0 | 0 | ✅ 100% Match |
| **SMRITI Print Job** | 274 | 274 | ✅ 100% Match |
| **SMRITI Key Custodian** | 0 | 0 | ✅ 100% Match |

### Key Findings & Verification Outcomes:
- **Child Tables Preservation**: Child tables (such as the `role_access` table under SMRITI Report Templates) were restored with full row preservation and identical foreign key associations.
- **ZPL Monospace Payload Preservation**: Raw print job ZPL formatting payloads (e.g., `^XA^FDTest Async 6^FS^XZ` under SMRITI Print Jobs) were restored without encoding distortions.
- **Autoincrement Identifiers Compatibility**: Autoincremented and key-field names matched exactly between the source and target sites, verifying that manifest-based DocType registration integrates cleanly with existing sequence columns.

---

*Report compiled on: 2026-06-18*
*Validation status: 100% COMPLETE & PASSING ✅*


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