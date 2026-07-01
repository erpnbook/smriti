# MIGRATION GUIDE — SMRITI Retail OS v1.8.6 → v2.0.0

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
Date: 2026-07-02

---

## Pre-Migration Checklist

Before starting migration, verify:

- [ ] Current site is on v1.8.6 (bench --site smriti_retail version)
- [ ] All active POS sessions are closed
- [ ] No pending background jobs in queue
- [ ] Database backup completed and verified
- [ ] Disk space: minimum 2GB free for migration
- [ ] bench is in maintenance mode (optional but recommended for production)

---

## Backup (Mandatory)

```bash
# Full site backup
bench --site smriti_retail backup --with-files

# Verify backup exists
ls -lh sites/smriti_retail/private/backups/
```

---

## Step 1 — Update Application Source

### Docker (recommended)

```bash
# Pull the latest image
docker pull frappe/erpnext:v16.19.1

# OR update the app source in the running container
docker exec smriti9-backend-1 bash -c "
  cd /home/frappe/frappe-bench/apps/smriti_retail_os &&
  git fetch origin &&
  git checkout v2.0.0
"
```

### Direct (non-Docker)

```bash
cd /home/frappe/frappe-bench/apps/smriti_retail_os
git fetch origin
git checkout v2.0.0
```

---

## Step 2 — Run Migrations

```bash
bench --site smriti_retail migrate
```

### What migrate does in v2.0.0

The migrate command will run the following patches in order:

**[pre_model_sync]**

1. `patches.v1_8_7.migrate_barcode_settings_to_standard`
   Moves SMRITI Barcode Settings from programmatic creation to file-backed DocType.
   Safe: existing settings data is preserved. No schema change.

2. `patches.v1_8_7.migrate_telemetry_event_to_standard`
   Moves SMRITI Telemetry Event Definition to file-backed DocType.
   Safe: existing event definitions are preserved.

**[post_model_sync]**

3. `patches.v1_8_7.add_idempotency_key_index`
   Adds a database index on `tabSMRITI UIE Sync Queue`.`idempotency_key`.
   Safe: additive index, no data change. Improves UIE dispatch deduplication.

4. `patches.seed_purchase_report_templates`
   Seeds 6 SMRITI Report Template records for the Purchase category.
   Idempotent: safe to run multiple times. Uses upsert pattern.

**after_migrate hooks** (automatic)
   - SMRITI Report Templates re-synced (existing templates updated)
   - Navigation workspace created/updated
   - Business dictionary terms re-seeded
   - Assets synced to shared volume

---

## Step 3 — Seed Purchase Templates (if not auto-applied)

If the seed patch was not run automatically (e.g., first-time install):

```bash
bench --site smriti_retail execute \
  smriti_retail_os.patches.seed_purchase_report_templates.execute
```

Expected output:
```
[seed_purchase_report_templates] Seeded 6 Purchase Report Templates.
```

---

## Step 4 — Restart Workers

```bash
# Docker
docker restart smriti9-backend-1 smriti9-queue-short-1 smriti9-queue-long-1 \
  smriti9-scheduler-1 smriti9-frontend-1

# Non-Docker
bench restart
```

---

## Step 5 — Verify Migration

### 5a. Verify Purchase Templates in DB
```bash
bench --site smriti_retail execute \
  smriti_retail_os.analytics_studio.sas_service.get_srs_report_list_for_sas
```
Expected: JSON response containing a "Purchase" key with 6 report entries.

### 5b. Verify New DocTypes Exist
```bash
bench --site smriti_retail execute \
  "frappe.get_meta('SMRITI Purchase Settings').name"
# Expected: "SMRITI Purchase Settings"

bench --site smriti_retail execute \
  "frappe.get_meta('SMRITI UIE Sync Queue').name"
# Expected: "SMRITI UIE Sync Queue"
```

### 5c. Verify App Version
```bash
bench --site smriti_retail version
# Expected: smriti_retail_os 2.0.0
```

### 5d. Smoke Test — Navigate to SMRITI Purchase
Open browser: http://your-site/smriti-purchase
Expected: Purchase Center loads without error.

### 5e. Smoke Test — Analytics Studio Purchase Category
Open browser: http://your-site/smriti-analytics-studio
Expected: "Purchase" category visible in report sidebar with 6 reports.

---

## New DocTypes Created (23 total)

These tables will be created by migrate. No manual action required.

| DocType                             | Module         |
|-------------------------------------|----------------|
| SMRITI Purchase Audit Log           | Purchase Studio |
| SMRITI Purchase Settings            | Purchase Studio |
| SMRITI Navigation Assignment        | Navigation     |
| SMRITI Navigation Override          | Navigation     |
| SMRITI Navigation Permission        | Navigation     |
| SMRITI Navigation Profile           | Navigation     |
| SMRITI Navigation Profile Favorite  | Navigation     |
| SMRITI Navigation Profile Order     | Navigation     |
| SMRITI Negative Stock Case          | SNSM           |
| SMRITI Negative Stock Policy        | SNSM           |
| SMRITI Negative Stock Reason        | SNSM           |
| SMRITI Negative Stock Recovery      | SNSM           |
| SMRITI Tally Settings               | UIE            |
| SMRITI Tally Sync Log               | UIE            |
| SMRITI UIE Credential               | UIE            |
| SMRITI UIE Endpoint                 | UIE            |
| SMRITI UIE Integration              | UIE            |
| SMRITI UIE Sync Log                 | UIE            |
| SMRITI UIE Sync Queue               | UIE            |
| SMRITI Barcode Settings (migrated)  | Barcode        |
| SMRITI Telemetry Event Definition   | Telemetry      |

---

## Rollback Procedure

If migration must be reversed:

```bash
# Step 1: Revert app source
git -C apps/smriti_retail_os checkout v1.8.6

# Step 2: Restore database from backup
bench --site smriti_retail restore \
  sites/smriti_retail/private/backups/<backup_file>.sql.gz

# Step 3: Run migrate on v1.8.6
bench --site smriti_retail migrate

# Step 4: Restart
bench restart
```

**Data safety notes:**
- All new DocType tables are additive — restore drops them cleanly.
- UIE Sync Queue records created during v2.0.0 will be removed on restore.
- SMRITI Report Template seeds (Purchase category) are removed on restore.
- No ERPNext core tables were modified.

---

## UIE (TallyPrime Integration) — First-Time Setup

After migration, to enable TallyPrime sync:

1. Open /smriti-uie (UIE Integration Center)
2. Create a SMRITI UIE Credential entry (Tally host, port)
3. Enable SMRITI Tally Settings (auto-create ledgers: Yes)
4. Test connection
5. First sync will auto-create mapped ledgers in Tally

---

## Known Migration Warnings (Non-Fatal)

1. Scheduler warning at migrate end (non-fatal):
   ```
   smriti_retail_os.negative_stock.service.recovery_service.SMRITINegativeStockRecoveryService
   .run_scheduler_safety_net is not a valid method
   ```
   Cause: SNSM scheduler path requires module package structure correction.
   Impact: None — SNSM recovery scheduler job is skipped, not crashed.
   Fix: Scheduled for v2.0.1.

2. V17FrappeDeprecationWarning: limit_page_length deprecated (use limit)
   Cause: Frappe v16 internal qb_query call.
   Impact: None — warning only, runs correctly.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
