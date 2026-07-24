# ==============================================================================
# SMRITI Retail OS™ — Database & Site Restore Utility
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

[CmdletBinding()]
param (
    [Parameter(Mandatory=$true)]
    [string]$SqlFile,
    [string]$Site = "smriti_retail"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "[SMRITI Restore] Initiating database restore for site '$Site'..." -ForegroundColor Cyan

if (-not (Test-Path $SqlFile)) {
    Write-Host "[ERROR] Specified SQL backup file not found: $SqlFile" -ForegroundColor Red
    exit 1
}

$backendContainer = "smriti9-backend-1"

# Check container running state
$status = docker inspect --format='{{.State.Running}}' $backendContainer 2>&1
if ($status -ne "true") {
    Write-Host "[ERROR] Container '$backendContainer' is not running." -ForegroundColor Red
    exit 1
}

$filename = Split-Path $SqlFile -Leaf
$containerDest = "/home/frappe/frappe-bench/backups/$filename"

Write-Host "[SMRITI Restore] Preparing backup file inside container..." -ForegroundColor Cyan
# Copy to backups volume if not already inside mounted backups folder
docker cp $SqlFile "${backendContainer}:${containerDest}"

Write-Host "[SMRITI Restore] Executing bench restore..." -ForegroundColor Cyan
docker exec -it $backendContainer bench --site $Site restore $containerDest --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Database restored successfully to site '$Site'!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Site restore failed." -ForegroundColor Red
    exit 1
}
