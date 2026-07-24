#!/usr/bin/env bash
# ==============================================================================
# SMRITI Retail OS™ — Master Bash Auto-Installer (Linux / macOS / WSL)
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

set -e

PORT=${1:-8765}

echo -e "\033[0;36m======================================================================\033[0m"
echo -e "\033[0;32m                SMRITI Retail OS™ Master Installer                    \033[0m"
echo -e "\033[0;33m         Enterprise Retail Operations & Intelligence Platform          \033[0m"
echo -e "\033[0;36m======================================================================\033[0m"
echo ""

echo -e "\033[0;36m[SMRITI Installer] Checking prerequisites...\033[0m"
command -v git >/dev/null 2>&1 || { echo -e "\033[0;31m[ERROR] git is required but not installed.\033[0m"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "\033[0;31m[ERROR] docker is required but not installed.\033[0m"; exit 1; }

docker info >/dev/null 2>&1 || { echo -e "\033[0;31m[ERROR] Docker daemon is not running. Please start Docker.\033[0m"; exit 1; }
echo -e "\033[0;37m  ✔ Prerequisites verified.\033[0m"

echo -e "\033[0;36m[SMRITI Installer] Preparing workspace directories...\033[0m"
mkdir -p apps backups company

if [ ! -d "apps/india_compliance" ]; then
    echo -e "\033[0;36m[SMRITI Installer] Cloning dependency: india_compliance (v16)...\033[0m"
    git clone --branch version-16 https://github.com/resilient-tech/india-compliance.git apps/india_compliance
fi

echo -e "\033[0;36m[SMRITI Installer] Launching Docker stack (pwd.yml)...\033[0m"
docker compose -f pwd.yml up -d

echo -e "\033[0;36m[SMRITI Installer] Monitoring site provisioning...\033[0m"
until [ "$(docker inspect --format='{{.State.Status}} ({{.State.ExitCode}})' smriti9-create-site-1 2>/dev/null)" = "exited (0)" ]; do
    sleep 5
    echo -n "."
done
echo ""

echo -e "\033[0;32m[SUCCESS] Site provisioning complete!\033[0m"
echo -e "\033[0;36m[SMRITI Installer] Verifying web application response on port ${PORT}...\033[0m"

until curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/" | grep -E '^(200|302)$' >/dev/null; do
    sleep 3
    echo -n "."
done

echo ""
echo -e "\033[0;32m======================================================================\033[0m"
echo -e "\033[0;32m 🎉 SMRITI Retail OS™ is SUCCESSFULLY INSTALLED and RUNNING!          \033[0m"
echo -e "\033[0;32m======================================================================\033[0m"
echo -e "\033[0;33m  🌐 Open Web Terminal : http://localhost:${PORT}\033[0m"
echo ""
