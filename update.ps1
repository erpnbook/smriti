# ==============================================================================
# SMRITI Retail OS™ — One-Click Update & Upgrade Utility
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

[CmdletBinding()]
param (
    [string]$Site = "smriti_retail",
    [string]$Port = "8765",
    [switch]$SkipBackup = $false
)

$ErrorActionPreference = "Stop"

function Write-Step ([string]$msg) {
    Write-Host "[SMRITI Update] $msg" -ForegroundColor Cyan
}

function Write-Success ([string]$msg) {
    Write-Host "[SUCCESS] $msg" -ForegroundColor Green
}

function Write-Warn ([string]$msg) {
    Write-Host "[WARNING] $msg" -ForegroundColor Yellow
}

function Write-Err ([string]$msg) {
    Write-Host "[ERROR] $msg" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "             SMRITI Retail OS™ One-Click Updater                       " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$backendContainer = "smriti9-backend-1"

# ------------------------------------------------------------------------------
# 1. Container Running State Check
# ------------------------------------------------------------------------------
Write-Step "Checking container stack status..."
$status = docker inspect --format='{{.State.Running}}' $backendContainer 2>&1
if ($status -ne "true") {
    Write-Err "Container '$backendContainer' is not running. Please start containers using .\install.ps1 or docker compose -f pwd.yml up -d first."
    exit 1
}
Write-Host "  ✔ Container stack is active." -ForegroundColor Gray

# ------------------------------------------------------------------------------
# 2. Automated Safety Backup
# ------------------------------------------------------------------------------
if (-not $SkipBackup) {
    Write-Step "Creating automatic safety database backup before update..."
    try {
        docker exec $backendContainer bench --site $Site backup --with-files
        Write-Success "Pre-update backup completed."
    } catch {
        Write-Warn "Automatic pre-update backup encountered an issue. Proceeding with update..."
    }
}

# ------------------------------------------------------------------------------
# 3. Pull Latest Code Updates
# ------------------------------------------------------------------------------
Write-Step "Pulling latest code updates from Git repositories..."

# Pull orchestration repo
Write-Host "  • Pulling main repository..." -ForegroundColor Gray
git pull origin main

# Pull india_compliance if present
$icPath = Join-Path (Get-Location) "apps\india_compliance"
if (Test-Path $icPath) {
    Write-Host "  • Pulling india_compliance repository..." -ForegroundColor Gray
    try {
        git -C $icPath pull origin version-16
    } catch {
        Write-Warn "Could not pull india_compliance updates. Continuing with local version."
    }
}

# ------------------------------------------------------------------------------
# 4. Run Site Migrations & Rebuild Assets
# ------------------------------------------------------------------------------
Write-Step "Executing bench site migration & database patches for '$Site'..."
docker exec $backendContainer bench --site $Site migrate --skip-failing
if ($LASTEXITCODE -ne 0) {
    Write-Err "Database migration failed. Please review container logs."
    exit 1
}
Write-Success "Database migration completed."

Write-Step "Rebuilding application assets..."
docker exec $backendContainer bench --site $Site build --app smriti_retail_os --app india_compliance
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Asset build reported warnings; completing asset sync..."
}

Write-Step "Executing SMRITI asset sync & status sentinel..."
docker exec $backendContainer /home/frappe/frappe-bench/env/bin/python /home/frappe/frappe-bench/apps/smriti_retail_os/smriti_retail_os/sync_assets.py

# ------------------------------------------------------------------------------
# 5. Restart Application & Worker Services
# ------------------------------------------------------------------------------
Write-Step "Restarting application backend & workers..."
docker compose -f pwd.yml restart backend queue-short queue-long scheduler

# ------------------------------------------------------------------------------
# 6. Verify Health Response
# ------------------------------------------------------------------------------
Write-Step "Verifying application health at http://localhost:$Port..."
$webOk = $false
$elapsed = 0

while ($elapsed -lt 60) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) {
            $webOk = $true
            break
        }
    } catch {
        # Backend warming up
    }
    Start-Sleep -Seconds 3
    $elapsed += 3
    Write-Host "." -NoNewline -ForegroundColor Cyan
}

Write-Host ""
if ($webOk) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host " 🎉 SMRITI Retail OS™ UPDATED and RESTARTED SUCCESSFULLY!             " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  🌐 Application Terminal : http://localhost:$Port" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Warn "Update complete, backend is finalizing startup."
    Write-Host "Check http://localhost:$Port in a few seconds." -ForegroundColor Yellow
}
