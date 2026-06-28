# SMRITI Retail OS — Production Deployment Guide

---

## About This Manual
* **Document Version:** 1.8.6
* **Release Date:** 2026-06-28
* **Intended Audience:** System Administrators, DevOps Engineers, and Implementation Partners
* **Learning Objectives:** Learn how to build, deploy, configure, backup, and upgrade SMRITI Retail OS in a high-availability production Docker environment.

---

### Author Section (Start)
* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL

---

## Prerequisites — Server Requirements

```
OS:      Ubuntu 22.04 LTS (recommended) / Debian 12
RAM:     Minimum 4GB, Recommended 8GB (2-3 outlets)
CPU:     2 vCPU minimum, 4 vCPU recommended
Disk:    40GB minimum, 100GB recommended (for backups)
Ports:   80, 443 open (HTTP/HTTPS)
Domain:  erp.tattly.in (or any domain pointed to server IP)
```

---

## Step 1 — Server Setup

```bash
# Docker install
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose plugin verify
docker compose version
# Must show: Docker Compose version v2.x.x

# Git
sudo apt install git -y
```

---

## Step 2 — Clone Both Repos

```bash
mkdir -p /opt/smriti
cd /opt/smriti

# Docker infrastructure
git clone https://github.com/erpnbook/smriti-docker.git
cd smriti-docker
```

---

## Step 3 — Environment Setup

```bash
cp example.env .env
nano .env
```

Set the following values in `.env`:

```env
# SMRITI version
ERPNEXT_VERSION=v16.19.1
CUSTOM_IMAGE=ghcr.io/erpnbook/smriti
CUSTOM_TAG=1.8.6

# Database — STRONG password set
DB_PASSWORD=Tattly@Prod2026!   # ← Use your strong password here

# Performance (optimized for 4GB RAM server)
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120

# Port — SMRITI standard
HTTP_PUBLISH_PORT=8765

# Domain (SSL via Traefik)
LETSENCRYPT_EMAIL=jawahar@aitdl.in
SITES_RULE=Host(`erp.tattly.in`)
NGINX_PROXY_HOSTS=erp.tattly.in

# Restart policy
RESTART_POLICY=always
```

---

## Step 4 — Build SMRITI Custom Image

```bash
cd /opt/smriti/smriti-docker

# Build the custom image with SMRITI app baked in
docker build \
  -f images/custom/Containerfile \
  -t ghcr.io/erpnbook/smriti:1.8.6 \
  --build-arg PYTHON_VERSION=3.11.9 \
  .

# Verify image built
docker images | grep smriti
```

---

## Step 5 — Start Infrastructure Services

```bash
cd /opt/smriti/smriti-docker

# Production with HTTPS (Traefik SSL)
docker compose \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.traefik.yaml \
  -f overrides/compose.https.yaml \
  --project-name smriti \
  up -d

# Check all containers healthy
docker compose --project-name smriti ps
```

**Expected output:**
```
smriti-backend-1     running (healthy)
smriti-frontend-1    running
smriti-mariadb-1     running (healthy)
smriti-redis-1       running
smriti-scheduler-1   running
smriti-queue-short-1 running
smriti-queue-long-1  running
smriti-websocket-1   running
```

---

## Step 6 — Create SMRITI Site

```bash
# Site create
docker compose --project-name smriti exec backend \
  bench new-site erp.tattly.in \
  --mariadb-root-password root \
  --admin-password "Tattly@Admin2026!" \
  --db-name tattly_smriti \
  --no-mariadb-socket

# Install SMRITI app
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in install-app smriti_retail_os

# Setup SMRITI (runs after_install hooks)
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in execute smriti_retail_os.setup.setup_smriti_retail_os

# Enable scheduler
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in enable-scheduler

# Set default site
docker compose --project-name smriti exec backend \
  bench use erp.tattly.in
```

---

## Step 7 — Setup Wizard

Access the site in your browser: `https://erp.tattly.in`

SMRITI Setup Wizard will launch automatically. Configure the steps:

```
Step 1 — Credentials: Admin username + password
Step 2 — Company: 
  - Company Name: Tattly Threads
  - GSTIN: 27AAXFT2508H1ZR
  - Address: Mumbai
Step 3 — Defaults:
  - Default Currency: INR
  - Fiscal Year: April-March
  - Default Warehouse: Mumbai Showroom
Step 4 — GST Tax:
  - State: Maharashtra
  - CGST/SGST rates auto-populate
Step 5 — Deploy: Confirm → SMRITI initializes
```

---

## Step 8 — Backup Setup

```bash
# Automated backup every 6 hours
docker compose \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.traefik.yaml \
  -f overrides/compose.https.yaml \
  -f overrides/compose.backup-cron.yaml \
  --project-name smriti \
  up -d

# Manual backup
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in backup --with-files
```

---

## Step 9 — Verify Everything

```bash
# Run SMRITI test suite
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in run-tests \
  --app smriti_retail_os \
  --module smriti_retail_os.tests.test_pos_profile

# Check logs
docker compose --project-name smriti logs backend --tail=50
docker compose --project-name smriti logs scheduler --tail=20

# Health check
curl https://erp.tattly.in/api/method/smriti_retail_os.boot.health_check
# Expected response: {"status": "ok", "version": "1.8.6"}
```

---

## Step 10 — Post-Deployment Checklist

```
[ ] SMRITI login works at https://erp.tattly.in
[ ] Setup Wizard completed — company + GST configured
[ ] POS counter opens without error
[ ] Test barcode scan works
[ ] Test invoice submit works
[ ] Backup running (check /opt/smriti/smriti-docker/sites/erp.tattly.in/private/backups/)
[ ] SSL certificate valid (green lock in browser)
[ ] health_check API returns version 1.8.6
```

---

## Updates — Future Versions

```bash
# Pull new SMRITI image
docker pull ghcr.io/erpnbook/smriti:1.8.7

# Update .env
CUSTOM_TAG=1.8.7

# Migrate
docker compose --project-name smriti exec backend \
  bench --site erp.tattly.in migrate

# Restart
docker compose --project-name smriti restart backend
```

---

## Important Guidance
Always perform testing in a sandbox/local environment first before deploying updates to a live production database. Local validation protects client transactions and ledger integrity.

---

### Author Section (End)
* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL
