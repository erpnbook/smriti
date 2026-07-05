---
Document ID: "DEV-008"
Title: "SMRITI Customer Growth Engine (CGE) — Disaster Recovery (DR) Runbook v1.0"
Owner: "Development Team"
Audience: "Developer"
Module: "CGE"
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

# SMRITI Customer Growth Engine (CGE) — Disaster Recovery (DR) Runbook v1.0

This runbook describes the disaster recovery procedures, backup schedules, database restore commands, and verification steps required to restore the SMRITI Customer Growth Engine (CGE) in the event of database corruption or hardware failure.

---

## 1. Backup Schedule & Policy

Database backups are captured automatically using [backup_api.py](../../apps/smriti_retail_os/smriti_retail_os/backup_api.py).

### Automatic Schedule
*   **Daily Backups**: Triggered nightly at `00:00` by the scheduler event listener [hooks.py](../../apps/smriti_retail_os/smriti_retail_os/hooks.py#L325).
*   **Storage Location**: Backups are written to `d:\Smriti_Retail_OS\backups\`.
*   **Retention**:
    *   Daily backups are kept for **90 days**.
    *   Monthly backups (captured on the 1st of each month) are kept for **5 years**.
    *   Expired snapshots are cleaned up daily by `execute_snapshot_cleanup` in [cge_service.py](../../apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py#L604).

---

## 2. Triggering a Manual Backup

To trigger a manual database backup:

### Via CGE Studio UI
1.  Navigate to **CGE Studio** -> **Disaster Recovery** tab.
2.  Click **Create Backup Now**.
3.  Wait for the progress spinner to complete.

### Via Bench CLI Command Line
Run the following command from the bench directory:
```bash
bench --site smriti_retail execute smriti_retail_os.backup_api.run_scheduled_backup
```

---

## 3. Simulating a Data Wipe (Testing DR Only)

To test the disaster recovery pipeline (as verified in [test_cge_rules.py](../../apps/smriti_retail_os/smriti_retail_os/tests/test_cge_rules.py#L256)):

1.  Run the manual backup to generate a snapshot.
2.  Log in to the database console:
    ```bash
    bench --site smriti_retail mariadb
    ```
3.  Wipe target CGE tables:
    ```sql
    TRUNCATE TABLE `tabSMRITI Loyalty Tier`;
    TRUNCATE TABLE `tabSMRITI Loyalty Rule`;
    TRUNCATE TABLE `tabSMRITI Coupon Campaign`;
    TRUNCATE TABLE `tabSMRITI Wallet Ledger`;
    ```

---

## 4. Database Restoration Procedure

To restore the database from a backup:

### Step 1: Identify the Latest Backup File
Get a list of available backups:
```bash
bench --site smriti_retail execute smriti_retail_os.backup_api.get_backup_history
```
This lists available backups sorted by date, such as `20260619_000000-smriti_retail-database.sql.gz`.

### Step 2: Restore the Backup
Execute the bench restore command. You must set the database root password in the environment for authentication:

#### Linux / macOS
```bash
export MARIADB_ROOT_PASSWORD="your_mariadb_root_password"
bench --site smriti_retail restore /absolute/path/to/backup.sql.gz
```

#### Windows PowerShell
```powershell
$env:MARIADB_ROOT_PASSWORD="your_mariadb_root_password"
bench --site smriti_retail restore D:\Smriti_Retail_OS\backups\20260619_000000-smriti_retail-database.sql.gz
```

### Step 3: Run Database Migrations
Synchronize document schemas and update stored fixtures:
```bash
bench --site smriti_retail migrate
bench --site smriti_retail clear-cache
```

---

## 5. Post-Restore Verification Checklist

After restoration, verify CGE data integrity:

1.  **Check Table Records**:
    Confirm rule and tier counts match pre-disaster targets.
2.  **Verify Cashback Ledger Balances**:
    Verify that the append-only ledger entries have been restored.
3.  **Run Wallet Reconciliation**:
    Run the reconciliation task to verify that ledger transactions and wallet totals match:
    ```bash
    bench --site smriti_retail execute smriti_retail_os.cge.service.cge_service.reconcile_wallet_liability
    ```
    Confirm that the output snapshot shows `status = Reconciled` and `variance = 0.0`.
4.  **Inspect System Activity Logs**:
    Verify that the Activity Log entries match expected post-restore state.


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