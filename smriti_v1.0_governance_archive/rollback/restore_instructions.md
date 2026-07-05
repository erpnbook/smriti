# SMRITI Retail OS v1.0 GA Rollback & Restore Instructions

This document provides step-by-step instructions for rolling back the environment to SMRITI Retail OS v1.0 GA using the files in this rollback package.

---

## 📋 Rollback Prerequisites
Ensure the target environment is online and running the SMRITI Retail OS docker containers.

---

## 🛠️ Step-by-Step Restore Protocol

### 1. Restore the Codebase State
Checkout the exact release freeze git commits for both repositories:
```bash
# Main Repository rollback
cd /path/to/Smriti_Retail_OS
git checkout 92e6d1567a59165fb20f8c17eb88efc6b0ff40cc

# App Repository rollback
cd /path/to/Smriti_Retail_OS/apps/smriti_retail_os
git checkout dbd9c86754689ec7dfb763d4b8708bb9bb74b230
```

### 2. Restore Site Configuration
Copy the archived `site_config.json` back into the container:
```bash
docker cp /path/to/rollback/site_config.json smriti_retail-backend-1:/home/frappe/frappe-bench/sites/smriti_retail/site_config.json
```

### 3. Restore Database State
1. Copy the database backup file into the container:
   ```bash
   docker cp /path/to/rollback/pre_v1_backup.sql.gz smriti_retail-backend-1:/home/frappe/frappe-bench/sites/smriti_retail/private/backups/pre_v1_backup.sql.gz
   ```
2. Execute the restore command using the database root credentials (default username `root` and password `admin`):
   ```bash
   docker exec smriti_retail-backend-1 bench --site smriti_retail restore /home/frappe/frappe-bench/sites/smriti_retail/private/backups/pre_v1_backup.sql.gz --db-root-username root --db-root-password admin --force
   ```

### 4. Clear Cache & Validate
Clear the site cache and verify that the system runs cleanly:
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
```

Once completed, navigate to `http://localhost:8765/billing` to verify the cashier terminal loads successfully.
