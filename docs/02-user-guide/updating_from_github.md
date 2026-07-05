---
Document ID: "USER-025"
Title: "Updating SMRITI Retail OS from GitHub"
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

# Updating SMRITI Retail OS from GitHub

This guide explains how to update an existing installation of SMRITI Retail OS to the latest version by pulling the latest code from GitHub and applying it inside the Docker environment.

---

## ⚡ Quick Update Checklist

If you are running the default Docker Desktop environment, follow these steps to pull updates and rebuild:

```bash
# 1. Update the orchestrator repository
git pull origin main

# 2. Update the SMRITI Retail OS application repository
cd apps/smriti_retail_os
git pull origin main
cd ../..

# 3. Build updated frontend assets
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os

# 4. Migrate database schemas (if changed)
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate

# 5. Sync production assets to Nginx
docker exec smriti_retail-backend-1 /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py

# 6. Clear cached resources
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache

# 7. Restart the Frappe background workers and backend server
docker exec smriti_retail-backend-1 bench restart
```

---

## Detailed Step-by-Step Guide

### 1. Update the Host Repositories
Since the SMRITI app and configuration are bind-mounted to your containers, you must first pull the latest code updates onto your host machine.

1. Open your terminal in the root directory of your project (e.g., `smriti_retail`).
2. Run `git pull origin main` to pull any docker configurations or orchestrator updates.
3. Move into the application directory and pull the latest application code:
   ```bash
   cd apps/smriti_retail_os
   git pull origin main
   cd ../..
   ```

### 2. Compile Frontend Assets
If the update includes any HTML, CSS, or Javascript modifications (such as the import verification panel UI), they must be compiled:
```bash
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os
```

### 3. Run Database Migrations
If there are any new DocTypes, custom fields, or schema changes introduced in the update, run the migration script:
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate
```

### 4. Sync Assets to Nginx
To ensure that new frontend code is served properly by the Nginx container, sync the compiled assets:
```bash
docker exec smriti_retail-backend-1 /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py
```

### 5. Clear Cache & Restart Backend Services
Finally, clear the application cache to reload metadata and restart the workers:
```bash
# Clear Cache
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache

# Restart Backend Workers/Server
docker exec smriti_retail-backend-1 bench restart
```

---

## Alternative: Service-Based (Compose) Commands

If your containers are named differently or you prefer using Docker Compose service commands, you can use `docker compose` from the project root directory instead:

```bash
# Rebuild assets
docker compose exec backend bench build --app smriti_retail_os

# Migrate
docker compose exec backend bench --site smriti_retail migrate

# Sync assets
docker compose exec backend /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py

# Clear Cache
docker compose exec backend bench --site smriti_retail clear-cache

# Restart
docker compose exec backend bench restart
```

---

## Troubleshooting

### Symlinks or MIME-Type errors (Blank/Unstyled UI)
If you experience a blank screen or Nginx returns `404` / MIME-type mismatch warnings after updating, re-run the `sync_assets.py` script:
```bash
docker exec smriti_retail-backend-1 /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py
```
This forces Nginx to map the correct physical static bundle instead of broken symlinks.

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