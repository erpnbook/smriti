---
Document ID: "INSTALL-009"
Title: "SMRITI Retail OS — Setup & Onboarding Guide"
Owner: "Installation Team"
Audience: "Installer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Last Updated: "2026-06-29"
---

# SMRITI Retail OS — Setup & Onboarding Guide

This document describes the onboarding, installation, and upgrade procedures for **SMRITI Retail OS**.

---

## 📋 Prerequisites

Before starting any installation, ensure your host environment meets the following specifications:
- **Operating System**: Windows 10/11 (with PowerShell 5.1+), Linux, or macOS.
- **Docker Desktop**: Installed and running (includes Docker Compose v2.x).
- **Git**: Installed and configured.
- **Hardware Resources**: At least **4 GB of free RAM** and **10 GB of free disk space**.
- **Network Ports**: Port `8765` (Desk and Billing, configurable via `HTTP_PUBLISH_PORT` in `.env`) must be free on the host. If you optionally map the cashier-locked terminal (container port `9000`) to the host, port `9000` must be free as well.

---

## ⚡ 1. Fresh Install (One-Command)

SMRITI Retail OS provides automated installation scripts. Choose the correct option based on your operating system:

> [!IMPORTANT]
> - **Windows Host (Recommended)**: Use the native **PowerShell installer (`install.ps1`)**. This is fully optimized for Windows systems and automatically configures SMRITI's branding folder icon (`🟢`) in Windows Explorer.
> - **Linux / macOS / WSL**: Use the **Bash installer (`install.sh`)** inside your terminal.

### Windows (PowerShell)
```powershell
# Clone the orchestration repository
git clone https://github.com/erpnbook/smriti-docker.git Smriti9
cd Smriti9

# Run the installer script (bypassing execution restrictions if necessary)
PowerShell -ExecutionPolicy Bypass -File .\install.ps1
```

> [!TIP]
> **Windows Custom Folder Icon**: On Windows systems, the installer dynamically copies SMRITI's branding icon (`smriti.ico`) and configures your installation directory to display the custom SMRITI visual identity (`🟢`) in Windows Explorer.


### Linux / macOS / WSL (Bash)
```bash
# Clone the orchestration repository
git clone https://github.com/erpnbook/smriti-docker.git Smriti9
cd Smriti9

# Execute the shell installer
bash install.sh
```

---

## 🐳 2. Docker Install (Manual / Advanced)

If you prefer to configure the container stack manually for finer deployment control:

### Step A: Populate Source Folders
Create an `apps/` directory and clone the custom Python application packages:
```bash
mkdir -p apps

# Clone custom retail app
git clone https://github.com/erpnbook/smriti.git apps/smriti_retail_os

# Clone GST regulatory compliance app
git clone --branch version-16 https://github.com/resilient-tech/india-compliance.git apps/india_compliance
```

### Step B: Configure Environment Variables
Copy the template configuration file:
```bash
cp example.env .env
```
Open `.env` and set secure database passwords (avoiding defaults).

### Step C: Spin Up Containers
Launch the Docker stack:
```bash
docker compose -f pwd.yml up -d
```
*Wait 2–5 minutes for site databases to provision. Monitor progress via:*
```bash
docker logs -f smriti_retail-create-site-1
```

### Step D: Run Setup Hooks & Sync Static Assets
Once the site is created, run SMRITI's onboarding configuration and copy files to the Nginx shared volume:
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.setup.setup_smriti_retail_os
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets
```

---

## 💻 3. Development Install

For local code development and debugging:

1. Enable Developer Mode on your Frappe site:
   ```bash
   docker exec -it smriti_retail-backend-1 bench --site smriti_retail set-config developer_mode 1
   ```
2. Bind-mount your local code workspace directly into the container inside `compose.yaml`.
3. Open a shell in the backend container to execute commands:
   ```bash
   docker exec -it smriti_retail-backend-1 bash
   ```
4. Run tests continuously to validate modifications:
   ```bash
   bench --site smriti_retail run-tests --app smriti_retail_os
   ```

---

## 🔄 4. Upgrade Existing Install

To pull the latest updates and migrate database schemas without losing operational data:

```powershell
# 1. Execute the automated update script (PowerShell)
.\update.ps1
```

Or execute the upgrade steps manually:
```bash
# 1. Pull the latest code in the app directory
cd apps/smriti_retail_os && git pull origin main && cd ../..

# 2. Run database schema migrations
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate

# 3. Build static bundles
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os

# 4. Sync compiled assets to Nginx
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets

# 5. Clear application caches
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
```

---

## 🧙‍♂️ 5. Initial Setup Wizard

Once the installation finishes, open your browser and navigate to:
```
http://localhost:8765/setup-wizard
```
The wizard guides you through 5 key provisioning steps:

- **Step 1: Administrator**: Establishes system administrator security credentials.
- **Step 2: Company**: Registers your Legal Entity, State Jurisdiction, base Currency, and fiscal calendars.
- **Step 3: Defaults**: Provisions the primary retail structures, including default cash-in-hand accounts and Store Registers.
- **Step 4: GST**: Links GSTIN registration codes, registers HSN codes, and sets up CGST/SGST/IGST tax slabs.
- **Step 5: Deploy**: Compiles configurations and opens the dashboard desk.

---

## ✅ 6. Verifying The Installation

Run SMRITI's pre-flight validator to verify container status and server health:
```powershell
# Run health check
.\check.ps1
```

### Running Automated Unit Tests
Verify the code state by running the test suite:
```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail run-tests --app smriti_retail_os
```
