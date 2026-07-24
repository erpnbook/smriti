#!/usr/bin/env bash
# ==============================================================================
# SMRITI Retail OS™ — One-Click Update & Upgrade Utility (Linux / macOS / WSL)
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

set -e

SITE=${1:-smriti_retail}
PORT=${2:-8765}

echo -e "\033[0;36m======================================================================\033[0m"
echo -e "\033[0;32m             SMRITI Retail OS™ One-Click Updater                       \033[0m"
echo -e "\033[0;36m======================================================================\033[0m"
echo ""

echo -e "\033[0;36m[SMRITI Update] Creating automatic safety database backup...\033[0m"
docker exec smriti9-backend-1 bench --site "$SITE" backup --with-files || true

echo -e "\033[0;36m[SMRITI Update] Pulling latest code updates from Git...\033[0m"
git pull origin main

if [ -d "apps/india_compliance" ]; then
    git -C apps/india_compliance pull origin version-16 || true
fi

echo -e "\033[0;36m[SMRITI Update] Running site migrations for '$SITE'...\033[0m"
docker exec smriti9-backend-1 bench --site "$SITE" migrate --skip-failing

echo -e "\033[0;36m[SMRITI Update] Rebuilding assets...\033[0m"
docker exec smriti9-backend-1 bench --site "$SITE" build --app smriti_retail_os --app india_compliance || true

echo -e "\033[0;36m[SMRITI Update] Syncing SMRITI assets...\033[0m"
docker exec smriti9-backend-1 /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py

echo -e "\033[0;36m[SMRITI Update] Restarting backend & worker services...\033[0m"
docker compose -f pwd.yml restart backend queue-short queue-long scheduler

echo ""
echo -e "\033[0;32m======================================================================\033[0m"
echo -e "\033[0;32m 🎉 SMRITI Retail OS™ UPDATED and RESTARTED SUCCESSFULLY!             \033[0m"
echo -e "\033[0;32m======================================================================\033[0m"
echo -e "\033[0;33m  🌐 Application Terminal : http://localhost:${PORT}\033[0m"
echo ""
