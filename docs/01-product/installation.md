---
Document ID: "PROD-008"
Title: "SMRITI OS Installation Guide"
Owner: "Product Team"
Audience: "Product / Executive"
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

# SMRITI OS Installation Guide

This guide covers deploying SMRITI Retail OS into standard Frappe Bench and containerized Docker environments.

## 📋 System Prerequisites

Ensure your host system meets the minimum hardware specs:
- **Processor**: Intel Core i5 / AMD Ryzen 5 or higher.
- **RAM**: Minimum 8 GB (16 GB recommended for local dev/testing with multiple backend processes).
- **Storage**: SSD with at least 20 GB free space.
- **OS**: Windows 10/11 with WSL2, or Ubuntu 20.04/22.04 LTS.

---

## 🐳 Docker Deployment (Recommended)

SMRITI utilizes Docker Compose to manage multi-container systems. The container stack includes:
- `smriti_retail-backend-1` (Frappe & Custom App service)
- `smriti_retail-mariadb-1` (Database service)
- `smriti_retail-redis-cache-1` / `redis-queue-1` / `redis-socketio-1`

### Step 1: Clone the Repository
Clone the production configuration workspace:
```bash
git clone https://github.com/erpnbook/smriti-docker.git smriti-docker
cd smriti-docker
```

### Step 2: Configure Environment Settings
Create your local environment file (`.env`):
```bash
cp example.env .env
```
Ensure the license signing secret variable is defined to prevent key verification warnings:
```bash
SMRITI_LICENSE_SECRET=your_production_hmac_secret_key
```

### Step 3: Boot Containers
Spin up the service stack in detached mode:
```bash
docker compose up -d
```
Verify that all containers are online:
```bash
docker ps
```

### Step 4: Install Custom App
Execute the installer inside the backend container to sync custom schemas and build web assets:
```bash
docker exec -it smriti_retail-backend-1 bench --site smriti_retail install-app smriti_retail_os
docker exec -it smriti_retail-backend-1 bench --site smriti_retail migrate
```

---

## 💻 Standard Bench Deployment

If you are running a direct bench installation:

### Step 1: Fetch the Custom App
Pull SMRITI Retail OS from the custom application repository:
```bash
bench get-app smriti_retail_os https://github.com/erpnbook/smriti_retail_os.git
```

### Step 2: Install to Local Site
Install the app onto your target site:
```bash
bench --site smriti_retail install-app smriti_retail_os
```

### Step 3: Set License Secret
Open your site config file (`sites/smriti_retail/site_config.json`) and configure your signing key:
```json
{
  "smriti_license_secret": "your_production_hmac_secret_key"
}
```

### Step 4: Migrate & Clear Cache
Rebuild database structures and flush Redis buffers:
```bash
bench --site smriti_retail migrate
bench --site smriti_retail clear-cache
```

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